"""
Job Search Page - Search for new jobs using JSearch API
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.queries import upsert_job, get_profile, upsert_job_match
from src.jobs.jsearch_client import search_jobs
from src.jobs.normalizer import normalize_job_list
from src.matching.scorer import match_profile_to_job
from streamlit_app.utils.session_state import get_selected_profile, get_selected_profile_name


def main():
    """Job Search page main function"""

    st.set_page_config(
        page_title="Job Search - Job App Assistant",
        page_icon="🔍",
        layout="wide"
    )

    st.title("🔍 Job Search")
    st.markdown("Search for new job listings using JSearch API")

    # Check for API key
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        st.error("RAPIDAPI_KEY environment variable not set. Please add it to your .env file.")
        st.code("RAPIDAPI_KEY=your_rapidapi_key_here", language="bash")
        return

    # Check for selected profile
    selected_profile_id = get_selected_profile()
    profile = None

    if selected_profile_id:
        profile = get_profile(selected_profile_id)
        st.success(f"Searching for: **{get_selected_profile_name()}** - Jobs will be auto-scored against this profile")
    else:
        st.info("Select a profile from the sidebar to auto-score job matches")

    st.markdown("---")

    # Search form
    st.subheader("Search Parameters")

    col1, col2 = st.columns(2)

    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., Python Developer, Data Analyst, Software Engineer",
            help="Enter job title, skills, or keywords"
        )

        location = st.text_input(
            "Location",
            placeholder="e.g., Houston, TX or Remote",
            help="City, state, or 'Remote'"
        )

    with col2:
        remote_only = st.checkbox("Remote Jobs Only", value=False)

        date_posted = st.selectbox(
            "Date Posted",
            options=["all", "today", "3days", "week", "month"],
            index=3,  # Default to "week"
            format_func=lambda x: {
                "all": "All Time",
                "today": "Today",
                "3days": "Last 3 Days",
                "week": "Last Week",
                "month": "Last Month"
            }.get(x, x)
        )

        employment_type = st.selectbox(
            "Employment Type",
            options=["", "FULLTIME", "CONTRACTOR", "PARTTIME", "INTERN"],
            format_func=lambda x: x.title() if x else "All Types"
        )

    # Search button
    search_button = st.button("🔍 Search Jobs", type="primary", use_container_width=True)

    st.markdown("---")

    # Initialize session state for search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False

    # Perform search
    if search_button:
        if not query:
            st.warning("Please enter a search query")
        else:
            with st.spinner("Searching for jobs..."):
                try:
                    raw_jobs = search_jobs(
                        query=query,
                        location=location if location else None,
                        remote_jobs_only=remote_only,
                        employment_types=employment_type if employment_type else None,
                        date_posted=date_posted,
                        num_pages=1,
                        api_key=api_key
                    )

                    # Normalize jobs
                    normalized_jobs = normalize_job_list(raw_jobs)

                    st.session_state.search_results = normalized_jobs
                    st.session_state.search_performed = True

                    st.success(f"Found {len(normalized_jobs)} jobs!")

                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
                    st.session_state.search_results = []

    # Display search results
    if st.session_state.search_performed:
        results = st.session_state.search_results

        if not results:
            st.info("No jobs found. Try adjusting your search criteria.")
        else:
            st.subheader(f"Search Results ({len(results)} jobs)")

            # Bulk actions
            col1, col2 = st.columns([1, 3])

            with col1:
                if st.button("💾 Save All Jobs", use_container_width=True):
                    saved_count = 0
                    with st.spinner("Saving jobs..."):
                        for job in results:
                            try:
                                job_id, was_updated = upsert_job(job)
                                saved_count += 1

                                # Auto-score if profile selected
                                if profile:
                                    score, matched, missing = match_profile_to_job(profile, job)
                                    upsert_job_match(
                                        selected_profile_id,
                                        job_id,
                                        score,
                                        matched,
                                        missing,
                                        f"Auto-scored from web search: {query}"
                                    )
                            except Exception as e:
                                st.warning(f"Error saving job: {e}")

                    st.success(f"Saved {saved_count} jobs to database!")

            with col2:
                st.caption("Save all jobs to your database for tracking and matching")

            st.markdown("---")

            # Display each job
            for i, job in enumerate(results):
                with st.expander(f"📋 {job['title']} at {job['company']}", expanded=i == 0):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**Company:** {job['company']}")
                        st.write(f"**Location:** {job['location']}")

                        if job.get('remote'):
                            st.success("🌍 Remote Available")

                        if job.get('salary_min') or job.get('salary_max'):
                            salary_text = "**Salary:** "
                            if job.get('salary_min') and job.get('salary_max'):
                                salary_text += f"${job['salary_min']:,} - ${job['salary_max']:,}"
                            elif job.get('salary_min'):
                                salary_text += f"${job['salary_min']:,}+"
                            elif job.get('salary_max'):
                                salary_text += f"Up to ${job['salary_max']:,}"
                            st.write(salary_text)

                        if job.get('posted_date'):
                            st.write(f"**Posted:** {job['posted_date']}")

                        if job.get('source'):
                            st.caption(f"Source: {job['source']}")

                    with col2:
                        # Save individual job button
                        if st.button(f"💾 Save", key=f"save_{i}", use_container_width=True):
                            try:
                                job_id, was_updated = upsert_job(job)
                                action = "Updated" if was_updated else "Saved"

                                # Auto-score if profile selected
                                if profile:
                                    score, matched, missing = match_profile_to_job(profile, job)
                                    upsert_job_match(
                                        selected_profile_id,
                                        job_id,
                                        score,
                                        matched,
                                        missing,
                                        f"Auto-scored from web search: {query}"
                                    )
                                    st.success(f"{action}! Match: {score:.1f}%")
                                else:
                                    st.success(f"{action} to database!")

                            except Exception as e:
                                st.error(f"Error: {e}")

                        # Apply link
                        if job.get('apply_url'):
                            st.link_button("Apply Now", job['apply_url'], use_container_width=True)

                    # Job description
                    if job.get('description'):
                        st.markdown("**Description:**")
                        # Truncate long descriptions
                        desc = job['description']
                        if len(desc) > 1000:
                            st.write(desc[:1000] + "...")
                            with st.expander("Read full description"):
                                st.write(desc)
                        else:
                            st.write(desc)

                    # Requirements
                    if job.get('requirements'):
                        st.markdown("**Requirements:**")
                        for req in job['requirements'][:10]:
                            st.write(f"• {req}")
                        if len(job['requirements']) > 10:
                            st.caption(f"... and {len(job['requirements']) - 10} more")

                    # Quick match preview if profile selected
                    if profile:
                        st.markdown("---")
                        st.markdown("**Quick Match Preview:**")
                        try:
                            score, matched, missing = match_profile_to_job(profile, job)

                            col_score, col_matched, col_missing = st.columns(3)

                            with col_score:
                                if score >= 75:
                                    st.success(f"🎯 {score:.1f}% Match")
                                elif score >= 50:
                                    st.warning(f"🎯 {score:.1f}% Match")
                                else:
                                    st.error(f"🎯 {score:.1f}% Match")

                            with col_matched:
                                if matched:
                                    st.write("**Matched Skills:**")
                                    for skill in matched[:3]:
                                        st.write(f"✅ {skill}")
                                    if len(matched) > 3:
                                        st.caption(f"+{len(matched) - 3} more")

                            with col_missing:
                                if missing:
                                    st.write("**Missing Skills:**")
                                    for skill in missing[:3]:
                                        st.write(f"❌ {skill}")
                                    if len(missing) > 3:
                                        st.caption(f"+{len(missing) - 3} more")
                        except Exception as e:
                            st.caption(f"Could not calculate match: {e}")

    st.markdown("---")
    st.caption("Jobs are fetched from JSearch API (RapidAPI). Saved jobs are stored locally and can be matched against your profile.")


if __name__ == "__main__":
    main()
