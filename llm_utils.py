"""
Basic LLM utilities that wrap Ollama API and provide fallback behavior when
the model server is not available.  The original implementation used rich
prompts and JSON parsing; here we recreate a minimal version so that the
frontend and backend continue to function after the accidental rollback.
"""

import requests
import json
import logging
import time
from typing import List, Dict, Optional

from config import OLLAMA_API_URL

# default Ollama model name
MODEL_NAME = "mistral"

# timeout for HTTP calls (seconds)
REQUEST_TIMEOUT = 15

logger = logging.getLogger(__name__)

# ------------------------
# LOW-LEVEL HTTP HELPERS
# ------------------------

def check_ollama_status() -> bool:
    try:
        resp = requests.get(OLLAMA_API_URL.replace("/generate", "/status"), timeout=3)
        return resp.ok
    except Exception:
        return False


def _call_ollama(prompt: str, max_tokens: int = 200, temperature: float = 0.3) -> Optional[str]:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        r = requests.post(OLLAMA_API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # Ollama returns choices list
        return data.get("choices", [{}])[0].get("text")
    except Exception as e:
        logger.warning("Ollama call failed: %s", e)
        return None

# ------------------------
# HIGH-LEVEL FUNCTIONS
# ------------------------

def generate_interview_questions(
    job_description: str,
    resume_text: str,
    interview_type: str = "technical",
    count: int = 5,
    language: str = "en"
) -> List[str]:
    """Generate a list of interview questions using LLM.

    If the Ollama service is unavailable or times out, return a generic
    fallback set of questions based on the type.
    """
    if not check_ollama_status():
        # simple fallback
        base = {
            "technical": [
                "Explain a challenging bug you fixed.",
                "Describe your experience with the primary technology in the JD.",
            ],
            "hr": [
                "Tell me about yourself.",
                "Why do you want this job?",
            ],
            "behavioral": [
                "Describe a time you worked in a team.",
                "Give an example of handling conflict.",
            ],
            "mixed": []
        }
        questions = base.get(interview_type, [])
        # pad to count
        while len(questions) < count:
            questions.append(f"(Additional {interview_type} question placeholder)")
        return questions[:count]

    prompt = (
        f"You are a helpful interview coach.\n"
        f"Generate {count} {interview_type} interview questions tailored to the following job description and resume.\n"
        f"Job Description:\n{job_description}\n"
        f"Resume Text:\n{resume_text}\n"
        f"Return the questions as a JSON array without any commentary."
    )
    text = _call_ollama(prompt, max_tokens=300)
    if not text:
        return generate_interview_questions(job_description, resume_text, interview_type, count, language)

    try:
        questions = json.loads(text)
        if isinstance(questions, list):
            return questions[:count]
    except Exception:
        # split by lines as fallback
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return lines[:count]

    return []


def evaluate_interview_answer(
    question: str,
    answer_text: str,
    interview_type: str = "technical"
) -> Dict:
    """Score the user's answer and provide feedback.

    Returns a dict with keys 'score' (0-100) and 'feedback'.
    """
    if not check_ollama_status():
        # simple heuristic: longer answers score higher
        score = min(100, len(answer_text.split()) * 2)
        return {"score": score, "feedback": "No LLM available; using heuristic scoring."}

    prompt = (
        f"You are an expert interviewer.\n"
        f"Question: {question}\n"
        f"Answer: {answer_text}\n"
        f"Provide a JSON object with 'score' (0-100) and 'feedback' fields."
    )
    text = _call_ollama(prompt, max_tokens=200)
    if not text:
        return {"score": 0, "feedback": "LLM request failed"}

    try:
        result = json.loads(text)
        if "score" in result and "feedback" in result:
            return result
    except Exception:
        pass
    # fallback
    return {"score": 50, "feedback": text}


def generate_resume_improvements(resume_text: str, job_description: str) -> Dict:
    """Produce advice for improving the resume.

    On failure the function returns a simple ATS score calculation.
    """
    if not check_ollama_status():
        from nlp_utils import extract_ats_keywords
        analysis = extract_ats_keywords(resume_text, job_description)
        return {
            "ats_score": analysis.get("ats_score"),
            "analysis": "Add more keywords from the job description and quantify achievements.",
            "success": True,
        }

    prompt = (
        f"You are a resume reviewer.\n"
        f"Provide constructive feedback for improving the resume text below to better match the job description.\n"
        f"Job Description:\n{job_description}\n"
        f"Resume:\n{resume_text}\n"
        f"Return a JSON object with fields 'analysis' (string), 'ats_score' (number 0-100), 'success' (boolean)."
    )
    text = _call_ollama(prompt, max_tokens=300)
    if not text:
        return generate_resume_improvements(resume_text, job_description)
    try:
        data = json.loads(text)
        return data
    except Exception:
        return {"analysis": text, "ats_score": 0, "success": False}


def get_interview_prep_tips() -> List[str]:
    """Return a short list of general interview preparation tips."""
    return [
        "Practice speaking clearly and confidently.",
        "Research the company beforehand.",
        "Prepare a few questions to ask the interviewer.",
        "Dress professionally and arrive early."
    ]
