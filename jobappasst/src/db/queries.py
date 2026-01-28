"""Common database queries for Job Application Assistant"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List
from .connection import get_db


def store_profile(profile_data: Dict[str, Any], source_file: str) -> int:
    """
    Store a parsed profile and related data in the database.

    Args:
        profile_data: Structured profile data from resume parser
        source_file: Original resume filename

    Returns:
        int: Profile ID of the inserted record

    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_db() as conn:
        # Insert profile
        cursor = conn.execute("""
            INSERT INTO profiles (name, email, phone, location, summary, raw_json, source_file, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            profile_data.get('name'),
            profile_data.get('email'),
            profile_data.get('phone'),
            profile_data.get('location'),
            profile_data.get('summary'),
            json.dumps(profile_data),  # Store full JSON
            source_file
        ))

        profile_id = cursor.lastrowid

        # Insert skills
        skills = profile_data.get('skills', [])
        for skill in skills:
            conn.execute("""
                INSERT INTO skills (profile_id, name, category, level, years, context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                skill.get('name'),
                skill.get('category'),
                skill.get('level'),
                skill.get('years'),
                skill.get('context')
            ))

        # Insert experience
        experiences = profile_data.get('experience', [])
        for exp in experiences:
            conn.execute("""
                INSERT INTO experience
                (profile_id, title, company, industry, start_date, end_date,
                 responsibilities, accomplishments, skills_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                exp.get('title'),
                exp.get('company'),
                exp.get('industry'),
                exp.get('start_date'),
                exp.get('end_date'),
                json.dumps(exp.get('responsibilities', [])),
                json.dumps(exp.get('accomplishments', [])),
                json.dumps(exp.get('skills_used', []))
            ))

        return profile_id


def get_profile(profile_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a complete profile with all related data.

    Args:
        profile_id: ID of the profile to retrieve

    Returns:
        dict: Complete profile data with skills and experience, or None if not found
    """
    with get_db() as conn:
        # Get profile
        cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        profile_row = cursor.fetchone()

        if not profile_row:
            return None

        # Convert to dict
        profile = dict(profile_row)

        # Get skills
        cursor = conn.execute("SELECT * FROM skills WHERE profile_id = ?", (profile_id,))
        skills = [dict(row) for row in cursor.fetchall()]
        profile['skills'] = skills

        # Get experience
        cursor = conn.execute("SELECT * FROM experience WHERE profile_id = ?", (profile_id,))
        experiences = []
        for row in cursor.fetchall():
            exp = dict(row)
            # Parse JSON fields
            exp['responsibilities'] = json.loads(exp['responsibilities']) if exp['responsibilities'] else []
            exp['accomplishments'] = json.loads(exp['accomplishments']) if exp['accomplishments'] else []
            exp['skills_used'] = json.loads(exp['skills_used']) if exp['skills_used'] else []
            experiences.append(exp)
        profile['experience'] = experiences

        return profile


def list_profiles() -> list[Dict[str, Any]]:
    """
    List all profiles with basic information.

    Returns:
        list: List of profile dictionaries
    """
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, name, email, location, source_file, created_at
            FROM profiles
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def delete_profile(profile_id: int) -> bool:
    """
    Delete a profile and all related data (skills, experience).

    Args:
        profile_id: ID of the profile to delete

    Returns:
        bool: True if profile was deleted, False if not found
    """
    with get_db() as conn:
        # Check if profile exists
        cursor = conn.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            return False

        # Delete profile (CASCADE will delete related data)
        conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        return True


def update_profile(profile_id: int, profile_data: Dict[str, Any]) -> bool:
    """
    Update an existing profile.

    Args:
        profile_id: ID of the profile to update
        profile_data: New profile data

    Returns:
        bool: True if updated, False if profile not found
    """
    with get_db() as conn:
        # Check if profile exists
        cursor = conn.execute("SELECT id FROM profiles WHERE id = ?", (profile_id,))
        if not cursor.fetchone():
            return False

        # Update profile
        conn.execute("""
            UPDATE profiles
            SET name = ?, email = ?, phone = ?, location = ?, summary = ?,
                raw_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            profile_data.get('name'),
            profile_data.get('email'),
            profile_data.get('phone'),
            profile_data.get('location'),
            profile_data.get('summary'),
            json.dumps(profile_data),
            profile_id
        ))

        # Delete and re-insert skills
        conn.execute("DELETE FROM skills WHERE profile_id = ?", (profile_id,))
        for skill in profile_data.get('skills', []):
            conn.execute("""
                INSERT INTO skills (profile_id, name, category, level, years, context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                skill.get('name'),
                skill.get('category'),
                skill.get('level'),
                skill.get('years'),
                skill.get('context')
            ))

        # Delete and re-insert experience
        conn.execute("DELETE FROM experience WHERE profile_id = ?", (profile_id,))
        for exp in profile_data.get('experience', []):
            conn.execute("""
                INSERT INTO experience
                (profile_id, title, company, industry, start_date, end_date,
                 responsibilities, accomplishments, skills_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                exp.get('title'),
                exp.get('company'),
                exp.get('industry'),
                exp.get('start_date'),
                exp.get('end_date'),
                json.dumps(exp.get('responsibilities', [])),
                json.dumps(exp.get('accomplishments', [])),
                json.dumps(exp.get('skills_used', []))
            ))

        return True


def find_profile_by_source(source_file: str) -> Optional[Dict[str, Any]]:
    """
    Find a profile by its source filename.

    Args:
        source_file: Resume filename to search for

    Returns:
        dict: Profile dict with id, name, email, etc., or None if not found
    """
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, name, email, source_file, created_at, updated_at
            FROM profiles
            WHERE source_file = ?
        """, (source_file,))
        row = cursor.fetchone()
        return dict(row) if row else None


def upsert_profile(profile_data: Dict[str, Any], source_file: str) -> tuple[int, bool]:
    """
    Insert or update a profile based on source_file.

    If a profile with the same source_file exists, update it.
    Otherwise, create a new profile.

    Args:
        profile_data: Structured profile data from resume parser
        source_file: Original resume filename

    Returns:
        tuple: (profile_id, was_updated) where was_updated is True if existing profile was updated

    Raises:
        sqlite3.Error: If database operation fails
    """
    # Check if profile already exists
    existing = find_profile_by_source(source_file)

    if existing:
        # Update existing profile
        profile_id = existing['id']
        update_profile(profile_id, profile_data)
        return (profile_id, True)
    else:
        # Create new profile
        profile_id = store_profile(profile_data, source_file)
        return (profile_id, False)


# ============================================================================
# JOB QUERIES
# ============================================================================

def store_job(job_data: Dict[str, Any]) -> int:
    """
    Store a job listing in the database.

    Args:
        job_data: Normalized job data

    Returns:
        int: Job ID of the inserted record

    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO jobs
            (external_id, title, company, location, remote, description,
             requirements, salary_min, salary_max, apply_url, source, posted_date, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_data.get('external_id'),
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            1 if job_data.get('remote') else 0,
            job_data.get('description'),
            json.dumps(job_data.get('requirements', [])),
            job_data.get('salary_min'),
            job_data.get('salary_max'),
            job_data.get('apply_url'),
            job_data.get('source'),
            job_data.get('posted_date'),
            json.dumps(job_data.get('raw_json', {}))
        ))

        return cursor.lastrowid


def find_job_by_external_id(external_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a job by its external (JSearch) ID.

    Args:
        external_id: External job ID from JSearch

    Returns:
        dict: Job dict or None if not found
    """
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT id, external_id, title, company, location, remote,
                   salary_min, salary_max, posted_date, fetched_at
            FROM jobs
            WHERE external_id = ?
        """, (external_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def upsert_job(job_data: Dict[str, Any]) -> tuple[int, bool]:
    """
    Insert or update a job based on external_id.

    Args:
        job_data: Normalized job data

    Returns:
        tuple: (job_id, was_updated) where was_updated is True if existing job was updated

    Raises:
        sqlite3.Error: If database operation fails
    """
    external_id = job_data.get('external_id')

    if not external_id:
        # No external ID, just insert
        job_id = store_job(job_data)
        return (job_id, False)

    # Check if job already exists
    existing = find_job_by_external_id(external_id)

    if existing:
        # Update existing job
        with get_db() as conn:
            conn.execute("""
                UPDATE jobs
                SET title = ?, company = ?, location = ?, remote = ?,
                    description = ?, requirements = ?, salary_min = ?,
                    salary_max = ?, apply_url = ?, source = ?,
                    posted_date = ?, raw_json = ?, fetched_at = CURRENT_TIMESTAMP
                WHERE external_id = ?
            """, (
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                1 if job_data.get('remote') else 0,
                job_data.get('description'),
                json.dumps(job_data.get('requirements', [])),
                job_data.get('salary_min'),
                job_data.get('salary_max'),
                job_data.get('apply_url'),
                job_data.get('source'),
                job_data.get('posted_date'),
                json.dumps(job_data.get('raw_json', {})),
                external_id
            ))

        return (existing['id'], True)
    else:
        # Create new job
        job_id = store_job(job_data)
        return (job_id, False)


def list_jobs(limit: int = 50, remote_only: bool = False) -> List[Dict[str, Any]]:
    """
    List recent jobs from the database.

    Args:
        limit: Maximum number of jobs to return
        remote_only: Only return remote jobs

    Returns:
        list: List of job dictionaries
    """
    with get_db() as conn:
        if remote_only:
            cursor = conn.execute("""
                SELECT id, external_id, title, company, location, remote,
                       description, requirements, salary_min, salary_max,
                       source, posted_date, fetched_at
                FROM jobs
                WHERE remote = 1
                ORDER BY fetched_at DESC
                LIMIT ?
            """, (limit,))
        else:
            cursor = conn.execute("""
                SELECT id, external_id, title, company, location, remote,
                       description, requirements, salary_min, salary_max,
                       source, posted_date, fetched_at
                FROM jobs
                ORDER BY fetched_at DESC
                LIMIT ?
            """, (limit,))

        jobs = []
        for row in cursor.fetchall():
            job = dict(row)
            # Parse JSON requirements field
            job['requirements'] = json.loads(job['requirements']) if job['requirements'] else []
            jobs.append(job)

        return jobs


def get_job(job_id: int) -> Optional[Dict[str, Any]]:
    """
    Get full job details by database ID.

    Args:
        job_id: Database job ID

    Returns:
        dict: Complete job data or None if not found
    """
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()

        if not row:
            return None

        job = dict(row)
        # Parse JSON fields
        job['requirements'] = json.loads(job['requirements']) if job['requirements'] else []
        job['raw_json'] = json.loads(job['raw_json']) if job['raw_json'] else {}

        return job


# ============================================================================
# JOB MATCH QUERIES
# ============================================================================

def store_job_match(
    profile_id: int,
    job_id: int,
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    notes: str
) -> int:
    """
    Store a job match score in the database.

    Args:
        profile_id: Profile ID
        job_id: Job ID
        match_score: Match score (0-100)
        matched_skills: List of matched skills
        missing_skills: List of missing skills
        notes: Analysis notes

    Returns:
        int: Job match ID

    Raises:
        sqlite3.Error: If database operation fails
    """
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO job_matches
            (profile_id, job_id, match_score, matched_skills, missing_skills, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            job_id,
            match_score,
            json.dumps(matched_skills),
            json.dumps(missing_skills),
            notes
        ))

        return cursor.lastrowid


def upsert_job_match(
    profile_id: int,
    job_id: int,
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    notes: str
) -> tuple[int, bool]:
    """
    Insert or update a job match.

    Args:
        profile_id: Profile ID
        job_id: Job ID
        match_score: Match score (0-100)
        matched_skills: List of matched skills
        missing_skills: List of missing skills
        notes: Analysis notes

    Returns:
        tuple: (match_id, was_updated)
    """
    with get_db() as conn:
        # Check if match exists
        cursor = conn.execute("""
            SELECT id FROM job_matches
            WHERE profile_id = ? AND job_id = ?
        """, (profile_id, job_id))

        existing = cursor.fetchone()

        if existing:
            # Update existing match
            conn.execute("""
                UPDATE job_matches
                SET match_score = ?, matched_skills = ?, missing_skills = ?,
                    notes = ?, scored_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                match_score,
                json.dumps(matched_skills),
                json.dumps(missing_skills),
                notes,
                existing['id']
            ))
            return (existing['id'], True)
        else:
            # Create new match
            match_id = store_job_match(
                profile_id, job_id, match_score,
                matched_skills, missing_skills, notes
            )
            return (match_id, False)


