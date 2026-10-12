"""Main Streamlit application — V2 presentation shell over the existing feature engines."""
import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ui.sidebar import render_sidebar, initialize_session_state
from ui.dashboard import render_dashboard
from ui.practice_hub import render_practice_hub
from ui.settings import render_settings, load_user_preferences, apply_user_preferences
from ui.reports import render_reports
from ui.interview_prep import render_interview_prep_tab
from ui.mock_interview import render_mock_interview_tab
from ui.chatbot import render_chatbot_tab
from ui.analytics import render_analytics_tab
from ui.security import render_security_testing_tab
from ui.visual_tools import render_visual_tools_tab
from ui.quiz_tracker import (
    render_quiz_tracker_tab,
    _daily_stats,
    _load_history,
    _now,
)
from ui.auth import require_authenticated_user
from ui.v2_theme import apply_v2_theme, render_brand_bar

# Set up the page
st.set_page_config(
    page_title="Interview Practice · V2",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


_WORKSPACE_LABELS = {
    -4: "⚙️ Settings",
    -3: "📄 Reports & History",
    -2: "🧪 Practice Hub",
    -1: "🏠 Command Center",
    0: "🧠 Quiz Studio & Progress",
    1: "📚 Interview Prep",
    2: "🎤 Mock Interview",
    3: "💬 Chat Assistant",
    4: "📊 Analytics",
    5: "🎨 Visual Tools",
    6: "🔒 Security Testing",
}


def _navigate(index: int, focus: str = "", topic: str = "") -> None:
    """Route to an existing workspace or one of the V2 wrapper screens."""
    st.session_state.active_tab = index
    if index in _WORKSPACE_LABELS:
        st.session_state.v2_workspace_picker = _WORKSPACE_LABELS[index]
    if focus:
        st.session_state.quiz_tracker_focus = focus
    elif index != 0:
        st.session_state.pop("quiz_tracker_focus", None)
    if topic:
        st.session_state.quiz_tracker_subject_input = topic
        st.session_state.quiz_tracker_focus = "topic"
    st.session_state.v2_global_search = ""


def _search_results(query: str, user_id: str) -> list[dict]:
    """Find workspaces and saved quiz topics without mutating stored records."""
    query = query.strip().casefold()
    if not query:
        return []

    result: list[dict] = []
    aliases = [
        (-1, ["dashboard", "home", "progress", "performance", "overview", "streak"]),
        (-2, ["practice", "practice hub", "quiz studio", "pdf practice", "notes", "weak topic", "weak topics"]),
        (-3, ["report", "reports", "history", "pdf download", "result card", "mock reports"]),
        (-4, ["settings", "profile", "account", "study goal", "preferences", "sign out"]),
        (0, ["quiz", "quizzes", "timed mock", "mock test", "revision"]),
        (1, ["interview prep", "study mode", "job description", "cv", "resume"]),
        (2, ["mock interview", "interview practice", "behavioral interview"]),
        (3, ["chat", "assistant", "ask a question"]),
        (4, ["analytics", "charts", "statistics", "stats"]),
        (5, ["visual tools", "result card", "shareable card"]),
        (6, ["security", "jailbreak", "security testing"]),
    ]
    for index, terms in aliases:
        label = _WORKSPACE_LABELS[index]
        if query in label.casefold() or any(query in term or term in query for term in terms):
            result.append({"label": label, "index": index, "kind": "workspace"})

    # Search topic labels from the same user-scoped data used by the dashboard.
    try:
        _, topics = _load_history(user_id)
        for row in topics:
            topic = str(row.get("topic") or "").strip()
            if topic and query in topic.casefold():
                result.append({
                    "label": f"Topic: {topic}",
                    "index": 0,
                    "kind": "topic",
                    "topic": topic,
                    "focus": "topic",
                })
    except Exception:
        # Navigation should remain usable even if optional search data is unavailable.
        pass

    # Keep the quick-switch compact and avoid duplicate workspace entries.
    unique = []
    seen = set()
    for item in result:
        key = (item["index"], item.get("topic", ""))
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:6]


