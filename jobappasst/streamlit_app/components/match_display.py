"""
Match display components for visualizing job match scores
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict


def display_match_gauge(score: float, title: str = "Match Score"):
    """Display a gauge chart for match score"""

    # Determine color based on score
    if score >= 75:
        bar_color = "#10B981"  # green
    elif score >= 50:
        bar_color = "#F59E0B"  # yellow/orange
    else:
        bar_color = "#EF4444"  # red

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'suffix': '%'},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': bar_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},
                {'range': [50, 75], 'color': '#fef3c7'},
                {'range': [75, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)


def display_score_progress_bar(score: float, label: str = None):
    """Display a simple progress bar for match score"""

    # Determine color based on score
    if score >= 75:
        color = "🟢"
        bar_color = "#10B981"
    elif score >= 50:
        color = "🟡"
        bar_color = "#F59E0B"
    else:
        color = "🔴"
        bar_color = "#EF4444"

    if label:
        st.write(f"**{label}**")

    # Create HTML progress bar
    html = f"""
    <div style="background-color: #e5e7eb; border-radius: 10px; padding: 3px; margin: 5px 0;">
        <div style="background-color: {bar_color}; width: {score}%; height: 20px; border-radius: 8px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
            <span style="color: white; font-weight: bold; font-size: 12px;">{score:.1f}%</span>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def display_skills_comparison(matched_skills: List[str], missing_skills: List[str]):
    """Display matched vs missing skills side by side"""

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Matched Skills**")
        if matched_skills:
            for skill in matched_skills:
                st.success(f"✓ {skill}")
        else:
            st.info("No matched skills")

    with col2:
        st.markdown("**❌ Missing Skills**")
        if missing_skills:
            for skill in missing_skills:
                st.warning(f"✗ {skill}")
        else:
            st.success("No missing skills!")


def display_skills_chips(skills: List[str], chip_type: str = "matched"):
    """Display skills as colored chips/tags"""

    if chip_type == "matched":
        bg_color = "#d1fae5"
        text_color = "#065f46"
    elif chip_type == "missing":
        bg_color = "#fee2e2"
        text_color = "#991b1b"
    else:
        bg_color = "#e0e7ff"
        text_color = "#3730a3"

    if skills:
        chips_html = ""
        for skill in skills:
            chips_html += f"""
            <span style="
                background-color: {bg_color};
                color: {text_color};
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 500;
                margin: 2px 4px 2px 0;
                display: inline-block;
            ">{skill}</span>
            """

        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.caption("None")


def display_match_summary_card(match: Dict):
    """Display a summary card for a job match"""

    score = match.get('match_score', 0)
    title = match.get('title', 'Unknown Position')
    company = match.get('company', 'Unknown Company')
    location = match.get('location', 'N/A')
    remote = match.get('remote', False)

    # Score indicator
    if score >= 75:
        score_badge = f'<span style="background: #10B981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{score:.0f}%</span>'
    elif score >= 50:
        score_badge = f'<span style="background: #F59E0B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{score:.0f}%</span>'
    else:
        score_badge = f'<span style="background: #EF4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{score:.0f}%</span>'

    remote_badge = '🌍 Remote' if remote else ''

    card_html = f"""
    <div style="
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background: white;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #1f2937;">{title}</h4>
                <p style="margin: 4px 0; color: #6b7280;">{company} • {location} {remote_badge}</p>
            </div>
            <div>{score_badge}</div>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def display_match_radar_chart(matched_skills: List[str], missing_skills: List[str], max_skills: int = 8):
    """Display a radar chart comparing matched vs required skills"""

    # Combine and limit skills
    all_skills = matched_skills[:max_skills//2] + missing_skills[:max_skills//2]

    if len(all_skills) < 3:
        st.info("Not enough skills data for radar chart")
        return

    # Create values (1 for matched, 0 for missing)
    values = []
    for skill in all_skills:
        if skill in matched_skills:
            values.append(1)
        else:
            values.append(0)

    # Close the radar chart
    all_skills_closed = all_skills + [all_skills[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=all_skills_closed,
        fill='toself',
        name='Your Skills',
        fillcolor='rgba(66, 135, 245, 0.3)',
        line=dict(color='#4287f5')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
