"""
SPP All-In-One Toolkit - Simplified Standalone Version
Industrial automation toolkit with enhanced features
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import re
import platform
import subprocess
import ipaddress
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional dependencies
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

# Dark theme colors
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
    "11.200.1.31": "AL1422 IO Link",
    "11.200.1.35": "Keyence IV4 Sensor",
}

class SimpleLogger:
    """Simple logger for GUI output"""
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
    
    def info(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_widget.insert(tk.END, f"{timestamp} - INFO - {message}\n")
        self.text_widget.see(tk.END)
        self.text_widget.update()
    
    def warning(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_widget.insert(tk.END, f"{timestamp} - WARNING - {message}\n")
        self.text_widget.see(tk.END)
        self.text_widget.update()
    
    def error(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_widget.insert(tk.END, f"{timestamp} - ERROR - {message}\n")
        self.text_widget.see(tk.END)
        self.text_widget.update()

class NetworkValidator:
    """Enhanced network validation with concurrent testing"""
    
    def __init__(self, logger: SimpleLogger):
        self.logger = logger
        self.results = []
    
    def _run_ping_blocking(self, ip: str, probes: int, timeout_ms: int) -> tuple:
        """Run ping command and return (reply_count, avg_response_time)"""
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
                m = re.search(r"Reply from ([0-9.]+):", line, flags=re.IGNORECASE)
                if m and m.group(1) == ip and "Destination host unreachable" not in line:
                    hits += 1
                
                time_match = re.search(r"time[<=](\d+)ms", line, flags=re.IGNORECASE)
                if time_match:
                    response_times.append(float(time_match.group(1)))
        else:
            for line in out.splitlines():
                m = re.search(r"bytes from\s+([0-9.]+)", line, flags=re.IGNORECASE)
                if m and m.group(1) == ip:
                    hits += 1
                
                time_match = re.search(r"time=(\d+\.?\d*)", line)
                if time_match:
                    response_times.append(float(time_match.group(1)))
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        return hits, avg_response_time
    
    def ping_device(self, ip: str, name: str, retries: int = 2, 
                   probes: int = 3, require: int = 1, timeout_ms: int = 700) -> dict:
        """Enhanced ping with better error handling"""
        result = {
            'ip': ip,
            'name': name,
            'status': 'Unknown',
            'response_time': None,
            'error_message': None,
            'attempts': 0
        }
        
        # ARP warm-up
        try:
            _ = self._run_ping_blocking(ip, probes=1, timeout_ms=timeout_ms)
        except Exception:
            pass
        time.sleep(0.08)
        
        for attempt in range(1, retries + 1):
            result['attempts'] = attempt
            self.logger.info(f"Attempt {attempt}: Pinging {name} ({ip})")
            
            try:
                hits, avg_response_time = self._run_ping_blocking(ip, probes, timeout_ms)
                result['response_time'] = avg_response_time
                
                if hits >= require:
                    result['status'] = 'Reachable'
                    self.logger.info(f"✓ {name} ({ip}) - SUCCESS")
                    return result
                else:
                    result['status'] = 'Unreachable'
                    result['error_message'] = f"Only {hits}/{probes} replies received"
                    
            except Exception as e:
                result['status'] = 'Error'
                result['error_message'] = str(e)
                self.logger.warning(f"✗ {name} ({ip}) - Error: {e}")
            
            if attempt < retries:
                time.sleep(0.3)
        
        self.logger.warning(f"✗ {name} ({ip}) - FAILED after {retries} attempts")
        return result
    
    def validate_devices_concurrent(self, devices: Dict[str, str], max_workers: int = 5) -> List[dict]:
        """Validate multiple devices concurrently"""
        self.logger.info(f"Starting concurrent validation of {len(devices)} devices")
        self.results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_device = {
                executor.submit(self.ping_device, ip, name): (ip, name)
                for ip, name in devices.items()
            }
            
            completed = 0
            total = len(devices)
            
            for future in as_completed(future_to_device):
                ip, name = future_to_device[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    completed += 1
                    self.logger.info(f"Progress: {completed}/{total} ({completed/total*100:.1f}%)")
                except Exception as e:
                    self.logger.error(f"Exception validating {name} ({ip}): {e}")
                    self.results.append({
                        'ip': ip, 'name': name, 'status': 'Exception', 
                        'error_message': str(e), 'response_time': None, 'attempts': 0
                    })
                    completed += 1
        
        # Sort results by IP address
        self.results.sort(key=lambda x: ipaddress.ip_address(x['ip']))
        return self.results
    
    def generate_report(self, results: List[dict]) -> str:
        """Generate formatted report"""
        report_lines = []
        report_lines.append("\n" + "=" * 80)
        report_lines.append("SPP IP VALIDATION REPORT")
        report_lines.append("=" * 80)
        
        # Summary
        total = len(results)
        reachable = len([r for r in results if r['status'] == 'Reachable'])
        unreachable = len([r for r in results if r['status'] == 'Unreachable'])
        errors = len([r for r in results if r['status'] == 'Error'])
        
        report_lines.append(f"\nSUMMARY:")
        report_lines.append(f"  Total Devices: {total}")
        report_lines.append(f"  Reachable: {reachable}")
        report_lines.append(f"  Unreachable: {unreachable}")
        report_lines.append(f"  Errors: {errors}")
        report_lines.append(f"  Success Rate: {(reachable/total*100):.1f}%")
        
        # Detailed results
        report_lines.append(f"\nDETAILED RESULTS:")
        report_lines.append("-" * 100)
        report_lines.append(f"{'IP Address':<16} {'Device Description':<45} {'Status':<12} {'Response Time':<12} {'Attempts'}")
        report_lines.append("-" * 100)
        
        for result in results:
            response_time_str = f"{result['response_time']:.1f}ms" if result['response_time'] else "N/A"
            report_lines.append(
                f"{result['ip']:<16} {result['name']:<45} {result['status']:<12} {response_time_str:<12} {result['attempts']}"
            )
        
        # Error details
        error_results = [r for r in results if r['error_message']]
        if error_results:
            report_lines.append(f"\nERROR DETAILS:")
            for result in error_results:
                report_lines.append(f"  {result['name']} ({result['ip']}): {result['error_message']}")
        
        report_lines.append("=" * 80)
        report_lines.append("Validation complete.\n")
        
        return "\n".join(report_lines)
    
    def export_results_csv(self, results: List[dict], filename: str = None) -> str:
        """Export results to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_validation_{timestamp}.csv"
        
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['IP Address', 'Device Name', 'Status', 'Response Time (ms)', 'Attempts', 'Error Message'])
            
            for result in results:
                writer.writerow([
                    result['ip'],
                    result['name'],
                    result['status'],
                    result['response_time'] or '',
                    result['attempts'],
                    result['error_message'] or ''
                ])
        
        self.logger.info(f"Results exported to: {filename}")
        return filename

