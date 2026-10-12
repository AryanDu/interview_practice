"""Hybrid analytics dashboard combining saved quiz history and existing app signals."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ui.quiz_tracker import _daily_stats, _load_history, _now


_ANALYTICS_CSS = """
<style>
.v2-analytics-hero { padding:1.25rem 1.45rem; margin-bottom:1rem; border:1px solid #E9E5D5; border-radius:18px; background:linear-gradient(110deg,#FFFFFF 0%,#FFFFFF 75%,#FFF4B8 100%); }
.v2-analytics-kicker { color:#3556D8; font-size:.67rem; font-weight:850; letter-spacing:.12em; }
.v2-analytics-hero h1 { margin:.45rem 0 .35rem; color:#1B2340; letter-spacing:-.055em; }
.v2-analytics-hero p { margin:0; color:#68718A; line-height:1.55; }
.v2-section-kicker { color:#3556D8; font-size:.66rem; font-weight:850; letter-spacing:.11em; margin:.2rem 0 .5rem; }
</style>
"""


def _open_quiz_studio() -> None:
    """Navigate via a callback so widget state is updated before the next render."""
    st.session_state.active_tab = 0
    st.session_state.v2_workspace_picker = "🧠 Quiz Studio & Progress"


def render_analytics_tab(user_id: str | None = None):
    """Analytics and statistics — read-only and scoped to the current signed-in user."""
    st.markdown(_ANALYTICS_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <section class="v2-analytics-hero">
          <div class="v2-analytics-kicker">MEASURE WHAT MATTERS</div>
          <h1>Progress & performance</h1>
          <p>Use recorded results to spot improvement, review weak areas and choose what to practise next.
          Missing history stays empty instead of being filled with sample numbers.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Current mock interview result remains visible using the original session values.
    if st.session_state.get("mock_interview_score") is not None:
        st.markdown('<div class="v2-section-kicker">LATEST MOCK INTERVIEW</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3, gap="medium")
        col1.metric("Interview score", f"{st.session_state.mock_interview_score}%")
        col2.metric("Domain", st.session_state.get("mock_interview_domain", "Not recorded"))
        col3.metric("Difficulty", st.session_state.get("mock_interview_difficulty", "Not recorded"))
        skills = st.session_state.get("mock_interview_skills", [])
        if skills:
            st.caption("Skills assessed: " + ", ".join(str(skill) for skill in skills))
        st.divider()

    profile_id = user_id or st.session_state.get("auth_user_id")
    if profile_id:
        try:
            attempts, topics = _load_history(profile_id)
            today_count, current_streak, best_streak = _daily_stats(attempts, _now().date())
        except Exception:
            attempts, topics = [], []
            today_count, current_streak, best_streak = 0, 0, 0
            st.warning("Saved quiz analytics couldn't be loaded. Other app metrics remain available.")

        total_questions = sum(int(row.get("total") or 0) for row in attempts)
        total_correct = sum(int(row.get("correct") or 0) for row in attempts)
        overall_accuracy = round(100 * total_correct / total_questions) if total_questions else None

        st.markdown('<div class="v2-section-kicker">QUIZ PERFORMANCE</div>', unsafe_allow_html=True)
        metrics = st.columns(4, gap="medium")
        metrics[0].metric("Sessions", len(attempts))
        metrics[1].metric("Questions", total_questions)
        metrics[2].metric("Accuracy", f"{overall_accuracy}%" if overall_accuracy is not None else "—")
        metrics[3].metric("Current streak", f"{current_streak} days", f"Best: {best_streak}" if best_streak else None)

        if attempts:
            # Use the saved attempt rows. The graph is a summary of actual results,
            # not an inferred model score or mock data.
            chart_rows = []
            for row in reversed(attempts):
                date_value = str(row.get("completed_at") or row.get("created_at") or "")[:10]
                if date_value:
                    chart_rows.append({
                        "Date": date_value,
                        "Score (%)": int(row.get("score") or 0),
                        "Questions": int(row.get("total") or 0),
                    })
            st.markdown("### Recent score trend")
            if chart_rows:
                trend = pd.DataFrame(chart_rows)
                trend = trend.groupby("Date", as_index=False).agg({"Score (%)": "mean", "Questions": "sum"})
                trend["Score (%)"] = trend["Score (%)"].round(1)
                left, right = st.columns([1.35, 0.85], gap="medium")
                with left:
                    st.line_chart(trend.set_index("Date")[["Score (%)"]], y_label="Score (%)")
                with right:
                    st.markdown("**Questions completed by day**")
                    st.bar_chart(trend.set_index("Date")[["Questions"]], y_label="Questions")
            else:
                st.caption("A score trend will appear after a completed session.")

            topic_rows = []
            for row in topics:
                attempted = int(row.get("attempted") or 0)
                correct = int(row.get("correct") or 0)
                if attempted:
                    topic_rows.append({
                        "Topic": str(row.get("topic") or "General"),
                        "Accuracy": round(100 * correct / attempted),
                        "Questions": attempted,
                    })
            if topic_rows:
                topic_rows.sort(key=lambda row: (row["Accuracy"], -row["Questions"]))
                left, right = st.columns(2, gap="medium")
                with left:
                    st.markdown("### Skill heatmap")
                    st.dataframe(
                        pd.DataFrame(topic_rows),
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Accuracy": st.column_config.ProgressColumn(
                                "Accuracy", min_value=0, max_value=100, format="%d%%"
                            ),
                        },
                    )
                with right:
                    st.markdown("### Where to focus")
                    for row in topic_rows[:3]:
                        st.progress(
                            row["Accuracy"] / 100,
                            text=f"{row['Topic']} · {row['Accuracy']}% · {row['Questions']} questions",
                        )
            else:
                st.info("Topic insights will appear after your first saved quiz.")

            with st.expander("View saved quiz attempts", expanded=False):
                for row in attempts[:20]:
                    date_value = str(row.get("completed_at") or row.get("created_at") or "").replace("T", " ")[:16]
                    with st.container(border=True):
                        left, right = st.columns([1.4, 0.6])
                        left.markdown(f"**{row.get('subject', 'Quiz')}**")
                        left.caption(f"{date_value} · {row.get('difficulty', 'Mixed')} · {row.get('mode', 'practice')}")
                        right.metric("Score", f"{int(row.get('score') or 0)}%")
        else:
            with st.container(border=True):
                st.markdown("### No quiz history yet — your first session starts the trend.")
                st.write("Complete a quiz to unlock the accuracy chart, topic breakdown and practice history.")
                st.button(
                    "Open Quiz Studio",
                    key="analytics_first_quiz",
                    type="primary",
                    on_click=_open_quiz_studio,
                )
    st.divider()

    # The existing app-level security/vector/chat statistics remain available.
    if st.session_state.get("security_guard"):
        st.markdown('<div class="v2-section-kicker">SECURITY ACTIVITY</div>', unsafe_allow_html=True)
        report = st.session_state.security_guard.get_security_report()
        cols = st.columns(3, gap="medium")
        cols[0].metric("Total requests", report["total_requests"])
        cols[1].metric("Unique users", report["unique_users"])
        cols[2].metric("Blocked patterns", report["blocked_patterns_count"])

    if st.session_state.get("vector_db"):
        st.markdown('<div class="v2-section-kicker">VECTOR STORE</div>', unsafe_allow_html=True)
        try:
            stats = st.session_state.vector_db.get_stats()
            st.metric("Total documents", stats["total_documents"])
        except Exception:
            st.warning("Vector-store statistics are temporarily unavailable.")

    with st.expander("Conversation history", expanded=False):
        entries = st.session_state.get("conversation_history", [])
        if entries:
            for index, entry in enumerate(reversed(entries[-10:]), 1):
                with st.container(border=True):
                    st.markdown(f"**Entry {index}: {entry.get('domain', 'Unknown')}**")
                    st.caption(f"Technique: {entry.get('technique', 'N/A')}")
                    st.json(entry)
        else:
            st.caption("No conversation history yet. Generated study packs will appear here.")
