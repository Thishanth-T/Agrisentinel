@echo off
title AgriSentinel Enterprise Launcher
color 0A

echo.
echo  ============================================================
echo     AGRISENTINEL - Parametric Crop Insurance Platform
echo     Enterprise B2B Demo Launcher with Redesigned Frontend
echo  ============================================================
echo.

:: Navigate to project folder
cd /d "%~dp0"

:: Kill any old instances still running on 8000 / 8501 / 3000
echo  [0/5] Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo  [1/5] Starting FastAPI Backend (port 8000)...
start "AgriSentinel Backend" /min cmd /c "cd /d "%~dp0" && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"

:: Wait for backend to be ready
timeout /t 3 >nul

echo  [2/5] Starting Redesigned Animated Frontend (port 3000)...
start "AgriSentinel Frontend" /min cmd /c "cd /d "%~dp0..\frontend" && npm run dev"

echo  [3/5] Starting Streamlit Insurer Cockpit (port 8501)...
start "AgriSentinel Dashboard" /min cmd /c "cd /d "%~dp0" && python -m streamlit run dashboard.py --server.port 8501 --server.headless true"

:: Wait for servers to spin up
timeout /t 3 >nul

echo  [4/5] Opening Redesigned Frontend in your browser...
start "" "http://localhost:3000"

echo  [5/5] Opening B2B Insurer Cockpit in your browser...
start "" "http://localhost:8501"

echo.
echo  ============================================================
echo     EVERYTHING IS RUNNING!
echo  ============================================================
echo.
echo     New Animated UI:     http://localhost:3000
echo     B2B Cockpit:         http://localhost:8501
echo     FastAPI Docs:        http://localhost:8000/docs
echo     Backend Status:      http://localhost:8000/health
echo.
echo     To STOP everything, double-click:
echo       stop_agrisentinel.bat
echo.
echo     (You can close THIS window - servers run in background)
echo  ============================================================
echo.
pause
