# 🚀 InnoCareer AI - Complete Setup & Deployment Guide

## **Project Overview**

InnoCareer AI is an all-in-one AI-powered career development platform featuring:
- ✅ Resume Analysis with ATS Scoring
- ✅ Adaptive Mock Interviews (Text/Voice/Webcam)
- ✅ Emotion Detection & Confidence Analysis
- ✅ Personalized Skill Gap Analysis
- ✅ AI-Powered Learning Pathways
- ✅ Multi-language Support (English, Hindi, Tamil, etc.)
- ✅ Fully Offline Capable (Privacy-First)
- ✅ No Paid APIs Required

---

## **Phase 1: Environment Setup**

### **Step 1A: Install Python & Git**
```bash
# Windows (Recommended: Python 3.10+)
# Download from: https://www.python.org/downloads/
# Make sure to check "Add Python to PATH"

# Verify installation:
python --version
git --version
```

### **Step 1B: Clone or Setup Project**
```bash
# Navigate to your project directory
cd c:\Users\user\Documents\InnoCareer-AI-Hackathon

# Verify project structure:
dir
# Should show: app.py, backend.py, models.py, requirements.txt, etc.
```

### **Step 1C: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate

# Windows PowerShell:
venv\Scripts\Activate.ps1
# (If error, run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser)

# Verify activation (should show "(venv)" prefix)
```

### **Step 1D: Install Dependencies**
```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Download spaCy model for NLP
python -m spacy download en_core_web_sm

# Optional: Download multilingual model
python -m spacy download xx_ent_wiki_sm
```

**Troubleshooting Dependencies:**
```bash
# If pip install fails, try installing in sections:
pip install streamlit==1.28.0
pip install fastapi==0.104.1 uvicorn==0.24.0
pip install PyPDF2==3.0.1 python-multipart==0.0.6
pip install spacy transformers torch
pip install deepface opencv-python
pip install pyttsx3 SpeechRecognition
# ... and so on

# Check installed packages:
pip list
```

---

## **Phase 2: Install & Setup Ollama (LLM Backend)**

Ollama allows us to run AI models locally without internet after initial download.

### **Step 2A: Download & Install Ollama**
1. Go to: https://ollama.ai
2. Download: OllamaSetup.exe (Windows)
3. Run installer and follow prompts
4. Ollama will automatically start on background

### **Step 2B: Download Required Models**
```bash
# In terminal, download the default model (one-time)
ollama pull mistral
# OR for multilingual support:
ollama pull llama3

# Download additional models (optional):
ollama pull neural-chat    # Better conversational
ollama pull openhermes     # Better reasoning

# List downloaded models:
ollama list
```

### **Step 2C: Start Ollama Server**
```bash
# Start Ollama service (if not running automatically)
ollama serve

# Verify Ollama is running:
# Open browser: http://localhost:11434/api/tags
# Should return list of available models in JSON
```

**Note:** Leave Ollama running in background while using the app.

---

## **Phase 3: Database Setup**

The app uses SQLite (file-based, zero setup required). Database will auto-create on first run.

```bash
# Manual database initialization (optional):
python models.py
# Should output: "✅ Database initialized!"

# Verify database file created:
dir *.db
# Should show: innovareer_ai.db
```

---

## **Phase 4: Start the Application**

**IMPORTANT: Use 3 separate terminals**

### **Terminal 1: Start Ollama (if not running)**
```bash
ollama serve
# Should show: Ollama is listening on 0.0.0.0:11434
```

### **Terminal 2: Start FastAPI Backend**
```bash
# Activate venv first
venv\Scripts\activate

# Start backend server
uvicorn backend:app --reload --host 0.0.0.0 --port 8000

# Should show:
# Uvicorn running on http://127.0.0.1:8000
# Application startup complete
```

### **Terminal 3: Start Streamlit Frontend**
```bash
# Activate venv first
venv\Scripts\activate

# Start frontend
streamlit run app.py

