"""
Simple NLP utilities for skill extraction and resume analysis.
This file was accidentally removed and is being restored with minimal
functionality necessary for the frontend/backend to operate.  It uses
basic keyword matching but can be extended later with spaCy patterns,
word embeddings, or a proper NER model.
"""

from typing import List, Dict

# Predefined skill lists (can be expanded or loaded from file)
TECHNICAL_SKILLS = {
    "Python", "Java", "C++", "SQL", "JavaScript", "React", "Django",
    "Flask", "AWS", "Docker", "Kubernetes", "Linux", "Node.js",
    "HTML", "CSS", "Git", "TensorFlow", "PyTorch", "spaCy", "Pandas",
    "NumPy", "Pandas", "Machine Learning", "Data Science"
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving",
    "adaptability", "creativity", "critical thinking", "time management",
    "work ethic", "collaboration", "conflict resolution", "empathy"
}


# -------------------------
# BASIC TEXT PROCESSING
# -------------------------

def extract_skills_from_text(text: str) -> List[str]:
    """Return a list of skills found in the provided text."""
    if not text:
        return []
    found = set()
    lower = text.lower()

    for skill in TECHNICAL_SKILLS.union(SOFT_SKILLS):
        if skill.lower() in lower:
            found.add(skill)
    return sorted(found)


def extract_ats_keywords(resume_text: str, job_description: str) -> Dict:
    """Compare resume text to job description to compute a simple ATS-like score.

    The function identifies skills present in the job description and then
    checks which of those appear in the resume. It returns matching and
    missing skills separated into "technical" and "soft" categories along
    with a very basic percentage score.
    """
    resume_skills = set(extract_skills_from_text(resume_text))
    jd_skills = set(extract_skills_from_text(job_description))

    matching = {"technical": [], "soft": []}
    missing = {"technical": [], "soft": []}

    for skill in jd_skills:
        target = "technical" if skill in TECHNICAL_SKILLS else "soft"
        if skill in resume_skills:
            matching[target].append(skill)
        else:
            missing[target].append(skill)

    total_jd = len(jd_skills) or 1
    score = int(100 * (len(matching["technical"]) + len(matching["soft"])) / total_jd)

    return {"ats_score": score, "matching": matching, "missing": missing}


def get_skill_recommendations(missing_skills: List[str], language: str = "en") -> List[str]:
    """Generate very basic recommendations for missing skills.

    This is a placeholder; in the full app this would call the LLM or look
    up curated learning resources. For now we simply tell the user to learn
    the missing items.
    """
    if not missing_skills:
        return []
    recs = []
    for skill in missing_skills:
        recs.append(f"Consider learning or highlighting '{skill}' on your resume.")
    return recs


def generate_resume_improvements(resume_text: str, job_description: str) -> Dict:
    """Return a stubbed improvement suggestion structure.

    This basic implementation simply echoes the ATS score and offers a
    generic tip. It can be replaced by an LLM-based reviewer later.
    """
    analysis = extract_ats_keywords(resume_text, job_description)
    return {
        "ats_score": analysis.get("ats_score"),
        "analysis": "Try incorporating more of the job description keywords.",
        "success": True
    }
