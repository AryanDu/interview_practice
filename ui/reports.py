"""Dedicated V2 reports and practice-history workspace."""
from __future__ import annotations

import streamlit as st

from ui.mock_interview_reports import render_reports_panel


_REPORTS_CSS = """
<style>
.v2-reports-intro { padding:1.3rem 1.45rem; margin-bottom:1rem; border:1px solid #E9E5D5; border-radius:18px; background:linear-gradient(110deg,#FFFFFF 0%,#FFFFFF 72%,#FFF4B8 100%); }
.v2-reports-kicker { color:#3556D8; font-size:.67rem; font-weight:850; letter-spacing:.12em; }
.v2-reports-intro h1 { margin:.5rem 0 .35rem; color:#1B2340; letter-spacing:-.05em; }
.v2-reports-intro p { margin:0; color:#68718A; line-height:1.55; }
</style>
"""


def render_reports(user_id: str) -> None:
    """Show existing saved evaluation PDFs in one reports-focused workspace."""
    st.markdown(_REPORTS_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <section class="v2-reports-intro">
          <div class="v2-reports-kicker">YOUR WORK, KEPT</div>
          <h1>Reports & practice history</h1>
          <p>Open completed evaluations and download PDFs generated from your saved interview results.
          Existing report storage and PDF generation remain unchanged.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_reports_panel(user_id)