# Should show:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Opens automatically in browser
```

---

## **Phase 5: First-Time Usage**

### **Step 5A: Create Test Account**
1. Go to: http://localhost:8501 (should open automatically)
2. Click "Sign Up" tab
3. Enter:
   - Email: `test@example.com`
   - Full Name: `Test User`
   - Password: `password123`
   - Language: `English`
4. Click "Create Account"
5. Login with credentials

### **Step 5B: Test Resume Analyzer**
1. Click "Resume Analyzer"
2. Upload sample resume (create simple PDF or use provided sample)
3. Paste job description (example provided below)
4. Click "Analyze Resume"
5. Should show ATS score, matching skills, missing skills

### **Step 5C: Test Interview Practice**
1. Click "Interview Practice"
2. Select: Technical, Text mode
3. Click "Start Interview"
4. Should generate 5 questions (from Ollama)
5. Answer questions and evaluate

---

## **Phase 6: Deployment Options**

### **Option A: Local/On-Premise (Recommended for Hackathon)**
✅ Privacy-first (no data leaves device)
✅ Works offline
✅ Zero cost
✅ Fast (local processing)

**Deployment:**
- Run on laptop/desktop with setup above
- Share access via: `http://<your-ip>:8501`

### **Option B: Cloud Deployment (Advanced)**

#### **Deploy on Heroku (Free Tier)**
```bash
# Install Heroku CLI
# Create Heroku account
heroku login
heroku create your-app-name
git push heroku main
```

#### **Deploy on Replit (Easy)**
1. Go to: https://replit.com
2. Create new Replit project
3. Upload files
4. Create `.replit` file:
```
run = "streamlit run app.py"
```
5. Click Run

#### **Deploy on Hugging Face Spaces**
1. Go to: https://huggingface.co/spaces
2. Create new Space
3. Select Streamlit SDK
4. Upload files
5. Add Dockerfile for Ollama integration

---

## **Phase 7: Testing Checklist**

