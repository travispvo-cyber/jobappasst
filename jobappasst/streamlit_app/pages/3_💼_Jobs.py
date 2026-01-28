"""
Jobs Page - Browse and filter job listings
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.queries import list_jobs, get_job
from streamlit_app.components.job_card import display_job_card, filter_jobs
from streamlit_app.utils.session_state import get_selected_profile, get_selected_profile_name


def main():
    """Jobs page main function"""

    st.set_page_config(
        page_title="Jobs - Job App Assistant",
        page_icon="💼",
        layout="wide"
    )

    st.title("💼 Job Listings")
    st.markdown("Browse and filter available job listings")

    # Get selected profile for tracking
    selected_profile_id = get_selected_profile()
    if selected_profile_id:
        st.success(f"Tracking for: **{get_selected_profile_name()}**")
    else:
        st.info("Select a profile from the sidebar to enable application tracking")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        remote_only = st.checkbox("Remote Jobs Only", value=False)

        location_filter = st.text_input("Filter by Location", placeholder="e.g., Houston, TX")

        company_filter = st.text_input("Filter by Company", placeholder="e.g., Google")

        sort_by = st.selectbox(
            "Sort By",
            options=["Most Recent", "Company Name", "Job Title"],
            index=0
        )

        limit = st.slider("Max Jobs to Display", min_value=10, max_value=100, value=50, step=10)

    # Get jobs from database
    with st.spinner("Loading jobs..."):
        all_jobs = list_jobs(limit=limit, remote_only=False)

    if not all_jobs:
        st.warning("No jobs found in the database.")
        st.info("Run a job search to fetch new listings (feature coming in Phase 2).")
        return

    # Apply filters
    filtered_jobs = filter_jobs(
        all_jobs,
        remote_only=remote_only,
        location=location_filter if location_filter else None,
        company=company_filter if company_filter else None
    )

    # Sort jobs
    if sort_by == "Most Recent":
        # Assume fetched_at is the date field
        filtered_jobs.sort(key=lambda x: x.get('fetched_at', ''), reverse=True)
    elif sort_by == "Company Name":
        filtered_jobs.sort(key=lambda x: x.get('company', ''))
    elif sort_by == "Job Title":
        filtered_jobs.sort(key=lambda x: x.get('title', ''))

    # Display count
    st.subheader(f"Found {len(filtered_jobs)} jobs")

    if len(all_jobs) != len(filtered_jobs):
        st.caption(f"(Filtered from {len(all_jobs)} total jobs)")

    st.markdown("---")

    # Display jobs
    if not filtered_jobs:
        st.info("No jobs match your filters. Try adjusting the filter criteria.")
    else:
        # Pagination
        page_size = 10
        total_pages = (len(filtered_jobs) - 1) // page_size + 1

        if total_pages > 1:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )
        else:
            page = 1

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        jobs_to_display = filtered_jobs[start_idx:end_idx]

        # Display each job
        for job in jobs_to_display:
            display_job_card(job, show_apply_link=True, profile_id=selected_profile_id)

        # Pagination info
        if total_pages > 1:
            st.caption(f"Showing page {page} of {total_pages}")

    st.markdown("---")
    st.caption("Track applications from here, then manage them in the Applications page.")


if __name__ == "__main__":
    main()
