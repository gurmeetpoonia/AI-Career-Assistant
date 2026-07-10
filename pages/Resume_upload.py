import streamlit as st
import plotly.graph_objects as go
import os
import json

from Analyzer import extract_text_from_pdf 
from ai_feedback import analyze_resume
from report_generator import generate_pdf_report
from ats_score import calculate_ats_score
from theme import inject_3d_theme

def show_resume_page():
    
    inject_3d_theme()
    # Custom CSS load karne ke liye function
    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    try:
        local_css("style.css")
    except FileNotFoundError:
        pass 

     # 👑 Centered Layout Wrapper for Premium Look
    _, main_content_col, _ = st.columns([0.05, 0.9, 0.05])
    
    with main_content_col:

    # Top Dot Design Layout element
        st.markdown('<div class="header-dots-left"></div><div class="header-dots-right"></div>', unsafe_allow_html=True)

        # Main Header Section 
        st.markdown('<div class="main-title">📄 AI Resume Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Optimize your resume against ATS algorithms and get instant AI-driven refinement insights.</p>', unsafe_allow_html=True)

        # Layout for inputs (Step 1 & Step 2 Containers)
        input_col1, input_col2 = st.columns(2, gap="large")

        with input_col1:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-header">📤 Upload Document</p>', unsafe_allow_html=True)
            upload_resume = st.file_uploader(
                "Upload Resume (PDF only)",
                type=["pdf"],
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with input_col2:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-header">📑 Target Job Description</p>', unsafe_allow_html=True)
            job_description = st.text_area(
                "Job Description", 
                height=78, 
                placeholder="Paste the target job description here to extract keywords...",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Gradient Primary Action Button
        st.markdown('<div class="btn-container">', unsafe_allow_html=True)
        analyze = st.button("🚀 Analyze Application Profile", width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)
        if analyze:
            if upload_resume is None:
                st.warning("Please upload your resume.")
                st.stop()

            if not job_description.strip():
                st.warning("Please enter Job Description.")
                st.stop()

            with st.spinner("Analyzing Resume..."):
                resume_text = extract_text_from_pdf(upload_resume)
                result = analyze_resume(resume_text, job_description)

                if result["status"] != "success":
                    st.error(result.get("message","Unknown Error"))
                    return

                st.session_state.analysis_done = True
                st.session_state.resume_text = resume_text
                st.session_state.result = result
                st.session_state.ats_score = calculate_ats_score( resume_text, result["job_skills"],result["matched_skills"]) 
                st.session_state.matched_skills = result["matched_skills"]
                st.session_state.missing_skills = result["missing_skills"]
                st.session_state.job_description = job_description
                
                score = st.session_state.ats_score

                if score >= 90:
                    st.session_state.final_verdict = (
                "🌟 Excellent Match – Your resume is highly optimized for this role and is likely to perform very well in ATS screening."
            )

                elif score >= 75:
                    st.session_state.final_verdict = (
                "✅ Good Match – Your resume aligns well with the job description. A few improvements can further strengthen your profile."
            )

                elif score >= 60:
                    st.session_state.final_verdict = (
                "🟡 Average Match – Your resume meets several requirements but is missing some important skills and keywords."
            )

                elif score >= 40:
                    st.session_state.final_verdict = (
                "🟠 Weak Match – Your resume requires significant improvements to better align with the target job."
            )

                else:
                    st.session_state.final_verdict = (
                "🔴 Poor Match – Your resume has low alignment with the job description. Add relevant skills, projects, and experience."
            )

            st.session_state.page = "analysis_result"
            st.rerun()
