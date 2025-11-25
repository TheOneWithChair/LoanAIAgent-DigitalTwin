@echo off
echo ====================================
echo Starting Loan Application API Server
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install fastapi uvicorn tortoise-orm pydantic pydantic-email-validator
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Virtual environment activated
echo.
echo Starting server at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn app.loan_api_example:app --reload --host 0.0.0.0 --port 8000
