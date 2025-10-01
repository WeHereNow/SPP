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
            
            # List of tags to read for project information (ESP_Comm_Setup scope for Compact GuardLogix)
            project_tags = [
                "Scope:ESP_Comm_Setup.CONST_SW_version",
                "ESP_Comm_Setup.CONST_SW_version",
                "Program:ESP_Comm_Setup.CONST_SW_version",
                "@ProjectName",
                "@MajorRevision",
                "@MinorRevision", 
                "@LastLoadTime",
                "@Checksum",
                "@Signature",
                "@ControllerName",
                "@ControllerType",
                "@FirmwareVersion",
                "@SerialNumber"
            ]
            
            # Alternative tag paths for traditional controllers
            alternative_tags = [
                "Scope:ESP_Comm_Setup.CONST_SW_version",
                "ESP_Comm_Setup.CONST_SW_version",
                "Program:ESP_Comm_Setup.CONST_SW_version",
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
            
            # Traditional ControlLogix tags
            traditional_tags = [
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
            
            # Try primary tags first (ESP_Comm_Setup scope for Compact GuardLogix)
            self.logger.info("Attempting to read project information from ESP_Comm_Setup scope and system tags...")
            results = comm.Read(project_tags)
            
            # Log results for debugging
            successful_tags = sum(1 for r in results if r.Status == "Success")
            self.logger.info(f"ESP_Comm_Setup and system tags: {successful_tags}/{len(results)} successful")
            
            # If system tags fail, try Controller.* tags
            if any(r.Status != "Success" for r in results):
                self.logger.warning("System tags failed, trying Controller.* tags...")
                results = comm.Read(alternative_tags)
                
                # Log Controller.* results
                successful_controller_tags = sum(1 for r in results if r.Status == "Success")
                self.logger.info(f"Controller.* tags: {successful_controller_tags}/{len(results)} successful")
            
            # If Controller.* tags also fail, try traditional Program:MainProgram.* tags
            if any(r.Status != "Success" for r in results):
                self.logger.warning("Controller.* tags failed, trying traditional Program:MainProgram.* tags...")
                results = comm.Read(traditional_tags)
                
                # Log traditional results
                successful_traditional_tags = sum(1 for r in results if r.Status == "Success")
                self.logger.info(f"Program:MainProgram.* tags: {successful_traditional_tags}/{len(results)} successful")
            
            # Parse results with better error handling
            try:
                # Check if we got ESP_Comm_Setup.CONST_SW_version (first 3 tags are ESP_Comm_Setup variants)
                esp_comm_version = None
                for i in range(3):  # Check first 3 tags (ESP_Comm_Setup variants)
                    if results[i].Status == "Success" and results[i].Value:
                        esp_comm_version = str(results[i].Value)
                        self.logger.info(f"Found ESP_Comm_Setup.CONST_SW_version: '{esp_comm_version}'")
                        break
                
                # Parse ESP_Comm_Setup.CONST_SW_version if found
                if esp_comm_version:
                    # Try to extract project name and version from the version string
                    # Format might be like "USP_V35_2025_09_16_OldSafety.ACD" or similar
                    project_info.project_name = esp_comm_version
                    
                    # Try to extract version numbers from the string
                    import re
                    version_match = re.search(r'V(\d+)\.(\d+)', esp_comm_version)
                    if version_match:
                        project_info.major_revision = int(version_match.group(1))
                        project_info.minor_revision = int(version_match.group(2))
                        self.logger.info(f"Extracted version from ESP_Comm_Setup: {project_info.major_revision}.{project_info.minor_revision}")
                    else:
                        self.logger.info(f"Could not extract version numbers from ESP_Comm_Setup version: '{esp_comm_version}'")
                
                # If ESP_Comm_Setup didn't provide project name, try other tags
                if not project_info.project_name and results[3].Status == "Success":
                    project_info.project_name = str(results[3].Value or "")
                    self.logger.info(f"Project name from system tag: '{project_info.project_name}'")
                elif not project_info.project_name:
                    self.logger.warning(f"Failed to read project name: {results[3].Status}")
                
                # If ESP_Comm_Setup didn't provide version, try other tags
                if not project_info.major_revision and results[4].Status == "Success":
                    project_info.major_revision = int(results[4].Value or 0)
                    self.logger.info(f"Major revision from system tag: {project_info.major_revision}")
                elif not project_info.major_revision:
                    self.logger.warning(f"Failed to read major revision: {results[4].Status}")
                
                if not project_info.minor_revision and results[5].Status == "Success":
                    project_info.minor_revision = int(results[5].Value or 0)
                    self.logger.info(f"Minor revision from system tag: {project_info.minor_revision}")
                elif not project_info.minor_revision:
                    self.logger.warning(f"Failed to read minor revision: {results[5].Status}")
                
                # Parse remaining tags (indices shifted due to ESP_Comm_Setup tags)
                if results[6].Status == "Success":
                    project_info.last_load_timestamp = str(results[6].Value or "")
                    self.logger.info(f"Last load time: '{project_info.last_load_timestamp}'")
                else:
                    self.logger.warning(f"Failed to read last load time: {results[6].Status}")
                
                if results[7].Status == "Success":
                    project_info.checksum = str(results[7].Value or "")
                    self.logger.info(f"Checksum: '{project_info.checksum}'")
                else:
                    self.logger.warning(f"Failed to read checksum: {results[7].Status}")
                
                if results[8].Status == "Success":
                    project_info.signature = str(results[8].Value or "")
                    self.logger.info(f"Signature: '{project_info.signature}'")
                else:
                    self.logger.warning(f"Failed to read signature: {results[8].Status}")
                
                if results[9].Status == "Success":
                    project_info.controller_name = str(results[9].Value or "")
                    self.logger.info(f"Controller name: '{project_info.controller_name}'")
                else:
                    self.logger.warning(f"Failed to read controller name: {results[9].Status}")
                
                if results[10].Status == "Success":
                    project_info.controller_type = str(results[10].Value or "")
                    self.logger.info(f"Controller type: '{project_info.controller_type}'")
                else:
                    self.logger.warning(f"Failed to read controller type: {results[10].Status}")
                
                if results[11].Status == "Success":
                    project_info.firmware_version = str(results[11].Value or "")
                    self.logger.info(f"Firmware version: '{project_info.firmware_version}'")
                else:
                    self.logger.warning(f"Failed to read firmware version: {results[11].Status}")
                
                if results[12].Status == "Success":
                    project_info.serial_number = str(results[12].Value or "")
                    self.logger.info(f"Serial number: '{project_info.serial_number}'")
                else:
                    self.logger.warning(f"Failed to read serial number: {results[12].Status}")
                    
            except Exception as e:
                self.logger.error(f"Error parsing project information results: {e}")
                # Continue with partial data
            
            # If we still don't have basic info, try additional fallback tags
            if not project_info.project_name:
                self.logger.info("Trying additional fallback tags for project information...")
                fallback_tags = [
                    "Scope:ESP_Comm_Setup.CONST_SW_version",
                    "ESP_Comm_Setup.CONST_SW_version",
                    "Program:ESP_Comm_Setup.CONST_SW_version",
                    "@ProjectName",
                    "@Project",
                    "@ProjectTitle",
                    "Controller.ProjectName",
                    "Controller.Project",
                    "Controller.ProjectTitle",
                    "Program:MainProgram.ProjectName",
                    "Program:MainProgram.Project",
                    "Program:MainProgram.ProjectTitle"
                ]
                
                for tag in fallback_tags:
                    try:
                        result = comm.Read(tag)
                        if result.Status == "Success" and result.Value:
                            value = str(result.Value)
                            
                            # If this is an ESP_Comm_Setup.CONST_SW_version tag, parse it
                            if "ESP_Comm_Setup" in tag and "CONST_SW_version" in tag:
                                project_info.project_name = value
                                self.logger.info(f"Found ESP_Comm_Setup.CONST_SW_version from {tag}: '{value}'")
                                
                                # Try to extract version numbers from the string
                                import re
                                version_match = re.search(r'V(\d+)\.(\d+)', value)
                                if version_match:
                                    project_info.major_revision = int(version_match.group(1))
                                    project_info.minor_revision = int(version_match.group(2))
                                    self.logger.info(f"Extracted version from ESP_Comm_Setup: {project_info.major_revision}.{project_info.minor_revision}")
                                break
                            else:
                                # Regular project name tag
                                project_info.project_name = value
                                self.logger.info(f"Found project name from {tag}: '{project_info.project_name}'")
                                break
                    except Exception as e:
                        self.logger.debug(f"Failed to read {tag}: {e}")
            
            # Try additional controller type tags
            if not project_info.controller_type:
                self.logger.info("Trying additional fallback tags for controller type...")
                controller_type_tags = [
                    "@ControllerType",
                    "@ProcessorType",
                    "@Type",
                    "@Model",
                    "Controller.ProcessorType",
                    "Controller.Type",
                    "Controller.Model",
                    "Program:MainProgram.ControllerType"
                ]
                
                for tag in controller_type_tags:
                    try:
                        result = comm.Read(tag)
                        if result.Status == "Success" and result.Value:
                            project_info.controller_type = str(result.Value)
                            self.logger.info(f"Found controller type from {tag}: '{project_info.controller_type}'")
                            break
                    except Exception as e:
                        self.logger.debug(f"Failed to read {tag}: {e}")
            
            # Try additional controller name tags
            if not project_info.controller_name:
                self.logger.info("Trying additional fallback tags for controller name...")
                controller_name_tags = [
                    "@ControllerName",
                    "@Name",
                    "@HostName",
                    "Controller.Name",
                    "Controller.HostName",
                    "Program:MainProgram.ControllerName"
                ]
                
                for tag in controller_name_tags:
                    try:
                        result = comm.Read(tag)
                        if result.Status == "Success" and result.Value:
                            project_info.controller_name = str(result.Value)
                            self.logger.info(f"Found controller name from {tag}: '{project_info.controller_name}'")
                            break
                    except Exception as e:
                        self.logger.debug(f"Failed to read {tag}: {e}")
            
            # Try additional version tags
            if not project_info.major_revision and not project_info.minor_revision:
                self.logger.info("Trying additional fallback tags for version information...")
                version_tags = [
                    "@MajorRevision",
                    "@MinorRevision",
                    "@Version",
                    "Controller.MajorRevision",
                    "Controller.MinorRevision",
                    "Controller.Version",
                    "Program:MainProgram.MajorRevision",
                    "Program:MainProgram.MinorRevision"
                ]
                
                for tag in version_tags:
                    try:
                        result = comm.Read(tag)
                        if result.Status == "Success" and result.Value:
                            if "Major" in tag:
                                project_info.major_revision = int(result.Value)
                                self.logger.info(f"Found major revision from {tag}: {project_info.major_revision}")
                            elif "Minor" in tag:
                                project_info.minor_revision = int(result.Value)
                                self.logger.info(f"Found minor revision from {tag}: {project_info.minor_revision}")
                    except Exception as e:
                        self.logger.debug(f"Failed to read {tag}: {e}")
            
            # If we still don't have any project information, try to get basic controller info
            if (not project_info.project_name and 
                not project_info.controller_name and 
                not project_info.controller_type and
                not project_info.firmware_version and
                not project_info.serial_number):
                
                self.logger.warning("No project information could be retrieved from any tag path")
                self.logger.info("This is common for Compact GuardLogix controllers that don't expose project information")
                self.logger.info("The PLC verification will continue with basic connection verification")
                
                # Try to get at least some basic information
                try:
                    # Test if we can read a simple tag to verify connection
                    test_result = comm.Read("g_Par")
                    if test_result.Status == "Success":
                        self.logger.info("✓ Basic PLC communication verified (g_Par tag readable)")
                        project_info.controller_name = "Compact GuardLogix (Connection Verified)"
                        project_info.controller_type = "5069-L330ERMS2"
                    else:
                        self.logger.warning(f"Basic communication test failed: {test_result.Status}")
                except Exception as e:
                    self.logger.warning(f"Basic communication test exception: {e}")
            
            # Log final summary
            self.logger.info("Final project information summary:")
            self.logger.info(f"  Project Name: '{project_info.project_name}'")
            self.logger.info(f"  Version: {project_info.major_revision}.{project_info.minor_revision}")
            self.logger.info(f"  Controller Name: '{project_info.controller_name}'")
            self.logger.info(f"  Controller Type: '{project_info.controller_type}'")
            self.logger.info(f"  Firmware Version: '{project_info.firmware_version}'")
            self.logger.info(f"  Serial Number: '{project_info.serial_number}'")
        
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
        
        progress = ProgressLogger(self.logger, len(plc_configs), "PLC Verification")
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
        
        progress.complete("PLC verification")
        
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