@echo off
REM CCD2 Project Quick Start Script
REM This script starts both backend and frontend services

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "BACKEND_PATH=%PROJECT_ROOT%backend"
set "FRONTEND_PATH=%PROJECT_ROOT%frontend"

cls
echo.
echo ============================================================
echo   CCD2 Customer Collection System - Quick Start
echo ============================================================
echo.

REM Check Python
echo [Info] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found! Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python installed

REM Check Node.js
echo [Info] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Node.js not found! Please install Node.js 16+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js installed

REM Check npm
echo [Info] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [Error] npm not found!
    pause
    exit /b 1
)
echo [OK] npm installed

REM Check .env
echo [Info] Checking configuration...
if not exist "%BACKEND_PATH%\.env" (
    echo [Error] backend\.env not found!
    echo Please create backend\.env file with database configuration
    pause
    exit /b 1
)
echo [OK] Configuration file exists

echo.
echo [Step] Installing backend dependencies...
cd /d "%BACKEND_PATH%"
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [Error] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed

cd /d "%PROJECT_ROOT%"

echo.
echo [Step] Checking frontend dependencies...
if not exist "%FRONTEND_PATH%\node_modules" (
    echo [Info] Installing npm dependencies (may take a few minutes)...
    cd /d "%FRONTEND_PATH%"
    call npm install
    if errorlevel 1 (
        echo [Error] Failed to install npm dependencies
        pause
        exit /b 1
    )
    cd /d "%PROJECT_ROOT%"
)
echo [OK] Frontend dependencies ready

echo.
echo [Step] Starting backend service...
cd /d "%BACKEND_PATH%"
start "CCD2 Backend" /MIN cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo [OK] Backend started

cd /d "%PROJECT_ROOT%"

echo.
echo ============================================================
echo   Services Started
echo ============================================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo ============================================================
echo.
echo Starting frontend service...
echo Close this window to stop frontend (backend runs separately)
echo.

cd /d "%FRONTEND_PATH%"
call npm run dev

echo.
echo Frontend stopped. Backend still running in separate window.
pause
