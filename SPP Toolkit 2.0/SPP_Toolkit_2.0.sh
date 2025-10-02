#!/bin/bash
# SPP Toolkit 2.0 - Linux/Mac Launcher
# Industrial PLC and Vision System Validation Toolkit

echo "============================================================"
echo "SPP Toolkit 2.0 - Industrial Validation Toolkit"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found"
    echo "Please run this script from the SPP Toolkit 2.0 directory"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Make the script executable
chmod +x "$0"

# Run the application
echo "Starting SPP Toolkit 2.0..."
echo
python3 main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error"
    read -p "Press Enter to exit..."
fi