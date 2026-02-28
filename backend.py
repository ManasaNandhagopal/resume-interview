"""
FastAPI Backend - InnoCareer AI
Handles authentication, data persistance, and API endpoints
Run with: uvicorn backend:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import json
from typing import List, Optional
import os
import traceback

from models import (
    User, Resume, JobDescription, InterviewSession, 
    InterviewQuestion, InterviewAnswer, SkillGap, 
    LearningProgress, get_db, init_db
)
from nlp_utils import extract_ats_keywords, get_skill_recommendations
from llm_utils import (
    generate_interview_questions, evaluate_interview_answer,
    generate_resume_improvements
)

# Initialize FastAPI
app = FastAPI(title="InnoCareer AI Backend", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# ------------------------------------------
# PYDANTIC MODELS (Request/Response)
# ------------------------------------------

class UserSignup(BaseModel):
    email: str
    password: str
    full_name: str
    language: str = "en"
    
class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    language: str
    profile_pic: Optional[str] = None
    created_at: datetime

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
    language: str = "en"

class ResumeAnalysisResponse(BaseModel):
    ats_score: int
    matching_skills: dict
    missing_skills: dict
    recommendations: list
    top_keywords: Optional[list] = None
    suggested_bullets: Optional[list] = None
    formatting_tips: Optional[list] = None
    strengths: Optional[list] = None
    weaknesses: Optional[list] = None
    raw_improvements: Optional[dict] = None

class InterviewSessionRequest(BaseModel):
    session_type: str  # Technical, HR, Mixed
    mode: str  # text, voice, webcam

class InterviewStartRequest(BaseModel):
    user_id: int
    session_type: str
    mode: str
    resume_text: str
    job_description: str
    language: str = "en"
    
class InterviewAnswerRequest(BaseModel):
    session_id: Optional[int] = None
    question_id: int
    answer_text: str
    emotion: Optional[dict] = None
    confidence_level: Optional[float] = None
    face_verified: Optional[bool] = False

# ------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password"""
    return hash_password(plain) == hashed

