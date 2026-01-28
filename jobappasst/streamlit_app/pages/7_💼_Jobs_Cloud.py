"""
Jobs Page (Cloud Mode) - Browse session-based job listings
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.session_state import (
    init_session_state,
    get_cloud_mode,
    get_session_jobs,
    get_session_profile
)


def main():
    st.set_page_config(
        page_title="Jobs - Job App Assistant",
        page_icon="💼",
        layout="wide"
    )

    init_session_state()

    st.title("💼 Job Listings")

    # Check for session data
    session_profile = get_session_profile()
    jobs = get_session_jobs()

    if not session_profile:
        st.warning("No profile found!")
        st.info("Go to the **Upload** page to upload your resume first.")
        return

    if not jobs:
        st.warning("No jobs found yet!")
        st.info("Go to the **Upload** page and click 'Find Jobs' to search for positions.")
        return

    st.success(f"Found **{len(jobs)}** jobs for **{session_profile.get('name', 'You')}**")

    # Filters
    with st.sidebar:
        st.header("Filters")
        remote_only = st.checkbox("Remote Only", value=True)
        search_term = st.text_input("Search", placeholder="Company or title...")

    # Filter jobs
    filtered_jobs = jobs
    if remote_only:
        filtered_jobs = [j for j in filtered_jobs if j.get('remote')]
    if search_term:
        search_lower = search_term.lower()
        filtered_jobs = [j for j in filtered_jobs if
                        search_lower in j.get('title', '').lower() or
                        search_lower in j.get('company', '').lower()]

    st.markdown("---")
    st.subheader(f"Showing {len(filtered_jobs)} jobs")

    # Display jobs
    for job in filtered_jobs:
        with st.expander(f"**{job['title']}** at {job['company']}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {job['title']}")
                st.write(f"**{job['company']}**")
                if job.get('location'):
                    st.write(f"📍 {job['location']}")

            with col2:
                if job.get('remote'):
                    st.success("🌍 Remote")
                if job.get('salary_max'):
                    st.write(f"💰 Up to ${job['salary_max']:,}")

            if job.get('description'):
                st.markdown("**Description:**")
                st.write(job['description'][:300] + "..." if len(job.get('description', '')) > 300 else job.get('description', ''))

            if job.get('requirements'):
                st.markdown("**Requirements:**")
                reqs = job['requirements']
                if isinstance(reqs, list):
                    for req in reqs[:5]:
                        st.write(f"• {req}")
                else:
                    st.write(reqs)

            if job.get('apply_url'):
                st.link_button("🔗 Apply Now", job['apply_url'], use_container_width=True)

    st.markdown("---")
    st.caption("Jobs fetched from JSearch API based on your skills")


if __name__ == "__main__":
    main()
