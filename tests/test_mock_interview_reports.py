from io import BytesIO
from pypdf import PdfReader
import ui.mock_interview_reports as reports


def sample_payload(**overrides):
    payload = reports.build_report_payload(
        domain="Python interview", difficulty="Intermediate", question_type="technical",
        questions=["What is a dictionary?"], answers={0: "A key-value data structure."},
        score=82, skills=["Python", "Data Structures"],
        ideal_answers={0: "A dictionary stores key-value pairs and supports fast lookup."},
    )
    payload.update(overrides)
    return payload


def configure_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(reports, "_database_url", lambda: "")
    monkeypatch.setattr(reports, "DB_PATH", tmp_path / "reports.sqlite3")


def test_report_history_isolated_by_user(monkeypatch, tmp_path):
    configure_sqlite(monkeypatch, tmp_path)
    report_id = reports.save_report("user-a", "token-a", sample_payload())
    reports.save_report("user-b", "token-b", sample_payload(score=55))
    assert reports.get_report("user-a", report_id)["score"] == 82
    assert reports.get_report("user-b", report_id) is None
    assert len(reports.list_reports("user-a")) == 1
    assert reports.list_reports("user-a")[0]["score"] == 82


def test_saving_same_interview_token_is_idempotent(monkeypatch, tmp_path):
    configure_sqlite(monkeypatch, tmp_path)
    first = reports.save_report("user-a", "same-token", sample_payload(score=60))
    second = reports.save_report("user-a", "same-token", sample_payload(score=91))
    assert first == second
    assert len(reports.list_reports("user-a")) == 1
    assert reports.list_reports("user-a")[0]["score"] == 91


def test_pdf_contains_question_and_answers(monkeypatch, tmp_path):
    configure_sqlite(monkeypatch, tmp_path)
    report_id = reports.save_report("user-a", "token-a", sample_payload())
    payload = reports.get_report("user-a", report_id)
    pdf = reports.build_pdf(payload)
    assert pdf.startswith(b"%PDF-")
    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages)
    assert "MOCK INTERVIEW REPORT" in text
    assert "OVERALL SCORE INDICATOR" in text
    assert "Questions answered: 1/1" in text
    assert "What is a dictionary?" in text
    assert "A key-value data structure." in text
    assert "A dictionary stores key-value pairs" in text


def test_pdf_escapes_untrusted_markup(monkeypatch, tmp_path):
    configure_sqlite(monkeypatch, tmp_path)
    payload = sample_payload(domain="<script>alert(1)</script>",
        questions=["Explain A & B < C?"], answers=["<img src=x onerror=alert(1)>"],
        ideal_answers=["Answer containing 1 < 2 and A & B."])
    pdf = reports.build_pdf(payload)
    assert pdf.startswith(b"%PDF-")
    assert len(PdfReader(BytesIO(pdf)).pages) >= 1


def test_report_payload_bounds_large_user_content():
    payload = reports.build_report_payload(
        domain="D" * 500, difficulty="Intermediate", question_type="technical",
        questions=["Q" * 3000], answers={0: "A" * 9000}, score=1000,
        skills=["Skill"] * 50, ideal_answers={0: "I" * 9000})
    assert len(payload["domain"]) <= 100
    assert len(payload["questions"][0]) <= 2000
    assert len(payload["answers"][0]) <= 5000
    assert len(payload["ideal_answers"][0]) <= 5000
    assert payload["score"] == 100
    assert len(payload["skills"]) <= 15


def test_60_simulated_users_have_isolated_report_history(monkeypatch, tmp_path):
    """Exercise shared-store concurrency with 60 identities and bounded parallel writes."""
    from concurrent.futures import ThreadPoolExecutor

    configure_sqlite(monkeypatch, tmp_path)

    def create_and_check(index):
        user_id = f"sim-user-{index}"
        report_id = reports.save_report(user_id, f"token-{index}", sample_payload(score=index % 101))
        own_history = reports.list_reports(user_id, limit=5)
        other_user_id = f"sim-user-{(index + 1) % 60}"
        cross_user_result = reports.get_report(other_user_id, report_id)
        return (
            len(own_history) == 1
            and own_history[0]["score"] == index % 101
            and cross_user_result is None
        )

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(create_and_check, range(60)))
    assert all(results)
