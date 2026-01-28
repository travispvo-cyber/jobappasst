#!/usr/bin/env python3
"""Migration script to add interview fields to applications table"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_db


def migrate():
    """Add interview_date and interview_notes columns to applications table"""

    with get_db() as conn:
        # Check existing columns
        cursor = conn.execute("PRAGMA table_info(applications)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add interview_date if not exists
        if 'interview_date' not in columns:
            conn.execute("ALTER TABLE applications ADD COLUMN interview_date TEXT")
            print("[+] Added column: interview_date")
        else:
            print("[=] Column already exists: interview_date")

        # Add interview_notes if not exists
        if 'interview_notes' not in columns:
            conn.execute("ALTER TABLE applications ADD COLUMN interview_notes TEXT")
            print("[+] Added column: interview_notes")
        else:
            print("[=] Column already exists: interview_notes")

        print("\n[+] Migration complete!")


if __name__ == "__main__":
    migrate()
