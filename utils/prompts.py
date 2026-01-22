"""
Prompt engineering utilities with various techniques
"""
from typing import Dict, List, Optional
import json
from jinja2 import Environment, FileSystemLoader
import logging


logger = logging.getLogger(__name__)

class PromptEngineer:
    """Prompt engineering with multiple techniques"""
    
    @staticmethod
    def zero_shot_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None,
        question_type: str = "technical"
    ) -> Dict[str, str]:
        """Zero-shot prompting - no examples provided"""
        system_prompt = f"""You are an expert interview coach specializing in {domain} interviews. \
        Your role is to help candidates prepare for their interviews by providing high-quality, \
        realistic interview questions and feedback."""

        # Jinja2 template rendering
        env = Environment(loader=FileSystemLoader('templates/prompts'))
        template = env.get_template('interview_question.jinja2')
        try:
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type=question_type
            )
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            user_prompt = "Error: Unable to generate prompt."

        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "zero_shot"
        }
    
    @staticmethod
    def few_shot_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None,
        question_type: str = "technical"
    ) -> Dict[str, str]:
        """Few-shot prompting - with examples"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        env = Environment(loader=FileSystemLoader('templates/prompts'))
        template = env.get_template('interview_question.jinja2')
        try:
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type=question_type
            )
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            user_prompt = "Error: Unable to generate prompt."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "few_shot"
        }
    
    @staticmethod
    def chain_of_thought_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None,
        question_type: str = "technical"
    ) -> Dict[str, str]:
        """Chain-of-Thought prompting - step-by-step reasoning"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        env = Environment(loader=FileSystemLoader('templates/prompts'))
        template = env.get_template('interview_question.jinja2')
        try:
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type=question_type
            )
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            user_prompt = "Error: Unable to generate prompt."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "chain_of_thought"
        }
    
    @staticmethod
    def role_playing_prompt(
        domain: str,
        difficulty: str,
        persona: str,
        job_description: Optional[str] = None
    ) -> Dict[str, str]:
        """Role-playing prompt - AI acts as interviewer"""
        system_prompt = f"You are acting as a {persona} interviewer for a {domain} position."
        try:
            env = Environment(loader=FileSystemLoader('templates/prompts'))
            template = env.get_template('interview_question.jinja2')
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type=f"role_playing ({persona})"
            )
        except Exception as e:
            logger.error(f"Jinja2 template error in role_playing_prompt: {e}")
            user_prompt = f"Role playing interview for {domain}, {difficulty}, persona: {persona}."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "role_playing"
        }
    
    @staticmethod
    def tree_of_thought_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None,
        question_type: str = "technical"
    ) -> Dict[str, str]:
        """Tree of Thoughts prompting - explore multiple angles"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        try:
            env = Environment(loader=FileSystemLoader('templates/prompts'))
            template = env.get_template('interview_question.jinja2')
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type="tree_of_thought"
            )
        except Exception as e:
            logger.error(f"Jinja2 template error in tree_of_thought_prompt: {e}")
            user_prompt = f"Tree-of-thought interview for {domain}, {difficulty}."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "tree_of_thought"
        }
    
    @staticmethod
    def self_consistency_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None,
        question_type: str = "technical"
    ) -> Dict[str, str]:
        """Self-consistency prompting - generate multiple versions and synthesize"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        try:
            env = Environment(loader=FileSystemLoader('templates/prompts'))
            template = env.get_template('interview_question.jinja2')
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type="self_consistency"
            )
        except Exception as e:
            logger.error(f"Jinja2 template error in self_consistency_prompt: {e}")
            user_prompt = f"Self-consistency interview for {domain}, {difficulty}."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "self_consistency"
        }
    
    @staticmethod
    def structured_output_prompt(
        domain: str,
        difficulty: str,
        output_format: str = "json",
        job_description: Optional[str] = None
    ) -> Dict[str, str]:
        """Prompt for structured JSON output"""
        system_prompt = f"""You are an expert interview coach specializing in {domain} interviews.
        Generate interview preparation content in structured format."""
        
        if output_format == "json":
            schema = {
                "questions": [
                    {
                        "question": "string",
                        "type": "technical|behavioral|system_design",
                        "difficulty": "easy|medium|hard",
                        "expected_answer_points": ["point1", "point2"],
                        "follow_up_questions": ["question1", "question2"]
                    }
                ],
                "summary": "string",
                "preparation_tips": ["tip1", "tip2"]
            }
            format_instruction = f"Return your response as valid JSON following this schema: {json.dumps(schema, indent=2)}"
        else:
            format_instruction = f"Return your response in structured {output_format} format."
        
        user_prompt = f"""Generate {difficulty}-level interview questions for a {domain} position.

{format_instruction}

Include 5-7 questions with detailed expected answers and follow-up questions."""
        
        if job_description:
            user_prompt += f"\n\nJob Description Context:\n{job_description}\n\nTailor questions to this role."
        
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "structured_output",
            "output_format": output_format
        }
    
    @staticmethod
    def detailed_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None
    ) -> Dict[str, str]:
        """Optimized for detailed, in-depth responses"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        try:
            env = Environment(loader=FileSystemLoader('templates/prompts'))
            template = env.get_template('interview_question.jinja2')
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type="detailed"
            )
        except Exception as e:
            logger.error(f"Jinja2 template error in detailed_prompt: {e}")
            user_prompt = f"Detailed interview for {domain}, {difficulty}."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "detailed"
        }

    @staticmethod
    def concise_prompt(
        domain: str,
        difficulty: str,
        job_description: Optional[str] = None
    ) -> Dict[str, str]:
        """Optimized for concise responses"""
        system_prompt = f"You are an expert interview coach specializing in {domain} interviews."
        try:
            env = Environment(loader=FileSystemLoader('templates/prompts'))
            template = env.get_template('interview_question.jinja2')
            user_prompt = template.render(
                domain=domain,
                difficulty=difficulty,
                job_description=job_description,
                question_type="concise"
            )
        except Exception as e:
            logger.error(f"Jinja2 template error in concise_prompt: {e}")
            user_prompt = f"Concise interview for {domain}, {difficulty}."
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "concise"
        }
    
    @staticmethod
    def interviewer_guidelines_prompt(domain: str) -> Dict[str, str]:
        """Generate interviewer evaluation guidelines"""
        system_prompt = """You are an expert in interview evaluation and assessment. Create structured evaluation criteria for interviews."""
        
        env = Environment(loader=FileSystemLoader('templates/prompts'))
        template = env.get_template('interview_guidelines.jinja2')
        try:
            user_prompt = template.render(domain=domain)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            user_prompt = "Error: Unable to generate prompt."
        
        return {
            "system": system_prompt,
            "user": user_prompt,
            "technique": "interviewer_guidelines"
        }
    
    @staticmethod
    def get_all_techniques() -> List[str]:
        """Get list of all available prompt techniques"""
        return [
            "zero_shot",
            "few_shot",
            "chain_of_thought",
            "tree_of_thought",
            "self_consistency",
            "role_playing",
            "structured_output",
            "concise",
            "detailed",
            "interviewer_guidelines"
        ]
