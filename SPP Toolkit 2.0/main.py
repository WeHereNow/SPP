#!/usr/bin/env python3
"""
SPP Toolkit 2.0 - Main Launcher
Industrial PLC and Vision System Validation Toolkit

This is the main entry point for the SPP Toolkit 2.0 application.
It handles initialization, dependency checking, and launches the GUI.
"""

import sys
import os
import traceback
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Check for required modules
    required_modules = [
        'tkinter',
        'pylogix',
        'ping3',
        'psutil'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 To install missing dependencies, run:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """Setup the application environment"""
    # Add src directory to Python path
    src_dir = Path(__file__).parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create config directory if it doesn't exist
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)

def main():
    """Main application entry point"""
    print("=" * 60)
    print("SPP Toolkit 2.0 - Industrial Validation Toolkit")
    print("=" * 60)
    print("Initializing application...")
    
    try:
        # Setup environment
        setup_environment()
        print("✅ Environment setup complete")
        
        # Check dependencies
        print("🔍 Checking dependencies...")
        if not check_dependencies():
            print("\n❌ Dependency check failed. Please install missing packages.")
            input("Press Enter to exit...")
            return 1
        print("✅ All dependencies available")
        
        # Import and launch the main application
        print("🚀 Launching SPP Toolkit GUI...")
        from spp_toolkit_enhanced import SPPToolkitEnhanced
        
        # Create and run the application
        app = SPPToolkitEnhanced()
        app.run()
        
        print("✅ Application closed successfully")
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all source files are in the 'src' directory")
        input("Press Enter to exit...")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n🔍 Full error details:")
        traceback.print_exc()
        input("Press Enter to exit...")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)