@echo off
setlocal

echo ==============================================================================
echo   Starting MboFlow Backend & Accessibility Agent
echo ==============================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first to set up dependencies.
    pause
    exit /b 1
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

echo [*] Launching FastAPI Unified Backend on http://localhost:8000 ...
echo [*] Interactive Simulated Bank Portal: http://localhost:8000/bank
echo [*] Interactive API Docs: http://localhost:8000/docs
echo [*] Deep Health & Readiness Probe: http://localhost:8000/api/v1/health/readiness
echo.
echo Press Ctrl+C in this terminal to stop the server.
echo.

python run_backend.py
