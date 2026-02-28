@echo off
REM InnoCareer AI - Quick Start for Windows
REM This script sets up and starts the entire application

echo.
echo ======================================
echo   InnoCareer AI - Startup Script
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Checking virtual environment...
if not exist "venv" (
    echo [CREATING] Virtual environment...
    python -m venv venv
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing/updating dependencies...
pip install -q -r requirements.txt >nul 2>&1
python -m spacy download -q en_core_web_sm 2>nul

echo [4/5] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul
if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: Ollama is NOT running!
    echo Please start Ollama first (search for "Ollama" in Start Menu)
    echo Then run this script again.
    echo.
    pause
    exit /b 1
)
echo ✅ Ollama detected

echo [5/5] Starting InnoCareer AI...
echo.
echo Press Ctrl+C to stop all services
echo.

REM Create batch files to run in parallel
(
    @echo off
    cd /d "%cd%"
    call venv\Scripts\activate.bat
    echo Starting FastAPI Backend...
    title InnoCareer Backend
    uvicorn backend:app --reload
) > temp_backend.bat

(
    @echo off
    cd /d "%cd%"
    call venv\Scripts\activate.bat
    echo Starting Streamlit Frontend...
    title InnoCareer Frontend
    timeout /t 2
    streamlit run app.py
) > temp_frontend.bat

echo.
echo ✅ Backend starting on http://localhost:8000
echo ✅ Frontend starting on http://localhost:8501
echo.
echo Waiting 3 seconds before opening browser...
timeout /t 3

REM Start both in separate windows
start "InnoCareer Backend" cmd /k temp_backend.bat
start "InnoCareer Frontend" cmd /k temp_frontend.bat

echo.
echo ✅ All services started!
echo Browser will open in a moment...
timeout /t 3

REM Open in browser
start http://localhost:8501

pause
exit /b 0
