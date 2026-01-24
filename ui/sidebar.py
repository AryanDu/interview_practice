"""
Sidebar configuration and setup for the Interview Practice App
"""
import streamlit as st
from config import Config
from utils.prompts import PromptEngineer


def render_sidebar():
    """Render and return sidebar configuration"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys status
        keys_status = Config.validate_api_keys()
        st.subheader("API Keys Status")
        for provider, status in keys_status.items():
            status_icon = "✅" if status else "❌"
            st.write(f"{status_icon} {provider.capitalize()}")
        
        if not any(keys_status.values()):
            st.error("⚠️ Please configure at least one API key in .env file")
            st.stop()
        
        # LLM Provider selection
        available_providers = [k for k, v in keys_status.items() if v]
        selected_provider = st.selectbox(
            "Select LLM Provider",
            options=available_providers,
            index=0 if available_providers else None
        )
        
        # Model selection
        models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"],
            "gemini": ["gemini-1.5-pro", "gemini-pro"],
            "claude": ["claude-3-5-sonnet-20241022"],
            "grok": ["grok-2", "grok-vision-beta"]
        }
        selected_model = st.selectbox(
            "Select Model",
            options=models.get(selected_provider, ["default"]),
            index=0
        )
        
        st.divider()
        
        # Prompt Engineering Technique
        st.subheader("📝 Prompt Engineering")
        prompt_engineer = PromptEngineer()
        techniques = prompt_engineer.get_all_techniques()
        selected_technique = st.selectbox(
            "Select Prompt Technique",
            options=techniques,
            index=0
        )
        
        st.divider()
        
        # LLM Parameters
        st.subheader("🎛️ LLM Parameters")
        temperature = st.slider("Temperature", 0.0, 2.0, Config.DEFAULT_TEMPERATURE, 0.1)
        top_p = st.slider("Top-p", 0.0, 1.0, Config.DEFAULT_TOP_P, 0.05)
        max_tokens = st.slider("Max Tokens", 100, 4000, Config.DEFAULT_MAX_TOKENS, 100)
        frequency_penalty = st.slider("Frequency Penalty", -2.0, 2.0, Config.DEFAULT_FREQUENCY_PENALTY, 0.1)
        presence_penalty = st.slider("Presence Penalty", -2.0, 2.0, Config.DEFAULT_PRESENCE_PENALTY, 0.1)
        
        st.divider()
        
        # Advanced features
        with st.expander("🔬 Advanced Features"):
            use_rag = st.checkbox("Use RAG (Job Description Context)", value=False)
            validate_with_llm = st.checkbox("Validate with Second LLM", value=False)
            validator_provider = None
            if validate_with_llm:
                other_providers = [p for p in available_providers if p != selected_provider]
                if other_providers:
                    validator_provider = st.selectbox(
                        "Validator LLM",
                        options=other_providers,
                        index=0
                    )
                else:
                    st.warning("No other providers available for validation")
            check_duplicates = st.checkbox("Check for Duplicates (Vector DB)", value=False)
            generate_image = st.checkbox("Generate Motivational Image", value=False)
            use_langchain = st.checkbox("Use LangChain Chains", value=False)
    
    return {
        "provider": selected_provider,
        "model": selected_model,
        "technique": selected_technique,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "use_rag": use_rag,
        "validate_with_llm": validate_with_llm,
        "validator_provider": validator_provider,
        "check_duplicates": check_duplicates,
        "generate_image": generate_image,
        "use_langchain": use_langchain,
    }


def initialize_session_state():
    """Initialize all required session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'llm_manager' not in st.session_state:
        from utils.llm_handlers import LLMManager
        st.session_state.llm_manager = LLMManager()
    if 'security_guard' not in st.session_state:
        from utils.security import SecurityGuard
        st.session_state.security_guard = SecurityGuard()
    if 'vector_db' not in st.session_state:
        try:
            from utils.vector_db import VectorDatabase
            st.session_state.vector_db = VectorDatabase()
        except Exception as e:
            st.session_state.vector_db = None
            st.warning(f"Vector database initialization failed: {e}")
    if 'image_generator' not in st.session_state:
        try:
            from utils.image_gen import ImageGenerator
            st.session_state.image_generator = ImageGenerator() if Config.OPENAI_API_KEY else None
        except:
            st.session_state.image_generator = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
