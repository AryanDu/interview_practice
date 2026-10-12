"""
Visual Tools tab - Result cards and visual analytics
"""
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import logging
import re
from utils.html_safety import escape_html_text, safe_filename_component

logger = logging.getLogger(__name__)


def _open_mock_interview() -> None:
    st.session_state.active_tab = 2
    st.session_state.v2_workspace_picker = "🎤 Mock Interview"


def render_visual_tools_tab():
    """Visual tools tab with shareable result cards"""
    st.markdown(
        '<section class="v2-workspace-intro"><div class="v2-page-kicker">MAKE PROGRESS VISIBLE</div>'
        '<h1>Visual Results</h1><p>Create a shareable performance card from your completed mock interview. Your original evaluation remains the source of truth.</p></section>',
        unsafe_allow_html=True,
    )
    
    # Check if mock interview has been completed
    if 'mock_interview_score' not in st.session_state or st.session_state.mock_interview_score is None:
        with st.container(border=True):
            st.markdown("### No result card yet — that's the next milestone.")
            st.write("Complete one mock interview first. Its recorded score and skills will populate this page automatically.")
            st.button(
                "Start a mock interview",
                key="v2_visual_start_interview",
                type="primary",
                on_click=_open_mock_interview,
                use_container_width=True,
            )
        return
    
    # Initialize result data
    if 'interview_results' not in st.session_state:
        st.session_state.interview_results = None
    if 'result_card_image' not in st.session_state:
        st.session_state.result_card_image = None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Interview Results")
        result_name = st.text_input("Your Name", placeholder="e.g., John Doe", key="visual_result_name")
        
        position_default = st.session_state.prefill_position if 'prefill_position' in st.session_state else ""
        position_applied = st.text_input("Position Applied", placeholder="e.g., Senior Software Engineer", key="visual_position", value=position_default)
        
        if 'prefill_mock_score' in st.session_state:
            mock_score_default = st.session_state.prefill_mock_score
        elif st.session_state.mock_interview_score is not None:
            mock_score_default = st.session_state.mock_interview_score
        else:
            mock_score_default = 80
        mock_interview_score = st.slider("Mock Interview Score (%)", 0, 100, mock_score_default, key="visual_mock_score")
        
        if 'prefill_improvement' in st.session_state:
            improvement_default = st.session_state.prefill_improvement
            improvement_idx = ["Beginner", "Intermediate", "Advanced", "Expert"].index(improvement_default) if improvement_default in ["Beginner", "Intermediate", "Advanced", "Expert"] else 0
        else:
            improvement_idx = 0
        improvement_level = st.selectbox("Improvement Level", ["Beginner", "Intermediate", "Advanced", "Expert"], index=improvement_idx, key="visual_improvement")
        
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
                "name": (str(result_name or "Candidate").strip()[:80] or "Candidate"),
                "position": (str(position_applied or "Position").strip()[:120] or "Position"),
                "mock_interview_score": int(mock_interview_score),
                "improvement_level": str(improvement_level)[:30],
                "skills_tested": [str(skill).strip()[:60] for skill in skills_tested if str(skill).strip()][:12] or ["Skills"]
            }
            try:
                st.session_state.result_card_image = _create_beautiful_card_image(st.session_state.interview_results)
                st.success("✅ Beautiful card generated successfully!")
            except Exception:
                logger.exception("Visual result-card generation failed")
                st.error("Could not generate the result card. Please check the inputs and try again.")
    
    with col2:
        st.subheader("⚙️ Options")
        card_style = st.selectbox("Card Style", ["Modern", "Minimal", "Detailed"])
        show_skills_breakdown = st.checkbox("Show Skills Breakdown", value=True)
        include_date = st.checkbox("Include Date", value=True)
    
    # Display result card
    if st.session_state.interview_results and st.session_state.result_card_image:
        st.divider()
        st.subheader("✨ Your Beautiful Interview Result Card")
        st.markdown("---")
        
        result = st.session_state.interview_results
        
        # Escape all user/AI-controlled text before inserting it into custom HTML.
        safe_name = escape_html_text(result.get("name", "Candidate"), max_length=80)
        safe_position = escape_html_text(result.get("position", "Position"), max_length=120)
        safe_level = escape_html_text(result.get("improvement_level", "Beginner"), max_length=30)
        safe_skills = escape_html_text(" • ".join(result.get("skills_tested", [])[:4]), max_length=300)

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
            <div class="card-name">{safe_name}</div>
            <div class="card-position">Position: {safe_position}</div>
            <div class="card-score">{result['mock_interview_score']}%</div>
            <div class="card-level">Level: {safe_level} ⭐</div>
            <div class="card-skills">Skills: {safe_skills}</div>
            <div class="card-footer">🚀 Keep Learning • Keep Growing 🚀</div>
        </div>
        """
        
        st.markdown(animated_card_html, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📥 Download as PNG",
                data=st.session_state.result_card_image.getvalue(),
                file_name=f"interview_result_{safe_filename_component(result['name'])}.png",
                mime="image/png",
                use_container_width=True,
                key="download_interview_result_card",
            )
        with col2:
            if st.button("📊 View Analytics", use_container_width=True):
                st.session_state.active_tab = 4
                st.rerun()
        with col3:
            if st.button("🔄 Create Another", use_container_width=True):
                st.session_state.interview_results = None
                st.session_state.result_card_image = None
                st.rerun()


def _create_beautiful_card_image(result):
    """Create a beautiful result card as an image using PIL"""
    img_width, img_height = 900, 600
    img = Image.new('RGBA', (img_width, img_height), color=(4, 21, 31, 255))
    draw = ImageDraw.Draw(img)
    
    teal_accent = (24, 58, 55, 255)
    orange = (196, 73, 0, 255)
    light_text = (239, 214, 172, 255)
    gold = (212, 165, 116, 255)
    
    # Draw rounded rectangle background
    corner_radius = 30
    draw.rounded_rectangle([corner_radius, corner_radius, img_width-corner_radius, img_height-corner_radius], 
                          radius=corner_radius, fill=teal_accent, outline=orange, width=5)
    
    usable_center_x = img_width // 2
    
    # Load fonts
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
    
    # Title
    title_text = "★ INTERVIEW EXCELLENCE ★"
    draw.text((usable_center_x, y_pos), title_text, font=title_font, fill=gold, anchor="mm")
    y_pos += 60
    
    # Separator
    draw.text((usable_center_x, y_pos), "★", font=label_font, fill=gold, anchor="mm")
    y_pos += 50
    
    # Name
    draw.text((usable_center_x, y_pos), result['name'], font=name_font, fill=orange, anchor="mm")
    y_pos += 50
    
    # Position
    draw.text((usable_center_x, y_pos), f"Position: {result['position']}", font=label_font, fill=light_text, anchor="mm")
    y_pos += 50
    
    # Score
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
    
    # Footer
    footer_text = ">> Keep Learning • Keep Growing <<"
    draw.text((usable_center_x, y_pos), footer_text, font=label_font, fill=orange, anchor="mm")
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes
