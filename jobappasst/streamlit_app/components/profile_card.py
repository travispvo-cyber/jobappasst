"""
Profile display component
"""

import streamlit as st
from typing import Dict, List


def display_profile_card(profile: Dict):
    """Display a profile in a card format"""

    with st.container():
        st.markdown(f"### {profile['name']}")

        # Contact information
        col1, col2, col3 = st.columns(3)
        with col1:
            if profile.get('email'):
                st.write(f"📧 {profile['email']}")
        with col2:
            if profile.get('phone'):
                st.write(f"📱 {profile['phone']}")
        with col3:
            if profile.get('location'):
                st.write(f"📍 {profile['location']}")

        # Summary
        if profile.get('summary'):
            st.write("**Summary:**")
            st.write(profile['summary'])

        st.divider()


def display_skills(skills: List[Dict]):
    """Display skills in a formatted layout"""

    if not skills:
        st.info("No skills found")
        return

    st.write(f"**Skills ({len(skills)}):**")

    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category = skill.get('category', 'Other')
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)

    # Display skills by category
    for category, category_skills in skills_by_category.items():
        with st.expander(f"{category.title()} ({len(category_skills)} skills)", expanded=True):
            for skill in category_skills:
                level = skill.get('level', '')
                years = skill.get('years', 0)

                skill_text = f"• **{skill['name']}**"
                if level:
                    skill_text += f" - {level.title()}"
                if years:
                    skill_text += f" ({years} years)"

                st.markdown(skill_text)


def display_experience(experiences: List[Dict]):
    """Display work experience"""

    if not experiences:
        st.info("No experience found")
        return

    st.write(f"**Experience ({len(experiences)}):**")

    for exp in experiences:
        with st.expander(f"{exp['title']} at {exp['company']}", expanded=False):
            # Date range
            start = exp.get('start_date', 'Unknown')
            end = exp.get('end_date', 'Present')
            st.write(f"**Duration:** {start} - {end}")

            if exp.get('industry'):
                st.write(f"**Industry:** {exp['industry']}")

            # Responsibilities
            if exp.get('responsibilities'):
                st.write("**Responsibilities:**")
                import json
                try:
                    resp = json.loads(exp['responsibilities']) if isinstance(exp['responsibilities'], str) else exp['responsibilities']
                    for r in resp:
                        st.write(f"• {r}")
                except:
                    st.write(exp['responsibilities'])

            # Accomplishments
            if exp.get('accomplishments'):
                st.write("**Accomplishments:**")
                try:
                    accom = json.loads(exp['accomplishments']) if isinstance(exp['accomplishments'], str) else exp['accomplishments']
                    for a in accom:
                        st.write(f"• {a}")
                except:
                    st.write(exp['accomplishments'])


def display_profile_summary(profile: Dict):
    """Display a compact profile summary"""

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.write(f"**{profile['name']}**")
        if profile.get('email'):
            st.caption(profile['email'])

    with col2:
        if profile.get('location'):
            st.write(f"📍 {profile['location']}")

    with col3:
        # Count skills
        skills_count = len(profile.get('skills', []))
        st.metric("Skills", skills_count)
