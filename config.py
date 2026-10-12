"""
Configuration management for the Interview Practice App
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load local environment variables; Streamlit Cloud secrets are read separately below.
load_dotenv()


def _configured_secret(*names: str) -> Optional[str]:
    """Read a setting from environment/.env first, then Streamlit Cloud Secrets."""
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    try:
        import streamlit as st
        for name in names:
            value = st.secrets.get(name)
            if value and str(value).strip():
                return str(value).strip()
    except Exception:
        # Local runs without Streamlit secrets are expected.
        pass
    return None


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = _configured_secret("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = _configured_secret("GEMINI_API_KEY", "GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = _configured_secret("ANTHROPIC_API_KEY")
    GROK_API_KEY: Optional[str] = _configured_secret("GROK_API_KEY", "XAI_API_KEY")
    OLLAMA_BASE_URL: Optional[str] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Model defaults
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"  # Change to gpt-4o, gpt-4.1, etc. as needed
    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"  # Current lightweight Gemini model default
    DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    DEFAULT_GROK_MODEL = "grok-2"
    DEFAULT_OLLAMA_MODEL = "phi3"  # Default Ollama model - lightweight and efficient
    
    # Supported OpenAI models (chat and non-chat)
    OPENAI_MODELS = [
        "gpt-5.2-codex",      # Non-chat model: code generation, uses responses.create
        "gpt-4o",             # Latest multimodal model
        "gpt-4o-mini",        # Efficient chat model
        "gpt-4.1",
        "gpt-4.1-mini", 
        "gpt-4.1-nano"
    ]
    
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
            "ollama": bool(os.getenv("OLLAMA_BASE_URL")),
        }
        return keys_status
