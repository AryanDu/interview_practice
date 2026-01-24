"""
Configuration management for the Interview Practice App
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")  # Uses GEMINI_API_KEY from .env
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")
    
    # Model defaults
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"  # Change to gpt-4o, gpt-4.1, etc. as needed
    DEFAULT_GEMINI_MODEL = "gemini-1.5-pro"  # Using gemini-1.5-pro for v1beta compatibility
    DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_GROK_MODEL = "grok-2"
    
    # Default LLM parameters
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 1.0
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_FREQUENCY_PENALTY = 0.0
    DEFAULT_PRESENCE_PENALTY = 0.0
    
    # Vector database
    VECTOR_DB_PATH = "./data/vector_db"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Security settings
    MAX_INPUT_LENGTH = 10000
    MAX_JOB_DESC_LENGTH = 50000
    RATE_LIMIT_REQUESTS = 50  # per hour
    
    # Image generation
    DEFAULT_IMAGE_SIZE = "1024x1024"
    DEFAULT_IMAGE_MODEL = "dall-e-3"
    
    # Deployment
    HOST = "0.0.0.0"
    PORT = 8501
    
    @classmethod
    def validate_api_keys(cls) -> dict:
        """Validate that required API keys are present"""
        keys_status = {
            "openai": cls.OPENAI_API_KEY is not None,
            "gemini": cls.GOOGLE_API_KEY is not None,
            "claude": cls.ANTHROPIC_API_KEY is not None,
            "grok": cls.GROK_API_KEY is not None,
        }
        return keys_status
