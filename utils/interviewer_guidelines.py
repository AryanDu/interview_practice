"""
Interviewer guidelines and structured evaluation criteria
"""
import logging

logger = logging.getLogger(__name__)


class InterviewerGuidelines:
    """Guidelines for technical and behavioral interviews"""

    TECHNICAL_CRITERIA = {
        "knowledge_depth": {
            "description": "Understanding of core concepts and technologies",
            "weight": 0.25
        },
        "problem_solving": {
            "description": "Ability to approach and solve problems systematically",
            "weight": 0.25
        },
        "code_quality": {
            "description": "Writing clean, maintainable, and efficient code",
            "weight": 0.20
        },
        "communication": {
            "description": "Ability to explain technical concepts clearly",
            "weight": 0.15
        },
        "experience": {
            "description": "Relevant practical experience and past projects",
            "weight": 0.15
        }
    }

    BEHAVIORAL_CRITERIA = {
        "teamwork": {
            "description": "Ability to work well with others and collaborate",
            "weight": 0.20
        },
        "leadership": {
            "description": "Taking initiative and guiding team efforts",
            "weight": 0.20
        },
        "adaptability": {
            "description": "Flexibility and willingness to learn new things",
            "weight": 0.20
        },
        "communication": {
            "description": "Clear and professional communication skills",
            "weight": 0.20
        },
        "motivation": {
            "description": "Passion for the role and company mission",
            "weight": 0.20
        }
    }

    SCORING_RUBRIC = {
        "excellent": {
            "score": 25,
            "description": "Exceptional performance, clear mastery"
        },
        "good": {
            "score": 20,
            "description": "Solid performance, meets expectations"
        },
        "satisfactory": {
            "score": 15,
            "description": "Acceptable performance, some gaps"
        },
        "poor": {
            "score": 10,
            "description": "Below expectations, significant gaps"
        },
        "fail": {
            "score": 0,
            "description": "Does not meet minimum requirements"
        }
    }

    PASS_FAIL_LOGIC = {
        "pass": {
            "min_percentage": 80,
            "message": "Congratulations! You have passed the interview. We were impressed with your performance."
        },
        "borderline": {
            "min_percentage": 75,
            "message": "You are close to passing. Review your answers and try again soon."
        },
        "fail": {
            "min_percentage": 0,
            "message": "We shall let you know. You did not pass this time. Keep practicing!"
        }
    }

    @staticmethod
    def get_evaluation_feedback(score_percentage: float) -> str:
        """Get feedback based on score percentage"""
        try:
            if score_percentage >= InterviewerGuidelines.PASS_FAIL_LOGIC["pass"]["min_percentage"]:
                return InterviewerGuidelines.PASS_FAIL_LOGIC["pass"]["message"]
            elif score_percentage >= InterviewerGuidelines.PASS_FAIL_LOGIC["borderline"]["min_percentage"]:
                return InterviewerGuidelines.PASS_FAIL_LOGIC["borderline"]["message"]
            else:
                return InterviewerGuidelines.PASS_FAIL_LOGIC["fail"]["message"]
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return ""

    @staticmethod
    def calculate_technical_score(criteria_scores: dict) -> float:
        """Calculate weighted technical score"""
        try:
            total_score = 0
            for criterion, weight_info in InterviewerGuidelines.TECHNICAL_CRITERIA.items():
                if criterion in criteria_scores:
                    total_score += criteria_scores[criterion] * weight_info["weight"]
            return total_score
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return 0.0

    @staticmethod
    def calculate_behavioral_score(criteria_scores: dict) -> float:
        """Calculate weighted behavioral score"""
        try:
            total_score = 0
            for criterion, weight_info in InterviewerGuidelines.BEHAVIORAL_CRITERIA.items():
                if criterion in criteria_scores:
                    total_score += criteria_scores[criterion] * weight_info["weight"]
            return total_score
        except Exception as e:
            logger.error(f"Error calculating behavioral score: {e}")
            return 0.0
