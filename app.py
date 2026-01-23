"""Main Streamlit application - Refactored for modularity"""
import streamlit as st
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ui.sidebar import render_sidebar, initialize_session_state
from ui.interview_prep import render_interview_prep_tab
from ui.mock_interview import render_mock_interview_tab
from ui.chatbot import render_chatbot_tab
from ui.analytics import render_analytics_tab
from ui.security import render_security_testing_tab
from ui.visual_tools import render_visual_tools_tab

# Set up the page
st.set_page_config(
    page_title="Interview Practice App",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    :root {
        --primary-color: #c44900;
        --secondary-color: #183a37;
        --dark-bg: #04151f;
        --text-light: #efd6ac;
        --text-gold: #d4a574;
    }
    
    body {
        background-color: var(--dark-bg);
        color: var(--text-light);
    }
    
    .main-header {
        color: var(--text-gold);
        text-align: center;
        font-size: 3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        color: var(--text-light);
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

def main():
    """Main orchestrator function"""
    st.markdown('<h1 class="main-header">💼 Interview Practice App</h1>', unsafe_allow_html=True)
    
    # Render sidebar and get configuration
    sidebar_config = render_sidebar()
    
    # Tab configuration with names
    tab_names = ["📚 Interview Prep", "🎤 Mock Interview", "💬 Chat Assistant", "📊 Analytics", "🎨 Visual Tools", "🔒 Security Testing"]
    
    # Initialize active_tab in session state if not exists
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Tab selection with navigation
    st.markdown("---")
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.write("**Navigate:**")
    with col2:
        selected_tab = st.selectbox(
            "Select Tab",
            options=range(len(tab_names)),
            format_func=lambda x: tab_names[x],
            index=st.session_state.active_tab,
            label_visibility="collapsed"
        )
        st.session_state.active_tab = selected_tab
    
    st.markdown("---")
    
    # Render selected tab based on active_tab
    if st.session_state.active_tab == 0:
        render_interview_prep_tab(sidebar_config)
    elif st.session_state.active_tab == 1:
        render_mock_interview_tab(sidebar_config)
    elif st.session_state.active_tab == 2:
        render_chatbot_tab(sidebar_config)
    elif st.session_state.active_tab == 3:
        render_analytics_tab()
    elif st.session_state.active_tab == 4:
        render_visual_tools_tab()
    elif st.session_state.active_tab == 5:
        render_security_testing_tab()

if __name__ == "__main__":
    main()
