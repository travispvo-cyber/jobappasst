"""View application status and statistics"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import list_profiles, get_profile
from src.automation import list_applications, get_application_stats, ApplicationStatus


def main():
    """Display application statistics for all profiles"""
    print("=" * 70)
    print("APPLICATION TRACKING DASHBOARD")
    print("=" * 70)
    print()

    if len(sys.argv) > 1:
        # Show detailed applications for specific profile
        profile_id = int(sys.argv[1])
        profile = get_profile(profile_id)

        if not profile:
            print(f"[!] Profile {profile_id} not found")
            sys.exit(1)

        print(f"Profile: {profile['name']} ({profile['email']})")
        print()

        # Get stats
        stats = get_application_stats(profile_id)
        print("Application Statistics:")
        print(f"  Total: {stats['total']}")
        print(f"  Draft: {stats['draft']}")
        print(f"  Applied: {stats['applied']}")
        print(f"  Interviewing: {stats['interviewing']}")
        print(f"  Rejected: {stats['rejected']}")
        print(f"  Offer: {stats['offer']}")
        print()

        # List recent applications
        applications = list_applications(profile_id, limit=20)
        if applications:
            print(f"Recent Applications ({len(applications)}):")
            print()
            for app in applications:
                print(f"  - {app['title']} at {app['company']}")
                print(f"    Status: {app['status']} | Location: {app['location']}")
                print(f"    Applied: {app.get('applied_at', 'N/A')}")
                if app.get('notes'):
                    print(f"    Notes: {app['notes'][:80]}...")
                print()
        else:
            print("  No applications found")

    else:
        # Show summary for all profiles
        profiles = list_profiles()

        for profile in profiles:
            stats = get_application_stats(profile['id'])

            if stats['total'] > 0:
                print(f"Profile: {profile['name']}")
                print(f"  Total: {stats['total']} | Applied: {stats['applied']} | "
                      f"Interviewing: {stats['interviewing']} | Offers: {stats['offer']}")
                print()

        print("-" * 70)
        print()
        print("Usage: python scripts/view_applications.py [profile_id]")
        print("  Run with a profile ID to see detailed application list")


if __name__ == "__main__":
    main()
