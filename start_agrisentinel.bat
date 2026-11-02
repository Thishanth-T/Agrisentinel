@echo off
setlocal EnableDelayedExpansion
title AgriSentinel Root Launcher
color 0A

set "ROOT_DIR=%~dp0"
set "ROOT_DIR=%ROOT_DIR:~0,-1%"

cd /d "%ROOT_DIR%\Agrisentinel"
call start_agrisentinel.bat
