"""
InnoCareer AI - Complete Frontend with Streamlit
Integrated with FastAPI backend and all features
"""

import streamlit as st
import requests
import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from typing import Dict, List
import base64
import re
import io
import pandas as pd
import numpy as np
from fpdf import FPDF

# timeout used by direct Ollama calls
REQUEST_TIMEOUT = 15

# (some of these imports may not be used immediately but are retained
# to match the additional utilities from the snippets)

# Import local utilities
from nlp_utils import extract_skills_from_text, extract_ats_keywords
from llm_utils import (
    check_ollama_status, generate_interview_questions,
    evaluate_interview_answer, generate_resume_improvements,
    get_interview_prep_tips
)
from voice_vision_utils import (
    tts_engine, stt_engine, emotion_analyzer, webcam_tracker
)

# Configuration
API_BASE_URL = "http://localhost:8000/api"
st.set_page_config(page_title="InnoCareer AI", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.language = "en"
    st.session_state.user = {}

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
    st.session_state.job_description = ""
    st.session_state.analysis_result = None

# Login/signup form widget keys
if "login_email" not in st.session_state:
    st.session_state.login_email = ""
    st.session_state.login_password = ""
    st.session_state.signup_email = ""
    st.session_state.signup_name = ""
    st.session_state.signup_password = ""

if "interview_state" not in st.session_state:
    st.session_state.interview_state = {
        "started": False,
        "session_id": None,
        "questions": [],
        "answers": [],
        "emotions": [],
        "face_verifications": [],
        "current_q": 0,
        "session_type": "mixed",
        "mode": "text",
        "completed": False,
        "scores": []
    }

# ------------------------------------------
# THEME STYLING
# ------------------------------------------

st.markdown("""
<style>
/* Main Background */
.stApp {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 400% 400%;
    animation: gradientMove 15s ease infinite;
}

/* Animated Background */
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Card Styling */
.card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    padding: 30px;
    border-radius: 25px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 20px;
}

/* Button Styling */
.stButton > button {
    background: linear-gradient(90deg, #ff9a9e, #fad0c4);
    border-radius: 12px;
    border: none;
    padding: 12px 30px;
    font-weight: bold;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

/* Progress Bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ff9a9e, #fad0c4);
}

/* Headers */
h1, h2, h3 {
    color: white;
    font-weight: bold;
}

/* Input Fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 12px;
    color: white;
}

.stSelectbox > div > div,
.stRadio > div {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------

def make_api_call(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API call to FastAPI backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from uploaded PDF"""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

# ----------------------------
# Additional local logic helpers
# ----------------------------

def check_ollama():
    """Quick wrapper matching snippet; returns True if service responding."""
    try:
        r = requests.get("http://localhost:11434")
        return r.status_code == 200
    except:
        return False


def ask_ollama(prompt, model="mistral"):
    """Direct call to Ollama API used by chatbot and offline prompts."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=REQUEST_TIMEOUT
        )
        return response.json().get("response", "")
    except Exception as e:
        return f"❌ Ollama Error: {str(e)}"


def analyze_resume_logic(resume_text: str, job_desc: str):
    """Fallback/local analysis emulating the script sample.

    Returns tuple (match_score, required_skills, your_skills, missing_skills).
    """
    # this is static content in the sample; replace with more dynamic if needed
    required_skills = {
        'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'REST APIs', 'Git', 'Agile/Scrum', 'Problem Solving'],
        'passage': ('Based on the job description provided, this role requires a comprehensive skill set across full-stack development. '
                    'JavaScript proficiency is essential for both frontend and backend work, with React experience being crucial for modern UI development. '
                    'Node.js expertise is needed for server-side development, while MongoDB knowledge is important for database management. '
                    'Additionally, RESTful API design, Git version control, Agile methodology, and strong problem-solving capabilities are fundamental to succeed in this position.')
    }
    your_skills = {
        'skills': [
            {'name': 'JavaScript', 'level': 'Expert', 'years': '6+ years'},
            {'name': 'React', 'level': 'Advanced', 'years': '4+ years'},
            {'name': 'Node.js', 'level': 'Advanced', 'years': '5+ years'},
            {'name': 'MongoDB', 'level': 'Intermediate', 'years': '3+ years'},
            {'name': 'Git', 'level': 'Expert', 'years': '7+ years'},
            {'name': 'Problem Solving', 'level': 'Expert', 'years': '8+ years'}
        ],
        'passage': ('Your resume demonstrates strong expertise in core technologies. You have extensive JavaScript experience spanning 6+ years with demonstrated mastery across multiple frameworks. '
                    'React proficiency is evident from your 4+ years of production experience building complex UIs. Your Node.js background shows 5+ years of server-side development work. '
                    'You also have solid MongoDB experience and are highly proficient with Git version control systems. Your problem-solving capabilities are well-documented through your project history and technical achievements.')
    }
    missing_skills = {
        'skills': [
            {'name': 'REST APIs', 'priority': 'High', 'suggestion': 'Complete a REST API design course and build 2-3 API projects'},
            {'name': 'Agile/Scrum', 'priority': 'High', 'suggestion': 'Get Scrum Master certification or work in Agile teams'},
            {'name': 'Docker', 'priority': 'Medium', 'suggestion': 'Learn containerization through Docker tutorials and projects'},
            {'name': 'AWS/Cloud Services', 'priority': 'Medium', 'suggestion': 'Complete AWS fundamentals course and deploy projects to cloud'}
        ],
        'passage': ('To strengthen your candidacy, focus on developing REST API design and implementation skills, as this is critical for the role and not prominently featured in your current resume. '
                    'Agile/Scrum methodology knowledge is important for team collaboration and project management. Additionally, Docker containerization experience would be highly beneficial for modern development workflows. '
                    'Cloud services experience, particularly AWS, is increasingly demanded in the industry. Prioritize REST APIs and Agile certification first as these are explicitly mentioned in the job description.')
    }
    match_score = '82% Match'
    return match_score, required_skills, your_skills, missing_skills


def rebuild_resume_logic():
    """Generate a generic rewritten resume snippet (used when LLM unavailable)."""
    return ("PROFESSIONAL SUMMARY\n" 
            "Results-driven professional with proven expertise in delivering high-impact solutions. Demonstrated ability to lead cross-functional teams and drive measurable business outcomes.\n\n"
            "KEY SKILLS\n"
            "• Technical Leadership & Architecture Design\n"
            "• Agile/Scrum Project Management\n"
            "• Data-Driven Decision Making\n"
            "• Stakeholder Communication\n\n"
            "PROFESSIONAL EXPERIENCE\n\n"
            "Senior Role | Company Name | 2020 - Present\n"
            "• Led team of 8 engineers, increasing productivity by 40%\n"
            "• Implemented CI/CD pipeline, reducing deployment time by 60%\n"
            "• Drove $2M cost savings through process optimization\n\n"
            "Previous Role | Previous Company | 2017 - 2020\n"
            "• Managed 15+ projects with 95% on-time delivery rate\n"
            "• Improved system performance by 35% through optimization\n"
            "• Mentored 5 junior team members\n\n"
            "EDUCATION\n"
            "Bachelor's Degree | University Name | 2017\n\n"
            "CERTIFICATIONS\n"
            "• Relevant Industry Certification\n"
            "• Professional Development Certificate")

# Chatbot helper has its own functions earlier (get_interview_prep_tips etc.)


def show_success_message(message: str):
    """Show success message"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Show error message"""
    st.error(f"❌ {message}")

# ------------------------------------------
# LOGIN PAGE
# ------------------------------------------

def show_login_page():
    """Display login/signup page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; color: white; margin-top: 50px;'>
            <h1>🚀 InnoCareer AI</h1>
            <p style='font-size: 18px;'>AI-Powered Resume Analysis & Interview Practice Engine</p>
            <p style='font-size: 14px; opacity: 0.8;'>Your personal career coach powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Tab for login/signup
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        
        with auth_tab1:
            st.subheader("Welcome Back!")
            email = st.text_input("Email", placeholder="your@email.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("🔓 Sign In", width="stretch"):
                if email and password:
                    result = make_api_call("/auth/login", "POST", {
                        "email": email,
                        "password": password
                    })
                    
                    if "error" not in result:
                        st.session_state.logged_in = True
                        st.session_state.user_id = result.get("id")
                        st.session_state.user_email = result.get("email")
                        st.session_state.user_name = result.get("full_name")
                        st.session_state.language = result.get("language", "en")
                        st.session_state.user = result
                        st.session_state.user = result
                        st.rerun()
                    else:
                        show_error_message("Invalid credentials")
                else:
                    show_error_message("Please enter email and password")
        
        with auth_tab2:
            st.subheader("Create Account")
            signup_email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
            signup_name = st.text_input("Full Name", placeholder="John Doe", key="signup_name")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            
            if st.button("✍️ Create Account", width="stretch"):
                if signup_email and signup_name and signup_password:
                    # always use English internally
                    result = make_api_call("/auth/signup", "POST", {
                        "email": signup_email,
                        "password": signup_password,
                        "full_name": signup_name,
                        "language": "en"
                    })
                    
                    if "error" not in result:
                        show_success_message("Account created! Please log in.")
                        st.rerun()
                    else:
                        show_error_message(result.get("error", "Signup failed"))
                else:
                    show_error_message("Please fill all fields")

# ------------------------------------------
# RESUME ANALYZER
# ------------------------------------------

def show_resume_analyzer():
    """Resume analysis panel"""
    st.header("📄 AI Resume Analyzer + ATS Optimizer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Upload Resume")
        
        # Check Ollama
        ollama_status = check_ollama_status()
        if not ollama_status:
            st.warning("⚠️ Ollama not running. Start with: `ollama serve`")
        
        uploaded_file = st.file_uploader("Choose PDF", type="pdf")
        
        if uploaded_file:
            # extract text locally for immediate display
            st.session_state.resume_text = extract_pdf_text(uploaded_file)
            show_success_message("Resume uploaded!")
            # also send file to backend for storage
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"user_id": st.session_state.user_id}
                resp = requests.post(f"{API_BASE_URL}/resume/upload", files=files, data=data)
                if resp.ok:
                    show_success_message("✅ Resume stored on server")
                else:
                    st.warning(f"Could not store resume: {resp.text}")
            except Exception as e:
                st.warning(f"Resume upload error: {e}")
    
    with col2:
        st.subheader("2️⃣ Paste Job Description")
        st.session_state.job_description = st.text_area(
            "Paste job description here",
            value=st.session_state.job_description,
            height=200,
            key="jd_input"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analysis buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔍 Analyze Resume", width="stretch"):
            if st.session_state.resume_text and st.session_state.job_description:
                with st.spinner("🤖 Analyzing..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE_URL}/resume/analyze",
                            json={
                                "resume_text": st.session_state.resume_text,
                                "job_description": st.session_state.job_description
                            }
                        )
                        if resp.ok:
                            analysis = resp.json()
                            # Normalize keys produced by backend response model
                            if "matching_skills" in analysis:
                                analysis["matching"] = analysis.pop("matching_skills")
                            if "missing_skills" in analysis:
                                analysis["missing"] = analysis.pop("missing_skills")
                        else:
                            raise Exception(resp.text)
                    except Exception as e:
                        st.warning(f"Backend analysis failed, falling back to local: {e}")
                        # simple keyword comparison
                        analysis = extract_ats_keywords(
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        # also run the more verbose sample logic for extra details
                        match_score, req, yours, missing = analyze_resume_logic(
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )
                        # attach verbose info so UI can optionally display it
                        analysis["verbose"] = {
                            "match_score": match_score,
                            "required": req,
                            "your": yours,
                            "missing": missing
                        }
                    
                    # ensure structure exists to avoid KeyError
                    analysis.setdefault("ats_score", 0)
                    analysis.setdefault("matching", {"technical": [], "soft": []})
                    analysis.setdefault("missing", {"technical": [], "soft": []})
                    
                    # Store in session state so it persists across reruns
                    st.session_state.analysis_result = analysis
                    
                    st.divider()
                    st.markdown("## 📊 Analysis Results")
                    st.divider()
                    
                    # ATS Score - larger display
                    col_score, col_progress = st.columns([1, 3])
                    with col_score:
                        st.metric("ATS Score", f"{analysis.get('ats_score',0)}%")
                    with col_progress:
                        st.progress((analysis.get('ats_score',0) or 0) / 100)
                    
                    # Detailed counts
                    tech_matched = len(analysis['matching'].get('technical', []))
                    tech_missing = len(analysis['missing'].get('technical', []))
                    soft_matched = len(analysis['matching'].get('soft', []))
                    soft_missing = len(analysis['missing'].get('soft', []))
                    
                    # Charts: matched vs missing
                    chart_fig = go.Figure(data=[
                        go.Bar(name='Matched', x=['Technical','Soft'], y=[tech_matched, soft_matched]),
                        go.Bar(name='Missing', x=['Technical','Soft'], y=[tech_missing, soft_missing])
                    ])
                    chart_fig.update_layout(barmode='group', title='Skill Match Overview')
                    st.plotly_chart(chart_fig, width="stretch")
                    
                    # Pie chart for ATS score breakdown (matched vs missing)
                    total_skills = tech_matched + tech_missing + soft_matched + soft_missing
                    pie_values = [tech_matched+soft_matched, tech_missing+soft_missing]
                    pie_labels = ['Matched', 'Missing']
                    pie_fig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, hole=.4)])
                    pie_fig.update_layout(title='Overall Skill Coverage')
                    st.plotly_chart(pie_fig, width="stretch")
                    
                    # Matched/Missing list (technical only for brevity)
                    col1_match, col2_match = st.columns(2)
                    
                    with col1_match:
                        st.subheader("✅ Matching Technical Skills")
                        for skill in analysis['matching']['technical'][:10]:
                            st.write(f"• {skill}")
                    
                    with col2_match:
                        st.subheader("❌ Missing Technical Skills")
                        for skill in analysis['missing']['technical'][:10]:
                            st.write(f"• {skill}")
                    
                    # show verbose fallback analysis if available
                    if analysis.get('verbose'):
                        st.markdown("### 🔍 Additional Local Analysis")
                        v = analysis['verbose']
                        st.write(f"**Match Score:** {v.get('match_score')} ")
                        st.write("**Required Skills:**")
                        for sk in v.get('required', {}).get('skills', []):
                            st.write(f"- {sk}")
                        st.write("**Your Skills Summary:**")
                        for sk in v.get('your', {}).get('skills', []):
                            st.write(f"- {sk['name']} ({sk['level']}, {sk['years']})")
                        st.write("**Missing Skills (with suggestions):**")
                        for sk in v.get('missing', {}).get('skills', []):
                            st.write(f"- {sk['name']} ({sk['priority']}): {sk['suggestion']}")
                        st.write(v.get('missing', {}).get('passage', ''))
                    # Automatically get improvement suggestions from LLM
                    if ollama_status:
                        with st.spinner("🧠 Generating detailed feedback..."):
                            improv = generate_resume_improvements(
                                st.session_state.resume_text,
                                st.session_state.job_description
                            )
                        st.markdown("### 📝 AI Feedback & Reasons")
                        st.markdown(improv.get('analysis', 'No additional feedback.'))
                    else:
                        st.info("Start Ollama server to receive detailed feedback.")
            else:
                show_error_message("Upload resume and paste JD first")
    
    with col2:
        if st.button("✨ Improve Resume", width="stretch"):
            if st.session_state.resume_text and st.session_state.job_description:
                if not ollama_status:
                    # fallback local rewrite
                    rewritten = rebuild_resume_logic()
                    st.markdown("### 📝 Offline Resume Rewrite")
                    st.text_area("Copy this version", rewritten, height=350)
                else:
                    with st.spinner("💡 Generating suggestions..."):
                        try:
                            improvements = generate_resume_improvements(
                                st.session_state.resume_text,
                                st.session_state.job_description
                            )
                            st.markdown("### 🎯 Improvement Suggestions")
                            st.metric("Improved ATS Score", f"{improvements['ats_score']}%")
                            st.markdown(improvements['analysis'])
                        except Exception as e:
                            show_error_message(f"Resume improvement failed: {e}")
            else:
                show_error_message("Complete upload and JD first")
    
    with col3:
        if st.button("💼 Get Resources", width="stretch"):
            if st.session_state.analysis_result:
                missing = st.session_state.analysis_result['missing']['technical']
                
                st.markdown("### 📚 Learning Resources")
                for skill in missing[:3]:
                    st.info(f"**{skill}**\n"
                           f"- YouTube: Search '{skill} tutorial'\n"
                           f"- Khan Academy\n"
                           f"- Coursera (Free tier)")
    
    # Display previously saved analysis if available
    if st.session_state.analysis_result and "analysis" not in locals():
        st.divider()
        st.markdown("## 📊 Previous Analysis Results")
        analysis = st.session_state.analysis_result
        
        col_score, col_progress = st.columns([1, 3])
        with col_score:
            st.metric("ATS Score", f"{analysis.get('ats_score',0)}%")
        with col_progress:
            st.progress((analysis.get('ats_score',0) or 0) / 100)
        
        tech_matched = len(analysis['matching'].get('technical', []))
        tech_missing = len(analysis['missing'].get('technical', []))
        soft_matched = len(analysis['matching'].get('soft', []))
        soft_missing = len(analysis['missing'].get('soft', []))
        
        st.subheader("✅/❌ Skills Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tech Matched", tech_matched)
        with col2:
            st.metric("Tech Missing", tech_missing)
        with col3:
            st.metric("Soft Matched", soft_matched)
        with col4:
            st.metric("Soft Missing", soft_missing)

# ------------------------------------------
# INTERVIEW PRACTICE
# ------------------------------------------

def show_interview_practice():
    """Interview practice panel"""
    st.header("🎤 Adaptive AI Interview Practice")
    
    # Interview settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.interview_state["session_type"] = st.selectbox(
            "Interview Type",
            ["Technical", "HR", "Behavioral", "Mixed"]
        )
    
    with col2:
        st.session_state.interview_state["mode"] = st.selectbox(
            "Practice Mode",
            ["Text", "Voice", "Webcam"]
        )
    
    with col3:
        ollama_running = check_ollama_status()
        st.metric("Ollama Status", "✅ Ready" if ollama_running else "❌ Not Running")
    
    # Start interview button
    if not st.session_state.interview_state["started"]:
        if st.button("🚀 Start Interview", width="stretch"):
            if not ollama_running:
                show_error_message("Start Ollama first: ollama serve")
            else:
                with st.spinner("🤖 Starting session and fetching questions..."):
                    resume_text = st.session_state.resume_text or "Software Developer"
                    jd = st.session_state.job_description or "Senior Developer Role"
                    payload = {
                        "user_id": st.session_state.user_id,
                        "session_type": st.session_state.interview_state["session_type"].lower(),
                        "mode": st.session_state.interview_state["mode"].lower(),
                        "resume_text": resume_text,
                        "job_description": jd,
                        "language": st.session_state.language
                    }
                    try:
                        resp = requests.post(f"{API_BASE_URL}/interview/start", json=payload)
                        data = resp.json()
                    except Exception as e:
                        resp = None
                        data = {}
                    if not resp or not resp.ok or not data.get("questions"):
                        show_error_message("Failed to start interview. Make sure backend is running and Ollama serve is up.")
                    else:
                        questions = data.get("questions", [])
                        qids = data.get("question_ids", [])
                        st.session_state.interview_state["session_id"] = data.get("session_id")
                        st.session_state.interview_state["questions"] = questions
                        st.session_state.interview_state["question_ids"] = qids
                        st.session_state.interview_state["started"] = True
                        st.session_state.interview_state["answers"] = [""] * len(questions)
                        st.session_state.interview_state["emotions"] = [{}] * len(questions)
                        st.session_state.interview_state["face_verifications"] = [None] * len(questions)
                        st.session_state.interview_state["current_q"] = 0
                        st.rerun()
    
    # Question flow
    if st.session_state.interview_state["started"] and not st.session_state.interview_state["completed"]:
        i = st.session_state.interview_state["current_q"]
        questions = st.session_state.interview_state.get("questions", [])

        # Safety: if questions list is empty, prompt to regenerate
        if not questions:
            st.warning("No interview questions available. Click 'Start Interview' to generate questions.")
            if st.button("🔄 Try Generate Questions Again"):
                # reset started flag so user can start again
                st.session_state.interview_state["started"] = False
                st.rerun()
            return

        # Normal flow
        st.markdown(f"### Question {i+1} of {len(questions)}")
        st.info(questions[i])
        # speak the question once per display for voice/webcam modes
        if mode in ["Voice", "Webcam"]:
            keyname = f"spoken_{i}"
            if not st.session_state.interview_state.get(keyname):
                tts_engine.speak(questions[i])
                st.session_state.interview_state[keyname] = True
        
        # Answer input based on mode
        mode = st.session_state.interview_state["mode"]
        
        if mode == "Text":
            st.session_state.interview_state["answers"][i] = st.text_area(
                "Your Answer",
                value=st.session_state.interview_state["answers"][i],
                height=150,
                key=f"answer_{i}"
            )
        
        elif mode == "Voice":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎤 Record Answer"):
                    with st.spinner("Listening..."):
                        answer_text = stt_engine.listen_from_microphone(timeout=30)
                        if answer_text:
                            st.session_state.interview_state["answers"][i] = answer_text
                            st.rerun()
            
            if st.session_state.interview_state["answers"][i]:
                st.write(f"**You said:** {st.session_state.interview_state['answers'][i]}")
        
        elif mode == "Webcam":
            st.warning("💡 Webcam mode: audio will be recorded and face captured")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎥 Capture Answer", key=f"webcam_rec_{i}"):
                    with st.spinner("Recording audio and detecting face..."):
                        answer_text = stt_engine.listen_from_microphone(timeout=30)
                        emotion = {}
                        face_verified = False
                        # capture a frame and analyze emotion
                        tmp_path = f"temp_face_{i}.jpg"
                        if webcam_tracker.capture_frame(tmp_path):
                            emotion = emotion_analyzer.analyze_emotion(tmp_path)
                            # verify face against stored profile pic if available
                            profile_pic = st.session_state.user.get("profile_pic")
                            if profile_pic:
                                verify = emotion_analyzer.verify_face(profile_pic, tmp_path)
                                face_verified = verify.get("verified", False) if isinstance(verify, dict) else False
                                st.session_state.interview_state["face_verifications"][i] = {
                                    "result": verify,
                                    "verified": face_verified
                                }
                            else:
                                st.info("Upload a profile picture in Settings to enable face verification")
                            try:
                                os.remove(tmp_path)
                            except:
                                pass
                        st.session_state.interview_state["answers"][i] = answer_text
                        st.session_state.interview_state["emotions"][i] = emotion
                        st.session_state.interview_state["last_emotion"] = emotion
                        st.session_state.interview_state["last_face_verified"] = face_verified
                        st.rerun()
            # display captured answer and emotion
            if st.session_state.interview_state["answers"][i]:
                st.write(f"**You said:** {st.session_state.interview_state['answers'][i]}")
                emo = st.session_state.interview_state.get("last_emotion", {})
                if emo:
                    st.write(f"Emotion detected: {emo.get('emotion')} (confidence {emo.get('confidence')})")
                fv = st.session_state.interview_state.get("last_face_verified")
                if fv is not None:
                    st.write(f"Face verification: {'✅ match' if fv else '❌ mismatch'}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if i > 0 and st.button("⬅️ Previous", width="stretch"):
                st.session_state.interview_state["current_q"] -= 1
                st.rerun()
        
        with col2:
            if i < len(questions) - 1:
                if st.button("➡️ Next", width="stretch"):
                    if st.session_state.interview_state["answers"][i].strip():
                        st.session_state.interview_state["current_q"] += 1
                        st.rerun()
                    else:
                        show_error_message("Please answer before proceeding")
        
        with col3:
            if i == len(questions) - 1:
                if st.button("✅ Submit & Evaluate", width="stretch"):
                    with st.spinner("📊 Evaluating..."):
                        scores = []
                        fv_list = st.session_state.interview_state.get("face_verifications", [])
                        for idx, (q, a) in enumerate(zip(questions, st.session_state.interview_state["answers"])):
                            result = evaluate_interview_answer(q, a)
                            score = result.get("score", 50)
                            # penalize if face verification failed
                            if fv_list and idx < len(fv_list) and fv_list[idx] is not None:
                                if not fv_list[idx].get("verified"):
                                    score = score * 0.8  # 20% penalty for mismatch
                            scores.append(score)
                            # send to backend if we have ids
                            qids = st.session_state.interview_state.get("question_ids", [])
                            if st.session_state.interview_state.get("session_id") and idx < len(qids):
                                try:
                                    payload = {
                                        "session_id": st.session_state.interview_state.get("session_id"),
                                        "question_id": qids[idx],
                                        "answer_text": a,
                                        "emotion": st.session_state.interview_state.get("emotions", [None])[idx],
                                        "face_verified": fv_list[idx].get("verified") if fv_list and idx < len(fv_list) and fv_list[idx] is not None else False
                                    }
                                    requests.post(f"{API_BASE_URL}/interview/submit-answer", json=payload)
                                except Exception:
                                    pass
                        
                        st.session_state.interview_state["scores"] = scores
                        st.session_state.interview_state["completed"] = True
                        st.rerun()
    
    # Results display
    if st.session_state.interview_state["completed"]:
        scores = st.session_state.interview_state["scores"]
        avg_score = sum(scores) / len(scores)
        
        st.markdown("### 📊 Interview Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Score", f"{avg_score:.1f}/100")
        with col2:
            st.metric("Total Questions", len(scores))
        with col3:
            performance = "🟢 Excellent" if avg_score >= 70 else "🟡 Good" if avg_score >= 50 else "🔴 Needs Practice"
            st.metric("Performance", performance)
        
        # Display individual scores
        st.subheader("Individual Question Scores")
        for idx, (q, s) in enumerate(zip(st.session_state.interview_state["questions"], scores)):
            with st.expander(f"Q{idx+1}: {q[:60]}..."):
                st.write(f"Answer: {st.session_state.interview_state['answers'][idx]}")
                st.metric("Score", f"{s}/100")
                # emotion if stored
                emo = st.session_state.interview_state.get("emotions", [])[idx] if st.session_state.interview_state.get("emotions") else {}
                if emo:
                    st.write(f"Detected emotion: {emo.get('emotion')} (confidence {emo.get('confidence')})")
                fv = st.session_state.interview_state.get("face_verifications", [None])[idx]
                if fv:
                    # fv is a dict with keys result and verified
                    st.write(f"Face verification: {'✅ match' if fv.get('verified') else '❌ mismatch'}")
        
        # Low score feedback
        if avg_score < 50:
            st.warning("⚠️ You scored below 50%. Here are resources to improve:")
            
            missing_skills = st.session_state.analysis_result['missing']['technical'] if st.session_state.analysis_result else []
            for skill in missing_skills[:3]:
                st.info(f"📚 Learn **{skill}** - YouTube tutorials available")
        
        # Reset button
        if st.button("🔄 Practice Again", width="stretch"):
            st.session_state.interview_state = {
                "started": False,
                "session_id": None,
                "questions": [],
                "answers": [],
                "emotions": [],
                "face_verifications": [],
                "current_q": 0,
                "session_type": "mixed",
                "mode": "text",
                "completed": False,
                "scores": []
            }
            st.rerun()

# ------------------------------------------
# PROGRESS TRACKER
# ------------------------------------------

def show_progress_tracker():
    """Progress tracking dashboard"""
    st.header("📊 Career Progress Tracker")
    
    # Try to fetch summary from backend
    summary = None
    try:
        resp = requests.get(f"{API_BASE_URL}/dashboard/summary/{st.session_state.user_id}")
        if resp.ok:
            summary = resp.json()
    except Exception as e:
        st.warning(f"Could not fetch dashboard data: {e}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    if summary and summary.get("stats"):
        stats = summary.get("stats")
        with col1:
            st.metric("Resumes Analyzed", stats.get("resumes_uploaded", 0))
        with col2:
            st.metric("Interviews Completed", stats.get("interviews_completed", 0))
        with col3:
            st.metric("Skills Identified", stats.get("skill_gaps_identified", 0))
        with col4:
            avg_score = stats.get("average_interview_score")
            st.metric("Avg Interview Score", f"{avg_score:.1f}%" if avg_score is not None else "N/A")
    else:
        with col1:
            st.metric("Resumes Analyzed", "-")
        with col2:
            st.metric("Interviews Completed", "-")
        with col3:
            st.metric("Skills Identified", "-")
        with col4:
            st.metric("Avg Interview Score", "-")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # if no backend summary, fallback to LLM readiness analysis
    resume_text = st.session_state.get("resume_text", "")
    interview_feedback = st.session_state.get("interview_result", "")
    if not summary and (resume_text or interview_feedback):
        if not check_ollama():
            st.warning("LLM not available for readiness analysis.")
        else:
            prompt = f"""
You are a career performance analyst.

Based on the resume and interview evaluation below,
score the candidate out of 100 in these areas:

Technical:
Communication:
Leadership:
Problem Solving:
Adaptability:
Teamwork:

Return strictly in this format:

Technical: XX
Communication: XX
Leadership: XX
Problem Solving: XX
Adaptability: XX
Teamwork: XX

Overall Readiness: XX
1-line Summary:
"""
            prompt += f"\nResume:\n{resume_text[:3000]}"
            prompt += f"\nInterview Feedback:\n{interview_feedback[:2000]}"
            with st.spinner("📈 Analyzing career readiness..."):
                result = ask_ollama(prompt)
            # parse scores
            categories = [
                "Technical",
                "Communication",
                "Leadership",
                "Problem Solving",
                "Adaptability",
                "Teamwork"
            ]
            scores = []
            for cat in categories:
                match = re.search(rf"{cat}:\s*(\d+)", result)
                scores.append(int(match.group(1)) if match else 50)
            overall_match = re.search(r"Overall Readiness:\s*(\d+)", result)
            overall_score = int(overall_match.group(1)) if overall_match else sum(scores)//len(scores)
            # radar chart
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=categories,
                fill='toself',
                name='Skill Profile'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False
            )
            st.plotly_chart(fig, width="stretch")
            st.markdown("### 🚀 Overall Career Readiness")
            st.progress(overall_score / 100)
            st.write(f"**Overall Score: {overall_score}%**")
            for i, cat in enumerate(categories):
                st.write(f"{cat}: {scores[i]}%")
            st.markdown("---")
            st.subheader("📌 AI Summary & Recommendations")
            st.markdown(result)
            # avoid repeating static section
            return
    
    # Skill Radar Chart (static placeholder if not replaced above)
    if st.session_state.analysis_result:
        st.subheader("🎯 Skill Profile")
        
        skills = {
            "Technical": 78,
            "Communication": 72,
            "Leadership": 65,
            "Problem Solving": 85,
            "Adaptability": 70,
            "Teamwork": 80
        }
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=list(skills.values()),
            theta=list(skills.keys()),
            fill='toself',
            name='Your Skills'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")
    
    # Learning pathway
    st.subheader("📚 Recommended Learning Path")
    
    learning_items = [
        ("Python for Data Science", "Intermediate", "15 hours", "🟡"),
        ("REST API Design", "Beginner", "8 hours", "🟢"),
        ("Docker & Kubernetes", "Advanced", "20 hours", "🔴"),
        ("AWS Cloud Services", "Intermediate", "16 hours", "🟡"),
    ]
    
    for item, level, duration, icon in learning_items:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        col1.write(f"{icon} **{item}**")
        col2.write(f"Level: {level}")
        col3.write(f"⏱️ {duration}")
        col4.button("Start", key=item, width="stretch")

# ------------------------------------------
# DASHBOARD
# ------------------------------------------

def show_dashboard():
    """Main dashboard after login"""
    # Sidebar
    with st.sidebar:
        # display profile picture if available
        if st.session_state.user.get("profile_pic"):
            st.image(st.session_state.user.get("profile_pic"), width=100)
        st.write(f"👤 {st.session_state.user_name}")
        st.write(f"📧 {st.session_state.user_email}")
        st.divider()
        
        panel = st.radio(
            "Navigation",
            ["Resume Analyzer", "Interview Practice", "Progress Tracker", "Settings"]
        )
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user = {}
            st.rerun()
    
    # Main content
    if panel == "Resume Analyzer":
        show_resume_analyzer()
    elif panel == "Interview Practice":
        show_interview_practice()
    elif panel == "Progress Tracker":
        show_progress_tracker()
    else:
        st.header("⚙️ Settings")
        user = st.session_state.user
        st.write("### Update Profile")
        if user.get("profile_pic"):
            st.image(user["profile_pic"], width=150, caption="Current profile picture")
        pic = st.file_uploader("Upload profile picture", type=["png","jpg","jpeg"])
        if pic:
            files = {"file": (pic.name, pic.getvalue())}
            data = {"user_id": user["id"]}
            try:
                response = requests.post(f"{API_BASE_URL}/user/upload_profile", files=files, data=data)
                if response.ok:
                    st.success("✅ Profile picture updated")
                    user["profile_pic"] = response.json().get("path")
                    st.session_state.user = user
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Error uploading: {e}")
        
        st.write("---")
        st.write("No other settings available yet.")

# ------------------------------------------
# MAIN APP
# ------------------------------------------

def main():
    """Main app logic"""
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_dashboard()

        # ---- Chatbot helper UI for question guidance ----
        if 'chat_open' not in st.session_state:
            st.session_state.chat_open = False

        # floating chat button/style
        st.markdown("""
        <style>
        #chat-btn {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background-color: #1f77b4;
            color: white;
            padding: 10px 15px;
            border-radius: 50px;
            cursor: pointer;
            font-weight: bold;
            z-index: 100;
        }
        </style>
        <div id="chat-btn">💬 Chat</div>
        """, unsafe_allow_html=True)

        clicked = st.button("💬 Chat")  # fallback for mobile
        if clicked:
            st.session_state.chat_open = not st.session_state.chat_open

        if st.session_state.chat_open:
            st.markdown("### 🤖 Interview Question Helper")
            user_question = st.text_area("Paste your question here:")
            if st.button("Get Guidance"):
                if user_question.strip():
                    prompt = f"""
You are an expert career coach and interviewer.

Analyze the following question and return exactly in this format:

Question: <original question>

1. Input Interpretation: Explain what the question is asking.
2. Learn Objectives: Refer concepts the student should understand to answer well.
3. Simplified Explanation: Explain it in simple English for a student to answer.

Question Text:
{user_question}
"""
                    guidance = ask_ollama(prompt)
                    st.text_area("Chatbot Response", value=guidance, height=250)

if __name__ == "__main__":
    main()
