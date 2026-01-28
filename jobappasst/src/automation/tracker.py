"""Application tracking and database updates"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class ApplicationStatus(Enum):
    """Application status enum"""
    DRAFT = 'draft'
    APPLIED = 'applied'
    INTERVIEWING = 'interviewing'
    REJECTED = 'rejected'
    OFFER = 'offer'


def track_application(
    profile_id: int,
    job_id: int,
    status: ApplicationStatus = ApplicationStatus.DRAFT,
    notes: Optional[str] = None
) -> int:
    """
    Track a job application in the database.

    Args:
        profile_id: Profile ID
        job_id: Job ID
        status: Application status
        notes: Optional notes about the application

    Returns:
        int: Application ID
    """
    # Import here to avoid circular dependency
    from ..db import get_db
    import json

    with get_db() as conn:
        # Check if application already exists
        cursor = conn.execute("""
            SELECT id, status FROM applications
            WHERE profile_id = ? AND job_id = ?
        """, (profile_id, job_id))

        existing = cursor.fetchone()

        if existing:
            # Update existing application
            app_id = existing['id']
            conn.execute("""
                UPDATE applications
                SET status = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, notes, app_id))
        else:
            # Create new application
            cursor = conn.execute("""
                INSERT INTO applications
                (profile_id, job_id, status, notes)
                VALUES (?, ?, ?, ?)
            """, (profile_id, job_id, status.value, notes))
            app_id = cursor.lastrowid

        return app_id


def get_application(profile_id: int, job_id: int) -> Optional[Dict[str, Any]]:
    """
    Get application details.

    Args:
        profile_id: Profile ID
        job_id: Job ID

    Returns:
        dict: Application data or None
    """
    from ..db import get_db

    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM applications
            WHERE profile_id = ? AND job_id = ?
        """, (profile_id, job_id))

        row = cursor.fetchone()
        return dict(row) if row else None


def list_applications(
    profile_id: int,
    status: Optional[ApplicationStatus] = None,
    limit: int = 50
) -> list:
    """
    List applications for a profile.

    Args:
        profile_id: Profile ID
        status: Filter by status (optional)
        limit: Maximum number of results

    Returns:
        list: List of application dictionaries
    """
    from ..db import get_db

    with get_db() as conn:
        if status:
            cursor = conn.execute("""
                SELECT a.*, j.title, j.company, j.location
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.profile_id = ? AND a.status = ?
                ORDER BY a.applied_at DESC
                LIMIT ?
            """, (profile_id, status.value, limit))
        else:
            cursor = conn.execute("""
                SELECT a.*, j.title, j.company, j.location
                FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE a.profile_id = ?
                ORDER BY a.applied_at DESC
                LIMIT ?
            """, (profile_id, limit))

        return [dict(row) for row in cursor.fetchall()]


def update_application_status(
    application_id: int,
    status: ApplicationStatus,
    notes: Optional[str] = None
) -> bool:
    """
    Update application status.

    Args:
        application_id: Application ID
        status: New status
        notes: Optional notes

    Returns:
        bool: True if update successful
    """
    from ..db import get_db

    with get_db() as conn:
        if notes:
            conn.execute("""
                UPDATE applications
                SET status = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, notes, application_id))
        else:
            conn.execute("""
                UPDATE applications
                SET status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status.value, application_id))

        return True


def get_application_stats(profile_id: int) -> Dict[str, int]:
    """
    Get application statistics for a profile.

    Args:
        profile_id: Profile ID

    Returns:
        dict: Statistics by status
    """
    from ..db import get_db

    with get_db() as conn:
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE profile_id = ?
            GROUP BY status
        """, (profile_id,))

        stats = {status.value: 0 for status in ApplicationStatus}
        for row in cursor.fetchall():
            stats[row['status']] = row['count']

        stats['total'] = sum(stats.values())
        return stats


def schedule_interview(
    application_id: int,
    interview_date: str,
    interview_notes: Optional[str] = None
) -> bool:
    """
    Schedule an interview for an application.

    Args:
        application_id: Application ID
        interview_date: Interview date (YYYY-MM-DD HH:MM format)
        interview_notes: Optional notes about the interview

    Returns:
        bool: True if update successful
    """
    from ..db import get_db

    with get_db() as conn:
        conn.execute("""
            UPDATE applications
            SET interview_date = ?,
                interview_notes = ?,
                status = 'interviewing',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (interview_date, interview_notes, application_id))

        return True


def set_follow_up(
    application_id: int,
    follow_up_date: str,
    notes: Optional[str] = None
) -> bool:
    """
    Set a follow-up reminder for an application.

    Args:
        application_id: Application ID
        follow_up_date: Follow-up date (YYYY-MM-DD format)
        notes: Optional notes to append

    Returns:
        bool: True if update successful
    """
    from ..db import get_db

    with get_db() as conn:
        if notes:
            conn.execute("""
                UPDATE applications
                SET follow_up_date = ?,
                    notes = COALESCE(notes || '\n' || ?, ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (follow_up_date, notes, notes, application_id))
        else:
            conn.execute("""
                UPDATE applications
                SET follow_up_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (follow_up_date, application_id))

        return True


def get_upcoming_interviews(profile_id: int, days_ahead: int = 7) -> list:
    """
    Get upcoming interviews for a profile.

    Args:
        profile_id: Profile ID
        days_ahead: Number of days to look ahead

    Returns:
        list: List of applications with upcoming interviews
    """
    from ..db import get_db

    with get_db() as conn:
        cursor = conn.execute("""
            SELECT a.*, j.title, j.company, j.location
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.profile_id = ?
              AND a.interview_date IS NOT NULL
              AND DATE(a.interview_date) >= DATE('now')
              AND DATE(a.interview_date) <= DATE('now', '+' || ? || ' days')
            ORDER BY a.interview_date ASC
        """, (profile_id, days_ahead))

        return [dict(row) for row in cursor.fetchall()]


def get_pending_follow_ups(profile_id: int) -> list:
    """
    Get applications with pending follow-ups (due today or past due).

    Args:
        profile_id: Profile ID

    Returns:
        list: List of applications needing follow-up
    """
    from ..db import get_db

    with get_db() as conn:
        cursor = conn.execute("""
            SELECT a.*, j.title, j.company, j.location
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.profile_id = ?
              AND a.follow_up_date IS NOT NULL
              AND DATE(a.follow_up_date) <= DATE('now')
              AND a.status NOT IN ('rejected', 'offer')
            ORDER BY a.follow_up_date ASC
        """, (profile_id,))

        return [dict(row) for row in cursor.fetchall()]
