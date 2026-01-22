import pytest
from utils.prompts import PromptEngineer

def test_study_mode_output():
    result = PromptEngineer.structured_output_prompt(
        domain="Software Engineering",
        difficulty="medium",
        output_format="json",
        job_description="Backend developer role"
    )
    assert "questions" in result["user"]
    assert "study_mode" in result["user"]
