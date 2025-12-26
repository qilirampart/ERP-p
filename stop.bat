@echo off
echo ========================================
echo    Print-ERP System Stop
echo ========================================
echo.

echo [1/2] Stopping backend service (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/2] Stopping frontend service (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo   All services stopped
echo ========================================
echo.
pause
