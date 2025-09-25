"""
Enhanced PLC Communication Module
"""
import time
import threading
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback for when modules aren't available
    class MockConfig:
        class PLCConfig:
            default_ip = "11.200.0.10"
            connection_timeout = 5.0
            read_timeout = 10.0
            max_retries = 3
            retry_delay = 1.0
        plc = PLCConfig()
    
    config = MockConfig()
    
    def get_logger(name, gui_widget=None):
        import logging
        return logging.getLogger(name)
    
    class ProgressLogger:
        def __init__(self, logger, total_steps, description=""):
            import time
            self.logger = logger
            self.total_steps = total_steps
            self.current_step = 0
            self.description = description
            self.start_time = time.time()
            if description:
                self.logger.info(f"Starting: {description}")
        
        def step(self, message=""):
            import time
            self.current_step += 1
            percentage = (self.current_step / self.total_steps) * 100
            if message:
                self.logger.info(f"[{percentage:.1f}%] {message}")
            else:
                self.logger.info(f"Progress: {self.current_step}/{self.total_steps} ({percentage:.1f}%)")
        
        def complete(self, message=""):
            import time
            elapsed = time.time() - self.start_time
            if message:
                self.logger.info(f"Completed: {message} (took {elapsed:.2f}s)")
            else:
                self.logger.info(f"Progress complete (took {elapsed:.2f}s)")
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
except ImportError:
    PYLOGIX_AVAILABLE = False
    PLC = None

@dataclass
class TagValue:
    """Container for PLC tag values with metadata"""
    tag: str
    value: Any
    status: str
    timestamp: float
    data_type: Optional[str] = None

@dataclass
class SafetyStatus:
    """Container for safety system status"""
    estop_relay_feedback: bool
    back_left_estop_a: bool
    back_left_estop_b: bool
    back_right_estop_a: bool
    back_right_estop_b: bool
    front_estop_a: bool
    front_estop_b: bool
    main_enclosure_estop_a: bool
    main_enclosure_estop_b: bool

