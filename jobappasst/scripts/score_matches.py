"""Score jobs against a profile and store matches"""

import sys
from pathlib import Path

# Load environment variables (optional - only needed for Claude API)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import (
    get_profile,
    list_profiles,
    list_jobs,
    get_job,
    upsert_job_match,
    get_top_matches,
    delete_matches_for_profile
)
from src.matching import match_profile_to_job


def safe_print(text):
    """Print text with safe encoding handling."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fall back to ASCII if Unicode fails
        print(text.encode('ascii', 'replace').decode('ascii'))


def main():
    """Score all jobs against a profile"""
    print("=" * 70)
    print("Job Application Assistant - Job Matcher")
    print("=" * 70)
    print()

    # Get profile ID
    if len(sys.argv) < 2:
        print("Usage: python scripts/score_matches.py <profile_id> [options]")
        print()
        print("Options:")
        print("  --min-score <num>      Minimum match score to display (0-100)")
        print("  --use-claude           Enable Claude API for enhanced matching")
        print("  --refresh              Delete existing matches and re-score all jobs")
        print("  --limit <num>          Max number of jobs to score (default: all)")
        print()
        print("Available profiles:")
        profiles = list_profiles()
        for p in profiles:
            skill_count = len(p.get('skills', []))
            print(f"  ID {p['id']}: {p['name']} ({skill_count} skills)")
        print()
        print("Examples:")
        print("  python scripts/score_matches.py 5")
        print("  python scripts/score_matches.py 5 --min-score 60 --use-claude")
        print("  python scripts/score_matches.py 5 --refresh")
        sys.exit(1)

    profile_id = int(sys.argv[1])

    # Parse optional arguments
    min_score = 0
    use_claude = False
    refresh = False
    limit = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--min-score" and i + 1 < len(sys.argv):
            min_score = float(sys.argv[i + 1])
            i += 2
        elif arg == "--use-claude":
            use_claude = True
            i += 1
        elif arg == "--refresh":
            refresh = True
            i += 1
        elif arg == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    # Load profile
    profile = get_profile(profile_id)
    if not profile:
        print(f"[!] Profile {profile_id} not found")
        sys.exit(1)

    print(f"Profile: {profile['name']}")
    print(f"Email: {profile['email']}")
    print(f"Skills: {len(profile.get('skills', []))} skills")
    print()

    # Refresh matches if requested
    if refresh:
        print("Deleting existing matches...")
        deleted_count = delete_matches_for_profile(profile_id)
        print(f"[+] Deleted {deleted_count} existing matches")
        print()

    # Load jobs
    print("Loading jobs from database...")
    all_jobs = list_jobs(limit=limit if limit else 10000)
    print(f"[+] Found {len(all_jobs)} jobs to score")
    print()

    if not all_jobs:
        print("[!] No jobs found in database")
        print("Run fetch_jobs_by_profile.py first to fetch jobs")
        sys.exit(0)

    # Display matching parameters
    if use_claude:
        print("Claude API: Enabled (enhanced matching)")
    else:
        print("Claude API: Disabled (basic skill matching)")
    print(f"Minimum score filter: {min_score}")
    print()

    # Score each job
    print("Scoring jobs against profile...")
    print("-" * 70)

    scored_count = 0
    stored_count = 0
    skipped_count = 0

    for i, job in enumerate(all_jobs, 1):
        # Show progress every 10 jobs
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(all_jobs)} jobs processed...")

        try:
            # Score the job
            match_result = match_profile_to_job(
                profile=profile,
                job=job,
                use_claude=use_claude
            )

            scored_count += 1

            # Store the match
            match_score = match_result['match_score']
            matched_skills = match_result['matched_skills']
            missing_skills = match_result['missing_skills']
            notes = match_result['notes']

            job_id, was_updated = upsert_job_match(
                profile_id=profile_id,
                job_id=job['id'],
                match_score=match_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                notes=notes
            )

            stored_count += 1

        except Exception as e:
            print(f"[!] Error scoring job {job.get('title', 'Unknown')}: {e}")
            skipped_count += 1

    print()
    print(f"[+] Scored {scored_count} jobs")
    print(f"[+] Stored {stored_count} matches")
    if skipped_count > 0:
        print(f"[!] Skipped {skipped_count} jobs due to errors")
    print()

    # Display top matches
    print("=" * 70)
    print("TOP MATCHES")
    print("=" * 70)
    print()

    top_matches = get_top_matches(profile_id, limit=20)

    if not top_matches:
        print("[!] No matches found")
        sys.exit(0)

    # Filter by minimum score
    filtered_matches = [m for m in top_matches if m['match_score'] >= min_score]

    if not filtered_matches:
        print(f"[!] No matches found with score >= {min_score}")
        print(f"Top score in database: {top_matches[0]['match_score']:.1f}")
        sys.exit(0)

    for i, match in enumerate(filtered_matches[:10], 1):
        job = get_job(match['job_id'])
        if not job:
            continue

        safe_print(f"Match {i}: Score {match['match_score']:.1f}%")
        safe_print(f"Title: {job['title']}")
        safe_print(f"Company: {job['company']}")
        safe_print(f"Location: {job['location']}")
        if job.get('remote'):
            safe_print("Remote: Yes")

        # Display matched skills
        if match['matched_skills']:
            skills_display = ', '.join(match['matched_skills'][:5])
            if len(match['matched_skills']) > 5:
                skills_display += f" (+{len(match['matched_skills']) - 5} more)"
            safe_print(f"Matched Skills: {skills_display}")

        # Display missing skills
        if match['missing_skills']:
            missing_display = ', '.join(match['missing_skills'][:3])
            if len(match['missing_skills']) > 3:
                missing_display += f" (+{len(match['missing_skills']) - 3} more)"
            safe_print(f"Missing Skills: {missing_display}")

        print()

    if len(filtered_matches) > 10:
        print(f"... and {len(filtered_matches) - 10} more matches")
        print()

    # Summary statistics
    print("=" * 70)
    print("MATCH STATISTICS")
    print("=" * 70)
    print()

    scores = [m['match_score'] for m in top_matches]
    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"Total matches: {len(top_matches)}")
    print(f"Matches >= {min_score}: {len(filtered_matches)}")
    print(f"Average score: {avg_score:.1f}%")
    print(f"Highest score: {max(scores):.1f}%")
    print(f"Lowest score: {min(scores):.1f}%")
    print()

    print("=" * 70)
    print("[+] Job matching complete!")
    print()
    print("Next steps:")
    print("  - Review top matches in database")
    print("  - Start Phase 5: Browser automation for applications!")
    print("=" * 70)


if __name__ == "__main__":
    main()
