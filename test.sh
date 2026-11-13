#!/usr/bin/env bash
# ==============================================================================
# Run MboFlow Test Suite on Linux / macOS
# ==============================================================================

set -e

if [ ! -f ".venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found in .venv!"
    echo "Please run ./setup.sh first."
    exit 1
fi

source .venv/bin/activate
python -m pytest tests/ "$@"
