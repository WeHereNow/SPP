@echo off
REM SPP Toolkit Standalone Launcher
REM This expects SPP_Toolkit.exe in the same folder

title SPP All-In-One Toolkit 2.0 - Standalone

echo ============================================
echo  SPP All-In-One Toolkit 2.0 - Standalone
echo  Starting application...
echo ============================================
echo.

REM Check if executable exists
if exist "SPP_Toolkit.exe" (
    echo Starting SPP_Toolkit.exe...
    echo.
    start "" "SPP_Toolkit.exe"
    exit /b 0
) else (
    echo ERROR: SPP_Toolkit.exe not found!
    echo.
    echo This launcher expects SPP_Toolkit.exe in the same folder.
    echo.
    echo To create the executable:
    echo   1. Run BUILD_EXECUTABLE.bat on a Windows machine
    echo   2. Copy the files from dist\SPP_Toolkit\ to this folder
    echo   3. Run this script again
    echo.
    echo OR use the Python version:
    echo   - Run SPP_Toolkit.bat instead
    echo.
    pause
    exit /b 1
)
