@echo off
REM SPP Toolkit Installation Script
REM This script installs Python dependencies

title SPP Toolkit Installation

echo ============================================
echo  SPP All-In-One Toolkit 2.0 - Installation
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install required packages
echo Installing required packages...
echo.

echo [1/2] Installing pylogix...
python -m pip install pylogix>=1.4.0 --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pylogix
    pause
    exit /b 1
)
echo     ✓ pylogix installed successfully

echo [2/2] Installing python-docx...
python -m pip install python-docx>=0.8.11 --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install python-docx
    pause
    exit /b 1
)
echo     ✓ python-docx installed successfully

echo.
echo ============================================
echo  Installation Complete!
echo ============================================
echo.
echo To run the SPP Toolkit:
echo   1. Double-click SPP_Toolkit.bat
echo   OR
echo   2. Run: python spp_toolkit_enhanced.py
echo.
echo Check README.md for usage instructions
echo.
pause
