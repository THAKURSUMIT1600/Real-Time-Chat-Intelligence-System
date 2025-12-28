@echo off
echo ========================================
echo Chat Intelligence System - Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Upgrading pip...
python -m pip install --upgrade pip

echo [4/6] Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/6] Downloading spaCy model...
python -m spacy download en_core_web_sm
if errorlevel 1 (
    echo WARNING: Failed to download spaCy model
    echo You can manually install it later with: python -m spacy download en_core_web_sm
)

echo [6/6] Initializing database...
python init_db.py
if errorlevel 1 (
    echo WARNING: Failed to initialize database
    echo You can manually initialize it later with: python init_db.py
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run the app: python app.py
echo   3. Open browser: http://localhost:5000
echo.
pause
