from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import ui.quiz_tracker as tracker


SAMPLE_QUESTIONS = [
    {
        "question": "Which index is the first array position in Python?",
        "options": ["1", "0", "-1", "2"],
        "correct_index": 1,
        "topic": "Arrays",
        "explanation": "Python sequences are zero-indexed.",
    },
    {
        "question": "Which structure maps keys to values?",
        "options": ["Stack", "Queue", "Dictionary", "Tuple"],
        "correct_index": 2,
        "topic": "Hash maps",
        "explanation": "A dictionary stores key-value pairs.",
    },
]


def _use_temporary_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(tracker, "_database_url", lambda: "")
    monkeypatch.setattr(tracker, "DB_PATH", tmp_path / "quiz_history.sqlite3")


def test_quiz_history_isolated_by_user(monkeypatch, tmp_path):
    _use_temporary_sqlite(monkeypatch, tmp_path)

    tracker._save_attempt("user-a", "Python", "Easy", SAMPLE_QUESTIONS, {0: 1})
    tracker._save_attempt("user-b", "Python", "Easy", SAMPLE_QUESTIONS, {0: 1, 1: 2})

    attempts_a, topics_a = tracker._load_history("user-a")
    attempts_b, topics_b = tracker._load_history("user-b")

    assert len(attempts_a) == 1
    assert attempts_a[0]["correct"] == 1
    assert len(attempts_b) == 1
    assert attempts_b[0]["correct"] == 2
    assert {row["topic"] for row in topics_a} == {"Arrays", "Hash maps"}
    assert {row["topic"] for row in topics_b} == {"Arrays", "Hash maps"}

    wrong_a = tracker._load_wrong_answers("user-a")
    wrong_b = tracker._load_wrong_answers("user-b")
    assert len(wrong_a) == 1
    assert len(wrong_b) == 0


def test_duplicate_submission_token_does_not_create_two_attempts(monkeypatch, tmp_path):
    _use_temporary_sqlite(monkeypatch, tmp_path)

    first = tracker._save_attempt(
        "user-a", "Python", "Easy", SAMPLE_QUESTIONS, {0: 1}, attempt_token="same-token"
    )
    second = tracker._save_attempt(
        "user-a", "Python", "Easy", SAMPLE_QUESTIONS, {0: 0}, attempt_token="same-token"
    )

    attempts, _ = tracker._load_history("user-a")
    assert first["id"] == second["id"]
    assert len(attempts) == 1


def test_daily_goal_is_scoped_to_user(monkeypatch, tmp_path):
    _use_temporary_sqlite(monkeypatch, tmp_path)
    assert tracker._get_daily_goal("user-a") == tracker.DEFAULT_DAILY_GOAL
    conn = tracker._db()
    try:
        with conn:
            conn.execute(
                "INSERT INTO user_settings(session_id, setting_key, setting_value) VALUES (?, ?, ?)",
                ("user-a", "daily_goal_questions", "35"),
            )
    finally:
        conn.close()

    assert tracker._get_daily_goal("user-a") == 35
    assert tracker._get_daily_goal("user-b") == tracker.DEFAULT_DAILY_GOAL


def test_streak_uses_consecutive_local_calendar_days():
    today = date(2026, 10, 13)
    tz = ZoneInfo("Asia/Kolkata")
    attempts = [
        {"completed_at": datetime.combine(today - timedelta(days=offset), datetime.min.time(), tzinfo=tz).isoformat(), "total": 10}
        for offset in (0, 1, 2, 4)
    ]

    today_count, current_streak, best_streak = tracker._daily_stats(attempts, today)

    assert today_count == 10
    assert current_streak == 3
    assert best_streak == 3
