@echo off
title AgriSentinel Root Launcher
color 0A

echo.
echo ============================================================
echo    AGRISENTINEL - Parametric Crop Insurance Platform
echo    Enterprise Hackathon Prototype Launcher
echo ============================================================
echo.

:: Navigate to the Agrisentinel folder containing backend & dashboard
cd /d "%~dp0Agrisentinel"

:: Run the core startup batch script
call start_agrisentinel.bat
