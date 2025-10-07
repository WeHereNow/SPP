#!/bin/bash
# SPP Toolkit 2.0 - Linux/Mac Executable Launcher
# No Python installation required!

echo "============================================================"
echo "SPP Toolkit 2.0 - Industrial Validation Toolkit"
echo "============================================================"
echo "Standalone Executable Version - No Python Required!"
echo

# Check if executable exists
if [ ! -f "SPP_Toolkit_2.0" ]; then
    echo "ERROR: SPP_Toolkit_2.0 not found"
    echo "Please make sure you're running this from the SPP Toolkit 2.0 directory"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Make executable if needed
chmod +x SPP_Toolkit_2.0

echo "Starting SPP Toolkit 2.0..."
echo "This may take a few moments to load..."
echo

# Run the standalone executable
./SPP_Toolkit_2.0

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error"
    read -p "Press Enter to exit..."
fi