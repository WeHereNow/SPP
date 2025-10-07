@echo off
REM Create Python Zip Application (runs without installation)
REM Creates a single .pyz file that can be run with: python SPP_Toolkit.pyz

title SPP Toolkit - Create Zip Application

echo ============================================
echo  Creating Python Zip Application
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Create temporary directory
if exist "zipapp_build" rmdir /s /q zipapp_build
mkdir zipapp_build

REM Copy all Python files
copy *.py zipapp_build\
copy requirements.txt zipapp_build\

REM Create __main__.py
echo import sys > zipapp_build\__main__.py
echo from spp_toolkit_enhanced import main >> zipapp_build\__main__.py
echo if __name__ == '__main__': >> zipapp_build\__main__.py
echo     main() >> zipapp_build\__main__.py

REM Create the zipapp
python -m zipapp zipapp_build -o SPP_Toolkit.pyz -p "/usr/bin/env python3"

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo  Success! Created SPP_Toolkit.pyz
    echo ============================================
    echo.
    echo To run: python SPP_Toolkit.pyz
    echo.
) else (
    echo ERROR: Failed to create zipapp
)

REM Cleanup
rmdir /s /q zipapp_build

pause
