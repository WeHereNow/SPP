# SPP Toolkit 2.0 - Windows Installation Guide

## 🚨 **Important Note**
The current package contains a **Linux executable** (`SPP_Toolkit_2.0` without `.exe`). For Windows, you have several options:

## 🎯 **Option 1: Use Python Version (Recommended for Windows)**

### Quick Setup
1. **Install Python 3.8+** from [python.org](https://python.org)
   - ✅ Check "Add Python to PATH" during installation
2. **Extract** `SPP Toolkit 2.0.zip`
3. **Open Command Prompt** in the SPP Toolkit 2.0 folder
4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```
5. **Run the application**:
   ```cmd
   python main.py
   ```
   Or double-click `SPP_Toolkit_2.0.bat`

### Why This Option?
- ✅ **Guaranteed to work** on Windows
- ✅ **No compatibility issues**
- ✅ **Easy to troubleshoot**
- ✅ **Can be updated easily**

## 🔧 **Option 2: Build Windows Executable**

If you want a standalone executable for Windows:

1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Extract** `SPP Toolkit 2.0.zip`
3. **Open Command Prompt** in the SPP Toolkit 2.0 folder
4. **Install PyInstaller**:
   ```cmd
   pip install pyinstaller
   ```
5. **Build Windows executable**:
   ```cmd
   python build_windows_executable.py
   ```
6. **Run the executable**:
   ```cmd
   SPP_Toolkit_2.0.exe
   ```

## ⚠️ **Option 3: Try Linux Executable (Not Recommended)**

The package includes a Linux executable that **may not work** on Windows:

1. **Extract** `SPP Toolkit 2.0.zip`
2. **Run** `RUN_SPP_TOOLKIT.bat`
3. **If it fails**, use Option 1 or 2 above

## 🛠️ **Troubleshooting**

### "SPP_Toolkit_2.0.exe not found"
**Solution**: Use Option 1 (Python version) or Option 2 (build Windows executable)

### "Python not found"
**Solution**: Install Python 3.8+ from [python.org](https://python.org)

### "Module not found" errors
**Solution**: Run `pip install -r requirements.txt`

### "Permission denied" errors
**Solution**: Run Command Prompt as Administrator

## 📋 **System Requirements**

### For Python Version
- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Network**: Ethernet connection to PLC network

### For Executable Version
- **OS**: Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50MB free space
- **Network**: Ethernet connection to PLC network
- **Python**: Not required (but needed to build)

## 🎯 **Recommended Installation Steps**

### Step 1: Install Python
1. Go to [python.org](https://python.org)
2. Download Python 3.8 or higher
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Restart Command Prompt after installation

### Step 2: Install Dependencies
1. Open Command Prompt in the SPP Toolkit 2.0 folder
2. Run: `pip install -r requirements.txt`
3. Wait for installation to complete

### Step 3: Run Application
1. Run: `python main.py`
2. Or double-click: `SPP_Toolkit_2.0.bat`

## 🎉 **Success!**

Once installed, you'll have access to:
- 🔧 **PLC Validation**: Complete G Par bit monitoring
- 📹 **Cognex Vision**: Configuration backup and upload
- 🌐 **Network Validation**: Device discovery and connectivity
- 🛑 **E-Stop Monitoring**: Real-time state monitoring

## 📞 **Need Help?**

If you encounter issues:
1. Check this guide first
2. Verify Python is installed and in PATH
3. Try running from Command Prompt to see error messages
4. Ensure all dependencies are installed
5. Check network connectivity to PLC

The Python version is the most reliable option for Windows systems!