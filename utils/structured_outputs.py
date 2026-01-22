"""
Structured output formats for interview preparation and evaluation
"""
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuestionAnswer:
    """Q&A pair with tips and solutions"""
    question: str
    answer: str
    tips: str
    additional_solutions: List[str]
    difficulty: str


@dataclass
class StudyModeOutput:
    """Study mode format 1: Detailed Q&A with tips and solutions"""
    domain: str
    difficulty: str
    questions_and_answers: List[QuestionAnswer]
    cv: Optional[str] = None
    job_description: Optional[str] = None

    def to_json(self) -> str:
        """Convert to JSON string"""
        try:
            data = {
                "domain": self.domain,
                "difficulty": self.difficulty,
                "cv": self.cv,
                "job_description": self.job_description,
                "questions_and_answers": [asdict(qa) for qa in self.questions_and_answers]
            }
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error converting StudyModeOutput to JSON: {e}")
            return ""


@dataclass
class InterviewEvaluation:
    """Structured evaluation for technical and behavioral interviews"""
    candidate_name: str
    role: str
    persona: str
    total_score: float
    pass_fail: str
    technical_score: float
    behavioral_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]

    def to_json(self) -> str:
        """Convert to JSON string"""
        try:
            data = asdict(self)
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error converting InterviewEvaluation to JSON: {e}")
            return ""


@dataclass
class MockInterviewResult:
    """Study mode format 2: Mock interview results with scoring"""
    candidate_score: float
    max_score: float
    percentage: float
    pass_fail_status: str
    technical_questions_score: float
    behavioral_questions_score: float
    questions_answered: List[str]
    cv: Optional[str] = None
    job_description: Optional[str] = None
    persona: Optional[str] = None

    def to_json(self) -> str:
        """Convert to JSON string"""
        try:
            data = asdict(self)
            return json.dumps(data, indent=2)
        except Exception as e:
            logger.error(f"Error converting MockInterviewResult to JSON: {e}")
            return ""
