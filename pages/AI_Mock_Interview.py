import streamlit as st
import time 
from interview_generator import generate_interview_questions
from interview_evaluator import evaluate_complete_interview
from components.voice_component.voice import voice_component
from streamlit_autorefresh import st_autorefresh
from streamlit_mic_recorder import mic_recorder
from Analyzer import extract_text_from_pdf
from theme import inject_3d_theme
def show_interview_page():

    inject_3d_theme()
    def local_css(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    try:
        local_css("style.css")
    except FileNotFoundError:
        pass 
        
    # ---------------------------------------------------------
    # Session State Initialization
    # ---------------------------------------------------------
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    if "job_description" not in st.session_state:
        st.session_state.job_description = ""

    if "interview_stage" not in st.session_state:
        st.session_state.interview_stage = "upload"
    
    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "current_question" not in st.session_state:
        st.session_state.current_question = 0    

    if "answers" not in st.session_state:
        st.session_state.answers = []    

    # ---------------------------------------------------------
    # 🎤 MAIN TITLE & DESCRIPTION 
    # ---------------------------------------------------------
    if st.session_state.interview_stage == "setup":
        st.markdown('<h1 class="setup-heading">🎤 AI Mock Interview</h1>', unsafe_allow_html=True)
        st.markdown('<p class="setup-subheading">Practice AI-generated interview questions based on your resume.</p>', unsafe_allow_html=True)

    elif st.session_state.interview_stage == "question":
        pass

    else:
        _, main_content_col, _ = st.columns([0.1, 0.8, 0.1])
        with main_content_col:
            st.title("🎤 AI Mock Interview")
            st.write("Practice AI-generated interview questions based on your resume.")

    # ---------------------------------------------------------
    # STAGE 1: Resume & Job Description Upload
    # ---------------------------------------------------------
    if st.session_state.interview_stage == "upload":
        _, main_content_col, _ = st.columns([0.1, 0.8, 0.1])
        with main_content_col:
            
            input_col1, input_col2 = st.columns(2, gap="large")
            with input_col1:
                st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                st.markdown('<p class="section-header">📤 Upload Resume </p>', unsafe_allow_html=True)
                uploaded_resume = st.file_uploader(
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
                    height=82, 
                    placeholder="Paste Target Job Description....",
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)


           
                
            col1,col2=st.columns([0.8,0.2])
            with col2:
                if st.button("Continue ➜",width="stretch"):
                    if not  uploaded_resume and job_description.strip():
                        st.warning ("Please upload your resume")
                        st.stop()
                    if not job_description.strip() :
                        st.warning("Please paste job description")  
                        st.stop() 
                    with st.spinner("Reading Resume..."):
                        resume_text = extract_text_from_pdf(uploaded_resume)
                        st.session_state.resume_text = resume_text
                        st.session_state.job_description = job_description
                    
                    
                    st.session_state.interview_stage = "setup"

                    st.rerun()
        
    # ---------------------------------------------------------
    # STAGE 2: Interview Setup 
    # ---------------------------------------------------------
    if st.session_state.interview_stage == "setup":
        
        

        
        left_space, center_card, right_space = st.columns([0.12, 0.76, 0.12])

        with center_card:
            with st.container(border=True):
                
                target_role = st.text_input("💼 Target Role", placeholder="Example: Data Scientist")
                
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    difficulty = st.selectbox("🎯 Difficulty", ["Select", "Easy", "Medium", "Hard"])
                    time_limit = st.selectbox("⏱ Total Interview Time", ["Select", 10, 20, 30], help="Time in minutes")
                with sub_col2:
                    num_questions = st.selectbox("📋 Number of Questions", ["Select", 5, 10, 15]) 
                    interview_type = st.selectbox("🧠 Interview Type", ["Select", "Technical", "HR", "Behavioral", "Mixed"])

                st.write("") 
                
                start_btn = st.button("🚀 Start Interview", width="stretch")

            if start_btn:
                st.session_state.question_start_time = time.time()
                if not target_role.strip():
                    st.warning("Enter Target Role")
                    st.stop()

                if difficulty == "Select" or num_questions == "Select" or time_limit == "Select" or interview_type == "Select":
                    st.warning("Please fill all the fields ")
                    st.stop()
                   
                st.session_state.target_role = target_role
                st.session_state.difficulty = difficulty
                st.session_state.num_questions = num_questions
                st.session_state.interview_type = interview_type
                
                with st.spinner("Generating Interview Questions..."):
                    try:
                        st.session_state.questions = generate_interview_questions(
                            resume_text=st.session_state.resume_text,
                            job_description=st.session_state.job_description,
                            target_role=target_role,
                            difficulty=difficulty,
                            interview_type=interview_type,
                            num_questions=num_questions
                        )
                    except Exception as e:
                        st.error("Your quota exceeded. Please try again later.")
                        st.stop()

                st.session_state.answers = [""] * len(st.session_state.questions)
                
                if num_questions == 5:
                    st.session_state.total_time = 10 * 60
                elif num_questions == 10:
                    st.session_state.total_time = 20 * 60
                else:
                    st.session_state.total_time = 30 * 60

                st.session_state.interview_start_time = time.time()
                st.session_state.current_question = 0
                st.session_state.interview_stage = "question"
                st.rerun()
    # ---------------------------------------------------------
    # STAGE 3: Interview Questions 
    # ---------------------------------------------------------
    elif st.session_state.interview_stage == "question":  
        st_autorefresh(interval=3000, key="timer_refresh")

        # Timer calculation
        elapsed = int(time.time() - st.session_state.interview_start_time)
        remaining = max(0, st.session_state.total_time - elapsed)
        minutes = remaining // 60
        seconds = remaining % 60
        progress = (st.session_state.current_question + 1) / len(st.session_state.questions)

        st.markdown('<p class="interview-mini-header">🎙️ Interview Live Session</p>', unsafe_allow_html=True)

       
        _, header_col1, header_col2,_ = st.columns([0.1,0.62, 0.18,0.1])
        with header_col1:
            st.caption(f"🚀 Overall Progress: {int(progress * 100)}%")
            st.progress(progress)
        with header_col2:
            time_str = f"⏱️ {minutes:02}:{seconds:02}"
            if remaining <= 120:
                st.error(f"Time Left: {time_str}")
            else:
                st.success(f"Time Left: {time_str}")

        st.write("") 

        
        _, main_content_col, _ = st.columns([0.1, 0.8, 0.1])

        with main_content_col:
            # No. of Present Question
            st.markdown(f"### 📋 Question {st.session_state.current_question + 1} of {st.session_state.num_questions}")
            
            st.markdown(f'<div class="question-card">💬 {st.session_state.questions[st.session_state.current_question]}</div>',unsafe_allow_html=True)

            st.markdown("#### ✍️ Your Answer")
            
            
            result = voice_component(
                key=f"voice_{st.session_state.current_question}",
                default_text=st.session_state.answers[st.session_state.current_question],
            )

            
            if result and isinstance(result, dict):
                if result.get("type") == "tab_switch":
                    st.warning("⚠️ Tab switch detected! Moving to next question.")
                    last_question = (st.session_state.current_question == len(st.session_state.questions) - 1)
                    if last_question:
                        st.session_state.interview_stage = "result"
                    else:
                        st.session_state.current_question += 1
                    st.rerun()
                elif result.get("type") == "text":
                    st.session_state.answers[st.session_state.current_question] = result["value"]

            answer = st.session_state.answers[st.session_state.current_question]

            st.write("") 

            
            btn_col1, btn_col2 = st.columns([0.8,0.2])

            with btn_col2:
                last_question = (st.session_state.current_question == len(st.session_state.questions) - 1)
                button_name = "Finish Interview ✅" if last_question else "Next Question ➡"

                if st.button(button_name, width="stretch"):
                    st.session_state.answers[st.session_state.current_question] = answer
                    if last_question:
                        st.session_state.interview_stage = "result"
                    else:
                        st.session_state.current_question += 1
                    st.rerun()

        if remaining == 0:
            st.warning("⏰ Interview Time Over!")

            st.session_state.interview_stage = "result"
            st.rerun()

    # ---------------------------------------------------------
    # STAGE 4: Evaluation Results 
    # ---------------------------------------------------------
    elif st.session_state.interview_stage == "result":
        
       
        _, main_content_col, _ = st.columns([0.1, 0.8, 0.1])
        
        with main_content_col:
           
            st.markdown(
                '<div class="result-success-banner">🎉 Interview Completed Successfully!</div>', 
                unsafe_allow_html=True
            )
            
            if "final_result" not in st.session_state:
                with st.spinner("Evaluating Interview..."):
                    st.session_state.final_result = evaluate_complete_interview(
                        st.session_state.questions,
                        st.session_state.answers
                    )
            
            result = st.session_state.final_result
            
            # 2. Score Metrics Grid 
            st.markdown('<p class="section-title-custom">📊 Performance Breakdown</p>', unsafe_allow_html=True)
            m_col1, m_col2, m_col3, m_col4 = st.columns(4, gap="medium")
            
            with m_col1:
                st.markdown(f'''
                    <div class="score-card overall-card">
                        <p class="score-label">Overall Score</p>
                        <p class="score-value">{result["overall_score"]}</p>
                    </div>
                ''', unsafe_allow_html=True)
                
            with m_col2:
                st.markdown(f'''
                    <div class="score-card">
                        <p class="score-label">Technical</p>
                        <p class="score-value">{result["technical_score"]}</p>
                    </div>
                ''', unsafe_allow_html=True)
                
            with m_col3:
                st.markdown(f'''
                    <div class="score-card">
                        <p class="score-label">Communication</p>
                        <p class="score-value">{result["communication_score"]}</p>
                    </div>
                ''', unsafe_allow_html=True)
                
            with m_col4:
                st.markdown(f'''
                    <div class="score-card">
                        <p class="score-label">Confidence</p>
                        <p class="score-value">{result["confidence_score"]}</p>
                    </div>
                ''', unsafe_allow_html=True)
                
            st.write("") 

            # 3. Insights Matrix (Side-by-Side Strengths & Weaknesses)
            st.markdown('<p class="section-title-custom">💡 Detailed Insights</p>', unsafe_allow_html=True)
            insight_col1, insight_col2 = st.columns(2, gap="large")
            
            with insight_col1:
                strengths_html = "".join([f"<li>{item}</li>" for item in result["strengths"]])
                st.markdown(f'''
                    <div class="insight-box strength-box">
                        <div class="insight-title">🟢 Key Strengths</div>
                        <ul>{strengths_html}</ul>
                    </div>
                ''', unsafe_allow_html=True)

            with insight_col2:
                weaknesses_html = "".join([f"<li>{item}</li>" for item in result["weaknesses"]])
                st.markdown(f'''
                    <div class="insight-box weakness-box">
                        <div class="insight-title">🔴 Areas of Improvement</div>
                        <ul>{weaknesses_html}</ul>
                    </div>
                ''', unsafe_allow_html=True)

            # 4. Actionable Tips Section
            st.write("") 
            tips_html = "".join([f"<li>{item}</li>" for item in result["improvements"]])
            st.markdown(f'''
                <div class="insight-box tips-box">
                    <div class="insight-title">🚀 Actionable Tips to Level Up</div>
                    <ul>{tips_html}</ul>
                </div>
            ''', unsafe_allow_html=True)

            # 5. Overall AI Feedback Summary
            st.write("")
            st.markdown(f'''
                <div class="feedback-summary-box">
                    <strong>AI Review Summary:</strong> {result["overall_feedback"]}
                </div>
            ''', unsafe_allow_html=True)         

            # 6. Bottom Navigation Buttons
            st.write("")
            col1, col2 = st.columns(2, gap="medium")        
            with col1:
                if st.button("🏠 Return Home", width="stretch"):
                    st.session_state.page = "home"
                    st.session_state.interview_stage = "upload"
                    st.session_state.current_question = 0
                    st.session_state.questions = []
                    st.session_state.answers = []
                    st.session_state.pop("final_result", None)
                    st.session_state.pop("question_start_time", None)
                    st.rerun()

            with col2:
                if st.button("🔄 Restart Practice", width="stretch"):
                    st.session_state.interview_stage = "upload"
                    st.session_state.current_question = 0
                    st.session_state.questions = []
                    st.session_state.answers = []
                    st.session_state.pop("final_result", None)
                    st.session_state.pop("question_start_time", None)
                    st.rerun()