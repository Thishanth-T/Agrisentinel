@echo off
setlocal EnableDelayedExpansion
title AgriSentinel Enterprise Launcher
color 0A

:: Forward directly to the root launcher
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%SCRIPT_DIR%\..") do set "ROOT_DIR=%%~fI"

cd /d "%ROOT_DIR%"
call start_agrisentinel.bat
