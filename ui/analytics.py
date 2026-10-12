"""
Analytics tab - Statistics and reporting
"""
import streamlit as st


def render_analytics_tab():
    """Analytics and statistics tab"""
    st.header("📊 Analytics & Statistics")
    
    # Current mock interview result, when available in this signed-in session.
    if st.session_state.get("mock_interview_score") is not None:
        st.subheader("🎤 Latest Mock Interview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Interview Score", f"{st.session_state.mock_interview_score}%")
        with col2:
            st.metric("Domain", st.session_state.get("mock_interview_domain", "Not recorded"))
        with col3:
            st.metric("Difficulty", st.session_state.get("mock_interview_difficulty", "Not recorded"))
        skills = st.session_state.get("mock_interview_skills", [])
        if skills:
            st.caption("Skills assessed: " + ", ".join(skills))

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
