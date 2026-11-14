#!/usr/bin/env bash

echo "============================================================"
echo "  AGRISENTINEL - PLATFORM LAUNCHER (UNIX/MACOS)"
echo "============================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/Agrisentinel"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# Clean up existing ports 8000, 3000, 8501
for port in 8000 3000 8501; do
    pid=$(lsof -ti :${port} 2>/dev/null || true)
    if [ -n "$pid" ]; then
        kill -9 $pid 2>/dev/null || true
    fi
done

echo "[1/3] Starting FastAPI Backend on port 8000..."
PYTHON_BIN="python3"
command -v python3 &> /dev/null || PYTHON_BIN="python"
(cd "${BACKEND_DIR}" && $PYTHON_BIN -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

sleep 2

echo "[2/3] Starting Animated UI Frontend on port 3000..."
if command -v npm &> /dev/null; then
    (cd "${FRONTEND_DIR}" && npm run dev) &
    FRONTEND_PID=$!
else
    echo "[NOTE] npm not detected; frontend not started automatically."
fi

sleep 2

echo "[3/3] Opening in default web browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:3000" 2>/dev/null || true
elif command -v open &> /dev/null; then
    open "http://localhost:3000" 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "  AGRISENTINEL PLATFORM STARTED!"
echo "  Animated UI:   http://localhost:3000"
echo "  API Docs:      http://localhost:8000/docs"
echo "  Press Ctrl+C to terminate services."
echo "============================================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" INT TERM
wait
