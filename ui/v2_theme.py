"""Visual design tokens and presentation-only styling for the V2 interface.

Keep this module free of application logic. The existing quiz, interview, report,
authentication, and database functions remain the source of truth.
"""
from __future__ import annotations

import streamlit as st


_V2_CSS = """
<style>
:root {
  --v2-cobalt: #3556D8;
  --v2-cobalt-deep: #233FAF;
  --v2-butter: #FFF0A6;
  --v2-chalk: #F6F7F2;
  --v2-paper: #FFFFFF;
  --v2-ink: #1B2340;
  --v2-muted: #68718A;
  --v2-line: #E3E7F0;
  --v2-sidebar: #17213A;
  --v2-sidebar-soft: #222E4B;
  --v2-radius: 16px;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--v2-chalk) !important;
  color: var(--v2-ink);
}

[data-testid="stMainBlockContainer"] {
  max-width: 1480px;
  padding-top: 1.25rem;
  padding-bottom: 3rem;
  padding-left: clamp(1rem, 3vw, 2.75rem);
  padding-right: clamp(1rem, 3vw, 2.75rem);
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  background: var(--v2-sidebar) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: #F1F3FC !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="textarea"] {
  color: #F7F8FF !important;
  background: var(--v2-sidebar-soft) !important;
  border-color: rgba(255, 255, 255, 0.14) !important;
  border-radius: 11px !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
  border-color: var(--v2-butter) !important;
}

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {
  color: var(--v2-ink);
  letter-spacing: -0.035em;
  font-weight: 750;
}

[data-testid="stMain"] h1 { font-size: clamp(1.9rem, 3.4vw, 2.7rem); }
[data-testid="stMain"] h2 { font-size: clamp(1.35rem, 2.4vw, 1.8rem); }
[data-testid="stMain"] h3 { font-size: 1.12rem; }

[data-testid="stMain"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stCaptionContainer"] {
  color: var(--v2-muted);
}

[data-testid="stMetric"] {
  background: var(--v2-paper);
  border: 1px solid var(--v2-line);
  border-radius: var(--v2-radius);
  padding: 1rem 1.1rem;
  box-shadow: 0 4px 18px rgba(27, 35, 64, 0.035);
}

[data-testid="stMetricLabel"] { color: var(--v2-muted) !important; }
[data-testid="stMetricValue"] { color: var(--v2-ink) !important; font-weight: 750; }
[data-testid="stMetricDelta"] { font-weight: 650; }

[data-testid="stExpander"] {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid var(--v2-line);
  border-radius: 14px;
  overflow: hidden;
}

[data-testid="stForm"] {
  background: var(--v2-paper);
  border: 1px solid var(--v2-line);
  border-radius: 18px;
  padding: 1.15rem 1.2rem 0.8rem;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-baseweb="select"] > div {
  border-color: #DCE2EE;
  border-radius: 11px;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: var(--v2-cobalt) !important;
  box-shadow: 0 0 0 1px var(--v2-cobalt) !important;
}

.stButton > button,
[data-testid="stDownloadButton"] > button {
  border-radius: 11px;
  min-height: 2.65rem;
  font-weight: 650;
  border: 1px solid #DCE2EE;
  transition: background-color 140ms ease, border-color 140ms ease, transform 140ms ease;
}

.stButton > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {
  background: var(--v2-cobalt) !important;
  color: #FFFFFF !important;
  border-color: var(--v2-cobalt) !important;
}

.stButton > button[kind="primary"]:hover {
  background: var(--v2-butter) !important;
  color: var(--v2-cobalt-deep) !important;
  border-color: var(--v2-butter) !important;
  transform: translateY(-1px);
}

.stButton > button:not([kind="primary"]):hover,
[data-testid="stDownloadButton"] > button:hover {
  border-color: var(--v2-cobalt) !important;
  color: var(--v2-cobalt-deep) !important;
  background: #F0F3FF !important;
}

[data-testid="stProgressBar"] > div > div {
  background: var(--v2-cobalt) !important;
}

[data-testid="stAlert"] {
  border-radius: 13px;
}

.v2-brandbar {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.2rem 0 1.1rem;
  margin-bottom: 1.1rem;
  border-bottom: 1px solid var(--v2-line);
}

.v2-brandmark {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 4px;
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  padding: 11px 10px;
  box-sizing: border-box;
  border-radius: 14px;
  background: var(--v2-cobalt);
  box-shadow: 0 7px 16px rgba(53, 86, 216, 0.17);
}

.v2-brandmark span {
  display: block;
  width: 5px;
  border-radius: 4px 4px 2px 2px;
  background: var(--v2-butter);
}

.v2-brandmark .v2-bar-one { height: 8px; }
.v2-brandmark .v2-bar-two { height: 14px; }
.v2-brandmark .v2-bar-three { height: 21px; }

.v2-brand-name {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.v2-brand-name strong {
  color: var(--v2-ink);
  font-size: 1.08rem;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -0.035em;
}

.v2-brand-name small {
  color: var(--v2-muted);
  font-size: 0.66rem;
  line-height: 1.2;
  font-weight: 750;
  letter-spacing: 0.12em;
}

.v2-brand-note {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.7rem;
  border: 1px solid #F0E2A1;
  border-radius: 999px;
  background: #FFF8D6;
  color: var(--v2-cobalt-deep);
  font-size: 0.7rem;
  font-weight: 750;
  letter-spacing: 0.045em;
  white-space: nowrap;
}

.v2-brand-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--v2-cobalt);
}

.v2-nav-label {
  color: var(--v2-ink);
  font-size: 0.73rem;
  font-weight: 800;
  letter-spacing: 0.10em;
  text-transform: uppercase;
  margin: 0.2rem 0 0.2rem;
}

.v2-nav-hint {
  color: var(--v2-muted);
  font-size: 0.86rem;
  margin-top: 0.1rem;
}

.v2-workspace-intro {
  padding: 1.25rem 1.45rem;
  margin-bottom: 1rem;
  border: 1px solid #E9E5D5;
  border-radius: 18px;
  background: linear-gradient(110deg, #FFFFFF 0%, #FFFFFF 75%, #FFF4B8 100%);
}
.v2-page-kicker {
  color: var(--v2-cobalt);
  font-size: .67rem;
  font-weight: 850;
  letter-spacing: .12em;
}
.v2-workspace-intro h1 {
  margin: .45rem 0 .35rem;
  color: var(--v2-ink);
  letter-spacing: -.055em;
  font-size: clamp(1.9rem, 3.5vw, 2.65rem);
}
.v2-workspace-intro p {
  margin: 0;
  max-width: 65ch;
  color: var(--v2-muted);
  line-height: 1.55;
}
.v2-sidebar-nav-title {
  color: #B9C4E2;
  font-size: .66rem;
  font-weight: 850;
  letter-spacing: .12em;
  margin: .2rem 0 .55rem;
}
[data-testid="stSidebar"] .stButton > button {
  min-height: 2.35rem;
  padding: .3rem .45rem;
  background: #222E4B !important;
  color: #F1F3FC !important;
  border: 1px solid rgba(255,255,255,.2) !important;
  border-radius: 10px;
  font-size: .95rem;
  box-shadow: 0 2px 7px rgba(0,0,0,.12);
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--v2-butter) !important;
  color: var(--v2-cobalt-deep) !important;
  border-color: var(--v2-butter) !important;
  box-shadow: 0 3px 10px rgba(255,240,166,.16);
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #FFF0A6 !important;
  color: #233FAF !important;
  border-color: #FFF0A6 !important;
  transform: translateY(-1px);
}
[data-testid="stSidebar"] .stButton > button:focus-visible {
  outline: 2px solid #FFF0A6 !important;
  outline-offset: 2px;
}
[data-testid="stMain"] {
  font-family: "Avenir Next", "Nunito", "Trebuchet MS", ui-rounded, system-ui, sans-serif;
}
@media (max-width: 760px) {
  .v2-workspace-intro {
    padding: 1.05rem;
    border-radius: 16px;
  }
  .v2-workspace-intro h1 {
    font-size: clamp(1.8rem, 7vw, 2.45rem);
  }
}

.v2-top-streak {
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  min-height:2.5rem;
  padding:.25rem .45rem;
  border:1px solid #F0E2A1;
  border-radius:12px;
  background:#FFF8D6;
  color:#233FAF;
}
.v2-top-streak strong { font-size:.92rem; line-height:1.05; }
.v2-top-streak small { color:#68718A; font-size:.58rem; line-height:1.1; white-space:nowrap; }
[data-testid="stPopover"] > button {
  border-radius:11px !important;
  border:1px solid #E3E7F0 !important;
  background:#FFFFFF !important;
  color:#1B2340 !important;
}
[data-testid="stPopoverBody"] {
  border-radius:16px !important;
}
div[role="radiogroup"] label,
[data-testid="stCheckbox"] label {
  border-radius:10px;
}
@media (max-width: 760px) {
  .v2-top-streak { min-height:2.25rem; padding:.2rem .35rem; }
  [data-testid="stPopover"] > button { padding-left:.35rem!important; padding-right:.35rem!important; }
}

@media (max-width: 760px) {
  [data-testid="stMainBlockContainer"] {
    padding-top: 0.8rem;
    padding-left: 0.85rem;
    padding-right: 0.85rem;
  }

  /* Stack content columns on phones, while keeping the numbered exam navigator compact. */
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: .6rem !important;
  }
  [data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 100% !important;
    width: 100% !important;
    min-width: 0 !important;
  }
  .st-key-v2-quiz-navigator [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: .3rem !important;
  }
  .st-key-v2-quiz-navigator [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    flex: 1 1 0 !important;
    width: auto !important;
    min-width: 0 !important;
  }

  .v2-brandbar {
    gap: 0.65rem;
    padding-bottom: 0.85rem;
    margin-bottom: 0.85rem;
  }

  .v2-brandmark {
    width: 40px;
    height: 40px;
    flex-basis: 40px;
    border-radius: 12px;
  }

  .v2-brand-name strong { font-size: 0.96rem; }
  .v2-brand-name small { font-size: 0.58rem; letter-spacing: 0.08em; }
  .v2-brand-note { display: none; }

  [data-testid="stSidebar"][aria-expanded="true"] {
    min-width: min(84vw, 310px) !important;
    width: min(84vw, 310px) !important;
  }

  [data-testid="stMetric"] { padding: 0.8rem; }
  [data-testid="stForm"] { padding: 0.85rem 0.8rem 0.55rem; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>
"""


def apply_v2_theme() -> None:
    """Apply presentation-only V2 styling; does not touch session or business logic."""
    st.markdown(_V2_CSS, unsafe_allow_html=True)


def render_brand_bar() -> None:
    """Render the V2 wordmark and compact brand line."""
    st.markdown(
        """
        <div class="v2-brandbar" role="banner">
          <div class="v2-brandmark" aria-hidden="true">
            <span class="v2-bar-one"></span>
            <span class="v2-bar-two"></span>
            <span class="v2-bar-three"></span>
          </div>
          <div class="v2-brand-name">
            <strong>Interview Practice</strong>
            <small>PRACTICE WITH INTENT</small>
          </div>
          <div class="v2-brand-note"><span class="v2-brand-dot"></span>FOCUS · FEEDBACK · GROWTH</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
