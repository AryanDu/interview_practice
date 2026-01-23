"""
Mock Interview tab - Practice with Real Questions
"""
import streamlit as st
from utils.prompts import PromptEngineer
from utils.validators import validate_interview_request


def render_mock_interview_tab(config):
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
        _generate_mock_interview_questions(config, domain, difficulty, question_type, num_questions)
    
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
                _evaluate_mock_interview(config)
        
        # Show answers summary if interview is completed
        if st.session_state.mock_interview_score is not None:
            st.divider()
            st.subheader("📊 Interview Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Mock Interview Score", f"{st.session_state.mock_interview_score}%")
            with col2:
                if st.button("📊 Create Result Card", type="primary", use_container_width=True):
                    st.session_state.prefill_position = st.session_state.mock_interview_domain
                    st.session_state.prefill_mock_score = st.session_state.mock_interview_score
                    st.session_state.prefill_improvement = st.session_state.mock_interview_difficulty
                    st.session_state.prefill_skills = st.session_state.mock_interview_skills
                    st.session_state.active_tab = 5
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


def _generate_mock_interview_questions(config, domain, difficulty, question_type, num_questions):
    """Generate mock interview questions"""
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
                provider=config["provider"],
                system_prompt=prompts["system"],
                user_prompt=modified_user_prompt,
                model=config["model"],
                temperature=config["temperature"],
                top_p=config["top_p"],
                max_tokens=config["max_tokens"]
            )
            response_text = response.get("content")
        
        if response_text:
            # Parse questions from response
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
                        if question:
                            questions.append(question)
            
            if questions:
                st.session_state.mock_interview_questions = questions[:num_questions]
                st.session_state.mock_interview_answers = {i: "" for i in range(len(questions[:num_questions]))}
                st.session_state.mock_interview_current_question = 0
                st.session_state.mock_interview_score = None
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


def _evaluate_mock_interview(config):
    """Evaluate mock interview answers and generate score"""
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
                provider=config["provider"],
                system_prompt="You are an expert interviewer evaluator.",
                user_prompt=evaluation_prompt,
                model=config["model"],
                temperature=0.3,
                top_p=0.9,
                max_tokens=50
            )
            
            score_text = eval_response.get("content", "0").strip()
            import re
            score_match = re.search(r'\d+', score_text)
            if score_match:
                score = int(score_match.group())
                score = min(100, max(0, score))
            else:
                score = 75
            
            st.session_state.mock_interview_score = score
            
            # Extract skills from questions using LLM
            with st.spinner("Analyzing skills tested..."):
                try:
                    skills_prompt = "Based on these interview questions, identify the key skills being tested.\nReturn ONLY a comma-separated list of skills, nothing else.\n\nQuestions:\n"
                    skills_prompt += "\n".join(st.session_state.mock_interview_questions)
                    
                    skills_response = st.session_state.llm_manager.generate_response(
                        provider=config["provider"],
                        system_prompt="You are an expert at identifying technical and professional skills from interview questions.",
                        user_prompt=skills_prompt,
                        model=config["model"],
                        temperature=0.3,
                        top_p=0.9,
                        max_tokens=100
                    )
                    
                    skills_text = skills_response.get("content", "").strip()
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
                            provider=config["provider"],
                            system_prompt="You are an expert at providing ideal interview answers.",
                            user_prompt=ideal_prompt,
                            model=config["model"],
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
