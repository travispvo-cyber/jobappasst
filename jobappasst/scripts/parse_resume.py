"""Parse a resume and store it in the database"""

import sys
import json
from pathlib import Path

# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.resume_parser import extract_text_from_resume
from src.parsers.profile_extractor import extract_profile_from_text
from src.db import upsert_profile


def main():
    """Main function to parse resume and store in database"""
    print("=" * 70)
    print("Job Application Assistant - Resume Parser")
    print("=" * 70)
    print()

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python scripts/parse_resume.py <path_to_resume>")
        print()
        print("Supported formats: PDF, DOCX")
        print("Example: python scripts/parse_resume.py data/resumes/my_resume.pdf")
        sys.exit(1)

    resume_path = Path(sys.argv[1])

    if not resume_path.exists():
        print(f"[!] Error: Resume file not found: {resume_path}")
        sys.exit(1)

    print(f"Resume file: {resume_path}")
    print()

    # Step 1: Extract text from resume
    print("Step 1: Extracting text from resume...")
    try:
        resume_text = extract_text_from_resume(resume_path)
        print(f"[+] Extracted {len(resume_text)} characters")
        print(f"[+] Found {len(resume_text.splitlines())} lines")
        print()
    except Exception as e:
        print(f"[!] Error extracting text: {e}")
        sys.exit(1)

    # Step 2: Parse with Claude
    print("Step 2: Parsing resume with Claude API...")
    print("    (This may take 10-30 seconds)")
    try:
        profile_data = extract_profile_from_text(resume_text)
        print(f"[+] Successfully parsed profile")
        print(f"[+] Name: {profile_data.get('name')}")
        print(f"[+] Skills: {len(profile_data.get('skills', []))} skills extracted")
        print(f"[+] Experience: {len(profile_data.get('experience', []))} positions")
        print()
    except Exception as e:
        print(f"[!] Error parsing with Claude: {e}")
        print()
        print("Make sure:")
        print("  1. You have set ANTHROPIC_API_KEY in your .env file")
        print("  2. You have Claude API credits available")
        sys.exit(1)

    # Step 3: Store in database (with upsert logic)
    print("Step 3: Storing profile in database...")
    try:
        profile_id, was_updated = upsert_profile(profile_data, resume_path.name)
        if was_updated:
            print(f"[+] Profile updated successfully!")
            print(f"[+] Profile ID: {profile_id} (existing profile updated)")
        else:
            print(f"[+] Profile stored successfully!")
            print(f"[+] Profile ID: {profile_id} (new profile created)")
        print()
    except Exception as e:
        print(f"[!] Error storing in database: {e}")
        sys.exit(1)

    # Step 4: Display summary
    print("=" * 70)
    print("PROFILE SUMMARY")
    print("=" * 70)
    print()
    print(f"Name:     {profile_data.get('name')}")
    print(f"Email:    {profile_data.get('email', 'N/A')}")
    print(f"Phone:    {profile_data.get('phone', 'N/A')}")
    print(f"Location: {profile_data.get('location', 'N/A')}")
    print()

    if profile_data.get('summary'):
        print("Summary:")
        print(f"  {profile_data['summary']}")
        print()

    print("Skills:")
    for skill in profile_data.get('skills', [])[:10]:  # Show first 10
        level = skill.get('level', 'N/A')
        years = skill.get('years', 'N/A')
        print(f"  - {skill['name']} ({level}, {years} years)")
    if len(profile_data.get('skills', [])) > 10:
        print(f"  ... and {len(profile_data['skills']) - 10} more")
    print()

    print("Experience:")
    for exp in profile_data.get('experience', []):
        dates = f"{exp.get('start_date', '?')} to {exp.get('end_date', '?')}"
        print(f"  - {exp['title']} at {exp['company']} ({dates})")
    print()

    # Automatically save JSON
    print("=" * 70)
    print()
    json_path = resume_path.parent / f"{resume_path.stem}_profile.json"
    with open(json_path, 'w') as f:
        json.dump(profile_data, f, indent=2)
    print(f"[+] Profile saved as JSON: {json_path}")
    print()

    print("=" * 70)
    print("[+] Resume parsing complete!")
    print()
    print("Next steps:")
    print(f"  - View profile in database (ID: {profile_id})")
    print("  - Start Phase 3: Job Fetcher")
    print("=" * 70)


if __name__ == "__main__":
    main()
