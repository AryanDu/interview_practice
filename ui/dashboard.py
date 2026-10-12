"""Read-only V2 command-center dashboard.

This module only reads the existing per-user quiz history and routes users to
existing workspaces. It does not write to the database or change scoring.
"""
from __future__ import annotations

from html import escape

import streamlit as st

from ui.quiz_tracker import _daily_stats, _get_daily_goal, _load_history, _now


_DASHBOARD_CSS = """
<style>
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: #FFFFFF;
  border: 1px solid var(--v2-line, #E3E7F0) !important;
  border-radius: 17px !important;
  box-shadow: 0 5px 20px rgba(27, 35, 64, 0.035);
}

.v2-dashboard-hero {
  isolation: isolate;
  position: relative;
  overflow: hidden;
  padding: clamp(1.25rem, 3.2vw, 2.2rem);
  margin: 0 0 1.25rem;
  border: 1px solid #E9E5D5;
  border-radius: 22px;
  background: linear-gradient(112deg, #FFFFFF 0%, #FFFFFF 68%, #FFF5BE 100%);
}

.v2-hero-kicker {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  border: 1px solid #EFE1A5;
  border-radius: 7px;
  padding: 0.4rem 0.6rem;
  background: var(--v2-butter, #FFF0A6);
  color: var(--v2-cobalt-deep, #233FAF);
  font-size: 0.66rem;
  line-height: 1.15;
  font-weight: 850;
  letter-spacing: 0.105em;
}

.v2-dashboard-hero h1 {
  position: relative;
  z-index: 1;
  max-width: 17ch;
  margin: 0.9rem 0 0.55rem;
  color: var(--v2-ink, #1B2340);
  font-size: clamp(2.05rem, 4.5vw, 3.3rem);
  line-height: 1.02;
  font-weight: 850;
  letter-spacing: -0.06em;
}

.v2-dashboard-hero p {
  position: relative;
  z-index: 1;
  max-width: 54ch;
  margin: 0;
  color: var(--v2-muted, #68718A);
  font-size: 1rem;
  line-height: 1.6;
}

.v2-hero-foot {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 1.35rem;
  color: var(--v2-muted, #68718A);
  font-size: 0.66rem;
  font-weight: 850;
  letter-spacing: 0.08em;
}

.v2-hero-foot span {
  display: inline-block;
  width: 24px;
  height: 3px;
  border-radius: 4px;
  background: var(--v2-cobalt, #3556D8);
}

.v2-hero-orbit {
  position: absolute;
  z-index: 0;
  top: 15%;
  right: 6%;
  width: 130px;
  aspect-ratio: 1;
  border: 1px solid rgba(53, 86, 216, 0.18);
  border-radius: 50%;
}

.v2-hero-orbit::before {
  position: absolute;
  content: "";
  inset: 18px -18px;
  border: 1px solid rgba(53, 86, 216, 0.20);
  border-radius: 50%;
  transform: rotate(42deg);
}

.v2-hero-orbit::after {
  position: absolute;
  content: "";
  top: 11px;
  right: 10px;
  width: 14px;
  height: 14px;
  border: 2px solid var(--v2-cobalt, #3556D8);
  border-radius: 50%;
  background: var(--v2-butter, #FFF0A6);
}

.v2-panel-kicker {
  color: var(--v2-muted, #68718A);
  font-size: 0.67rem;
  font-weight: 850;
  letter-spacing: 0.11em;
  margin-bottom: 0.2rem;
}

.v2-goal-count {
  margin: 0.25rem 0 0.65rem;
  color: var(--v2-cobalt, #3556D8);
  font-size: 2.1rem;
  line-height: 1.2;
  font-weight: 850;
  letter-spacing: -0.06em;
}

.v2-goal-count span {
  display: block;
  margin-top: 0.2rem;
  color: var(--v2-muted, #68718A);
  font-size: 0.82rem;
  font-weight: 650;
  letter-spacing: 0;
}

.v2-action-heading {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.2rem;
}

.v2-action-number {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 36px;
  width: 36px;
  height: 36px;
  border-radius: 11px;
  background: var(--v2-butter, #FFF0A6);
  color: var(--v2-cobalt-deep, #233FAF);
  font-size: 0.7rem;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.v2-action-title {
  color: var(--v2-ink, #1B2340);
  font-size: 1.1rem;
  font-weight: 850;
  letter-spacing: -0.035em;
}

.v2-history-label {
  display: inline-block;
  padding: 0.35rem 0.45rem;
  border-radius: 6px;
  background: #EDF0FF;
  color: var(--v2-cobalt-deep, #233FAF);
  font-size: 0.6rem;
  font-weight: 850;
  letter-spacing: 0.07em;
}

.v2-empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 13px;
  background: var(--v2-butter, #FFF0A6);
  color: var(--v2-cobalt, #3556D8);
  font-size: 1.5rem;
}

@media (max-width: 760px) {
  .v2-dashboard-hero {
    padding: 1.2rem;
    border-radius: 18px;
  }

  .v2-dashboard-hero h1 {
    max-width: 15ch;
    font-size: clamp(1.95rem, 7vw, 2.55rem);
  }

  .v2-dashboard-hero p { font-size: 0.93rem; }
  .v2-hero-orbit { display: none; }
  .v2-hero-foot { font-size: 0.58rem; letter-spacing: 0.045em; }
}

@media (prefers-reduced-motion: reduce) {
  .v2-dashboard-hero *,
  .v2-dashboard-hero::before,
  .v2-dashboard-hero::after {
    animation: none !important;
    transition: none !important;
  }
}
</style>
"""


