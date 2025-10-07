# E Stop State Change Monitoring

This document describes the E Stop state change monitoring functionality added to the SPP All-In-One Toolkit.

## Overview

The E Stop monitoring system provides real-time monitoring of individual E Stop states, detecting and logging state changes with detailed information including timestamps, duration of previous states, and channel information for dual-channel E Stops.

## Features

### Individual E Stop Tracking
- **E-Stop Relay Feedback**: Main E-Stop relay feedback signal
- **Back Left E-Stop**: Dual-channel E-Stop button (Channels A & B)
- **Back Right E-Stop**: Dual-channel E-Stop button (Channels A & B)
- **Front E-Stop**: Dual-channel E-Stop button (Channels A & B)
- **Main Enclosure E-Stop**: Dual-channel E-Stop button (Channels A & B)

### State Change Detection
- Real-time monitoring with configurable intervals (0.1 to 60 seconds)
- Detection of state changes from ACTIVE to INACTIVE and vice versa
- Channel-specific monitoring for dual-channel E Stops
- Duration tracking for previous states
- Comprehensive logging of all state changes

### Reporting and Export
- Real-time status display
- Comprehensive monitoring reports
- JSON export of state change history
- Configurable history size limits

## Usage

### GUI Interface

1. **Open the E Stop Monitor Tab**: Use Ctrl+E or click on the "E Stop Monitor" tab
2. **Configure Settings**:
   - Enter PLC IP address (default: 11.200.0.10)
   - Set monitoring interval (default: 1.0 seconds)
3. **Start Monitoring**: Click "Start Monitoring" button
4. **View Changes**: State changes appear in real-time in the log area
5. **Get Status**: Click "Get Status" to view current states of all E Stops
6. **Generate Report**: Click "Generate Report" for a comprehensive status report
7. **Export Changes**: Click "Export Changes" to save state change history to JSON file
8. **Stop Monitoring**: Click "Stop Monitoring" when done

### Programmatic Interface

```python
from plc_communication import EnhancedPLCValidator
from estop_monitor import EStopStateChange

# Create validator
validator = EnhancedPLCValidator("11.200.0.10")

# Add callback for state changes
def on_estop_change(change: EStopStateChange):
    print(f"E Stop {change.estop_name}: {change.old_state.value} -> {change.new_state.value}")

validator.add_estop_change_callback(on_estop_change)

# Start monitoring
validator.start_estop_monitoring(1.0)  # 1 second interval

# Get current status
status = validator.get_estop_status()

# Generate report
report = validator.generate_estop_report()

# Export changes
validator.export_estop_changes("estop_changes.json")

# Stop monitoring
validator.stop_estop_monitoring()
validator.close()
```

## Configuration

### Settings Tab Configuration

Access the Settings tab to configure E Stop monitoring parameters:

- **Default Monitor Interval**: Default monitoring interval in seconds (0.1-60.0)
- **Max History Size**: Maximum number of state changes to keep in memory (default: 1000)
- **Auto-start monitoring**: Automatically start monitoring when opening the E Stop Monitor tab
- **Log all state changes**: Enable detailed logging of all state changes

### E Stop Definitions

The system monitors the following E Stop tags:

| E Stop | Location | Tag | Channels |
|--------|----------|-----|----------|
| E-Stop Relay Feedback | Safety System | `Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback` | Single |
| Back Left E-Stop | Machine Back Left | `Program:SafetyProgram.SDIN_MachineBackLeftESTOP` | A, B |
| Back Right E-Stop | Machine Back Right | `Program:SafetyProgram.SDIN_MachineBackRightESTOP` | A, B |
| Front E-Stop | Machine Front | `Program:SafetyProgram.SDIN_MachineFrontESTOP` | A, B |
| Main Enclosure E-Stop | Main Enclosure | `Program:SafetyProgram.SDIN_MainEnclosureESTOP` | A, B |

## State Definitions

