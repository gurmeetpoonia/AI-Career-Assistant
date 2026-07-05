import streamlit as st
import plotly.graph_objects as go
import os
import json
from Analyzer import extract_text_from_pdf 
from ai_feedback import analyze_resume
from report_generator import generate_pdf_report
from ats_score import calculate_ats_score


# Page configuration 
st.set_page_config(
    page_title="AI Resume Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS load karne ke liye function
def local_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    local_css("style.css")
except FileNotFoundError:
    pass 

# Initialize Session State variables
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
    st.session_state.ats_score = 0
    st.session_state.matched_skills = []
    st.session_state.missing_skills = []
    st.session_state.result = {}
    st.session_state.resume_text = ""
    st.session_state.final_verdict = "" 
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
            st.stop()

        st.session_state.analysis_done = True
        st.session_state.resume_text = resume_text
        st.session_state.result = result
        st.session_state.ats_score = calculate_ats_score( resume_text, result["job_skills"],result["matched_skills"]) 
        st.session_state.matched_skills = result["matched_skills"]
        st.session_state.missing_skills = result["missing_skills"]

        
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

if st.session_state.analysis_done:
    ats_score = st.session_state.ats_score
    matched_skills = st.session_state.matched_skills
    missing_skills = st.session_state.missing_skills
    result = st.session_state.result
    resume_text = st.session_state.resume_text

    # ================= ROW 1: ATS SCORE & SKILL GAP MATRIX =================
    score_col, skill_col = st.columns([1, 1.3], gap="medium")

    with score_col:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-header">🎯 ATS Alignment Score</p>', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ats_score,
            number={"suffix": "%", "font": {"color": "#ffffff", "size": 55, "family": "Inter, sans-serif", "weight": "bold"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#8b9bb4", "tickvals": [0, 50, 75, 100]},
                "bar": {"color": "rgba(0,0,0,0)"}, 
                "bgcolor": "rgba(0,0,0,0)", 
                "borderwidth": 0,
                "steps": [
                    {"range": [0, ats_score], "color": "#6366f1" if ats_score < 75 else "#10b981"},
                    {"range": [ats_score, 100], "color": "#1e293b"}
                ]
            }
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=180, 
            margin=dict(l=30, r=30, t=10, b=0),
            transition={'duration': 800, 'easing': 'cubic-in-out'} # Added smooth layout graph easing transition
        )

        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        
        match_status = "Excellent Match" if ats_score >= 90 else "Good Match" if ats_score >= 75 else "Average Match" if ats_score >= 60 else "Low Compatibility"
        status_color = "#10b981" if ats_score >= 90 else "#47B550" if ats_score >= 75 else "#cdef44" if ats_score>=60 else "#ef4444"
        st.markdown(f'<div class="gauge-status-label" style="color: {status_color};">{match_status}</div>', unsafe_allow_html=True)
        st.markdown('<div class="compatibility-badge">✓ Strong ATS Compatibility</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with skill_col:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-header">🔍 Skill Gap Matrix</p>', unsafe_allow_html=True)
        
        sk_col1, sk_col2 = st.columns(2)
        with sk_col1:
            st.markdown(f'<div class="skills-subheading-matched">✅ Matching Keywords ({len(matched_skills)})</div>', unsafe_allow_html=True)
            if matched_skills:
                html_tags = "".join([f'<div class="skill-tag match-tag">{skill}</div>' for skill in matched_skills])
                st.markdown(f'<div class="tag-container">{html_tags}</div>', unsafe_allow_html=True)
            else:
                st.caption("No matching skills identified.")

        with sk_col2:
            st.markdown(f'<div class="skills-subheading-missing">❌ Missing Core Skills ({len(missing_skills)})</div>', unsafe_allow_html=True)     
            if missing_skills:
                html_tags = "".join([f'<div class="skill-tag miss-tag">{skill}</div>' for skill in missing_skills])
                st.markdown(f'<div class="tag-container">{html_tags}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#10b981; font-size:14px; margin-top:12px;">✓ Perfect alignment! No skills missing.</div>', unsafe_allow_html=True)
        
        total_skills = len(matched_skills) + len(missing_skills)
        progress_percentage = (len(matched_skills) / total_skills * 100) if total_skills > 0 else 0
        st.markdown(f"""
            <div class="progress-wrapper">
                <span style="color:#8b9bb4; font-size: 0.85rem;">Match Rate</span>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {progress_percentage}%;"></div></div>
                <span style="color:#ffffff; font-size: 0.85rem; font-weight:600;">{len(matched_skills)} / {total_skills} Skills Matched</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ================= FIXED ROW 2: AI STRATEGIC REVIEW GRID =================
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-header">🤖 AI Strategic Review</p>', unsafe_allow_html=True)
    
    col_str, col_weak, col_sug, col_verdict = st.columns([1, 1, 1, 1.2], gap="medium")

    with col_str:
        strengths_list = "".join([f'<div class="bullet-insight-item">• {item}</div>' for item in result.get("strengths", [])])
        st.markdown(f"""
            <div class="nested-insight-card">
                <h3 class="card-heading strength">🟢 Key Strengths</h3>
                <div class="card-content-scroll">{strengths_list}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_weak:
        weaknesses_list = "".join([f'<div class="bullet-insight-item">• {item}</div>' for item in result.get("weaknesses", [])])
        st.markdown(f"""
            <div class="nested-insight-card">
                <h3 class="card-heading weakness">⚠️ Vulnerabilities</h3>
                <div class="card-content-scroll">{weaknesses_list}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_sug:
        suggestions_list = "".join([f'<div class="bullet-insight-item">• {item}</div>' for item in result.get("suggestions", [])])
        st.markdown(f"""
            <div class="nested-insight-card">
                <h3 class="card-heading suggestion">💡 Optimization Tips</h3>
                <div class="card-content-scroll">{suggestions_list}</div>
            </div>
        """, unsafe_allow_html=True)

    with col_verdict:
        verdict_text = st.session_state.final_verdict
        st.markdown(f"""
            <div class="nested-insight-card verdict-box-premium">
                <span style="font-size:0.8rem; color:#a5b4fc; text-transform:uppercase; letter-spacing:1px; font-weight:600;">🛡️ Final Verdict</span>
                <div class="verdict-highlight-status">{verdict_text}</div>
                <p style="font-size:0.82rem; color:#94a3b8; line-height:1.5; margin-top:5px; border-top: 1px solid #4f46e5; padding-top:10px;">
                    Your profile demonstrates competitive alignments with core technical stacks. Address the identified gap components to maximize screening index scores.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    ai_feedback = f"""
Strengths:
{chr(10).join(result["strengths"])}

Weaknesses:
{chr(10).join(result["weaknesses"])}

Suggestions:
{chr(10).join(result["suggestions"])}

Final Verdict:
{st.session_state.final_verdict}
"""

    generate_pdf_report(
    filename="resume_report.pdf",
    ats_score=round(ats_score),
    matched_skills=matched_skills,
    missing_skills=missing_skills,
    ai_feedback=ai_feedback
)

    # ================= HIGHLIGHTED PREVIEW & DOWNLOAD REPORT =================
    preview_col, download_col = st.columns([1.8, 1], gap="medium")

    with preview_col:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-header">📄 Resume Preview (Highlighted)</p>', unsafe_allow_html=True)

        preview = resume_text

        for skill in matched_skills:
            if skill.strip():
                preview = preview.replace(skill, f'<span class="inline-match">{skill}</span>')

        for skill in missing_skills:
            if skill.strip():
                preview = preview.replace(skill, f'<span class="inline-miss">{skill}</span>')

        st.markdown(f"""<div class="text-preview-window">{preview}</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with download_col:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-header">📥 Download Executive Report</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.85rem; color:#8da2bb; margin-bottom:20px;">Get a comprehensive layout ecosystem PDF structure compiled with strategic keyword indicators.</p>', unsafe_allow_html=True)
        
        

        if os.path.exists("resume_report.pdf"):
            with open("resume_report.pdf", "rb") as pdf_file:
                st.download_button(
            "📥 Download Executive Report",
            data=pdf_file,
            file_name="AI_Resume_Report.pdf",
            mime="application/pdf",
            width="stretch",
        )
        else:
            st.error("❌ PDF report could not be generated.")