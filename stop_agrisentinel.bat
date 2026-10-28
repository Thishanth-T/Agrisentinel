@echo off
title AgriSentinel Shutdown
color 0C

echo.
echo  Stopping all AgriSentinel services...
echo.

:: Kill backend (port 8000)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do (
    echo  Killing Backend PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill dashboard (port 8501)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 " ^| findstr LISTENING') do (
    echo  Killing Dashboard PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill any remaining python/uvicorn/streamlit orphans from our project
taskkill /F /FI "WINDOWTITLE eq AgriSentinel Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq AgriSentinel Dashboard" >nul 2>&1

echo.
echo  All AgriSentinel services stopped.
echo.
timeout /t 2 >nul
