"""
Enhanced Cognex Validation Module
Includes CFG file comparison, backup, and upload functionality
"""
import os
import time
import socket
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback configuration
    class MockConfig:
        class CognexConfig:
            telnet_port = 23
            connect_timeout = 5.0
            idle_read_timeout = 1.0
            overall_read_limit = 20.0
            max_backup_bytes = 50 * 1024**2
            sleep_between_commands = 0.2
            socket_timeout = 3.0
        cognex = CognexConfig()
    
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
class CognexDevice:
    """Cognex device configuration"""
    name: str
    model: str
    ip: str
    cfg_file: str = ""
    backup_path: str = ""

@dataclass
class CognexResult:
    """Result of Cognex validation"""
    device: CognexDevice
    backup_successful: bool
    backup_size: int
    backup_hash: str
    local_file_exists: bool
    local_file_hash: str
    files_match: bool
    upload_successful: bool
    error_message: str = ""
    timestamp: str = ""

class CognexValidator:
    """Enhanced Cognex validation with CFG file comparison"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("CognexValidator")
        self.results: List[CognexResult] = []
        
        # Telnet control bytes
        self.IAC, self.DONT, self.DO, self.WONT, self.WILL = 255, 254, 253, 252, 251
        
        # Set global socket timeout
        socket.setdefaulttimeout(config.cognex.socket_timeout)
    
    def negotiate_all_off(self, sock: socket.socket, data: bytes) -> bytes:
        """Respond WONT/DONT to all Telnet options and strip Telnet negotiations"""
        out = bytearray()
        i, n = 0, len(data)
        
        while i < n:
            b = data[i]
            if b == self.IAC:
                if i + 2 < n:
                    cmd, opt = data[i + 1], data[i + 2]
                    if cmd == self.DO:
                        sock.sendall(bytes([self.IAC, self.WONT, opt]))
                    elif cmd == self.WILL:
                        sock.sendall(bytes([self.IAC, self.DONT, opt]))
                    i += 3
                elif i + 1 < n and data[i + 1] == self.IAC:
                    out.append(self.IAC)
                    i += 2
                else:
                    i += 1
            else:
                out.append(b)
                i += 1
        
        return bytes(out)
    
    def recv_all_with_timeouts(self, sock: socket.socket) -> bytes:
        """Read from socket until idle or overall timeout, with Telnet negotiation handling"""
        sock.setblocking(False)
        chunks: List[bytes] = []
        total = 0
        start = last = time.time()
        
        while True:
            now = time.time()
            if now - start > config.cognex.overall_read_limit:
                break
            if now - last > config.cognex.idle_read_timeout:
                break
            
            try:
                data = sock.recv(8192)
                if data:
                    last = now
                    filtered = self.negotiate_all_off(sock, data)
                    if filtered:
                        chunks.append(filtered)
                        total += len(filtered)
                        if total >= config.cognex.max_backup_bytes:
                            break
                else:
                    break
            except BlockingIOError:
                time.sleep(0.05)
            except socket.timeout:
                break
        
        return b"".join(chunks)
    
    def dmcc_send(self, sock: socket.socket, line: str) -> None:
        """Send one DMCC command line terminated with CRLF"""
        sock.sendall((line + "\r\n").encode("utf-8"))
    
    def dmcc_backup(self, ip: str) -> bytes:
        """Connect to a Cognex reader and return bytes from DEVICE.BACKUP"""
        with socket.create_connection((ip, config.cognex.telnet_port), 
                                    timeout=config.cognex.connect_timeout) as s:
            try:
                initial = s.recv(4096)
                if initial:
                    _ = self.negotiate_all_off(s, initial)
            except socket.timeout:
                pass
            
            self.dmcc_send(s, "||>DEVICE.BACKUP")
            time.sleep(config.cognex.sleep_between_commands)
            return self.recv_all_with_timeouts(s)
    
    def build_config_load_bytes(self, cfg_path: str) -> bytes:
        """Build the CONFIG.LOAD payload"""
        with open(cfg_path, "rb") as f:
            cfg = f.read()
        header = f"||>CONFIG.LOAD {len(cfg)}\r\n".encode("utf-8")
        return header + cfg
    
    def push_config(self, ip: str, load_bytes: bytes) -> None:
        """Send CONFIG.LOAD, then CONFIG.SAVE, REBOOT, and BEEP to the Cognex reader"""
        with socket.create_connection((ip, config.cognex.telnet_port), 
                                    timeout=config.cognex.connect_timeout) as s:
            try:
                initial = s.recv(4096)
                if initial:
                    _ = self.negotiate_all_off(s, initial)
            except socket.timeout:
                pass
            
            self.logger.info("  Loading config (CONFIG.LOAD)...")
            s.sendall(load_bytes)
            time.sleep(config.cognex.sleep_between_commands)
            
            self.logger.info("  Saving configuration (CONFIG.SAVE)...")
            self.dmcc_send(s, "||>CONFIG.SAVE")
            time.sleep(config.cognex.sleep_between_commands)
            
            self.logger.info("  Rebooting reader (REBOOT)...")
            self.dmcc_send(s, "||>REBOOT")
            time.sleep(0.5)
            
            self.logger.info("  Beeping reader (BEEP 3,2)...")
            self.dmcc_send(s, "||>BEEP 3,2")
            time.sleep(config.cognex.sleep_between_commands)
    
    def sha256_bytes(self, b: bytes) -> str:
        """Return the SHA-256 hex digest for the given bytes"""
        return hashlib.sha256(b).hexdigest()
    
    def sha256_file(self, path: str) -> str:
        """Return the SHA-256 hex digest of a file"""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    
    def save_backup_bytes(self, ip: str, device_name: str, data: bytes) -> str:
        """Save backup bytes to backup directory with timestamp"""
        os.makedirs("backups", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = device_name.replace(" ", "_")
        fname = f"backups/{safe_name}_{ip}_{ts}.cfg"
        
        with open(fname, "wb") as f:
            f.write(data)
        
        return fname
    
    def process_cognex_device(self, device: CognexDevice, upload_if_different: bool = True) -> CognexResult:
        """Process a single Cognex device: backup, compare, and optionally upload"""
        self.logger.info(f"\n=== {device.name} ({device.ip}) ===")
        
        result = CognexResult(
            device=device,
            backup_successful=False,
            backup_size=0,
            backup_hash="",
            local_file_exists=False,
            local_file_hash="",
            files_match=False,
            upload_successful=False,
            timestamp=datetime.now().isoformat()
        )
        
        # Step 1: Backup current configuration
        backup = b""
        try:
            self.logger.info("  Reading current configuration (DEVICE.BACKUP)...")
            backup = self.dmcc_backup(device.ip)
            
            if not backup:
                result.error_message = "No backup data received (device returned empty)"
                self.logger.warning(f"  Warning: {result.error_message}")
            else:
                result.backup_successful = True
                result.backup_size = len(backup)
                result.backup_hash = self.sha256_bytes(backup)
                
                # Save backup to file
                backup_path = self.save_backup_bytes(device.ip, device.name, backup)
                result.device.backup_path = backup_path
                self.logger.info(f"  Backup saved: {backup_path} ({len(backup)} bytes)")
                self.logger.info(f"  Backup SHA-256: {result.backup_hash}")
                
        except Exception as e:
            result.error_message = f"Error during backup: {e}"
            self.logger.error(f"  {result.error_message}")
            return result
        
        # Step 2: Check if local CFG file exists
        if not device.cfg_file or not os.path.isfile(device.cfg_file):
            result.error_message = f"Local config file not found: {device.cfg_file}"
            self.logger.warning(f"  {result.error_message}")
            return result
        
        result.local_file_exists = True
        result.local_file_hash = self.sha256_file(device.cfg_file)
        self.logger.info(f"  Local file: {device.cfg_file}")
        self.logger.info(f"  Local SHA-256: {result.local_file_hash}")
        
        # Step 3: Compare files
        if result.backup_hash == result.local_file_hash:
            result.files_match = True
            self.logger.info("  ✓ Files are identical - no upload needed")
            return result
        else:
            result.files_match = False
            self.logger.info("  ⚠ Files differ - upload required")
        
        # Step 4: Upload if requested and files differ
        if upload_if_different:
            try:
                self.logger.info("  Uploading new configuration...")
                load_bytes = self.build_config_load_bytes(device.cfg_file)
                self.push_config(device.ip, load_bytes)
                result.upload_successful = True
                self.logger.info("  ✓ Configuration uploaded successfully")
                
            except Exception as e:
                result.error_message = f"Error uploading config: {e}"
                self.logger.error(f"  {result.error_message}")
        
        return result
    
    def validate_devices(self, devices: List[CognexDevice], upload_if_different: bool = True) -> List[CognexResult]:
        """Validate multiple Cognex devices"""
        self.logger.info(f"Starting Cognex validation for {len(devices)} devices")
        self.results = []
        
        with ProgressLogger(self.logger, len(devices), "Cognex Validation") as progress:
            for device in devices:
                try:
                    result = self.process_cognex_device(device, upload_if_different)
                    self.results.append(result)
                    progress.step(f"Completed {device.name}")
                except Exception as e:
                    self.logger.error(f"Exception processing {device.name}: {e}")
                    error_result = CognexResult(
                        device=device,
                        backup_successful=False,
                        backup_size=0,
                        backup_hash="",
                        local_file_exists=False,
                        local_file_hash="",
                        files_match=False,
                        upload_successful=False,
                        error_message=str(e),
                        timestamp=datetime.now().isoformat()
                    )
                    self.results.append(error_result)
                    progress.step(f"Failed {device.name}")
        
        return self.results
    
    def generate_report(self, results: List[CognexResult]) -> str:
        """Generate a formatted report of validation results"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("COGNEX VALIDATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary statistics
        total = len(results)
        successful_backups = len([r for r in results if r.backup_successful])
        files_match = len([r for r in results if r.files_match])
        uploads_successful = len([r for r in results if r.upload_successful])
        errors = len([r for r in results if r.error_message])
        
        report_lines.append(f"\nSUMMARY:")
        report_lines.append(f"  Total Devices: {total}")
        report_lines.append(f"  Successful Backups: {successful_backups}")
        report_lines.append(f"  Files Match: {files_match}")
        report_lines.append(f"  Successful Uploads: {uploads_successful}")
        report_lines.append(f"  Errors: {errors}")
        
        # Detailed results
        report_lines.append(f"\nDETAILED RESULTS:")
        report_lines.append("-" * 100)
        report_lines.append(f"{'Device':<25} {'IP':<16} {'Backup':<8} {'Match':<6} {'Upload':<8} {'Status'}")
        report_lines.append("-" * 100)
        
        for result in results:
            backup_status = "✓" if result.backup_successful else "✗"
            match_status = "✓" if result.files_match else "✗"
            upload_status = "✓" if result.upload_successful else "✗"
            status = "OK" if not result.error_message else "ERROR"
            
            report_lines.append(
                f"{result.device.name:<25} {result.device.ip:<16} {backup_status:<8} {match_status:<6} {upload_status:<8} {status}"
            )
        
        # Error details
        error_results = [r for r in results if r.error_message]
        if error_results:
            report_lines.append(f"\nERROR DETAILS:")
            for result in error_results:
                report_lines.append(f"  {result.device.name} ({result.device.ip}): {result.error_message}")
        
        # File details
        report_lines.append(f"\nFILE DETAILS:")
        for result in results:
            if result.backup_successful:
                report_lines.append(f"  {result.device.name}:")
                report_lines.append(f"    Backup: {result.device.backup_path} ({result.backup_size} bytes)")
                report_lines.append(f"    Local:  {result.device.cfg_file}")
                report_lines.append(f"    Match:  {'Yes' if result.files_match else 'No'}")
        
        report_lines.append("=" * 80)
        report_lines.append("Validation complete.\n")
        
        return "\n".join(report_lines)
    
    def export_results_json(self, results: List[CognexResult], filename: str = None) -> str:
        """Export results to JSON file"""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cognex_validation_{timestamp}.json"
        
        # Convert results to serializable format
        json_data = []
        for result in results:
            json_data.append({
                "device": {
                    "name": result.device.name,
                    "model": result.device.model,
                    "ip": result.device.ip,
                    "cfg_file": result.device.cfg_file,
                    "backup_path": result.device.backup_path
                },
                "backup_successful": result.backup_successful,
                "backup_size": result.backup_size,
                "backup_hash": result.backup_hash,
                "local_file_exists": result.local_file_exists,
                "local_file_hash": result.local_file_hash,
                "files_match": result.files_match,
                "upload_successful": result.upload_successful,
                "error_message": result.error_message,
                "timestamp": result.timestamp
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results exported to JSON: {filename}")
        return filename
    
    def export_results_csv(self, results: List[CognexResult], filename: str = None) -> str:
        """Export results to CSV file"""
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cognex_validation_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Device Name', 'Model', 'IP Address', 'CFG File', 'Backup Path',
                'Backup Successful', 'Backup Size', 'Backup Hash',
                'Local File Exists', 'Local File Hash', 'Files Match',
                'Upload Successful', 'Error Message', 'Timestamp'
            ])
            
            for result in results:
                writer.writerow([
                    result.device.name,
                    result.device.model,
                    result.device.ip,
                    result.device.cfg_file,
                    result.device.backup_path,
                    result.backup_successful,
                    result.backup_size,
                    result.backup_hash,
                    result.local_file_exists,
                    result.local_file_hash,
                    result.files_match,
                    result.upload_successful,
                    result.error_message,
                    result.timestamp
                ])
        
        self.logger.info(f"Results exported to CSV: {filename}")
        return filename