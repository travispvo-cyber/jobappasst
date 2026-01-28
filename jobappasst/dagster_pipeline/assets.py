"""
Dagster Assets for Job Application Assistant

Assets represent data artifacts that are produced by the pipeline:
- all_profiles: All user profiles in the database
- fetched_jobs: Jobs fetched from JSearch API
- scored_matches: Match scores between profiles and jobs
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

from dagster import (
    asset,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    define_asset_job,
    AssetSelection,
)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@asset(
    description="Load all profiles from the database",
    group_name="job_pipeline",
)
def all_profiles(context: AssetExecutionContext) -> List[Dict[str, Any]]:
    """
    Load all user profiles from the database.

    Returns:
        List of profile dictionaries with skills
    """
    from src.db.queries import list_profiles, get_profile_skills

    profiles = list_profiles()
    context.log.info(f"Loaded {len(profiles)} profiles")

    # Enrich with skills
    enriched_profiles = []
    for profile in profiles:
        skills = get_profile_skills(profile['id'])
        profile['skills'] = [s['name'] for s in skills]
        enriched_profiles.append(profile)
        context.log.info(f"Profile {profile['name']}: {len(profile['skills'])} skills")

    return enriched_profiles


@asset(
    deps=[all_profiles],
    description="Fetch jobs from JSearch API based on profile skills",
    group_name="job_pipeline",
)
def fetched_jobs(context: AssetExecutionContext, all_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fetch jobs from JSearch API for each profile's skills.

    Args:
        all_profiles: List of profiles with skills

    Returns:
        Dictionary with fetch statistics
    """
    from src.jobs.jsearch_client import JSearchClient
    from src.db.queries import insert_job

    client = JSearchClient()
    stats = {
        'total_fetched': 0,
        'total_saved': 0,
        'by_profile': {}
    }

    for profile in all_profiles:
        profile_id = profile['id']
        profile_name = profile['name']
        skills = profile.get('skills', [])

        if not skills:
            context.log.warning(f"Profile {profile_name} has no skills, skipping")
            continue

        # Use top 3 skills as search query
        top_skills = skills[:3]
        query = ' '.join(top_skills)

        context.log.info(f"Fetching jobs for {profile_name} with query: {query}")

        try:
            jobs = client.search_jobs(
                query=query,
                location="USA",
                remote_only=True,
                num_pages=2
            )

            fetched_count = len(jobs)
            saved_count = 0

            for job in jobs:
                try:
                    insert_job(job)
                    saved_count += 1
                except Exception as e:
                    # Skip duplicates
                    pass

            stats['total_fetched'] += fetched_count
            stats['total_saved'] += saved_count
            stats['by_profile'][profile_name] = {
                'fetched': fetched_count,
                'saved': saved_count
            }

            context.log.info(f"Profile {profile_name}: fetched {fetched_count}, saved {saved_count} new jobs")

        except Exception as e:
            context.log.error(f"Error fetching jobs for {profile_name}: {e}")
            stats['by_profile'][profile_name] = {'error': str(e)}

    context.log.info(f"Total: fetched {stats['total_fetched']}, saved {stats['total_saved']} jobs")
    return stats


@asset(
    deps=[all_profiles, fetched_jobs],
    description="Score job matches for all profiles",
    group_name="job_pipeline",
)
def scored_matches(
    context: AssetExecutionContext,
    all_profiles: List[Dict[str, Any]],
    fetched_jobs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Score all unscored jobs against each profile.

    Args:
        all_profiles: List of profiles with skills
        fetched_jobs: Stats from job fetching (dependency only)

    Returns:
        Dictionary with scoring statistics
    """
    from src.matching.scorer import score_job_for_profile
    from src.db.queries import insert_match, get_profile_skills
    from src.db import get_db
    import json

    stats = {
        'total_scored': 0,
        'by_profile': {}
    }

    for profile in all_profiles:
        profile_id = profile['id']
        profile_name = profile['name']

        # Get unscored jobs for this profile
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT j.* FROM jobs j
                LEFT JOIN job_matches jm ON j.id = jm.job_id AND jm.profile_id = ?
                WHERE jm.id IS NULL
            """, (profile_id,))
            unscored_jobs = [dict(row) for row in cursor.fetchall()]

        context.log.info(f"Profile {profile_name}: {len(unscored_jobs)} unscored jobs")

        scored_count = 0
        for job in unscored_jobs:
            try:
                # Get profile skills
                skills = get_profile_skills(profile_id)
                skill_names = [s['name'] for s in skills]

                # Score the job
                result = score_job_for_profile(profile_id, job['id'])

                if result:
                    match_data = {
                        'profile_id': profile_id,
                        'job_id': job['id'],
                        'match_score': result['score'],
                        'matched_skills': json.dumps(result.get('matched_skills', [])),
                        'missing_skills': json.dumps(result.get('missing_skills', [])),
                    }
                    insert_match(match_data)
                    scored_count += 1

            except Exception as e:
                context.log.warning(f"Error scoring job {job['id']} for {profile_name}: {e}")

        stats['total_scored'] += scored_count
        stats['by_profile'][profile_name] = scored_count
        context.log.info(f"Profile {profile_name}: scored {scored_count} jobs")

    context.log.info(f"Total: scored {stats['total_scored']} job matches")
    return stats


# Define the daily job that runs all assets in sequence
daily_job_pipeline = define_asset_job(
    name="daily_job_pipeline",
    selection=AssetSelection.groups("job_pipeline"),
    description="Daily pipeline: fetch jobs and score matches for all profiles"
)
