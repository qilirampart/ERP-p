@echo off
chcp 65001 >nul
cls

echo =========================================
echo   ERP System - Docker Deploy
echo =========================================
echo.

docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not installed
    pause
    exit /b 1
)

echo SUCCESS: Docker installed
echo.

if not exist .env (
    echo WARNING: .env file not found
    copy .env.example .env >nul
    echo SUCCESS: .env file created
    echo.
    echo Please edit .env file...
    pause
    notepad .env
    echo.
) else (
    echo SUCCESS: .env file exists
    echo.
)

echo Choose deploy method:
echo   1 - Quick start
echo   2 - Full rebuild
echo.
set /p choice=Enter choice [1 or 2]:

if "%choice%"=="1" (
    echo.
    echo Starting services...
    docker compose up -d
    goto :check
)

if "%choice%"=="2" (
    echo.
    echo Building images...
    docker compose build --no-cache
    echo.
    echo Starting services...
    docker compose up -d
    goto :check
)

echo ERROR: Invalid choice
pause
exit /b 1

:check
echo.
echo Waiting for services...
timeout /t 10 /nobreak >nul

echo.
echo Service status:
docker compose ps

echo.
echo =========================================
echo   Deploy completed!
echo =========================================
echo.
echo Access URLs:
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo Default account:
echo   Username: admin
echo   Password: admin123
echo.
echo IMPORTANT: Change password after first login!
echo.
pause
