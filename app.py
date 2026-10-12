"""Main Streamlit application - Refactored for modularity"""
import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ui.sidebar import render_sidebar, initialize_session_state
from ui.interview_prep import render_interview_prep_tab
from ui.mock_interview import render_mock_interview_tab
from ui.chatbot import render_chatbot_tab
from ui.analytics import render_analytics_tab
from ui.security import render_security_testing_tab
from ui.visual_tools import render_visual_tools_tab
from ui.quiz_tracker import render_quiz_tracker_tab
from ui.auth import require_authenticated_user
from ui.v2_theme import apply_v2_theme, render_brand_bar

# Set up the page
st.set_page_config(
    page_title="Interview Practice · V2",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main orchestrator function, protected by Google OIDC login."""
    user = require_authenticated_user()
    st.session_state.auth_user_id = user["id"]
    initialize_session_state()

    # V2 styling is presentation-only; feature modules remain unchanged.
    apply_v2_theme()

    with st.sidebar:
        st.caption("SIGNED IN AS")
        st.write(f"**{user['name']}**")
        st.caption(user["email"])
        st.button("Sign out", on_click=st.logout, use_container_width=True)

    render_brand_bar()

    # Render sidebar configuration and get the exact same feature configuration.
    sidebar_config = render_sidebar()

    # Keep the existing seven workspaces and their original render functions.
    tab_names = [
        "🧠 Quiz Studio & Progress",
        "📚 Interview Prep",
        "🎤 Mock Interview",
        "💬 Chat Assistant",
        "📊 Analytics",
        "🎨 Visual Tools",
        "🔒 Security Testing",
    ]

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    st.markdown('<div class="v2-nav-label">JUMP TO A WORKSPACE</div>', unsafe_allow_html=True)
    nav_intro, nav_picker = st.columns([0.34, 0.66], gap="medium")
    with nav_intro:
        st.markdown("**What are we working on?**")
        st.markdown(
            '<div class="v2-nav-hint">Your practice history and saved progress stay intact.</div>',
            unsafe_allow_html=True,
        )
    with nav_picker:
        # Streamlit's native selectbox supports type-to-filter, so this stays a
        # real navigation control rather than a decorative, non-functional search.
        selected_section = st.selectbox(
            "Search sections",
            options=tab_names,
            index=st.session_state.active_tab,
            placeholder="Type to find a section…",
            label_visibility="collapsed",
        )
        st.session_state.active_tab = tab_names.index(selected_section)

    st.markdown("---")

    # Existing rendering and feature behavior stays the same.
    if st.session_state.active_tab == 0:
        render_quiz_tracker_tab(user_id=user["id"])
    elif st.session_state.active_tab == 1:
        render_interview_prep_tab(sidebar_config)
    elif st.session_state.active_tab == 2:
        render_mock_interview_tab(sidebar_config)
    elif st.session_state.active_tab == 3:
        render_chatbot_tab(sidebar_config)
    elif st.session_state.active_tab == 4:
        render_analytics_tab()
    elif st.session_state.active_tab == 5:
        render_visual_tools_tab()
    elif st.session_state.active_tab == 6:
        render_security_testing_tab()


if __name__ == "__main__":
    main()