class PLCConnectionManager:
    """Enhanced PLC connection management with connection pooling and retry logic"""
    
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.logger = get_logger("PLCConnection")
        self._connection = None
        self._lock = threading.Lock()
        self._last_used = 0
        self._connection_timeout = 300  # 5 minutes
    
    @contextmanager
    def get_connection(self):
        """Context manager for PLC connections with automatic cleanup"""
        with self._lock:
            if self._connection is None or time.time() - self._last_used > self._connection_timeout:
                self._create_connection()
            
            self._last_used = time.time()
            yield self._connection
    
    def _create_connection(self):
        """Create a new PLC connection with retry logic and better diagnostics"""
        if not PYLOGIX_AVAILABLE:
            raise RuntimeError("pylogix is not installed. Please run: pip install pylogix")
        
        # First, test basic network connectivity
        self.logger.info(f"Testing network connectivity to {self.ip_address}...")
        if not self._test_network_connectivity():
            raise ConnectionError(f"Network connectivity test failed for {self.ip_address}")
        
        for attempt in range(config.plc.max_retries):
            try:
                self.logger.info(f"Creating PLC connection to {self.ip_address} (attempt {attempt + 1}/{config.plc.max_retries})")
                self._connection = PLC()
                self._connection.IPAddress = self.ip_address
                self._connection.SocketTimeout = config.plc.read_timeout
                
                # Test connection with a simple read
                self.logger.debug("Testing PLC communication with g_Par tag...")
                test_result = self._connection.Read("Program:MainProgram.g_Par")
                if test_result.Status == "Success":
                    self.logger.info(f"Successfully connected to PLC at {self.ip_address}")
                    return
                else:
                    self.logger.warning(f"PLC communication test failed: {test_result.Status}")
                    if hasattr(test_result, 'StatusExtended'):
                        self.logger.warning(f"Extended status: {test_result.StatusExtended}")
                    
            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < config.plc.max_retries - 1:
                    self.logger.info(f"Retrying in {config.plc.retry_delay} seconds...")
                    time.sleep(config.plc.retry_delay)
        
        raise ConnectionError(f"Failed to connect to PLC at {self.ip_address} after {config.plc.max_retries} attempts. Check:\n"
                            f"1. PLC is powered on and running\n"
                            f"2. Network connectivity to {self.ip_address}\n"
                            f"3. PLC IP address is correct\n"
                            f"4. No firewall blocking EtherNet/IP communication")
    
    def _test_network_connectivity(self) -> bool:
        """Test basic network connectivity to the PLC"""
        import socket
        import subprocess
        import platform
        
        try:
            # Test 1: Socket connection test
            self.logger.debug("Testing socket connectivity...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.ip_address, 44818))  # EtherNet/IP port
            sock.close()
            
            if result == 0:
                self.logger.info("✓ Socket connectivity test passed")
                return True
            else:
                self.logger.warning(f"✗ Socket connectivity test failed (error code: {result})")
            
            # Test 2: Ping test
            self.logger.debug("Testing ping connectivity...")
            is_windows = platform.system().lower() == "windows"
            if is_windows:
                cmd = ["ping", "-n", "1", "-w", "3000", self.ip_address]
            else:
                cmd = ["ping", "-c", "1", "-W", "3", self.ip_address]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.logger.info("✓ Ping connectivity test passed")
                return True
            else:
                self.logger.warning("✗ Ping connectivity test failed")
                self.logger.warning(f"Ping output: {result.stdout}")
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Network connectivity test failed: {e}")
            return False
    
    def close(self):
        """Close the PLC connection"""
        with self._lock:
            if self._connection:
                try:
                    self._connection.Close()
                except Exception as e:
                    self.logger.warning(f"Error closing PLC connection: {e}")
                finally:
                    self._connection = None

class EnhancedPLCValidator:
    """Enhanced PLC validation with better error handling and caching"""
    
    def __init__(self, ip_address: str, logger=None):
        self.ip_address = ip_address
        self.logger = logger or get_logger("PLCValidator")
        self.connection_manager = PLCConnectionManager(ip_address)
        self._tag_cache: Dict[str, TagValue] = {}
        self._cache_timeout = 5.0  # 5 seconds
    
    def _is_cache_valid(self, tag: str) -> bool:
        """Check if cached tag value is still valid"""
        if tag not in self._tag_cache:
            return False
        return time.time() - self._tag_cache[tag].timestamp < self._cache_timeout
    
    def read_tag(self, tag: str, use_cache: bool = True) -> TagValue:
        """Read a single tag with caching and error handling"""
        if use_cache and self._is_cache_valid(tag):
            return self._tag_cache[tag]
        
        try:
            with self.connection_manager.get_connection() as plc:
                result = plc.Read(tag)
                
                tag_value = TagValue(
                    tag=tag,
                    value=result.Value,
                    status=result.Status,
                    timestamp=time.time(),
                    data_type=result.DataType
                )
                
                self._tag_cache[tag] = tag_value
                return tag_value
                
        except Exception as e:
            self.logger.error(f"Error reading tag {tag}: {e}")
            return TagValue(
                tag=tag,
                value=None,
                status="Error",
                timestamp=time.time(),
                data_type=None
            )
    
    def read_multiple_tags(self, tags: List[str]) -> Dict[str, TagValue]:
        """Read multiple tags efficiently"""
        results = {}
        
        try:
            with self.connection_manager.get_connection() as plc:
                plc_results = plc.Read(tags)
                
                for tag, result in zip(tags, plc_results):
                    results[tag] = TagValue(
                        tag=tag,
                        value=result.Value,
                        status=result.Status,
                        timestamp=time.time(),
                        data_type=result.DataType
                    )
                    
        except Exception as e:
            self.logger.error(f"Error reading multiple tags: {e}")
            for tag in tags:
                results[tag] = TagValue(
                    tag=tag,
                    value=None,
                    status="Error",
                    timestamp=time.time()
                )
        
        return results
    
    def get_parameter_bits(self, tag: str, descriptions: Dict[int, str]) -> List[Tuple[int, str]]:
        """Get active parameter bits with descriptions"""
        tag_value = self.read_tag(tag)
        
        if tag_value.status != "Success" or tag_value.value is None:
            self.logger.warning(f"Failed to read {tag}: {tag_value.status}")
            return []
        
        try:
            value = int(tag_value.value)
            active_bits = []
            
            for bit, description in descriptions.items():
                if value & (1 << bit):
                    active_bits.append((bit, description))
            
            return active_bits
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error parsing {tag} value: {e}")
            return []
    
    def get_safety_status(self) -> SafetyStatus:
        """Get comprehensive safety system status"""
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
        
        results = self.read_multiple_tags(safety_tags)
        
        return SafetyStatus(
            estop_relay_feedback=bool(results.get(safety_tags[0], TagValue("", False, "Error", 0)).value),
            back_left_estop_a=bool(results.get(safety_tags[1], TagValue("", False, "Error", 0)).value),
            back_left_estop_b=bool(results.get(safety_tags[2], TagValue("", False, "Error", 0)).value),
            back_right_estop_a=bool(results.get(safety_tags[3], TagValue("", False, "Error", 0)).value),
            back_right_estop_b=bool(results.get(safety_tags[4], TagValue("", False, "Error", 0)).value),
            front_estop_a=bool(results.get(safety_tags[5], TagValue("", False, "Error", 0)).value),
            front_estop_b=bool(results.get(safety_tags[6], TagValue("", False, "Error", 0)).value),
            main_enclosure_estop_a=bool(results.get(safety_tags[7], TagValue("", False, "Error", 0)).value),
            main_enclosure_estop_b=bool(results.get(safety_tags[8], TagValue("", False, "Error", 0)).value),
        )
    
    def get_connectivity_status(self) -> Dict[str, bool]:
        """Get WMS and network connectivity status"""
        connectivity_tags = [
            'H1_PACK_WMS_Connected',
            'H2_SLAM1_WMS_Connected',
            'NTP_Connected'
        ]
        
        results = self.read_multiple_tags(connectivity_tags)
        return {tag: bool(result.value) for tag, result in results.items()}
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive PLC status report"""
        self.logger.info("Generating comprehensive PLC status report")
        
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("COMPREHENSIVE PLC STATUS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"PLC IP Address: {self.ip_address}")
        report_lines.append(f"Report Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Parameter bits
        parameter_tags = {
            'g_Par': {
                0: 'Pneumatic Roll Lift', 1: 'Webber Installed', 2: 'Disable Downstream Conveyor Interlock',
                3: 'Printer Forward Sensor Disabled', 4: 'Not Used', 5: 'Disable OEE Starved Time Reporting',
                6: 'Enable 3-Position Nip Valve', 7: 'Enable Auto Splice', 8: 'Use Extended Discharge Timer',
                9: 'Bypass Guarding Fault', 10: 'Enable Machine Test Mode', 11: 'Enable Manual Bypass',
                12: 'Disable Alarm Horn', 13: 'Enable Remote Start', 14: 'Enable Diagnostic Logging',
                15: 'Enable Power Save Mode', 16: 'Enable Light Curtain Override', 17: 'Bypass Safety Interlock',
                18: 'Allow Index During Alarm', 19: 'Enable Maintenance Mode', 20: 'Ignore Load Cell Faults',
                21: 'Enable High-Speed Mode', 22: 'Use Alternative Recipe Logic', 23: 'Bypass Printer Faults',
                24: 'Enable Label Verification', 25: 'Ignore Film Tracking Sensor', 26: 'Use Legacy Motion Control',
                27: 'Enable Secondary Safety Check', 28: 'Disable Zero Speed Check', 29: 'Enable Slow Start Feature',
                30: 'Use Backup PLC Settings', 31: 'Force E-Stop Override',
            }
        }
        
        for tag, descriptions in parameter_tags.items():
            active_bits = self.get_parameter_bits(tag, descriptions)
            report_lines.append(f"{tag.upper()} ACTIVE BITS:")
            if active_bits:
                for bit, description in active_bits:
                    report_lines.append(f"  Bit {bit}: {description}")
            else:
                report_lines.append("  None")
            report_lines.append("")
        
        # Safety status
        report_lines.append("SAFETY & E-STOP STATUS:")
        safety_status = self.get_safety_status()
        report_lines.append(f"  E-Stop Relay Feedback: {'ON' if safety_status.estop_relay_feedback else 'OFF'}")
        report_lines.append(f"  Back Left E-Stop A: {'ON' if safety_status.back_left_estop_a else 'OFF'}")
        report_lines.append(f"  Back Left E-Stop B: {'ON' if safety_status.back_left_estop_b else 'OFF'}")
        report_lines.append(f"  Back Right E-Stop A: {'ON' if safety_status.back_right_estop_a else 'OFF'}")
        report_lines.append(f"  Back Right E-Stop B: {'ON' if safety_status.back_right_estop_b else 'OFF'}")
        report_lines.append(f"  Front E-Stop A: {'ON' if safety_status.front_estop_a else 'OFF'}")
        report_lines.append(f"  Front E-Stop B: {'ON' if safety_status.front_estop_b else 'OFF'}")
        report_lines.append(f"  Main Enclosure E-Stop A: {'ON' if safety_status.main_enclosure_estop_a else 'OFF'}")
        report_lines.append(f"  Main Enclosure E-Stop B: {'ON' if safety_status.main_enclosure_estop_b else 'OFF'}")
        report_lines.append("")
        
        # Interlock status
        interlock_result = self.read_tag('IO.PLC.In.DownstreamConveyorEnabled')
        report_lines.append("INTERLOCK STATUS:")
        report_lines.append(f"  Downstream Conveyor: {'ENABLED' if interlock_result.value else 'DISABLED'}")
        report_lines.append("")
        
        # Connectivity status
        report_lines.append("WMS & NETWORK CONNECTIVITY:")
        connectivity = self.get_connectivity_status()
        for tag, connected in connectivity.items():
            report_lines.append(f"  {tag}: {'CONNECTED' if connected else 'DISCONNECTED'}")
        
        report_lines.append("=" * 80)
        report_lines.append("End of Report\n")
        
        return "\n".join(report_lines)
    
    def close(self):
        """Close the PLC connection"""
        self.connection_manager.close()