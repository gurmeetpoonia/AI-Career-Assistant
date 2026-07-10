import streamlit as st

from pages.Resume_upload import show_resume_page
from pages.AI_Mock_Interview import show_interview_page
from pages.analyser_result import show_analysis_result
from theme import inject_3d_theme
inject_3d_theme()
# 1. Page Configuration
st.set_page_config(
    page_icon="📄",
    page_title="AI Resume Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed" 
)\
# 2. Local CSS Injector
def local_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    local_css("style.css")
except FileNotFoundError:
    pass 

# 3. Session State Initialization
if "page" not in st.session_state:
    st.session_state.page = "home"

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.ats_score = 0
    st.session_state.matched_skills = []
    st.session_state.missing_skills = []
    st.session_state.result = {}
    st.session_state.resume_text = ""
    st.session_state.final_verdict = ""
    st.session_state.job_description = ""

# 4. SIDEBAR FEATURES
with st.sidebar:
    st.markdown("### ⚙️ App Controls")
    st.markdown("---")
    
    theme_choice = st.toggle("☀️ Light Mode / 🌙 Dark Mode", value=True)
    
    st.markdown("---")
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

# Dynamic Theme Engine Configuration
if not theme_choice:
    st.markdown('''
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        [data-testid="stSidebar"] {
            background-color: #f1f5f9 !important;
        }
        p, span, li, div {
            color: #1e293b !important;
        }
        </style>
    ''', unsafe_allow_html=True)
    theme_class = "light-mode-active"
else:
    theme_class = "dark-mode-active"

_,main_content_center,_=st.columns([0.1,0.8,0.1])
with main_content_center:
# 5. Routing & Home Page UI
    if st.session_state.page == "home":
        st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)
        
        st.markdown('<div class="header-dots-left"></div>', unsafe_allow_html=True)
        st.markdown('<div class="header-dots-right"></div>', unsafe_allow_html=True)
        
        st.markdown('<h1 class="main-title">🤖 AI Career Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Evaluate your industry fitment and crack technical interviews with precision pipeline models.</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown('<div class="section-header">🛠️ Choose Your Target Module</div>', unsafe_allow_html=True)
        
        mod_col1, mod_col2 = st.columns(2)
        
        with mod_col1:
            with st.container(border=True):
                st.markdown('<div class="card-heading strength" style="font-weight: 700; padding-bottom:10px; margin-bottom:15px;">📄 Resume Intelligence Analyzer</div>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Parse complex resumes into precise the text metrics instantly.</p>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Compare matching vs missing technical skill graphs against descriptions.</p>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Deep-dive feedback system with simulated dynamic ATS grading system.</p>', unsafe_allow_html=True)
                st.write("") 
                
                if st.button("Launch Resume Analyzer", key="btn_resume", use_container_width=True):
                    st.session_state.page = "resume"
                    st.rerun()

        with mod_col2:
            with st.container(border=True):
                st.markdown('<div class="card-heading suggestion" style="font-weight: 700; padding-bottom:10px; margin-bottom:15px;">🤖 AI Voice & Mock Interviewer</div>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Adaptive AI engine generating textual questions based on your domain.</p>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Simulated technical panel assessment with targeted stack evaluation.</p>', unsafe_allow_html=True)
                st.markdown('<p class="bullet-insight-item">✦ Detailed performance report with strengths, flaws, and optimal answers.</p>', unsafe_allow_html=True)
                st.write("") 
                
                if st.button("Launch AI Interview", key="btn_interview", use_container_width=True):
                    st.session_state.page = "interview"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 6. Routing Page Conditions
    elif st.session_state.page == "resume":
        show_resume_page()
    elif st.session_state.page == "analysis_result":
        show_analysis_result()
    elif st.session_state.page == "interview":
        show_interview_page()