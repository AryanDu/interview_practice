"""Regression checks for V2 navigation, progress summaries and preferences."""
from ui import dashboard, quiz_tracker, settings


class FakeSessionState(dict):
    """Small dict-backed stand-in for Streamlit's attribute-access session state."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


def test_topic_accuracy_uses_recorded_counts():
    topics = [
        {"topic": "Arrays", "attempted": 10, "correct": 8},
        {"topic": "Hash maps", "attempted": 4, "correct": 1},
    ]

    assert dashboard._accuracy(topics) == [
        {"topic": "Arrays", "attempted": 10, "accuracy": 80},
        {"topic": "Hash maps", "attempted": 4, "accuracy": 25},
    ]


def test_topic_accuracy_handles_missing_or_zero_attempts():
    topics = [
        {"topic": "Untested", "attempted": 0, "correct": 0},
        {"correct": None},
    ]

    assert dashboard._accuracy(topics) == [
        {"topic": "Untested", "attempted": 0, "accuracy": 0},
        {"topic": "General", "attempted": 0, "accuracy": 0},
    ]


def test_dashboard_shortcut_keeps_existing_workspace_indexes(monkeypatch):
    fake_state = FakeSessionState(quiz_tracker_focus="weak")
    monkeypatch.setattr(dashboard.st, "session_state", fake_state)

    dashboard._go_to_workspace(2)

    assert fake_state.active_tab == 2
    assert fake_state.v2_workspace_picker == "🎤 Mock Interview"
    assert "quiz_tracker_focus" not in fake_state


def test_exam_navigator_clamps_question_index(monkeypatch):
    fake_state = FakeSessionState(
        quiz_tracker_quiz=[{"question": "One"}, {"question": "Two"}, {"question": "Three"}],
        quiz_tracker_current_question_index=0,
    )
    monkeypatch.setattr(quiz_tracker.st, "session_state", fake_state)

    quiz_tracker._jump_to_question(99)
    assert fake_state.quiz_tracker_current_question_index == 2

    quiz_tracker._jump_to_question(-7)
    assert fake_state.quiz_tracker_current_question_index == 0


def test_answers_from_widgets_keeps_answers_for_unrendered_questions(monkeypatch):
    token = "attempt-123"
    session_id = "user-123"
    fake_state = FakeSessionState(
        quiz_tracker_attempt_token=token,
        quiz_tracker_answers={0: 2, 2: 1},
    )
    # Only question 1 is currently rendered; answers for questions 0 and 2
    # must survive when Streamlit has removed their radio widgets.
    fake_state[f"quiz_answer_{session_id}_{token}_1"] = 3
    monkeypatch.setattr(quiz_tracker.st, "session_state", fake_state)

    answers = quiz_tracker._answers_from_widgets(session_id, [{}, {}, {}, {}])

    assert answers == {0: 2, 1: 3, 2: 1}
    assert fake_state.quiz_tracker_answers == answers


def test_radio_change_persists_answer_in_durable_state(monkeypatch):
    token = "attempt-456"
    session_id = "user-456"
    fake_state = FakeSessionState(
        quiz_tracker_attempt_token=token,
        quiz_tracker_answers={0: 1},
    )
    fake_state[f"quiz_answer_{session_id}_{token}_2"] = 3
    monkeypatch.setattr(quiz_tracker.st, "session_state", fake_state)

    quiz_tracker._persist_answer_from_widget(session_id, 2)

    assert fake_state.quiz_tracker_answers == {0: 1, 2: 3}


def test_v2_preferences_use_existing_user_settings_table(monkeypatch, tmp_path):
    monkeypatch.setattr(quiz_tracker, "_database_url", lambda: "")
    monkeypatch.setattr(quiz_tracker, "DB_PATH", tmp_path / "v2_preferences.sqlite3")
    fake_state = FakeSessionState(v2_compact_layout=True)
    monkeypatch.setattr(settings.st, "session_state", fake_state)

    settings._save_preference("user-a", "v2_compact_layout", "v2_compact_layout")

    assert settings._load_preference("user-a", "v2_compact_layout", "False") == "True"
    assert settings._load_preference("user-b", "v2_compact_layout", "False") == "False"
