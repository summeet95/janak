@echo off
setlocal enabledelayedexpansion

echo ============================================
echo AIC Inventory Management System
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo ✗ Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

echo ✓ Virtual environment found
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ✗ Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

echo ✓ Virtual environment activated
echo.

REM Check MongoDB with better diagnostics
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000); client.admin.command('ping'); print('✓ MongoDB is running')" 2>nul
if errorlevel 1 (
    echo.
    echo ✗ MongoDB is not running!
    echo.
    echo TO START MONGODB:
    echo   1. Press Win + R
    echo   2. Type: services.msc
    echo   3. Find "MongoDB Server"
    echo   4. Right-click and select "Start"
    echo.
    echo IMPORTANT: Wait 10 seconds for MongoDB to fully start
    echo Then run this batch file again.
    echo.
    echo If you don't have MongoDB installed:
    echo   Download from: https://www.mongodb.com/try/download/community
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Starting Flask Application...
echo ============================================
echo.
echo ✓ Open your browser to: http://localhost:5000
echo.
echo Press CTRL+C in this window to stop the server
echo.

REM Run the app
python run.py
if errorlevel 1 (
    echo.
    echo ✗ Error running application
    echo.
    pause
    exit /b 1
)

pause
