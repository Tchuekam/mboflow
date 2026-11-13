#!/usr/bin/env bash
# ==============================================================================
# MboFlow - Local Environment Setup Script for Linux & macOS
# ==============================================================================

set -e

echo "=============================================================================="
echo "  MboFlow - Autonomous Multilingual Financial Accessibility Platform"
echo "  Local Environment Setup Script (Linux / macOS)"
echo "=============================================================================="
echo ""

# 1. Check Python version
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python was not found in your PATH!"
    echo "Please install Python 3.11 or higher."
    exit 1
fi

echo "[*] Using Python: $($PYTHON_CMD --version)"

# 2. Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment in .venv ..."
    $PYTHON_CMD -m venv .venv
    echo "[OK] Virtual environment created."
else
    echo "[OK] Existing virtual environment found in .venv."
fi

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Upgrade pip and packaging tools
echo "[*] Upgrading pip, setuptools, wheel ..."
pip install --upgrade pip setuptools wheel --quiet

# 5. Install dependencies
echo "[*] Installing dependencies from requirements.txt and requirements-dev.txt ..."
pip install -r requirements-dev.txt
echo "[OK] Dependencies installed successfully."

# 6. Install Playwright Chromium browser binary
echo "[*] Installing Playwright Chromium browser ..."
python -m playwright install chromium
echo "[OK] Playwright Chromium browser installed."

# 7. Create local .env from .env.example if missing
if [ ! -f ".env" ]; then
    echo "[*] Generating .env from .env.example ..."
    cp .env.example .env
    echo "[OK] Created .env configuration file."
else
    echo "[OK] .env configuration file already exists."
fi

# 8. Create data directory if missing
mkdir -p data

echo ""
echo "=============================================================================="
echo "  Setup Complete! Your MboFlow environment is ready."
echo "=============================================================================="
echo ""
echo "  To launch the application:"
echo "    ./run.sh   (or: source .venv/bin/activate && python run_backend.py)"
echo ""
echo "  To run the test suite:"
echo "    ./test.sh  (or: source .venv/bin/activate && pytest tests/)"
echo ""
echo "  Simulated Banking Interface URL:"
echo "    http://localhost:8000/bank"
echo "=============================================================================="
echo ""
