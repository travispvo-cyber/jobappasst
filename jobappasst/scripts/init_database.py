"""Initialize the Job Application Assistant database"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.connection import init_db, get_db_path
from src.db.models import create_all_tables


def main():
    """Initialize the database with all tables"""
    print("=" * 60)
    print("Job Application Assistant - Database Initialization")
    print("=" * 60)
    print()

    # Step 1: Create database file
    print("Step 1: Creating database file...")
    init_db()
    print()

    # Step 2: Create tables
    print("Step 2: Creating tables and indexes...")
    create_all_tables()
    print()

    # Step 3: Confirm success
    print("=" * 60)
    print("[+] Database initialization complete!")
    print(f"[+] Database location: {get_db_path()}")
    print()
    print("Next steps:")
    print("  1. Run 'python scripts/verify_database.py' to test the database")
    print("  2. Start Phase 2: Resume Parser")
    print("=" * 60)


if __name__ == "__main__":
    main()
