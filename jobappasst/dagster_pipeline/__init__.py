"""
Dagster Pipeline for Job Application Assistant

This module provides automated orchestration for:
- Daily job fetching for all profiles
- Automatic job-profile matching/scoring
- Scheduled execution with configurable timing
"""

from dagster import Definitions, ScheduleDefinition

from .assets import (
    all_profiles,
    fetched_jobs,
    scored_matches,
    daily_job_pipeline
)
from .resources import JSearchResource, DatabaseResource


# Define the daily schedule - runs at 6 AM every day
daily_schedule = ScheduleDefinition(
    job=daily_job_pipeline,
    cron_schedule="0 6 * * *",  # 6:00 AM daily
    execution_timezone="America/Chicago",
)


# Dagster Definitions - the main entry point
defs = Definitions(
    assets=[all_profiles, fetched_jobs, scored_matches],
    jobs=[daily_job_pipeline],
    schedules=[daily_schedule],
    resources={
        "jsearch": JSearchResource(),
        "database": DatabaseResource(),
    }
)
