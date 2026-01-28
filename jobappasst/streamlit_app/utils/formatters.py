"""
Data formatting utilities for Streamlit app
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def format_salary(salary_min: Optional[int], salary_max: Optional[int]) -> str:
    """Format salary range for display"""

    if not salary_min and not salary_max:
        return "Not specified"

    if salary_min and salary_max:
        return f"${salary_min:,} - ${salary_max:,}"
    elif salary_min:
        return f"${salary_min:,}+"
    else:
        return f"Up to ${salary_max:,}"


def format_date(date_str: Optional[str], format_out: str = "%b %d, %Y") -> str:
    """Format date string for display"""

    if not date_str:
        return "N/A"

    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime(format_out)
    except:
        pass

    try:
        # Try parsing YYYY-MM-DD format
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime(format_out)
    except:
        pass

    return date_str


def format_location(location: Optional[str], remote: bool = False) -> str:
    """Format location with remote indicator"""

    if remote and location:
        return f"{location} (Remote)"
    elif remote:
        return "Remote"
    elif location:
        return location
    else:
        return "Not specified"


def format_match_score(score: float) -> str:
    """Format match score with emoji indicator"""

    if score >= 80:
        return f"🟢 {score:.1f}%"
    elif score >= 60:
        return f"🟡 {score:.1f}%"
    else:
        return f"🔴 {score:.1f}%"


def format_application_status(status: str) -> str:
    """Format application status with emoji"""

    status_map = {
        'draft': '📝 Draft',
        'applied': '📬 Applied',
        'interviewing': '🎤 Interviewing',
        'rejected': '❌ Rejected',
        'offer': '🎉 Offer'
    }

    return status_map.get(status.lower(), f"📋 {status.title()}")


def format_skill_level(level: Optional[str]) -> str:
    """Format skill level with indicator"""

    if not level:
        return ""

    level_map = {
        'beginner': '⭐ Beginner',
        'intermediate': '⭐⭐ Intermediate',
        'advanced': '⭐⭐⭐ Advanced'
    }

    return level_map.get(level.lower(), level.title())


def format_skills_list(skills: List[Dict]) -> str:
    """Format skills list as a comma-separated string"""

    if not skills:
        return "No skills listed"

    skill_names = [s.get('name', '') for s in skills if s.get('name')]
    return ", ".join(skill_names[:10])


def format_experience_duration(start_date: Optional[str], end_date: Optional[str]) -> str:
    """Format experience duration"""

    if not start_date:
        return "Duration unknown"

    end = end_date if end_date else "Present"
    return f"{start_date} - {end}"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def format_requirements_list(requirements: List[str], max_items: int = 5) -> List[str]:
    """Format requirements list, limiting to max items"""

    if not requirements:
        return []

    formatted = []
    for req in requirements[:max_items]:
        # Clean up the requirement text
        req = req.strip()
        if not req.startswith("•") and not req.startswith("-"):
            req = f"• {req}"
        formatted.append(req)

    if len(requirements) > max_items:
        formatted.append(f"... and {len(requirements) - max_items} more")

    return formatted


def job_to_display_dict(job: Dict[str, Any]) -> Dict[str, str]:
    """Convert job data to display-friendly format"""

    return {
        'title': job.get('title', 'Unknown Position'),
        'company': job.get('company', 'Unknown Company'),
        'location': format_location(job.get('location'), job.get('remote', False)),
        'salary': format_salary(job.get('salary_min'), job.get('salary_max')),
        'posted': format_date(job.get('posted_date')),
        'source': job.get('source', 'Unknown'),
        'apply_url': job.get('apply_url', '#')
    }


def profile_to_summary(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Convert profile data to summary format"""

    skills = profile.get('skills', [])
    experience = profile.get('experience', [])

    return {
        'name': profile.get('name', 'Unknown'),
        'email': profile.get('email', 'N/A'),
        'location': profile.get('location', 'N/A'),
        'skills_count': len(skills),
        'skills_preview': format_skills_list(skills),
        'experience_count': len(experience),
        'technical_skills': len([s for s in skills if s.get('category') == 'technical']),
        'soft_skills': len([s for s in skills if s.get('category') == 'soft'])
    }


def stats_to_metrics(stats: Dict[str, int]) -> List[Dict[str, Any]]:
    """Convert stats dict to metrics format for display"""

    metrics = []

    status_config = {
        'total': {'label': 'Total', 'emoji': '📊'},
        'draft': {'label': 'Draft', 'emoji': '📝'},
        'applied': {'label': 'Applied', 'emoji': '📬'},
        'interviewing': {'label': 'Interviewing', 'emoji': '🎤'},
        'rejected': {'label': 'Rejected', 'emoji': '❌'},
        'offer': {'label': 'Offer', 'emoji': '🎉'}
    }

    for key, config in status_config.items():
        value = stats.get(key, 0)
        metrics.append({
            'label': f"{config['emoji']} {config['label']}",
            'value': value
        })

    return metrics
