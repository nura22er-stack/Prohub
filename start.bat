@echo off
REM ProHub Bot Starter Script for Windows

echo ======================================
echo   ProHub Bot - Starting Services
echo ======================================

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements if needed
pip install -q -r requirements-dev.txt

echo.
echo Starting ProHub Bot services...
echo.
echo Note: These are running in separate windows. Close each to stop them.
echo.

REM Start bot in new window
start "ProHub Bot" python -m bot.main

REM Start API in new window
timeout /t 2 /nobreak
start "ProHub API" python api\app.py

REM Keep this window open
echo.
echo All services started!
echo - Bot: Check "ProHub Bot" window
echo - API: http://localhost:5000 (check "ProHub API" window)
echo.
echo Press any key to exit...
pause
