@echo off
title AgriSentinel Terminator
color 0C

echo.
echo ============================================================
echo    Stopping AgriSentinel Backend and Dashboard...
echo ============================================================
echo.

cd /d "%~dp0Agrisentinel"
call stop_agrisentinel.bat