- [ ] Python installed and venv activated
- [ ] All requirements installed (pip list)
- [ ] spaCy models downloaded
- [ ] Ollama running and models downloaded
- [ ] Database file created (innovareer_ai.db)
- [ ] Backend API running (green status on terminal 2)
- [ ] Frontend loads (http://localhost:8501)
- [ ] Can create account and login
- [ ] Can upload PDF and analyze
- [ ] Interview questions generate
- [ ] Can answer and get evaluation scores
- [ ] Voice features work (if microphone available)
- [ ] Emotion detection works (if webcam available - deepface installed)

---

## **Phase 8: Performance Optimization**

### **Reduce Load Times**
```python
# In app.py, add caching:
import streamlit as st

@st.cache_data
def extract_ats_keywords_cached(resume_text, jd):
    return extract_ats_keywords(resume_text, jd)
```

### **Optimize Ollama Responses**
- Use smaller models: `neural-chat` instead of `llama3`
- Reduce prompt length (already done in code)
- Increase Ollama memory: `OLLAMA_NUM_GPU=1`

### **Database Optimization**
- Add indices: `db.execute("CREATE INDEX idx_user_id ON resumes(user_id)")`
- Regular cleanup of old sessions

---

## **Phase 9: Troubleshooting**

### **Issue: "Ollama not running"**
```bash
# Solution:
# 1. Check if process running:
tasklist | findstr ollama

# 2. Restart Ollama:
ollama serve

# 3. Verify on: http://localhost:11434/api/tags
```

### **Issue: "Port 8501 already in use"**
```bash
# Solution: Kill existing process
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or use different port:
streamlit run app.py --server.port 8502
```

### **Issue: "Database locked"**
```bash
# Solution: 
# 1. Stop all running instances
# 2. Delete innovareer_ai.db
# 3. Restart (will recreate)
```

### **Issue: "Memory error with deepface"**
```bash
# Solution: Use CPU instead of GPU
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Or skip emotion detection:
# Comment out emotion_analyzer lines in app.py
```

### **Issue: "Voice not working"**
```bash
# Solution:
# 1. Check microphone: Settings > Sound
# 2. Test: 
from voice_vision_utils import stt_engine
text = stt_engine.listen_from_microphone()
print(text)

# 3. May need: pip install pyaudio
```

---

## **Phase 10: Advanced Customization**

### **Add More Languages**
```python
# In nlp_utils.py, add language resources:
RESOURCES = {
    "te": {  # Telugu
        "python": [
            {"title": "Python Telugu", "link": "..."}
        ]
    }
}
```

### **Add Custom Skills Database**
```python
# In nlp_utils.py, extend:
TECHNICAL_SKILLS = {
    "existing...",
    "kubernetes", "grok", "dspy"  # New tech
}
```

### **Custom Interview Questions**
```python
# In llm_utils.py, add template:
CUSTOM_PROMPTS = {
    "startup_specific": "Questions for startup roles...",
    "data_science": "Questions for data science..."
}
```

---

## **Phase 11: Presentation Tips for Judges**

### **Demo Script (5 mins)**
1. **Introduction** (30s): "InnoCareer AI - offline, multilingual, emotion-aware"
2. **Login** (30s): Create account, show user data storage
3. **Resume Upload** (1 min): Upload PDF, show ATS analysis
4. **Interview Practice** (2 min): Start interview, show voice/text modes, evaluation
5. **Resources** (1 min): Show how app suggests learning for low scores
6. **Metrics** (1 min): Show dashboard with radar chart

### **Key Points to Highlight**
- ✅ **Offline & Privacy**: "Unlike Final Round AI (cloud/paid), 100% local"
- ✅ **Multilingual**: "Support for Tamil, Hindi - for rural students"
- ✅ **Emotion AI**: "Real-time confidence/nervousness detection"
- ✅ **Free**: "Zero cost, no paid APIs"
- ✅ **Accessible**: "Works for students without internet connections"

### **Comparison Slide (for PPT)**
| Feature | Final Round AI | Huru | InnoCareer AI |
|---------|----------------|------|---------------|
| Cost | $40/mo | $8/mo | FREE |
| Offline | ❌ | ❌ | ✅ |
| Multilingual | ❌ | ❌ | ✅ |
| Emotion AI | Paid addon | ❌ | ✅ Integrated |
| Rural Focus | ❌ | ❌ | ✅ |
| Open Source | ❌ | ❌ | ✅ |

---

## **Phase 12: Post-Hackathon Improvements**

### **Short-term (1-2 weeks)**
- [ ] Add React/Vue frontend for better UX
- [ ] Mobile app (Flutter/React Native)
- [ ] More languages (Telugu, Marathi, Bengali)
- [ ] Video interview playback & analysis
- [ ] Peer-to-peer practice (matching candidates)

### **Medium-term (1-3 months)**
- [ ] Fine-tune Ollama models on custom data
- [ ] Integration with LinkedIn/Indeed scraping
- [ ] Real recruiter feedback API
- [ ] Job recommendation engine
- [ ] Career counselor chatbot

### **Long-term (3-6 months)**
- [ ] Mobile apps on App Store/Play Store
- [ ] SaaS deployment (freemium model)
- [ ] Integrate with college placement cells
- [ ] B2B: Sell to ed-tech companies
- [ ] Expand to global markets

---

## **Quick Commands Reference**

```bash
# Activate environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Start Backend
uvicorn backend:app --reload

# Start Frontend
streamlit run app.py

# Test API
curl http://localhost:8000/api/health

# View database
sqlite3 innovareer_ai.db

# Clear cache
del *.db
del uploads\*

# All at once (PowerShell, 3 windows needed):
# Window 1: ollama serve
# Window 2: uvicorn backend:app --reload
# Window 3: streamlit run app.py
```

---

## **Contact & Support**

For issues during setup:
1. Check Troubleshooting section above
2. Read error messages carefully (they guide you!)
3. Verify all 3 services running on different terminals
4. Check internet connection (for downloading models)
5. Try restarting Ollama: `ollama serve`

---

**NOW READY TO DEMO! 🎉**

Start with Phase 4 (Terminal 1, 2, 3) and you're good to go!

Good luck at SIH 2026! 🚀🏆
