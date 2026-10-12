"""Regression checks for V2's read-only dashboard helpers."""
import ui.dashboard as dashboard


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
    fake_state = {}
    monkeypatch.setattr(dashboard.st, "session_state", fake_state)

    dashboard._go_to_workspace(2)

    assert fake_state["active_tab"] == 2
