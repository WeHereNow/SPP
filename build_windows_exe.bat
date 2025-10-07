@echo off
echo ========================================
echo SPP Toolkit - Windows Executable Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from python.org
    pause
    exit /b 1
)

echo Installing required dependencies...
pip install --upgrade pip
pip install pylogix python-docx pandas matplotlib reportlab cryptography
pip install pyinstaller

echo.
echo Building Windows executable...
pyinstaller spp_toolkit.spec --clean

if exist "dist\SPP_Toolkit.exe" (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\SPP_Toolkit.exe
    echo.
    echo Creating release package...
    
    REM Create release directory
    if not exist "release" mkdir release
    
    REM Copy files to release directory
    copy dist\SPP_Toolkit.exe release\
    copy requirements.txt release\
    copy README.txt release\
    copy RUN_TOOLKIT.bat release\
    
    REM Create zip file
    echo.
    echo Creating ZIP archive...
    powershell Compress-Archive -Path release\* -DestinationPath SPP_Toolkit_Windows.zip -Force
    
    echo.
    echo ========================================
    echo PACKAGE COMPLETE!
    echo ========================================
    echo.
    echo Release package: SPP_Toolkit_Windows.zip
    echo.
    echo Contents:
    dir release
    
) else (
    echo.
    echo ERROR: Build failed. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo Press any key to exit...
pause >nul