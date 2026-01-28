# Dagster Pipeline - Job Application Assistant

This module provides automated orchestration for the Job Application Assistant using Dagster.

## Features

- **Daily Job Fetching**: Automatically fetches jobs from JSearch API for all profiles
- **Automatic Matching**: Scores all new jobs against each profile's skills
- **Scheduled Execution**: Runs daily at 6 AM (configurable)

## Installation

```bash
# Install Dagster and dependencies
pip install dagster dagster-webserver

# Or add to requirements
pip install -r requirements.txt
```

## Usage

### Run the Dagster Web UI

```bash
# From the project root
dagster dev -m dagster_pipeline

# Or specify the module path
dagster dev --working-directory . -m dagster_pipeline
```

Then open http://localhost:3000 in your browser.

### Run Pipeline Manually

```bash
# Materialize all assets
dagster asset materialize -m dagster_pipeline --select "*"

# Run specific job
dagster job execute -m dagster_pipeline -j daily_job_pipeline
```

### Run from Python

```python
from dagster_pipeline import defs

# Execute the daily pipeline
result = defs.get_job_def("daily_job_pipeline").execute_in_process()
```

## Assets

### all_profiles
Loads all user profiles from the database with their skills.

### fetched_jobs
Fetches jobs from JSearch API based on each profile's top skills.
- Uses top 3 skills as search query
- Fetches 2 pages of results per profile
- Filters for remote jobs only

### scored_matches
Scores all unscored jobs against each profile.
- Uses the matching engine's scoring algorithm
- Stores matched and missing skills

## Schedule

The default schedule runs at **6:00 AM Central Time** daily.

To modify the schedule, edit `__init__.py`:

```python
daily_schedule = ScheduleDefinition(
    job=daily_job_pipeline,
    cron_schedule="0 6 * * *",  # Change this cron expression
    execution_timezone="America/Chicago",
)
```

Common cron patterns:
- `0 6 * * *` - Daily at 6 AM
- `0 */4 * * *` - Every 4 hours
- `0 6 * * 1-5` - Weekdays at 6 AM
- `0 6,18 * * *` - Twice daily at 6 AM and 6 PM

## Configuration

Environment variables:
- `RAPIDAPI_KEY`: API key for JSearch (required)
- `ANTHROPIC_API_KEY`: API key for Claude (optional, for enhanced matching)

## Monitoring

The Dagster UI provides:
- Asset lineage visualization
- Run history and logs
- Schedule management
- Alerts and notifications
