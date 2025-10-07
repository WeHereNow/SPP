@echo off
REM SPP Toolkit 2.0 - Windows Executable Launcher
REM No Python installation required!

title SPP Toolkit 2.0 - Standalone Executable

echo ============================================================
echo SPP Toolkit 2.0 - Industrial Validation Toolkit
echo ============================================================
echo Standalone Executable Version - No Python Required!
echo.

REM Check if Windows executable exists, if not try Linux executable
if exist "SPP_Toolkit_2.0.exe" (
    set EXECUTABLE=SPP_Toolkit_2.0.exe
) else if exist "SPP_Toolkit_2.0" (
    echo WARNING: Found Linux executable (SPP_Toolkit_2.0) but you're on Windows
    echo This executable was built on Linux and may not work on Windows
    echo.
    echo To fix this:
    echo 1. Install Python 3.8+ from https://python.org
    echo 2. Run: pip install -r requirements.txt
    echo 3. Use the Python version instead: SPP_Toolkit_2.0.bat
    echo.
    echo Attempting to run anyway...
    set EXECUTABLE=SPP_Toolkit_2.0
) else (
    echo ERROR: No executable found
    echo Please make sure you're running this from the SPP Toolkit 2.0 directory
    echo.
    echo Available options:
    echo 1. Use Python version: SPP_Toolkit_2.0.bat
    echo 2. Build Windows executable: python build_executable.py
    echo.
    pause
    exit /b 1
)

echo Starting SPP Toolkit 2.0...
echo This may take a few moments to load...
echo.

REM Run the standalone executable
%EXECUTABLE%

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)