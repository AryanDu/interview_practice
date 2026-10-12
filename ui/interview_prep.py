"""
Interview Prep tab - Study Mode
"""
import streamlit as st
import logging
from utils.prompts import PromptEngineer
from utils.validators import validate_interview_request
from utils.cost_calculator import CostCalculator
from chains.interview_chains import InterviewChain

logger = logging.getLogger(__name__)


def render_interview_prep_tab(config):
    """Interview preparation tab"""
    st.markdown(
        '<section class="v2-workspace-intro"><div class="v2-page-kicker">PREPARE WITH CONTEXT</div>'
        '<h1>Interview Prep</h1><p>Build a tailored study pack from a role, CV or job description. The existing generation and validation pipeline is unchanged.</p></section>',
        unsafe_allow_html=True,
    )
    cv_file = st.file_uploader("Upload CV (PDF or TXT)", type=["pdf", "txt"], key="interview_prep_cv")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        domain = st.text_input("Domain/Field", placeholder="e.g., Software Engineering, Data Science")
        difficulty = st.selectbox("Difficulty Level", ["easy", "medium", "hard"], index=1)
        question_type = st.selectbox("Question Type", ["technical", "behavioral", "system_design", "mixed"], index=0)
        num_questions = st.slider("Number of Questions", min_value=1, max_value=20, value=5, step=1)
        
        # Job description for RAG
        job_description = None
        if config["use_rag"]:
            job_description = st.text_area(
                "Job Description (for RAG)",
                placeholder="Paste the job description here...",
                height=200,
                key="interview_prep_rag_job_desc"
            )
    
    with col2:
        persona = None
        if config["technique"] == "role_playing":
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
            user_id=st.session_state.get("auth_user_id", "local-profile")
        )
        
        if not is_safe:
            st.error(f"Security check failed: {security_error}")
            return
        
        # Check for duplicates
        duplicate_found = False
        if config["check_duplicates"] and st.session_state.vector_db:
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
            except Exception:
                logger.exception("Interview duplicate check failed")
                st.warning("Duplicate detection is temporarily unavailable; generation can continue.")
        
        # Generate prompts using selected technique
        prompt_engineer = PromptEngineer()
        
        try:
            if config["technique"] == "zero_shot":
                prompts = prompt_engineer.zero_shot_prompt(domain, difficulty, job_description, question_type)
            elif config["technique"] == "few_shot":
                prompts = prompt_engineer.few_shot_prompt(domain, difficulty, job_description, question_type)
            elif config["technique"] == "chain_of_thought":
                prompts = prompt_engineer.chain_of_thought_prompt(domain, difficulty, job_description, question_type)
            elif config["technique"] == "tree_of_thought":
                prompts = prompt_engineer.tree_of_thought_prompt(domain, difficulty, job_description, question_type)
            elif config["technique"] == "self_consistency":
                prompts = prompt_engineer.self_consistency_prompt(domain, difficulty, job_description, question_type)
            elif config["technique"] == "role_playing":
                prompts = prompt_engineer.role_playing_prompt(domain, difficulty, persona, job_description)
            elif config["technique"] == "structured_output":
                prompts = prompt_engineer.structured_output_prompt(domain, difficulty, "json", job_description)
            elif config["technique"] == "concise":
                prompts = prompt_engineer.concise_prompt(domain, difficulty, job_description)
            elif config["technique"] == "detailed":
                prompts = prompt_engineer.detailed_prompt(domain, difficulty, job_description)
            elif config["technique"] == "interviewer_guidelines":
                prompts = prompt_engineer.interviewer_guidelines_prompt(domain)
            else:
                prompts = prompt_engineer.zero_shot_prompt(domain, difficulty, job_description, question_type)
            
            # Enforce requested number of questions and Q&A format
            include_answers = True
            qa_instruction = (
                f"\n\nIMPORTANT: Generate exactly {num_questions} interview questions and provide a clear answer for each one. "
                "Format each item as a numbered Q&A pair like:\n1. Question?\nAnswer: ...\n2. Question?\nAnswer: ...\n" 
                "Return ONLY the numbered Q&A pairs and nothing else."
            )
            prompts["user"] = prompts.get("user", "") + qa_instruction

            # RAG: Get context from vector database
            rag_context = ""
            if config["use_rag"] and job_description and st.session_state.vector_db:
                try:
                    rag_context = st.session_state.vector_db.get_context_for_rag(
                        job_description=job_description,
                        domain=domain
                    )
                    if rag_context:
                        prompts["user"] = f"Context from similar interview preparations:\n\n{rag_context}\n\n---\n\n{prompts['user']}"
                except Exception:
                    logger.exception("Interview RAG context retrieval failed")
                    st.warning("Retrieved context is temporarily unavailable; continuing without it.")
            
            # Use LangChain if requested
            response = None
            if config["use_langchain"]:
                try:
                    chain = InterviewChain(provider=config["provider"], model=config["model"])
                    # Pass the requested number of questions and request answers (Q&A)
                    result = chain.run_interview_chain(
                        domain,
                        difficulty,
                        job_description,
                        num_questions=num_questions,
                        include_answers=True
                    )
                    response_text = result.get("questions", "No response generated")
                    response = {"content": response_text, "usage": {}}
                except Exception:
                    logger.exception("LangChain question generation failed")
                    st.error("Could not generate the study pack with the selected chain. Try again or choose another method.")
                    response_text = None
            else:
                # Generate response using LLM manager
                with st.spinner("Generating interview questions..."):
                    response = st.session_state.llm_manager.generate_response(
                        provider=config["provider"],
                        system_prompt=prompts["system"],
                        user_prompt=prompts["user"],
                        model=config["model"],
                        temperature=config["temperature"],
                        top_p=config["top_p"],
                        max_tokens=config["max_tokens"],
                        frequency_penalty=config["frequency_penalty"] if config["provider"] == "openai" else None,
                        presence_penalty=config["presence_penalty"] if config["provider"] == "openai" else None
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
                        provider=config["provider"],
                        model=config["model"],
                        usage=response["usage"]
                    )
                    st.markdown("### Cost Information")
                    st.markdown(CostCalculator.format_cost_display(cost_info))
                
                # LLM Validation
                if config["validate_with_llm"] and config["validator_provider"]:
                    with st.spinner("Validating with second LLM..."):
                        try:
                            validation = st.session_state.llm_manager.validate_response(
                                main_provider=config["provider"],
                                validator_provider=config["validator_provider"],
                                main_response=response_text,
                                original_prompt=prompts["user"]
                            )
                            st.markdown("### LLM Validation")
                            st.markdown(validation["validation"])
                        except Exception:
                            logger.exception("Second-model validation failed")
                            st.warning("Second-model validation is unavailable; the original response is still shown.")
                
                # Store in vector database
                if st.session_state.vector_db:
                    try:
                        st.session_state.vector_db.add_interview_prep(
                            domain=domain,
                            difficulty=difficulty,
                            content=response_text,
                            metadata={
                                "technique": config["technique"],
                                "question_type": question_type,
                                "model": config["model"],
                                "provider": config["provider"]
                            }
                        )
                    except Exception:
                        logger.exception("Vector-store write failed")
                        st.warning("The generated pack could not be saved to the optional vector store.")
                
                # Generate image
                if config["generate_image"] and st.session_state.image_generator:
                    with st.spinner("Generating motivational image..."):
                        try:
                            image_result = st.session_state.image_generator.generate_motivational_image()
                            if image_result.get("success"):
                                st.image(image_result["url"], caption="Motivational Image for Interview Prep")
                        except Exception:
                            logger.exception("Optional image generation failed")
                            st.warning("The optional motivational image could not be generated.")
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "type": "interview_prep",
                    "domain": domain,
                    "difficulty": difficulty,
                    "technique": config["technique"],
                    "response": response_text
                })
                
        except Exception:
            logger.exception("Study-pack generation failed")
            st.error("Could not generate the study pack. Please retry or check the deployment logs.")