class SimpleApp(tk.Tk):
    """Simplified SPP Toolkit with enhanced features"""
    
    def __init__(self):
        super().__init__()
        self.title("SPP All-In-One Toolkit — Enhanced")
        self.geometry("1120x760")
        
        # Apply dark theme
        self.style = self._apply_dark_theme()
        
        # Initialize components
        self.network_validator = None
        self.network_results = []
        
        # Build UI
        self._build_header()
        self._build_notebook()
        self._build_tabs()
        
        self._bind_shortcuts()
    
    def _apply_dark_theme(self) -> ttk.Style:
        """Apply dark theme"""
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
        
        # Tab styles
        style.configure("TNotebook.Tab", 
                       background=SURFACE, 
                       foreground=SUBTEXT,
                       padding=(14, 8), 
                       borderwidth=0)
        style.map("TNotebook.Tab",
                 background=[("selected", RAISED)],
                 foreground=[("selected", TEXT)])
        
        # Button styles
        style.configure("TButton", 
                       background=SURFACE, 
                       foreground=TEXT,
                       borderwidth=1, 
                       padding=(12, 8))
        style.map("TButton",
                 background=[("active", RAISED)],
                 foreground=[("disabled", "#6b7280")])
        
        style.configure("Accent.TButton", 
                       background=ACCENT, 
                       foreground="#001018",
                       borderwidth=0, 
                       padding=(14, 9))
        style.map("Accent.TButton",
                 background=[("active", ACCENT_DIM), ("disabled", "#335561")],
                 foreground=[("disabled", "#122027")])
        
        # Other widgets
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
        """Build header with status indicators"""
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
        ttk.Label(title_row, text="Enhanced • Network • PLC • Cognex • Faults", 
                 foreground=SUBTEXT).pack(side=tk.LEFT, padx=12)
        
        # Status indicators
        status_frame = ttk.Frame(title_row)
        status_frame.pack(side=tk.RIGHT)
        
        pylogix_status = "✓" if PYLOGIX_AVAILABLE else "✗"
        docx_status = "✓" if DOCX_AVAILABLE else "✗"
        
        ttk.Label(status_frame, text=f"pylogix: {pylogix_status}", 
                 foreground=SUCCESS if PYLOGIX_AVAILABLE else ERROR).pack(side=tk.RIGHT, padx=5)
        ttk.Label(status_frame, text=f"docx: {docx_status}", 
                 foreground=SUCCESS if DOCX_AVAILABLE else ERROR).pack(side=tk.RIGHT, padx=5)
    
    def _build_notebook(self):
        """Build main notebook"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _build_tabs(self):
        """Build all tabs"""
        self._build_network_tab()
        self._build_plc_tab()
        self._build_cognex_tab()
        self._build_faults_tab()
    
    def _build_network_tab(self):
        """Build network validation tab"""
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
    
    def _build_plc_tab(self):
        """Build PLC validation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PLC Validation")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "PLC Validation", "Enhanced parameter reading with error recovery")
        
        # PLC IP input
        ttk.Label(toolbar, text="PLC IP:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_plc_ip = ttk.Entry(toolbar, width=24)
        self.entry_plc_ip.insert(0, "11.200.0.10")
        self.entry_plc_ip.pack(side=tk.LEFT, padx=(0, 10))
        
        # Control buttons
        self.btn_plc_run = ttk.Button(toolbar, text="Run Validation", 
                                     style="Accent.TButton", 
                                     command=self._on_run_plc_validation)
        self.btn_plc_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        # Results display
        self.plc_text, self.plc_logger = self._make_text_panel(tab)
    
    def _build_cognex_tab(self):
        """Build Cognex validation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Cognex Validation")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Cognex Validation", "Backup and upload configuration files")
        
        self.btn_cognex_run = ttk.Button(toolbar, text="Run Backup & Upload", 
                                        style="Accent.TButton", 
                                        command=self._on_run_cognex_validation)
        self.btn_cognex_run.pack(side=tk.LEFT, padx=6, pady=6)
        
        # Results display
        self.cognex_text, self.cognex_logger = self._make_text_panel(tab)
    
    def _build_faults_tab(self):
        """Build faults/warnings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Faults & Warnings")
        
        # Toolbar
        toolbar = self._build_toolbar(tab, "Faults & Warnings", "Load DOCX mapping and scan PLC for active faults")
        
        # PLC IP input
        ttk.Label(toolbar, text="PLC IP:").pack(side=tk.LEFT, padx=(0, 6))
        self.entry_faults_ip = ttk.Entry(toolbar, width=24)
        self.entry_faults_ip.insert(0, "11.200.0.10")
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
    
    def _build_toolbar(self, parent, title, subtitle=""):
        """Build toolbar with title and subtitle"""
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
        """Create scrollable text area with logger"""
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
        
        logger = SimpleLogger(text)
        return text, logger
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.bind('<Control-n>', lambda e: self.notebook.select(0))  # Network tab
        self.bind('<Control-p>', lambda e: self.notebook.select(1))  # PLC tab
        self.bind('<Control-c>', lambda e: self.notebook.select(2))  # Cognex tab
        self.bind('<Control-f>', lambda e: self.notebook.select(3))  # Faults tab
        self.bind('<F5>', lambda e: self._refresh_current_tab())
    
    def _refresh_current_tab(self):
        """Refresh current tab"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 0:  # Network tab
            self._on_run_network_validation()
        elif current_tab == 1:  # PLC tab
            self._on_run_plc_validation()
    
    def _run_in_thread(self, button, target, *args, **kwargs):
        """Run function in background thread"""
        button.configure(state=tk.DISABLED)
        
        def worker():
            try:
                target(*args, **kwargs)
            except Exception as e:
                print(f"Thread error: {e}")
            finally:
                self.after(0, lambda: button.configure(state=tk.NORMAL))
        
        threading.Thread(target=worker, daemon=True).start()
    
    # Event handlers
    def _on_run_network_validation(self):
        """Run network validation"""
        self.network_text.delete("1.0", tk.END)
        self.network_progress.start()
        self.btn_network_export.configure(state=tk.DISABLED)
        
        def run_validation():
            try:
                self.network_validator = NetworkValidator(self.network_logger)
                results = self.network_validator.validate_devices_concurrent(PROGRAM1_DEVICES)
                self.network_results = results
                
                report = self.network_validator.generate_report(results)
                self.network_text.insert(tk.END, report)
                
                self.after(0, lambda: self.btn_network_export.configure(state=tk.NORMAL))
                self.after(0, lambda: self.network_progress.stop())
                
            except Exception as e:
                self.network_logger.error(f"Network validation error: {e}")
                self.after(0, lambda: self.network_progress.stop())
        
        self._run_in_thread(self.btn_network_run, run_validation)
    
    def _on_export_network_results(self):
        """Export network results to CSV"""
        if not self.network_results:
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
        """Run PLC validation"""
        self.plc_text.delete("1.0", tk.END)
        ip = self.entry_plc_ip.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter a PLC IP address")
            return
        
        if not PYLOGIX_AVAILABLE:
            self.plc_text.insert(tk.END, "pylogix is not installed. Please run: pip install pylogix\n")
            return
        
        def run_validation():
            try:
                self.plc_logger.info(f"Starting PLC validation for {ip}")
                # Placeholder for PLC validation logic
                self.plc_text.insert(tk.END, f"PLC validation for {ip} would be implemented here.\n")
                self.plc_text.insert(tk.END, "This would include reading g_Par bits, safety status, etc.\n")
                
            except Exception as e:
                self.plc_logger.error(f"PLC validation error: {e}")
        
        self._run_in_thread(self.btn_plc_run, run_validation)
    
    def _on_run_cognex_validation(self):
        """Run Cognex validation"""
        self.cognex_text.delete("1.0", tk.END)
        self.cognex_text.insert(tk.END, "Cognex validation functionality would be integrated here.\n")
        self.cognex_text.insert(tk.END, "This would include the original backup and upload features.\n")
    
    def _on_load_faults_docx(self):
        """Load faults DOCX file"""
        self.faults_text.delete("1.0", tk.END)
        self.faults_text.insert(tk.END, "Faults DOCX loading functionality would be integrated here.\n")
    
    def _on_run_faults_scan(self):
        """Run faults scan"""
        self.faults_text.delete("1.0", tk.END)
        self.faults_text.insert(tk.END, "Faults scanning functionality would be integrated here.\n")

def main():
    """Main application entry point"""
    try:
        app = SimpleApp()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()