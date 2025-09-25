"""
Faults and Warnings Module
Handles DOCX parsing and PLC scanning for fault/warning mapping
"""
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from config import config
    from logger import get_logger, ProgressLogger
except ImportError:
    # Fallback for when modules aren't available
    class MockConfig:
        class PLCConfig:
            default_ip = "11.200.0.10"
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

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

# Regex pattern to match fault/warning tags like {[PLC]Alarm_Fault[0].3}
TAG_RE = re.compile(r"\{\[PLC\](Alarm_(Fault|Warning))\[(\d+)\]\.(\d+)\}")

@dataclass
class FaultEntry:
    """Container for fault/warning entry data"""
    source: str  # "Alarm_Fault" or "Alarm_Warning"
    index: int   # Array index
    bit: int     # Bit index
    tag: str     # Original tag string
    description: str
    resolution: str

class FaultsWarningsProcessor:
    """Enhanced faults and warnings processor with better error handling"""
    
    def __init__(self, logger=None):
        self.logger = logger or get_logger("FaultsWarnings")
        self.entries: List[FaultEntry] = []
        self.docx_path: Optional[str] = None
    
    def parse_faults_docx(self, docx_path: str) -> List[FaultEntry]:
        """
        Parse a DOCX with tables containing columns: TAG | Description | Resolution.
        Returns list of FaultEntry objects.
        """
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx not installed. Install with: pip install python-docx")
        
        if not os.path.isfile(docx_path):
            raise FileNotFoundError(f"DOCX file not found: {docx_path}")
        
        self.logger.info(f"Parsing DOCX file: {docx_path}")
        entries = []
        
        try:
            doc = Document(docx_path)
            table_count = 0
            entry_count = 0
            
            for tbl in doc.tables:
                table_count += 1
                self.logger.debug(f"Processing table {table_count} with {len(tbl.rows)} rows")
                
                for r_i, row in enumerate(tbl.rows):
                    if r_i == 0:  # Skip header row
                        continue
                    
                    cells = row.cells
                    if len(cells) < 3:
                        self.logger.warning(f"Table {table_count}, row {r_i}: Insufficient columns ({len(cells)} < 3)")
                        continue
                    
                    # Extract and normalize text from cells
                    raw_tag = (cells[0].text or "").strip()
                    desc = " ".join((cells[1].text or "").split())  # Normalize whitespace
                    res = " ".join((cells[2].text or "").split())   # Normalize whitespace
                    
                    # Skip empty rows
                    if not raw_tag and not desc and not res:
                        continue
                    
                    # Parse tag with regex
                    m = TAG_RE.search(raw_tag)
                    if not m:
                        self.logger.debug(f"Table {table_count}, row {r_i}: Unrecognized tag format: {raw_tag}")
                        continue
                    
                    try:
                        source = m.group(1)      # "Alarm_Fault" or "Alarm_Warning"
                        arr_idx = int(m.group(3))  # Array index
                        bit_idx = int(m.group(4))  # Bit index
                        
                        entry = FaultEntry(
                            source=source,
                            index=arr_idx,
                            bit=bit_idx,
                            tag=raw_tag,
                            description=desc,
                            resolution=res
                        )
                        entries.append(entry)
                        entry_count += 1
                        
                    except (ValueError, IndexError) as e:
                        self.logger.warning(f"Table {table_count}, row {r_i}: Error parsing tag {raw_tag}: {e}")
                        continue
            
            self.logger.info(f"Successfully parsed {entry_count} entries from {table_count} tables")
            self.entries = entries
            self.docx_path = docx_path
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Error parsing DOCX file: {e}")
            raise
    
    def scan_faults_from_plc(self, ip: str) -> List[FaultEntry]:
        """
        Scan PLC for active faults/warnings using loaded entries.
        Returns list of active FaultEntry objects.
        """
        if not PYLOGIX_AVAILABLE:
            raise RuntimeError("pylogix is not installed. Please run: pip install pylogix")
        
        if not self.entries:
            raise ValueError("No fault entries loaded. Call parse_faults_docx() first.")
        
        self.logger.info(f"Scanning PLC {ip} for active faults/warnings")
        
        # Group entries by source and collect unique indices
        fault_indices = sorted({e.index for e in self.entries if e.source == "Alarm_Fault"})
        warn_indices = sorted({e.index for e in self.entries if e.source == "Alarm_Warning"})
        
        self.logger.info(f"Need to read {len(fault_indices)} fault arrays and {len(warn_indices)} warning arrays")
        
        # Build tag lists
        fault_tags = [f"Alarm_Fault[{i}]" for i in fault_indices]
        warn_tags = [f"Alarm_Warning[{i}]" for i in warn_indices]
        
        # Storage for array values
        values: Dict[str, Dict[int, int]] = {
            "Alarm_Fault": {},
            "Alarm_Warning": {}
        }
        
        try:
            with PLC() as comm:
                comm.IPAddress = ip
                comm.SocketTimeout = 5
                
                # Read fault arrays
                if fault_tags:
                    self.logger.info(f"Reading fault arrays: {fault_tags}")
                    results = comm.Read(fault_tags)
                    
                    if isinstance(results, list):
                        for tag, result, idx in zip(fault_tags, results, fault_indices):
                            if result.Status == "Success":
                                try:
                                    values["Alarm_Fault"][idx] = int(result.Value)
                                    self.logger.debug(f"Fault array {idx}: {result.Value}")
                                except (ValueError, TypeError) as e:
                                    self.logger.warning(f"Failed to parse fault array {idx}: {e}")
                            else:
                                self.logger.warning(f"Failed to read fault array {idx}: {result.Status}")
                    else:
                        self.logger.error(f"Expected list of results for fault arrays, got: {type(results)}")
                
                # Read warning arrays
                if warn_tags:
                    self.logger.info(f"Reading warning arrays: {warn_tags}")
                    results = comm.Read(warn_tags)
                    
                    if isinstance(results, list):
                        for tag, result, idx in zip(warn_tags, results, warn_indices):
                            if result.Status == "Success":
                                try:
                                    values["Alarm_Warning"][idx] = int(result.Value)
                                    self.logger.debug(f"Warning array {idx}: {result.Value}")
                                except (ValueError, TypeError) as e:
                                    self.logger.warning(f"Failed to parse warning array {idx}: {e}")
                            else:
                                self.logger.warning(f"Failed to read warning array {idx}: {result.Status}")
                    else:
                        self.logger.error(f"Expected list of results for warning arrays, got: {type(results)}")
        
        except Exception as e:
            self.logger.error(f"Error communicating with PLC: {e}")
            raise
        
        # Find active entries
        active_entries = []
        for entry in self.entries:
            src = entry.source
            idx = entry.index
            bit = entry.bit
            
            val = values.get(src, {}).get(idx)
            if val is None:
                self.logger.debug(f"Skipping {entry.tag}: no value for array {idx}")
                continue
            
            if val & (1 << bit):  # Test if bit is set
                active_entries.append(entry)
                self.logger.debug(f"Active: {entry.tag} (array {idx}, bit {bit})")
        
        self.logger.info(f"Found {len(active_entries)} active faults/warnings")
        return active_entries
    
    def generate_report(self, active_entries: List[FaultEntry]) -> str:
        """Generate a formatted report of active faults and warnings"""
        if not active_entries:
            return "No active Faults/Warnings found.\n"
        
        # Separate faults and warnings
        faults = [e for e in active_entries if e.source == "Alarm_Fault"]
        warnings = [e for e in active_entries if e.source == "Alarm_Warning"]
        
        report_lines = []
        report_lines.append(f"Found {len(faults)} active Fault(s), {len(warnings)} active Warning(s)\n")
        
        if faults:
            report_lines.append("=== ACTIVE FAULTS ===")
            for entry in faults:
                report_lines.append(f"- {entry.tag}")
                report_lines.append(f"  Description: {entry.description}")
                report_lines.append(f"  Resolution : {entry.resolution}")
                report_lines.append("")
        
        if warnings:
            report_lines.append("=== ACTIVE WARNINGS ===")
            for entry in warnings:
                report_lines.append(f"- {entry.tag}")
                report_lines.append(f"  Description: {entry.description}")
                report_lines.append(f"  Resolution : {entry.resolution}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary information about loaded entries"""
        if not self.entries:
            return {
                "total_entries": 0,
                "fault_entries": 0,
                "warning_entries": 0,
                "docx_path": None
            }
        
        fault_count = len([e for e in self.entries if e.source == "Alarm_Fault"])
        warning_count = len([e for e in self.entries if e.source == "Alarm_Warning"])
        
        return {
            "total_entries": len(self.entries),
            "fault_entries": fault_count,
            "warning_entries": warning_count,
            "docx_path": self.docx_path
        }