"""
Chatbot tab - Conversational Interview Assistant
"""
import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render_chatbot_tab(config):
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
    
    # Chat display area
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
                            provider=config["provider"],
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            model=config["model"],
                            temperature=config["temperature"],
                            top_p=config["top_p"],
                            max_tokens=config["max_tokens"]
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
