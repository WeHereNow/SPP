@echo off
REM Build Standalone Executable for Windows
REM Run this on a Windows machine to create SPP_Toolkit.exe

title SPP Toolkit - Build Standalone Executable

echo ============================================
echo  SPP Toolkit - Executable Builder
echo  Building standalone executable...
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8+ from python.org
    echo Then run this script again.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo PyInstaller installed successfully
echo.

REM Install required packages
echo Installing required packages...
python -m pip install pylogix python-docx --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install required packages
    pause
    exit /b 1
)
echo Required packages installed
echo.

REM Build executable
echo Building standalone executable...
echo This may take a few minutes...
echo.

pyinstaller spp_toolkit.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Build Complete!
echo ============================================
echo.
echo Executable created in: dist\SPP_Toolkit\
echo.
echo To create deployment package:
echo   1. Go to dist\SPP_Toolkit\ folder
echo   2. Copy all files to your deployment location
echo   3. Run SPP_Toolkit.exe (no Python needed!)
echo.
echo To create ZIP:
echo   1. Right-click dist\SPP_Toolkit folder
echo   2. Send to > Compressed (zipped) folder
echo   3. Rename to SPP_Toolkit_Standalone.zip
echo.
pause
