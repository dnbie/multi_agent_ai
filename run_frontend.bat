@echo off
echo Starting Agent X React Frontend...
echo.
cd /d "%~dp0frontend"

:: Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting development server...
npm start
pause
