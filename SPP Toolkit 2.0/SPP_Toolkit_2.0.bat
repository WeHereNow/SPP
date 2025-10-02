@echo off
REM SPP Toolkit 2.0 - Windows Launcher
REM Industrial PLC and Vision System Validation Toolkit

title SPP Toolkit 2.0

echo ============================================================
echo SPP Toolkit 2.0 - Industrial Validation Toolkit
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this batch file from the SPP Toolkit 2.0 directory
    echo.
    pause
    exit /b 1
)

REM Run the application
echo Starting SPP Toolkit 2.0...
echo.
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)