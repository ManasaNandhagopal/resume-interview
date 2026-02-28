"""
SQLAlchemy models for InnoCareer AI app.  Reconstructed after accidental deletion.
Includes user, resume, job description, interview/session/answer, skill gaps,
learning progress, plus helper functions for database initialization.
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

DATABASE_URL = "sqlite:///innovareer_ai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)


# ------------------------------------------
# DATA MODELS
# ------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    language = Column(String, default="en")
    profile_pic = Column(String, nullable=True)
    face_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user")
    sessions = relationship("InterviewSession", back_populates="user")
    skill_gaps = relationship("SkillGap", back_populates="user")
    learn_progress = relationship("LearningProgress", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    file_path = Column(String)
    extracted_text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String)
    mode = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    overall_score = Column(Float, default=0.0)

    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    question_number = Column(Integer)
    question_text = Column(Text)
    category = Column(String)
    difficulty = Column(String)

    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id"))
    answer_text = Column(Text)
    score = Column(Float)
    feedback = Column(Text)
    emotion = Column(Text)
    confidence_level = Column(Float)
    face_verified = Column(Boolean, default=False)

    question = relationship("InterviewQuestion", back_populates="answers")

class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill = Column(String)
    identified_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="skill_gaps")

class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    progress = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="learn_progress")
