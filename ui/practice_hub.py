"""Unified V2 practice hub built on top of the existing feature screens."""
from __future__ import annotations

import streamlit as st


_HUB_CSS = """
<style>
.v2-hub-intro {
  padding: 1.45rem 1.5rem;
  margin-bottom: 1.15rem;
  border-radius: 19px;
  background: linear-gradient(110deg, #FFFFFF 0%, #FFFFFF 67%, #FFF4B8 100%);
  border: 1px solid #E9E5D5;
}
.v2-hub-kicker {
  color: #3556D8;
  font-size: .68rem;
  font-weight: 850;
  letter-spacing: .12em;
}
.v2-hub-intro h1 {
  margin: .55rem 0 .35rem;
  color: #1B2340;
  font-size: clamp(1.8rem, 3.4vw, 2.6rem);
  letter-spacing: -.055em;
}
.v2-hub-intro p { max-width: 58ch; margin: 0; line-height: 1.55; color: #68718A; }
.v2-hub-card { margin-bottom: .3rem; }
.v2-hub-card-head { display:flex; align-items:center; gap:.7rem; margin-bottom:.3rem; }
.v2-hub-index { display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:11px; background:#FFF0A6; color:#233FAF; font-size:.72rem; font-weight:900; }
.v2-hub-card-title { font-size:1.1rem; color:#1B2340; font-weight:850; letter-spacing:-.035em; }
.v2-hub-tag { display:inline-block; margin-top:.4rem; color:#3556D8; background:#EDF0FF; border-radius:6px; padding:.28rem .43rem; font-size:.62rem; font-weight:850; letter-spacing:.07em; }
</style>
"""


def _open_workspace(index: int, focus: str = "") -> None:
    st.session_state.active_tab = index
    if focus:
        st.session_state.quiz_tracker_focus = focus
    else:
        st.session_state.pop("quiz_tracker_focus", None)


def _card(column, number: str, title: str, body: str, tag: str, button: str, target: int, focus: str = "") -> None:
    with column:
        with st.container(border=True):
            st.markdown(
                f'<div class="v2-hub-card-head"><span class="v2-hub-index">{number}</span>'
                f'<span class="v2-hub-card-title">{title}</span></div>',
                unsafe_allow_html=True,
            )
            st.write(body)
            st.markdown(f'<span class="v2-hub-tag">{tag}</span>', unsafe_allow_html=True)
            st.button(
                button,
                key=f"v2_hub_{number}",
                type="primary" if number in {"01", "02"} else "secondary",
                use_container_width=True,
                on_click=_open_workspace,
                args=(target, focus),
            )


def render_practice_hub() -> None:
    """Provide four clear routes without recreating the existing practice engines."""
    st.markdown(_HUB_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <section class="v2-hub-intro">
          <div class="v2-hub-kicker">CHOOSE YOUR SESSION</div>
          <h1>Practice, your way.</h1>
          <p>Pick a focused session. Your existing quizzes, uploaded study notes, timed tests,
          interview evaluations and saved history all use the same trusted workflows.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    first = st.columns(2, gap="medium")
    _card(
        first[0], "01", "Quiz Studio",
        "Generate multiple-choice questions from a topic or pasted notes. Review explanations and track accuracy.",
        "BUILD KNOWLEDGE", "Create a quiz", 0, "quiz",
    )
    _card(
        first[1], "02", "Mock Interview",
        "Practise technical, behavioral or mixed interviews, save answers and review evaluation reports.",
        "REHEARSE OUT LOUD", "Start mock interview", 2,
    )
    second = st.columns(2, gap="medium")
    _card(
        second[0], "03", "PDF & Notes Practice",
        "Use a PDF, TXT, Markdown file, syllabus or job description as the source for a tailored quiz.",
        "LEARN FROM YOUR MATERIAL", "Practise from notes", 0, "pdf",
    )
    _card(
        second[1], "04", "Weak Topics",
        "Revisit topics where your saved answers show room for improvement. No sample or invented scores.",
        "TARGETED REVISION", "Review weak topics", 0, "weak",
    )

    st.caption("Tip: each card opens the original feature screen, so there is only one quiz engine and one source of truth.")
