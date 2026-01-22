"""
Main Streamlit application for Interview Practice App
"""
import streamlit as st
import json
from typing import Dict, Optional
import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.llm_handlers import LLMManager
from utils.prompts import PromptEngineer
from utils.security import SecurityGuard
from utils.cost_calculator import CostCalculator
from utils.vector_db import VectorDatabase
from utils.image_gen import ImageGenerator
from utils.validators import validate_interview_request
from utils.structured_outputs import StudyModeOutput, MockInterviewResult, QuestionAnswer
from utils.interviewer_guidelines import InterviewerGuidelines
from chains.interview_chains import InterviewChain
import logging

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Interview Practice App",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()
if 'security_guard' not in st.session_state:
    st.session_state.security_guard = SecurityGuard()
if 'vector_db' not in st.session_state:
    try:
        st.session_state.vector_db = VectorDatabase()
    except Exception as e:
        st.session_state.vector_db = None
        st.warning(f"Vector database initialization failed: {e}")
if 'image_generator' not in st.session_state:
    try:
        st.session_state.image_generator = ImageGenerator() if Config.OPENAI_API_KEY else None
    except:
        st.session_state.image_generator = None

# Custom CSS
st.markdown("""
    <style>
    :root {
        --primary-color: #c44900;
        --dark-bg: #04151f;
        --secondary-color: #183a37;
        --accent-light: #efd6ac;
        --dark-purple: #432534;
    }
    body {
        background-color: #04151f;
        color: #efd6ac;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #c44900;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #183a37;
        border: 2px solid #c44900;
        color: #efd6ac;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #432534;
        border: 2px solid #c44900;
        color: #efd6ac;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    st.markdown('<h1 class="main-header">💼 Interview Practice App</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration
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
            "claude": ["claude-3-5-sonnet-20241022"]
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
        
        # Chatbot mode toggle
        chatbot_mode = st.checkbox("💬 Enable Chatbot Mode", value=False)
        
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
    
    # Initialize active tab tracking
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Tab selection
    st.markdown("---")
    tab_names = ["🎯 Interview Prep", "🎤 Mock Interview", "💬 Chatbot", "📊 Analytics", "🔒 Security Testing", "🎨 Visual Tools"]
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.write("**Navigate:**")
    with col2:
        selected_tab = st.selectbox("", options=range(len(tab_names)), format_func=lambda x: tab_names[x], label_visibility="collapsed")
        st.session_state.active_tab = selected_tab
    
    st.markdown("---")
    
    # Display selected tab content
    if st.session_state.active_tab == 0:
        interview_prep_tab(selected_provider, selected_model, selected_technique, 
                          temperature, top_p, max_tokens, frequency_penalty, presence_penalty,
                          use_rag, validate_with_llm, validator_provider,
                          check_duplicates, generate_image, use_langchain)
    
    elif st.session_state.active_tab == 1:
        mock_interview_tab(selected_provider, selected_model, temperature, top_p, max_tokens)
    
    elif st.session_state.active_tab == 2:
        chatbot_tab(selected_provider, selected_model, temperature, top_p, max_tokens)
    
    elif st.session_state.active_tab == 3:
        analytics_tab()
    
    elif st.session_state.active_tab == 4:
        security_testing_tab()
    
    elif st.session_state.active_tab == 5:
        visual_tools_tab()


def interview_prep_tab(provider, model, technique, temperature, top_p, max_tokens, 
                       frequency_penalty, presence_penalty, use_rag, validate_with_llm,
                       validator_provider, check_duplicates, generate_image, use_langchain):
    """Interview preparation tab"""
    st.header("Interview Preparation - Study Mode")
    st.markdown("Upload your CV or job description for personalized questions.")
    cv_file = st.file_uploader("Upload CV (PDF or TXT)", type=["pdf", "txt"], key="interview_prep_cv")
    job_description = st.text_area("Job Description (optional)", height=150, key="interview_prep_job_desc")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        domain = st.text_input("Domain/Field", placeholder="e.g., Software Engineering, Data Science")
        difficulty = st.selectbox("Difficulty Level", ["easy", "medium", "hard"], index=1)
        question_type = st.selectbox("Question Type", ["technical", "behavioral", "system_design", "mixed"], index=0)
        num_questions = st.slider("Number of Questions", min_value=1, max_value=20, value=5, step=1)
        
        # Job description for RAG
        job_description = None
        if use_rag:
            job_description = st.text_area(
                "Job Description (for RAG)",
                placeholder="Paste the job description here...",
                height=200,
                key="interview_prep_rag_job_desc"
            )
    
    with col2:
        persona = None
        if technique == "role_playing":
            persona = st.selectbox("Interviewer Persona", ["friendly", "strict", "neutral"], index=0)
        
        response_style = st.selectbox("Response Style", ["concise", "detailed"], index=1)
    
    # Generate prompts
    if st.button("🚀 Generate Study Pack", type="primary"):
        if not domain:
            st.error("Please enter a domain/field")
            return
        
        # Validate input
        is_valid, error_msg, request = validate_interview_request(
            domain=domain,
            difficulty=difficulty,
            question_type=question_type,
            job_description=job_description
        )
        
        if not is_valid:
            st.error(f"Validation error: {error_msg}")
            return
        
        # Security check
        user_input = f"{domain} {difficulty} {question_type}"
        is_safe, security_error = st.session_state.security_guard.comprehensive_check(
            user_input=user_input,
            job_description=job_description,
            user_id="streamlit_user"
        )
        
        if not is_safe:
            st.error(f"Security check failed: {security_error}")
            return
        
        # Check for duplicates
        duplicate_found = False
        if check_duplicates and st.session_state.vector_db:
            try:
                content_preview = f"{domain} {difficulty} {question_type}"
                is_duplicate, duplicate_info = st.session_state.vector_db.check_duplicate(
                    domain=domain,
                    difficulty=difficulty,
                    content=content_preview
                )
                if is_duplicate:
                    duplicate_found = True
                    st.warning("⚠️ Similar content found in database. Consider generating new questions.")
            except Exception as e:
                st.warning(f"Duplicate check failed: {e}")
        
        # Generate prompts using selected technique
        prompt_engineer = PromptEngineer()
        
        try:
            if technique == "zero_shot":
                prompts = prompt_engineer.zero_shot_prompt(domain, difficulty, job_description, question_type)
            elif technique == "few_shot":
                prompts = prompt_engineer.few_shot_prompt(domain, difficulty, job_description, question_type)
            elif technique == "chain_of_thought":
                prompts = prompt_engineer.chain_of_thought_prompt(domain, difficulty, job_description, question_type)
            elif technique == "tree_of_thought":
                prompts = prompt_engineer.tree_of_thought_prompt(domain, difficulty, job_description, question_type)
            elif technique == "self_consistency":
                prompts = prompt_engineer.self_consistency_prompt(domain, difficulty, job_description, question_type)
            elif technique == "role_playing":
                prompts = prompt_engineer.role_playing_prompt(domain, difficulty, persona, job_description)
            elif technique == "structured_output":
                prompts = prompt_engineer.structured_output_prompt(domain, difficulty, "json", job_description)
            elif technique == "concise":
                prompts = prompt_engineer.concise_prompt(domain, difficulty, job_description)
            elif technique == "detailed":
                prompts = prompt_engineer.detailed_prompt(domain, difficulty, job_description)
            elif technique == "interviewer_guidelines":
                prompts = prompt_engineer.interviewer_guidelines_prompt(domain)
            else:
                prompts = prompt_engineer.zero_shot_prompt(domain, difficulty, job_description, question_type)
            
            # RAG: Get context from vector database
            rag_context = ""
            if use_rag and job_description and st.session_state.vector_db:
                try:
                    rag_context = st.session_state.vector_db.get_context_for_rag(
                        job_description=job_description,
                        domain=domain
                    )
                    if rag_context:
                        prompts["user"] = f"Context from similar interview preparations:\n\n{rag_context}\n\n---\n\n{prompts['user']}"
                except Exception as e:
                    st.warning(f"RAG context retrieval failed: {e}")
            
            # Use LangChain if requested
            response = None
            if use_langchain:
                try:
                    chain = InterviewChain(provider=provider, model=model)
                    result = chain.run_interview_chain(domain, difficulty, job_description)
                    response_text = result.get("questions", "No response generated")
                    # Create a mock response dict for LangChain (cost calculation may not work)
                    response = {"content": response_text, "usage": {}}
                except Exception as e:
                    st.error(f"LangChain error: {e}")
                    response_text = None
            else:
                # Generate response using LLM manager
                with st.spinner("Generating interview questions..."):
                    response = st.session_state.llm_manager.generate_response(
                        provider=provider,
                        system_prompt=prompts["system"],
                        user_prompt=prompts["user"],
                        model=model,
                        temperature=temperature,
                        top_p=top_p,
                        max_tokens=max_tokens,
                        frequency_penalty=frequency_penalty if provider == "openai" else None,
                        presence_penalty=presence_penalty if provider == "openai" else None
                    )
                    response_text = response.get("content")
            
            if response_text:
                # Display response
                st.success("✅ Interview questions generated!")
                st.markdown("### Generated Content")
                st.markdown(response_text)
                
                # Calculate cost
                if response and "usage" in response and response["usage"]:
                    cost_info = CostCalculator.calculate_from_response(
                        provider=provider,
                        model=model,
                        usage=response["usage"]
                    )
                    st.markdown("### Cost Information")
                    st.markdown(CostCalculator.format_cost_display(cost_info))
                
                # LLM Validation
                if validate_with_llm and validator_provider:
                    with st.spinner("Validating with second LLM..."):
                        try:
                            validation = st.session_state.llm_manager.validate_response(
                                main_provider=provider,
                                validator_provider=validator_provider,
                                main_response=response_text,
                                original_prompt=prompts["user"]
                            )
                            st.markdown("### LLM Validation")
                            st.markdown(validation["validation"])
                        except Exception as e:
                            st.warning(f"Validation failed: {e}")
                
                # Store in vector database
                if st.session_state.vector_db:
                    try:
                        st.session_state.vector_db.add_interview_prep(
                            domain=domain,
                            difficulty=difficulty,
                            content=response_text,
                            metadata={
                                "technique": technique,
                                "question_type": question_type,
                                "model": model,
                                "provider": provider
                            }
                        )
                    except Exception as e:
                        st.warning(f"Failed to store in vector database: {e}")
                
                # Generate image
                if generate_image and st.session_state.image_generator:
                    with st.spinner("Generating motivational image..."):
                        try:
                            image_result = st.session_state.image_generator.generate_motivational_image()
                            if image_result.get("success"):
                                st.image(image_result["url"], caption="Motivational Image for Interview Prep")
                        except Exception as e:
                            st.warning(f"Image generation failed: {e}")
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "type": "interview_prep",
                    "domain": domain,
                    "difficulty": difficulty,
                    "technique": technique,
                    "response": response_text
                })
                
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            st.exception(e)


def mock_interview_tab(provider, model, temperature, top_p, max_tokens):
    """Mock interview tab with interactive Q&A and scoring"""
    st.header("🎤 Mock Interview - Practice with Real Questions")
    st.markdown("Answer interview questions and receive a personalized score based on your responses.")
    
    # Initialize session state for mock interview
    if 'mock_interview_questions' not in st.session_state:
        st.session_state.mock_interview_questions = None
    if 'mock_interview_answers' not in st.session_state:
        st.session_state.mock_interview_answers = {}
    if 'mock_interview_score' not in st.session_state:
        st.session_state.mock_interview_score = None
    if 'mock_interview_current_question' not in st.session_state:
        st.session_state.mock_interview_current_question = 0
    
    # Setup section
    st.subheader("📝 Interview Setup")
    setup_col1, setup_col2 = st.columns([1, 1])
    
    with setup_col1:
        domain = st.text_input("Domain/Field", placeholder="e.g., Software Engineering, Data Science", key="mock_domain")
        difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced", "Expert"], index=1, key="mock_difficulty")
    
    with setup_col2:
        question_type = st.selectbox("Question Type", ["technical", "behavioral", "mixed"], index=2, key="mock_question_type")
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=3, step=1, key="mock_num_questions")
    
    # Generate questions button
    if st.button("🚀 Generate Interview Questions", type="primary", use_container_width=True):
        if not domain:
            st.error("Please enter a domain/field")
            return
        
        # Validate input
        is_valid, error_msg, request = validate_interview_request(
            domain=domain,
            difficulty=difficulty,
            question_type=question_type
        )
        
        if not is_valid:
            st.error(f"Validation error: {error_msg}")
            return
        
        # Security check
        user_input = f"{domain} {difficulty} {question_type}"
        is_safe, security_error = st.session_state.security_guard.comprehensive_check(
            user_input=user_input,
            user_id="streamlit_user"
        )
        
        if not is_safe:
            st.error(f"Security check failed: {security_error}")
            return
        
        # Generate prompts
        prompt_engineer = PromptEngineer()
        
        try:
            # Map difficulty level to LLM prompt level
            difficulty_map = {"Beginner": "easy", "Intermediate": "medium", "Advanced": "hard", "Expert": "hard"}
            prompt_difficulty = difficulty_map.get(difficulty, "medium")
            
            if question_type == "technical":
                prompts = prompt_engineer.zero_shot_prompt(domain, prompt_difficulty, None, "technical")
            elif question_type == "behavioral":
                prompts = prompt_engineer.zero_shot_prompt(domain, prompt_difficulty, None, "behavioral")
            else:
                prompts = prompt_engineer.zero_shot_prompt(domain, prompt_difficulty, None, "mixed")
            
            # Modify the prompt to generate exactly num_questions questions
            modified_user_prompt = f"""{prompts['user']}

IMPORTANT: Generate exactly {num_questions} interview questions. Format each question on a new line starting with the question number (1., 2., etc.).
Return ONLY the questions, nothing else."""
            
            # Generate response
            with st.spinner(f"Generating {num_questions} interview questions..."):
                response = st.session_state.llm_manager.generate_response(
                    provider=provider,
                    system_prompt=prompts["system"],
                    user_prompt=modified_user_prompt,
                    model=model,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
                response_text = response.get("content")
            
            if response_text:
                # Parse questions from response
                import re
                # Split by numbered lines (1., 2., 3., etc.)
                lines = response_text.strip().split('\n')
                questions = []
                for line in lines:
                    line = line.strip()
                    # Check if line starts with a number followed by a period
                    if line and line[0].isdigit():
                        # Remove the numbering (1., 2., etc.)
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            question = parts[1].strip()
                            if question:  # Only add non-empty questions
                                questions.append(question)
                
                if questions:
                    st.session_state.mock_interview_questions = questions[:num_questions]
                    st.session_state.mock_interview_answers = {i: "" for i in range(len(questions[:num_questions]))}
                    st.session_state.mock_interview_current_question = 0
                    st.session_state.mock_interview_score = None
                    # Store domain and difficulty for later use
                    st.session_state.mock_interview_domain = domain
                    st.session_state.mock_interview_difficulty = difficulty
                    st.success(f"✅ {len(questions[:num_questions])} questions generated! Click 'Next' to start the interview.")
                    st.rerun()
                else:
                    st.error("Failed to parse questions from response. Response was: " + response_text[:200])
            else:
                st.error("Failed to generate questions")
                
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
    
    # Interview progress
    if st.session_state.mock_interview_questions:
        st.divider()
        st.subheader(f"🎤 Mock Interview - Question {st.session_state.mock_interview_current_question + 1}/{len(st.session_state.mock_interview_questions)}")
        
        # Progress bar
        progress = st.session_state.mock_interview_current_question / len(st.session_state.mock_interview_questions)
        st.progress(progress)
        
        # Display current question
        current_q_idx = st.session_state.mock_interview_current_question
        current_question = st.session_state.mock_interview_questions[current_q_idx]
        
        st.markdown(f"### Question {current_q_idx + 1}")
        st.markdown(f"**{current_question}**")
        
        # Text area for answer
        answer = st.text_area(
            "Your Answer:",
            value=st.session_state.mock_interview_answers.get(current_q_idx, ""),
            height=150,
            placeholder="Type your answer here...",
            label_visibility="collapsed",
            key=f"mock_answer_{current_q_idx}"
        )
        
        # Save answer
        st.session_state.mock_interview_answers[current_q_idx] = answer
        
        # Navigation buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⬅️ Previous", use_container_width=True):
                if st.session_state.mock_interview_current_question > 0:
                    st.session_state.mock_interview_current_question -= 1
                    st.rerun()
        
        with col2:
            if st.button("➡️ Next", use_container_width=True):
                if st.session_state.mock_interview_current_question < len(st.session_state.mock_interview_questions) - 1:
                    st.session_state.mock_interview_current_question += 1
                    st.rerun()
                else:
                    st.warning("This is the last question. Click 'Submit Interview' to finish.")
        
        with col3:
            if st.button("🔄 Skip", use_container_width=True):
                if st.session_state.mock_interview_current_question < len(st.session_state.mock_interview_questions) - 1:
                    st.session_state.mock_interview_current_question += 1
                    st.rerun()
        
        with col4:
            if st.button("✅ Submit Interview", type="primary", use_container_width=True):
                # Calculate score
                with st.spinner("Evaluating your answers..."):
                    try:
                        # Prepare evaluation prompt
                        evaluation_prompt = """You are an expert interviewer. Rate the following interview responses on a scale of 0-100 based on:
- Completeness of answer
- Clarity and communication
- Technical accuracy (if applicable)
- Relevance to the question

Provide a single overall score between 0-100 for the candidate's performance across all answers.

Questions and Answers:
"""
                        
                        for i, (q, a) in enumerate(zip(st.session_state.mock_interview_questions, 
                                                        [st.session_state.mock_interview_answers.get(j, "") for j in range(len(st.session_state.mock_interview_questions))]
                                                      ), 1):
                            evaluation_prompt += f"\nQ{i}: {q}\nA{i}: {a}\n"
                        
                        evaluation_prompt += "\nProvide ONLY the numerical score (0-100), nothing else."
                        
                        # Get evaluation from LLM
                        eval_response = st.session_state.llm_manager.generate_response(
                            provider=provider,
                            system_prompt="You are an expert interviewer evaluator.",
                            user_prompt=evaluation_prompt,
                            model=model,
                            temperature=0.3,
                            top_p=0.9,
                            max_tokens=50
                        )
                        
                        score_text = eval_response.get("content", "0").strip()
                        import re
                        score_match = re.search(r'\d+', score_text)
                        if score_match:
                            score = int(score_match.group())
                            score = min(100, max(0, score))  # Clamp between 0-100
                        else:
                            score = 75  # Default score
                        
                        st.session_state.mock_interview_score = score
                        
                        # Extract skills from questions using LLM
                        with st.spinner("Analyzing skills tested..."):
                            try:
                                skills_prompt = "Based on these interview questions, identify the key skills being tested.\nReturn ONLY a comma-separated list of skills, nothing else.\n\nQuestions:\n"
                                skills_prompt += "\n".join(st.session_state.mock_interview_questions)
                                
                                skills_response = st.session_state.llm_manager.generate_response(
                                    provider=provider,
                                    system_prompt="You are an expert at identifying technical and professional skills from interview questions.",
                                    user_prompt=skills_prompt,
                                    model=model,
                                    temperature=0.3,
                                    top_p=0.9,
                                    max_tokens=100
                                )
                                
                                skills_text = skills_response.get("content", "").strip()
                                # Parse skills and filter to valid ones
                                valid_skills = ["Python", "JavaScript", "System Design", "Database", "Problem Solving", 
                                              "Communication", "Leadership", "Teamwork", "AWS", "Docker", "React", "Node.js"]
                                detected_skills = [s.strip() for s in skills_text.split(',')]
                                detected_skills = [s for s in detected_skills if s in valid_skills]
                                st.session_state.mock_interview_skills = detected_skills if detected_skills else ["Problem Solving"]
                            except Exception as e:
                                st.session_state.mock_interview_skills = ["Problem Solving"]
                        
                        # Generate ideal answers for each question
                        with st.spinner("Generating ideal answers..."):
                            try:
                                ideal_answers = {}
                                for i, question in enumerate(st.session_state.mock_interview_questions):
                                    ideal_prompt = f"""You are an expert interviewer. Provide the ideal/best answer to this interview question.
Provide a comprehensive, well-structured answer that demonstrates strong understanding.

Question: {question}

Provide only the ideal answer, nothing else."""
                                    
                                    ideal_response = st.session_state.llm_manager.generate_response(
                                        provider=provider,
                                        system_prompt="You are an expert at providing ideal interview answers.",
                                        user_prompt=ideal_prompt,
                                        model=model,
                                        temperature=0.3,
                                        top_p=0.9,
                                        max_tokens=300
                                    )
                                    
                                    ideal_answers[i] = ideal_response.get("content", "No ideal answer generated.")
                                st.session_state.mock_interview_ideal_answers = ideal_answers
                            except Exception as e:
                                st.session_state.mock_interview_ideal_answers = {}
                        
                        st.success(f"✅ Interview completed! Your Mock Interview Score: **{score}%**")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error evaluating answers: {e}")
        
        # Show answers summary if interview is completed
        if st.session_state.mock_interview_score is not None:
            st.divider()
            st.subheader("📊 Interview Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mock Interview Score", f"{st.session_state.mock_interview_score}%")
            with col2:
                if st.button("📊 Create Result Card", type="primary", use_container_width=True):
                    # Pre-fill Visual Tools with interview data
                    st.session_state.prefill_position = st.session_state.mock_interview_domain
                    st.session_state.prefill_mock_score = st.session_state.mock_interview_score
                    st.session_state.prefill_improvement = st.session_state.mock_interview_difficulty
                    st.session_state.prefill_skills = st.session_state.mock_interview_skills
                    st.session_state.active_tab = 5  # Switch to Visual Tools tab
                    st.success("✅ Switching to Visual Tools with your interview data...")
                    st.rerun()
            
            # Show all answers with ideal answers
            with st.expander("📖 Review Your Answers & Ideal Responses"):
                for i, (q, a) in enumerate(zip(st.session_state.mock_interview_questions,
                                              [st.session_state.mock_interview_answers.get(j, "") for j in range(len(st.session_state.mock_interview_questions))]), 1):
                    st.markdown(f"**Q{i}: {q}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### Your Answer:")
                        st.markdown(f"_{a if a else 'No answer provided'}_")
                    
                    with col2:
                        st.markdown("##### 💡 Ideal Answer:")
                        ideal = st.session_state.mock_interview_ideal_answers.get(i-1, "No ideal answer generated.") if 'mock_interview_ideal_answers' in st.session_state else "No ideal answer generated."
                        st.markdown(f"_{ideal}_")
                    
                    st.divider()


def chatbot_tab(provider, model, temperature, top_p, max_tokens):
    """Conversational chatbot tab"""
    st.header("💬 Professional Interview Assistant")
    st.markdown("Ask me professional interview questions and get detailed answers.")
    
    # Initialize chatbot session state
    if 'conversation_chat_messages' not in st.session_state:
        st.session_state.conversation_chat_messages = []
    if 'chat_active' not in st.session_state:
        st.session_state.chat_active = True
    
    # Sidebar setup
    with st.sidebar:
        st.subheader("💬 Chat Settings")
        role = st.selectbox("Interview Role", ["Candidate", "Interviewer"])
        expertise = st.text_input("Your Expertise Area", placeholder="e.g., Python, Machine Learning, DevOps", value="Software Engineering")
        
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.conversation_chat_messages = []
            st.rerun()
    
    # Chat display area with scrollable messages
    st.markdown("""
    <style>
    .chat-container {
        height: 500px;
        overflow-y: auto;
        border: 2px solid #c44900;
        border-radius: 10px;
        padding: 15px;
        background-color: #04151f;
    }
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 10px;
    }
    .user-message-content {
        background-color: #c44900;
        color: #efd6ac;
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        border-bottom-right-radius: 3px;
        word-wrap: break-word;
    }
    .bot-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .bot-message-content {
        background-color: #183a37;
        color: #efd6ac;
        padding: 10px 15px;
        border-radius: 15px;
        max-width: 70%;
        border-bottom-left-radius: 3px;
        word-wrap: break-word;
        border: 1px solid #c44900;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display chat messages
    chat_placeholder = st.container()
    with chat_placeholder:
        for message in st.session_state.conversation_chat_messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message"><div class="user-message-content">👤 {message["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message"><div class="bot-message-content">🤖 {message["content"]}</div></div>', unsafe_allow_html=True)
    
    # Show initial prompt if no messages
    if not st.session_state.conversation_chat_messages:
        st.info("💡 Ask me any professional interview question! For example:\n- 'What is your experience with microservices?'\n- 'Tell me about a time you solved a difficult problem'\n- 'What are your strengths as a developer?'")
    
    # Chat input and send
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        user_input = st.text_input(
            "Ask a question:",
            placeholder="Type your professional interview question...",
            label_visibility="collapsed",
            key="chat_user_input"
        )
    
    with col2:
        if st.button("✅ Send", use_container_width=True):
            if user_input.strip():
                # Add user message
                st.session_state.conversation_chat_messages.append({
                    "role": "user",
                    "content": user_input
                })
                
                # Build context for the response
                system_prompt = f"""You are a professional interview assistant. You are having a conversation with a candidate. 
Your role is to answer their professional interview questions thoughtfully and helpfully.

Candidate's expertise: {expertise}
Interview format: Conversational

Provide detailed, professional, and helpful answers to their questions."""
                
                user_prompt = f"{user_input}\n\nPlease provide a thoughtful and professional answer."
                
                try:
                    with st.spinner("💭 Thinking..."):
                        response = st.session_state.llm_manager.generate_response(
                            provider=provider,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            model=model,
                            temperature=temperature,
                            top_p=top_p,
                            max_tokens=max_tokens
                        )
                    
                    if response and response.get("content"):
                        assistant_response = response["content"]
                    else:
                        assistant_response = "I couldn't generate a response. Please try again."
                except Exception as e:
                    logger.error(f"Error generating response: {e}")
                    assistant_response = f"I encountered an error: {str(e)}. Please try again."
                
                # Add assistant response
                st.session_state.conversation_chat_messages.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
                st.rerun()


def analytics_tab():
    """Analytics and statistics tab"""
    st.header("📊 Analytics & Statistics")
    
    # Security statistics
    if st.session_state.security_guard:
        st.subheader("🔒 Security Statistics")
        security_report = st.session_state.security_guard.get_security_report()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Requests", security_report["total_requests"])
        with col2:
            st.metric("Unique Users", security_report["unique_users"])
        with col3:
            st.metric("Blocked Patterns", security_report["blocked_patterns_count"])
    
    # Vector database statistics
    if st.session_state.vector_db:
        st.subheader("🗄️ Vector Database Statistics")
        try:
            db_stats = st.session_state.vector_db.get_stats()
            st.metric("Total Documents", db_stats["total_documents"])
        except Exception as e:
            st.warning(f"Could not retrieve database stats: {e}")
    
    # Conversation history
    st.subheader("📝 Conversation History")
    if st.session_state.conversation_history:
        for i, entry in enumerate(reversed(st.session_state.conversation_history[-10:]), 1):
            with st.expander(f"Entry {i}: {entry.get('domain', 'Unknown')} - {entry.get('technique', 'N/A')}"):
                st.json(entry)
    else:
        st.info("No conversation history yet.")


def security_testing_tab():
    """Security testing tab"""
    st.header("🔒 Security Testing (Jailbreak Tests)")
    st.warning("⚠️ This tab runs security tests to validate the application's security guards.")
    
    if st.button("🚀 Run Jailbreak Tests", type="primary"):
        from tests.jailbreak_tests import JailbreakTester
        
        with st.spinner("Running security tests..."):
            tester = JailbreakTester()
            results_df = tester.run_all_tests()
            
            st.success("✅ Tests completed!")
            st.dataframe(results_df, use_container_width=True)
            
            # Export results
            if st.button("📥 Export Results to Excel"):
                try:
                    filepath = tester.export_results(results_df)
                    st.success(f"✅ Results exported to: {filepath}")
                except Exception as e:
                    st.error(f"Export failed: {e}")


def create_beautiful_card_image(result):
    """Create a beautiful result card matching the HTML design with rounded corners and emojis"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create image with RGBA for transparency support
    img_width, img_height = 900, 600
    img = Image.new('RGBA', (img_width, img_height), color=(4, 21, 31, 255))  # Dark background
    draw = ImageDraw.Draw(img)
    
    # Colors
    teal_accent = (24, 58, 55, 255)  # RGBA
    orange = (196, 73, 0, 255)
    light_text = (239, 214, 172, 255)
    gold = (212, 165, 116, 255)
    
    # Create rounded rectangle background
    corner_radius = 30
    # Draw filled rounded rectangle
    draw.rounded_rectangle([corner_radius, corner_radius, img_width-corner_radius, img_height-corner_radius], 
                          radius=corner_radius, fill=teal_accent, outline=orange, width=5)
    
    # Calculate usable center area (accounting for corner radius padding)
    usable_center_x = img_width // 2
    
    # Load serif fonts
    font_paths = [
        "C:\\Windows\\Fonts\\georgia.ttf",
        "C:\\Windows\\Fonts\\times.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Georgia.ttf",
    ]
    
    title_font = None
    name_font = None
    label_font = None
    value_font = None
    
    for font_path in font_paths:
        try:
            title_font = ImageFont.truetype(font_path, 48)
            name_font = ImageFont.truetype(font_path, 46)
            label_font = ImageFont.truetype(font_path, 22)
            value_font = ImageFont.truetype(font_path, 54)
            break
        except:
            continue
    
    if not title_font:
        try:
            title_font = ImageFont.truetype("georgia.ttf", 48)
            name_font = ImageFont.truetype("georgia.ttf", 46)
            label_font = ImageFont.truetype("georgia.ttf", 22)
            value_font = ImageFont.truetype("georgia.ttf", 54)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
    
    y_pos = 90
    
    # Title - using stars instead of sparkles for better emoji support
    title_text = "★ INTERVIEW EXCELLENCE ★"
    draw.text((usable_center_x, y_pos), title_text, font=title_font, fill=gold, anchor="mm")
    y_pos += 60
    
    # Separator star
    draw.text((usable_center_x, y_pos), "★", font=label_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Name
    draw.text((usable_center_x, y_pos), result['name'], font=name_font, fill=orange, anchor="mm")
    y_pos += 50
    
    # Position
    draw.text((usable_center_x, y_pos), f"Position: {result['position']}", font=label_font, fill=light_text, anchor="mm")
    y_pos += 50
    
    # Score (large and bold)
    draw.text((usable_center_x, y_pos), f"{result['mock_interview_score']}%", font=value_font, fill=orange, anchor="mm")
    y_pos += 60
    
    # Level
    level_text = f"Level: {result['improvement_level']} ★"
    draw.text((usable_center_x, y_pos), level_text, font=label_font, fill=gold, anchor="mm")
    y_pos += 35
    
    # Skills
    skills_text = " • ".join(result['skills_tested'][:2])
    if len(result['skills_tested']) > 2:
        skills_text += " •••"
    draw.text((usable_center_x, y_pos), f"Skills: {skills_text}", font=label_font, fill=light_text, anchor="mm")
    y_pos += 45
    
    # Footer - using arrows instead of rockets
    footer_text = ">> Keep Learning • Keep Growing <<"
    draw.text((usable_center_x, y_pos), footer_text, font=label_font, fill=orange, anchor="mm")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes
    """Create a beautiful, animated result card as an image using PIL with LLM-generated design elements"""
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create image with higher quality
    img_width, img_height = 1400, 900
    img = Image.new('RGB', (img_width, img_height), color='#04151f')
    draw = ImageDraw.Draw(img)
    
    # Colors - enhanced palette
    dark_bg = '#04151f'
    teal_accent = '#183a37'
    orange = '#c44900'
    light_text = '#efd6ac'
    gold = '#d4a574'
    
    # Draw gradient-like background with layered rectangles
    teal_color = tuple(int(teal_accent[i:i+2], 16) for i in (1, 3, 5))
    dark_color = tuple(int(dark_bg[i:i+2], 16) for i in (1, 3, 5))
    
    # Main section with accent border
    border_color = tuple(int(orange[i:i+2], 16) for i in (1, 3, 5))
    gold_color = tuple(int(gold[i:i+2], 16) for i in (1, 3, 5))
    
    # Draw background
    draw.rectangle([40, 40, img_width-40, img_height-40], fill=teal_color)
    
    # Load serif fonts - elegant and professional
    font_paths = [
        "C:\\Windows\\Fonts\\georgia.ttf",  # Georgia on Windows
        "C:\\Windows\\Fonts\\times.ttf",    # Times New Roman
        "C:\\Windows\\Fonts\\garamond.ttf", # Garamond
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Georgia.ttf",
        "/System/Library/Fonts/Garamond.ttc",
    ]
    
    title_font = None
    name_font = None
    label_font = None
    value_font = None
    
    for font_path in font_paths:
        try:
            title_font = ImageFont.truetype(font_path, 70)
            name_font = ImageFont.truetype(font_path, 50)
            label_font = ImageFont.truetype(font_path, 32)
            value_font = ImageFont.truetype(font_path, 60)
            break
        except:
            continue
    
    # Fallback to serif fonts
    if not title_font:
        try:
            title_font = ImageFont.truetype("georgia.ttf", 70)
            name_font = ImageFont.truetype("georgia.ttf", 50)
            label_font = ImageFont.truetype("georgia.ttf", 32)
            value_font = ImageFont.truetype("georgia.ttf", 60)
        except:
            title_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()
    
    text_color = tuple(int(light_text[i:i+2], 16) for i in (1, 3, 5))
    orange_color = tuple(int(orange[i:i+2], 16) for i in (1, 3, 5))
    gold_text = gold_color
    
    y_pos = 100
    
    # Title with decorative elements
    draw.text((img_width//2, y_pos), "✨ INTERVIEW EXCELLENCE ✨", font=title_font, fill=gold_text, anchor="mm")
    y_pos += 90
    
    # Decorative line
    draw.line([(150, y_pos), (img_width-150, y_pos)], fill=orange_color, width=3)
    y_pos += 40
    
    # Candidate Name - prominently displayed
    draw.text((img_width//2, y_pos), result['name'].upper(), font=name_font, fill=orange_color, anchor="mm")
    y_pos += 70
    
    # Position
    draw.text((img_width//2, y_pos), f"Position Applied: {result['position']}", font=label_font, fill=gold_text, anchor="mm")
    y_pos += 80
    
    # Decorative line
    draw.line([(150, y_pos), (img_width-150, y_pos)], fill=orange_color, width=2)
    y_pos += 50
    
    # Mock Interview Score - Large and prominent
    draw.text((img_width//2, y_pos), "PERFORMANCE SCORE", font=label_font, fill=text_color, anchor="mm")
    y_pos += 70
    
    score_text = f"{result['mock_interview_score']}%"
    draw.text((img_width//2, y_pos), score_text, font=value_font, fill=orange_color, anchor="mm")
    y_pos += 90
    
    # Improvement level with visual indicator
    draw.text((img_width//2, y_pos), f"Level: {result['improvement_level']} ⭐", font=label_font, fill=gold_text, anchor="mm")
    y_pos += 70
    
    # Skills tested
    skills_text = " • ".join(result['skills_tested'][:4])
    if len(result['skills_tested']) > 4:
        skills_text += " •••"
    draw.text((img_width//2, y_pos), f"Skills: {skills_text}", font=label_font, fill=text_color, anchor="mm")
    y_pos += 70
    
    # Footer - motivational message
    draw.line([(150, y_pos), (img_width-150, y_pos)], fill=orange_color, width=2)
    y_pos += 30
    draw.text((img_width//2, y_pos), "🚀 Keep Learning • Keep Growing 🚀", font=label_font, fill=gold_text, anchor="mm")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


def visual_tools_tab():
    """Visual tools tab with shareable result cards"""
    st.header("🎨 Visual Results & Analytics")
    st.markdown("Create and share beautiful interview performance cards.")
    
    # Check if mock interview has been completed
    if 'mock_interview_score' not in st.session_state or st.session_state.mock_interview_score is None:
        st.info("📝 **To access Visual Tools, please complete a Mock Interview first!**")
        st.write("Here's how to get started:")
        st.write("1. Go to the **Mock Interview** tab")
        st.write("2. Configure your interview settings (domain, difficulty, etc.)")
        st.write("3. Complete the mock interview by answering all questions")
        st.write("4. Your results will automatically populate here!")
        st.markdown("---")
        st.write("Once you've completed a mock interview, you'll be able to create and download beautiful result cards to share your achievement! 🎉")
        return
    
    # Initialize result data in session state if not exists
    if 'interview_results' not in st.session_state:
        st.session_state.interview_results = None
    if 'result_card_image' not in st.session_state:
        st.session_state.result_card_image = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Interview Results")
        result_name = st.text_input("Your Name", placeholder="e.g., John Doe", key="visual_result_name")
        
        # Pre-fill position from mock interview domain if available
        position_default = st.session_state.prefill_position if 'prefill_position' in st.session_state else ""
        position_applied = st.text_input("Position Applied", placeholder="e.g., Senior Software Engineer", key="visual_position", value=position_default)
        
        # Try to get mock interview score from session state or pre-fill
        if 'prefill_mock_score' in st.session_state:
            mock_score_default = st.session_state.prefill_mock_score
        elif st.session_state.mock_interview_score is not None:
            mock_score_default = st.session_state.mock_interview_score
        else:
            mock_score_default = 80
        mock_interview_score = st.slider("Mock Interview Score (%)", 0, 100, mock_score_default, key="visual_mock_score")
        
        # Pre-fill improvement level from mock interview difficulty if available
        if 'prefill_improvement' in st.session_state:
            improvement_default = st.session_state.prefill_improvement
            improvement_idx = ["Beginner", "Intermediate", "Advanced", "Expert"].index(improvement_default) if improvement_default in ["Beginner", "Intermediate", "Advanced", "Expert"] else 0
        else:
            improvement_idx = 0
        improvement_level = st.selectbox("Improvement Level", ["Beginner", "Intermediate", "Advanced", "Expert"], index=improvement_idx, key="visual_improvement")
        
        # Pre-fill skills from mock interview if available
        if 'prefill_skills' in st.session_state:
            skills_default = st.session_state.prefill_skills
        else:
            skills_default = ["System Design", "Problem Solving"]
        skills_tested = st.multiselect(
            "Skills Tested",
            ["Python", "JavaScript", "System Design", "Database", "Problem Solving", 
             "Communication", "Leadership", "Teamwork", "AWS", "Docker", "React", "Node.js"],
            default=skills_default,
            key="visual_skills"
        )
        
        if st.button("🎨 Generate Result Card", type="primary", use_container_width=True):
            st.session_state.interview_results = {
                "name": result_name or "Candidate",
                "position": position_applied or "Position",
                "mock_interview_score": mock_interview_score,
                "improvement_level": improvement_level,
                "skills_tested": skills_tested if skills_tested else ["Skills"]
            }
            try:
                # Generate beautiful card for download
                st.session_state.result_card_image = create_beautiful_card_image(st.session_state.interview_results)
                st.success("✅ Beautiful card generated successfully!")
            except Exception as e:
                st.error(f"Error generating card: {e}")
    
    with col2:
        st.subheader("⚙️ Options")
        card_style = st.selectbox("Card Style", ["Modern", "Minimal", "Detailed"])
        show_skills_breakdown = st.checkbox("Show Skills Breakdown", value=True)
        include_date = st.checkbox("Include Date", value=True)
    
    # Display result card
    if st.session_state.interview_results and st.session_state.result_card_image:
        st.divider()
        st.subheader("✨ Your Beautiful Interview Result Card")
        
        # Add animated HTML card
        st.markdown("---")
        
        result = st.session_state.interview_results
        
        # Create animated HTML card
        animated_card_html = f"""
        <style>
            .interview-card {{
                background: linear-gradient(135deg, #183a37 0%, #04151f 100%);
                border: 3px solid #c44900;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                margin: 30px auto;
                box-shadow: 0 10px 40px rgba(196, 73, 0, 0.3);
                animation: slideIn 0.8s ease-out;
                font-family: 'Georgia', 'Garamond', 'Times New Roman', serif;
                color: #efd6ac;
                text-align: center;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .card-title {{
                font-size: 32px;
                font-weight: bold;
                color: #d4a574;
                margin-bottom: 20px;
                animation: fadeIn 1s ease-out;
            }}
            
            .card-name {{
                font-size: 40px;
                color: #c44900;
                font-style: italic;
                margin: 20px 0;
                animation: scaleIn 0.8s ease-out 0.2s both;
            }}
            
            .card-position {{
                font-size: 18px;
                color: #efd6ac;
                margin: 15px 0;
                animation: fadeIn 1s ease-out 0.4s both;
            }}
            
            .card-score {{
                font-size: 60px;
                color: #c44900;
                font-weight: bold;
                margin: 30px 0;
                animation: countUp 2s ease-out 0.6s both;
            }}
            
            .card-level {{
                font-size: 20px;
                color: #d4a574;
                margin: 20px 0;
                animation: fadeIn 1s ease-out 0.8s both;
            }}
            
            .card-skills {{
                font-size: 16px;
                color: #efd6ac;
                margin: 20px 0;
                animation: fadeIn 1s ease-out 1s both;
            }}
            
            .card-footer {{
                font-size: 16px;
                color: #c44900;
                margin-top: 30px;
                font-style: italic;
                animation: fadeIn 1s ease-out 1.2s both;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            
            @keyframes scaleIn {{
                from {{
                    opacity: 0;
                    transform: scale(0.8);
                }}
                to {{
                    opacity: 1;
                    transform: scale(1);
                }}
            }}
            
            @keyframes countUp {{
                from {{
                    opacity: 0;
                    transform: scale(0.5);
                }}
                to {{
                    opacity: 1;
                    transform: scale(1);
                }}
            }}
        </style>
        
        <div class="interview-card">
            <div class="card-title">✨ INTERVIEW EXCELLENCE ✨</div>
            <div class="card-name">{result['name']}</div>
            <div class="card-position">Position: {result['position']}</div>
            <div class="card-score">{result['mock_interview_score']}%</div>
            <div class="card-level">Level: {result['improvement_level']} ⭐</div>
            <div class="card-skills">Skills: {' • '.join(result['skills_tested'][:4])}</div>
            <div class="card-footer">🚀 Keep Learning • Keep Growing 🚀</div>
        </div>
        """
        
        st.markdown(animated_card_html, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Download as PNG", use_container_width=True):
                st.download_button(
                    label="⬇️ Click to Download",
                    data=st.session_state.result_card_image,
                    file_name=f"interview_result_{result['name'].replace(' ', '_')}.png",
                    mime="image/png",
                    use_container_width=True
                )
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.info("📊 Analytics coming soon!")
        with col3:
            if st.button("🔄 Create Another", use_container_width=True):
                st.session_state.interview_results = None
                st.session_state.result_card_image = None
                st.rerun()


if __name__ == "__main__":
    main()
