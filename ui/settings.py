"""Organized settings hub. Reuses existing user-scoped study-goal persistence."""
from __future__ import annotations

import streamlit as st

from ui.quiz_tracker import DEFAULT_DAILY_GOAL, _get_daily_goal, _save_daily_goal


_SETTINGS_CSS = """
<style>
.v2-settings-intro { padding:1.25rem 1.4rem; margin-bottom:1rem; border:1px solid #E9E5D5; border-radius:18px; background:linear-gradient(110deg,#FFFFFF 0%,#FFFFFF 76%,#FFF4B8 100%); }
.v2-settings-kicker { color:#3556D8; font-size:.67rem; font-weight:850; letter-spacing:.12em; }
.v2-settings-intro h1 { margin:.5rem 0 .35rem; color:#1B2340; letter-spacing:-.05em; }
.v2-settings-intro p { margin:0; color:#68718A; line-height:1.55; }
.v2-settings-section { color:#3556D8; font-size:.68rem; font-weight:850; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.25rem; }
.v2-settings-value { color:#1B2340; font-size:1rem; font-weight:750; overflow-wrap:anywhere; }
</style>
"""


def render_settings(user: dict) -> None:
    """Render profile, account, goals, appearance preferences, and sign-out."""
    st.markdown(_SETTINGS_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <section class="v2-settings-intro">
          <div class="v2-settings-kicker">YOUR SPACE</div>
          <h1>Profile & settings</h1>
          <p>Manage your account details, study target and comfortable viewing preferences.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    profile, account = st.columns([1, 1], gap="medium")
    with profile:
        with st.container(border=True):
            st.markdown('<div class="v2-settings-section">PROFILE</div>', unsafe_allow_html=True)
            name = str(user.get("name") or "Learner")
            email = str(user.get("email") or "Not available")
            st.markdown(f'<div class="v2-settings-value">{name}</div>', unsafe_allow_html=True)
            st.caption("Signed-in profile")
            st.write(email)
            st.caption("Account identity comes from the existing Google sign-in.")
    with account:
        with st.container(border=True):
            st.markdown('<div class="v2-settings-section">ACCOUNT & ACCESS</div>', unsafe_allow_html=True)
            st.write("Google authentication is managed by the existing secure sign-in flow.")
            st.write("Quiz and report history remains scoped to your signed-in account.")
            st.caption("Security-sensitive credentials are never shown here.")

    st.markdown("## Study goals")
    with st.container(border=True):
        st.markdown('<div class="v2-settings-section">PERSONAL TARGET</div>', unsafe_allow_html=True)
        user_id = str(user.get("id") or st.session_state.get("auth_user_id") or "")
        try:
            goal = _get_daily_goal(user_id) if user_id else DEFAULT_DAILY_GOAL
        except Exception:
            goal = DEFAULT_DAILY_GOAL
            st.warning("Your saved goal could not be loaded. The default is shown temporarily.")
        if "daily_goal_input" not in st.session_state:
            st.session_state.daily_goal_input = goal
        st.number_input(
            "Questions to complete per day",
            min_value=5,
            max_value=200,
            step=5,
            key="daily_goal_input",
            on_change=_save_daily_goal,
            args=(user_id,),
            help="Saved using the existing per-user study-goal setting.",
        )
        st.caption("Your dashboard uses this target for daily progress.")

    st.markdown("## Viewing preferences")
    with st.container(border=True):
        st.markdown('<div class="v2-settings-section">DEFAULT LANDING PAGE</div>', unsafe_allow_html=True)
        st.selectbox(
            "Start each visit at",
            options=["Command Center", "Practice Hub"],
            key="v2_landing_preference",
            help="Applies to a new app session in this browser session; it doesn't change saved practice data.",
        )
        st.markdown('<div class="v2-settings-section">COMFORT & DENSITY</div>', unsafe_allow_html=True)
        st.checkbox(
            "Compact cards and tighter spacing",
            key="v2_compact_layout",
            help="Affects presentation in this browser session only; no study data is changed.",
        )
        st.checkbox(
            "Reduce decorative motion",
            key="v2_reduce_motion",
            help="A visual preference for this session. Core interactions and timers are unchanged.",
        )
        if st.session_state.get("v2_compact_layout"):
            st.markdown(
                "<style>[data-testid='stMetric']{padding:.65rem!important}"
                "[data-testid='stVerticalBlockBorderWrapper']{border-radius:12px!important}"
                "[data-testid='stMainBlockContainer']{padding-top:.7rem!important}</style>",
                unsafe_allow_html=True,
            )
        if st.session_state.get("v2_reduce_motion"):
            st.markdown(
                "<style>*,*::before,*::after{animation:none!important;transition:none!important;"
                "scroll-behavior:auto!important}</style>",
                unsafe_allow_html=True,
            )
        st.caption("These two appearance preferences currently apply to this session; account and study data stay unchanged.")

    st.markdown("## Sign out")
    with st.container(border=True):
        st.write("Finish this session on the current device.")
        st.button(
            "Sign out of Interview Practice",
            key="v2_settings_sign_out",
            type="primary",
            on_click=st.logout,
            use_container_width=True,
        )
