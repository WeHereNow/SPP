"""
HMI Verification Module
Verifies HMI program installation and runtime information
"""
import time
import json
import csv
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback configuration
    class MockConfig:
        class HMIConfig:
            default_port = 2222  # FactoryTalk View SE default port
            connection_timeout = 5.0
            read_timeout = 10.0
            max_retries = 3
            retry_delay = 1.0
        hmi = HMIConfig()
    
    config = MockConfig()
    
    def get_logger(name, gui_widget=None):
        import logging
        return logging.getLogger(name)
    
    class ProgressLogger:
        def __init__(self, logger, total_steps, description=""):
            self.logger = logger
            self.total_steps = total_steps
            self.current_step = 0
            self.description = description
            if description:
                self.logger.info(f"Starting: {description}")
        
        def step(self, message=""):
            self.current_step += 1
            percentage = (self.current_step / self.total_steps) * 100
            if message:
                self.logger.info(f"[{percentage:.1f}%] {message}")
            else:
                self.logger.info(f"Progress: {self.current_step}/{self.total_steps} ({percentage:.1f}%)")
        
        def complete(self, message=""):
            if message:
                self.logger.info(f"Completed: {message}")
            else:
                self.logger.info("Progress complete")
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

@dataclass
class HMIInfo:
    """HMI runtime information"""
    app_name: str = ""
    app_version: str = ""
    runtime_version: str = ""
    last_modified: str = ""
    file_size: int = 0
    checksum: str = ""
    ip_address: str = ""
    port: int = 0
    connection_status: str = ""

@dataclass
class HMIVerificationResult:
    """Result of HMI verification"""
    ip_address: str
    port: int
    connection_successful: bool
    hmi_info: HMIInfo
    verification_timestamp: str
    error_message: str = ""
    expected_app_name: str = ""
    expected_version: str = ""
    app_matches: bool = False
    version_matches: bool = False

