import pytest
from utils.structured_outputs import StudyModeOutput, MockInterviewResult, QuestionAnswer
from utils.interviewer_guidelines import InterviewerGuidelines


def test_study_mode_output_json():
    """Test StudyModeOutput JSON serialization"""
    qa = QuestionAnswer(
        question="What is OOP?",
        answer="Object-Oriented Programming is a paradigm based on objects and classes.",
        tips="Focus on the four pillars: Encapsulation, Inheritance, Polymorphism, Abstraction",
        additional_solutions=["Learn through examples", "Practice with code"],
        difficulty="medium"
    )
    study_output = StudyModeOutput(
        domain="Software Engineering",
        difficulty="medium",
        questions_and_answers=[qa]
    )
    json_output = study_output.to_json()
    assert "OOP" in json_output
    assert "Encapsulation" in json_output


def test_mock_interview_result_json():
    """Test MockInterviewResult JSON serialization"""
    mock_result = MockInterviewResult(
        candidate_score=95,
        max_score=125,
        percentage=76.0,
        pass_fail_status="pass",
        technical_questions_score=50,
        behavioral_questions_score=45,
        questions_answered=["Q1", "Q2", "Q3"]
    )
    json_output = mock_result.to_json()
    assert "95" in json_output
    assert "pass" in json_output


def test_interviewer_guidelines_pass_fail():
    """Test pass/fail logic in interviewer guidelines"""
    feedback_pass = InterviewerGuidelines.get_evaluation_feedback(85.0)
    assert "passed" in feedback_pass.lower()
    
    feedback_borderline = InterviewerGuidelines.get_evaluation_feedback(75.0)
    assert "close" in feedback_borderline.lower()
    
    feedback_fail = InterviewerGuidelines.get_evaluation_feedback(60.0)
    assert "practicing" in feedback_fail.lower()


def test_technical_score_calculation():
    """Test technical score weighted calculation"""
    criteria_scores = {
        "knowledge_depth": 20,
        "problem_solving": 18,
        "code_quality": 16,
        "communication": 14,
        "experience": 12
    }
    score = InterviewerGuidelines.calculate_technical_score(criteria_scores)
    assert score > 0


def test_behavioral_score_calculation():
    """Test behavioral score weighted calculation"""
    criteria_scores = {
        "teamwork": 18,
        "leadership": 16,
        "adaptability": 17,
        "communication": 19,
        "motivation": 20
    }
    score = InterviewerGuidelines.calculate_behavioral_score(criteria_scores)
    assert score > 0
