"""
Matches Page - View job matches for selected profile
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.queries import get_matches_for_profile, get_job, get_profile
from src.automation.tracker import track_application, get_application, ApplicationStatus
from streamlit_app.utils.session_state import get_selected_profile, get_selected_profile_name


def display_match_score(score):
    """Display match score with color-coded progress bar"""
    if score >= 75:
        color = "green"
    elif score >= 50:
        color = "orange"
    else:
        color = "red"

    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px;">
        <div style="background-color: {color}; width: {score}%; height: 20px; border-radius: 3px;"></div>
        <p style="margin-top: 5px; text-align: center; font-weight: bold;">{score:.1f}% Match</p>
    </div>
    """, unsafe_allow_html=True)


def display_skills_comparison(matched_skills, missing_skills):
    """Display matched vs missing skills"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Matched Skills**")
        if matched_skills:
            try:
                skills = json.loads(matched_skills) if isinstance(matched_skills, str) else matched_skills
                for skill in skills:
                    st.success(f"✓ {skill}")
            except:
                st.write(matched_skills)
        else:
            st.info("No matched skills")

    with col2:
        st.markdown("**❌ Missing Skills**")
        if missing_skills:
            try:
                skills = json.loads(missing_skills) if isinstance(missing_skills, str) else missing_skills
                for skill in skills:
                    st.warning(f"✗ {skill}")
            except:
                st.write(missing_skills)
        else:
            st.success("No missing skills!")


def main():
    """Matches page main function"""

    st.set_page_config(
        page_title="Matches - Job App Assistant",
        page_icon="🎯",
        layout="wide"
    )

    st.title("🎯 Job Matches")
    st.markdown("View personalized job matches based on your skills")

    # Check for selected profile
    selected_profile_id = get_selected_profile()

    if not selected_profile_id:
        st.warning("Please select a profile from the sidebar to view matches.")
        return

    st.success(f"Showing matches for: **{get_selected_profile_name()}**")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        min_score = st.slider(
            "Minimum Match Score",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="Filter jobs by minimum match percentage"
        )

        sort_by = st.selectbox(
            "Sort By",
            options=["Highest Score", "Lowest Score", "Most Recent"],
            index=0
        )

        limit = st.slider("Max Matches to Show", min_value=10, max_value=100, value=50, step=10)

    # Get matches from database
    with st.spinner("Loading matches..."):
        matches = get_matches_for_profile(
            selected_profile_id,
            min_score=min_score,
            limit=limit
        )

    if not matches:
        st.warning(f"No matches found with a score >= {min_score}%")
        st.info("Try lowering the minimum match score or run a job search to find new opportunities.")
        return

    # Sort matches
    if sort_by == "Highest Score":
        matches.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    elif sort_by == "Lowest Score":
        matches.sort(key=lambda x: x.get('match_score', 0))
    elif sort_by == "Most Recent":
        matches.sort(key=lambda x: x.get('scored_at', ''), reverse=True)

    # Display match count
    st.subheader(f"Found {len(matches)} matches")

    if len(matches) > 0:
        avg_score = sum(m.get('match_score', 0) for m in matches) / len(matches)
        st.caption(f"Average match score: {avg_score:.1f}%")

    st.markdown("---")

    # Display matches
    for match in matches:
        # Get job details
        job = get_job(match['job_id'])

        if not job:
            continue

        # Create expandable match card
        match_score = match.get('match_score', 0)

        with st.expander(
            f"⭐ {match_score:.1f}% - {job['title']} at {job['company']}",
            expanded=False
        ):
            # Match score visualization
            display_match_score(match_score)

            st.markdown("---")

            # Job details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"### {job['title']}")
                st.markdown(f"**{job['company']}**")

            with col2:
                if job.get('remote'):
                    st.success("🌍 Remote")
                if job.get('location'):
                    st.write(f"📍 {job['location']}")

            # Skills comparison
            st.markdown("---")
            st.markdown("#### Skills Analysis")

            matched_skills = match.get('matched_skills')
            missing_skills = match.get('missing_skills')

            display_skills_comparison(matched_skills, missing_skills)

            # Match notes
            if match.get('notes'):
                st.markdown("---")
                st.markdown("#### Match Notes")
                st.info(match['notes'])

            # Job description
            if job.get('description'):
                st.markdown("---")
                st.markdown("#### Job Description")
                with st.expander("View Full Description"):
                    st.write(job['description'])

            # Apply and Track section
            st.markdown("---")

            col_apply, col_track = st.columns(2)

            with col_apply:
                if job.get('apply_url'):
                    st.link_button("🔗 Apply Now", job['apply_url'], use_container_width=True)

            with col_track:
                # Check if already tracked
                existing_app = get_application(selected_profile_id, job['id'])

                if existing_app:
                    status_emoji = {
                        'draft': '📝', 'applied': '📬', 'interviewing': '🎤',
                        'rejected': '❌', 'offer': '🎉'
                    }.get(existing_app['status'], '📋')
                    st.info(f"{status_emoji} Already tracked: {existing_app['status'].title()}")
                else:
                    if st.button("📋 Track Application", key=f"track_{match['id']}", use_container_width=True):
                        try:
                            track_application(
                                selected_profile_id,
                                job['id'],
                                ApplicationStatus.DRAFT,
                                f"Added from Matches page - {match_score:.1f}% match"
                            )
                            st.success("Added to Applications!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            # Scored date
            if match.get('scored_at'):
                st.caption(f"Scored on: {match['scored_at']}")

    st.markdown("---")
    st.caption("Track applications from here, then manage them in the Applications page.")


if __name__ == "__main__":
    main()
