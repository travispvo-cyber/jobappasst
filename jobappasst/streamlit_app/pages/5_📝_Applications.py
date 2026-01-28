"""
Applications Page - Track and manage job applications
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
from src.db.queries import get_job
from src.automation.tracker import (
    list_applications,
    update_application_status,
    get_application_stats,
    track_application,
    schedule_interview,
    set_follow_up,
    get_upcoming_interviews,
    get_pending_follow_ups,
    ApplicationStatus
)
from streamlit_app.utils.session_state import get_selected_profile, get_selected_profile_name


def main():
    """Applications page main function"""

    st.set_page_config(
        page_title="Applications - Job App Assistant",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 Application Tracker")
    st.markdown("Track and manage your job applications")

    # Check for selected profile
    selected_profile_id = get_selected_profile()

    if not selected_profile_id:
        st.warning("Please select a profile from the sidebar to view applications.")
        return

    st.success(f"Tracking applications for: **{get_selected_profile_name()}**")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")

        # Status filter
        status_options = ["All"] + [s.value.title() for s in ApplicationStatus]
        selected_status = st.selectbox("Filter by Status", status_options)

        # Sort options
        sort_by = st.selectbox(
            "Sort By",
            options=["Most Recent", "Company Name", "Job Title", "Status"],
            index=0
        )

    # Get application stats
    stats = get_application_stats(selected_profile_id)

    # Stats row
    st.markdown("---")
    st.subheader("Application Summary")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total", stats.get('total', 0))

    with col2:
        st.metric("📝 Draft", stats.get('draft', 0))

    with col3:
        st.metric("📬 Applied", stats.get('applied', 0))

    with col4:
        st.metric("🎤 Interviewing", stats.get('interviewing', 0))

    with col5:
        st.metric("❌ Rejected", stats.get('rejected', 0))

    with col6:
        st.metric("🎉 Offer", stats.get('offer', 0))

    st.markdown("---")

    # Upcoming Interviews & Follow-ups Section
    col_interviews, col_followups = st.columns(2)

    with col_interviews:
        st.subheader("📅 Upcoming Interviews")
        upcoming = get_upcoming_interviews(selected_profile_id, days_ahead=14)
        if upcoming:
            for interview in upcoming:
                interview_date = interview.get('interview_date', '')
                st.info(f"**{interview.get('title')}** at {interview.get('company')}\n\n📅 {interview_date}")
                if interview.get('interview_notes'):
                    st.caption(f"Notes: {interview.get('interview_notes')}")
        else:
            st.caption("No upcoming interviews scheduled")

    with col_followups:
        st.subheader("⏰ Pending Follow-ups")
        pending = get_pending_follow_ups(selected_profile_id)
        if pending:
            for followup in pending:
                follow_date = followup.get('follow_up_date', '')
                st.warning(f"**{followup.get('title')}** at {followup.get('company')}\n\n📅 Due: {follow_date}")
        else:
            st.caption("No pending follow-ups")

    st.markdown("---")

    # Get applications
    if selected_status == "All":
        applications = list_applications(selected_profile_id, limit=100)
    else:
        status_enum = ApplicationStatus(selected_status.lower())
        applications = list_applications(selected_profile_id, status=status_enum, limit=100)

    # Sort applications
    if applications:
        if sort_by == "Most Recent":
            applications.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        elif sort_by == "Company Name":
            applications.sort(key=lambda x: x.get('company', ''))
        elif sort_by == "Job Title":
            applications.sort(key=lambda x: x.get('title', ''))
        elif sort_by == "Status":
            status_order = {'offer': 0, 'interviewing': 1, 'applied': 2, 'draft': 3, 'rejected': 4}
            applications.sort(key=lambda x: status_order.get(x.get('status', 'draft'), 5))

    # Display applications
    st.subheader(f"Applications ({len(applications)})")

    if not applications:
        st.info("No applications found. Start tracking your job applications!")

        # Quick add section
        st.markdown("---")
        st.subheader("Quick Add Application")
        st.write("Go to the **Matches** or **Jobs** page to start tracking applications.")
    else:
        # Application list
        for app in applications:
            status = app.get('status', 'draft')

            status_emoji = {
                'draft': '📝',
                'applied': '📬',
                'interviewing': '🎤',
                'rejected': '❌',
                'offer': '🎉'
            }.get(status, '📋')

            status_color = {
                'draft': 'gray',
                'applied': 'blue',
                'interviewing': 'orange',
                'rejected': 'red',
                'offer': 'green'
            }.get(status, 'gray')

            with st.expander(
                f"{status_emoji} {app.get('title', 'Unknown Position')} at {app.get('company', 'Unknown Company')}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Company:** {app.get('company', 'N/A')}")
                    st.write(f"**Location:** {app.get('location', 'N/A')}")

                    if app.get('applied_date'):
                        st.write(f"**Applied Date:** {app['applied_date']}")

                    if app.get('notes'):
                        st.write(f"**Notes:** {app['notes']}")

                with col2:
                    # Status badge
                    st.markdown(f"**Current Status:**")

                    # Status update dropdown
                    new_status = st.selectbox(
                        "Update Status",
                        options=[s.value for s in ApplicationStatus],
                        index=[s.value for s in ApplicationStatus].index(status),
                        key=f"status_{app['id']}"
                    )

                    # Notes input
                    new_notes = st.text_area(
                        "Update Notes",
                        value=app.get('notes', '') or '',
                        height=100,
                        key=f"notes_{app['id']}"
                    )

                    # Save button
                    if st.button("Save Changes", key=f"save_{app['id']}", type="primary"):
                        try:
                            update_application_status(
                                app['id'],
                                ApplicationStatus(new_status),
                                new_notes if new_notes else None
                            )
                            st.success("Application updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating application: {e}")

                # Interview & Follow-up Section
                st.markdown("---")
                col_interview, col_followup = st.columns(2)

                with col_interview:
                    st.markdown("**📅 Schedule Interview**")
                    interview_date = st.date_input(
                        "Interview Date",
                        value=None,
                        key=f"int_date_{app['id']}"
                    )
                    interview_time = st.time_input(
                        "Time",
                        value=None,
                        key=f"int_time_{app['id']}"
                    )
                    interview_notes = st.text_input(
                        "Interview Notes",
                        placeholder="e.g., Video call, Panel interview",
                        key=f"int_notes_{app['id']}"
                    )
                    if st.button("Schedule", key=f"sched_{app['id']}"):
                        if interview_date:
                            date_str = str(interview_date)
                            if interview_time:
                                date_str += f" {interview_time.strftime('%H:%M')}"
                            try:
                                schedule_interview(app['id'], date_str, interview_notes)
                                st.success("Interview scheduled!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("Please select a date")

                    # Show existing interview
                    if app.get('interview_date'):
                        st.success(f"Scheduled: {app['interview_date']}")
                        if app.get('interview_notes'):
                            st.caption(app['interview_notes'])

                with col_followup:
                    st.markdown("**⏰ Set Follow-up**")
                    followup_date = st.date_input(
                        "Follow-up Date",
                        value=None,
                        key=f"fu_date_{app['id']}"
                    )
                    followup_note = st.text_input(
                        "Reminder Note",
                        placeholder="e.g., Check status, Send thank you",
                        key=f"fu_note_{app['id']}"
                    )
                    if st.button("Set Reminder", key=f"fu_{app['id']}"):
                        if followup_date:
                            try:
                                set_follow_up(app['id'], str(followup_date), followup_note)
                                st.success("Follow-up set!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("Please select a date")

                    # Show existing follow-up
                    if app.get('follow_up_date'):
                        st.info(f"Follow-up: {app['follow_up_date']}")

                # View job details
                if app.get('job_id'):
                    job = get_job(app['job_id'])
                    if job and job.get('apply_url'):
                        st.link_button("View Original Job Posting", job['apply_url'])

                # Last updated
                if app.get('updated_at'):
                    st.caption(f"Last updated: {app['updated_at']}")

    st.markdown("---")

    # Export section
    st.subheader("Export Data")

    col1, col2 = st.columns(2)

    with col1:
        if applications:
            # Prepare CSV data
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Title', 'Company', 'Location', 'Status', 'Applied Date', 'Notes', 'Updated At'])

            for app in applications:
                writer.writerow([
                    app.get('title', ''),
                    app.get('company', ''),
                    app.get('location', ''),
                    app.get('status', ''),
                    app.get('applied_date', ''),
                    app.get('notes', ''),
                    app.get('updated_at', '')
                ])

            csv_data = output.getvalue()

            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="applications.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to export")

    with col2:
        st.caption("Export your application data to track progress offline or share with others.")

    st.markdown("---")
    st.caption("Tip: Update application status as you progress through the hiring process.")


if __name__ == "__main__":
    main()
