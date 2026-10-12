from ui.auth import _reset_session_for_user


def test_session_is_cleared_when_authenticated_account_changes():
    state = {
        "_app_session_owner_id": "user-a",
        "mock_interview_report_payload": {"score": 92},
        "conversation_history": ["private chat"],
        "vector_db": object(),
    }
    _reset_session_for_user(state, "user-b")
    assert state == {"_app_session_owner_id": "user-b"}


def test_same_authenticated_account_keeps_current_session_data():
    report = {"score": 84}
    state = {"_app_session_owner_id": "user-a", "mock_interview_report_payload": report}
    _reset_session_for_user(state, "user-a")
    assert state["mock_interview_report_payload"] is report


def test_session_reset_rejects_empty_identity():
    state = {"mock_interview_report_payload": {"score": 99}}
    try:
        _reset_session_for_user(state, "")
    except ValueError:
        pass
    else:
        raise AssertionError("Empty user ID should be rejected")
    assert "mock_interview_report_payload" in state
