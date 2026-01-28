"""
Upload Page - Resume upload and processing for cloud mode
Handles the full workflow: upload -> parse -> fetch jobs -> match
"""

import streamlit as st
import sys
import os
from pathlib import Path
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.session_state import (
    init_session_state,
    get_cloud_mode,
    set_session_profile,
    get_session_profile,
    set_session_jobs,
    get_session_jobs,
    set_session_matches,
    get_session_matches
)


def get_api_key(key_name: str) -> str:
    """Get API key from Streamlit secrets or environment"""
    try:
        return st.secrets["api_keys"][key_name]
    except (KeyError, FileNotFoundError):
        pass
    return os.getenv(key_name, "")


def parse_resume_text(file_bytes, filename: str) -> str:
    """Extract text from uploaded resume file"""
    import io

    if filename.endswith('.pdf'):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""

    elif filename.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return ""

    return ""


def extract_profile_with_claude(resume_text: str, api_key: str) -> dict:
    """Use Claude to extract structured profile data from resume text"""
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        prompt = """Extract structured information from this resume. Return a JSON object with:
{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, State",
    "summary": "Brief professional summary",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "dates": "Start - End",
            "highlights": ["achievement1", "achievement2"]
        }
    ]
}

Resume text:
"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt + resume_text}
            ]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        import re
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())

        return {"error": "Could not parse response"}

    except Exception as e:
        return {"error": str(e)}


def fetch_jobs_for_skills(skills: list, api_key: str, num_results: int = 20) -> list:
    """Fetch jobs from JSearch API based on skills"""
    import requests

    if not skills:
        return []

    # Use top skills as search query
    query = " ".join(skills[:3])

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{query} remote",
        "page": "1",
        "num_pages": "2",
        "remote_jobs_only": "true"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        jobs = []
        for job in data.get("data", [])[:num_results]:
            jobs.append({
                "id": job.get("job_id", ""),
                "title": job.get("job_title", "Unknown"),
                "company": job.get("employer_name", "Unknown"),
                "location": job.get("job_city", "") + ", " + job.get("job_state", ""),
                "remote": job.get("job_is_remote", False),
                "description": job.get("job_description", "")[:500],
                "apply_url": job.get("job_apply_link", ""),
                "requirements": job.get("job_required_skills") or [],
                "salary_min": job.get("job_min_salary"),
                "salary_max": job.get("job_max_salary"),
            })
        return jobs

    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        return []


def score_matches(profile: dict, jobs: list) -> list:
    """Score jobs against profile skills"""
    from src.matching.taxonomy import normalize_skill

    profile_skills = set(normalize_skill(s) for s in profile.get('skills', []))
    matches = []

    for job in jobs:
        job_reqs = job.get('requirements', [])
        if isinstance(job_reqs, str):
            job_reqs = [job_reqs]

        job_skills = set(normalize_skill(r) for r in job_reqs if r)

        if job_skills:
            matched = profile_skills & job_skills
            score = (len(matched) / len(job_skills)) * 100
        else:
            # No requirements specified, give base score
            score = 50.0
            matched = set()

        missing = job_skills - profile_skills

        matches.append({
            "job": job,
            "score": round(score, 1),
            "matched_skills": list(matched),
            "missing_skills": list(missing)
        })

    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches


def main():
    st.set_page_config(
        page_title="Upload Resume - Job App Assistant",
        page_icon="📤",
        layout="wide"
    )

    init_session_state()

    st.title("📤 Upload Your Resume")
    st.markdown("Upload your resume to get personalized job matches")

    # Check for existing profile
    session_profile = get_session_profile()
    if session_profile:
        st.success(f"Profile loaded: **{session_profile.get('name', 'Your Profile')}**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Skills detected:**")
            skills = session_profile.get('skills', [])
            st.write(", ".join(skills[:10]) + ("..." if len(skills) > 10 else ""))

        with col2:
            if st.button("Clear Profile & Start Over", type="secondary"):
                st.session_state.session_profile = None
                st.session_state.session_jobs = []
                st.session_state.session_matches = []
                st.rerun()

        st.markdown("---")

        # Show job/match stats
        jobs = get_session_jobs()
        matches = get_session_matches()

        if jobs:
            st.success(f"Found **{len(jobs)}** jobs and **{len(matches)}** matches!")
            st.info("Go to the **Jobs** or **Matches** page to view results.")
        else:
            st.info("Click 'Find Jobs' below to search for matching positions.")

            if st.button("🔍 Find Jobs", type="primary"):
                with st.spinner("Searching for jobs..."):
                    rapidapi_key = get_api_key("RAPIDAPI_KEY")
                    if not rapidapi_key:
                        st.error("RapidAPI key not configured!")
                    else:
                        jobs = fetch_jobs_for_skills(skills, rapidapi_key)
                        set_session_jobs(jobs)

                        if jobs:
                            matches = score_matches(session_profile, jobs)
                            set_session_matches(matches)
                            st.success(f"Found {len(jobs)} jobs!")
                            st.rerun()
                        else:
                            st.warning("No jobs found. Try adjusting your skills.")

    else:
        # File upload section
        st.markdown("### Step 1: Upload Resume")

        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'docx'],
            help="Supported formats: PDF, DOCX"
        )

        if uploaded_file:
            st.success(f"File uploaded: **{uploaded_file.name}**")

            # Process button
            st.markdown("### Step 2: Process Resume")

            anthropic_key = get_api_key("ANTHROPIC_API_KEY")
            rapidapi_key = get_api_key("RAPIDAPI_KEY")

            if not anthropic_key:
                st.error("Anthropic API key not configured. Please add it to Streamlit secrets.")
                st.code("""
# In Streamlit Cloud dashboard, add these secrets:
[api_keys]
ANTHROPIC_API_KEY = "your-key-here"
RAPIDAPI_KEY = "your-key-here"
                """)
            else:
                if st.button("🚀 Parse Resume & Find Jobs", type="primary"):
                    progress = st.progress(0, text="Starting...")

                    # Step 1: Extract text
                    progress.progress(10, text="Extracting text from resume...")
                    file_bytes = uploaded_file.read()
                    resume_text = parse_resume_text(file_bytes, uploaded_file.name)

                    if not resume_text:
                        st.error("Could not extract text from resume")
                        return

                    # Step 2: Parse with Claude
                    progress.progress(30, text="AI analyzing your resume...")
                    profile = extract_profile_with_claude(resume_text, anthropic_key)

                    if "error" in profile:
                        st.error(f"Error parsing resume: {profile['error']}")
                        return

                    # Save profile to session
                    set_session_profile(profile)
                    progress.progress(50, text="Profile created!")

                    # Step 3: Fetch jobs
                    if rapidapi_key:
                        progress.progress(60, text="Searching for matching jobs...")
                        skills = profile.get('skills', [])
                        jobs = fetch_jobs_for_skills(skills, rapidapi_key)
                        set_session_jobs(jobs)
                        progress.progress(80, text=f"Found {len(jobs)} jobs!")

                        # Step 4: Score matches
                        progress.progress(90, text="Scoring job matches...")
                        matches = score_matches(profile, jobs)
                        set_session_matches(matches)

                    progress.progress(100, text="Complete!")
                    st.balloons()
                    st.rerun()

    st.markdown("---")

    # Privacy notice
    st.caption("🔒 **Privacy**: Your resume data is processed in your browser session only and is not stored on any server.")
    st.caption("Data will be cleared when you close this browser tab.")


if __name__ == "__main__":
    main()
