================================================================================
  SPP ALL-IN-ONE TOOLKIT 2.0 - STANDALONE VERSION
================================================================================

IMPORTANT: This package requires ONE-TIME BUILD on a Windows machine to create
the standalone executable. After building, workers need NO Python installation!

================================================================================
  QUICK START (For IT/Admin - Build the Executable)
================================================================================

STEP 1: BUILD EXECUTABLE (One-time, on Windows)
------------------------------------------------
1. Extract this ZIP to a folder on a Windows 10/11 computer
2. Double-click: BUILD_EXECUTABLE.bat
3. Wait 2-5 minutes for build to complete
4. Press any key when done

STEP 2: CREATE DEPLOYMENT PACKAGE
----------------------------------
1. Go to: dist\SPP_Toolkit\ folder
2. Copy ALL files and folders
3. Paste into new folder: SPP_Toolkit_Standalone
4. Right-click folder → Send to → Compressed (zipped) folder
5. Rename to: SPP_Toolkit_Standalone.zip

STEP 3: DISTRIBUTE TO WORKERS
------------------------------
1. Give workers: SPP_Toolkit_Standalone.zip
2. Workers extract ZIP
3. Workers double-click: SPP_Toolkit.exe
4. Done! NO Python needed!

================================================================================
  FOR WORKERS (After Executable is Built)
================================================================================

STEP 1: EXTRACT
---------------
Right-click SPP_Toolkit_Standalone.zip → Extract All

STEP 2: RUN
-----------
Open extracted folder → Double-click SPP_Toolkit.exe

STEP 3: USE
-----------
Application opens → No installation needed!

================================================================================
  WHAT'S IN THIS PACKAGE
================================================================================

Python Source Files:
- spp_toolkit_enhanced.py    (Main application)
- config.py                  (Configuration)
- logger.py                  (Logging system)
- input_validator.py         (Security validation)
- plc_communication.py       (PLC module)
- plc_verification.py        (PLC verification)
- network_validation.py      (Network testing)
- cognex_validation.py       (Cognex management)
- estop_monitor.py          (E-Stop monitoring)
- faults_warnings.py        (Fault processing)
- tag_validator.py          (Tag validation)

Build Tools:
- BUILD_EXECUTABLE.bat       (Creates standalone .exe)
- spp_toolkit.spec          (Build configuration)
- CREATE_ZIPAPP.bat         (Alternative: creates .pyz)

Launcher Scripts:
- SPP_Toolkit.bat           (Python version launcher)
- INSTALL.bat               (Install Python dependencies)
- RUN_STANDALONE.bat        (Standalone version launcher)

Documentation:
- README.md                  (Full user guide)
- QUICK_START.txt           (Quick reference)
- STANDALONE_BUILD_GUIDE.md (Build instructions)
- DEPLOYMENT_GUIDE.md       (IT deployment guide)
- VERSION.txt               (Version info)
- requirements.txt          (Python dependencies)

================================================================================
  BUILD REQUIREMENTS
================================================================================

To build the standalone executable you need:
- Windows 10 or 11 computer
- Python 3.8 or higher installed
- Internet connection (for downloading PyInstaller)
- 2-5 minutes build time
- 500 MB free disk space (temporary)

After building, the executable:
- Size: ~25-40 MB (compressed)
- Runs on: Any Windows 10/11 (no Python needed!)
- Contains: Everything needed to run

================================================================================
  TWO DEPLOYMENT OPTIONS
================================================================================

OPTION 1: STANDALONE EXECUTABLE (Recommended)
----------------------------------------------
Pro: No Python needed on worker machines
Pro: Simple double-click to run
Pro: Best for non-technical users
Con: Requires one-time build on Windows
Con: Larger file size (~40 MB)

How to use:
1. Build with BUILD_EXECUTABLE.bat (one-time)
2. Distribute the .exe package
3. Workers just run SPP_Toolkit.exe

OPTION 2: PYTHON VERSION
------------------------
Pro: Smaller file size (~200 KB)
Pro: Ready to use immediately
Con: Requires Python on worker machines
Con: Requires running INSTALL.bat first

How to use:
1. Workers install Python 3.8+
2. Workers extract ZIP
3. Workers run SPP_Toolkit.bat (auto-installs packages)

================================================================================
  TROUBLESHOOTING BUILD
================================================================================

Problem: "Python not found"
Solution: Install Python from python.org, check "Add to PATH"

Problem: "BUILD_EXECUTABLE.bat fails"
Solution: Run as Administrator, check internet connection

Problem: "PyInstaller error"
Solution: Run: pip install --upgrade pyinstaller

Problem: "Built .exe doesn't run"
Solution: Build with console=True in spec file to see errors

Problem: "Antivirus blocks .exe"
Solution: Add exception (it's a false positive)

================================================================================
  FILE SIZE REFERENCE
================================================================================

Source Package:        62 KB    (SPP_Toolkit_2.0_FINAL.zip)
Standalone Package:    25-40 MB (SPP_Toolkit_Standalone.zip)
Portable Python:       50-100 MB (Alternative method)

Workers download:      Standalone package (once)
Workers extract to:    Any folder
Workers run:          SPP_Toolkit.exe (double-click)

================================================================================
  SUPPORT RESOURCES
================================================================================

For Build Help:
- See: STANDALONE_BUILD_GUIDE.md
- Check: build\spp_toolkit\warn-spp_toolkit.txt (after build)

For Usage Help:
- See: README.md
- See: QUICK_START.txt

For IT/Admin:
- See: DEPLOYMENT_GUIDE.md

For Errors:
- Check: logs\ folder
- Use: Diagnose Connection feature

================================================================================
  VERSION INFORMATION
================================================================================

Package Version:     2.0.0
Release Date:       October 7, 2025
Platform:           Windows 10/11 (64-bit)
Python Required:    Only for building (3.8+)
Runtime Required:   None (after build)

Build Method:       PyInstaller
Compression:        UPX (automatic if available)
Dependencies:       pylogix, python-docx (included in .exe)

================================================================================
  NEXT STEPS
================================================================================

1. READ: STANDALONE_BUILD_GUIDE.md (detailed instructions)
2. BUILD: Run BUILD_EXECUTABLE.bat on Windows
3. TEST: Run SPP_Toolkit.exe on a test machine
4. PACKAGE: Create SPP_Toolkit_Standalone.zip
5. DISTRIBUTE: Give to workers
6. DONE: Workers extract and run!

================================================================================

Questions? See STANDALONE_BUILD_GUIDE.md for complete instructions.

Your toolkit will be completely standalone after building - no Python needed!

================================================================================
