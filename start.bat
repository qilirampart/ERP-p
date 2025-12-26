@echo off
echo ========================================
echo    Print-ERP System Startup
echo ========================================
echo.

if not exist "backend" (
    echo [ERROR] Backend directory not found
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] Frontend directory not found
    pause
    exit /b 1
)

echo [1/2] Starting backend service on port 8000...
start "Print-ERP Backend" cmd /k "cd /d %cd%\backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend service on port 5173...
start "Print-ERP Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"

echo.
echo [3/3] Waiting for services to start...
timeout /t 8 /nobreak >nul

echo Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173 (Auto-opened)
echo.
echo Browser should open automatically in a few seconds...
echo If not, please visit: http://localhost:5173
echo.
pause
