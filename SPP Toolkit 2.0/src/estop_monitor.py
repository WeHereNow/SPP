"""
E Stop State Change Monitor
Monitors individual E Stop states for changes and provides detailed logging and reporting
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    from config import config
    from logger import get_logger
except ImportError:
    # Fallback for when modules aren't available
    class MockConfig:
        class EStopConfig:
            default_monitor_interval = 1.0  # seconds
            change_detection_enabled = True
            log_all_changes = True
            max_history_size = 1000
        estop = EStopConfig()
    
    config = MockConfig()
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)

class EStopState(Enum):
    """E Stop state enumeration"""
    UNKNOWN = "unknown"
    ACTIVE = "active"      # E Stop is pressed/active (safety state)
    INACTIVE = "inactive"  # E Stop is released/normal operation

@dataclass
class EStopInfo:
    """Information about a specific E Stop"""
    name: str
    tag: str
    description: str
    location: str
    is_dual_channel: bool = False
    channel_a_tag: Optional[str] = None
    channel_b_tag: Optional[str] = None

@dataclass
class EStopStateChange:
    """Record of an E Stop state change"""
    timestamp: datetime
    estop_name: str
    old_state: EStopState
    new_state: EStopState
    channel: Optional[str] = None  # For dual-channel E Stops
    duration_seconds: Optional[float] = None  # How long the previous state lasted

@dataclass
class EStopStatus:
    """Current status of an E Stop"""
    name: str
    state: EStopState
    last_change: Optional[EStopStateChange] = None
    channel_a_state: Optional[EStopState] = None  # For dual-channel
    channel_b_state: Optional[EStopState] = None  # For dual-channel
    total_changes: int = 0
    last_read_time: Optional[datetime] = None
    read_error: Optional[str] = None

class EStopMonitor:
    """Monitors E Stop states for changes and provides detailed tracking"""
    
    def __init__(self, plc_connection_manager, logger=None):
        self.plc_connection_manager = plc_connection_manager
        self.logger = logger or get_logger("EStopMonitor")
        
        # E Stop definitions
        self.estop_definitions = self._initialize_estop_definitions()
        
        # Current states
        self.current_states: Dict[str, EStopStatus] = {}
        
        # State change history
        self.state_changes: List[EStopStateChange] = []
        
        # Monitoring control
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = config.estop.default_monitor_interval
        
        # Callbacks for state changes
        self.state_change_callbacks: List[Callable[[EStopStateChange], None]] = []
        
        # Initialize current states
        self._initialize_current_states()
    
    def _initialize_estop_definitions(self) -> Dict[str, EStopInfo]:
        """Initialize E Stop definitions with their tags and descriptions"""
        return {
            "relay_feedback": EStopInfo(
                name="E-Stop Relay Feedback",
                tag="Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback",
                description="Main E-Stop relay feedback signal",
                location="Safety System"
            ),
            "back_left": EStopInfo(
                name="Back Left E-Stop",
                tag="Program:SafetyProgram.SDIN_MachineBackLeftESTOP",
                description="Back left E-Stop button",
                location="Machine Back Left",
                is_dual_channel=True,
                channel_a_tag="Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA",
                channel_b_tag="Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB"
            ),
            "back_right": EStopInfo(
                name="Back Right E-Stop",
                tag="Program:SafetyProgram.SDIN_MachineBackRightESTOP",
                description="Back right E-Stop button",
                location="Machine Back Right",
                is_dual_channel=True,
                channel_a_tag="Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA",
                channel_b_tag="Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB"
            ),
            "front": EStopInfo(
                name="Front E-Stop",
                tag="Program:SafetyProgram.SDIN_MachineFrontESTOP",
                description="Front E-Stop button",
                location="Machine Front",
                is_dual_channel=True,
                channel_a_tag="Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA",
                channel_b_tag="Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB"
            ),
            "main_enclosure": EStopInfo(
                name="Main Enclosure E-Stop",
                tag="Program:SafetyProgram.SDIN_MainEnclosureESTOP",
                description="Main enclosure E-Stop button",
                location="Main Enclosure",
                is_dual_channel=True,
                channel_a_tag="Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA",
                channel_b_tag="Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB"
            )
        }
    
    def _initialize_current_states(self):
        """Initialize current states for all E Stops"""
        for estop_id, estop_info in self.estop_definitions.items():
            self.current_states[estop_id] = EStopStatus(
                name=estop_info.name,
                state=EStopState.UNKNOWN
            )
    
    def add_state_change_callback(self, callback: Callable[[EStopStateChange], None]):
        """Add a callback function to be called when E Stop states change"""
        self.state_change_callbacks.append(callback)
    
    def remove_state_change_callback(self, callback: Callable[[EStopStateChange], None]):
        """Remove a state change callback"""
        if callback in self.state_change_callbacks:
            self.state_change_callbacks.remove(callback)
    
    def _notify_state_change(self, change: EStopStateChange):
        """Notify all registered callbacks of a state change"""
        for callback in self.state_change_callbacks:
            try:
                callback(change)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
    def _bool_to_estop_state(self, value: bool) -> EStopState:
        """Convert boolean PLC value to E Stop state"""
        # In safety systems, True typically means E Stop is ACTIVE (pressed)
        # False means E Stop is INACTIVE (released)
        return EStopState.ACTIVE if value else EStopState.INACTIVE
    
    def read_current_states(self) -> Dict[str, EStopStatus]:
        """Read current E Stop states from PLC using the same approach as PLC validation"""
        try:
            # Use the same SAFETY_TAGS list as the PLC validation script
            safety_tags = [
                'Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback',
                'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA',
                'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB',
                'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA',
                'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB',
                'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA',
                'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB',
                'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA',
                'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB',
            ]
            
            # Create mapping from tags to E Stop IDs and channels
            tag_mapping = {
                'Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback': ('relay_feedback', None),
                'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA': ('back_left', 'A'),
                'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB': ('back_left', 'B'),
                'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA': ('back_right', 'A'),
                'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB': ('back_right', 'B'),
                'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA': ('front', 'A'),
                'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB': ('front', 'B'),
                'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA': ('main_enclosure', 'A'),
                'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB': ('main_enclosure', 'B'),
            }
            
            # Read all safety tags at once (same as PLC validation script)
            with self.plc_connection_manager.get_connection() as plc:
                results = plc.Read(safety_tags)
                
                if isinstance(results, list):
                    # Process results
                    for tag, result in zip(safety_tags, results):
                        estop_id, channel = tag_mapping[tag]
                        
                        if result.Status == "Success":
                            new_state = self._bool_to_estop_state(result.Value)
                            self._update_estop_state(estop_id, new_state, channel)
                        else:
                            self.logger.warning(f"Failed to read {tag}: {result.Status}")
                            self.current_states[estop_id].read_error = result.Status
                else:
                    self.logger.error(f"Expected list of results, got {type(results)}")
                    # Mark all as having read errors
                    for estop_status in self.current_states.values():
                        estop_status.read_error = "Invalid result type"
                
                # Update last read time
                current_time = datetime.now()
                for estop_status in self.current_states.values():
                    estop_status.last_read_time = current_time
                
        except Exception as e:
            self.logger.error(f"Error reading E Stop states: {e}")
            # Mark all as having read errors and update last read time
            current_time = datetime.now()
            for estop_status in self.current_states.values():
                estop_status.read_error = str(e)
                estop_status.last_read_time = current_time
        
        return self.current_states.copy()
    
    def _update_estop_state(self, estop_id: str, new_state: EStopState, channel: Optional[str] = None):
        """Update E Stop state and detect changes"""
        current_status = self.current_states[estop_id]
        old_state = current_status.state
        
        # Determine if this is a state change
        state_changed = False
        
        if self.estop_definitions[estop_id].is_dual_channel:
            # Dual channel E Stop - check both channels
            if channel == "A":
                old_channel_state = current_status.channel_a_state
                current_status.channel_a_state = new_state
                if old_channel_state != new_state:
                    state_changed = True
            elif channel == "B":
                old_channel_state = current_status.channel_b_state
                current_status.channel_b_state = new_state
                if old_channel_state != new_state:
                    state_changed = True
            
            # Overall state is ACTIVE if either channel is ACTIVE
            if current_status.channel_a_state == EStopState.ACTIVE or current_status.channel_b_state == EStopState.ACTIVE:
                overall_new_state = EStopState.ACTIVE
            else:
                overall_new_state = EStopState.INACTIVE
            
            if current_status.state != overall_new_state:
                current_status.state = overall_new_state
                state_changed = True
        else:
            # Single channel E Stop
            if old_state != new_state:
                current_status.state = new_state
                state_changed = True
        
        # Record state change if detected
        if state_changed:
            change = EStopStateChange(
                timestamp=datetime.now(),
                estop_name=current_status.name,
                old_state=old_state,
                new_state=new_state,
                channel=channel
            )
            
            # Calculate duration if we have a previous change
            if current_status.last_change:
                duration = (change.timestamp - current_status.last_change.timestamp).total_seconds()
                change.duration_seconds = duration
            
            # Update status
            current_status.last_change = change
            current_status.total_changes += 1
            current_status.read_error = None
            
            # Add to history
            self.state_changes.append(change)
            
            # Limit history size
            if len(self.state_changes) > config.estop.max_history_size:
                self.state_changes = self.state_changes[-config.estop.max_history_size:]
            
            # Log the change
            self.logger.info(f"E Stop State Change: {change.estop_name} -> {change.new_state.value} "
                           f"(was {change.old_state.value})" + 
                           (f" [Channel {change.channel}]" if change.channel else ""))
            
            # Notify callbacks
            self._notify_state_change(change)
    
    def start_monitoring(self, interval: Optional[float] = None):
        """Start continuous monitoring of E Stop states"""
        if self.monitoring_active:
            self.logger.warning("E Stop monitoring is already active")
            return
        
        if interval:
            self.monitor_interval = interval
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"Started E Stop monitoring with {self.monitor_interval}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        self.logger.info("Stopped E Stop monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.read_current_states()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of all E Stop states"""
        # Attempt to read current states first
        self.read_current_states()
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "monitor_interval": self.monitor_interval,
            "estops": {}
        }
        
        for estop_id, status in self.current_states.items():
            estop_info = self.estop_definitions[estop_id]
            summary["estops"][estop_id] = {
                "name": status.name,
                "location": estop_info.location,
                "description": estop_info.description,
                "current_state": status.state.value,
                "is_dual_channel": estop_info.is_dual_channel,
                "channel_a_state": status.channel_a_state.value if status.channel_a_state else None,
                "channel_b_state": status.channel_b_state.value if status.channel_b_state else None,
                "total_changes": status.total_changes,
                "last_change_time": status.last_change.timestamp.isoformat() if status.last_change else None,
                "last_read_time": status.last_read_time.isoformat() if status.last_read_time else None,
                "read_error": status.read_error
            }
        
        return summary
    
    def get_recent_changes(self, count: int = 10) -> List[EStopStateChange]:
        """Get the most recent state changes"""
        return self.state_changes[-count:] if self.state_changes else []
    
    def get_changes_for_estop(self, estop_id: str, count: int = 10) -> List[EStopStateChange]:
        """Get recent changes for a specific E Stop"""
        estop_name = self.estop_definitions[estop_id].name
        changes = [change for change in self.state_changes if change.estop_name == estop_name]
        return changes[-count:] if changes else []
    
    def clear_history(self):
        """Clear the state change history"""
        self.state_changes.clear()
        self.logger.info("E Stop state change history cleared")
    
    def export_changes_to_json(self, filename: str):
        """Export state changes to JSON file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_changes": len(self.state_changes),
                "changes": []
            }
            
            for change in self.state_changes:
                export_data["changes"].append({
                    "timestamp": change.timestamp.isoformat(),
                    "estop_name": change.estop_name,
                    "old_state": change.old_state.value,
                    "new_state": change.new_state.value,
                    "channel": change.channel,
                    "duration_seconds": change.duration_seconds
                })
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.logger.info(f"Exported {len(self.state_changes)} state changes to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting changes to JSON: {e}")
    
    def export_changes_to_csv(self, filename: str):
        """Export state changes to CSV file with timestamps"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'date', 'time', 'estop_name', 'location', 
                    'old_state', 'new_state', 'channel', 'duration_seconds'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for change in self.state_changes:
                    # Find estop_id from estop_name
                    estop_id = None
                    for eid, estop_def in self.estop_definitions.items():
                        if estop_def.name == change.estop_name:
                            estop_id = eid
                            break
                    
                    estop_info = self.estop_definitions.get(estop_id, None)
                    location = estop_info.location if estop_info else "Unknown"
                    
                    writer.writerow({
                        'timestamp': change.timestamp.isoformat(),
                        'date': change.timestamp.strftime('%Y-%m-%d'),
                        'time': change.timestamp.strftime('%H:%M:%S.%f')[:-3],  # Include milliseconds
                        'estop_name': change.estop_name,
                        'location': location,
                        'old_state': change.old_state.value.upper(),
                        'new_state': change.new_state.value.upper(),
                        'channel': change.channel or '',
                        'duration_seconds': f"{change.duration_seconds:.3f}" if change.duration_seconds else ''
                    })
            
            self.logger.info(f"Exported {len(self.state_changes)} state changes to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting changes to CSV: {e}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive summary of the monitoring session"""
        summary = {
            "session_info": {
                "start_time": None,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": None,
                "monitoring_interval": self.monitor_interval,
                "total_reads": len(self.state_changes) + len(self.current_states),
                "monitoring_active": self.monitoring_active
            },
            "estop_summary": {},
            "change_statistics": {
                "total_changes": len(self.state_changes),
                "changes_by_estop": {},
                "changes_by_state": {"active": 0, "inactive": 0},
                "changes_by_channel": {"A": 0, "B": 0, "single": 0}
            },
            "current_states": {}
        }
        
        # Calculate session duration if we have changes
        if self.state_changes:
            first_change = min(self.state_changes, key=lambda x: x.timestamp)
            last_change = max(self.state_changes, key=lambda x: x.timestamp)
            summary["session_info"]["start_time"] = first_change.timestamp.isoformat()
            duration = last_change.timestamp - first_change.timestamp
            summary["session_info"]["duration_seconds"] = duration.total_seconds()
        
        # E Stop summary
        for estop_id, status in self.current_states.items():
            estop_info = self.estop_definitions[estop_id]
            summary["estop_summary"][estop_id] = {
                "name": status.name,
                "location": estop_info.location,
                "current_state": status.state.value,
                "total_changes": status.total_changes,
                "last_change_time": status.last_change.timestamp.isoformat() if status.last_change else None,
                "is_dual_channel": estop_info.is_dual_channel
            }
            
            if estop_info.is_dual_channel:
                summary["estop_summary"][estop_id]["channel_a_state"] = status.channel_a_state.value if status.channel_a_state else "unknown"
                summary["estop_summary"][estop_id]["channel_b_state"] = status.channel_b_state.value if status.channel_b_state else "unknown"
        
        # Change statistics
        for change in self.state_changes:
            # Count by E Stop
            if change.estop_name not in summary["change_statistics"]["changes_by_estop"]:
                summary["change_statistics"]["changes_by_estop"][change.estop_name] = 0
            summary["change_statistics"]["changes_by_estop"][change.estop_name] += 1
            
            # Count by state
            if change.new_state.value == "active":
                summary["change_statistics"]["changes_by_state"]["active"] += 1
            elif change.new_state.value == "inactive":
                summary["change_statistics"]["changes_by_state"]["inactive"] += 1
            
            # Count by channel
            if change.channel:
                if change.channel in summary["change_statistics"]["changes_by_channel"]:
                    summary["change_statistics"]["changes_by_channel"][change.channel] += 1
            else:
                summary["change_statistics"]["changes_by_channel"]["single"] += 1
        
        # Current states
        for estop_id, status in self.current_states.items():
            summary["current_states"][estop_id] = {
                "state": status.state.value,
                "read_error": status.read_error,
                "last_read_time": status.last_read_time.isoformat() if status.last_read_time else None
            }
        
        return summary
    
    def generate_monitoring_session_report(self) -> str:
        """Generate a comprehensive monitoring session report"""
        # Attempt to read current states first to get latest connection status
        self.read_current_states()
        
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("E STOP MONITORING SESSION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Monitoring Active: {'Yes' if self.monitoring_active else 'No'}")
        report_lines.append(f"Monitor Interval: {self.monitor_interval}s")
        report_lines.append(f"Total State Changes Recorded: {len(self.state_changes)}")
        report_lines.append("")
        
        # Session information
        if self.state_changes:
            first_change = min(self.state_changes, key=lambda x: x.timestamp)
            last_change = max(self.state_changes, key=lambda x: x.timestamp)
            session_duration = last_change.timestamp - first_change.timestamp
            
            report_lines.append("MONITORING SESSION INFORMATION:")
            report_lines.append("-" * 40)
            report_lines.append(f"Session Start: {first_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Session End: {last_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append(f"Session Duration: {session_duration.total_seconds():.1f} seconds ({session_duration.total_seconds()/60:.1f} minutes)")
            report_lines.append(f"Total Read Attempts: {len(self.state_changes) + len(self.current_states)}")
            report_lines.append("")
        
        # Connection status
        has_read_errors = any(status.read_error for status in self.current_states.values())
        if has_read_errors:
            report_lines.append("⚠️  PLC CONNECTION STATUS:")
            report_lines.append("-" * 40)
            report_lines.append("❌ PLC Connection Issues Detected")
            report_lines.append("   E Stop states showing as 'UNKNOWN' due to connection problems.")
            report_lines.append("   This is expected when:")
            report_lines.append("   - pylogix library is not installed")
            report_lines.append("   - PLC is not accessible on the network")
            report_lines.append("   - PLC IP address is incorrect")
            report_lines.append("")
        
        # Current states
        report_lines.append("CURRENT E STOP STATES:")
        report_lines.append("-" * 40)
        for estop_id, status in self.current_states.items():
            estop_info = self.estop_definitions[estop_id]
            report_lines.append(f"{status.name} ({estop_info.location}):")
            
            # Show state with appropriate indicator
            if status.read_error:
                report_lines.append(f"  Current State: {status.state.value.upper()} (⚠️  Connection Error)")
            else:
                report_lines.append(f"  Current State: {status.state.value.upper()}")
            
            if estop_info.is_dual_channel:
                channel_a_state = status.channel_a_state.value.upper() if status.channel_a_state else 'UNKNOWN'
                channel_b_state = status.channel_b_state.value.upper() if status.channel_b_state else 'UNKNOWN'
                report_lines.append(f"  Channel A: {channel_a_state}")
                report_lines.append(f"  Channel B: {channel_b_state}")
            
            report_lines.append(f"  Total Changes: {status.total_changes}")
            
            if status.last_read_time:
                report_lines.append(f"  Last Read: {status.last_read_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if status.last_change:
                report_lines.append(f"  Last Change: {status.last_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                report_lines.append(f"    {status.last_change.old_state.value} -> {status.last_change.new_state.value}")
                if status.last_change.channel:
                    report_lines.append(f"    Channel: {status.last_change.channel}")
            
            if status.read_error:
                report_lines.append(f"  Read Error: {status.read_error}")
            
            report_lines.append("")
        
        # State change statistics
        if self.state_changes:
            report_lines.append("STATE CHANGE STATISTICS:")
            report_lines.append("-" * 40)
            
            # Changes by E Stop
            changes_by_estop = {}
            for change in self.state_changes:
                if change.estop_name not in changes_by_estop:
                    changes_by_estop[change.estop_name] = 0
                changes_by_estop[change.estop_name] += 1
            
            report_lines.append("Changes by E Stop:")
            for estop_name, count in changes_by_estop.items():
                report_lines.append(f"  {estop_name}: {count} changes")
            report_lines.append("")
            
            # Changes by state
            active_changes = sum(1 for change in self.state_changes if change.new_state.value == "active")
            inactive_changes = sum(1 for change in self.state_changes if change.new_state.value == "inactive")
            
            report_lines.append("Changes by State:")
            report_lines.append(f"  ACTIVE: {active_changes}")
            report_lines.append(f"  INACTIVE: {inactive_changes}")
            report_lines.append("")
            
            # Changes by channel
            channel_changes = {"A": 0, "B": 0, "Single": 0}
            for change in self.state_changes:
                if change.channel:
                    if change.channel in channel_changes:
                        channel_changes[change.channel] += 1
                else:
                    channel_changes["Single"] += 1
            
            report_lines.append("Changes by Channel:")
            for channel, count in channel_changes.items():
                if count > 0:
                    report_lines.append(f"  Channel {channel}: {count} changes")
            report_lines.append("")
        
        # Recent changes
        recent_changes = self.get_recent_changes(20)
        if recent_changes:
            report_lines.append("RECENT STATE CHANGES:")
            report_lines.append("-" * 40)
            for change in recent_changes:
                timestamp = change.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                channel_info = f" [Channel {change.channel}]" if change.channel else ""
                duration_info = f" (Duration: {change.duration_seconds:.1f}s)" if change.duration_seconds else ""
                
                report_lines.append(f"{timestamp}: {change.estop_name}")
                report_lines.append(f"  {change.old_state.value.upper()} -> {change.new_state.value.upper()}{channel_info}{duration_info}")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("End of E Stop Monitoring Session Report")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def export_monitoring_session_to_csv(self, filename: str):
        """Export comprehensive monitoring session data to CSV"""
        try:
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Write session summary
                fieldnames = [
                    'report_type', 'timestamp', 'value', 'description'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Session information
                current_time = datetime.now()
                writer.writerow({
                    'report_type': 'SESSION_INFO',
                    'timestamp': current_time.isoformat(),
                    'value': 'Report Generated',
                    'description': f'Monitoring Session Report - {current_time.strftime("%Y-%m-%d %H:%M:%S")}'
                })
                
                writer.writerow({
                    'report_type': 'SESSION_INFO',
                    'timestamp': current_time.isoformat(),
                    'value': str(self.monitoring_active),
                    'description': 'Monitoring Active'
                })
                
                writer.writerow({
                    'report_type': 'SESSION_INFO',
                    'timestamp': current_time.isoformat(),
                    'value': f'{self.monitor_interval}s',
                    'description': 'Monitor Interval'
                })
                
                writer.writerow({
                    'report_type': 'SESSION_INFO',
                    'timestamp': current_time.isoformat(),
                    'value': str(len(self.state_changes)),
                    'description': 'Total State Changes Recorded'
                })
                
                # Session duration
                if self.state_changes:
                    first_change = min(self.state_changes, key=lambda x: x.timestamp)
                    last_change = max(self.state_changes, key=lambda x: x.timestamp)
                    session_duration = last_change.timestamp - first_change.timestamp
                    
                    writer.writerow({
                        'report_type': 'SESSION_INFO',
                        'timestamp': first_change.timestamp.isoformat(),
                        'value': 'Session Start',
                        'description': first_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    writer.writerow({
                        'report_type': 'SESSION_INFO',
                        'timestamp': last_change.timestamp.isoformat(),
                        'value': 'Session End',
                        'description': last_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    writer.writerow({
                        'report_type': 'SESSION_INFO',
                        'timestamp': current_time.isoformat(),
                        'value': f'{session_duration.total_seconds():.1f}',
                        'description': f'Session Duration (seconds)'
                    })
                
                # Current E Stop states
                for estop_id, status in self.current_states.items():
                    estop_info = self.estop_definitions[estop_id]
                    
                    writer.writerow({
                        'report_type': 'CURRENT_STATE',
                        'timestamp': status.last_read_time.isoformat() if status.last_read_time else current_time.isoformat(),
                        'value': status.state.value.upper(),
                        'description': f'{status.name} ({estop_info.location}) - Current State'
                    })
                    
                    if estop_info.is_dual_channel:
                        channel_a_state = status.channel_a_state.value.upper() if status.channel_a_state else 'UNKNOWN'
                        channel_b_state = status.channel_b_state.value.upper() if status.channel_b_state else 'UNKNOWN'
                        
                        writer.writerow({
                            'report_type': 'CURRENT_STATE',
                            'timestamp': status.last_read_time.isoformat() if status.last_read_time else current_time.isoformat(),
                            'value': channel_a_state,
                            'description': f'{status.name} - Channel A State'
                        })
                        
                        writer.writerow({
                            'report_type': 'CURRENT_STATE',
                            'timestamp': status.last_read_time.isoformat() if status.last_read_time else current_time.isoformat(),
                            'value': channel_b_state,
                            'description': f'{status.name} - Channel B State'
                        })
                    
                    writer.writerow({
                        'report_type': 'CURRENT_STATE',
                        'timestamp': current_time.isoformat(),
                        'value': str(status.total_changes),
                        'description': f'{status.name} - Total Changes'
                    })
                    
                    if status.read_error:
                        writer.writerow({
                            'report_type': 'CURRENT_STATE',
                            'timestamp': status.last_read_time.isoformat() if status.last_read_time else current_time.isoformat(),
                            'value': 'ERROR',
                            'description': f'{status.name} - Read Error: {status.read_error}'
                        })
                
                # State changes
                for change in self.state_changes:
                    channel_info = f" [Channel {change.channel}]" if change.channel else ""
                    duration_info = f" (Duration: {change.duration_seconds:.1f}s)" if change.duration_seconds else ""
                    
                    writer.writerow({
                        'report_type': 'STATE_CHANGE',
                        'timestamp': change.timestamp.isoformat(),
                        'value': f'{change.old_state.value.upper()} -> {change.new_state.value.upper()}',
                        'description': f'{change.estop_name}{channel_info}{duration_info}'
                    })
            
            self.logger.info(f"Exported monitoring session report to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error exporting monitoring session to CSV: {e}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive E Stop monitoring report"""
        # Attempt to read current states first to get latest connection status
        self.read_current_states()
        
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("E STOP STATE MONITORING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Monitoring Active: {'Yes' if self.monitoring_active else 'No'}")
        report_lines.append(f"Monitor Interval: {self.monitor_interval}s")
        report_lines.append(f"Total State Changes Recorded: {len(self.state_changes)}")
        report_lines.append("")
        
        # Connection status
        has_read_errors = any(status.read_error for status in self.current_states.values())
        if has_read_errors:
            report_lines.append("⚠️  PLC CONNECTION STATUS:")
            report_lines.append("-" * 40)
            report_lines.append("❌ PLC Connection Issues Detected")
            report_lines.append("   E Stop states showing as 'UNKNOWN' due to connection problems.")
            report_lines.append("   This is expected when:")
            report_lines.append("   - pylogix library is not installed")
            report_lines.append("   - PLC is not accessible on the network")
            report_lines.append("   - PLC IP address is incorrect")
            report_lines.append("")
        
        # Current states
        report_lines.append("CURRENT E STOP STATES:")
        report_lines.append("-" * 40)
        for estop_id, status in self.current_states.items():
            estop_info = self.estop_definitions[estop_id]
            report_lines.append(f"{status.name} ({estop_info.location}):")
            
            # Show state with appropriate indicator
            if status.read_error:
                report_lines.append(f"  Current State: {status.state.value.upper()} (⚠️  Connection Error)")
            else:
                report_lines.append(f"  Current State: {status.state.value.upper()}")
            
            if estop_info.is_dual_channel:
                channel_a_state = status.channel_a_state.value.upper() if status.channel_a_state else 'UNKNOWN'
                channel_b_state = status.channel_b_state.value.upper() if status.channel_b_state else 'UNKNOWN'
                report_lines.append(f"  Channel A: {channel_a_state}")
                report_lines.append(f"  Channel B: {channel_b_state}")
            
            report_lines.append(f"  Total Changes: {status.total_changes}")
            
            if status.last_read_time:
                report_lines.append(f"  Last Read: {status.last_read_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if status.last_change:
                report_lines.append(f"  Last Change: {status.last_change.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                report_lines.append(f"    {status.last_change.old_state.value} -> {status.last_change.new_state.value}")
                if status.last_change.channel:
                    report_lines.append(f"    Channel: {status.last_change.channel}")
            
            if status.read_error:
                report_lines.append(f"  Read Error: {status.read_error}")
            
            report_lines.append("")
        
        # Recent changes
        recent_changes = self.get_recent_changes(20)
        if recent_changes:
            report_lines.append("RECENT STATE CHANGES:")
            report_lines.append("-" * 40)
            for change in recent_changes:
                report_lines.append(f"{change.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                                  f"{change.estop_name}: {change.old_state.value} -> {change.new_state.value}")
                if change.channel:
                    report_lines.append(f"  Channel: {change.channel}")
                if change.duration_seconds:
                    report_lines.append(f"  Previous State Duration: {change.duration_seconds:.1f}s")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("End of E Stop Monitoring Report\n")
        
        return "\n".join(report_lines)