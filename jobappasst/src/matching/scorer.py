"""Match scoring logic for profiles vs jobs"""

import os
import json
from typing import Dict, Any, List, Tuple
from .taxonomy import extract_matched_skills, normalize_skill


def calculate_basic_match_score(
    profile_skills: List[Dict[str, Any]],
    job_requirements: List[str],
    job_description: str
) -> Tuple[float, List[str], List[str]]:
    """
    Calculate a basic match score based on skill overlap.

    Args:
        profile_skills: List of skill dictionaries from profile
        job_requirements: List of job requirements
        job_description: Full job description

    Returns:
        tuple: (match_score, matched_skills, missing_skills)
    """
    # Extract skill names from profile
    profile_skill_names = [s.get('name') for s in profile_skills if s.get('name')]

    # Find matched skills
    matched_skills = extract_matched_skills(profile_skill_names, job_requirements)

    # Calculate base score from skill overlap
    if not job_requirements:
        base_score = 50.0  # Default if no requirements listed
    else:
        match_ratio = len(matched_skills) / len(job_requirements)
        base_score = min(match_ratio * 100, 100)

    # Boost score for advanced skills
    for skill in profile_skills:
        if skill.get('name') in matched_skills and skill.get('level') == 'advanced':
            base_score = min(base_score + 5, 100)

    # Identify potential missing skills (requirements not matched)
    missing_skills = []
    for req in job_requirements:
        req_normalized = normalize_skill(req)
        is_matched = False

        for matched in matched_skills:
            if normalize_skill(matched) in req_normalized:
                is_matched = True
                break

        if not is_matched and len(req) > 3:  # Skip very short requirements
            missing_skills.append(req)

    return (base_score, matched_skills, missing_skills[:10])  # Limit to top 10 missing


def match_profile_to_job(
    profile: Dict[str, Any],
    job: Dict[str, Any],
    use_claude: bool = True,
    api_key: str = None
) -> Dict[str, Any]:
    """
    Match a profile against a job and generate detailed analysis.

    Args:
        profile: Profile dictionary with skills and experience
        job: Job dictionary with requirements and description
        use_claude: Whether to use Claude API for enhanced matching
        api_key: Optional Claude API key

    Returns:
        dict: Match result with score, matched_skills, missing_skills, notes
    """
    # Get basic match score
    profile_skills = profile.get('skills', [])
    job_requirements = job.get('requirements', [])
    job_description = job.get('description', '')

    base_score, matched_skills, missing_skills = calculate_basic_match_score(
        profile_skills,
        job_requirements,
        job_description
    )

    # Prepare result
    result = {
        'match_score': base_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'notes': f"Basic skill match: {len(matched_skills)} skills matched"
    }

    # Enhance with Claude analysis if requested
    if use_claude and (base_score > 30 or len(matched_skills) > 0):
        try:
            claude_analysis = analyze_match_with_claude(profile, job, api_key)
            if claude_analysis:
                result['match_score'] = claude_analysis.get('score', base_score)
                result['notes'] = claude_analysis.get('notes', result['notes'])
                # Keep matched/missing from basic analysis but add Claude's insights
                result['notes'] += f"\n\nClaude Analysis:\n{claude_analysis.get('analysis', '')}"
        except Exception as e:
            # Fall back to basic score if Claude fails
            result['notes'] += f"\n(Claude analysis unavailable: {str(e)})"

    return result


def analyze_match_with_claude(
    profile: Dict[str, Any],
    job: Dict[str, Any],
    api_key: str = None
) -> Dict[str, Any]:
    """
    Use Claude API to analyze profile-job match.

    Args:
        profile: Profile dictionary
        job: Job dictionary
        api_key: Optional API key (reads from env if not provided)

    Returns:
        dict: Claude's analysis with score and notes
    """
    # Import Anthropic only when needed
    try:
        from anthropic import Anthropic
    except ImportError:
        return None

    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    client = Anthropic(api_key=api_key)

    # Prepare profile summary
    profile_summary = {
        'name': profile.get('name'),
        'summary': profile.get('summary'),
        'skills': [
            {
                'name': s.get('name'),
                'level': s.get('level'),
                'years': s.get('years')
            }
            for s in profile.get('skills', [])[:15]  # Top 15 skills
        ],
        'experience': [
            {
                'title': e.get('title'),
                'company': e.get('company'),
                'years': f"{e.get('start_date')} to {e.get('end_date')}"
            }
            for e in profile.get('experience', [])[:5]  # Recent 5 roles
        ]
    }

    # Prepare job summary
    job_summary = {
        'title': job.get('title'),
        'company': job.get('company'),
        'location': job.get('location'),
        'remote': job.get('remote'),
        'requirements': job.get('requirements', [])[:10],  # Top 10 requirements
        'description': job.get('description', '')[:1000]  # First 1000 chars
    }

    prompt = f"""You are a professional recruiter analyzing candidate-job fit.

CANDIDATE PROFILE:
{json.dumps(profile_summary, indent=2)}

JOB POSTING:
{json.dumps(job_summary, indent=2)}

Analyze how well this candidate matches this job. Consider:
1. Skill alignment (technical and soft skills)
2. Experience level and relevance
3. Career trajectory fit
4. Location/remote match
5. Missing critical qualifications

Provide your response as JSON:
{{
  "score": <number 0-100>,
  "analysis": "<2-3 sentence summary of fit>",
  "strengths": ["strength1", "strength2", "strength3"],
  "concerns": ["concern1", "concern2"]
}}

Return ONLY the JSON, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        # Parse JSON response
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                analysis = json.loads(json_str)
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                analysis = json.loads(json_str)
            else:
                return None

        # Format notes
        notes = analysis.get('analysis', '')
        if analysis.get('strengths'):
            notes += "\n\nStrengths:\n" + "\n".join(f"- {s}" for s in analysis['strengths'])
        if analysis.get('concerns'):
            notes += "\n\nConcerns:\n" + "\n".join(f"- {c}" for c in analysis['concerns'])

        return {
            'score': analysis.get('score', 50),
            'notes': analysis.get('analysis', ''),
            'analysis': notes
        }

    except Exception as e:
        print(f"Claude analysis error: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Test basic scoring
    profile_skills = [
        {'name': 'Python', 'level': 'advanced', 'years': 5},
        {'name': 'SQL', 'level': 'advanced', 'years': 4},
        {'name': 'Tableau', 'level': 'intermediate', 'years': 2}
    ]

    job_requirements = [
        "5+ years Python experience",
        "Strong SQL skills",
        "Experience with data visualization tools",
        "Knowledge of cloud platforms (AWS/Azure)"
    ]

    score, matched, missing = calculate_basic_match_score(
        profile_skills,
        job_requirements,
        "We need a data engineer..."
    )

    print(f"Match Score: {score:.1f}%")
    print(f"Matched Skills: {matched}")
    print(f"Missing Skills: {missing}")
