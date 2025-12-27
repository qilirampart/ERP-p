@echo off
echo ========================================
echo    Print-ERP System Installation
echo    First time setup
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

echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python installed
echo.

echo [2/6] Checking Poetry...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] Poetry not found, installing...
    pip install poetry
    if errorlevel 1 (
        echo [ERROR] Poetry installation failed
        pause
        exit /b 1
    )
)
poetry --version
echo [OK] Poetry installed
echo.

echo [3/6] Installing backend dependencies...
cd backend
echo This may take a few minutes...
poetry install
if errorlevel 1 (
    echo [ERROR] Backend installation failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed
cd ..
echo.

echo [4/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found, please install Node.js 16+
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo [OK] Node.js installed
echo.

echo [5/6] Installing frontend dependencies...
cd frontend
echo This may take a few minutes...
call npm install
if errorlevel 1 (
    echo [ERROR] Frontend installation failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Frontend dependencies installed
cd ..
echo.

echo [6/6] Checking database configuration...
if not exist "backend\.env" (
    echo [WARN] backend\.env not found
    echo Please create backend\.env based on backend\.env.example
    echo.
    echo Minimum configuration:
    echo DATABASE_URL=mysql://root:password@localhost:3306/erp_db
    echo SECRET_KEY=your-secret-key-here
    echo.
) else (
    echo [OK] Configuration file exists
)

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure MySQL is running
echo 2. Check backend\.env configuration
echo 3. Run database migrations:
echo    cd backend
echo    poetry run alembic upgrade head
echo 4. Initialize database:
echo    poetry run python scripts/init_db.py
echo 5. Start system: double-click start.bat
echo.
pause
