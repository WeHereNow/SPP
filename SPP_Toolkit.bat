@echo off
REM SPP All-In-One Toolkit Launcher
REM Automatically detects Python and runs the toolkit

title SPP All-In-One Toolkit 2.0

echo ============================================
echo  SPP All-In-One Toolkit 2.0
echo  Starting application...
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pylogix" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required package: pylogix...
    python -m pip install pylogix --quiet
)

python -c "import docx" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required package: python-docx...
    python -m pip install python-docx --quiet
)

echo.
echo Starting SPP Toolkit...
echo.

REM Run the application
python spp_toolkit_enhanced.py

REM Check if application exited with error
if %errorlevel% neq 0 (
    echo.
    echo ============================================
    echo  Application exited with error code: %errorlevel%
    echo ============================================
    echo.
    pause
)

exit /b 0
