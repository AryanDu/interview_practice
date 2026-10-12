"""Read-only V2 command-center dashboard.

This module only reads the existing per-user quiz history and routes users to
existing workspaces. It does not write to the database or change scoring.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from ui.quiz_tracker import _daily_stats, _get_daily_goal, _load_history, _now


def _go_to_workspace(index: int) -> None:
    """Use the app's existing workspace switcher to open a feature."""
    st.session_state.active_tab = index


def _accuracy(topics: list[dict]) -> list[dict]:
    rows = []
    for topic in topics:
        attempted = int(topic.get("attempted") or 0)
        correct = int(topic.get("correct") or 0)
        rows.append(
            {
                "topic": str(topic.get("topic") or "General"),
                "attempted": attempted,
                "accuracy": round(100 * correct / attempted) if attempted else 0,
            }
        )
    return rows


def _render_action_card(
    column,
    *,
    number: str,
    title: str,
    descriptor: str,
    button_label: str,
    target_index: int,
    action_key: str,
) -> None:
    with column:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="v2-action-heading">
                  <span class="v2-action-number">{escape(number)}</span>
                  <div class="v2-action-title">{escape(title)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(descriptor)
            st.button(
                button_label,
                key=f"v2_action_{action_key}",
                use_container_width=True,
                on_click=_go_to_workspace,
                args=(target_index,),
            )


def render_dashboard(user_id: str, user_name: str = "") -> None:
    """Render progress-led homepage from the signed-in user's real history."""
    first_name = (user_name or "").strip().split()
    display_name = escape(first_name[0]) if first_name else "there"

    st.markdown(
        f"""
        <section class="v2-dashboard-hero">
          <div class="v2-hero-kicker">YOUR AI INTERVIEW COMMAND CENTER</div>
          <h1>Welcome back, {display_name}.</h1>
          <p>Your preparation, at a glance. Review your progress, spot the next skill to build,
          and choose a focused session when you're ready.</p>
          <div class="v2-hero-foot"><span></span> PRACTICE&nbsp;&nbsp; / &nbsp;&nbsp;REVIEW&nbsp;&nbsp; / &nbsp;&nbsp;IMPROVE</div>
          <div class="v2-hero-orbit" aria-hidden="true"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # These are read-only calls to the existing user-scoped quiz history.
    try:
        attempts, topics = _load_history(user_id)
        goal = _get_daily_goal(user_id)
        today_count, streak, best_streak = _daily_stats(attempts, _now().date())
    except Exception:
        st.error(
            "We couldn't load your saved progress just now. Your existing records haven't been changed."
        )
        if st.button("Retry loading progress", key="v2_dashboard_retry", type="primary"):
            st.rerun()
        return

    total_questions = sum(int(row.get("total") or 0) for row in attempts)
    total_correct = sum(int(row.get("correct") or 0) for row in attempts)
    overall_accuracy = round(100 * total_correct / total_questions) if total_questions else None

    metric_cols = st.columns(4, gap="medium")
    metric_cols[0].metric("Questions answered", f"{total_questions:,}")
    metric_cols[1].metric(
        "Overall accuracy",
        f"{overall_accuracy}%" if overall_accuracy is not None else "—",
        f"{total_correct:,} correct" if total_questions else "Start with your first quiz",
    )
    metric_cols[2].metric("Practice sessions", f"{len(attempts):,}")
    metric_cols[3].metric(
        "Current streak",
        f"{streak} days" if streak else "Start today",
        f"Best: {best_streak} days" if best_streak else "A little practice adds up",
    )

    topic_rows = _accuracy(topics)
    established_topics = [row for row in topic_rows if row["attempted"] >= 3]
    weakest = sorted(established_topics, key=lambda row: (row["accuracy"], -row["attempted"]))
    strongest = sorted(established_topics, key=lambda row: (-row["accuracy"], -row["attempted"]))

    focus_col, goal_col = st.columns([1.2, 0.8], gap="medium")
    with focus_col:
        with st.container(border=True):
            st.markdown('<div class="v2-panel-kicker">YOUR NEXT BEST STEP</div>', unsafe_allow_html=True)
            if weakest:
                target = weakest[0]
                st.markdown(f"### Give **{escape(target['topic'])}** another round.")
                st.write(
                    f"Your recorded accuracy is {target['accuracy']}% across "
                    f"{target['attempted']} questions. A short revision session can help reinforce it."
                )
                st.button(
                    "Open Quiz Studio",
                    key="v2_next_step_quiz",
                    type="primary",
                    on_click=_go_to_workspace,
                    args=(0,),
                    use_container_width=True,
                )
            elif attempts:
                st.markdown("### Build a clearer skill picture.")
                st.write(
                    "Keep practising. Once a topic has at least three recorded questions, "
                    "the dashboard can highlight reliable strengths and revision opportunities."
                )
                st.button(
                    "Continue practising",
                    key="v2_next_step_continue",
                    type="primary",
                    on_click=_go_to_workspace,
                    args=(0,),
                    use_container_width=True,
                )
            else:
                st.markdown("### Start with one focused session.")
                st.write(
                    "Your dashboard is ready. Complete a quiz to begin building your personal "
                    "history, topic accuracy and study streak."
                )
                st.button(
                    "Create your first quiz",
                    key="v2_next_step_first_quiz",
                    type="primary",
                    on_click=_go_to_workspace,
                    args=(0,),
                    use_container_width=True,
                )

    with goal_col:
        with st.container(border=True):
            st.markdown('<div class="v2-panel-kicker">TODAY\'S FOCUS</div>', unsafe_allow_html=True)
            st.markdown("### Daily practice goal")
            st.markdown(
                f'<div class="v2-goal-count">{today_count:,}<span> / {goal:,} questions</span></div>',
                unsafe_allow_html=True,
            )
            st.progress(min(1.0, today_count / max(goal, 1)))
            if today_count >= goal:
                st.success("Daily goal reached. Nice consistency.")
            elif today_count == 0:
                st.caption("One short session is enough to get today's streak started.")
            else:
                st.caption(f"{max(0, goal - today_count):,} more questions to meet today's goal.")
            st.button(
                "Adjust daily goal",
                key="v2_adjust_goal",
                use_container_width=True,
                on_click=_go_to_workspace,
                args=(0,),
            )

    st.markdown("## Skill snapshot")
    with st.container(border=True):
        if topic_rows:
            left, right = st.columns(2, gap="large")
            with left:
                st.markdown("**Needs more practice**")
                if weakest:
                    for row in weakest[:3]:
                        st.progress(
                            row["accuracy"] / 100,
                            text=f"{row['topic']} · {row['accuracy']}% · {row['attempted']} questions",
                        )
                else:
                    st.caption("Complete at least 3 questions in a topic to reveal a useful trend.")
            with right:
                st.markdown("**Current strengths**")
                if strongest:
                    for row in strongest[:3]:
                        st.progress(
                            row["accuracy"] / 100,
                            text=f"{row['topic']} · {row['accuracy']}% · {row['attempted']} questions",
                        )
                else:
                    st.caption("Your stronger topics will appear here after a few practice rounds.")
        else:
            st.markdown("### Your skill map starts with your first quiz.")
            st.write(
                "Topic-level patterns appear here after practice. We won't fill this space with "
                "sample scores or guessed readiness estimates."
            )

    st.markdown("## Pick your next move")
    st.caption("Four quick routes into the existing features. No duplicate workflows.")
    action_cols = st.columns(2, gap="medium")
    _render_action_card(
        action_cols[0],
        number="01",
        title="Quiz Studio",
        descriptor="Build a quiz from a topic, study notes, or a weak area. Keep practice untimed or start a timed mock.",
        button_label="Open Quiz Studio",
        target_index=0,
        action_key="quiz",
    )
    _render_action_card(
        action_cols[1],
        number="02",
        title="Mock Interview",
        descriptor="Work through interview questions, save your answers, get an evaluation and review the result.",
        button_label="Start an interview",
        target_index=2,
        action_key="interview",
    )
    action_cols = st.columns(2, gap="medium")
    _render_action_card(
        action_cols[0],
        number="03",
        title="Analytics",
        descriptor="Review available performance and activity signals without changing your saved history.",
        button_label="View analytics",
        target_index=4,
        action_key="analytics",
    )
    _render_action_card(
        action_cols[1],
        number="04",
        title="Reports & Reviews",
        descriptor="Return to interview reports and saved evaluations from the existing interview workspace.",
        button_label="Open reports",
        target_index=2,
        action_key="reports",
    )

    st.markdown("## Recent practice")
    if attempts:
        with st.container(border=True):
            for row in attempts[:4]:
                stamp = str(row.get("completed_at") or row.get("created_at") or "")
                stamp = stamp.replace("T", " ")[:16]
                mode = "Timed mock" if row.get("mode") == "mock" else "Practice quiz"
                item_cols = st.columns([2.2, 1.1, 0.8], gap="small")
                item_cols[0].markdown(f"**{escape(str(row.get('subject') or 'Practice session'))}**")
                item_cols[0].caption(f"{escape(stamp)} · {mode}")
                item_cols[1].markdown(f"**{int(row.get('score') or 0)}%**")
                item_cols[1].caption(f"{int(row.get('correct') or 0)}/{int(row.get('total') or 0)} correct")
                item_cols[2].markdown(
                    '<span class="v2-history-label">COMPLETED</span>',
                    unsafe_allow_html=True,
                )
                st.divider()
            st.button(
                "View full practice history",
                key="v2_full_history",
                on_click=_go_to_workspace,
                args=(0,),
                use_container_width=True,
            )
    else:
        with st.container(border=True):
            st.markdown('<div class="v2-empty-icon">✳</div>', unsafe_allow_html=True)
            st.markdown("### No sessions yet — a clean slate.")
            st.write("Your completed quizzes and timed mocks will appear here automatically.")
            st.button(
                "Create a quiz",
                key="v2_empty_history_quiz",
                type="primary",
                on_click=_go_to_workspace,
                args=(0,),
            )
