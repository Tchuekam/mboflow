#!/usr/bin/env bash
# ==============================================================================
# Run MboFlow Backend on Linux / macOS
# ==============================================================================

set -e

if [ ! -f ".venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found in .venv!"
    echo "Please run ./setup.sh first."
    exit 1
fi

source .venv/bin/activate

echo "=============================================================================="
echo "  Starting MboFlow Backend & Accessibility Agent"
echo "=============================================================================="
echo "[*] Interactive Simulated Bank Portal: http://localhost:8000/bank"
echo "[*] Interactive API Docs: http://localhost:8000/docs"
echo "[*] Deep Readiness Probe: http://localhost:8000/api/v1/health/readiness"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

python run_backend.py
