@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo   MboFlow - Autonomous Multilingual Financial Accessibility Platform
echo   Local Environment Setup Script for Windows
echo ==============================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.11 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Create virtual environment if missing
if not exist ".venv" (
    echo [*] Creating virtual environment in .venv ...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [OK] Existing virtual environment found in .venv.
)

:: 3. Activate virtual environment
echo [*] Activating virtual environment ...
call .venv\Scripts\activate.bat

:: 4. Upgrade pip and packaging tools
echo [*] Upgrading pip, setuptools, wheel ...
python -m pip install --upgrade pip setuptools wheel --quiet

:: 5. Install dependencies
echo [*] Installing dependencies from requirements.txt and requirements-dev.txt ...
python -m pip install -r requirements-dev.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.

:: 6. Install Playwright Chromium headless browser
echo [*] Installing Playwright Chromium browser binary ...
python -m playwright install chromium
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Playwright browser installation reported an issue.
) else (
    echo [OK] Playwright Chromium browser ready.
)

:: 7. Create local .env from .env.example if missing
if not exist ".env" (
    echo [*] Generating .env from .env.example ...
    copy .env.example .env >nul
    echo [OK] Created .env configuration file.
) else (
    echo [OK] .env configuration file already exists.
)

:: 8. Create data directory if missing
if not exist "data" (
    mkdir data
    echo [OK] Created data directory for SQLite WAL database.
)

echo.
echo ==============================================================================
echo   Setup Complete! Your MboFlow environment is ready.
echo ==============================================================================
echo.
echo   To launch the application:
echo     run.bat   (or: python run_backend.py)
echo.
echo   To run the test suite:
echo     test.bat  (or: pytest tests/)
echo.
echo   Simulated Banking Interface URL:
echo     http://localhost:8000/bank
echo ==============================================================================
echo.
pause
