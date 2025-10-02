@echo off
REM SPP Toolkit 2.0 - Windows Executable Launcher
REM No Python installation required!

title SPP Toolkit 2.0 - Standalone Executable

echo ============================================================
echo SPP Toolkit 2.0 - Industrial Validation Toolkit
echo ============================================================
echo Standalone Executable Version - No Python Required!
echo.

REM Check if executable exists
if not exist "SPP_Toolkit_2.0.exe" (
    echo ERROR: SPP_Toolkit_2.0.exe not found
    echo Please make sure you're running this from the SPP Toolkit 2.0 directory
    echo.
    pause
    exit /b 1
)

echo Starting SPP Toolkit 2.0...
echo This may take a few moments to load...
echo.

REM Run the standalone executable
SPP_Toolkit_2.0.exe

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)