#!/usr/bin/env bash
set -e

echo "=================================================="
echo "  Starting Mboa Finance AI Backend..."
echo "=================================================="

if [ ! -f ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -e .
    .venv/bin/playwright install chromium
fi

echo "Launching server on http://127.0.0.1:8000..."
.venv/bin/python run_backend.py

