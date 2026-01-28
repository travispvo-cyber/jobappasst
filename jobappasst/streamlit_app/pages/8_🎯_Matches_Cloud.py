"""
Matches Page (Cloud Mode) - View session-based job matches
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.session_state import (
    init_session_state,
    get_session_matches,
    get_session_profile
)


def display_score_bar(score: float):
    """Display a colored score bar"""
    if score >= 75:
        color = "green"
    elif score >= 50:
        color = "orange"
    else:
        color = "red"

    st.markdown(f"""
    <div style="background-color: #e0e0e0; padding: 3px; border-radius: 5px; margin: 5px 0;">
        <div style="background-color: {color}; width: {score}%; height: 20px; border-radius: 3px;"></div>
    </div>
    <p style="text-align: center; font-weight: bold; margin: 0;">{score:.0f}% Match</p>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Matches - Job App Assistant",
        page_icon="🎯",
        layout="wide"
    )

    init_session_state()

    st.title("🎯 Job Matches")
    st.markdown("Your personalized job recommendations")

    # Check for session data
    session_profile = get_session_profile()
    matches = get_session_matches()

    if not session_profile:
        st.warning("No profile found!")
        st.info("Go to the **Upload** page to upload your resume first.")
        return

    if not matches:
        st.warning("No matches found yet!")
        st.info("Go to the **Upload** page and click 'Find Jobs' to get matches.")
        return

    st.success(f"Found **{len(matches)}** matches for **{session_profile.get('name', 'You')}**")

    # Show profile skills
    with st.expander("Your Skills", expanded=False):
        skills = session_profile.get('skills', [])
        st.write(", ".join(skills))

    # Filters
    with st.sidebar:
        st.header("Filters")
        min_score = st.slider("Minimum Score", 0, 100, 50, 5)

    # Filter matches
    filtered_matches = [m for m in matches if m['score'] >= min_score]

    st.markdown("---")

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Matches", len(filtered_matches))
    with col2:
        if filtered_matches:
            avg_score = sum(m['score'] for m in filtered_matches) / len(filtered_matches)
            st.metric("Avg Score", f"{avg_score:.0f}%")
        else:
            st.metric("Avg Score", "N/A")
    with col3:
        high_matches = len([m for m in filtered_matches if m['score'] >= 75])
        st.metric("High Matches (75%+)", high_matches)

    st.markdown("---")
    st.subheader(f"Top {len(filtered_matches)} Matches")

    # Display matches
    for match in filtered_matches:
        job = match['job']
        score = match['score']

        with st.expander(f"⭐ {score:.0f}% - **{job['title']}** at {job['company']}", expanded=False):
            # Score bar
            display_score_bar(score)

            st.markdown("---")

            # Job info
            col1, col2 = st.columns([2, 1])
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

            # Skills analysis
            st.markdown("---")
            st.markdown("#### Skills Analysis")

            col_match, col_miss = st.columns(2)

            with col_match:
                st.markdown("**✅ Matched Skills**")
                matched = match.get('matched_skills', [])
                if matched:
                    for skill in matched[:5]:
                        st.success(f"✓ {skill}")
                else:
                    st.info("No specific skill requirements")

            with col_miss:
                st.markdown("**📚 Skills to Learn**")
                missing = match.get('missing_skills', [])
                if missing:
                    for skill in missing[:5]:
                        st.warning(f"○ {skill}")
                else:
                    st.success("You have all required skills!")

            # Description
            if job.get('description'):
                st.markdown("---")
                with st.expander("Job Description"):
                    st.write(job['description'])

            # Apply button
            if job.get('apply_url'):
                st.markdown("---")
                st.link_button("🔗 Apply Now", job['apply_url'], use_container_width=True)

    st.markdown("---")
    st.caption("Matches are scored based on skill overlap with job requirements")


if __name__ == "__main__":
    main()
