"""Fetch jobs based on profile skills rather than specific job titles"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jobs.jsearch_client import JSearchClient
from src.jobs.normalizer import normalize_job_list, extract_job_summary
from src.db import upsert_job, list_jobs, get_profile, list_profiles


def generate_skill_based_queries(profile_id: int, max_queries: int = 5) -> list[str]:
    """
    Generate search queries based on profile skills.

    Args:
        profile_id: Database profile ID
        max_queries: Maximum number of search queries to generate

    Returns:
        list: List of search query strings
    """
    profile = get_profile(profile_id)

    if not profile:
        raise ValueError(f"Profile {profile_id} not found")

    skills = profile.get('skills', [])

    if not skills:
        raise ValueError(f"Profile {profile_id} has no skills")

    # Sort skills by years of experience (descending)
    sorted_skills = sorted(
        skills,
        key=lambda s: s.get('years', 0),
        reverse=True
    )

    # Filter to technical skills with at least intermediate level
    technical_skills = [
        s for s in sorted_skills
        if s.get('category') in ['technical', 'tool']
        and s.get('level') in ['intermediate', 'advanced']
    ]

    queries = []

    # Strategy 1: Top individual skills
    for skill in technical_skills[:max_queries]:
        queries.append(skill['name'])

    # Strategy 2: Skill combinations (top 2-3 skills)
    if len(technical_skills) >= 2:
        top_skills = [s['name'] for s in technical_skills[:3]]
        queries.append(" ".join(top_skills[:2]))
        if len(top_skills) >= 3:
            queries.append(" ".join(top_skills[:3]))

    # Remove duplicates and limit
    unique_queries = []
    seen = set()
    for q in queries:
        if q not in seen:
            unique_queries.append(q)
            seen.add(q)

    return unique_queries[:max_queries]


def main():
    """Fetch jobs based on profile skills"""
    print("=" * 70)
    print("Job Application Assistant - Skill-Based Job Fetcher")
    print("=" * 70)
    print()

    # Get profile ID
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_jobs_by_profile.py <profile_id> [options]")
        print()
        print("Options:")
        print("  --location <location>      Location filter (e.g., 'Houston, TX')")
        print("  --remote                   Only fetch remote jobs")
        print("  --type <types>             Employment types (FULLTIME,CONTRACTOR,PARTTIME)")
        print("  --date <filter>            Date filter (all, today, 3days, week, month)")
        print("  --max-queries <num>        Max skill-based queries (default: 5)")
        print()
        print("Available profiles:")
        profiles = list_profiles()
        for p in profiles:
            print(f"  ID {p['id']}: {p['name']} ({p['email']})")
        print()
        print("Examples:")
        print("  python scripts/fetch_jobs_by_profile.py 5 --location 'Houston, TX'")
        print("  python scripts/fetch_jobs_by_profile.py 5 --remote --date week")
        sys.exit(1)

    profile_id = int(sys.argv[1])

    # Parse optional arguments
    location = None
    remote_only = False
    employment_types = None
    date_posted = "week"
    max_queries = 5

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--location" and i + 1 < len(sys.argv):
            location = sys.argv[i + 1]
            i += 2
        elif arg == "--remote":
            remote_only = True
            i += 1
        elif arg == "--type" and i + 1 < len(sys.argv):
            employment_types = sys.argv[i + 1]
            i += 1
        elif arg == "--date" and i + 1 < len(sys.argv):
            date_posted = sys.argv[i + 1]
            i += 1
        elif arg == "--max-queries" and i + 1 < len(sys.argv):
            max_queries = int(sys.argv[i + 1])
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

    # Generate skill-based queries
    print("Generating skill-based search queries...")
    try:
        queries = generate_skill_based_queries(profile_id, max_queries=max_queries)
        print(f"[+] Generated {len(queries)} search queries:")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q}")
        print()
    except Exception as e:
        print(f"[!] Error generating queries: {e}")
        sys.exit(1)

    # Display search parameters
    if location:
        print(f"Location filter: {location}")
    if remote_only:
        print("Remote jobs only: Yes")
    if employment_types:
        print(f"Employment types: {employment_types}")
    print(f"Date filter: {date_posted}")
    print()

    # Fetch jobs for each query
    all_jobs = []
    client = JSearchClient()

    for i, query in enumerate(queries, 1):
        print(f"Query {i}/{len(queries)}: {query}")

        try:
            response = client.search(
                query=query,
                location=location,
                remote_jobs_only=remote_only,
                employment_types=employment_types,
                date_posted=date_posted,
                num_pages=1
            )

            raw_jobs = response.get("data", [])
            print(f"  [+] Found {len(raw_jobs)} jobs")
            all_jobs.extend(raw_jobs)

        except Exception as e:
            print(f"  [!] Error: {e}")

    print()
    print(f"Total jobs fetched: {len(all_jobs)}")
    print()

    if not all_jobs:
        print("[!] No jobs found")
        sys.exit(0)

    # Normalize and store
    print("Normalizing and storing jobs...")
    normalized_jobs = normalize_job_list(all_jobs)

    new_count = 0
    updated_count = 0

    for job in normalized_jobs:
        try:
            job_id, was_updated = upsert_job(job)
            if was_updated:
                updated_count += 1
            else:
                new_count += 1
        except Exception as e:
            print(f"[!] Error storing job: {e}")

    print(f"[+] Stored {new_count} new jobs")
    print(f"[+] Updated {updated_count} existing jobs")
    print()

    # Display sample jobs
    print("=" * 70)
    print("SAMPLE JOBS FETCHED")
    print("=" * 70)
    print()

    # Show unique jobs (by title + company)
    unique_jobs = {}
    for job in normalized_jobs:
        key = (job['title'], job['company'])
        if key not in unique_jobs:
            unique_jobs[key] = job

    unique_job_list = list(unique_jobs.values())

    for i, job in enumerate(unique_job_list[:10], 1):
        print(f"Job {i}:")
        print(extract_job_summary(job))
        print()

    if len(unique_job_list) > 10:
        print(f"... and {len(unique_job_list) - 10} more unique jobs")
        print()

    # Display database stats
    print("=" * 70)
    total_jobs = len(list_jobs(limit=10000))
    print(f"Total jobs in database: {total_jobs}")
    print()

    print("=" * 70)
    print("[+] Skill-based job fetching complete!")
    print()
    print("Next steps:")
    print("  - Review jobs in SQLite database")
    print("  - Start Phase 4: Match these jobs against your profile!")
    print("=" * 70)


if __name__ == "__main__":
    main()
