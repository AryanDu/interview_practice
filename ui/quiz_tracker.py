"""AI-generated quizzes with topic-level performance tracking."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "quiz_history.sqlite3"
DEFAULT_MODEL = "gemini-2.5-flash"


def _api_key():
    """Read a Gemini key from Streamlit secrets or environment variables."""
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(name)
        if value:
            return value.strip()
    try:
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            value = st.secrets.get(name)
            if value:
                return str(value).strip()
    except Exception:
        pass
    return ""


def _db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            subject TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            correct INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            selected_index INTEGER,
            correct_index INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY(attempt_id) REFERENCES quiz_attempts(id)
        )
    """)
    conn.commit()
    return conn


def _generate_quiz(api_key, model, subject, difficulty, count, source_text):
    prompt = f"""
Create exactly {count} multiple-choice quiz questions for a student's learning.
Subject: {subject}
Difficulty: {difficulty}
Study notes / syllabus / job description:
{source_text[:18000] if source_text else "No notes supplied. Use standard, accurate knowledge for the subject."}

Return ONLY valid JSON with this exact shape:
{{
  "questions": [
    {{
      "question": "A clear question",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "topic": "Short skill/topic label",
      "explanation": "Brief explanation of why the answer is correct"
    }}
  ]
}}
Rules:
- correct_index must be an integer from 0 to 3.
- Every question must have exactly four options and one best answer.
- Cover distinct subtopics where possible.
- If notes are supplied, prioritize them and do not invent facts about the notes.
- Keep explanations concise and educational.
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        },
        timeout=45,
    )
    if not response.ok:
        detail = response.text[:500]
        raise RuntimeError(f"Gemini API returned HTTP {response.status_code}: {detail}")
    payload = response.json()
    try:
        raw = payload["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(raw)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("The AI response was not valid quiz JSON. Please try again.") from exc

    questions = data.get("questions", [])
    valid = []
    for item in questions:
        options = item.get("options", [])
        correct_index = item.get("correct_index")
        question = str(item.get("question", "")).strip()
        if (
            question
            and isinstance(options, list)
            and len(options) == 4
            and isinstance(correct_index, int)
            and 0 <= correct_index <= 3
        ):
            valid.append({
                "question": question,
                "options": [str(option) for option in options],
                "correct_index": correct_index,
                "topic": str(item.get("topic") or subject).strip()[:80],
                "explanation": str(item.get("explanation") or "").strip(),
            })
    if len(valid) < 1:
        raise RuntimeError("No valid questions were returned. Try a shorter topic or notes.")
    return valid[:count]


def _save_attempt(session_id, subject, difficulty, questions, answers):
    correct = sum(
        1 for index, question in enumerate(questions)
        if answers.get(index) == question["correct_index"]
    )
    conn = _db()
    try:
        cur = conn.execute(
            """INSERT INTO quiz_attempts
            (session_id, created_at, subject, difficulty, score, total, correct)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                subject,
                difficulty,
                round(100 * correct / len(questions)),
                len(questions),
                correct,
            ),
        )
        attempt_id = cur.lastrowid
        for index, question in enumerate(questions):
            selected = answers.get(index)
            conn.execute(
                """INSERT INTO quiz_responses
                (attempt_id, topic, question, selected_index, correct_index, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    attempt_id,
                    question["topic"],
                    question["question"],
                    selected,
                    question["correct_index"],
                    int(selected == question["correct_index"]),
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return correct


def _load_history(session_id):
    conn = _db()
    try:
        attempts = conn.execute(
            """SELECT * FROM quiz_attempts WHERE session_id = ?
            ORDER BY id DESC LIMIT 50""",
            (session_id,),
        ).fetchall()
        topics = conn.execute(
            """SELECT r.topic, COUNT(*) AS attempted,
            SUM(r.is_correct) AS correct
            FROM quiz_responses r
            JOIN quiz_attempts a ON a.id = r.attempt_id
            WHERE a.session_id = ?
            GROUP BY r.topic
            ORDER BY attempted DESC""",
            (session_id,),
        ).fetchall()
        return [dict(row) for row in attempts], [dict(row) for row in topics]
    finally:
        conn.close()


def _render_history(session_id):
    attempts, topics = _load_history(session_id)
    st.subheader("Your strengths & weak areas")
    if topics:
        cols = st.columns(min(3, len(topics)))
        ranked = sorted(topics, key=lambda row: (row["correct"] or 0) / row["attempted"])
        weak = ranked[: min(3, len(ranked))]
        strong = list(reversed(ranked))[: min(3, len(ranked))]
        with cols[0]:
            st.markdown("**Needs practice**")
            for row in weak:
                pct = round(100 * (row["correct"] or 0) / row["attempted"])
                st.write(f"🔴 {row['topic']} — {pct}%")
        if len(cols) > 1:
            with cols[1]:
                st.markdown("**Strong topics**")
                for row in strong:
                    pct = round(100 * (row["correct"] or 0) / row["attempted"])
                    st.write(f"🟢 {row['topic']} — {pct}%")
        if len(cols) > 2:
            with cols[2]:
                st.markdown("**Attempts**")
                st.metric("Questions answered", sum(row["attempted"] for row in topics))
                st.metric("Topics practiced", len(topics))
        st.caption("Topic percentages are based on answers recorded in this app, not a formal assessment.")
    else:
        st.info("Complete your first quiz to start seeing strengths and weak areas.")

    st.subheader("Recent quiz history")
    if attempts:
        for row in attempts:
            with st.expander(
                f"{row['created_at'][:10]} · {row['subject']} · {row['score']}% ({row['correct']}/{row['total']})"
            ):
                st.write(f"Difficulty: {row['difficulty']}")
        csv_rows = [
            "date,subject,difficulty,score,total,correct",
            *[
                f"{r['created_at']},{json.dumps(r['subject'])},{r['difficulty']},{r['score']},{r['total']},{r['correct']}"
                for r in attempts
            ],
        ]
        st.download_button(
            "Download quiz history (CSV)",
            data="\n".join(csv_rows),
            file_name="quiz_history.csv",
            mime="text/csv",
        )
    else:
        st.caption("No attempts saved yet.")


def render_quiz_tracker_tab():
    st.header("🧠 Quiz & Progress Tracker")
    st.write("Add a topic or your own notes, take an AI-generated MCQ quiz, and track which topics need more practice.")

    if "quiz_tracker_session_id" not in st.session_state:
        st.session_state.quiz_tracker_session_id = str(uuid.uuid4())
    session_id = st.session_state.quiz_tracker_session_id

    with st.expander("How to enable free AI quiz generation", expanded=not bool(_api_key())):
        st.markdown(
            "This feature uses Google's Gemini API. A paid plan is not required if your account has free-tier access, "
            "but free quotas and model availability apply. Never put your API key in a public code file."
        )
        st.markdown(
            "For Streamlit Community Cloud, add a secret named GEMINI_API_KEY in App Settings → Secrets. "
            "Locally, set GEMINI_API_KEY in your environment or .env file."
        )
        st.markdown("[Get a Gemini API key](https://aistudio.google.com/app/apikey)")

    with st.form("quiz_generation_form"):
        subject = st.text_input("Subject / topic", placeholder="e.g. Python, SQL, Machine Learning, DSA")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        count = st.slider("Number of questions", min_value=5, max_value=20, value=10, step=5)
        notes_file = st.file_uploader("Optional study notes (.txt or .md)", type=["txt", "md"])
        source_text = st.text_area(
            "Paste notes, syllabus, or job description (optional)",
            height=160,
            placeholder="Paste your study material here. Questions will focus on this content."
        )
        submitted = st.form_submit_button("Generate quiz", type="primary")

    if submitted:
        api_key = _api_key()
        if not subject.strip():
            st.error("Please enter a subject or topic.")
        elif not api_key:
            st.error("Gemini API key is not configured yet. Follow the setup instructions above, then retry.")
        else:
            if notes_file is not None:
                try:
                    source_text += "\n\n" + notes_file.getvalue().decode("utf-8", errors="replace")
                except Exception:
                    st.warning("Could not read the uploaded text file; continuing with pasted notes.")
            try:
                with st.spinner("Generating your quiz..."):
                    quiz = _generate_quiz(api_key, DEFAULT_MODEL, subject.strip(), difficulty, count, source_text)
                st.session_state.quiz_tracker_quiz = quiz
                st.session_state.quiz_tracker_subject = subject.strip()
                st.session_state.quiz_tracker_difficulty = difficulty
                st.session_state.quiz_tracker_answers = {}
                st.session_state.quiz_tracker_submitted = False
                st.success(f"Generated {len(quiz)} questions.")
            except Exception as exc:
                st.error(f"Quiz generation failed: {exc}")

    quiz = st.session_state.get("quiz_tracker_quiz")
    if quiz:
        st.divider()
        st.subheader(f"Quiz: {st.session_state.quiz_tracker_subject}")
        st.caption(f"{st.session_state.quiz_tracker_difficulty} · {len(quiz)} questions")
        if not st.session_state.get("quiz_tracker_submitted", False):
            with st.form("answer_quiz_form"):
                answers = {}
                for index, question in enumerate(quiz):
                    st.markdown(f"**Q{index + 1}. {question['question']}**")
                    answers[index] = st.radio(
                        "Choose one answer",
                        options=list(range(4)),
                        format_func=lambda choice, opts=question["options"]: f"{'ABCD'[choice]}. {opts[choice]}",
                        key=f"quiz_answer_{session_id}_{index}",
                        index=None,
                        label_visibility="collapsed",
                    )
                    st.caption(f"Topic: {question['topic']}")
                submitted_quiz = st.form_submit_button("Submit answers", type="primary")
            if submitted_quiz:
                normalized = {i: value for i, value in answers.items() if value is not None}
                correct = _save_attempt(
                    session_id,
                    st.session_state.quiz_tracker_subject,
                    st.session_state.quiz_tracker_difficulty,
                    quiz,
                    normalized,
                )
                st.session_state.quiz_tracker_answers = normalized
                st.session_state.quiz_tracker_submitted = True
                st.session_state.quiz_tracker_last_result = (correct, len(quiz))
                st.rerun()
        else:
            correct, total = st.session_state.get("quiz_tracker_last_result", (0, len(quiz)))
            st.metric("Your score", f"{round(100 * correct / total)}%", f"{correct} of {total} correct")
            for index, question in enumerate(quiz):
                selected = st.session_state.quiz_tracker_answers.get(index)
                is_correct = selected == question["correct_index"]
                st.markdown(f"**Q{index + 1}. {'✅' if is_correct else '❌'} {question['question']}**")
                if selected is None:
                    st.write("Your answer: Not answered")
                else:
                    st.write(f"Your answer: {'ABCD'[selected]}. {question['options'][selected]}")
                st.write(f"Correct answer: {'ABCD'[question['correct_index']]}. {question['options'][question['correct_index']]}")
                st.write(f"**Topic:** {question['topic']}")
                if question["explanation"]:
                    st.caption(question["explanation"])
                st.divider()
            if st.button("Generate another quiz", type="primary"):
                st.session_state.quiz_tracker_quiz = None
                st.session_state.quiz_tracker_submitted = False
                st.rerun()

    st.divider()
    _render_history(session_id)
