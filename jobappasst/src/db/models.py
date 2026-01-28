"""Database table definitions for Job Application Assistant"""

import sqlite3
from datetime import datetime
from typing import Optional

from .connection import get_db


# ============================================================================
# TABLE CREATION SQL
# ============================================================================

CREATE_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT,
    summary TEXT,
    raw_json TEXT,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SKILLS_TABLE = """
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('technical', 'soft', 'tool', 'concept')),
    level TEXT CHECK(level IN ('beginner', 'intermediate', 'advanced')),
    years REAL,
    context TEXT,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
"""

CREATE_EXPERIENCE_TABLE = """
CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    industry TEXT,
    start_date TEXT,
    end_date TEXT,
    responsibilities TEXT,
    accomplishments TEXT,
    skills_used TEXT,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);
"""

CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT UNIQUE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    remote BOOLEAN DEFAULT 0,
    description TEXT,
    requirements TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    apply_url TEXT,
    source TEXT,
    posted_date TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT
);
"""

CREATE_JOB_MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS job_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score REAL CHECK(match_score >= 0 AND match_score <= 100),
    matched_skills TEXT,
    missing_skills TEXT,
    notes TEXT,
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE(profile_id, job_id)
);
"""

CREATE_APPLICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'applied', 'interviewing', 'rejected', 'offer')),
    applied_date TEXT,
    cover_letter TEXT,
    resume_version TEXT,
    notes TEXT,
    follow_up_date TEXT,
    interview_date TEXT,
    interview_notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
"""

# ============================================================================
# INDEX CREATION SQL (for performance)
# ============================================================================

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_skills_profile ON skills(profile_id);",
    "CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);",
    "CREATE INDEX IF NOT EXISTS idx_experience_profile ON experience(profile_id);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_external_id ON jobs(external_id);",
    "CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);",
    "CREATE INDEX IF NOT EXISTS idx_job_matches_profile ON job_matches(profile_id);",
    "CREATE INDEX IF NOT EXISTS idx_job_matches_job ON job_matches(job_id);",
    "CREATE INDEX IF NOT EXISTS idx_job_matches_score ON job_matches(match_score DESC);",
    "CREATE INDEX IF NOT EXISTS idx_applications_profile ON applications(profile_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);",
    "CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);",
]


# ============================================================================
# TABLE CREATION FUNCTIONS
# ============================================================================

def create_all_tables(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Create all database tables and indexes.

    Args:
        conn: Optional database connection. If None, creates a new connection.

    Tables created:
        - profiles: User profile data
        - skills: Skills linked to profiles
        - experience: Work experience linked to profiles
        - jobs: Job listings
        - job_matches: Matching scores between profiles and jobs
        - applications: Application tracking
    """
    close_conn = False

    if conn is None:
        from .connection import get_connection
        conn = get_connection()
        close_conn = True

    try:
        # Create tables
        conn.execute(CREATE_PROFILES_TABLE)
        print("[+] Created table: profiles")

        conn.execute(CREATE_SKILLS_TABLE)
        print("[+] Created table: skills")

        conn.execute(CREATE_EXPERIENCE_TABLE)
        print("[+] Created table: experience")

        conn.execute(CREATE_JOBS_TABLE)
        print("[+] Created table: jobs")

        conn.execute(CREATE_JOB_MATCHES_TABLE)
        print("[+] Created table: job_matches")

        conn.execute(CREATE_APPLICATIONS_TABLE)
        print("[+] Created table: applications")

        # Create indexes
        for index_sql in CREATE_INDEXES:
            conn.execute(index_sql)
        print(f"[+] Created {len(CREATE_INDEXES)} indexes for performance")

        conn.commit()
        print("\n[+] All tables and indexes created successfully!")

    except sqlite3.Error as e:
        print(f"[!] Error creating tables: {e}")
        conn.rollback()
        raise

    finally:
        if close_conn:
            conn.close()


def drop_all_tables(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Drop all database tables. USE WITH CAUTION!

    Args:
        conn: Optional database connection. If None, creates a new connection.

    Warning:
        This will delete all data in the database.
    """
    close_conn = False

    if conn is None:
        from .connection import get_connection
        conn = get_connection()
        close_conn = True

    try:
        tables = ['applications', 'job_matches', 'jobs', 'experience', 'skills', 'profiles']

        for table in tables:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"[+] Dropped table: {table}")

        conn.commit()
        print("\n[+] All tables dropped successfully!")

    except sqlite3.Error as e:
        print(f"[!] Error dropping tables: {e}")
        conn.rollback()
        raise

    finally:
        if close_conn:
            conn.close()


def get_table_info(conn: Optional[sqlite3.Connection] = None) -> dict:
    """
    Get information about all tables in the database.

    Args:
        conn: Optional database connection. If None, creates a new connection.

    Returns:
        dict: Dictionary with table names as keys and row counts as values
    """
    close_conn = False

    if conn is None:
        from .connection import get_connection
        conn = get_connection()
        close_conn = True

    try:
        tables = ['profiles', 'skills', 'experience', 'jobs', 'job_matches', 'applications']
        info = {}

        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            info[table] = count

        return info

    finally:
        if close_conn:
            conn.close()
