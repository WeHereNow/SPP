# SPP Toolkit 2.0 - Installation Guide

## Quick Start (Executable Version)

### For End Users
1. **Download** `SPP Toolkit 2.0.zip`
2. **Extract** to your desired location (e.g., `C:\SPP Toolkit 2.0\`)
3. **Run** `SPP_Toolkit_2.0.exe` (Windows) or `SPP_Toolkit_2.0` (Linux/Mac)

### For Developers/Advanced Users

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Installation Steps

1. **Extract the package**
   ```bash
   unzip "SPP Toolkit 2.0.zip"
   cd "SPP Toolkit 2.0"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Windows
   python main.py
   # or double-click SPP_Toolkit_2.0.bat
   
   # Linux/Mac
   python3 main.py
   # or run ./SPP_Toolkit_2.0.sh
   ```

## Building Executable from Source

If you want to build your own executable:

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build executable**
   ```bash
   python build_executable.py
   ```

3. **Find executable**
   - Windows: `dist/SPP_Toolkit_2.0.exe`
   - Linux/Mac: `dist/SPP_Toolkit_2.0`

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8+ (for source version)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Network**: Ethernet connection to PLC network

### Network Requirements
- **PLC Access**: Direct network access to PLC IP addresses
- **Ports**: EtherNet/IP port 44818 must be open
- **Firewall**: Configure firewall to allow PLC communication

## Configuration

### First Run Setup
1. Launch the application
2. Go to "Settings" tab
3. Configure default PLC IP address (default: 11.200.0.10)
4. Adjust timeouts if needed
5. Save settings

### Network Device Configuration
The toolkit comes pre-configured with common devices:
- `11.200.1.31` - AL1422 IO Link
- `11.200.1.35` - Keyence IV4 Sensor

Add additional devices in the Network Validation tab.

## Troubleshooting

### Common Installation Issues

**"Python not found" Error**
- Install Python 3.8+ from [python.org](https://python.org)
- Make sure Python is added to PATH during installation
- Restart command prompt/terminal after installation

**"Module not found" Errors**
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory
- Check internet connection for package downloads

**Executable Won't Run**
- Try running from command line to see error messages
- Check Windows Defender/Antivirus isn't blocking the file
- Ensure all files are extracted from the ZIP

**PLC Connection Issues**
- Verify PLC IP address is correct
- Test network connectivity: `ping <PLC_IP>`
- Check PLC is in RUN mode
- Verify EtherNet/IP port 44818 is open

### Getting Help
1. Check log files in `logs/` directory
2. Run from command line to see detailed error messages
3. Verify network connectivity and PLC status
4. Review this installation guide

## File Structure After Installation

```
SPP Toolkit 2.0/
├── SPP_Toolkit_2.0.exe          # Main executable (Windows)
├── SPP_Toolkit_2.0              # Main executable (Linux/Mac)
├── SPP_Toolkit_2.0.bat          # Windows launcher
├── SPP_Toolkit_2.0.sh           # Linux/Mac launcher
├── main.py                      # Python entry point
├── build_executable.py          # Executable builder script
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── INSTALLATION.md              # This file
├── src/                         # Source code
│   ├── spp_toolkit_enhanced.py  # Main GUI application
│   ├── config.py                # Configuration management
│   ├── logger.py                # Logging utilities
│   ├── plc_communication.py     # PLC communication
│   ├── plc_verification.py      # PLC verification
│   ├── cognex_validation.py     # Cognex validation
│   ├── network_validation.py    # Network validation
│   ├── estop_monitor.py         # E-Stop monitoring
│   └── tag_validator.py         # Tag validation
├── config/                      # Configuration files
├── docs/                        # Documentation
└── logs/                        # Log files (created at runtime)
```

## Uninstallation

### Executable Version
Simply delete the `SPP Toolkit 2.0` folder.

### Python Version
1. Delete the `SPP Toolkit 2.0` folder
2. Optionally uninstall Python packages:
   ```bash
   pip uninstall pylogix ping3 psutil pandas openpyxl
   ```

## Support

For technical support:
1. Check log files in `logs/` directory
2. Review documentation in `docs/` directory
3. Verify system requirements and network connectivity
4. Contact your system administrator for network/PLC access issues