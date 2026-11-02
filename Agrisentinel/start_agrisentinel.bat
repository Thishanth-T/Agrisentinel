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

:: Get exact directory of this script (d:\agri sentinels\Agrisentinel\)
set "AGRI_DIR=%~dp0"
:: Strip trailing backslash
set "AGRI_DIR=%AGRI_DIR:~0,-1%"
:: Get root folder (d:\agri sentinels)
for %%I in ("%AGRI_DIR%\..") do set "ROOT_DIR=%%~fI"

echo  [0/4] Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo  [1/4] Starting FastAPI Backend (port 8000)...
start "AgriSentinel Backend" /min cmd /c "cd /d "%AGRI_DIR%" && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"

:: Wait for backend
timeout /t 2 >nul

echo  [2/4] Starting Redesigned Animated Frontend (port 3000)...
start "AgriSentinel Frontend" /min cmd /c "cd /d "%ROOT_DIR%\frontend" && npm run dev"

:: Wait for frontend to be fully ready
timeout /t 4 >nul

echo  [3/4] Opening Redesigned Frontend in your browser...
start "" "http://localhost:3000"

echo  [4/4] Opening API Docs in your browser...
start "" "http://localhost:8000/docs"

echo.
echo  ============================================================
echo     SUCCESSFULLY RUNNING!
echo  ============================================================
echo.
echo     New Animated UI:    http://localhost:3000
echo     Backend APIs:       http://localhost:8000/docs
echo.
echo     To STOP everything, double-click:
echo       stop_agrisentinel.bat
echo.
echo     (You can close THIS window - servers run in background)
echo  ============================================================
echo.
pause
