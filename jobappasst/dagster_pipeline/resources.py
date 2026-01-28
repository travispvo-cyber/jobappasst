"""
Dagster Resources for Job Application Assistant

Resources provide shared connections and clients that can be
injected into assets and ops.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from dagster import ConfigurableResource, InitResourceContext
from pydantic import Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


class JSearchResource(ConfigurableResource):
    """Resource for JSearch API access"""

    api_key: str = Field(
        default_factory=lambda: os.getenv("RAPIDAPI_KEY", ""),
        description="RapidAPI key for JSearch"
    )
    api_host: str = Field(
        default="jsearch.p.rapidapi.com",
        description="JSearch API host"
    )

    def search_jobs(self, query: str, location: str = "USA", num_pages: int = 1, remote_only: bool = True):
        """
        Search for jobs using JSearch API.

        Args:
            query: Search query (skills or job title)
            location: Location filter
            num_pages: Number of pages to fetch
            remote_only: Filter for remote jobs only

        Returns:
            list: List of job dictionaries
        """
        from src.jobs.jsearch_client import JSearchClient

        client = JSearchClient()
        return client.search_jobs(
            query=query,
            location=location,
            num_pages=num_pages,
            remote_only=remote_only
        )


class DatabaseResource(ConfigurableResource):
    """Resource for database access"""

    db_path: str = Field(
        default_factory=lambda: str(Path(__file__).parent.parent / "data" / "jobapp.db"),
        description="Path to SQLite database"
    )

    def get_all_profiles(self):
        """Get all profiles from database"""
        from src.db.queries import list_profiles
        return list_profiles()

    def get_profile_skills(self, profile_id: int):
        """Get skills for a profile"""
        from src.db.queries import get_profile_skills
        return get_profile_skills(profile_id)

    def save_jobs(self, jobs: list):
        """Save jobs to database"""
        from src.db.queries import insert_job
        saved = 0
        for job in jobs:
            try:
                insert_job(job)
                saved += 1
            except Exception:
                pass  # Skip duplicates
        return saved

    def get_unscored_jobs(self, profile_id: int):
        """Get jobs that haven't been scored for a profile"""
        from src.db import get_db

        with get_db() as conn:
            cursor = conn.execute("""
                SELECT j.* FROM jobs j
                LEFT JOIN job_matches jm ON j.id = jm.job_id AND jm.profile_id = ?
                WHERE jm.id IS NULL
            """, (profile_id,))
            return [dict(row) for row in cursor.fetchall()]

    def save_match(self, profile_id: int, job_id: int, score: float, matched_skills: list, missing_skills: list):
        """Save a job match"""
        from src.db.queries import insert_match
        import json

        match_data = {
            'profile_id': profile_id,
            'job_id': job_id,
            'match_score': score,
            'matched_skills': json.dumps(matched_skills),
            'missing_skills': json.dumps(missing_skills),
        }
        return insert_match(match_data)
