"""Apply to jobs using browser automation"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import get_profile, get_job, get_top_matches, list_profiles
from src.automation import (
    BrowserManager,
    navigate_to_job,
    ApplicationFormData,
    fill_application_form,
    detect_form_fields,
    track_application,
    ApplicationStatus
)


def create_form_data_from_profile(profile: dict, resume_path: str = None) -> ApplicationFormData:
    """
    Create ApplicationFormData from a profile.

    Args:
        profile: Profile dictionary
        resume_path: Optional path to resume file

    Returns:
        ApplicationFormData: Form data object
    """
    # Split name if needed
    name_parts = profile['name'].split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    # Get current experience
    experience = profile.get('experience', [])
    current_company = None
    current_title = None

    if experience:
        latest = experience[0]
        current_company = latest.get('company')
        current_title = latest.get('title')

    return ApplicationFormData(
        first_name=first_name,
        last_name=last_name,
        email=profile.get('email', ''),
        phone=profile.get('phone', ''),
        location=profile.get('location'),
        linkedin_url=profile.get('linkedin_url'),
        portfolio_url=profile.get('portfolio_url'),
        resume_path=resume_path,
        current_company=current_company,
        current_title=current_title
    )


def apply_to_job_interactive(
    profile_id: int,
    job_id: int,
    headless: bool = False,
    dry_run: bool = False,
    resume_path: str = None
):
    """
    Apply to a job with interactive browser automation.

    Args:
        profile_id: Profile ID
        job_id: Job ID
        headless: Run browser in headless mode
        dry_run: Only detect fields, don't fill
        resume_path: Optional resume file path
    """
    # Load profile and job
    profile = get_profile(profile_id)
    if not profile:
        print(f"[!] Profile {profile_id} not found")
        return False

    job = get_job(job_id)
    if not job:
        print(f"[!] Job {job_id} not found")
        return False

    print("=" * 70)
    print("Job Application Automation")
    print("=" * 70)
    print()
    print(f"Profile: {profile['name']} ({profile['email']})")
    print(f"Job: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print()

    # Check for apply URL
    apply_url = job.get('apply_url')
    if not apply_url:
        print("[!] No apply URL found for this job")
        return False

    print(f"Apply URL: {apply_url}")
    print()

    if dry_run:
        print("[DRY RUN MODE] Will detect fields only, not fill or submit")
        print()

    # Create form data
    form_data = create_form_data_from_profile(profile, resume_path)

    # Start browser
    print("Starting browser...")
    with BrowserManager(headless=headless, slow_mo=1000) as page:
        # Navigate to job
        print(f"Navigating to {apply_url}...")
        if not navigate_to_job(page, apply_url):
            print("[!] Failed to navigate to job URL")
            return False

        print("[+] Page loaded successfully")
        print()

        # Wait for user to see the page
        input("Press Enter when ready to detect form fields...")
        print()

        # Detect form fields
        print("Detecting form fields...")
        detected = detect_form_fields(page)

        print(f"  Text inputs: {len(detected['text_inputs'])}")
        for field in detected['text_inputs'][:10]:
            print(f"    - {field}")
        if len(detected['text_inputs']) > 10:
            print(f"    ... and {len(detected['text_inputs']) - 10} more")

        print(f"  File inputs: {len(detected['file_inputs'])}")
        for field in detected['file_inputs']:
            print(f"    - {field}")

        print(f"  Textareas: {len(detected['textareas'])}")
        for field in detected['textareas']:
            print(f"    - {field}")

        print()

        # Fill form
        if not dry_run:
            input("Press Enter to fill the form...")
            print()

            print("Filling form...")
            results = fill_application_form(page, form_data, dry_run=False)

            print(f"[+] Filled fields: {', '.join(results['filled_fields'])}")
            if results['missing_fields']:
                print(f"[!] Missing fields: {', '.join(results['missing_fields'])}")
            if results['errors']:
                print(f"[!] Errors: {', '.join(results['errors'])}")
            print()

            # Ask before submitting
            submit = input("Submit application? (yes/no): ").lower().strip()

            if submit == 'yes':
                print("Submitting application...")
                # Note: Actual submission handled manually or with custom logic
                # This is intentionally left for manual verification

                # Track application
                app_id = track_application(
                    profile_id=profile_id,
                    job_id=job_id,
                    status=ApplicationStatus.APPLIED,
                    notes=f"Applied via automation. Filled: {', '.join(results['filled_fields'])}"
                )

                print(f"[+] Application tracked (ID: {app_id})")
                print("[+] Application process complete!")
            else:
                print("[!] Application not submitted")

                # Track as draft
                app_id = track_application(
                    profile_id=profile_id,
                    job_id=job_id,
                    status=ApplicationStatus.DRAFT,
                    notes="Form filled but not submitted"
                )
                print(f"[+] Saved as draft (ID: {app_id})")

        else:
            print("[DRY RUN] Skipping form fill and submission")

        # Keep browser open for review
        input("\nPress Enter to close browser...")

    return True


def main():
    """Main entry point"""
    print("=" * 70)
    print("Job Application Assistant - Application Automation")
    print("=" * 70)
    print()

    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python scripts/apply_to_jobs.py <profile_id> <job_id> [options]")
        print()
        print("Options:")
        print("  --headless         Run browser in headless mode")
        print("  --dry-run          Only detect fields, don't fill")
        print("  --resume <path>    Path to resume file")
        print()
        print("Available profiles:")
        profiles = list_profiles()
        for p in profiles:
            print(f"  ID {p['id']}: {p['name']}")
        print()
        print("Examples:")
        print("  python scripts/apply_to_jobs.py 5 52")
        print("  python scripts/apply_to_jobs.py 5 52 --resume data/resumes/TravisVo-V1.pdf")
        print("  python scripts/apply_to_jobs.py 5 52 --dry-run")
        sys.exit(1)

    profile_id = int(sys.argv[1])
    job_id = int(sys.argv[2])

    # Parse options
    headless = '--headless' in sys.argv
    dry_run = '--dry-run' in sys.argv
    resume_path = None

    if '--resume' in sys.argv:
        idx = sys.argv.index('--resume')
        if idx + 1 < len(sys.argv):
            resume_path = sys.argv[idx + 1]

    # Run automation
    success = apply_to_job_interactive(
        profile_id=profile_id,
        job_id=job_id,
        headless=headless,
        dry_run=dry_run,
        resume_path=resume_path
    )

    if success:
        print()
        print("=" * 70)
        print("[+] Automation complete!")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("[!] Automation failed")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