def get_matches_for_profile(
    profile_id: int,
    min_score: float = 0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get all job matches for a profile, ordered by score.

    Args:
        profile_id: Profile ID
        min_score: Minimum match score to include
        limit: Maximum number of matches to return

    Returns:
        list: List of match dictionaries with job details
    """
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT
                jm.id,
                jm.match_score,
                jm.matched_skills,
                jm.missing_skills,
                jm.notes,
                jm.scored_at,
                j.id as job_id,
                j.title,
                j.company,
                j.location,
                j.remote,
                j.salary_min,
                j.salary_max,
                j.apply_url,
                j.posted_date
            FROM job_matches jm
            JOIN jobs j ON jm.job_id = j.id
            WHERE jm.profile_id = ? AND jm.match_score >= ?
            ORDER BY jm.match_score DESC
            LIMIT ?
        """, (profile_id, min_score, limit))

        matches = []
        for row in cursor.fetchall():
            match = dict(row)
            # Parse JSON fields
            match['matched_skills'] = json.loads(match['matched_skills']) if match['matched_skills'] else []
            match['missing_skills'] = json.loads(match['missing_skills']) if match['missing_skills'] else []
            matches.append(match)

        return matches


def get_top_matches(profile_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top job matches for a profile.

    Args:
        profile_id: Profile ID
        limit: Number of top matches to return

    Returns:
        list: List of top match dictionaries
    """
    return get_matches_for_profile(profile_id, min_score=50, limit=limit)


def delete_matches_for_profile(profile_id: int) -> int:
    """
    Delete all job matches for a profile.

    Args:
        profile_id: Profile ID

    Returns:
        int: Number of matches deleted
    """
    with get_db() as conn:
        cursor = conn.execute("""
            DELETE FROM job_matches WHERE profile_id = ?
        """, (profile_id,))
        return cursor.rowcount
