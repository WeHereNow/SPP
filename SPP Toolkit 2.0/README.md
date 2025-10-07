# SPP Toolkit 2.0
## Industrial PLC and Vision System Validation Toolkit

### Overview
SPP Toolkit 2.0 is a comprehensive industrial automation validation tool designed for SmartPack Pro (SPP) systems. It provides validation capabilities for PLCs, vision systems (Cognex), network devices, and E-Stop monitoring.

### Features

#### 🔧 PLC Validation
- **G Par Bit Monitoring**: Comprehensive monitoring of all G Par configuration bits
  - `g_Par` (30 bits) - Main configuration parameters
  - `g_Par1` (8 bits) - Extended configuration parameters  
  - `g_ParNew` (21 bits) - Advanced feature parameters
  - `g_parTemp` (6 bits) - Temporary rollback parameters
- **Safety & E-Stop Status**: Real-time monitoring of all E-Stop channels
- **Project Verification**: PLC project name and version validation
- **CSV Export**: Export validation results for documentation

#### 📹 Cognex Vision System Validation
- **Configuration Backup**: Automatic backup of camera configurations
- **Upload Management**: Smart upload of new configurations when changes detected
- **Hash Verification**: Ensures configuration integrity
- **CSV Export**: Export validation results

#### 🌐 Network Validation
- **Device Discovery**: Ping and identify network devices
- **Connectivity Testing**: Verify network connectivity to all devices
- **Device Mapping**: Pre-configured device identification

#### 🛑 E-Stop Monitoring
- **Real-time Monitoring**: Continuous monitoring of E-Stop states
- **State Change Detection**: Automatic detection and logging of E-Stop changes
- **Session Reporting**: Comprehensive monitoring session reports
- **CSV Export**: Export state changes with timestamps

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Network**: Ethernet connection to PLC network

#### Network Requirements
- **PLC Network Access**: Direct network access to PLC IP addresses
- **Vision System Access**: Network access to Cognex cameras (if using vision validation)
- **Firewall**: Ensure ports 44818 (EtherNet/IP) are open for PLC communication

### Installation

#### Option 1: Standalone Executable (Linux/Mac - No Python Required!)
1. Download `SPP Toolkit 2.0.zip`
2. Extract to desired location
3. **Linux/Mac**: Run `./RUN_SPP_TOOLKIT.sh`
4. **Direct**: Run `SPP_Toolkit_2.0` executable directly

**⚠️ Windows Users**: The included executable is for Linux. For Windows, use Option 2 (Python version) or build your own Windows executable.

#### Option 2: Python Installation (Recommended for Windows)
1. Install Python 3.8+ from [python.org](https://python.org)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
   Or double-click `SPP_Toolkit_2.0.bat` (Windows) or `./SPP_Toolkit_2.0.sh` (Linux/Mac)

#### Option 3: Build Windows Executable
1. Install Python 3.8+ and PyInstaller: `pip install pyinstaller`
2. Run: `python build_windows_executable.py`
3. Use the generated `SPP_Toolkit_2.0.exe`

### Configuration

#### PLC Settings
- **Default IP**: 11.200.0.10 (configurable in GUI)
- **Connection Timeout**: 5 seconds
- **Read Timeout**: 10 seconds

#### Network Devices
Pre-configured device mappings:
- `11.200.1.31` - AL1422 IO Link
- `11.200.1.35` - Keyence IV4 Sensor
- Additional devices can be added in the GUI

#### E-Stop Tags
The toolkit monitors these E-Stop tags:
- `Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback`
- `Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA/B`
- `Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA/B`
- `Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA/B`
- `Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA/B`

### Usage

#### Starting the Application
1. Launch `SPP Toolkit 2.0.exe`
2. The main window will open with multiple tabs

#### PLC Validation
1. Go to "PLC Validation" tab
2. Enter PLC IP address (default: 11.200.0.10)
3. Click "Run Validation"
4. Review results in the text area
5. Export results to CSV if needed

#### Cognex Validation
1. Go to "Cognex Validation" tab
2. Configure camera settings if needed
3. Click "Run Backup & Upload"
4. Review validation results
5. Export results to CSV if needed

#### Network Validation
1. Go to "Network Validation" tab
2. Click "Validate Network"
3. Review connectivity results

#### E-Stop Monitoring
1. Go to "E-Stop Monitor" tab
2. Click "Start Monitoring" to begin real-time monitoring
3. Click "Stop Monitoring" to end the session
4. Review state changes and generate reports
5. Export changes to CSV

### File Structure
```
SPP Toolkit 2.0/
├── SPP_Toolkit_2.0              # Standalone executable (8.2 MB)
├── RUN_SPP_TOOLKIT.bat          # Windows launcher (executable version)
├── RUN_SPP_TOOLKIT.sh           # Linux/Mac launcher (executable version)
├── main.py                      # Python entry point
├── SPP_Toolkit_2.0.bat          # Windows launcher (Python version)
├── SPP_Toolkit_2.0.sh           # Linux/Mac launcher (Python version)
├── build_executable.py          # Executable builder script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── INSTALLATION.md               # Installation guide
├── VERSION.txt                   # Version information
├── src/                          # Source code
│   ├── spp_toolkit_enhanced.py   # Main GUI application
│   ├── config.py                 # Configuration management
│   ├── logger.py                 # Logging utilities
│   ├── plc_communication.py      # PLC communication module
│   ├── plc_verification.py       # PLC verification module
│   ├── cognex_validation.py      # Cognex validation module
│   ├── network_validation.py     # Network validation module
│   ├── estop_monitor.py          # E-Stop monitoring module
│   └── tag_validator.py          # Tag validation utilities
├── config/                       # Configuration files
├── docs/                         # Documentation
└── logs/                         # Log files (created at runtime)
```

### Troubleshooting

#### Common Issues

**PLC Connection Failed**
- Verify PLC IP address is correct
- Check network connectivity (ping the PLC)
- Ensure EtherNet/IP port (44818) is open
- Verify PLC is in RUN mode

**E-Stop Monitor Shows "Unknown"**
- This is normal when not connected to a PLC
- Connect to PLC and start monitoring to see actual states
- Check E-Stop tag names match your PLC program

**Cognex Validation Fails**
- Verify camera IP addresses are correct
- Check network connectivity to cameras
- Ensure camera credentials are correct
- Verify camera is in proper mode for configuration access

#### Log Files
Log files are created in the `logs/` directory and contain detailed information about:
- PLC communication attempts
- E-Stop monitoring sessions
- Validation results
- Error messages

### Support

#### Getting Help
1. Check the log files in the `logs/` directory
2. Review this README for common solutions
3. Verify network connectivity and PLC status
4. Ensure all required dependencies are installed

#### Version Information
- **Version**: 2.0
- **Build Date**: 2025-10-02
- **Compatible PLCs**: Allen-Bradley ControlLogix, CompactLogix, GuardLogix
- **Compatible Vision**: Cognex In-Sight series

### License
This software is provided for industrial automation validation purposes. Please ensure compliance with your organization's software policies.

### Changelog

#### Version 2.0 (2025-10-02)
- ✅ Complete G Par bit monitoring (g_Par, g_Par1, g_ParNew, g_parTemp)
- ✅ Enhanced E-Stop monitoring with state change detection
- ✅ Simplified PLC verification output
- ✅ Removed JSON export options (CSV only)
- ✅ Improved error handling and logging
- ✅ Network device validation
- ✅ Comprehensive session reporting
- ✅ Executable packaging for easy distribution

#### Previous Versions
- Version 1.x: Basic PLC validation and E-Stop monitoring