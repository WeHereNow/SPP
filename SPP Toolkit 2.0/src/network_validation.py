"""
Enhanced Network Validation Module
"""
import re
import time
import platform
import subprocess
import ipaddress
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback for when modules aren't available
    class MockConfig:
        class NetworkConfig:
            default_probes = 3
            default_retries = 2
            default_timeout_ms = 700
            require_min_replies = 1
            arp_warmup_delay = 0.08
            backoff_delay = 0.3
        network = NetworkConfig()
    
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

@dataclass
class DeviceResult:
    """Result of device validation"""
    ip: str
    name: str
    status: str
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    attempts: int = 0

class NetworkValidator:
    """Enhanced network validation with concurrent testing and better error handling"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("NetworkValidator")
        self.results: List[DeviceResult] = []
        self._lock = threading.Lock()
    
    def _run_ping_blocking(self, ip: str, probes: int, timeout_ms: int) -> Tuple[int, float]:
        """
        Run a single OS 'ping' command and return (reply_count, avg_response_time)
        """
        is_windows = platform.system().lower() == "windows"
        
        if is_windows:
            cmd = ["ping", "-n", str(probes), "-w", str(timeout_ms), ip]
        else:
            timeout_s = max(1, int(round(timeout_ms / 1000.0)))
            cmd = ["ping", "-c", str(probes), "-W", str(timeout_s), ip]
        
        popen_kwargs = {}
        if is_windows:
            CREATE_NO_WINDOW = 0x08000000
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            popen_kwargs = {"creationflags": CREATE_NO_WINDOW, "startupinfo": si}
        
        start_time = time.time()
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            **popen_kwargs,
        )
        response_time = time.time() - start_time
        
        out = res.stdout or ""
        hits = 0
        response_times = []
        
        if is_windows:
            for line in out.splitlines():
                # Count replies
                m = re.search(r"Reply from ([0-9.]+):", line, flags=re.IGNORECASE)
                if m and m.group(1) == ip and "Destination host unreachable" not in line:
                    hits += 1
                
                # Extract response time
                time_match = re.search(r"time[<=](\d+)ms", line, flags=re.IGNORECASE)
                if time_match:
                    response_times.append(float(time_match.group(1)))
        else:
            for line in out.splitlines():
                # Count replies
                m = re.search(r"bytes from\s+([0-9.]+)", line, flags=re.IGNORECASE)
                if m and m.group(1) == ip:
                    hits += 1
                
                # Extract response time
                time_match = re.search(r"time=(\d+\.?\d*)", line)
                if time_match:
                    response_times.append(float(time_match.group(1)))
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        return hits, avg_response_time
    
    def ping_device(self, ip: str, name: str, retries: int = None, 
                   probes: int = None, require: int = None, timeout_ms: int = None) -> DeviceResult:
        """
        Enhanced ping with better error handling and response time tracking
        """
        retries = retries or config.network.default_retries
        probes = probes or config.network.default_probes
        require = require or config.network.require_min_replies
        timeout_ms = timeout_ms or config.network.default_timeout_ms
        
        result = DeviceResult(ip=ip, name=name, status="Unknown", attempts=0)
        
        # ARP warm-up
        try:
            _ = self._run_ping_blocking(ip, probes=1, timeout_ms=timeout_ms)
        except Exception:
            pass
        time.sleep(config.network.arp_warmup_delay)
        
        for attempt in range(1, retries + 1):
            result.attempts = attempt
            self.logger.debug(f"Attempt {attempt}: Pinging {name} ({ip}) - {probes} probes")
            
            try:
                hits, avg_response_time = self._run_ping_blocking(ip, probes, timeout_ms)
                result.response_time = avg_response_time
                
                self.logger.debug(f"  Replies from target: {hits}/{probes}")
                if avg_response_time:
                    self.logger.debug(f"  Average response time: {avg_response_time:.2f}ms")
                
                if hits >= require:
                    result.status = "Reachable"
                    self.logger.info(f"  ✓ {name} ({ip}) - SUCCESS")
                    return result
                else:
                    result.status = "Unreachable"
                    result.error_message = f"Only {hits}/{probes} replies received"
                    
            except Exception as e:
                result.status = "Error"
                result.error_message = str(e)
                self.logger.warning(f"  ✗ {name} ({ip}) - Error: {e}")
            
            if attempt < retries:
                time.sleep(config.network.backoff_delay)
        
        self.logger.warning(f"  ✗ {name} ({ip}) - FAILED after {retries} attempts")
        return result
    
    def validate_devices_concurrent(self, devices: Dict[str, str], max_workers: int = 5) -> List[DeviceResult]:
        """
        Validate multiple devices concurrently for better performance
        """
        self.logger.info(f"Starting concurrent validation of {len(devices)} devices")
        self.results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all ping tasks
            future_to_device = {
                executor.submit(self.ping_device, ip, name): (ip, name)
                for ip, name in devices.items()
            }
            
            # Collect results as they complete
            progress = ProgressLogger(self.logger, len(devices), "Network Validation")
            completed = 0
            for future in as_completed(future_to_device):
                ip, name = future_to_device[future]
                try:
                    result = future.result()
                    with self._lock:
                        self.results.append(result)
                    completed += 1
                    progress.step(f"Completed {name}")
                except Exception as e:
                    self.logger.error(f"Exception validating {name} ({ip}): {e}")
                    with self._lock:
                        self.results.append(DeviceResult(
                            ip=ip, name=name, status="Exception", error_message=str(e)
                        ))
                    completed += 1
                    progress.step(f"Failed {name}")
            
            progress.complete("Network validation")
        
        # Sort results by IP address for consistent output
        self.results.sort(key=lambda x: ipaddress.ip_address(x.ip))
        return self.results
    
    def generate_report(self, results: List[DeviceResult]) -> str:
        """Generate a formatted report of validation results"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("SPP IP VALIDATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary statistics
        total = len(results)
        reachable = len([r for r in results if r.status == "Reachable"])
        unreachable = len([r for r in results if r.status == "Unreachable"])
        errors = len([r for r in results if r.status == "Error"])
        
        report_lines.append(f"\nSUMMARY:")
        report_lines.append(f"  Total Devices: {total}")
        report_lines.append(f"  Reachable: {reachable}")
        report_lines.append(f"  Unreachable: {unreachable}")
        report_lines.append(f"  Errors: {errors}")
        report_lines.append(f"  Success Rate: {(reachable/total*100):.1f}%")
        
        # Detailed results table
        report_lines.append(f"\nDETAILED RESULTS:")
        report_lines.append("-" * 100)
        report_lines.append(f"{'IP Address':<16} {'Device Description':<45} {'Status':<12} {'Response Time':<12} {'Attempts'}")
        report_lines.append("-" * 100)
        
        for result in results:
            response_time_str = f"{result.response_time:.1f}ms" if result.response_time else "N/A"
            report_lines.append(
                f"{result.ip:<16} {result.name:<45} {result.status:<12} {response_time_str:<12} {result.attempts}"
            )
        
        # Error details
        error_results = [r for r in results if r.error_message]
        if error_results:
            report_lines.append(f"\nERROR DETAILS:")
            for result in error_results:
                report_lines.append(f"  {result.name} ({result.ip}): {result.error_message}")
        
        report_lines.append("=" * 80)
        report_lines.append("Validation complete.\n")
        
        return "\n".join(report_lines)
    
    def export_results_csv(self, results: List[DeviceResult], filename: str = None) -> str:
        """Export validation results to CSV file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_validation_{timestamp}.csv"
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IP Address', 'Device Name', 'Status', 'Response Time (ms)', 'Attempts', 'Error Message'])
            
            for result in results:
                writer.writerow([
                    result.ip,
                    result.name,
                    result.status,
                    result.response_time or '',
                    result.attempts,
                    result.error_message or ''
                ])
        
        self.logger.info(f"Results exported to: {filename}")
        return filename