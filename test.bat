@echo off
setlocal

echo ==============================================================================
echo   Running MboFlow Verification & Test Suite
echo ==============================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first to set up dependencies.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pytest tests/ %*
