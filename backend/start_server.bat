@echo off
echo Starting FastAPI Backend Server...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Set PYTHONPATH to current directory
set PYTHONPATH=%CD%

REM Start the server
echo Starting server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
