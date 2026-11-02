@echo off
setlocal EnableDelayedExpansion
title AgriSentinel Enterprise Launcher
color 0A

echo.
echo  ============================================================
echo     AGRISENTINEL - Parametric Crop Insurance Platform
echo     Enterprise Launcher: Redesigned Frontend + Backend
echo  ============================================================
echo.

:: Get exact directory of this script (d:\agri sentinels\)
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"
set "BACKEND_DIR=%ROOT_DIR%\Agrisentinel"
set "FRONTEND_DIR=%ROOT_DIR%\frontend"

echo  [0/4] Cleaning up any old AgriSentinel instances...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
ping -n 2 127.0.0.1 >nul

echo  [1/4] Starting FastAPI Backend on port 8000...
start "AgriSentinel Backend (Port 8000)" cmd /k "cd /d "%BACKEND_DIR%" && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"

ping -n 3 127.0.0.1 >nul

echo  [2/4] Starting Animated UI Frontend on port 3000...
start "AgriSentinel Frontend (Port 3000)" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

ping -n 4 127.0.0.1 >nul

echo  [3/4] Opening Animated Frontend in your browser (http://localhost:3000)...
start "" "http://localhost:3000"

echo  [4/4] Opening API Docs in your browser (http://localhost:8000/docs)...
start "" "http://localhost:8000/docs"

echo.
echo  ============================================================
echo     AGRISENTINEL PLATFORM STARTED!
echo  ============================================================
echo.
echo     Animated UI:    http://localhost:3000
echo     Backend APIs:   http://localhost:8000/docs
echo.
echo     Both server windows will remain open so you can see live logs.
echo     To terminate all services, run stop_agrisentinel.bat
echo  ============================================================
echo.
pause
