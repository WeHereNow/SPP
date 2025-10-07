# SPP Toolkit - Standalone Executable Build Guide

## 🎯 Goal
Create a Windows executable (.exe) that runs WITHOUT requiring Python installation.

---

## 📋 Prerequisites

**You need:**
- A Windows 10/11 computer
- Python 3.8 or higher installed
- Internet connection
- The SPP_Toolkit_2.0_FINAL.zip package

---

## 🚀 Quick Build (Automated)

### Step 1: Extract Package
1. Extract `SPP_Toolkit_2.0_FINAL.zip` to a folder
2. Open that folder in File Explorer

### Step 2: Build Executable
1. **Double-click** `BUILD_EXECUTABLE.bat`
2. Wait for the build to complete (2-5 minutes)
3. Press any key when prompted

### Step 3: Find Your Executable
1. Open the `dist\SPP_Toolkit\` folder
2. You'll see `SPP_Toolkit.exe` and supporting files

### Step 4: Create Deployment Package
1. Copy the entire `dist\SPP_Toolkit\` folder contents
2. Create a new folder called `SPP_Toolkit_Standalone`
3. Paste all files into it
4. Right-click the folder → Send to → Compressed (zipped) folder
5. Rename to `SPP_Toolkit_Standalone.zip`

### Step 5: Distribute
✅ Your `SPP_Toolkit_Standalone.zip` is ready!
- Workers just extract and double-click `SPP_Toolkit.exe`
- NO Python installation needed!
- NO dependency installation needed!

---

## 📁 What the Standalone Package Contains

```
SPP_Toolkit_Standalone.zip
├── SPP_Toolkit.exe           # Main executable (NO Python needed!)
├── _internal/                # Dependencies (auto-managed)
│   ├── Python DLLs
│   ├── Libraries
│   └── Supporting files
├── README.txt                # User instructions
└── RUN_STANDALONE.bat        # Optional launcher
```

**Total Size**: Approximately 25-40 MB (compressed)

---

## 🛠️ Manual Build (If Automated Fails)

### Step 1: Install PyInstaller
```batch
pip install pyinstaller
```

### Step 2: Run Build Command
```batch
pyinstaller spp_toolkit.spec --clean --noconfirm
```

### Step 3: Collect Files
The executable and dependencies will be in: `dist\SPP_Toolkit\`

---

## ⚙️ Build Configuration

The build uses `spp_toolkit.spec` which:
- ✅ Includes all required modules
- ✅ Bundles Python interpreter
- ✅ Includes pylogix and python-docx
- ✅ Creates GUI application (no console)
- ✅ Optimizes with UPX compression
- ✅ Excludes unused packages (matplotlib, pandas, etc.)

---

## 📦 Alternative: Portable Python Bundle

If PyInstaller doesn't work, create a portable bundle:

### Step 1: Download WinPython
1. Go to https://winpython.github.io/
2. Download WinPython 3.9+ (Zero edition)
3. Extract to a folder

### Step 2: Install Dependencies
```batch
cd WinPython-3.9.x\python-3.9.x
python.exe -m pip install pylogix python-docx
```

### Step 3: Copy Toolkit Files
Copy all `.py` files to the WinPython folder

### Step 4: Create Launcher
Create `RUN_TOOLKIT.bat`:
```batch
@echo off
.\python-3.9.x\python.exe spp_toolkit_enhanced.py
```

### Step 5: Package
Zip the entire WinPython folder → Portable toolkit!

---

## 🔍 Troubleshooting Build Issues

### "PyInstaller not found"
**Solution:**
```batch
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

### "Module not found" during build
**Solution:**
```batch
pip install pylogix python-docx
```

### Build succeeds but .exe crashes
**Solution:**
1. Check `build/spp_toolkit/warn-spp_toolkit.txt` for warnings
2. Try building with console enabled:
   - Edit `spp_toolkit.spec`
   - Change `console=False` to `console=True`
   - Rebuild

### .exe is too large
**Solution:**
- Install UPX compressor: https://upx.github.io/
- UPX is automatically used if installed
- Can reduce size by 50%

### Antivirus blocks .exe
**Solution:**
1. The .exe is safe (false positive)
2. Add exception in antivirus
3. Or use code signing certificate

---

## 📊 Build Size Comparison

| Method | Size | Python Required | Notes |
|--------|------|-----------------|-------|
| **Python Scripts** | 200 KB | ✅ Yes | Current package |
| **PyInstaller .exe** | 25-40 MB | ❌ No | Best for distribution |
| **Portable Python** | 50-100 MB | ❌ No | Alternative method |
| **Zipapp .pyz** | 200 KB | ✅ Yes | Single file, needs Python |

---

## ✅ Verification Checklist

After building, verify:
- [ ] SPP_Toolkit.exe runs without errors
- [ ] Application window opens correctly
- [ ] All tabs are accessible
- [ ] Can connect to test PLC
- [ ] Network validation works
- [ ] File exports work
- [ ] Application closes cleanly

---

## 📝 For IT/Admin: Deployment

### Step 1: Build on Windows
Run `BUILD_EXECUTABLE.bat` on a Windows machine

### Step 2: Test Executable
1. Copy `dist\SPP_Toolkit\` to a clean Windows machine (no Python)
2. Run `SPP_Toolkit.exe`
3. Verify all features work

### Step 3: Create Distribution Package
```
SPP_Toolkit_Standalone\
├── SPP_Toolkit.exe
├── _internal\          (PyInstaller files)
├── README.txt          (User instructions)
└── config\             (Optional: pre-configured settings)
```

### Step 4: Distribute
1. Zip the folder: `SPP_Toolkit_Standalone.zip`
2. Distribute to workers
3. Instructions: "Extract and run SPP_Toolkit.exe"

---

## 🎯 End User Instructions (Standalone Version)

**For Workers (Non-Technical):**

1. **Extract** `SPP_Toolkit_Standalone.zip` to any folder
2. **Open** the extracted folder
3. **Double-click** `SPP_Toolkit.exe`
4. **Done!** The application will start

**No installation needed!**
**No Python needed!**
**Just extract and run!**

---

## 🔄 Updating the Standalone Version

### When Code Changes:
1. Update Python source files
2. Run `BUILD_EXECUTABLE.bat` again
3. Create new distribution ZIP
4. Deploy updated package

### Version Control:
- Keep track of which .exe version is deployed
- Include VERSION.txt in distribution
- Test thoroughly before deploying updates

---

## 📞 Support

### Build Issues:
1. Check Python version: `python --version` (need 3.8+)
2. Check PyInstaller version: `pip show pyinstaller`
3. Review build warnings in `build\spp_toolkit\warn-spp_toolkit.txt`
4. Try manual build steps

### Runtime Issues:
1. Check if all DLLs are in `_internal\` folder
2. Run with console enabled to see errors
3. Check Windows Event Viewer for crash details

---

## 🎉 Success!

Once built, your standalone executable:
- ✅ Runs on any Windows 10/11 machine
- ✅ No Python installation required
- ✅ No dependency installation required
- ✅ Single double-click to run
- ✅ Perfect for non-technical workers

---

**Next Steps:**
1. Build the executable using `BUILD_EXECUTABLE.bat`
2. Test on a clean Windows machine
3. Create deployment ZIP
4. Distribute to workers

**Build Time:** 2-5 minutes  
**Result:** Production-ready standalone application!
