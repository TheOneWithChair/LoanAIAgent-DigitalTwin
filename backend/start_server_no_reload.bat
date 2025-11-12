@echo off
echo Starting FastAPI Backend Server for Testing...
echo.

cd /d "%~dp0"

REM Set PYTHONPATH to current directory
set PYTHONPATH=%CD%

REM Start the server WITHOUT pause so it stays running
echo Server starting on http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

call venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
