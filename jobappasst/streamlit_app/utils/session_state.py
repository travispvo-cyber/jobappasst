"""
Session state management utilities for Streamlit app
"""

import streamlit as st
import os
from pathlib import Path


def is_cloud_mode():
    """
    Detect if running on Streamlit Cloud (no local database).
    Returns True if running in cloud mode.
    """
    # Check for Streamlit Cloud environment
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        return True

    # Check if database exists locally
    db_path = Path(__file__).parent.parent.parent / "data" / "jobapp.db"
    if not db_path.exists():
        return True

    return False


def init_session_state():
    """Initialize session state variables"""
    if "selected_profile_id" not in st.session_state:
        st.session_state.selected_profile_id = None

    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    if "filters" not in st.session_state:
        st.session_state.filters = {}

    # Cloud mode - session-based data storage
    if "cloud_mode" not in st.session_state:
        st.session_state.cloud_mode = is_cloud_mode()

    if "session_profile" not in st.session_state:
        st.session_state.session_profile = None

    if "session_jobs" not in st.session_state:
        st.session_state.session_jobs = []

    if "session_matches" not in st.session_state:
        st.session_state.session_matches = []


def get_cloud_mode():
    """Check if running in cloud mode"""
    return st.session_state.get("cloud_mode", False)


def set_session_profile(profile_data: dict):
    """Store profile data in session (for cloud mode)"""
    st.session_state.session_profile = profile_data
    st.session_state.selected_profile_id = "session"
    st.session_state.user_name = profile_data.get("name", "Your Profile")


def get_session_profile():
    """Get session-stored profile data"""
    return st.session_state.get("session_profile")


def set_session_jobs(jobs: list):
    """Store jobs in session (for cloud mode)"""
    st.session_state.session_jobs = jobs


def get_session_jobs():
    """Get session-stored jobs"""
    return st.session_state.get("session_jobs", [])


def set_session_matches(matches: list):
    """Store matches in session (for cloud mode)"""
    st.session_state.session_matches = matches


def get_session_matches():
    """Get session-stored matches"""
    return st.session_state.get("session_matches", [])


def set_selected_profile(profile_id, profile_name):
    """Set the currently selected profile"""
    st.session_state.selected_profile_id = profile_id
    st.session_state.user_name = profile_name


def get_selected_profile():
    """Get the currently selected profile ID"""
    return st.session_state.get("selected_profile_id")


def get_selected_profile_name():
    """Get the currently selected profile name"""
    return st.session_state.get("user_name", "No Profile Selected")


def clear_profile_selection():
    """Clear the selected profile"""
    st.session_state.selected_profile_id = None
    st.session_state.user_name = None


def set_filter(key, value):
    """Set a filter value"""
    if "filters" not in st.session_state:
        st.session_state.filters = {}
    st.session_state.filters[key] = value


def get_filter(key, default=None):
    """Get a filter value"""
    return st.session_state.get("filters", {}).get(key, default)


def clear_filters():
    """Clear all filters"""
    st.session_state.filters = {}
