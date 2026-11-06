@echo off
setlocal enabledelayedexpansion

echo ============================================
echo AIC Inventory Management System Setup
echo ============================================
echo.

REM Change to script directory
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ✗ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    echo After installing Python, restart your computer and run this setup again.
    echo.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version
echo.
pause

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ✗ ERROR: Failed to create virtual environment
        echo Try running this file as Administrator
        echo.
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
    echo.
) else (
    echo ✓ Virtual environment already exists
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ✗ ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.
pause

echo Installing dependencies (this may take a minute)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ✗ ERROR: Failed to install dependencies
    echo Try running this file as Administrator
    echo.
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.
pause

echo Initializing database...
python init_db.py
if errorlevel 1 (
    echo.
    echo ✗ ERROR: Database initialization failed
    echo Make sure MongoDB is running!
    echo.
    echo To start MongoDB:
    echo   1. Press Win + R
    echo   2. Type: services.msc
    echo   3. Find "MongoDB Server"
    echo   4. Right-click and select "Start"
    echo.
    echo Then run this setup again.
    echo.
    pause
    exit /b 1
)
echo ✓ Database initialized
echo.
pause

echo.
echo ============================================
echo ✓ SETUP COMPLETE!
echo ============================================
echo.
echo Next steps:
echo 1. Close this window
echo 2. Make sure MongoDB is running (Services > MongoDB Server)
echo 3. Double-click: run.bat
echo.
pause
