"""SQLite connection management for Job Application Assistant"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


# Database file path - relative to project root
DB_PATH = Path(__file__).parent.parent.parent / "data" / "job_assistant.db"


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Returns:
        sqlite3.Connection: Database connection object

    Note:
        Remember to close the connection when done, or use the
        get_db() context manager for automatic cleanup.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Enable foreign key constraints
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row

    return conn


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.

    Automatically commits on success and rolls back on error.
    Always closes the connection.

    Usage:
        with get_db() as conn:
            conn.execute("SELECT * FROM profiles")

    Yields:
        sqlite3.Connection: Database connection
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize the database by creating the database file if it doesn't exist.

    This doesn't create tables - use models.create_all_tables() for that.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create database file if it doesn't exist
    if not DB_PATH.exists():
        conn = get_connection()
        conn.close()
        print(f"[+] Database file created at: {DB_PATH}")
    else:
        print(f"[+] Database file already exists at: {DB_PATH}")


def get_db_path() -> Path:
    """
    Get the path to the database file.

    Returns:
        Path: Path to job_assistant.db
    """
    return DB_PATH
