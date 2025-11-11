# PowerShell script to start the FastAPI backend server

Write-Host "Starting FastAPI Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
Set-Location $PSScriptRoot

# Set PYTHONPATH
$env:PYTHONPATH = $PSScriptRoot

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host ""
}

# Activate virtual environment (if it exists)
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host ""

# Start the server
Write-Host "Starting server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