### E Stop States
- **ACTIVE**: E Stop is pressed/active (safety state)
- **INACTIVE**: E Stop is released/normal operation
- **UNKNOWN**: State not yet determined or read error

### Dual-Channel Logic
For dual-channel E Stops:
- Overall state is **ACTIVE** if either Channel A OR Channel B is ACTIVE
- Overall state is **INACTIVE** only if both channels are INACTIVE
- Individual channel states are tracked separately

## Data Structures

### EStopStateChange
```python
@dataclass
class EStopStateChange:
    timestamp: datetime          # When the change occurred
    estop_name: str             # Name of the E Stop
    old_state: EStopState       # Previous state
    new_state: EStopState       # New state
    channel: Optional[str]      # Channel (A/B) for dual-channel E Stops
    duration_seconds: Optional[float]  # Duration of previous state
```

### EStopStatus
```python
@dataclass
class EStopStatus:
    name: str                   # E Stop name
    state: EStopState          # Current overall state
    last_change: Optional[EStopStateChange]  # Most recent change
    channel_a_state: Optional[EStopState]    # Channel A state
    channel_b_state: Optional[EStopState]    # Channel B state
    total_changes: int          # Total number of changes
    last_read_time: Optional[datetime]       # Last successful read
    read_error: Optional[str]   # Last read error, if any
```

## Export Format

State changes are exported to JSON format with the following structure:

```json
{
  "export_timestamp": "2024-01-15T10:30:00",
  "total_changes": 25,
  "changes": [
    {
      "timestamp": "2024-01-15T10:25:30",
      "estop_name": "Front E-Stop",
      "old_state": "inactive",
      "new_state": "active",
      "channel": "A",
      "duration_seconds": 45.2
    }
  ]
}
```

## Error Handling

The system includes comprehensive error handling:

- **Connection Errors**: Automatic retry with exponential backoff
- **Read Errors**: Individual tag read failures are logged and reported
- **Network Issues**: Graceful handling of network connectivity problems
- **Invalid Data**: Validation of PLC tag values and state transitions

## Performance Considerations

- **Monitoring Interval**: Lower intervals provide faster detection but increase PLC load
- **History Size**: Larger history uses more memory but provides more historical data
- **Concurrent Monitoring**: Multiple monitoring sessions can run simultaneously
- **Thread Safety**: All operations are thread-safe for concurrent access

## Troubleshooting

### Common Issues

1. **"E Stop monitoring not available"**: Enhanced modules not loaded
   - Ensure `estop_monitor.py` is in the same directory
   - Check that all dependencies are installed

2. **Connection failures**: PLC not reachable
   - Verify PLC IP address is correct
   - Check network connectivity
   - Ensure PLC is powered on and running

3. **No state changes detected**: E Stops not changing
   - Verify E Stop buttons are being pressed/released
   - Check PLC tag names are correct
   - Ensure PLC program is running

4. **Read errors**: Individual tag read failures
   - Check PLC tag names and paths
   - Verify PLC program structure
   - Check for PLC communication issues

### Debug Mode

Enable debug logging by setting the logger level to DEBUG:

```python
import logging
logging.getLogger("EStopMonitor").setLevel(logging.DEBUG)
```

## Integration

The E Stop monitoring system integrates with:

- **PLC Communication Module**: Uses existing PLC connection management
- **Enhanced Toolkit UI**: Provides dedicated monitoring tab
- **Configuration System**: Uses centralized configuration management
- **Logging System**: Integrates with application logging

## Future Enhancements

Potential future improvements:

- **Alarm Integration**: Connect to alarm systems for critical state changes
- **Trend Analysis**: Historical trend analysis and reporting
- **Remote Monitoring**: Web-based monitoring interface
- **Database Storage**: Persistent storage of state change history
- **Custom E Stop Definitions**: User-configurable E Stop definitions
- **Notification System**: Email/SMS alerts for state changes