"""
Enhanced PLC Verification Module
Verifies PLC logic, project information, and generates detailed reports
"""
import time
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback configuration
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

try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
except ImportError:
    PYLOGIX_AVAILABLE = False
    PLC = None

@dataclass
class PLCProjectInfo:
    """PLC project information"""
    project_name: str = ""
    major_revision: int = 0
    minor_revision: int = 0
    last_load_timestamp: str = ""
    checksum: str = ""
    signature: str = ""
    controller_name: str = ""
    controller_type: str = ""
    firmware_version: str = ""
    serial_number: str = ""
    ip_address: str = ""

@dataclass
class PLCVerificationResult:
    """Result of PLC verification"""
    ip_address: str
    connection_successful: bool
    project_info: PLCProjectInfo
    verification_timestamp: str
    error_message: str = ""
    expected_project_name: str = ""
    expected_major_revision: int = 0
    expected_minor_revision: int = 0
    project_matches: bool = False
    version_matches: bool = False

class PLCVerifier:
    """Enhanced PLC verification with project information and checksum validation"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("PLCVerifier")
        self.results: List[PLCVerificationResult] = []
    
    def get_plc_project_info(self, ip_address: str) -> PLCProjectInfo:
        """Get comprehensive PLC project information"""
        if not PYLOGIX_AVAILABLE:
            raise RuntimeError("pylogix is not installed. Please run: pip install pylogix")
        
        project_info = PLCProjectInfo(ip_address=ip_address)
        
        with PLC() as comm:
            comm.IPAddress = ip_address
            comm.SocketTimeout = config.plc.read_timeout
            
            # List of tags to read for project information
            project_tags = [
                "Program:MainProgram.ProjectName",
                "Program:MainProgram.MajorRevision", 
                "Program:MainProgram.MinorRevision",
                "Program:MainProgram.LastLoadTime",
                "Program:MainProgram.Checksum",
                "Program:MainProgram.Signature",
                "Program:MainProgram.ControllerName",
                "Program:MainProgram.ControllerType",
                "Program:MainProgram.FirmwareVersion",
                "Program:MainProgram.SerialNumber"
            ]
            
            # Alternative tag paths if the above don't exist
            alternative_tags = [
                "Controller.ProjectName",
                "Controller.MajorRevision",
                "Controller.MinorRevision", 
                "Controller.LastLoadTime",
                "Controller.Checksum",
                "Controller.Signature",
                "Controller.Name",
                "Controller.Type",
                "Controller.FirmwareVersion",
                "Controller.SerialNumber"
            ]
            
            # Try primary tags first
            results = comm.Read(project_tags)
            
            # If primary tags fail, try alternative tags
            if any(r.Status != "Success" for r in results):
                self.logger.warning("Primary project tags failed, trying alternative paths...")
                results = comm.Read(alternative_tags)
            
            # Parse results
            if results[0].Status == "Success":
                project_info.project_name = str(results[0].Value or "")
            if results[1].Status == "Success":
                project_info.major_revision = int(results[1].Value or 0)
            if results[2].Status == "Success":
                project_info.minor_revision = int(results[2].Value or 0)
            if results[3].Status == "Success":
                project_info.last_load_timestamp = str(results[3].Value or "")
            if results[4].Status == "Success":
                project_info.checksum = str(results[4].Value or "")
            if results[5].Status == "Success":
                project_info.signature = str(results[5].Value or "")
            if results[6].Status == "Success":
                project_info.controller_name = str(results[6].Value or "")
            if results[7].Status == "Success":
                project_info.controller_type = str(results[7].Value or "")
            if results[8].Status == "Success":
                project_info.firmware_version = str(results[8].Value or "")
            if results[9].Status == "Success":
                project_info.serial_number = str(results[9].Value or "")
            
            # If we still don't have basic info, try to get controller properties
            if not project_info.project_name:
                try:
                    # Try to get controller properties directly
                    controller_info = comm.GetPLCType()
                    if controller_info.Status == "Success":
                        project_info.controller_type = str(controller_info.Value or "")
                except Exception as e:
                    self.logger.warning(f"Could not get controller type: {e}")
            
            # Try to get controller name from system tags
            if not project_info.controller_name:
                try:
                    name_result = comm.Read("Controller.Name")
                    if name_result.Status == "Success":
                        project_info.controller_name = str(name_result.Value or "")
                except Exception:
                    pass
        
        return project_info
    
    def verify_plc(self, ip_address: str, expected_project_name: str = "", 
                   expected_major_revision: int = 0, expected_minor_revision: int = 0) -> PLCVerificationResult:
        """Verify PLC project information against expected values"""
        self.logger.info(f"Verifying PLC at {ip_address}")
        
        result = PLCVerificationResult(
            ip_address=ip_address,
            connection_successful=False,
            project_info=PLCProjectInfo(ip_address=ip_address),
            verification_timestamp=datetime.now().isoformat(),
            expected_project_name=expected_project_name,
            expected_major_revision=expected_major_revision,
            expected_minor_revision=expected_minor_revision
        )
        
        try:
            # Get project information
            project_info = self.get_plc_project_info(ip_address)
            result.project_info = project_info
            result.connection_successful = True
            
            # Verify project name
            if expected_project_name:
                result.project_matches = (project_info.project_name == expected_project_name)
                if result.project_matches:
                    self.logger.info(f"  ✓ Project name matches: {project_info.project_name}")
                else:
                    self.logger.warning(f"  ⚠ Project name mismatch - Expected: {expected_project_name}, Found: {project_info.project_name}")
            
            # Verify version
            if expected_major_revision or expected_minor_revision:
                major_match = (not expected_major_revision or project_info.major_revision == expected_major_revision)
                minor_match = (not expected_minor_revision or project_info.minor_revision == expected_minor_revision)
                result.version_matches = major_match and minor_match
                
                if result.version_matches:
                    self.logger.info(f"  ✓ Version matches: {project_info.major_revision}.{project_info.minor_revision}")
                else:
                    self.logger.warning(f"  ⚠ Version mismatch - Expected: {expected_major_revision}.{expected_minor_revision}, Found: {project_info.major_revision}.{project_info.minor_revision}")
            
            # Log project information
            self.logger.info(f"  Project Name: {project_info.project_name}")
            self.logger.info(f"  Version: {project_info.major_revision}.{project_info.minor_revision}")
            self.logger.info(f"  Last Load: {project_info.last_load_timestamp}")
            self.logger.info(f"  Controller: {project_info.controller_name} ({project_info.controller_type})")
            self.logger.info(f"  Firmware: {project_info.firmware_version}")
            self.logger.info(f"  Serial: {project_info.serial_number}")
            if project_info.checksum:
                self.logger.info(f"  Checksum: {project_info.checksum}")
            if project_info.signature:
                self.logger.info(f"  Signature: {project_info.signature}")
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"  ✗ Error verifying PLC: {e}")
        
        return result
    
    def verify_multiple_plcs(self, plc_configs: List[Dict[str, Any]]) -> List[PLCVerificationResult]:
        """Verify multiple PLCs"""
        self.logger.info(f"Starting PLC verification for {len(plc_configs)} controllers")
        self.results = []
        
        with ProgressLogger(self.logger, len(plc_configs), "PLC Verification") as progress:
            for config in plc_configs:
                try:
                    result = self.verify_plc(
                        ip_address=config.get("ip_address", ""),
                        expected_project_name=config.get("expected_project_name", ""),
                        expected_major_revision=config.get("expected_major_revision", 0),
                        expected_minor_revision=config.get("expected_minor_revision", 0)
                    )
                    self.results.append(result)
                    progress.step(f"Completed {config.get('ip_address', 'Unknown')}")
                except Exception as e:
                    self.logger.error(f"Exception verifying PLC {config.get('ip_address', 'Unknown')}: {e}")
                    error_result = PLCVerificationResult(
                        ip_address=config.get("ip_address", ""),
                        connection_successful=False,
                        project_info=PLCProjectInfo(ip_address=config.get("ip_address", "")),
                        verification_timestamp=datetime.now().isoformat(),
                        error_message=str(e),
                        expected_project_name=config.get("expected_project_name", ""),
                        expected_major_revision=config.get("expected_major_revision", 0),
                        expected_minor_revision=config.get("expected_minor_revision", 0)
                    )
                    self.results.append(error_result)
                    progress.step(f"Failed {config.get('ip_address', 'Unknown')}")
        
        return self.results
    
    def generate_report(self, results: List[PLCVerificationResult]) -> str:
        """Generate a formatted report of verification results"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("PLC VERIFICATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary statistics
        total = len(results)
        successful_connections = len([r for r in results if r.connection_successful])
        project_matches = len([r for r in results if r.project_matches])
        version_matches = len([r for r in results if r.version_matches])
        errors = len([r for r in results if r.error_message])
        
        report_lines.append(f"\nSUMMARY:")
        report_lines.append(f"  Total PLCs: {total}")
        report_lines.append(f"  Successful Connections: {successful_connections}")
        report_lines.append(f"  Project Name Matches: {project_matches}")
        report_lines.append(f"  Version Matches: {version_matches}")
        report_lines.append(f"  Errors: {errors}")
        
        # Detailed results
        report_lines.append(f"\nDETAILED RESULTS:")
        report_lines.append("-" * 120)
        report_lines.append(f"{'IP Address':<16} {'Project Name':<25} {'Version':<10} {'Controller':<20} {'Status'}")
        report_lines.append("-" * 120)
        
        for result in results:
            project_name = result.project_info.project_name[:24] if result.project_info.project_name else "Unknown"
            version = f"{result.project_info.major_revision}.{result.project_info.minor_revision}"
            controller = result.project_info.controller_name[:19] if result.project_info.controller_name else "Unknown"
            
            if result.error_message:
                status = "ERROR"
            elif result.connection_successful:
                status = "OK"
            else:
                status = "FAILED"
            
            report_lines.append(
                f"{result.ip_address:<16} {project_name:<25} {version:<10} {controller:<20} {status}"
            )
        
        # Detailed information for each PLC
        report_lines.append(f"\nDETAILED INFORMATION:")
        for result in results:
            report_lines.append(f"\nPLC: {result.ip_address}")
            report_lines.append(f"  Project Name: {result.project_info.project_name}")
            report_lines.append(f"  Version: {result.project_info.major_revision}.{result.project_info.minor_revision}")
            report_lines.append(f"  Last Load Time: {result.project_info.last_load_timestamp}")
            report_lines.append(f"  Controller Name: {result.project_info.controller_name}")
            report_lines.append(f"  Controller Type: {result.project_info.controller_type}")
            report_lines.append(f"  Firmware Version: {result.project_info.firmware_version}")
            report_lines.append(f"  Serial Number: {result.project_info.serial_number}")
            if result.project_info.checksum:
                report_lines.append(f"  Checksum: {result.project_info.checksum}")
            if result.project_info.signature:
                report_lines.append(f"  Signature: {result.project_info.signature}")
            
            if result.expected_project_name:
                report_lines.append(f"  Expected Project: {result.expected_project_name}")
                report_lines.append(f"  Project Match: {'✓' if result.project_matches else '✗'}")
            
            if result.expected_major_revision or result.expected_minor_revision:
                expected_version = f"{result.expected_major_revision}.{result.expected_minor_revision}"
                report_lines.append(f"  Expected Version: {expected_version}")
                report_lines.append(f"  Version Match: {'✓' if result.version_matches else '✗'}")
            
            if result.error_message:
                report_lines.append(f"  Error: {result.error_message}")
        
        report_lines.append("=" * 80)
        report_lines.append("Verification complete.\n")
        
        return "\n".join(report_lines)
    
    def export_results_json(self, results: List[PLCVerificationResult], filename: str = None) -> str:
        """Export results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plc_verification_{timestamp}.json"
        
        # Convert results to serializable format
        json_data = []
        for result in results:
            json_data.append({
                "ip_address": result.ip_address,
                "connection_successful": result.connection_successful,
                "project_info": asdict(result.project_info),
                "verification_timestamp": result.verification_timestamp,
                "error_message": result.error_message,
                "expected_project_name": result.expected_project_name,
                "expected_major_revision": result.expected_major_revision,
                "expected_minor_revision": result.expected_minor_revision,
                "project_matches": result.project_matches,
                "version_matches": result.version_matches
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results exported to JSON: {filename}")
        return filename
    
    def export_results_csv(self, results: List[PLCVerificationResult], filename: str = None) -> str:
        """Export results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plc_verification_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'IP Address', 'Connection Successful', 'Project Name', 'Major Revision', 'Minor Revision',
                'Last Load Timestamp', 'Controller Name', 'Controller Type', 'Firmware Version',
                'Serial Number', 'Checksum', 'Signature', 'Expected Project Name',
                'Expected Major Revision', 'Expected Minor Revision', 'Project Matches',
                'Version Matches', 'Error Message', 'Verification Timestamp'
            ])
            
            for result in results:
                writer.writerow([
                    result.ip_address,
                    result.connection_successful,
                    result.project_info.project_name,
                    result.project_info.major_revision,
                    result.project_info.minor_revision,
                    result.project_info.last_load_timestamp,
                    result.project_info.controller_name,
                    result.project_info.controller_type,
                    result.project_info.firmware_version,
                    result.project_info.serial_number,
                    result.project_info.checksum,
                    result.project_info.signature,
                    result.expected_project_name,
                    result.expected_major_revision,
                    result.expected_minor_revision,
                    result.project_matches,
                    result.version_matches,
                    result.error_message,
                    result.verification_timestamp
                ])
        
        self.logger.info(f"Results exported to CSV: {filename}")
        return filename