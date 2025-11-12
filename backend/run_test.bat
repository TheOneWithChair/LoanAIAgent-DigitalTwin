@echo off
echo ================================================================================
echo 🧪 RUNNING AI AGENT TEST
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment and run test
call venv\Scripts\activate.bat
python test_agent_responses.py

echo.
pause
