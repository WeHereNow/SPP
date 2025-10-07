# SPP All-In-One Toolkit 2.0

**Industrial Automation Toolkit for PLC Validation, Network Testing, and Device Management**

---

## 🚀 Quick Start (No Python Required!)

### Windows Users
1. Extract the ZIP file to any folder
2. Double-click `SPP_Toolkit.bat` to run the application
3. That's it! The toolkit will start automatically

---

## 📋 Features

### 1. **Network Validation**
- Concurrent ping testing for multiple devices
- Response time tracking
- Automatic device discovery
- CSV export for reports

### 2. **PLC Validation**
- Read and validate PLC parameters (g_Par, g_Par1, g_ParNew, g_parTemp)
- Safety & E-Stop status monitoring
- Real-time tag reading
- Connection diagnostics
- Comprehensive reporting

### 3. **E-Stop Monitoring**
- Real-time E-Stop state change detection
- Individual channel monitoring (A/B)
- Automatic change logging
- Session reports with statistics
- CSV export with timestamps

### 4. **Cognex Vision System**
- Configuration backup and comparison
- Automatic upload when differences detected
- Hash verification for integrity
- Multiple device support

### 5. **PLC Verification**
- Project name validation
- Version checking
- Controller information
- Comprehensive validation reports

### 6. **Faults & Warnings**
- DOCX file parsing for fault mappings
- Active fault scanning from PLC
- Resolution guidance
- Detailed fault reports

---

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB
- **Storage**: 100MB free space
- **Network**: Ethernet connection to PLC/device network

### Network Requirements
- Access to PLC network (typically 11.200.0.x)
- EtherNet/IP port 44818 (PLC communication)
- Telnet port 23 (Cognex communication)

---

## 📖 How to Use

### Network Validation
1. Open the **Network Validation** tab
2. Click **Run Validation**
3. View results in the output panel
4. Click **Export CSV** to save results

### PLC Validation
1. Open the **PLC Validation** tab
2. Enter PLC IP address (default: 11.200.0.10)
3. Click **Test IP** to verify connectivity
4. Click **Run Validation** to read all parameters
5. Use **Diagnose Connection** for troubleshooting

### E-Stop Monitoring
1. Open the **E-Stop Monitor** tab
2. Enter PLC IP address
3. Set monitoring interval (default: 1.0 second)
4. Click **Start Monitoring**
5. Watch for state changes in real-time
6. Click **Export Changes CSV** to save data
7. Click **Stop Monitoring** when done

### Cognex Validation
1. Open the **Cognex Validation** tab
2. Select .cfg files for each device (Browse button)
3. Click **Run Backup & Upload**
4. System will:
   - Backup current configuration
   - Compare with selected file
   - Upload if different
   - Display results

### PLC Verification
1. Open the **PLC Verification** tab
2. Enter PLC IP address
3. Enter expected project name (optional)
4. Click **Verify PLC**
5. View project information and validation results

### Faults & Warnings
1. Open the **Faults & Warnings** tab
2. Click **Load DOCX** and select fault mapping file
3. Enter PLC IP address
4. Click **Scan PLC** to find active faults
5. View descriptions and resolutions

---

## ⌨️ Keyboard Shortcuts

- `Ctrl+N` - Network Validation tab
- `Ctrl+P` - PLC Validation tab
- `Ctrl+E` - E-Stop Monitor tab
- `Ctrl+C` - Cognex Validation tab
- `Ctrl+V` - PLC Verification tab
- `Ctrl+F` - Faults & Warnings tab
- `Ctrl+S` - Settings tab
- `F5` - Refresh current tab

---

## 🛠️ Troubleshooting

### "Cannot connect to PLC"
**Check:**
1. PLC is powered on and in RUN mode
2. Network cable is connected
3. Computer is on same network as PLC (11.200.0.x)
4. IP address is correct
5. No firewall blocking port 44818

### "E-Stop states show as UNKNOWN"
**Check:**
1. PLC connection is working (use PLC Validation first)
2. Safety program is loaded and running
3. E-Stop tags are correctly mapped

### "Cognex connection fails"
**Check:**
1. Vision system is powered on
2. IP address is correct
3. Telnet port 23 is accessible
4. No firewall blocking telnet

### "DOCX parsing fails"
**Check:**
1. File is valid .docx format
2. Tables have TAG | Description | Resolution columns
3. Tags follow format: {[PLC]Alarm_Fault[X].Y}

---

## 📊 Configuration

Access the **Settings** tab to configure:

### Network Settings
- Default ping probes: 3
- Default timeout: 700ms
- Retry count and delays

### PLC Settings
- Default IP address
- Connection timeout
- Read timeout

### E-Stop Monitoring
- Default monitoring interval
- History size limit
- Auto-start options

---

## 📁 File Locations

- **Logs**: `logs/spp_toolkit_YYYYMMDD.log`
- **Backups**: `backups/` (Cognex configs)
- **Exports**: Current directory (CSV files)
- **Config**: `config/` (settings)

---

## 🔒 Security Features

- Input validation for all IP addresses
- Command sanitization for device communication
- File path validation to prevent traversal attacks
- Connection timeout enforcement
- Secure cleanup on exit

---

## 📝 Export Formats

### CSV Exports Include:
- **Network**: IP, Device Name, Status, Response Time, Attempts
- **E-Stop**: Timestamp, E-Stop Name, Old State, New State, Duration
- **Cognex**: Device Name, IP, Backup Status, File Match, Upload Status
- **PLC Verification**: IP, Project Name, Version, Validation Results

---

## ⚠️ Important Notes

1. **Do not modify files** while the application is running
2. **Always stop E-Stop monitoring** before closing the application
3. **Review Cognex backups** before uploading new configurations
4. **Close PLC connections** properly using application exit (X button)
5. **Keep backups** of all configuration files

---

## 🆘 Support

For issues or questions:
1. Check the log files in `logs/` directory
2. Use **Diagnose Connection** feature in PLC Validation
3. Review this README for troubleshooting steps
4. Contact your system administrator

---

## 📋 Version Information

**Version**: 2.0.0  
**Release Date**: 2025-10-07  
**Platform**: Windows 10/11 (64-bit)

---

## 🏗️ For Developers

### Running from Source (Python Required)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python spp_toolkit_enhanced.py
```

### Required Python Packages
- pylogix >= 1.4.0
- python-docx >= 0.8.11

### Optional Packages (for enhanced features)
- pandas >= 1.5.0
- matplotlib >= 3.6.0
- reportlab >= 3.6.0

---

**Made with ❤️ for Industrial Automation**