def _go_to_workspace(index: int) -> None:
    """Use the app's existing workspace switcher to open a feature."""
    st.session_state.active_tab = index
    labels = {
        -4: "⚙️ Settings", -3: "📄 Reports & History", -2: "🧪 Practice Hub",
        -1: "🏠 Command Center", 0: "🧠 Quiz Studio & Progress",
        1: "📚 Interview Prep", 2: "🎤 Mock Interview", 3: "💬 Chat Assistant",
        4: "📊 Analytics", 5: "🎨 Visual Tools", 6: "🔒 Security Testing",
    }
    if index in labels:
        st.session_state.v2_workspace_picker = labels[index]
    st.session_state.pop("quiz_tracker_focus", None)


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
    st.markdown(_DASHBOARD_CSS, unsafe_allow_html=True)

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

    # Two rows keep metric cards readable on smaller laptop and phone widths.
    metric_cols = st.columns(2, gap="medium")
    metric_cols[0].metric("Questions answered", f"{total_questions:,}")
    metric_cols[1].metric(
        "Overall accuracy",
        f"{overall_accuracy}%" if overall_accuracy is not None else "—",
        f"{total_correct:,} correct" if total_questions else "Start with your first quiz",
    )
    metric_cols = st.columns(2, gap="medium")
    metric_cols[0].metric("Practice sessions", f"{len(attempts):,}")
    metric_cols[1].metric(
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
        target_index=-3,
        action_key="reports",
    )

    st.markdown("## Recent practice")
    if attempts:
        for row in attempts[:4]:
            stamp = str(row.get("completed_at") or row.get("created_at") or "")
            stamp = stamp.replace("T", " ")[:16]
            mode = "Timed mock" if row.get("mode") == "mock" else "Practice quiz"
            with st.container(border=True):
                item_cols = st.columns([1.5, 1], gap="small")
                item_cols[0].markdown(f"**{escape(str(row.get('subject') or 'Practice session'))}**")
                item_cols[0].caption(f"{escape(stamp)} · {mode}")
                item_cols[1].markdown(f"**{int(row.get('score') or 0)}%**")
                item_cols[1].caption(f"{int(row.get('correct') or 0)}/{int(row.get('total') or 0)} correct")
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
