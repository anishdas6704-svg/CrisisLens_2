@echo off
echo ===================================================
echo   CrisisLens AI Command Center - Full Stack Launcher
echo ===================================================

echo [1/3] Starting Backend Server (Port 8000)...
start "CrisisLens Backend" cmd /k "cd /d "%~dp0backend" && python run.py"

timeout /t 2 /nobreak >nul

echo [2/3] Starting Frontend Server (Port 3000)...
start "CrisisLens Frontend" cmd /k "cd /d "%~dp0" && python -m http.server 3000"

timeout /t 1 /nobreak >nul

echo [3/3] Opening Browser...
start http://localhost:3000

echo.
echo CrisisLens AI Command Center is now running!
echo Backend:  http://localhost:8000/api/v1
echo Docs:     http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