def extract_pdf_text(file_path: str) -> str:
    """Extract text from PDF"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return ""

# ------------------------------------------
# AUTH ENDPOINTS
# ------------------------------------------

@app.post("/api/auth/signup", response_model=UserResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    """User registration"""
    try:
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = User(
            email=user.email,
            password_hash=hash_password(user.password),
            full_name=user.full_name,
            language=user.language
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            language=new_user.language,
            profile_pic=new_user.profile_pic,
            created_at=new_user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        language=db_user.language,
        profile_pic=db_user.profile_pic,
        created_at=db_user.created_at
    )

# ------------------------------------------
# USER PROFILE ENDPOINTS
# ------------------------------------------

@app.post("/api/user/upload_profile")
async def upload_profile_picture(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload profile picture and update user record"""
    try:
        os.makedirs("profiles", exist_ok=True)
        file_path = f"profiles/user_{user_id}{os.path.splitext(file.filename)[1]}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.profile_pic = file_path
        db.commit()
        return {"message": "Profile picture uploaded", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------
# RESUME ENDPOINTS
# ------------------------------------------

@app.post("/api/resume/upload")
async def upload_resume(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        file_path = f"uploads/{user_id}_{datetime.now().timestamp()}.pdf"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        resume_text = extract_pdf_text(file_path)
        resume = Resume(
            user_id=user_id,
            file_name=file.filename,
            file_path=file_path,
            extracted_text=resume_text
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return {
            "id": resume.id,
            "filename": resume.file_name,
            "text_length": len(resume_text),
            "message": "✅ Resume uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume(request: ResumeAnalysisRequest, db: Session = Depends(get_db)):
    try:
        analysis = extract_ats_keywords(request.resume_text, request.job_description)
        missing_skills = analysis.get("missing", {}).get("technical", []) + analysis.get("missing", {}).get("soft", [])
        recommendations = get_skill_recommendations(missing_skills, request.language)
        return ResumeAnalysisResponse(
            ats_score=analysis.get("ats_score", 0),
            matching_skills={
                "technical": analysis.get("matching", {}).get("technical", []),
                "soft": analysis.get("matching", {}).get("soft", [])
            },
            missing_skills={
                "technical": analysis.get("missing", {}).get("technical", []),
                "soft": analysis.get("missing", {}).get("soft", [])
            },
            recommendations=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume/improve")
def improve_resume(
    user_id: int,
    resume_text: str,
    job_description: str,
    db: Session = Depends(get_db)
):
    try:
        improvements = generate_resume_improvements(resume_text, job_description)
        return {
            "ats_score": improvements.get("ats_score"),
            "analysis": improvements.get("analysis"),
            "success": improvements.get("success")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------
# INTERVIEW ENDPOINTS
# ------------------------------------------

@app.post("/api/interview/start")
def start_interview(
    payload: InterviewStartRequest,
    db: Session = Depends(get_db)
):
    try:
        session = InterviewSession(
            user_id=payload.user_id,
            session_type=payload.session_type,
            mode=payload.mode
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        questions = generate_interview_questions(
            payload.job_description,
            payload.resume_text,
            interview_type=payload.session_type,
            count=5,
            language=payload.language
        )
        question_ids = []
        for idx, q_text in enumerate(questions):
            question = InterviewQuestion(
                session_id=session.id,
                question_number=idx+1,
                question_text=q_text,
                category=payload.session_type,
                difficulty="Medium"
            )
            db.add(question)
            db.flush()
            question_ids.append(question.id)
        db.commit()
        return {
            "session_id": session.id,
            "questions": questions,
            "question_ids": question_ids,
            "total_questions": len(questions),
            "message": "✅ Interview session started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/submit-answer")
def submit_answer(
    payload: InterviewAnswerRequest,
    db: Session = Depends(get_db)
):
    try:
        question = db.query(InterviewQuestion).filter(InterviewQuestion.id==payload.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        evaluation = evaluate_interview_answer(
            question.question_text,
            payload.answer_text,
            interview_type=question.category
        )
        answer = InterviewAnswer(
            question_id=payload.question_id,
            answer_text=payload.answer_text,
            score=evaluation.get("score",50),
            feedback=evaluation.get("feedback",""),
            emotion=payload.emotion,
            confidence_level=payload.emotion.get("confidence") if payload.emotion else None,
            face_verified=payload.face_verified
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return {"answer_id": answer.id, "score": answer.score, "feedback": answer.feedback, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/interview/session/{session_id}")
def get_session_results(session_id: int, db: Session = Depends(get_db)):
    try:
        session = db.query(InterviewSession).filter(InterviewSession.id==session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        answers = db.query(InterviewAnswer).join(InterviewQuestion).filter(InterviewQuestion.session_id==session_id).all()
        scores=[a.score for a in answers]
        overall = sum(scores)/len(scores) if scores else 0
        session.overall_score=overall
        session.completed=True
        db.commit()
        return {"session_id":session.id,"overall_score":overall,"total_questions":len(answers),"individual_scores":scores,
                "answers":[{"question":a.answer_text,"score":a.score,"feedback":a.feedback,"emotion":a.emotion,"face_verified":a.face_verified} for a in answers]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/summary/{user_id}")
def get_dashboard_summary(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id==user_id).first()
        if not user: raise HTTPException(status_code=404, detail="User not found")
        resume_count = db.query(Resume).filter(Resume.user_id==user_id).count()
        sessions = db.query(InterviewSession).filter(InterviewSession.user_id==user_id).all()
        avg_interview_score = 0
        if sessions:
            scores=[s.overall_score for s in sessions if s.overall_score]
            avg_interview_score = sum(scores)/len(scores) if scores else 0
        skill_gaps = db.query(SkillGap).filter(SkillGap.user_id==user_id).all()
        return {"user":{"id":user.id,"email":user.email,"full_name":user.full_name},
                "stats":{"resumes_uploaded":resume_count,"interviews_completed":len([s for s in sessions if s.completed]),
                          "average_interview_score":round(avg_interview_score,1),"skill_gaps_identified":len(skill_gaps)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# health check
@app.get("/api/health")
def health_check():
    return {"status":"✅ Backend is running","timestamp":datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ... rest of endpoints omitted for brevity (they were previously large) ...

@app.get("/api/health")
def health_check():
    return {"status":"✅ Backend is running","timestamp":datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
