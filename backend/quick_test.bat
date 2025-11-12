@echo off
echo Testing API with detailed error output...
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
python quick_test.py
echo.
pause
