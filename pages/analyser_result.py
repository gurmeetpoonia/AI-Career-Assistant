import streamlit as st 
import plotly.graph_objects as go
import os
import base64
from report_generator import generate_pdf_report
from theme import inject_3d_theme
inject_3d_theme()
def show_analysis_result():

    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    try:
        local_css("style.css")
    except FileNotFoundError:
        pass 
    
    if not st.session_state.get("analysis_done", False):
        st.warning("Please analyze your resume first.")
        return
    
    if st.session_state.analysis_done:
        ats_score = st.session_state.ats_score
        matched_skills = st.session_state.matched_skills
        missing_skills = st.session_state.missing_skills
        result = st.session_state.result
        resume_text = st.session_state.resume_text
        job_description = st.session_state.job_description
        
        _, main_content_col, _ = st.columns([0.05, 0.9, 0.05])
        
        with main_content_col:
            # ================= MAIN DASHBOARD HEADER =================
            st.markdown('''
                <div class="analysis-header-container">
                    <div class="analysis-badge">🎯 ANALYSIS REPORT</div>
                    <h1 class="analysis-main-title">AI Resume Optimization Insights</h1>
                    <p class="analysis-subtitle">Deep matrix scanning and keyword matching for your target job profile.</p>
                </div>
            ''', unsafe_allow_html=True)

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
                    transition={'duration': 800, 'easing': 'cubic-in-out'}
                )

                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
                
                match_status = "Excellent Match" if ats_score >= 90 else "Good Match" if ats_score >= 75 else "Average Match" if ats_score >= 60 else "Low Compatibility"
                status_color = "#10b981" if ats_score >= 90 else "#47B550" if ats_score >= 75 else "#cdef44" if ats_score>=60 else "#ef4444"
                st.markdown(f'<div class="gauge-status-label" style="color: {status_color};">{match_status}</div>', unsafe_allow_html=True)
                st.markdown('<div class="compatibility-badge">✓ ATS Compatibility Checked</div>', unsafe_allow_html=True)
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
            preview_col, download_col = st.columns([1.3, 1.3], gap="large")

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
                st.markdown('<p class="section-header">📊 Generated Report Preview</p>', unsafe_allow_html=True)
                
                if os.path.exists("resume_report.pdf"):
                    # 1. Pehle PDF ko base64 me convert kiya
                   
                    with open("resume_report.pdf", "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                    
                    # 2. UPPER: Pehle live preview embed hoke show hoga
                    pdf_display = f'''
                        <div class="pdf-preview-container">
                            <iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=1" width="100%" height="300px" style="border:none; border-radius:6px;"></iframe>
                        </div>
                    '''
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    
                    st.write("") 
                    
                    # 3. NEECHE: Preview ke just neeche full-width download button
                    with open("resume_report.pdf", "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Executive Report PDF",
                            data=pdf_file,
                            file_name="AI_Resume_Report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                else:
                    st.error("❌ PDF report could not be generated for preview.")
                    
                st.markdown('</div>', unsafe_allow_html=True)
            