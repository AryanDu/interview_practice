"""
LLM handler implementations for OpenAI, Gemini, and Claude
"""
from typing import List, Dict, Optional, Any
import openai
import google.generativeai as genai
import anthropic
from config import Config
import json
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OpenAIHandler:
    """Handler for OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        frequency_penalty: float = None,
        presence_penalty: float = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response from OpenAI"""
        if not self.client:
            logger.error("OpenAI API key not configured")
            raise ValueError("OpenAI API key not configured")
        
        model = model or Config.DEFAULT_OPENAI_MODEL
        temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE
        top_p = top_p if top_p is not None else Config.DEFAULT_TOP_P
        max_tokens = max_tokens or Config.DEFAULT_MAX_TOKENS
        frequency_penalty = frequency_penalty if frequency_penalty is not None else Config.DEFAULT_FREQUENCY_PENALTY
        presence_penalty = presence_penalty if presence_penalty is not None else Config.DEFAULT_PRESENCE_PENALTY
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream
        )
        
        if stream:
            return response  # Return stream object
        
        return {
            "content": response.choices[0].message.content,
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }


class GeminiHandler:
    """Handler for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.GOOGLE_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = Config.DEFAULT_GEMINI_MODEL
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Gemini"""
        if not self.api_key:
            logger.error("Gemini API key not configured")
            raise ValueError("Gemini API key not configured")
        
        model_name = model or self.model_name
        model = genai.GenerativeModel(model_name)
        
        # Combine system and user prompts for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        generation_config = {
            "temperature": temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            "top_p": top_p if top_p is not None else Config.DEFAULT_TOP_P,
            "max_output_tokens": max_tokens or Config.DEFAULT_MAX_TOKENS,
        }
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return {
            "content": response.text,
            "model": model_name,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
            },
            "finish_reason": response.candidates[0].finish_reason if response.candidates else None
        }


class ClaudeHandler:
    """Handler for Anthropic Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.model_name = Config.DEFAULT_CLAUDE_MODEL
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Claude"""
        if not self.client:
            logger.error("Claude API key not configured")
            raise ValueError("Claude API key not configured")
        
        model_name = model or self.model_name
        
        response = self.client.messages.create(
            model=model_name,
            max_tokens=max_tokens or Config.DEFAULT_MAX_TOKENS,
            temperature=temperature if temperature is not None else Config.DEFAULT_TEMPERATURE,
            top_p=top_p if top_p is not None else Config.DEFAULT_TOP_P,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "content": response.content[0].text,
            "model": model_name,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "finish_reason": response.stop_reason
        }


class LLMManager:
    """Manager for multiple LLM providers"""
    
    def __init__(self):
        self.openai_handler = OpenAIHandler() if Config.OPENAI_API_KEY else None
        self.gemini_handler = GeminiHandler() if Config.GOOGLE_API_KEY else None
        self.claude_handler = ClaudeHandler() if Config.ANTHROPIC_API_KEY else None
    
    def get_handler(self, provider: str):
        """Get handler for specified provider"""
        handlers = {
            "openai": self.openai_handler,
            "gemini": self.gemini_handler,
            "claude": self.claude_handler
        }
        handler = handlers.get(provider.lower())
        if not handler:
            logger.error(f"Provider {provider} not available or not configured")
            raise ValueError(f"Provider {provider} not available or not configured")
        return handler
    
    def generate_response(
        self,
        provider: str,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified provider"""
        handler = self.get_handler(provider)
        return handler.generate_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            **kwargs
        )
    
    def validate_response(
        self,
        main_provider: str,
        validator_provider: str,
        main_response: str,
        original_prompt: str
    ) -> Dict[str, Any]:
        """Use a second LLM to validate the main LLM's response"""
        validation_prompt = f"""
        Please evaluate the following interview preparation response for quality, accuracy, and appropriateness.
        
        Original prompt: {original_prompt}
        
        Response to evaluate:
        {main_response}
        
        Provide:
        1. Quality score (1-10)
        2. Strengths
        3. Weaknesses
        4. Suggestions for improvement
        5. Overall assessment (pass/fail)
        """
        
        system_prompt = "You are an expert evaluator of AI-generated interview preparation content."
        
        validation_response = self.generate_response(
            provider=validator_provider,
            system_prompt=system_prompt,
            user_prompt=validation_prompt
        )
        
        return {
            "validator_provider": validator_provider,
            "validation": validation_response["content"],
            "original_response": main_response
        }
