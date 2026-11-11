# PowerShell startup script for Mboa Finance AI
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  Starting Mboa Finance AI..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

if (-Not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .venv\Scripts\pip.exe install -e .
    & .venv\Scripts\playwright.exe install chromium
}

Write-Host "Launching server on http://127.0.0.1:8000..." -ForegroundColor Cyan
& .venv\Scripts\python.exe run_backend.py

