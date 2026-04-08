@echo off
echo ========================================
echo    Agent X - Development Startup
echo ========================================
echo.
echo Starting both API server and React frontend...
echo.

:: Start API server in a new window
start "Agent X API" cmd /k "cd /d %~dp0 && python app.py"

:: Wait a moment for API to start
timeout /t 3 /nobreak > nul

:: Start React frontend in a new window
start "Agent X Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo API Server: http://localhost:5000
echo Frontend:   http://localhost:3002
echo ========================================
echo.
echo Press any key to close this window...
pause > nul
