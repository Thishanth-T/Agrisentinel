#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  AGRISENTINEL - AUTOMATIC SETUP & INSTALLER (UNIX/MACOS)"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/4] Checking Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.10+."
    exit 1
fi

echo "[2/4] Installing Python backend dependencies..."
PYTHON_BIN="python3"
command -v python3 &> /dev/null || PYTHON_BIN="python"
$PYTHON_BIN -m pip install --upgrade pip
$PYTHON_BIN -m pip install -r "${SCRIPT_DIR}/requirements.txt"

echo "[3/4] Initializing environment config..."
if [ ! -f "${SCRIPT_DIR}/.env" ] && [ -f "${SCRIPT_DIR}/.env.example" ]; then
    cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
    echo "Created .env from .env.example"
fi
if [ ! -f "${SCRIPT_DIR}/Agrisentinel/.env" ] && [ -f "${SCRIPT_DIR}/Agrisentinel/.env.example" ]; then
    cp "${SCRIPT_DIR}/Agrisentinel/.env.example" "${SCRIPT_DIR}/Agrisentinel/.env"
fi

echo "[4/4] Checking Node.js for Animated React Frontend..."
if command -v npm &> /dev/null; then
    echo "Installing frontend npm packages..."
    (cd "${SCRIPT_DIR}/frontend" && npm install)
else
    echo "[NOTE] npm not detected. To use the React UI on port 3000, install Node.js."
fi

echo ""
echo "============================================================"
echo "  SETUP COMPLETE!"
echo "  To launch AgriSentinel anytime, run:"
echo "    ./start_agrisentinel.sh"
echo "============================================================"
