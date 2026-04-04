@echo off
REM Setup script for AI-Powered API Builder (Windows)

echo.
echo 🚀 AI-Powered API Builder Setup
echo ==================================
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv\" (
    echo ✓ Creating virtual environment...
    python -m venv venv
)

echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo ✓ Installing dependencies...
python -m pip install --upgrade pip > nul
pip install -r requirements.txt > nul

REM Setup environment file
if not exist ".env" (
    echo ✓ Creating .env file...
    copy .env.example .env
)

echo.
echo ==================================
echo ✓ Setup Complete!
echo ==================================
echo.
echo 📋 Next Steps:
echo.
echo 1. Start Ollama (in another terminal):
echo    ollama serve
echo.
echo 2. Pull the model (first time only):
echo    ollama pull qwen2.5-coder:7b
echo.
echo 3. Run the application:
echo    cd app
echo    python -m uvicorn main:app --reload
echo.
echo 4. Open your browser:
echo    http://localhost:8000
echo.
pause

