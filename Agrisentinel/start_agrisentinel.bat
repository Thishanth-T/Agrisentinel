@echo off
title AgriSentinel Enterprise Launcher
color 0A

echo.
echo  ============================================================
echo     AGRISENTINEL - Parametric Crop Insurance Platform
echo     Enterprise B2B Demo Launcher
echo  ============================================================
echo.

:: Navigate to project folder (wherever this .bat file lives)
cd /d "%~dp0"

:: Set credentials for this execution session
set "TWILIO_ACCOUNT_SID=AC7b5b6cc7e83c59d0edc54bcf59a4dee1"
set "TWILIO_AUTH_TOKEN=6af791ff2a26f1c8e69afe984fafcf17"
set "TWILIO_PHONE_NUMBER=+17372508034"
set "GROQ_API_KEY=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"
set "OPENWEATHER_API_KEY=0f5614e650857443251cbb524550aad8"
set "FARMER_TEST_PHONE=+919363849952"

:: Kill any old instances still running on 8000 / 8501
echo  [0/4] Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8501 " ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo  [1/4] Starting FastAPI Backend (port 8000)...
start "AgriSentinel Backend" /min cmd /c "cd /d "%~dp0" && python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"

:: Wait for backend to be ready
timeout /t 3 >nul

echo  [2/4] Starting Streamlit Dashboard (port 8501)...
start "AgriSentinel Dashboard" /min cmd /c "cd /d "%~dp0" && python -m streamlit run dashboard.py --server.port 8501 --server.headless true"

:: Wait for dashboard to be ready
timeout /t 3 >nul

echo  [3/4] Opening Dashboard in your browser...
start "" "http://localhost:8501"

echo  [4/4] Opening API Docs in your browser...
start "" "http://localhost:8000/docs"

echo.
echo  ============================================================
echo     EVERYTHING IS RUNNING!
echo  ============================================================
echo.
echo     Dashboard:  http://localhost:8501
echo     API Docs:   http://localhost:8000/docs
echo     Backend:    http://localhost:8000/health
echo.
echo     To STOP everything, double-click:
echo       stop_agrisentinel.bat
echo.
echo     (You can close THIS window - servers run in background)
echo  ============================================================
echo.
pause
