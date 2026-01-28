"""Fetch job listings from JSearch API and store in database"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.jobs.jsearch_client import JSearchClient
from src.jobs.normalizer import normalize_job_list, extract_job_summary
from src.db import upsert_job, list_jobs


def main():
    """Fetch jobs and store in database"""
    print("=" * 70)
    print("Job Application Assistant - Job Fetcher")
    print("=" * 70)
    print()

    # Get search parameters
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_jobs.py <search_query> [options]")
        print()
        print("Options:")
        print("  --location <location>      Location filter (e.g., 'Houston, TX')")
        print("  --remote                   Only fetch remote jobs")
        print("  --type <types>             Employment types (FULLTIME,CONTRACTOR,PARTTIME)")
        print("  --date <filter>            Date filter (all, today, 3days, week, month)")
        print("  --pages <num>              Number of pages to fetch (default: 1)")
        print()
        print("Examples:")
        print("  python scripts/fetch_jobs.py 'Python developer' --location 'Houston, TX'")
        print("  python scripts/fetch_jobs.py 'Data Engineer' --remote --date week")
        print("  python scripts/fetch_jobs.py 'Software Engineer' --type FULLTIME --pages 2")
        sys.exit(1)

    query = sys.argv[1]

    # Parse optional arguments
    location = None
    remote_only = False
    employment_types = None
    date_posted = "all"
    num_pages = 1

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
        elif arg == "--pages" and i + 1 < len(sys.argv):
            num_pages = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    print(f"Search query: {query}")
    if location:
        print(f"Location: {location}")
    if remote_only:
        print("Remote jobs only: Yes")
    if employment_types:
        print(f"Employment types: {employment_types}")
    print(f"Date filter: {date_posted}")
    print(f"Pages to fetch: {num_pages}")
    print()

    # Step 1: Fetch jobs from JSearch API
    print("Step 1: Fetching jobs from JSearch API...")
    try:
        client = JSearchClient()
        response = client.search(
            query=query,
            location=location,
            remote_jobs_only=remote_only,
            employment_types=employment_types,
            date_posted=date_posted,
            num_pages=num_pages
        )

        raw_jobs = response.get("data", [])
        print(f"[+] Fetched {len(raw_jobs)} jobs from API")
        print()

    except Exception as e:
        print(f"[!] Error fetching jobs: {e}")
        print()
        print("Make sure:")
        print("  1. You have set RAPIDAPI_KEY in your .env file")
        print("  2. You have a RapidAPI account with JSearch API access")
        print("  3. You have available API credits")
        sys.exit(1)

    if not raw_jobs:
        print("[!] No jobs found for this search")
        sys.exit(0)

    # Step 2: Normalize job data
    print("Step 2: Normalizing job data...")
    normalized_jobs = normalize_job_list(raw_jobs)
    print(f"[+] Normalized {len(normalized_jobs)} jobs")
    print()

    # Step 3: Store in database
    print("Step 3: Storing jobs in database...")
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
            print(f"[!] Error storing job {job.get('title')}: {e}")

    print(f"[+] Stored {new_count} new jobs")
    print(f"[+] Updated {updated_count} existing jobs")
    print()

    # Step 4: Display sample jobs
    print("=" * 70)
    print("SAMPLE JOBS FETCHED")
    print("=" * 70)
    print()

    # Show first 5 jobs
    for i, job in enumerate(normalized_jobs[:5], 1):
        print(f"Job {i}:")
        print(extract_job_summary(job))
        print(f"Apply: {job['apply_url']}")
        print()

    if len(normalized_jobs) > 5:
        print(f"... and {len(normalized_jobs) - 5} more jobs")
        print()

    # Display database stats
    print("=" * 70)
    print()
    total_jobs = len(list_jobs(limit=10000))
    print(f"Total jobs in database: {total_jobs}")
    print()

    print("=" * 70)
    print("[+] Job fetching complete!")
    print()
    print("Next steps:")
    print("  - View jobs in SQLite database")
    print("  - Start Phase 4: Matching Engine")
    print("=" * 70)


if __name__ == "__main__":
    main()
