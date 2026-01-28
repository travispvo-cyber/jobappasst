"""Normalize job data from JSearch API to our database schema"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


def normalize_job_data(raw_job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a job from JSearch API format to our database schema.

    Args:
        raw_job: Raw job data from JSearch API

    Returns:
        dict: Normalized job data matching our database schema

    Schema mapping:
        external_id: job_id
        title: job_title
        company: employer_name
        location: job_city + job_state + job_country
        remote: job_is_remote
        description: job_description
        requirements: job_required_skills or job_highlights.Qualifications
        salary_min: job_min_salary
        salary_max: job_max_salary
        apply_url: job_apply_link
        source: job_publisher
        posted_date: job_posted_at_datetime_utc
        raw_json: full JSON
    """
    # Extract location
    location_parts = []
    if raw_job.get("job_city"):
        location_parts.append(raw_job["job_city"])
    if raw_job.get("job_state"):
        location_parts.append(raw_job["job_state"])
    if raw_job.get("job_country"):
        location_parts.append(raw_job["job_country"])

    location = ", ".join(location_parts) if location_parts else raw_job.get("job_location", "N/A")

    # Extract requirements
    requirements = []

    # Try job_required_skills first
    if raw_job.get("job_required_skills"):
        requirements.extend(raw_job["job_required_skills"])

    # Try job_highlights.Qualifications
    if raw_job.get("job_highlights") and raw_job["job_highlights"].get("Qualifications"):
        qualifications = raw_job["job_highlights"]["Qualifications"]
        if isinstance(qualifications, list):
            requirements.extend(qualifications)

    # Try job_required_experience
    if raw_job.get("job_required_experience") and raw_job["job_required_experience"].get("required_experience_in_months"):
        months = raw_job["job_required_experience"]["required_experience_in_months"]
        years = months / 12
        requirements.append(f"{years:.1f} years of experience required")

    # Extract salary
    salary_min = raw_job.get("job_min_salary")
    salary_max = raw_job.get("job_max_salary")

    # Extract posted date
    posted_date = None
    if raw_job.get("job_posted_at_datetime_utc"):
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(raw_job["job_posted_at_datetime_utc"].replace("Z", "+00:00"))
            posted_date = dt.strftime("%Y-%m-%d")
        except:
            posted_date = raw_job.get("job_posted_at_datetime_utc", "")[:10]  # Just take YYYY-MM-DD part

    # Normalize to our schema
    normalized = {
        "external_id": raw_job.get("job_id"),
        "title": raw_job.get("job_title", "Untitled"),
        "company": raw_job.get("employer_name", "Unknown"),
        "location": location,
        "remote": bool(raw_job.get("job_is_remote", False)),
        "description": raw_job.get("job_description", ""),
        "requirements": requirements,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "apply_url": raw_job.get("job_apply_link") or raw_job.get("job_google_link"),
        "source": raw_job.get("job_publisher", "JSearch"),
        "posted_date": posted_date,
        "raw_json": raw_job  # Store full JSON for reference
    }

    return normalized


def normalize_job_list(raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize a list of jobs from JSearch API.

    Args:
        raw_jobs: List of raw job data from JSearch API

    Returns:
        list: List of normalized job dictionaries
    """
    return [normalize_job_data(job) for job in raw_jobs]


def extract_job_summary(job: Dict[str, Any]) -> str:
    """
    Extract a human-readable summary of a job.

    Args:
        job: Normalized job dictionary

    Returns:
        str: Job summary
    """
    lines = []

    lines.append(f"Title: {job['title']}")
    lines.append(f"Company: {job['company']}")
    lines.append(f"Location: {job['location']}")

    if job.get('remote'):
        lines.append("Remote: Yes")

    if job.get('salary_min') or job.get('salary_max'):
        salary_range = []
        if job.get('salary_min'):
            salary_range.append(f"${job['salary_min']:,}")
        if job.get('salary_max'):
            salary_range.append(f"${job['salary_max']:,}")
        lines.append(f"Salary: {' - '.join(salary_range)}")

    if job.get('posted_date'):
        lines.append(f"Posted: {job['posted_date']}")

    if job.get('requirements'):
        lines.append(f"Requirements: {len(job['requirements'])} listed")

    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    # Example raw job from JSearch API
    example_job = {
        "job_id": "abc123",
        "job_title": "Senior Python Developer",
        "employer_name": "Tech Corp",
        "job_city": "Houston",
        "job_state": "TX",
        "job_country": "US",
        "job_is_remote": False,
        "job_description": "We are looking for a senior Python developer...",
        "job_required_skills": ["Python", "Django", "PostgreSQL"],
        "job_min_salary": 120000,
        "job_max_salary": 160000,
        "job_apply_link": "https://example.com/apply",
        "job_publisher": "LinkedIn",
        "job_posted_at_datetime_utc": "2025-01-20T10:00:00Z",
        "job_highlights": {
            "Qualifications": [
                "5+ years Python experience",
                "Bachelor's degree in CS"
            ]
        }
    }

    normalized = normalize_job_data(example_job)

    print("Normalized job:")
    print(json.dumps(normalized, indent=2, default=str))

    print("\n" + "=" * 60)
    print("Job Summary:")
    print("=" * 60)
    print(extract_job_summary(normalized))
