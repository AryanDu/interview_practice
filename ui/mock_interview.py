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
            # Parse questions from response - more flexible parsing
            lines = response_text.strip().split('\n')
            questions = []
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and lines that are just whitespace
                if not line:
                    continue
                
                # Try to extract question if line starts with number + period (1., 2., etc.)
                if line and line[0].isdigit():
                    # Remove the numbering (1., 2., etc.)
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        question = parts[1].strip()
                        if question and len(question) > 10:  # Ensure it's a real question
                            questions.append(question)
                # Also accept lines that look like questions (contain ?)
                elif '?' in line and len(line) > 10:
                    questions.append(line)
            
            if questions:
                # Take only the requested number of questions
                st.session_state.mock_interview_questions = questions[:num_questions]
                st.session_state.mock_interview_answers = {i: "" for i in range(len(questions[:num_questions]))}
                st.session_state.mock_interview_current_question = 0
                st.session_state.mock_interview_score = None
                st.session_state.mock_interview_domain = domain
                st.session_state.mock_interview_difficulty = difficulty
                st.success(f"✅ {len(questions[:num_questions])} questions generated! Start answering.")
                st.rerun()
            else:
                # Fallback: if no questions parsed, try to split by sentence
                import re
                sentences = re.split(r'[.!?]+', response_text)
                backup_questions = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15 and '?' in s]
                
                if backup_questions:
                    st.session_state.mock_interview_questions = backup_questions[:num_questions]
                    st.session_state.mock_interview_answers = {i: "" for i in range(len(backup_questions[:num_questions]))}
                    st.session_state.mock_interview_current_question = 0
                    st.session_state.mock_interview_score = None
                    st.session_state.mock_interview_domain = domain
                    st.session_state.mock_interview_difficulty = difficulty
                    st.success(f"✅ {len(backup_questions[:num_questions])} questions parsed! Start answering.")
                    st.rerun()
                else:
                    st.error(f"Failed to parse questions. Please ensure response contains questions.\n\nResponse preview:\n{response_text[:300]}")
        else:
            st.error("Failed to generate questions")
            
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")


def _evaluate_mock_interview(config):
    """Evaluate a mock interview in one LLM call to avoid serial-request delays."""
    import json
    import re

    questions = st.session_state.mock_interview_questions or []
    answers = [
        st.session_state.mock_interview_answers.get(i, "")
        for i in range(len(questions))
    ]
    if not questions:
        st.error("No interview questions found to evaluate.")
        return

    with st.spinner("Evaluating your answers and preparing feedback..."):
        try:
            qa_text = "\n\n".join(
                f"Q{i + 1}: {question}\nCandidate answer: {answer or '[No answer provided]'}"
                for i, (question, answer) in enumerate(zip(questions, answers))
            )
            prompt = f"""Evaluate this candidate's mock interview and return ONLY valid JSON.
Use this exact schema:
{{
  "score": 0,
  "skills": ["Skill 1", "Skill 2"],
  "ideal_answers": ["Ideal answer to question 1", "Ideal answer to question 2"]
}}
Rules:
- score must be an integer from 0 to 100 based on completeness, clarity, technical accuracy, and relevance.
- skills must be a concise list of the main skills tested.
- ideal_answers must contain exactly one useful, concise model answer per question, in the same order.
- If an answer is blank, evaluate it as unanswered; do not assume the candidate answered it.
- Return JSON only, no Markdown fences or extra commentary.

Questions and candidate answers:
{qa_text}"""

            response = st.session_state.llm_manager.generate_response(
                provider=config["provider"],
                system_prompt="You are a fair, constructive expert interview evaluator. Follow the requested JSON schema exactly.",
                user_prompt=prompt,
                model=config["model"],
                temperature=0.2,
                top_p=0.9,
                max_tokens=min(6000, max(1200, 500 * len(questions))),
            )
            raw = response.get("content", "").strip()
            raw = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw, flags=re.IGNORECASE)
            result = json.loads(raw)

            score_value = result.get("score", 0)
            score = min(100, max(0, int(score_value)))
            st.session_state.mock_interview_score = score

            valid_skills = [
                str(skill).strip() for skill in result.get("skills", [])
                if str(skill).strip()
            ]
            st.session_state.mock_interview_skills = valid_skills[:12] or ["Problem Solving"]

            ideal_answers = result.get("ideal_answers", [])
            st.session_state.mock_interview_ideal_answers = {
                i: str(ideal_answers[i]).strip()
                for i in range(min(len(questions), len(ideal_answers)))
                if str(ideal_answers[i]).strip()
            }

            st.success(f"✅ Interview completed! Your Mock Interview Score: **{score}%**")
            if len(st.session_state.mock_interview_ideal_answers) < len(questions):
                st.warning("Score is ready, but some ideal answers were missing from the AI response.")
            st.rerun()

        except Exception as e:
            st.error(f"Error evaluating answers: {e}")
