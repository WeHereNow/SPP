@echo off
echo Starting SPP All-In-One Toolkit...
echo.
SPP_Toolkit.exe
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start.
    echo Press any key to exit...
    pause >nul
)