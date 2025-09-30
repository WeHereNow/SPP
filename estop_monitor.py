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
        """Read current E Stop states from PLC"""
        try:
            # Collect all tags to read
            tags_to_read = []
            tag_mapping = {}  # Maps tag to (estop_id, channel)
            
            for estop_id, estop_info in self.estop_definitions.items():
                if estop_info.is_dual_channel:
                    # Add both channels
                    tags_to_read.append(estop_info.channel_a_tag)
                    tags_to_read.append(estop_info.channel_b_tag)
                    tag_mapping[estop_info.channel_a_tag] = (estop_id, "A")
                    tag_mapping[estop_info.channel_b_tag] = (estop_id, "B")
                else:
                    # Single channel
                    tags_to_read.append(estop_info.tag)
                    tag_mapping[estop_info.tag] = (estop_id, None)
            
            # Read all tags at once
            with self.plc_connection_manager.get_connection() as plc:
                results = plc.Read(tags_to_read)
                
                if isinstance(results, list):
                    # Process results
                    for tag, result in zip(tags_to_read, results):
                        estop_id, channel = tag_mapping[tag]
                        
                        if result.Status == "Success":
                            new_state = self._bool_to_estop_state(result.Value)
                            self._update_estop_state(estop_id, new_state, channel)
                        else:
                            self.logger.warning(f"Failed to read {tag}: {result.Status}")
                            self.current_states[estop_id].read_error = result.Status
                
                # Update last read time
                current_time = datetime.now()
                for estop_status in self.current_states.values():
                    estop_status.last_read_time = current_time
                
        except Exception as e:
            self.logger.error(f"Error reading E Stop states: {e}")
            # Mark all as having read errors
            for estop_status in self.current_states.values():
                estop_status.read_error = str(e)
        
        return self.current_states.copy()
    
    def _update_estop_state(self, estop_id: str, new_state: EStopState, channel: Optional[str] = None):
        """Update E Stop state and detect changes"""
        current_status = self.current_states[estop_id]
        old_state = current_status.state
        
        # Determine if this is a state change
        state_changed = False
        
        if current_status.estop_definitions[estop_id].is_dual_channel:
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
    
    def generate_report(self) -> str:
        """Generate a comprehensive E Stop monitoring report"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("E STOP STATE MONITORING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Monitoring Active: {'Yes' if self.monitoring_active else 'No'}")
        report_lines.append(f"Monitor Interval: {self.monitor_interval}s")
        report_lines.append(f"Total State Changes Recorded: {len(self.state_changes)}")
        report_lines.append("")
        
        # Current states
        report_lines.append("CURRENT E STOP STATES:")
        report_lines.append("-" * 40)
        for estop_id, status in self.current_states.items():
            estop_info = self.estop_definitions[estop_id]
            report_lines.append(f"{status.name} ({estop_info.location}):")
            report_lines.append(f"  Current State: {status.state.value.upper()}")
            
            if estop_info.is_dual_channel:
                report_lines.append(f"  Channel A: {status.channel_a_state.value.upper() if status.channel_a_state else 'UNKNOWN'}")
                report_lines.append(f"  Channel B: {status.channel_b_state.value.upper() if status.channel_b_state else 'UNKNOWN'}")
            
            report_lines.append(f"  Total Changes: {status.total_changes}")
            
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