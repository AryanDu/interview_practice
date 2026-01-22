"""
Input validation utilities
"""
from typing import Tuple, Optional
from pydantic import BaseModel, ValidationError, validator
from config import Config


class InterviewRequest(BaseModel):
    """Pydantic model for interview request validation"""
    domain: str
    difficulty: str
    question_type: str = "technical"
    job_description: Optional[str] = None
    
    @validator('domain')
    def validate_domain(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Domain cannot be empty')
        if len(v) > 100:
            raise ValueError('Domain must be less than 100 characters')
        return v.strip()
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        # Accept both old and new difficulty level names
        allowed = ['easy', 'medium', 'hard', 'Beginner', 'Intermediate', 'Advanced', 'Expert']
        if v not in allowed:
            raise ValueError(f'Difficulty must be one of: {allowed}')
        return v
    
    @validator('question_type')
    def validate_question_type(cls, v):
        allowed = ['technical', 'behavioral', 'system_design', 'mixed']
        if v.lower() not in allowed:
            raise ValueError(f'Question type must be one of: {allowed}')
        return v.lower()
    
    @validator('job_description')
    def validate_job_description(cls, v):
        if v and len(v) > Config.MAX_JOB_DESC_LENGTH:
            raise ValueError(f'Job description exceeds maximum length of {Config.MAX_JOB_DESC_LENGTH}')
        return v


def validate_interview_request(
    domain: str,
    difficulty: str,
    question_type: str = "technical",
    job_description: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[InterviewRequest]]:
    """Validate interview request"""
    try:
        request = InterviewRequest(
            domain=domain,
            difficulty=difficulty,
            question_type=question_type,
            job_description=job_description
        )
        return True, None, request
    except ValidationError as e:
        error_msg = "; ".join([err['msg'] for err in e.errors()])
        return False, error_msg, None
