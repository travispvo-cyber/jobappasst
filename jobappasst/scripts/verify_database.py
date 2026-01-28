"""Verify the database is working correctly by running test operations"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.connection import get_db, get_db_path
from src.db.models import get_table_info


def test_insert_profile():
    """Test inserting a sample profile"""
    print("Testing profile insertion...")

    sample_profile = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-0123",
        "location": "San Francisco, CA",
        "summary": "Software engineer with 5 years of experience"
    }

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO profiles (name, email, phone, location, summary, source_file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            sample_profile["name"],
            sample_profile["email"],
            sample_profile["phone"],
            sample_profile["location"],
            sample_profile["summary"],
            "test_resume.pdf"
        ))

        profile_id = cursor.lastrowid
        print(f"  [+] Inserted profile with ID: {profile_id}")

        return profile_id


def test_insert_skills(profile_id):
    """Test inserting sample skills"""
    print("Testing skills insertion...")

    sample_skills = [
        ("Python", "technical", "advanced", 5.0, "Backend development"),
        ("JavaScript", "technical", "intermediate", 3.0, "Frontend development"),
        ("Communication", "soft", "advanced", 5.0, "Team collaboration"),
    ]

    with get_db() as conn:
        for skill in sample_skills:
            conn.execute("""
                INSERT INTO skills (profile_id, name, category, level, years, context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (profile_id, *skill))

        print(f"  [+] Inserted {len(sample_skills)} skills")


def test_insert_experience(profile_id):
    """Test inserting sample experience"""
    print("Testing experience insertion...")

    responsibilities = json.dumps([
        "Developed backend APIs",
        "Managed database migrations",
        "Collaborated with frontend team"
    ])

    accomplishments = json.dumps([
        "Reduced API response time by 40%",
        "Implemented automated testing"
    ])

    skills_used = json.dumps(["Python", "FastAPI", "PostgreSQL"])

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO experience
            (profile_id, title, company, industry, start_date, end_date,
             responsibilities, accomplishments, skills_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            "Senior Software Engineer",
            "Tech Corp",
            "Software",
            "2020-01",
            "present",
            responsibilities,
            accomplishments,
            skills_used
        ))

        print(f"  [+] Inserted experience record")


def test_insert_job():
    """Test inserting a sample job"""
    print("Testing job insertion...")

    requirements = json.dumps([
        "5+ years Python experience",
        "Experience with web frameworks",
        "Strong communication skills"
    ])

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO jobs
            (external_id, title, company, location, remote, description,
             requirements, salary_min, salary_max, apply_url, source, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "test_job_001",
            "Senior Python Developer",
            "Awesome Startup",
            "San Francisco, CA",
            1,  # True
            "We are looking for an experienced Python developer...",
            requirements,
            120000,
            160000,
            "https://example.com/apply",
            "LinkedIn",
            "2025-01-25"
        ))

        job_id = cursor.lastrowid
        print(f"  [+] Inserted job with ID: {job_id}")

        return job_id


def test_insert_job_match(profile_id, job_id):
    """Test inserting a job match"""
    print("Testing job match insertion...")

    matched_skills = json.dumps(["Python", "Communication"])
    missing_skills = json.dumps(["Docker", "Kubernetes"])

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO job_matches
            (profile_id, job_id, match_score, matched_skills, missing_skills, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            job_id,
            85.5,
            matched_skills,
            missing_skills,
            "Strong match - has core Python skills, missing some DevOps tools"
        ))

        print(f"  [+] Inserted job match with score: 85.5")


def test_insert_application(profile_id, job_id):
    """Test inserting an application"""
    print("Testing application insertion...")

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO applications
            (profile_id, job_id, status, applied_date, cover_letter, resume_version, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id,
            job_id,
            "draft",
            "2025-01-25",
            "Dear Hiring Manager, I am excited to apply...",
            "resume_v2.pdf",
            "Need to tailor cover letter more"
        ))

        print(f"  [+] Inserted application record")


def test_query_data(profile_id):
    """Test querying data with JOINs"""
    print("\nTesting complex queries...")

    with get_db() as conn:
        # Query profile with skills
        print("\n  Profile with skills:")
        cursor = conn.execute("""
            SELECT p.name, s.name as skill, s.level, s.years
            FROM profiles p
            JOIN skills s ON p.id = s.profile_id
            WHERE p.id = ?
        """, (profile_id,))

        for row in cursor.fetchall():
            print(f"    {row['name']}: {row['skill']} ({row['level']}, {row['years']} years)")

        # Query job matches
        print("\n  Job matches:")
        cursor = conn.execute("""
            SELECT j.title, j.company, jm.match_score, jm.notes
            FROM jobs j
            JOIN job_matches jm ON j.id = jm.job_id
            WHERE jm.profile_id = ?
            ORDER BY jm.match_score DESC
        """, (profile_id,))

        for row in cursor.fetchall():
            print(f"    {row['title']} at {row['company']}: {row['match_score']}%")
            print(f"      {row['notes']}")


def display_table_summary():
    """Display summary of all tables"""
    print("\nDatabase Summary:")
    print("-" * 40)

    info = get_table_info()
    for table, count in info.items():
        print(f"  {table:20} {count:>5} rows")


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Job Application Assistant - Database Verification")
    print("=" * 60)
    print(f"\nDatabase: {get_db_path()}")
    print()

    try:
        # Test all operations
        profile_id = test_insert_profile()
        test_insert_skills(profile_id)
        test_insert_experience(profile_id)
        job_id = test_insert_job()
        test_insert_job_match(profile_id, job_id)
        test_insert_application(profile_id, job_id)

        # Test queries
        test_query_data(profile_id)

        # Display summary
        display_table_summary()

        print("\n" + "=" * 60)
        print("[+] All verification tests passed!")
        print("=" * 60)
        print("\nYour database is working correctly!")
        print("\nNext steps:")
        print("  • Start building the resume parser (Phase 2)")
        print("  • Check out the sample data inserted")
        print("  • Use a SQLite viewer to explore the database")
        print()

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[!] Verification failed: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    main()
