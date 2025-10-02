#!/usr/bin/env python3
"""
SPP Toolkit 2.0 - Windows Executable Builder
Builds a Windows-compatible executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} is available")
        return True
    except ImportError:
        print("❌ PyInstaller is not installed")
        print("💡 Install it with: pip install pyinstaller")
        return False

def build_windows_executable():
    """Build the Windows executable using PyInstaller"""
    print("🔨 Building SPP Toolkit 2.0 Windows executable...")
    
    # PyInstaller command for Windows
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=SPP_Toolkit_2.0",
        "--add-data=src;src",
        "--add-data=config;config", 
        "--add-data=README.md;.",
        "--add-data=requirements.txt;.",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=pylogix",
        "--hidden-import=ping3",
        "--hidden-import=psutil",
        "--console",
        "--distpath=dist_windows",
        "main.py"
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Windows executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def cleanup_build_files():
    """Clean up PyInstaller build files"""
    print("🧹 Cleaning up build files...")
    
    cleanup_dirs = ["build", "__pycache__"]
    cleanup_files = ["SPP_Toolkit_2.0.spec"]
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    for file_name in cleanup_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   Removed {file_name}")

def main():
    """Main build process"""
    print("=" * 60)
    print("SPP Toolkit 2.0 - Windows Executable Builder")
    print("=" * 60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️  WARNING: This script is designed for Windows")
        print("   The executable will be built but may not work on other platforms")
        print()
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please run this script from the SPP Toolkit 2.0 directory.")
        return 1
    
    # Check PyInstaller
    if not check_pyinstaller():
        return 1
    
    # Build executable
    if not build_windows_executable():
        return 1
    
    # Clean up
    cleanup_build_files()
    
    # Check if executable was created
    exe_name = "SPP_Toolkit_2.0.exe"
    if os.path.exists(f"dist_windows/{exe_name}"):
        print(f"🎉 Windows executable created: dist_windows/{exe_name}")
        
        # Copy to main directory
        shutil.copy2(f"dist_windows/{exe_name}", exe_name)
        print(f"📁 Copied to main directory: {exe_name}")
        
        # Clean up dist_windows
        shutil.rmtree("dist_windows")
        print("🧹 Cleaned up build directory")
        
        print("📦 You can now distribute this executable to Windows PCs")
    else:
        print("❌ Windows executable not found in dist_windows/ directory")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)