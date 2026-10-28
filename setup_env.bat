@echo off
title AgriSentinel - One-Time Setup
color 0B

echo ============================================================
echo   AGRISENTINEL - AUTOMATIC SETUP & INSTALLER
echo ============================================================
echo.
echo [1/2] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo [2/2] Installing required Python libraries...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ============================================================
echo   SETUP COMPLETE!
echo   To launch AgriSentinel anytime, simply double-click:
echo     start_agrisentinel.bat
echo ============================================================
echo.
pause
