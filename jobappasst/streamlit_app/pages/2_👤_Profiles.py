"""
Profiles Page - View and manage user profiles
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.queries import list_profiles, get_profile, upsert_profile, delete_profile
from src.parsers.resume_parser import extract_text_from_resume
from src.parsers.profile_extractor import extract_profile_from_text
from streamlit_app.components.profile_card import (
    display_profile_card,
    display_skills,
    display_experience
)
from streamlit_app.utils.session_state import get_selected_profile


def main():
    """Profiles page main function"""

    st.set_page_config(
        page_title="Profiles - Job App Assistant",
        page_icon="👤",
        layout="wide"
    )

    st.title("👤 Profiles")
    st.markdown("View and manage user profiles")

    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")

        # Resume upload section
        st.subheader("Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=['pdf', 'docx'],
            help="Upload a PDF or DOCX resume to create a new profile"
        )

        if uploaded_file:
            if st.button("🚀 Parse Resume", type="primary", use_container_width=True):
                # Check for API key
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    st.error("ANTHROPIC_API_KEY not set in environment variables")
                else:
                    with st.spinner("Parsing resume with Claude AI..."):
                        try:
                            # Save uploaded file temporarily
                            data_dir = Path(__file__).parent.parent.parent / "data" / "resumes"
                            data_dir.mkdir(parents=True, exist_ok=True)

                            file_path = data_dir / uploaded_file.name
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            # Extract text from resume
                            resume_text = extract_text_from_resume(str(file_path))

                            if not resume_text:
                                st.error("Could not extract text from resume. Please check the file.")
                            else:
                                # Parse with Claude
                                st.info("Extracting profile data with AI...")
                                profile_data = extract_profile_from_text(resume_text)

                                if profile_data:
                                    # Save to database
                                    profile_id, was_updated = upsert_profile(profile_data, uploaded_file.name)

                                    if was_updated:
                                        st.success(f"Updated existing profile: {profile_data.get('name', 'Unknown')}")
                                    else:
                                        st.success(f"Created new profile: {profile_data.get('name', 'Unknown')}")

                                    st.rerun()
                                else:
                                    st.error("Could not parse profile data from resume")

                        except Exception as e:
                            st.error(f"Error parsing resume: {str(e)}")

    # Get all profiles
    profiles = list_profiles()

    if not profiles:
        st.warning("No profiles found in the database.")
        st.info("👈 Upload a resume using the sidebar to create your first profile.")

        # Show upload instructions
        st.markdown("---")
        st.subheader("Getting Started")
        st.markdown("""
        1. **Upload your resume** (PDF or DOCX) using the sidebar
        2. Click **Parse Resume** to extract your profile data
        3. Claude AI will automatically extract your skills and experience
        4. Your profile will be saved and you can start matching jobs!
        """)
        return

    # View mode selection
    view_mode = st.radio(
        "View Mode",
        options=["All Profiles", "Selected Profile Only"],
        horizontal=True
    )

    st.markdown("---")

    if view_mode == "All Profiles":
        # Display all profiles
        st.subheader(f"All Profiles ({len(profiles)})")

        for profile_data in profiles:
            # Get full profile details
            full_profile = get_profile(profile_data['id'])

            if full_profile:
                with st.expander(f"📋 {full_profile['name']}", expanded=False):
                    # Profile actions
                    col1, col2 = st.columns([4, 1])

                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{profile_data['id']}", type="secondary"):
                            if st.session_state.get(f"confirm_delete_{profile_data['id']}"):
                                delete_profile(profile_data['id'])
                                st.success(f"Deleted profile: {full_profile['name']}")
                                st.rerun()
                            else:
                                st.session_state[f"confirm_delete_{profile_data['id']}"] = True
                                st.warning("Click again to confirm deletion")

                    display_profile_card(full_profile)

                    # Tabs for skills and experience
                    tab1, tab2, tab3 = st.tabs(["Skills", "Experience", "Raw Data"])

                    with tab1:
                        skills = full_profile.get('skills', [])
                        display_skills(skills)

                    with tab2:
                        experience = full_profile.get('experience', [])
                        display_experience(experience)

                    with tab3:
                        st.json(full_profile)

    else:
        # Display selected profile only
        selected_profile_id = get_selected_profile()

        if not selected_profile_id:
            st.warning("Please select a profile from the sidebar.")
            return

        # Get full profile details
        profile = get_profile(selected_profile_id)

        if not profile:
            st.error("Profile not found.")
            return

        # Profile header with actions
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(f"Profile: {profile['name']}")

        with col2:
            if st.button("🗑️ Delete Profile", type="secondary"):
                if st.session_state.get(f"confirm_delete_selected"):
                    delete_profile(selected_profile_id)
                    st.success(f"Deleted profile: {profile['name']}")
                    st.rerun()
                else:
                    st.session_state["confirm_delete_selected"] = True
                    st.warning("Click again to confirm deletion")

        # Display profile
        display_profile_card(profile)

        # Tabs for detailed information
        tab1, tab2, tab3 = st.tabs(["Skills", "Experience", "Raw Data"])

        with tab1:
            skills = profile.get('skills', [])
            display_skills(skills)

            # Skill statistics
            if skills:
                st.markdown("---")
                st.subheader("Skill Statistics")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Skills", len(skills))

                with col2:
                    technical_skills = [s for s in skills if s.get('category') == 'technical']
                    st.metric("Technical Skills", len(technical_skills))

                with col3:
                    soft_skills = [s for s in skills if s.get('category') == 'soft']
                    st.metric("Soft Skills", len(soft_skills))

        with tab2:
            experience = profile.get('experience', [])
            display_experience(experience)

            # Experience statistics
            if experience:
                st.markdown("---")
                st.subheader("Experience Statistics")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Positions", len(experience))

                with col2:
                    companies = set(e.get('company', '') for e in experience)
                    st.metric("Companies Worked At", len(companies))

        with tab3:
            st.json(profile)

    st.markdown("---")

    # Tips section
    st.subheader("Tips")
    st.markdown("""
    - **Upload resumes** in PDF or DOCX format for best results
    - **Claude AI** extracts skills, experience, and contact information automatically
    - **Select a profile** from the sidebar to use it across all pages
    - **Delete profiles** you no longer need to keep your database clean
    """)


if __name__ == "__main__":
    main()
