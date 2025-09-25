"""
SPP All-In-One Toolkit - Enhanced Version
Industrial automation toolkit with improved performance, logging, and user experience
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import Dict, List, Optional
from datetime import datetime

# Import our enhanced modules
try:
    from config import config
    from logger import get_logger, ProgressLogger
    from network_validation import NetworkValidator, DeviceResult
    from plc_communication import EnhancedPLCValidator
    from cognex_validation import CognexValidator, CognexDevice, CognexResult
    from plc_verification import PLCVerifier, PLCVerificationResult
    from hmi_verification import HMIVerifier, HMIVerificationResult
    ENHANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced modules not available: {e}")
    print("Falling back to basic functionality...")
    ENHANCED_MODULES_AVAILABLE = False
    
    # Create minimal fallbacks
    class MockConfig:
        class NetworkConfig:
            default_probes = 3
            default_retries = 2
            default_timeout_ms = 700
            require_min_replies = 1
            arp_warmup_delay = 0.08
            backoff_delay = 0.3
        class PLCConfig:
            default_ip = "11.200.0.10"
            connection_timeout = 5.0
            read_timeout = 10.0
            max_retries = 3
            retry_delay = 1.0
        class UIConfig:
            window_size = "1120x760"
            window_title = "SPP All-In-One Toolkit — Enhanced"
            log_max_lines = 10000
            auto_scroll = True
            theme = "dark"
        network = NetworkConfig()
        plc = PLCConfig()
        ui = UIConfig()
    
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
    
    # Mock classes for enhanced functionality
    class NetworkValidator:
        def __init__(self, logger=None):
            pass
        def validate_devices_concurrent(self, devices):
            return []
        def generate_report(self, results):
            return "Enhanced network validation not available"
        def export_results_csv(self, results, filename):
            pass
    
    class DeviceResult:
        pass
    
    class EnhancedPLCValidator:
        def __init__(self, ip, logger=None):
            pass
        def generate_comprehensive_report(self):
            return "Enhanced PLC validation not available"
        def close(self):
            pass
    
    # Mock classes for new enhanced functionality
    class CognexValidator:
        def __init__(self, logger=None):
            pass
        def validate_devices(self, devices, upload_if_different=True):
            return []
        def generate_report(self, results):
            return "Enhanced Cognex validation not available"
        def export_results_json(self, results, filename=None):
            return "cognex_results.json"
        def export_results_csv(self, results, filename=None):
            return "cognex_results.csv"
    
    class CognexDevice:
        def __init__(self, name, model, ip, cfg_file="", backup_path=""):
            self.name = name
            self.model = model
            self.ip = ip
            self.cfg_file = cfg_file
            self.backup_path = backup_path
    
    class CognexResult:
        pass
    
    class PLCVerifier:
        def __init__(self, logger=None):
            pass
        def verify_plc(self, ip_address, expected_project_name="", expected_major_revision=0, expected_minor_revision=0):
            return None
        def generate_report(self, results):
            return "Enhanced PLC verification not available"
        def export_results_json(self, results, filename=None):
            return "plc_verification.json"
        def export_results_csv(self, results, filename=None):
            return "plc_verification.csv"
    
    class PLCVerificationResult:
        pass
    
    class HMIVerifier:
        def __init__(self, logger=None):
            pass
        def verify_hmi(self, ip_address, port=2222, expected_app_name="", expected_version=""):
            return None
        def generate_report(self, results):
            return "Enhanced HMI verification not available"
        def export_results_json(self, results, filename=None):
            return "hmi_verification.json"
        def export_results_csv(self, results, filename=None):
            return "hmi_verification.csv"
    
    class HMIVerificationResult:
        pass

# Import original modules for compatibility
try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
except ImportError:
    PYLOGIX_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Dark theme colors (enhanced)
BG = "#0c0f13"
PANEL = "#11161d"
SURFACE = "#151b24"
RAISED = "#1a222d"
TEXT = "#e6eaf0"
SUBTEXT = "#a7b0bd"
ACCENT = "#00d1ff"
ACCENT_DIM = "#00a0c0"
BORDER = "#233142"
ERROR = "#e74c3c"
SUCCESS = "#27ae60"
WARNING = "#f39c12"
MONO = ("Consolas", 10)
UIFONT = ("Segoe UI", 10)

# Device configurations
PROGRAM1_DEVICES = {
    "11.200.0.1": "Cisco ISA 3000 NAT",
    "11.200.0.2": "Cisco IE 2000 Switch",
    "11.200.0.10": "AB CompactLogix SmartPac PLC",
    "11.200.0.180": "AB PanelView Plus HMI",
    "11.200.1.24": "1734 Point IO",
    "11.200.1.25": "1734 Point IO",
    "11.200.1.21": "Kinetix 300 Nip Roller Servo",
    "11.200.1.22": "Kinetix 300 Gripper Servo",
    "11.200.1.18": "Cognex DM262 Ship Verify Reader",
    "11.200.1.19": "Cognex Tote Reader",
    "11.200.1.20": "Kinetix 5700",
    "11.200.1.30": "AL1120 IO Link",
    "11.200.1.35": "Keyence IV4 Sensor",
}

class EnhancedApp(tk.Tk):
    """Enhanced SPP Toolkit with improved UI and functionality"""
    
    def __init__(self):
        super().__init__()
        self.title(config.ui.window_title)
        self.geometry(config.ui.window_size)
        
        # Initialize logger
        self.logger = get_logger("SPPToolkit")
        self.logger.info("Starting SPP All-In-One Toolkit - Enhanced Version")
        
        # Apply dark theme
        self.style = self._apply_dark_theme()
        
        # Initialize components
        self.network_validator = None
        self.plc_validator = None
        
        # Build UI
        self._build_header()
        self._build_notebook()
        self._build_tabs()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        self.logger.info("Application initialized successfully")
    
    def _apply_dark_theme(self) -> ttk.Style:
        """Apply enhanced dark theme"""
        self.configure(bg=BG)
        self.option_add("*Font", UIFONT)
        self.option_add("*TCombobox*Listbox*Font", UIFONT)
        
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Base styles
        style.configure(".", background=BG, foreground=TEXT, fieldbackground=SURFACE)
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("TNotebook", background=BG, borderwidth=0)
        
        # Enhanced tab styles
        style.configure("TNotebook.Tab", 
                       background=SURFACE, 
                       foreground=SUBTEXT,
                       padding=(14, 8), 
                       borderwidth=0)
        style.map("TNotebook.Tab",
                 background=[("selected", RAISED)],
                 foreground=[("selected", TEXT)])
        
        # Enhanced button styles
        style.configure("TButton", 
                       background=SURFACE, 
                       foreground=TEXT,
                       borderwidth=1, 
                       padding=(12, 8))
        style.map("TButton",
                 background=[("active", RAISED)],
                 foreground=[("disabled", "#6b7280")])
        
        # Success and error button styles
        style.configure("Success.TButton", 
                       background=SUCCESS, 
                       foreground="white",
                       borderwidth=0, 
                       padding=(14, 9))
        style.configure("Error.TButton", 
                       background=ERROR, 
                       foreground="white",
                       borderwidth=0, 
                       padding=(14, 9))
        
        # Accent button
        style.configure("Accent.TButton", 
                       background=ACCENT, 
                       foreground="#001018",
                       borderwidth=0, 
                       padding=(14, 9))
        style.map("Accent.TButton",
                 background=[("active", ACCENT_DIM), ("disabled", "#335561")],
                 foreground=[("disabled", "#122027")])
        
        # Entry and other widgets
        style.configure("TEntry", 
                       fieldbackground=SURFACE, 
                       foreground=TEXT,
                       insertcolor=TEXT)
        style.configure("Vertical.TScrollbar", 
                       background=SURFACE, 
                       troughcolor=BG,
                       bordercolor=BORDER, 
                       arrowcolor=TEXT)
        style.configure("TSeparator", background=BORDER)
        
        return style
    
    def _build_header(self):
        """Build enhanced header with status indicators"""
        header = ttk.Frame(self)
        header.configure(style="TFrame")
        header.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Accent line
        tk.Frame(header, height=3, bg=ACCENT, bd=0, highlightthickness=0).pack(fill=tk.X, side=tk.TOP)
        
        # Title row
        title_row = ttk.Frame(header)
        title_row.pack(fill=tk.X, pady=(10, 8))
        
        ttk.Label(title_row, text="SPP All-In-One Toolkit", 
                 font=("Segoe UI Semibold", 14)).pack(side=tk.LEFT)
        ttk.Label(title_row, text="Enhanced • Network • PLC • Cognex • Verification • Faults", 
                 foreground=SUBTEXT).pack(side=tk.LEFT, padx=12)
        
        # Status indicators
        status_frame = ttk.Frame(title_row)
        status_frame.pack(side=tk.RIGHT)
        
        # Dependency status
        pylogix_status = "✓" if PYLOGIX_AVAILABLE else "✗"
        docx_status = "✓" if DOCX_AVAILABLE else "✗"
        enhanced_status = "✓" if ENHANCED_MODULES_AVAILABLE else "✗"
        
        ttk.Label(status_frame, text=f"Enhanced: {enhanced_status}", 
                 foreground=SUCCESS if ENHANCED_MODULES_AVAILABLE else WARNING).pack(side=tk.RIGHT, padx=5)
        ttk.Label(status_frame, text=f"pylogix: {pylogix_status}", 
                 foreground=SUCCESS if PYLOGIX_AVAILABLE else ERROR).pack(side=tk.RIGHT, padx=5)
        ttk.Label(status_frame, text=f"docx: {docx_status}", 
                 foreground=SUCCESS if DOCX_AVAILABLE else ERROR).pack(side=tk.RIGHT, padx=5)
    
    def _build_notebook(self):
        """Build the main notebook widget"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _build_tabs(self):
        """Build all application tabs"""
        self._build_network_tab()
        self._build_plc_tab()
        self._build_cognex_tab()
        self._build_plc_verification_tab()
        self._build_hmi_verification_tab()
        self._build_faults_tab()
        self._build_settings_tab()
    
    def _build_network_tab(self):
        """Build enhanced network validation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Network Validation")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Network Validation", "Concurrent multi-probe ping with response time tracking")
        
        # Control buttons
        self.btn_network_run = ttk.Button(toolbar, text="Run Validation", 
                                         style="Accent.TButton", 
                                         command=self._on_run_network_validation)
        self.btn_network_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_network_export = ttk.Button(toolbar, text="Export CSV", 
                                           command=self._on_export_network_results)
        self.btn_network_export.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_network_export.configure(state=tk.DISABLED)
        
        # Progress bar
        self.network_progress = ttk.Progressbar(toolbar, mode='indeterminate')
        self.network_progress.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)
        
        # Results display
        self.network_text, self.network_logger = self._make_text_panel(tab)
        self.network_results = []
    
    def _build_plc_tab(self):
        """Build enhanced PLC validation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PLC Validation")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "PLC Validation", "Enhanced parameter reading with caching and error recovery")
        
        # PLC IP input
        ttk.Label(toolbar, text="PLC IP:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_plc_ip = ttk.Entry(toolbar, width=24)
        self.entry_plc_ip.insert(0, config.plc.default_ip)
        self.entry_plc_ip.pack(side=tk.LEFT, padx=(0, 6))
        
        ttk.Button(toolbar, text="Test IP", 
                  command=self._on_test_plc_ip).pack(side=tk.LEFT, padx=6)
        
        # Control buttons
        self.btn_plc_run = ttk.Button(toolbar, text="Run Validation", 
                                     style="Accent.TButton", 
                                     command=self._on_run_plc_validation)
        self.btn_plc_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_plc_diagnose = ttk.Button(toolbar, text="Diagnose Connection", 
                                          command=self._on_diagnose_plc_connection)
        self.btn_plc_diagnose.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_plc_test_tags = ttk.Button(toolbar, text="Test Individual Tags", 
                                           command=self._on_test_individual_tags)
        self.btn_plc_test_tags.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_plc_export = ttk.Button(toolbar, text="Export Report", 
                                        command=self._on_export_plc_report)
        self.btn_plc_export.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_plc_export.configure(state=tk.DISABLED)
        
        # Results display
        self.plc_text, self.plc_logger = self._make_text_panel(tab)
    
    def _build_cognex_tab(self):
        """Build enhanced Cognex validation tab with CFG file comparison"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Cognex Validation")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Cognex Validation", "Backup current config and upload selected .cfg if different")
        
        # Control buttons
        self.btn_cognex_run = ttk.Button(toolbar, text="Run Backup & Upload", 
                                        style="Accent.TButton", 
                                        command=self._on_run_cognex_validation)
        self.btn_cognex_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_cognex_export_json = ttk.Button(toolbar, text="Export JSON", 
                                                command=self._on_export_cognex_json)
        self.btn_cognex_export_json.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_cognex_export_json.configure(state=tk.DISABLED)
        
        self.btn_cognex_export_csv = ttk.Button(toolbar, text="Export CSV", 
                                               command=self._on_export_cognex_csv)
        self.btn_cognex_export_csv.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_cognex_export_csv.configure(state=tk.DISABLED)
        
        # Device configuration area
        config_frame = ttk.Frame(tab)
        config_frame.pack(fill=tk.X, padx=10, pady=6)
        
        # Header for device list
        header = ttk.Frame(config_frame)
        header.pack(fill=tk.X, pady=(6, 2))
        ttk.Label(header, text="Device", width=28, foreground=SUBTEXT).pack(side=tk.LEFT, padx=4)
        ttk.Label(header, text="IP", width=18, foreground=SUBTEXT).pack(side=tk.LEFT, padx=4)
        ttk.Label(header, text="Config File (.cfg)", width=48, foreground=SUBTEXT).pack(side=tk.LEFT, padx=4)
        
        # Cognex devices configuration
        self.cognex_devices = [
            CognexDevice("Ship Verify Reader", "Cognex DM262", "11.200.1.18"),
            CognexDevice("KO Tote Reader", "Cognex DataMan", "11.200.1.19"),
        ]
        
        self.cognex_path_vars = []
        for device in self.cognex_devices:
            row = ttk.Frame(config_frame)
            row.pack(fill=tk.X, pady=3)
            
            ttk.Label(row, text=f"{device.name} ({device.model})", width=28).pack(side=tk.LEFT, padx=4)
            ttk.Label(row, text=device.ip, width=18, foreground=SUBTEXT).pack(side=tk.LEFT, padx=4)
            
            var = tk.StringVar()
            var.set("SHIPconfig.cfg" if "Ship" in device.name else "KOconfig.cfg")
            self.cognex_path_vars.append(var)
            
            entry = ttk.Entry(row, textvariable=var, width=54)
            entry.pack(side=tk.LEFT, padx=4)
            
            def browse_cfg(var_ref=var):
                path = filedialog.askopenfilename(
                    title="Select .cfg file",
                    filetypes=[("CFG files", "*.cfg"), ("All files", "*.*")]
                )
                if path:
                    var_ref.set(path)
            
            ttk.Button(row, text="Browse", command=browse_cfg).pack(side=tk.LEFT, padx=4)
        
        # Results display
        self.cognex_text, self.cognex_logger = self._make_text_panel(tab)
        self.cognex_results = []
    
    def _build_plc_verification_tab(self):
        """Build PLC verification tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PLC Verification")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "PLC Verification", "Verify PLC project name, version, timestamp, and checksum")
        
        # PLC configuration
        config_frame = ttk.Frame(tab)
        config_frame.pack(fill=tk.X, padx=10, pady=6)
        
        # PLC IP input
        ip_frame = ttk.Frame(config_frame)
        ip_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ip_frame, text="PLC IP Address:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_plc_verify_ip = ttk.Entry(ip_frame, width=24)
        self.entry_plc_verify_ip.insert(0, config.plc.default_ip)
        self.entry_plc_verify_ip.pack(side=tk.LEFT, padx=(0, 20))
        
        # Expected values
        expected_frame = ttk.Frame(config_frame)
        expected_frame.pack(fill=tk.X, pady=2)
        ttk.Label(expected_frame, text="Expected Project Name:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_plc_expected_project = ttk.Entry(expected_frame, width=30)
        self.entry_plc_expected_project.pack(side=tk.LEFT, padx=(0, 20))
        
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=2)
        ttk.Label(version_frame, text="Expected Version:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_plc_expected_major = ttk.Entry(version_frame, width=8)
        self.entry_plc_expected_major.insert(0, "1")
        self.entry_plc_expected_major.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(version_frame, text=".").pack(side=tk.LEFT)
        self.entry_plc_expected_minor = ttk.Entry(version_frame, width=8)
        self.entry_plc_expected_minor.insert(0, "0")
        self.entry_plc_expected_minor.pack(side=tk.LEFT, padx=(5, 20))
        
        # Control buttons
        self.btn_plc_verify_run = ttk.Button(toolbar, text="Verify PLC", 
                                            style="Accent.TButton", 
                                            command=self._on_run_plc_verification)
        self.btn_plc_verify_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_plc_verify_export_json = ttk.Button(toolbar, text="Export JSON", 
                                                    command=self._on_export_plc_verify_json)
        self.btn_plc_verify_export_json.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_plc_verify_export_json.configure(state=tk.DISABLED)
        
        self.btn_plc_verify_export_csv = ttk.Button(toolbar, text="Export CSV", 
                                                   command=self._on_export_plc_verify_csv)
        self.btn_plc_verify_export_csv.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_plc_verify_export_csv.configure(state=tk.DISABLED)
        
        # Results display
        self.plc_verify_text, self.plc_verify_logger = self._make_text_panel(tab)
        self.plc_verify_results = []
    
    def _build_hmi_verification_tab(self):
        """Build HMI verification tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="HMI Verification")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "HMI Verification", "Verify HMI runtime app name and version")
        
        # HMI configuration
        config_frame = ttk.Frame(tab)
        config_frame.pack(fill=tk.X, padx=10, pady=6)
        
        # HMI IP input
        ip_frame = ttk.Frame(config_frame)
        ip_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ip_frame, text="HMI IP Address:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_hmi_verify_ip = ttk.Entry(ip_frame, width=24)
        self.entry_hmi_verify_ip.insert(0, "11.200.0.180")
        self.entry_hmi_verify_ip.pack(side=tk.LEFT, padx=(0, 20))
        
        # Port input
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=2)
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_hmi_verify_port = ttk.Entry(port_frame, width=8)
        self.entry_hmi_verify_port.insert(0, "2222")
        self.entry_hmi_verify_port.pack(side=tk.LEFT, padx=(0, 20))
        
        # Expected values
        expected_frame = ttk.Frame(config_frame)
        expected_frame.pack(fill=tk.X, pady=2)
        ttk.Label(expected_frame, text="Expected App Name:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_hmi_expected_app = ttk.Entry(expected_frame, width=30)
        self.entry_hmi_expected_app.insert(0, "FactoryTalk View SE")
        self.entry_hmi_expected_app.pack(side=tk.LEFT, padx=(0, 20))
        
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=2)
        ttk.Label(version_frame, text="Expected Version:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_hmi_expected_version = ttk.Entry(version_frame, width=20)
        self.entry_hmi_expected_version.pack(side=tk.LEFT, padx=(0, 20))
        
        # Control buttons
        self.btn_hmi_verify_run = ttk.Button(toolbar, text="Verify HMI", 
                                            style="Accent.TButton", 
                                            command=self._on_run_hmi_verification)
        self.btn_hmi_verify_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_hmi_verify_export_json = ttk.Button(toolbar, text="Export JSON", 
                                                    command=self._on_export_hmi_verify_json)
        self.btn_hmi_verify_export_json.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_hmi_verify_export_json.configure(state=tk.DISABLED)
        
        self.btn_hmi_verify_export_csv = ttk.Button(toolbar, text="Export CSV", 
                                                   command=self._on_export_hmi_verify_csv)
        self.btn_hmi_verify_export_csv.pack(side=tk.LEFT, padx=6, pady=6)
        self.btn_hmi_verify_export_csv.configure(state=tk.DISABLED)
        
        # Results display
        self.hmi_verify_text, self.hmi_verify_logger = self._make_text_panel(tab)
        self.hmi_verify_results = []
    
    def _build_faults_tab(self):
        """Build faults/warnings tab (keeping original functionality)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Faults & Warnings")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Faults & Warnings", "Load DOCX mapping and scan PLC for active faults")
        
        # PLC IP input
        ttk.Label(toolbar, text="PLC IP:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_faults_ip = ttk.Entry(toolbar, width=24)
        self.entry_faults_ip.insert(0, config.plc.default_ip)
        self.entry_faults_ip.pack(side=tk.LEFT, padx=(0, 12))
        
        # Control buttons
        self.btn_faults_load = ttk.Button(toolbar, text="Load DOCX", 
                                         command=self._on_load_faults_docx)
        self.btn_faults_load.pack(side=tk.LEFT, padx=6, pady=6)
        
        self.btn_faults_scan = ttk.Button(toolbar, text="Scan PLC", 
                                         style="Accent.TButton", 
                                         command=self._on_run_faults_scan)
        self.btn_faults_scan.pack(side=tk.LEFT, padx=6, pady=6)
        
        # Status label
        self.faults_status_var = tk.StringVar(value="No mapping loaded")
        ttk.Label(toolbar, textvariable=self.faults_status_var, 
                 foreground=SUBTEXT).pack(side=tk.LEFT, padx=10)
        
        # Results display
        self.faults_text, self.faults_logger = self._make_text_panel(tab)
        self.fault_entries = []
        self.fault_docx_path = None
    
    def _build_settings_tab(self):
        """Build settings tab for configuration"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Settings", "Configure application preferences")
        
        # Settings content
        settings_frame = ttk.Frame(tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Network settings
        network_group = ttk.LabelFrame(settings_frame, text="Network Settings", padding=10)
        network_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(network_group, text="Default Probes:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.entry_probes = ttk.Entry(network_group, width=10)
        self.entry_probes.insert(0, str(config.network.default_probes))
        self.entry_probes.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(network_group, text="Default Timeout (ms):").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.entry_timeout = ttk.Entry(network_group, width=10)
        self.entry_timeout.insert(0, str(config.network.default_timeout_ms))
        self.entry_timeout.grid(row=0, column=3, sticky=tk.W)
        
        # PLC settings
        plc_group = ttk.LabelFrame(settings_frame, text="PLC Settings", padding=10)
        plc_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(plc_group, text="Default IP:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.entry_plc_default = ttk.Entry(plc_group, width=20)
        self.entry_plc_default.insert(0, config.plc.default_ip)
        self.entry_plc_default.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(plc_group, text="Connection Timeout:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        self.entry_plc_timeout = ttk.Entry(plc_group, width=10)
        self.entry_plc_timeout.insert(0, str(config.plc.connection_timeout))
        self.entry_plc_timeout.grid(row=0, column=3, sticky=tk.W)
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", 
                  style="Accent.TButton", 
                  command=self._on_save_settings).pack(pady=20)
    
    def _build_toolbar(self, parent, title, subtitle=""):
        """Build a toolbar with title and subtitle"""
        bar = ttk.Frame(parent)
        bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        ttk.Separator(bar).pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))
        
        title_row = ttk.Frame(bar)
        title_row.pack(fill=tk.X, pady=(8, 6))
        
        ttk.Label(title_row, text=title, font=("Segoe UI Semibold", 12)).pack(side=tk.LEFT)
        if subtitle:
            ttk.Label(title_row, text=subtitle, foreground=SUBTEXT).pack(side=tk.LEFT, padx=10)
        
        return bar
    
    def _make_text_panel(self, parent):
        """Create a scrollable text area with logger"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = tk.Text(frame, wrap="word", font=MONO, bg="#0b1118", fg=TEXT,
                      insertbackground=TEXT, relief="flat", padx=10, pady=10)
        
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview, 
                              style="Vertical.TScrollbar")
        text.configure(yscrollcommand=scroll.set)
        
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        
        logger = get_logger(f"GUI_{parent.winfo_name()}", text)
        return text, logger
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-n>', lambda e: self.notebook.select(0))  # Network tab
        self.bind('<Control-p>', lambda e: self.notebook.select(1))  # PLC tab
        self.bind('<Control-c>', lambda e: self.notebook.select(2))  # Cognex tab
        self.bind('<Control-v>', lambda e: self.notebook.select(3))  # PLC Verification tab
        self.bind('<Control-h>', lambda e: self.notebook.select(4))  # HMI Verification tab
        self.bind('<Control-f>', lambda e: self.notebook.select(5))  # Faults tab
        self.bind('<Control-s>', lambda e: self.notebook.select(6))  # Settings tab
        self.bind('<F5>', lambda e: self._refresh_current_tab())
    
    def _refresh_current_tab(self):
        """Refresh the currently selected tab"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:  # Network tab
            self._on_run_network_validation()
        elif current_tab == 1:  # PLC tab
            self._on_run_plc_validation()
        elif current_tab == 2:  # Cognex tab
            self._on_run_cognex_validation()
        elif current_tab == 3:  # PLC Verification tab
            self._on_run_plc_verification()
        elif current_tab == 4:  # HMI Verification tab
            self._on_run_hmi_verification()
    
    def _run_in_thread(self, button, target, *args, **kwargs):
        """Run function in background thread with button state management"""
        button.configure(state=tk.DISABLED)
        
        def worker():
            try:
                target(*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Thread error: {e}")
            finally:
                self.after(0, lambda: button.configure(state=tk.NORMAL))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _show_confirmation_dialog(self, title: str, message: str, operation: str = "operation") -> bool:
        """Show confirmation dialog before running operations"""
        result = messagebox.askyesno(
            title=title,
            message=f"{message}\n\nDo you want to proceed with this {operation}?",
            icon='question'
        )
        return result
    
    # Event handlers
    def _on_run_network_validation(self):
        """Run enhanced network validation"""
        self.network_text.delete("1.0", tk.END)
        self.network_progress.start()
        self.btn_network_export.configure(state=tk.DISABLED)
        
        def run_validation():
            try:
                self.logger.info("Starting enhanced network validation")
                self.network_validator = NetworkValidator(self.network_logger)
                results = self.network_validator.validate_devices_concurrent(PROGRAM1_DEVICES)
                self.network_results = results
                
                report = self.network_validator.generate_report(results)
                self.network_text.insert(tk.END, report)
                
                self.after(0, lambda: self.btn_network_export.configure(state=tk.NORMAL))
                self.after(0, lambda: self.network_progress.stop())
                
            except Exception as e:
                self.logger.error(f"Network validation error: {e}")
                self.network_text.insert(tk.END, f"Error: {e}\n")
                self.after(0, lambda: self.network_progress.stop())
        
        self._run_in_thread(self.btn_network_run, run_validation)
    
    def _on_export_network_results(self):
        """Export network validation results to CSV"""
        if not self.network_results or not self.network_validator:
            messagebox.showwarning("No Data", "No network validation results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Network Validation Results"
        )
        
        if filename:
            try:
                self.network_validator.export_results_csv(self.network_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_run_plc_validation(self):
        """Run enhanced PLC validation"""
        self.plc_text.delete("1.0", tk.END)
        ip = self.entry_plc_ip.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        def run_validation():
            try:
                self.logger.info(f"Starting PLC validation for {ip}")
                self.plc_validator = EnhancedPLCValidator(ip, self.plc_logger)
                report = self.plc_validator.generate_comprehensive_report()
                self.plc_text.insert(tk.END, report)
                self.after(0, lambda: self.btn_plc_export.configure(state=tk.NORMAL))
                
            except Exception as e:
                self.logger.error(f"PLC validation error: {e}")
                self.plc_text.insert(tk.END, f"Error: {e}\n")
            finally:
                if self.plc_validator:
                    self.plc_validator.close()
        
        self._run_in_thread(self.btn_plc_run, run_validation)
    
    def _on_diagnose_plc_connection(self):
        """Diagnose PLC connection issues"""
        self.plc_text.delete("1.0", tk.END)
        ip = self.entry_plc_ip.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        def run_diagnosis():
            try:
                self.logger.info(f"Starting PLC connection diagnosis for {ip}")
                self.plc_text.insert(tk.END, f"PLC Connection Diagnosis for {ip}\n")
                self.plc_text.insert(tk.END, "=" * 50 + "\n\n")
                
                # Test 1: Basic ping
                self.plc_text.insert(tk.END, "1. Testing basic network connectivity...\n")
                import subprocess
                import platform
                
                is_windows = platform.system().lower() == "windows"
                if is_windows:
                    cmd = ["ping", "-n", "3", "-w", "3000", ip]
                else:
                    cmd = ["ping", "-c", "3", "-W", "3", ip]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    self.plc_text.insert(tk.END, "   ✓ Ping successful\n")
                    self.plc_text.insert(tk.END, f"   Response: {result.stdout.split('time=')[-1].split()[0] if 'time=' in result.stdout else 'OK'}\n")
                else:
                    self.plc_text.insert(tk.END, "   ✗ Ping failed\n")
                    self.plc_text.insert(tk.END, f"   Error: {result.stderr}\n")
                
                # Test 2: EtherNet/IP port test
                self.plc_text.insert(tk.END, "\n2. Testing EtherNet/IP port (44818)...\n")
                import socket
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((ip, 44818))
                    sock.close()
                    
                    if result == 0:
                        self.plc_text.insert(tk.END, "   ✓ EtherNet/IP port is accessible\n")
                    else:
                        self.plc_text.insert(tk.END, f"   ✗ EtherNet/IP port not accessible (error: {result})\n")
                except Exception as e:
                    self.plc_text.insert(tk.END, f"   ✗ Port test failed: {e}\n")
                
                # Test 3: pylogix availability
                self.plc_text.insert(tk.END, "\n3. Checking pylogix library...\n")
                if PYLOGIX_AVAILABLE:
                    self.plc_text.insert(tk.END, "   ✓ pylogix is available\n")
                    
                    # Test 4: Basic pylogix connection
                    self.plc_text.insert(tk.END, "\n4. Testing pylogix connection...\n")
                    try:
                        from pylogix import PLC
                        with PLC() as comm:
                            comm.IPAddress = ip
                            comm.SocketTimeout = 5
                            
                            # Try to read a simple tag
                            result = comm.Read("Program:MainProgram.g_Par")
                            if result.Status == "Success":
                                self.plc_text.insert(tk.END, "   ✓ pylogix connection successful\n")
                                self.plc_text.insert(tk.END, f"   Tag value: {result.Value}\n")
                            else:
                                self.plc_text.insert(tk.END, f"   ✗ pylogix connection failed: {result.Status}\n")
                                if hasattr(result, 'StatusExtended'):
                                    self.plc_text.insert(tk.END, f"   Extended status: {result.StatusExtended}\n")
                    except Exception as e:
                        self.plc_text.insert(tk.END, f"   ✗ pylogix connection error: {e}\n")
                else:
                    self.plc_text.insert(tk.END, "   ✗ pylogix is not installed\n")
                    self.plc_text.insert(tk.END, "   Install with: pip install pylogix\n")
                
                # Summary and recommendations
                self.plc_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.plc_text.insert(tk.END, "DIAGNOSIS SUMMARY:\n")
                self.plc_text.insert(tk.END, "=" * 50 + "\n")
                self.plc_text.insert(tk.END, "If connection failed, check:\n")
                self.plc_text.insert(tk.END, "1. PLC is powered on and running\n")
                self.plc_text.insert(tk.END, "2. PLC IP address is correct\n")
                self.plc_text.insert(tk.END, "3. Network cable is connected\n")
                self.plc_text.insert(tk.END, "4. No firewall blocking EtherNet/IP (port 44818)\n")
                self.plc_text.insert(tk.END, "5. PLC is in RUN mode (not PROGRAM mode)\n")
                self.plc_text.insert(tk.END, "6. PLC has the correct program loaded\n")
                self.plc_text.insert(tk.END, "7. Your computer is on the same network as the PLC\n")
                
            except Exception as e:
                self.logger.error(f"PLC diagnosis error: {e}")
                self.plc_text.insert(tk.END, f"Diagnosis error: {e}\n")
        
        self._run_in_thread(self.btn_plc_diagnose, run_diagnosis)
    
    def _on_test_plc_ip(self):
        """Quick test of PLC IP connectivity"""
        ip = self.entry_plc_ip.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        def test_ip():
            try:
                import subprocess
                import platform
                
                is_windows = platform.system().lower() == "windows"
                if is_windows:
                    cmd = ["ping", "-n", "1", "-w", "3000", ip]
                else:
                    cmd = ["ping", "-c", "1", "-W", "3", ip]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    messagebox.showinfo("IP Test", f"✓ IP {ip} is reachable\n\nPing successful!")
                else:
                    messagebox.showerror("IP Test", f"✗ IP {ip} is not reachable\n\nPing failed.\n\nCheck:\n- PLC is powered on\n- Network cable connected\n- IP address is correct")
                    
            except Exception as e:
                messagebox.showerror("IP Test Error", f"Error testing IP {ip}:\n{e}")
        
        self._run_in_thread(self.btn_plc_diagnose, test_ip)
    
    def _on_test_individual_tags(self):
        """Test individual PLC tags for debugging"""
        self.plc_text.delete("1.0", tk.END)
        ip = self.entry_plc_ip.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        def test_tags():
            try:
                self.logger.info(f"Testing individual tags for {ip}")
                self.plc_text.insert(tk.END, f"Testing Individual PLC Tags for {ip}\n")
                self.plc_text.insert(tk.END, "=" * 50 + "\n\n")
                
                self.plc_validator = EnhancedPLCValidator(ip, self.plc_logger)
                
                # Test all the tags from the original script
                all_tags = [
                    'g_Par', 'g_Par1', 'g_ParNew', 'g_parTemp',
                    'Program:SafetyProgram.SafetyIO.In.ESTOP_Relay1Feedback',
                    'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelA',
                    'Program:SafetyProgram.SDIN_MachineBackLeftESTOP.ChannelB',
                    'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelA',
                    'Program:SafetyProgram.SDIN_MachineBackRightESTOP.ChannelB',
                    'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelA',
                    'Program:SafetyProgram.SDIN_MachineFrontESTOP.ChannelB',
                    'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelA',
                    'Program:SafetyProgram.SDIN_MainEnclosureESTOP.ChannelB',
                    'IO.PLC.In.DownstreamConveyorEnabled',
                    'H1_PACK_WMS_Connected',
                    'H2_SLAM1_WMS_Connected',
                    'NTP_Connected'
                ]
                
                results = self.plc_validator.test_individual_tags(all_tags)
                
                # Display results
                successful = []
                failed = []
                
                for tag, result in results.items():
                    if result.status == "Success":
                        successful.append(f"✓ {tag}: {result.value}")
                    else:
                        failed.append(f"✗ {tag}: {result.status}")
                
                self.plc_text.insert(tk.END, f"RESULTS SUMMARY:\n")
                self.plc_text.insert(tk.END, f"Total tags tested: {len(all_tags)}\n")
                self.plc_text.insert(tk.END, f"Successful: {len(successful)}\n")
                self.plc_text.insert(tk.END, f"Failed: {len(failed)}\n\n")
                
                if successful:
                    self.plc_text.insert(tk.END, "SUCCESSFUL TAGS:\n")
                    for result in successful:
                        self.plc_text.insert(tk.END, f"  {result}\n")
                    self.plc_text.insert(tk.END, "\n")
                
                if failed:
                    self.plc_text.insert(tk.END, "FAILED TAGS:\n")
                    for result in failed:
                        self.plc_text.insert(tk.END, f"  {result}\n")
                
                self.plc_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.plc_text.insert(tk.END, "Individual tag testing complete.\n")
                
            except Exception as e:
                self.logger.error(f"Individual tag testing error: {e}")
                self.plc_text.insert(tk.END, f"Error: {e}\n")
            finally:
                if hasattr(self, 'plc_validator') and self.plc_validator:
                    self.plc_validator.close()
        
        self._run_in_thread(self.btn_plc_test_tags, test_tags)
    
    def _on_export_plc_report(self):
        """Export PLC report to file"""
        if not self.plc_text.get("1.0", tk.END).strip():
            messagebox.showwarning("No Data", "No PLC report to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save PLC Report"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.plc_text.get("1.0", tk.END))
                messagebox.showinfo("Export Complete", f"Report saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save report:\n{e}")
    
    def _on_run_cognex_validation(self):
        """Run enhanced Cognex validation with CFG file comparison"""
        if not self._show_confirmation_dialog(
            "Cognex Validation",
            "This will backup current configurations and upload new ones if they differ.\nThis may cause temporary disruption to vision systems.",
            "Cognex validation"
        ):
            return
        
        self.cognex_text.delete("1.0", tk.END)
        self.btn_cognex_export_json.configure(state=tk.DISABLED)
        self.btn_cognex_export_csv.configure(state=tk.DISABLED)
        
        def run_validation():
            try:
                self.logger.info("Starting enhanced Cognex validation")
                self.cognex_validator = CognexValidator(self.cognex_logger)
                
                # Update device configurations with user-selected files
                for device, var in zip(self.cognex_devices, self.cognex_path_vars):
                    device.cfg_file = var.get().strip()
                
                results = self.cognex_validator.validate_devices(self.cognex_devices, upload_if_different=True)
                self.cognex_results = results
                
                report = self.cognex_validator.generate_report(results)
                self.cognex_text.insert(tk.END, report)
                
                self.after(0, lambda: self.btn_cognex_export_json.configure(state=tk.NORMAL))
                self.after(0, lambda: self.btn_cognex_export_csv.configure(state=tk.NORMAL))
                
            except Exception as e:
                self.logger.error(f"Cognex validation error: {e}")
                self.cognex_text.insert(tk.END, f"Error: {e}\n")
        
        self._run_in_thread(self.btn_cognex_run, run_validation)
    
    def _on_export_cognex_json(self):
        """Export Cognex results to JSON"""
        if not self.cognex_results:
            messagebox.showwarning("No Data", "No Cognex validation results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Cognex Validation Results (JSON)"
        )
        
        if filename:
            try:
                self.cognex_validator.export_results_json(self.cognex_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_export_cognex_csv(self):
        """Export Cognex results to CSV"""
        if not self.cognex_results:
            messagebox.showwarning("No Data", "No Cognex validation results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Cognex Validation Results (CSV)"
        )
        
        if filename:
            try:
                self.cognex_validator.export_results_csv(self.cognex_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_run_plc_verification(self):
        """Run PLC verification"""
        if not self._show_confirmation_dialog(
            "PLC Verification",
            "This will connect to the PLC and read project information including version, checksum, and timestamps.",
            "PLC verification"
        ):
            return
        
        self.plc_verify_text.delete("1.0", tk.END)
        ip = self.entry_plc_verify_ip.get().strip()
        expected_project = self.entry_plc_expected_project.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        try:
            expected_major = int(self.entry_plc_expected_major.get() or "0")
            expected_minor = int(self.entry_plc_expected_minor.get() or "0")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid version numbers")
            return
        
        def run_verification():
            try:
                self.logger.info(f"Starting PLC verification for {ip}")
                self.plc_verifier = PLCVerifier(self.plc_verify_logger)
                
                result = self.plc_verifier.verify_plc(
                    ip_address=ip,
                    expected_project_name=expected_project,
                    expected_major_revision=expected_major,
                    expected_minor_revision=expected_minor
                )
                
                self.plc_verify_results = [result]
                report = self.plc_verifier.generate_report(self.plc_verify_results)
                self.plc_verify_text.insert(tk.END, report)
                
                self.after(0, lambda: self.btn_plc_verify_export_json.configure(state=tk.NORMAL))
                self.after(0, lambda: self.btn_plc_verify_export_csv.configure(state=tk.NORMAL))
                
            except Exception as e:
                self.logger.error(f"PLC verification error: {e}")
                self.plc_verify_text.insert(tk.END, f"Error: {e}\n")
        
        self._run_in_thread(self.btn_plc_verify_run, run_verification)
    
    def _on_export_plc_verify_json(self):
        """Export PLC verification results to JSON"""
        if not self.plc_verify_results:
            messagebox.showwarning("No Data", "No PLC verification results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save PLC Verification Results (JSON)"
        )
        
        if filename:
            try:
                self.plc_verifier.export_results_json(self.plc_verify_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_export_plc_verify_csv(self):
        """Export PLC verification results to CSV"""
        if not self.plc_verify_results:
            messagebox.showwarning("No Data", "No PLC verification results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save PLC Verification Results (CSV)"
        )
        
        if filename:
            try:
                self.plc_verifier.export_results_csv(self.plc_verify_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_run_hmi_verification(self):
        """Run HMI verification"""
        if not self._show_confirmation_dialog(
            "HMI Verification",
            "This will connect to the HMI and check runtime application information.",
            "HMI verification"
        ):
            return
        
        self.hmi_verify_text.delete("1.0", tk.END)
        ip = self.entry_hmi_verify_ip.get().strip()
        expected_app = self.entry_hmi_expected_app.get().strip()
        expected_version = self.entry_hmi_expected_version.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter an HMI IP address")
            return
        
        try:
            port = int(self.entry_hmi_verify_port.get() or "2222")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
            return
        
        def run_verification():
            try:
                self.logger.info(f"Starting HMI verification for {ip}:{port}")
                self.hmi_verifier = HMIVerifier(self.hmi_verify_logger)
                
                result = self.hmi_verifier.verify_hmi(
                    ip_address=ip,
                    port=port,
                    expected_app_name=expected_app,
                    expected_version=expected_version
                )
                
                self.hmi_verify_results = [result]
                report = self.hmi_verifier.generate_report(self.hmi_verify_results)
                self.hmi_verify_text.insert(tk.END, report)
                
                self.after(0, lambda: self.btn_hmi_verify_export_json.configure(state=tk.NORMAL))
                self.after(0, lambda: self.btn_hmi_verify_export_csv.configure(state=tk.NORMAL))
                
            except Exception as e:
                self.logger.error(f"HMI verification error: {e}")
                self.hmi_verify_text.insert(tk.END, f"Error: {e}\n")
        
        self._run_in_thread(self.btn_hmi_verify_run, run_verification)
    
    def _on_export_hmi_verify_json(self):
        """Export HMI verification results to JSON"""
        if not self.hmi_verify_results:
            messagebox.showwarning("No Data", "No HMI verification results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save HMI Verification Results (JSON)"
        )
        
        if filename:
            try:
                self.hmi_verifier.export_results_json(self.hmi_verify_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_export_hmi_verify_csv(self):
        """Export HMI verification results to CSV"""
        if not self.hmi_verify_results:
            messagebox.showwarning("No Data", "No HMI verification results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save HMI Verification Results (CSV)"
        )
        
        if filename:
            try:
                self.hmi_verifier.export_results_csv(self.hmi_verify_results, filename)
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results:\n{e}")
    
    def _on_load_faults_docx(self):
        """Load faults DOCX file (placeholder - would integrate original functionality)"""
        self.faults_text.delete("1.0", tk.END)
        self.faults_text.insert(tk.END, "Faults DOCX loading functionality would be integrated here.\n")
    
    def _on_run_faults_scan(self):
        """Run faults scan (placeholder - would integrate original functionality)"""
        self.faults_text.delete("1.0", tk.END)
        self.faults_text.insert(tk.END, "Faults scanning functionality would be integrated here.\n")
    
    def _on_save_settings(self):
        """Save application settings"""
        try:
            # Update network settings
            config.network.default_probes = int(self.entry_probes.get())
            config.network.default_timeout_ms = int(self.entry_timeout.get())
            
            # Update PLC settings
            config.plc.default_ip = self.entry_plc_default.get()
            config.plc.connection_timeout = float(self.entry_plc_timeout.get())
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully")
            self.logger.info("Settings saved successfully")
            
        except ValueError as e:
            messagebox.showerror("Invalid Settings", f"Please check your input values:\n{e}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings:\n{e}")

def main():
    """Main application entry point"""
    try:
        app = EnhancedApp()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()