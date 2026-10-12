"""User-isolated mock-interview report storage and PDF generation.

PDF creation and history access reuse the completed evaluation payload; neither calls an LLM.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
from html import escape
from io import BytesIO
import json
import os
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("MOCK_INTERVIEW_REPORTS_DB_PATH", str(ROOT / "data" / "mock_interview_reports.sqlite3")))
MAX_HISTORY_ITEMS = 30
_POOL = None
_POOL_URL = ""
_POOL_LOCK = threading.Lock()
_SCHEMA_LOCK = threading.Lock()


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get("DATABASE_URL", "")).strip()
    except Exception:
        return ""


def _pool_for(database_url: str):
    global _POOL, _POOL_URL
    with _POOL_LOCK:
        if _POOL is None or _POOL_URL != database_url:
            if _POOL is not None:
                try:
                    _POOL.close()
                except Exception:
                    pass
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
            _POOL = ConnectionPool(
                conninfo=database_url, min_size=1, max_size=5, timeout=10,
                kwargs={"row_factory": dict_row}, open=True,
            )
            _POOL_URL = database_url
        return _POOL


def _ensure_schema(conn, postgres: bool) -> None:
    if postgres:
        conn.execute("""CREATE TABLE IF NOT EXISTS mock_interview_reports (
            id BIGSERIAL PRIMARY KEY, user_id TEXT NOT NULL, report_token TEXT NOT NULL,
            created_at TEXT NOT NULL, domain TEXT NOT NULL, difficulty TEXT NOT NULL,
            score INTEGER NOT NULL CHECK(score >= 0 AND score <= 100),
            payload_json TEXT NOT NULL, UNIQUE(user_id, report_token))""")
    else:
        conn.execute("""CREATE TABLE IF NOT EXISTS mock_interview_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, report_token TEXT NOT NULL,
            created_at TEXT NOT NULL, domain TEXT NOT NULL, difficulty TEXT NOT NULL,
            score INTEGER NOT NULL CHECK(score >= 0 AND score <= 100),
            payload_json TEXT NOT NULL, UNIQUE(user_id, report_token))""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mock_reports_user_date ON mock_interview_reports(user_id, created_at DESC)")


@contextmanager
def _connection() -> Iterator[tuple[Any, bool]]:
    database_url = _database_url()
    if database_url:
        pool = _pool_for(database_url)
        with pool.connection(timeout=10) as conn:
            with _SCHEMA_LOCK:
                _ensure_schema(conn, True)
            yield conn, True
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        _ensure_schema(conn, False)
        yield conn, False
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _clip(value: Any, limit: int) -> str:
    return str(value if value is not None else "").replace("\x00", "").strip()[:limit]


def _indexed(values: Any, index: int, limit: int = 5000) -> str:
    if isinstance(values, dict):
        return _clip(values.get(index, values.get(str(index), "")), limit)
    if isinstance(values, (list, tuple)) and index < len(values):
        return _clip(values[index], limit)
    return ""


def build_report_payload(*, domain: str, difficulty: str, questions: list[str], answers: Any,
                         score: Any, skills: Any, ideal_answers: Any, question_type: str = "mixed") -> dict[str, Any]:
    """Normalize the existing evaluation into a bounded, serializable report."""
    try:
        numeric_score = int(float(score))
    except (TypeError, ValueError, OverflowError):
        numeric_score = 0
    numeric_score = min(100, max(0, numeric_score))
    clean_questions = [_clip(q, 2000) for q in (questions or [])[:10]]
    clean_answers = [_indexed(answers, i) for i in range(len(clean_questions))]
    clean_ideal = [_indexed(ideal_answers, i) for i in range(len(clean_questions))]
    if isinstance(skills, str):
        skills = skills.split(",")
    if not isinstance(skills, (list, tuple)):
        skills = []
    clean_skills, seen = [], set()
    for skill in skills:
        value = _clip(skill, 80)
        if value and value.casefold() not in seen:
            clean_skills.append(value)
            seen.add(value.casefold())
        if len(clean_skills) >= 15:
            break
    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "domain": _clip(domain, 100) or "General",
        "difficulty": _clip(difficulty, 30) or "Not specified",
        "question_type": _clip(question_type, 30) or "mixed",
        "score": numeric_score,
        "skills": clean_skills,
        "questions": clean_questions,
        "answers": clean_answers,
        "ideal_answers": clean_ideal,
    }


