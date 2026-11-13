@echo off
setlocal EnableDelayedExpansion
title AgriSentinel - One-Time Environment Setup
color 0B

echo ============================================================
echo   AGRISENTINEL - AUTOMATIC SETUP & INSTALLER
echo ============================================================
echo.

:: Get exact directory of this script
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo [2/4] Installing Python backend dependencies...
python -m pip install --upgrade pip
python -m pip install -r "%ROOT_DIR%\requirements.txt"

echo [3/4] Initializing environment config...
if not exist "%ROOT_DIR%\.env" (
    if exist "%ROOT_DIR%\.env.example" (
        copy "%ROOT_DIR%\.env.example" "%ROOT_DIR%\.env" >nul
        echo Created .env from .env.example
    )
)
if not exist "%ROOT_DIR%\Agrisentinel\.env" (
    if exist "%ROOT_DIR%\Agrisentinel\.env.example" (
        copy "%ROOT_DIR%\Agrisentinel\.env.example" "%ROOT_DIR%\Agrisentinel\.env" >nul
    )
)

echo [4/4] Checking Node.js for Animated React Frontend...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo [NOTE] npm/Node.js not detected in PATH.
    echo Backend APIs and Streamlit dashboard will function normally.
    echo To use the animated React UI on port 3000, please install Node.js from https://nodejs.org/
) else (
    echo Installing frontend npm packages...
    pushd "%ROOT_DIR%\frontend"
    call npm install
    popd
)

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo   To launch AgriSentinel anytime, simply double-click:
echo     start_agrisentinel.bat
echo ============================================================
echo.
pause
