"""
Configuration File for InnoCareer AI
"""

# API Configuration
API_HOST = "localhost"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"

# Streamlit Configuration
STREAMLIT_PORT = 8501

# Database Configuration
DATABASE_NAME = "innovareer_ai.db"
DATABASE_URL = f"sqlite:///./{DATABASE_NAME}"

# LLM Configuration
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
OLLAMA_API_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
DEFAULT_MODEL = "mistral"  # Options: mistral, llama3, neural-chat, etc.

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "hi", "ta", "te", "ml"]

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "हिंदी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "ml": "മലയാളം (Malayalam)"
}

# Feature Flags
ENABLE_VOICE = True
ENABLE_WEBCAM = True
ENABLE_CHATBOT = True
ENABLE_EMOTION_DETECTION = True
ENABLE_OFFLINE_MODE = True

# Interview Settings
DEFAULT_INTERVIEW_QUESTIONS = 5
INTERVIEW_TIMEOUT_SECONDS = 300
INTERVIEW_MODES = ["text", "voice", "webcam"]
INTERVIEW_TYPES = ["Technical", "HR", "Behavioral", "Mixed"]

# Voice Settings
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 0.9
STT_TIMEOUT = 30  # Seconds
STT_LANGUAGE = "en-US"

# File Upload Settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# PDF Extraction Settings
MAX_CHARS_TO_EXTRACT = 5000

# NLP Settings
MIN_SKILL_CONFIDENCE = 0.5
NUM_TOP_SKILLS = 10
NUM_RECOMMENDATIONS = 5

# ATS Score Settings
MIN_ATS_SCORE = 0
MAX_ATS_SCORE = 100
ATS_SCORE_FORMULA = "keyword_match"  # Options: keyword_match, neural

# Interview Answer Evaluation
MIN_ANSWER_LENGTH = 20
MAX_ANSWER_LENGTH = 2000
EVALUATION_TIMEOUT = 30

# Emotion Detection Settings
EMOTION_CONFIDENCE_THRESHOLD = 0.5
CENTER_FACE_DETECTION = True

# Learning Resources
RESOURCE_LANGUAGE_SUPPORT = {
    "en": ["YouTube", "Khan Academy", "Coursera", "Udemy"],
    "hi": ["YouTube", "Khan Academy", "Swayam"],
    "ta": ["YouTube", "Local Tamil Content"]
}

# Performance Thresholds
EXCELLENT_THRESHOLD = 80
GOOD_THRESHOLD = 60
NEEDS_PRACTICE_THRESHOLD = 40

# Cache Settings
CACHE_TTL = 3600  # Cache time to live in seconds
CACHE_ENABLED = True

# Debug Settings
DEBUG_MODE = False
LOG_LEVEL = "INFO"