def save_report(user_id: str, report_token: str, payload: dict[str, Any]) -> int:
    """Save once per user/interview token; repeat submissions update that same row."""
    user_id, report_token = _clip(user_id, 128), _clip(report_token, 128)
    if not user_id or not report_token:
        raise ValueError("A user identifier and report token are required.")
    created_at = _clip(payload.get("created_at"), 50) or datetime.now(timezone.utc).isoformat(timespec="seconds")
    domain = _clip(payload.get("domain"), 100) or "General"
    difficulty = _clip(payload.get("difficulty"), 30) or "Not specified"
    score = min(100, max(0, int(payload.get("score", 0))))
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    with _connection() as (conn, postgres):
        ph = "%s" if postgres else "?"
        conn.execute(
            f"""INSERT INTO mock_interview_reports
            (user_id, report_token, created_at, domain, difficulty, score, payload_json)
            VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            ON CONFLICT(user_id, report_token) DO UPDATE SET
            created_at=excluded.created_at, domain=excluded.domain, difficulty=excluded.difficulty,
            score=excluded.score, payload_json=excluded.payload_json""",
            (user_id, report_token, created_at, domain, difficulty, score, serialized),
        )
        row = conn.execute(
            f"SELECT id FROM mock_interview_reports WHERE user_id={ph} AND report_token={ph}",
            (user_id, report_token),
        ).fetchone()
        if row is None:
            raise RuntimeError("The report could not be saved.")
        return int(row["id"] if isinstance(row, dict) else row[0])