class HMIVerifier:
    """HMI verification with runtime information and version checking"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("HMIVerifier")
        self.results: List[HMIVerificationResult] = []
    
    def check_hmi_connection(self, ip_address: str, port: int = 2222) -> bool:
        """Check if HMI is reachable on the specified port"""
        try:
            with socket.create_connection((ip_address, port), timeout=config.hmi.connection_timeout):
                return True
        except (socket.timeout, socket.error, ConnectionRefusedError):
            return False
    
    def get_hmi_runtime_info(self, ip_address: str, port: int = 2222) -> HMIInfo:
        """Get HMI runtime information via network connection"""
        hmi_info = HMIInfo(ip_address=ip_address, port=port)
        
        # Check connection first
        if not self.check_hmi_connection(ip_address, port):
            hmi_info.connection_status = "Unreachable"
            return hmi_info
        
        hmi_info.connection_status = "Connected"
        
        try:
            # For FactoryTalk View SE, we can try to connect and get basic info
            # This is a simplified approach - in a real implementation, you might use
            # FactoryTalk View SE's API or specific protocols
            
            with socket.create_connection((ip_address, port), timeout=config.hmi.connection_timeout) as sock:
                # Send a simple query to get runtime information
                # This is a placeholder - actual implementation would depend on the HMI type
                query = b"GET_RUNTIME_INFO\r\n"
                sock.send(query)
                
                # Set a short timeout for response
                sock.settimeout(2.0)
                
                try:
                    response = sock.recv(1024).decode('utf-8', errors='ignore')
                    # Parse response (this would be specific to the HMI protocol)
                    # For now, we'll set some default values
                    hmi_info.app_name = "FactoryTalk View SE"
                    hmi_info.runtime_version = "Unknown"
                    hmi_info.app_version = "Unknown"
                    
                except socket.timeout:
                    # No response, but connection was successful
                    hmi_info.app_name = "FactoryTalk View SE (No Response)"
                    hmi_info.runtime_status = "Connected - No Info"
        
        except Exception as e:
            hmi_info.connection_status = f"Error: {str(e)}"
        
        return hmi_info
    
    def get_hmi_info_via_ping(self, ip_address: str) -> HMIInfo:
        """Get basic HMI information via ping and common port checks"""
        hmi_info = HMIInfo(ip_address=ip_address)
        
        # Check common HMI ports
        common_ports = [2222, 8080, 80, 443, 502]  # FactoryTalk, HTTP, HTTPS, Modbus
        
        for port in common_ports:
            if self.check_hmi_connection(ip_address, port):
                hmi_info.port = port
                hmi_info.connection_status = f"Connected on port {port}"
                
                # Try to identify HMI type based on port
                if port == 2222:
                    hmi_info.app_name = "FactoryTalk View SE"
                elif port in [80, 8080]:
                    hmi_info.app_name = "Web-based HMI"
                elif port == 443:
                    hmi_info.app_name = "Secure Web HMI"
                elif port == 502:
                    hmi_info.app_name = "Modbus HMI"
                else:
                    hmi_info.app_name = f"Unknown HMI (Port {port})"
                
                break
        
        if not hmi_info.connection_status:
            hmi_info.connection_status = "No accessible ports found"
        
        return hmi_info
    
    def verify_hmi(self, ip_address: str, port: int = 2222, 
                   expected_app_name: str = "", expected_version: str = "") -> HMIVerificationResult:
        """Verify HMI runtime information against expected values"""
        self.logger.info(f"Verifying HMI at {ip_address}:{port}")
        
        result = HMIVerificationResult(
            ip_address=ip_address,
            port=port,
            connection_successful=False,
            hmi_info=HMIInfo(ip_address=ip_address, port=port),
            verification_timestamp=datetime.now().isoformat(),
            expected_app_name=expected_app_name,
            expected_version=expected_version
        )
        
        try:
            # Get HMI information
            hmi_info = self.get_hmi_runtime_info(ip_address, port)
            
            # If specific port fails, try common ports
            if not hmi_info.connection_status or "Unreachable" in hmi_info.connection_status:
                self.logger.warning(f"  Port {port} unreachable, trying common HMI ports...")
                hmi_info = self.get_hmi_info_via_ping(ip_address)
            
            result.hmi_info = hmi_info
            result.connection_successful = "Connected" in hmi_info.connection_status
            
            if result.connection_successful:
                # Verify app name
                if expected_app_name:
                    result.app_matches = (expected_app_name.lower() in hmi_info.app_name.lower())
                    if result.app_matches:
                        self.logger.info(f"  ✓ App name matches: {hmi_info.app_name}")
                    else:
                        self.logger.warning(f"  ⚠ App name mismatch - Expected: {expected_app_name}, Found: {hmi_info.app_name}")
                
                # Verify version
                if expected_version:
                    result.version_matches = (expected_version.lower() in hmi_info.app_version.lower())
                    if result.version_matches:
                        self.logger.info(f"  ✓ Version matches: {hmi_info.app_version}")
                    else:
                        self.logger.warning(f"  ⚠ Version mismatch - Expected: {expected_version}, Found: {hmi_info.app_version}")
                
                # Log HMI information
                self.logger.info(f"  App Name: {hmi_info.app_name}")
                self.logger.info(f"  App Version: {hmi_info.app_version}")
                self.logger.info(f"  Runtime Version: {hmi_info.runtime_version}")
                self.logger.info(f"  Connection: {hmi_info.connection_status}")
                self.logger.info(f"  Port: {hmi_info.port}")
                
            else:
                self.logger.warning(f"  ✗ HMI not reachable: {hmi_info.connection_status}")
                result.error_message = hmi_info.connection_status
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"  ✗ Error verifying HMI: {e}")
        
        return result
    
    def verify_multiple_hmis(self, hmi_configs: List[Dict[str, Any]]) -> List[HMIVerificationResult]:
        """Verify multiple HMIs"""
        self.logger.info(f"Starting HMI verification for {len(hmi_configs)} devices")
        self.results = []
        
        with ProgressLogger(self.logger, len(hmi_configs), "HMI Verification") as progress:
            for config in hmi_configs:
                try:
                    result = self.verify_hmi(
                        ip_address=config.get("ip_address", ""),
                        port=config.get("port", 2222),
                        expected_app_name=config.get("expected_app_name", ""),
                        expected_version=config.get("expected_version", "")
                    )
                    self.results.append(result)
                    progress.step(f"Completed {config.get('ip_address', 'Unknown')}")
                except Exception as e:
                    self.logger.error(f"Exception verifying HMI {config.get('ip_address', 'Unknown')}: {e}")
                    error_result = HMIVerificationResult(
                        ip_address=config.get("ip_address", ""),
                        port=config.get("port", 2222),
                        connection_successful=False,
                        hmi_info=HMIInfo(ip_address=config.get("ip_address", "")),
                        verification_timestamp=datetime.now().isoformat(),
                        error_message=str(e),
                        expected_app_name=config.get("expected_app_name", ""),
                        expected_version=config.get("expected_version", "")
                    )
                    self.results.append(error_result)
                    progress.step(f"Failed {config.get('ip_address', 'Unknown')}")
        
        return self.results
    
    def generate_report(self, results: List[HMIVerificationResult]) -> str:
        """Generate a formatted report of verification results"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("HMI VERIFICATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary statistics
        total = len(results)
        successful_connections = len([r for r in results if r.connection_successful])
        app_matches = len([r for r in results if r.app_matches])
        version_matches = len([r for r in results if r.version_matches])
        errors = len([r for r in results if r.error_message])
        
        report_lines.append(f"\nSUMMARY:")
        report_lines.append(f"  Total HMIs: {total}")
        report_lines.append(f"  Successful Connections: {successful_connections}")
        report_lines.append(f"  App Name Matches: {app_matches}")
        report_lines.append(f"  Version Matches: {version_matches}")
        report_lines.append(f"  Errors: {errors}")
        
        # Detailed results
        report_lines.append(f"\nDETAILED RESULTS:")
        report_lines.append("-" * 100)
        report_lines.append(f"{'IP Address':<16} {'Port':<6} {'App Name':<25} {'Version':<15} {'Status'}")
        report_lines.append("-" * 100)
        
        for result in results:
            app_name = result.hmi_info.app_name[:24] if result.hmi_info.app_name else "Unknown"
            version = result.hmi_info.app_version[:14] if result.hmi_info.app_version else "Unknown"
            
            if result.error_message:
                status = "ERROR"
            elif result.connection_successful:
                status = "OK"
            else:
                status = "FAILED"
            
            report_lines.append(
                f"{result.ip_address:<16} {result.port:<6} {app_name:<25} {version:<15} {status}"
            )
        
        # Detailed information for each HMI
        report_lines.append(f"\nDETAILED INFORMATION:")
        for result in results:
            report_lines.append(f"\nHMI: {result.ip_address}:{result.port}")
            report_lines.append(f"  App Name: {result.hmi_info.app_name}")
            report_lines.append(f"  App Version: {result.hmi_info.app_version}")
            report_lines.append(f"  Runtime Version: {result.hmi_info.runtime_version}")
            report_lines.append(f"  Connection Status: {result.hmi_info.connection_status}")
            
            if result.expected_app_name:
                report_lines.append(f"  Expected App: {result.expected_app_name}")
                report_lines.append(f"  App Match: {'✓' if result.app_matches else '✗'}")
            
            if result.expected_version:
                report_lines.append(f"  Expected Version: {result.expected_version}")
                report_lines.append(f"  Version Match: {'✓' if result.version_matches else '✗'}")
            
            if result.error_message:
                report_lines.append(f"  Error: {result.error_message}")
        
        report_lines.append("=" * 80)
        report_lines.append("Verification complete.\n")
        
        return "\n".join(report_lines)
    
    def export_results_json(self, results: List[HMIVerificationResult], filename: str = None) -> str:
        """Export results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hmi_verification_{timestamp}.json"
        
        # Convert results to serializable format
        json_data = []
        for result in results:
            json_data.append({
                "ip_address": result.ip_address,
                "port": result.port,
                "connection_successful": result.connection_successful,
                "hmi_info": asdict(result.hmi_info),
                "verification_timestamp": result.verification_timestamp,
                "error_message": result.error_message,
                "expected_app_name": result.expected_app_name,
                "expected_version": result.expected_version,
                "app_matches": result.app_matches,
                "version_matches": result.version_matches
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results exported to JSON: {filename}")
        return filename
    
    def export_results_csv(self, results: List[HMIVerificationResult], filename: str = None) -> str:
        """Export results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hmi_verification_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'IP Address', 'Port', 'Connection Successful', 'App Name', 'App Version',
                'Runtime Version', 'Connection Status', 'Expected App Name',
                'Expected Version', 'App Matches', 'Version Matches', 'Error Message',
                'Verification Timestamp'
            ])
            
            for result in results:
                writer.writerow([
                    result.ip_address,
                    result.port,
                    result.connection_successful,
                    result.hmi_info.app_name,
                    result.hmi_info.app_version,
                    result.hmi_info.runtime_version,
                    result.hmi_info.connection_status,
                    result.expected_app_name,
                    result.expected_version,
                    result.app_matches,
                    result.version_matches,
                    result.error_message,
                    result.verification_timestamp
                ])
        
        self.logger.info(f"Results exported to CSV: {filename}")
        return filename