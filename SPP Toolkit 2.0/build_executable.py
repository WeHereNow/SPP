#!/usr/bin/env python3
"""
SPP Toolkit 2.0 - Executable Builder
Builds a standalone executable using PyInstaller
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

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building SPP Toolkit 2.0 executable...")
    
    # PyInstaller command
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
        "main.py"
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable built successfully!")
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
    print("SPP Toolkit 2.0 - Executable Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please run this script from the SPP Toolkit 2.0 directory.")
        return 1
    
    # Check PyInstaller
    if not check_pyinstaller():
        return 1
    
    # Build executable
    if not build_executable():
        return 1
    
    # Clean up
    cleanup_build_files()
    
    # Check if executable was created
    exe_name = "SPP_Toolkit_2.0.exe" if os.name == 'nt' else "SPP_Toolkit_2.0"
    if os.path.exists(f"dist/{exe_name}"):
        print(f"🎉 Executable created: dist/{exe_name}")
        print("📦 You can now distribute this executable to other PCs")
    else:
        print("❌ Executable not found in dist/ directory")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)