def list_reports(user_id: str, limit: int = 20) -> list[dict[str, Any]]:
    user_id, limit = _clip(user_id, 128), min(MAX_HISTORY_ITEMS, max(1, int(limit)))
    with _connection() as (conn, postgres):
        ph = "%s" if postgres else "?"
        rows = conn.execute(
            f"""SELECT id, created_at, domain, difficulty, score FROM mock_interview_reports
            WHERE user_id={ph} ORDER BY created_at DESC, id DESC LIMIT {ph}""",
            (user_id, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_report(user_id: str, report_id: int) -> dict[str, Any] | None:
    user_id = _clip(user_id, 128)
    try:
        report_id = int(report_id)
    except (TypeError, ValueError):
        return None
    with _connection() as (conn, postgres):
        ph = "%s" if postgres else "?"
        row = conn.execute(
            f"""SELECT id, created_at, domain, difficulty, score, payload_json
            FROM mock_interview_reports WHERE user_id={ph} AND id={ph}""",
            (user_id, report_id),
        ).fetchone()
    if row is None:
        return None
    record = dict(row)
    try:
        payload = json.loads(record["payload_json"])
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    payload.update({"report_id": int(record["id"]), "created_at": record["created_at"],
                    "domain": record["domain"], "difficulty": record["difficulty"], "score": int(record["score"])})
    return payload


def _paragraph(value: Any, style):
    from reportlab.platypus import Paragraph
    return Paragraph(escape(_clip(value, 12000)).replace("\n", "<br/>"), style)


def build_pdf(report: dict[str, Any]) -> bytes:
    """Render an accessible, visual PDF using local data only (no model/API calls)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm,
                            topMargin=17*mm, bottomMargin=17*mm, title="Mock Interview Report",
                            author="Interview Practice App")
    width = A4[0] - 32*mm
    navy, blue = colors.HexColor("#132238"), colors.HexColor("#2457A7")
    pale, gray, muted = colors.HexColor("#EEF4FF"), colors.HexColor("#F3F5F8"), colors.HexColor("#5D6878")
    styles = getSampleStyleSheet()
    title = ParagraphStyle("MockTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                           fontSize=21, leading=25, textColor=navy, alignment=0, spaceAfter=3*mm)
    subtitle = ParagraphStyle("MockSubtitle", parent=styles["Normal"], fontSize=9, leading=13,
                              textColor=muted, spaceAfter=3*mm)
    section = ParagraphStyle("MockSection", parent=styles["Heading2"], fontName="Helvetica-Bold",
                             fontSize=13, leading=16, textColor=navy, spaceBefore=4*mm, spaceAfter=2*mm)
    question_style = ParagraphStyle("MockQuestion", parent=styles["Heading3"], fontName="Helvetica-Bold",
                                    fontSize=10, leading=14, textColor=blue, spaceBefore=3*mm, spaceAfter=2*mm)
    label = ParagraphStyle("MockLabel", parent=styles["Normal"], fontName="Helvetica-Bold",
                           fontSize=8, leading=11, textColor=muted, spaceBefore=1*mm, spaceAfter=1*mm)
    body = ParagraphStyle("MockBody", parent=styles["BodyText"], fontSize=9, leading=13,
                          textColor=navy, spaceAfter=2*mm)
    score_style = ParagraphStyle("MockScore", parent=styles["Title"], fontName="Helvetica-Bold",
                                 fontSize=26, leading=30, textColor=colors.white, alignment=1)
    score_label = ParagraphStyle("MockScoreLabel", parent=styles["Normal"], fontName="Helvetica-Bold",
                                 fontSize=9, leading=12, textColor=colors.white, alignment=1)
    domain = _clip(report.get("domain"), 100) or "General"
    difficulty = _clip(report.get("difficulty"), 30) or "Not specified"
    qtype = _clip(report.get("question_type"), 30).title() or "Mixed"
    date_text = _clip(report.get("created_at"), 50) or "Date unavailable"
    try:
        score = min(100, max(0, int(report.get("score", 0))))
    except (TypeError, ValueError):
        score = 0

    story = [
        Paragraph("MOCK INTERVIEW REPORT", title),
        Paragraph("Personal performance summary · generated from your completed evaluation", subtitle),
        HRFlowable(width="100%", thickness=1.2, color=blue, spaceAfter=4*mm),
    ]
    metadata = Table([
        [_paragraph("DOMAIN", label), _paragraph("DIFFICULTY", label), _paragraph("TYPE", label)],
        [_paragraph(domain, body), _paragraph(difficulty, body), _paragraph(qtype, body)],
    ], colWidths=[width*.45, width*.27, width*.28])
    metadata.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), gray), ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#DDE3EA")),
        ("INNERGRID", (0,0), (-1,-1), .4, colors.HexColor("#DDE3EA")),
        ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [metadata, Spacer(1, 4*mm)]
    score_panel = Table(
        [[Paragraph("OVERALL SCORE", score_label), Paragraph(f"{score}<font size='14'> / 100</font>", score_style)]],
        colWidths=[width*.55, width*.45], rowHeights=[22*mm])
    score_panel.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), navy), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"), ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story += [score_panel, Spacer(1, 2*mm), _paragraph(f"Report date: {date_text}", subtitle)]
    story.append(Paragraph("Skills identified", section))
    skills = report.get("skills", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    if not isinstance(skills, (list, tuple)):
        skills = []
    if skills:
        box = Table([[_paragraph("  •  ".join(_clip(s, 80) for s in skills[:15]), body)]], colWidths=[width])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), pale), ("BOX", (0,0), (-1,-1), .5, colors.HexColor("#C8D9F8")),
            ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(box)
    else:
        story.append(_paragraph("No skills were returned by the evaluation.", body))
    questions, answers, ideal = report.get("questions", []), report.get("answers", []), report.get("ideal_answers", [])
    if not isinstance(questions, list): questions = []
    if not isinstance(answers, list): answers = []
    if not isinstance(ideal, list): ideal = []
    story += [Paragraph("Question-wise review", section),
              _paragraph("Compare your submitted response with the model answer from the completed evaluation.", subtitle)]
    if not questions:
        story.append(_paragraph("No question details were stored for this report.", body))
    for i, question in enumerate(questions[:10]):
        story.append(_paragraph(f"Q{i+1}. {_clip(question, 2000)}", question_style))
        answer = answers[i] if i < len(answers) else ""
        ideal_answer = ideal[i] if i < len(ideal) else ""
        story += [
            _paragraph("YOUR ANSWER", label),
            _paragraph(answer or "No answer provided.", body),
            _paragraph("IDEAL ANSWER", label),
            _paragraph(ideal_answer or "No ideal answer was generated for this question.", body),
            Spacer(1, 2*mm),
            HRFlowable(width="100%", thickness=.4, color=colors.HexColor("#DDE3EA"),
                       spaceBefore=1*mm, spaceAfter=1*mm),
        ]
    story += [Spacer(1, 3*mm),
              _paragraph("This report is AI-generated for practice and is not a guarantee of interview performance.", subtitle)]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#DDE3EA"))
        canvas.line(16*mm, 12*mm, A4[0]-16*mm, 12*mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(muted)
        canvas.drawString(16*mm, 7.5*mm, "Interview Practice · Personal report")
        canvas.drawRightString(A4[0]-16*mm, 7.5*mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


def render_reports_panel(user_id: str) -> None:
    """Show the current report and user-scoped report history in Streamlit."""
    import streamlit as st
    st.divider()
    st.subheader("📄 Mock Interview Report Cards")
    current_id = st.session_state.get("mock_interview_report_id")
    current = st.session_state.get("mock_interview_report_payload")
    if current_id:
        try:
            current = get_report(user_id, current_id) or current
        except Exception:
            pass
    if current:
        st.success("Your report is ready. Preview and download reuse the saved evaluation; no AI call is made.")
        cols = st.columns(3)
        cols[0].metric("Overall score", f"{int(current.get('score', 0))}/100")
        cols[1].metric("Questions", len(current.get("questions", [])))
        cols[2].metric("Skills", len(current.get("skills", [])))
        identifier = str(current.get("report_id") or current_id or "current")
        try:
            st.download_button("⬇️ Download PDF Report", data=build_pdf(current),
                               file_name=f"mock-interview-report-{identifier}.pdf", mime="application/pdf",
                               key=f"download_current_mock_report_{identifier}", use_container_width=True)
        except Exception:
            st.error("PDF creation failed. The evaluation data remains available; try again.")
    else:
        st.info("Complete a Mock Interview to generate your first downloadable PDF report.")

    try:
        history = list_reports(user_id, limit=20)
    except Exception:
        st.warning("Report history is temporarily unavailable. The current result may still be downloadable.")
        return
    if not history:
        st.caption("Completed reports will appear here for future download.")
        return
    st.markdown("**Previous reports**")
    for record in history:
        record_id = int(record["id"])
        with st.container(border=True):
            col1, col2 = st.columns([.75, .25])
            with col1:
                st.markdown(f"**{_clip(record.get('domain'), 100)}** · {_clip(record.get('difficulty'), 30)}")
                st.caption(f"{_clip(record.get('created_at'), 50)} · Score: {int(record.get('score', 0))}/100")
            with col2:
                if st.button("View / download", key=f"view_mock_report_{record_id}", use_container_width=True):
                    st.session_state.mock_interview_history_selected_id = record_id
        selected_id = st.session_state.get("mock_interview_history_selected_id")
        if selected_id and int(selected_id) == record_id:
            selected = get_report(user_id, record_id)
            if selected:
                try:
                    st.download_button(f"⬇️ Download report #{record_id}", data=build_pdf(selected),
                                       file_name=f"mock-interview-report-{record_id}.pdf", mime="application/pdf",
                                       key=f"download_history_mock_report_{record_id}")
                except Exception:
                    st.warning("This saved report could not be rendered as a PDF.")
