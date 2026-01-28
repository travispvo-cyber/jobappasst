"""
Job Application Assistant - Streamlit Web Interface
Main landing page with profile selection and database statistics
Supports both local (database) and cloud (session-based) modes
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_app.utils.session_state import (
    init_session_state,
    set_selected_profile,
    get_selected_profile,
    get_selected_profile_name,
    get_cloud_mode,
    get_session_profile,
    get_session_jobs,
    get_session_matches
)


def get_api_key(key_name: str) -> str:
    """Get API key from Streamlit secrets or environment"""
    import os
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["api_keys"][key_name]
    except (KeyError, FileNotFoundError):
        pass
    # Fall back to environment variable
    return os.getenv(key_name, "")


def main():
    """Main application entry point"""

    # Page configuration
    st.set_page_config(
        page_title="Job Application Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_session_state()
    cloud_mode = get_cloud_mode()

    # Sidebar
    with st.sidebar:
        st.title("🤖 Job App Assistant")

        if cloud_mode:
            st.caption("☁️ Cloud Mode")
        else:
            st.caption("💾 Local Mode")

        st.markdown("---")

        if cloud_mode:
            # Cloud mode - session-based profile
            session_profile = get_session_profile()
            if session_profile:
                st.success(f"Profile: **{session_profile.get('name', 'Your Profile')}**")
                skills = session_profile.get('skills', [])
                if skills:
                    st.caption(f"{len(skills)} skills detected")
            else:
                st.info("Upload a resume to get started!")
        else:
            # Local mode - database profiles
            try:
                from src.db.queries import list_profiles
                profiles = list_profiles()

                if not profiles:
                    st.warning("No profiles found!")
                    st.info("Upload a resume in the Profiles page.")
                else:
                    profile_options = {
                        f"{p['name']} ({p.get('email', 'No email')})": p['id']
                        for p in profiles
                    }

                    selected_key = st.selectbox(
                        "Select Profile",
                        options=list(profile_options.keys()),
                        key="profile_selector"
                    )

                    if selected_key:
                        profile_id = profile_options[selected_key]
                        profile_name = selected_key.split(" (")[0]
                        set_selected_profile(profile_id, profile_name)
            except Exception as e:
                st.error(f"Database error: {e}")
                profiles = []

        st.markdown("---")
        st.caption("**Pages:**")
        st.caption("📤 Upload Resume")
        st.caption("💼 Jobs")
        st.caption("🎯 Matches")
        if not cloud_mode:
            st.caption("📝 Applications")

    # Main content
    st.title("🤖 Job Application Assistant")
    st.markdown("### AI-powered job search companion")

    if cloud_mode:
        st.info("☁️ **Cloud Mode**: Upload your resume to get personalized job matches. Data is stored in your browser session only.")
    else:
        current_profile = get_selected_profile()
        if current_profile:
            st.success(f"Viewing data for: **{get_selected_profile_name()}**")
        else:
            st.info("Select a profile from the sidebar to get started.")

    st.markdown("---")

    # Statistics
    st.header("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)

    if cloud_mode:
        # Session-based stats
        session_profile = get_session_profile()
        session_jobs = get_session_jobs()
        session_matches = get_session_matches()

        with col1:
            st.metric("Profile", "1" if session_profile else "0")
        with col2:
            st.metric("Jobs Found", len(session_jobs))
        with col3:
            remote_jobs = [j for j in session_jobs if j.get('remote')]
            st.metric("Remote Jobs", len(remote_jobs))
        with col4:
            st.metric("Matches", len(session_matches))
    else:
        # Database stats
        try:
            from src.db.queries import list_profiles, list_jobs, get_matches_for_profile
            profiles = list_profiles()
            all_jobs = list_jobs(limit=1000)
            current_profile = get_selected_profile()

            with col1:
                st.metric("Profiles", len(profiles) if profiles else 0)
            with col2:
                st.metric("Jobs", len(all_jobs) if all_jobs else 0)
            with col3:
                remote_jobs = [j for j in all_jobs if j.get('remote')] if all_jobs else []
                st.metric("Remote Jobs", len(remote_jobs))
            with col4:
                if current_profile:
                    matches = get_matches_for_profile(current_profile, min_score=0, limit=1000)
                    st.metric("Your Matches", len(matches) if matches else 0)
                else:
                    st.metric("Your Matches", 0)
        except Exception:
            for col in [col1, col2, col3, col4]:
                with col:
                    st.metric("--", 0)

    st.markdown("---")

    # Quick Start
    st.header("🚀 Quick Start")

    if cloud_mode:
        st.markdown("""
        1. **📤 Upload Resume** - Go to the Upload page and submit your PDF or DOCX resume
        2. **⏳ AI Parsing** - Claude AI will extract your skills and experience
        3. **🔍 Find Jobs** - We'll search for matching remote jobs
        4. **🎯 View Matches** - See personalized job recommendations with match scores
        5. **📋 Apply** - Click through to apply on company websites
        """)

        # Check for API keys
        anthropic_key = get_api_key("ANTHROPIC_API_KEY")
        rapidapi_key = get_api_key("RAPIDAPI_KEY")

        if not anthropic_key or not rapidapi_key:
            st.warning("⚠️ API keys not configured. Some features may be limited.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **New Users:**
            1. Go to **👤 Profiles** page
            2. Upload your resume (PDF/DOCX)
            3. Browse **💼 Jobs**
            4. Check **🎯 Matches**
            """)
        with col2:
            st.markdown("""
            **Existing Users:**
            1. Select profile from sidebar
            2. View **🎯 Matches**
            3. Track **📝 Applications**
            """)

    st.markdown("---")

    # Features
    st.header("✨ Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📄 Resume Parsing**
        - Upload PDF/DOCX
        - AI-powered extraction
        - Skill detection
        """)

    with col2:
        st.markdown("""
        **🎯 Smart Matching**
        - Skill-based matching
        - 0-100% scores
        - Synonym recognition
        """)

    with col3:
        st.markdown("""
        **💼 Job Search**
        - Remote jobs
        - Real-time search
        - Direct apply links
        """)

    st.markdown("---")
    st.caption("Built with Streamlit, Claude AI, and Python")
    st.caption("v2.0 - Cloud Edition" if cloud_mode else "v2.0 - Local Edition")


if __name__ == "__main__":
    main()
