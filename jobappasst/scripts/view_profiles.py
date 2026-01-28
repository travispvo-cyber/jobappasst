"""View all profiles in the database"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_table_info, list_profiles, get_profile


def main():
    print("=" * 70)
    print("DATABASE SUMMARY")
    print("=" * 70)

    info = get_table_info()
    for table, count in info.items():
        print(f"{table:20} {count:>5} rows")

    print("\n" + "=" * 70)
    print("PROFILES")
    print("=" * 70)

    profiles = list_profiles()
    for p in profiles:
        print(f"\nID: {p['id']}")
        print(f"Name: {p['name']}")
        print(f"Email: {p['email']}")
        print(f"Location: {p['location']}")
        print(f"Source: {p['source_file']}")
        print(f"Created: {p['created_at']}")


if __name__ == "__main__":
    main()
