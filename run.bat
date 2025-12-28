@echo off
echo ========================================
echo Starting Chat Intelligence System...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if database exists
if not exist "chat_intelligence.db" (
    echo WARNING: Database not found. Creating database...
    python init_db.py
)

REM Start the application
echo.
echo Starting Flask server...
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server.
echo.
python app.py
