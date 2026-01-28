"""
Job listing display component
"""

import streamlit as st
from typing import Dict, List, Optional
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.automation.tracker import track_application, get_application, ApplicationStatus


def display_job_card(job: Dict, show_apply_link: bool = True, profile_id: Optional[int] = None):
    """Display a job listing in a card format"""

    with st.container():
        # Header with title and company
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### {job['title']}")
            st.write(f"**{job['company']}**")

        with col2:
            if job.get('remote'):
                st.success("🌍 Remote")
            if job.get('location'):
                st.caption(f"📍 {job['location']}")

        # Salary info
        if job.get('salary_min') or job.get('salary_max'):
            salary_text = "💰 Salary: "
            if job.get('salary_min') and job.get('salary_max'):
                salary_text += f"${job['salary_min']:,} - ${job['salary_max']:,}"
            elif job.get('salary_min'):
                salary_text += f"${job['salary_min']:,}+"
            elif job.get('salary_max'):
                salary_text += f"Up to ${job['salary_max']:,}"
            st.write(salary_text)

        # Description
        if job.get('description'):
            with st.expander("Job Description"):
                st.write(job['description'])

        # Requirements
        if job.get('requirements'):
            with st.expander("Requirements"):
                try:
                    reqs = json.loads(job['requirements']) if isinstance(job['requirements'], str) else job['requirements']
                    for req in reqs:
                        st.write(f"• {req}")
                except:
                    st.write(job['requirements'])

        # Apply and Track section
        if show_apply_link:
            col_apply, col_track = st.columns(2)

            with col_apply:
                if job.get('apply_url'):
                    st.link_button("🔗 Apply Now", job['apply_url'], use_container_width=True)

            with col_track:
                if profile_id:
                    # Check if already tracked
                    existing_app = get_application(profile_id, job['id'])
                    if existing_app:
                        status_emoji = {
                            'draft': '📝', 'applied': '📬', 'interviewing': '🎤',
                            'rejected': '❌', 'offer': '🎉'
                        }.get(existing_app['status'], '📋')
                        st.info(f"{status_emoji} {existing_app['status'].title()}")
                    else:
                        if st.button("📋 Track", key=f"track_job_{job['id']}", use_container_width=True):
                            try:
                                track_application(
                                    profile_id,
                                    job['id'],
                                    ApplicationStatus.DRAFT,
                                    "Added from Jobs page"
                                )
                                st.success("Tracked!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

        # Posted date
        if job.get('posted_date'):
            st.caption(f"Posted: {job['posted_date']}")

        st.divider()


def display_job_summary(job: Dict):
    """Display a compact job summary"""

    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.write(f"**{job['title']}**")
        st.caption(job['company'])

    with col2:
        if job.get('location'):
            st.write(f"📍 {job['location']}")
        if job.get('remote'):
            st.success("Remote")

    with col3:
        if job.get('salary_max'):
            st.metric("Max Salary", f"${job['salary_max']:,}")


def display_job_list(jobs: List[Dict], page_size: int = 10):
    """Display a paginated list of jobs"""

    if not jobs:
        st.info("No jobs found")
        return

    st.write(f"**Found {len(jobs)} jobs**")

    # Pagination
    if len(jobs) > page_size:
        page = st.number_input(
            "Page",
            min_value=1,
            max_value=(len(jobs) // page_size) + 1,
            value=1,
            step=1
        )
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        jobs_to_display = jobs[start_idx:end_idx]
    else:
        jobs_to_display = jobs

    # Display jobs
    for job in jobs_to_display:
        display_job_card(job)


def filter_jobs(jobs: List[Dict], remote_only: bool = False, location: str = None, company: str = None) -> List[Dict]:
    """Filter jobs based on criteria"""

    filtered = jobs

    if remote_only:
        filtered = [j for j in filtered if j.get('remote')]

    if location:
        filtered = [j for j in filtered if location.lower() in (j.get('location', '')).lower()]

    if company:
        filtered = [j for j in filtered if company.lower() in (j.get('company', '')).lower()]

    return filtered
