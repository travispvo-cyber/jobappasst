"""
Dashboard Page - Stats and visualizations for job application tracking
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.queries import list_profiles, list_jobs, get_matches_for_profile, get_top_matches
from src.automation.tracker import list_applications, get_application_stats, ApplicationStatus
from streamlit_app.utils.session_state import get_selected_profile, get_selected_profile_name


def main():
    """Dashboard page main function"""

    st.set_page_config(
        page_title="Dashboard - Job App Assistant",
        page_icon="🏠",
        layout="wide"
    )

    st.title("🏠 Dashboard")
    st.markdown("Overview of your job search progress")

    # Check for selected profile
    selected_profile_id = get_selected_profile()

    if not selected_profile_id:
        st.warning("Please select a profile from the sidebar to view your dashboard.")

        # Show global stats instead
        st.markdown("---")
        st.subheader("Global Statistics")

        profiles = list_profiles()
        jobs = list_jobs(limit=1000)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Profiles", len(profiles) if profiles else 0)

        with col2:
            st.metric("Total Jobs", len(jobs) if jobs else 0)

        with col3:
            remote_jobs = [j for j in jobs if j.get('remote')] if jobs else []
            st.metric("Remote Jobs", len(remote_jobs))

        return

    st.success(f"Viewing dashboard for: **{get_selected_profile_name()}**")

    # Get data for selected profile
    matches = get_matches_for_profile(selected_profile_id, min_score=0, limit=500)
    top_matches = get_top_matches(selected_profile_id, limit=5)
    applications = list_applications(selected_profile_id, limit=500)
    app_stats = get_application_stats(selected_profile_id)
    all_jobs = list_jobs(limit=1000)

    st.markdown("---")

    # Key Metrics Row
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Matches",
            value=len(matches),
            help="Jobs scored against your profile"
        )

    with col2:
        if matches:
            avg_score = sum(m.get('match_score', 0) for m in matches) / len(matches)
            st.metric(
                label="Avg Match Score",
                value=f"{avg_score:.1f}%",
                help="Average match score across all jobs"
            )
        else:
            st.metric(label="Avg Match Score", value="N/A")

    with col3:
        high_matches = [m for m in matches if m.get('match_score', 0) >= 75]
        st.metric(
            label="High Matches (75%+)",
            value=len(high_matches),
            help="Jobs with 75% or higher match score"
        )

    with col4:
        st.metric(
            label="Total Applications",
            value=app_stats.get('total', 0),
            help="Total applications tracked"
        )

    st.markdown("---")

    # Two column layout for charts
    col_left, col_right = st.columns(2)

    with col_left:
        # Application Status Distribution
        st.subheader("Application Status")

        if app_stats.get('total', 0) > 0:
            status_data = {
                'Status': [],
                'Count': []
            }

            status_colors = {
                'draft': '#9CA3AF',
                'applied': '#3B82F6',
                'interviewing': '#F59E0B',
                'rejected': '#EF4444',
                'offer': '#10B981'
            }

            for status in ApplicationStatus:
                count = app_stats.get(status.value, 0)
                if count > 0:
                    status_data['Status'].append(status.value.title())
                    status_data['Count'].append(count)

            if status_data['Status']:
                fig = px.pie(
                    status_data,
                    values='Count',
                    names='Status',
                    color='Status',
                    color_discrete_map={
                        'Draft': '#9CA3AF',
                        'Applied': '#3B82F6',
                        'Interviewing': '#F59E0B',
                        'Rejected': '#EF4444',
                        'Offer': '#10B981'
                    },
                    hole=0.4
                )
                fig.update_layout(
                    showlegend=True,
                    height=300,
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No applications yet")
        else:
            st.info("No applications tracked yet. Start applying to jobs!")

    with col_right:
        # Match Score Distribution
        st.subheader("Match Score Distribution")

        if matches:
            scores = [m.get('match_score', 0) for m in matches]

            fig = go.Figure(data=[go.Histogram(
                x=scores,
                nbinsx=10,
                marker_color='#4287f5'
            )])
            fig.update_layout(
                xaxis_title="Match Score (%)",
                yaxis_title="Number of Jobs",
                height=300,
                margin=dict(l=20, r=20, t=20, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No matches scored yet. Run job scoring to see distribution.")

    st.markdown("---")

    # Top Matches Section
    st.subheader("Top 5 Job Matches")

    if top_matches:
        for i, match in enumerate(top_matches, 1):
            score = match.get('match_score', 0)

            # Color based on score
            if score >= 80:
                score_color = "🟢"
            elif score >= 60:
                score_color = "🟡"
            else:
                score_color = "🔴"

            with st.expander(f"{score_color} {i}. {match['title']} at {match['company']} - {score:.1f}%"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Location:** {match.get('location', 'Not specified')}")
                    if match.get('remote'):
                        st.success("Remote Available")

                    if match.get('salary_min') or match.get('salary_max'):
                        salary_text = "**Salary:** "
                        if match.get('salary_min') and match.get('salary_max'):
                            salary_text += f"${match['salary_min']:,} - ${match['salary_max']:,}"
                        elif match.get('salary_min'):
                            salary_text += f"${match['salary_min']:,}+"
                        else:
                            salary_text += f"Up to ${match['salary_max']:,}"
                        st.write(salary_text)

                with col2:
                    # Mini gauge for score
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#4287f5"},
                            'steps': [
                                {'range': [0, 50], 'color': "#fee2e2"},
                                {'range': [50, 75], 'color': "#fef3c7"},
                                {'range': [75, 100], 'color': "#d1fae5"}
                            ]
                        }
                    ))
                    fig.update_layout(
                        height=150,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Skills comparison
                col_matched, col_missing = st.columns(2)

                with col_matched:
                    matched_skills = match.get('matched_skills', [])
                    if matched_skills:
                        st.write("**Matched Skills:**")
                        for skill in matched_skills[:5]:
                            st.write(f"✅ {skill}")
                        if len(matched_skills) > 5:
                            st.caption(f"... and {len(matched_skills) - 5} more")

                with col_missing:
                    missing_skills = match.get('missing_skills', [])
                    if missing_skills:
                        st.write("**Missing Skills:**")
                        for skill in missing_skills[:5]:
                            st.write(f"❌ {skill}")
                        if len(missing_skills) > 5:
                            st.caption(f"... and {len(missing_skills) - 5} more")

                if match.get('apply_url'):
                    st.link_button("Apply Now", match['apply_url'], use_container_width=True)
    else:
        st.info("No matches found. Run job scoring to see your top matches.")

    st.markdown("---")

    # Recent Activity
    st.subheader("Recent Applications")

    if applications:
        recent_apps = applications[:5]

        for app in recent_apps:
            status = app.get('status', 'draft')
            status_emoji = {
                'draft': '📝',
                'applied': '📬',
                'interviewing': '🎤',
                'rejected': '❌',
                'offer': '🎉'
            }.get(status, '📋')

            st.write(f"{status_emoji} **{app.get('title', 'Unknown')}** at {app.get('company', 'Unknown')} - {status.title()}")
    else:
        st.info("No applications tracked yet.")

    st.markdown("---")
    st.caption("Dashboard updates automatically as you track applications and score jobs.")


if __name__ == "__main__":
    main()
