SPP All-In-One Toolkit - Windows Executable Package
==================================================

CONTENTS:
---------
- SPP_Toolkit.exe       : Main application executable
- requirements.txt      : Python dependencies (for reference)
- README.txt            : This file

QUICK START:
------------
1. Double-click SPP_Toolkit.exe to launch the application
2. No installation required - all dependencies are bundled

FEATURES:
---------
- Network Validation: Test connectivity to all devices
- PLC Validation: Read and verify PLC parameters
- Cognex Validation: Backup and upload Cognex camera configurations
- PLC Verification: Verify PLC project name, version, and checksum
- HMI Verification: Verify HMI runtime application
- Faults & Warnings: Load DOCX mapping and scan PLC for active faults

REQUIREMENTS:
-------------
- Windows 7 or later
- Network access to industrial devices

USAGE NOTES:
------------
- The application requires network access to communicate with PLCs, HMIs, and Cognex devices
- For Faults & Warnings feature, prepare a DOCX file with fault mappings
- All validation results can be exported to CSV/JSON files

DEPENDENCIES:
-------------
The following Python packages are bundled in the executable:
- pylogix: For PLC communication
- python-docx: For DOCX file parsing
- pandas: For data processing
- matplotlib: For reporting
- reportlab: For PDF generation

TROUBLESHOOTING:
----------------
1. If the application doesn't start:
   - Check Windows Event Viewer for errors
   - Ensure no antivirus is blocking the executable
   - Run as Administrator if needed

2. If device connections fail:
   - Verify network connectivity
   - Check firewall settings
   - Ensure correct IP addresses

3. For missing features:
   - Some features require optional dependencies
   - Check the status indicators in the main window

SUPPORT:
--------
For issues or questions, refer to the project documentation.

VERSION:
--------
Enhanced SPP Toolkit v1.0
Build Date: 2025-10-07