def main():
    """Main orchestrator function, protected by Google OIDC login."""
    user = require_authenticated_user()
    st.session_state.auth_user_id = user["id"]
    initialize_session_state()
    load_user_preferences(user["id"])

    # A new session opens on the command center (unless the user selected another
    # landing point in Settings during this session). Existing feature indexes 0–6
    # remain stable, so widget and feature behavior is not remapped.
    if not st.session_state.get("_v2_workspace_initialized"):
        preferred = st.session_state.get("v2_landing_preference", "Command Center")
        st.session_state.active_tab = -2 if preferred == "Practice Hub" else -1
        st.session_state._v2_workspace_initialized = True

    apply_v2_theme()
    apply_user_preferences()
    render_brand_bar()

    # Real study streak for the compact productivity bar. Failure to read it must
    # never block normal navigation.
    current_streak = 0
    try:
        attempts, _ = _load_history(user["id"])
        _, current_streak, _ = _daily_stats(attempts, _now().date())
    except Exception:
        pass

    current_index = st.session_state.get("active_tab", -1)
    current_label = st.session_state.get("v2_workspace_picker") or _WORKSPACE_LABELS.get(current_index, "🏠 Command Center")
    with st.container():
        bar_title, bar_search, bar_streak, bar_profile = st.columns([1.15, 2.25, 0.72, 0.9], gap="small")
        with bar_title:
            st.markdown("**YOUR WORKSPACE**")
            st.caption(current_label)
        with bar_search:
            st.text_input(
                "Search workspaces and topics",
                placeholder="Search workspaces, topics, reports…",
                key="v2_global_search",
                label_visibility="collapsed",
            )
        with bar_streak:
            st.markdown(
                f'<div class="v2-top-streak">🔥 <strong>{current_streak}</strong><small>day streak</small></div>',
                unsafe_allow_html=True,
            )
        with bar_profile:
            with st.popover("👤 Profile", use_container_width=True):
                st.markdown(f"**{user['name']}**")
                st.caption(user["email"])
                st.button(
                    "Profile & settings",
                    key="v2_profile_settings",
                    use_container_width=True,
                    on_click=_navigate,
                    args=(-4,),
                )
                st.button(
                    "Sign out",
                    key="v2_profile_signout",
                    use_container_width=True,
                    on_click=st.logout,
                )

    query = st.session_state.get("v2_global_search", "")
    if query.strip():
        results = _search_results(query, user["id"])
        if results:
            st.markdown('<div class="v2-nav-label">MATCHING RESULTS</div>', unsafe_allow_html=True)
            result_cols = st.columns(min(3, len(results)), gap="small")
            for position, result in enumerate(results):
                with result_cols[position % len(result_cols)]:
                    st.button(
                        result["label"],
                        key=f"v2_search_result_{position}_{result['index']}_{result.get('topic', '')}",
                        use_container_width=True,
                        on_click=_navigate,
                        args=(result["index"], result.get("focus", ""), result.get("topic", "")),
                    )
        else:
            st.caption("No matches yet. Try a workspace name or a topic from your saved quiz history.")

    # Compact icon-like workspace shortcuts sit above the collapsible AI settings.
    # The native Streamlit sidebar remains collapsible; shortcuts are real navigation.
    with st.sidebar:
        st.markdown('<div class="v2-sidebar-nav-title">WORKSPACES</div>', unsafe_allow_html=True)
        shortcuts = [
            ("⌂", -1, "Command Center"),
            ("▦", -2, "Practice Hub"),
            ("Q", 0, "Quiz Studio"),
            ("🎤", 2, "Mock Interview"),
            ("▤", -3, "Reports"),
            ("⚙", -4, "Settings"),
        ]
        for row_start in range(0, len(shortcuts), 3):
            shortcut_row = shortcuts[row_start:row_start + 3]
            shortcut_cols = st.columns(3, gap="small")
            for col, (icon_label, target_index, help_text) in zip(shortcut_cols, shortcut_row):
                with col:
                    st.button(
                        icon_label,
                        key=f"v2_sidebar_nav_{target_index}",
                        help=help_text,
                        use_container_width=True,
                        on_click=_navigate,
                        args=(target_index,),
                    )
        st.divider()

    # Render the existing model / prompt controls. Their values are passed through
    # unchanged to the original Interview Prep, Mock Interview, and Chat screens.
    sidebar_config = render_sidebar()

    workspace_order = [-1, -2, -3, -4, 0, 1, 2, 3, 4, 5, 6]
    workspace_options = [_WORKSPACE_LABELS[index] for index in workspace_order]
    active_tab = st.session_state.get("active_tab", -1)
    if active_tab not in workspace_order:
        active_tab = -1
        st.session_state.active_tab = active_tab

    nav_intro, nav_picker = st.columns([0.42, 0.58], gap="medium")
    with nav_intro:
        st.markdown('<div class="v2-nav-label">GO TO A WORKSPACE</div>', unsafe_allow_html=True)
        st.caption("Type in the search above, or choose a destination.")
    with nav_picker:
        selected_label = st.selectbox(
            "Workspace",
            options=workspace_options,
            index=workspace_order.index(active_tab),
            label_visibility="collapsed",
            key="v2_workspace_picker",
        )
    # The keyed picker is the single source of truth after manual navigation.
    selected_index = workspace_order[workspace_options.index(selected_label)]
    st.session_state.active_tab = selected_index

    st.markdown("---")

    if selected_index == -1:
        render_dashboard(user_id=user["id"], user_name=user["name"])
    elif selected_index == -2:
        render_practice_hub()
    elif selected_index == -3:
        render_reports(user["id"])
    elif selected_index == -4:
        render_settings(user)
    elif selected_index == 0:
        render_quiz_tracker_tab(user_id=user["id"])
    elif selected_index == 1:
        render_interview_prep_tab(sidebar_config)
    elif selected_index == 2:
        render_mock_interview_tab(sidebar_config)
    elif selected_index == 3:
        render_chatbot_tab(sidebar_config)
    elif selected_index == 4:
        render_analytics_tab(user_id=user["id"])
    elif selected_index == 5:
        render_visual_tools_tab()
    elif selected_index == 6:
        render_security_testing_tab()


if __name__ == "__main__":
    main()
