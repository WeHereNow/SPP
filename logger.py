"""
Enhanced logging system for SPP All-In-One Toolkit
"""
import logging
import sys
import queue
import threading
from datetime import datetime
from typing import Optional, TextIO, Dict

# Optional tkinter import for GUI functionality
try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    # Create dummy classes for when tkinter is not available
    class tk:
        class Text:
            pass
        class StringVar:
            pass
    class ttk:
        pass

class GuiLogHandler(logging.Handler):
    """Custom logging handler that sends messages to a GUI text widget"""
    
    def __init__(self, text_widget=None):
        super().__init__()
        if TKINTER_AVAILABLE and text_widget is not None:
            self.text_widget = text_widget
            self.q: queue.Queue[str] = queue.Queue()
            self._poll_queue()
        else:
            self.text_widget = None
            self.q = None
        
    def _poll_queue(self) -> None:
        """Periodically move messages from the queue into the Text widget"""
        try:
            for _ in range(100):  # Up to 100 messages per poll
                msg = self.q.get_nowait()
                self.text_widget.insert(tk.END, msg)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass
        self.text_widget.after(50, self._poll_queue)
    
    def emit(self, record):
        """Emit a log record to the GUI"""
        try:
            msg = self.format(record) + '\n'
            if self.q is not None:
                self.q.put(msg)
        except Exception:
            self.handleError(record)

class EnhancedLogger:
    """Enhanced logger with multiple outputs and formatting"""
    
    def __init__(self, name: str, gui_widget=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # GUI handler
        if gui_widget:
            gui_handler = GuiLogHandler(gui_widget)
            gui_handler.setLevel(logging.DEBUG)
            gui_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            gui_handler.setFormatter(gui_format)
            self.logger.addHandler(gui_handler)
        
        # File handler
        try:
            file_handler = logging.FileHandler(
                f'logs/spp_toolkit_{datetime.now().strftime("%Y%m%d")}.log',
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
        except Exception:
            pass  # Ignore file logging errors
    
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

class ProgressLogger:
    """Logger with progress indication capabilities"""
    
    def __init__(self, logger: EnhancedLogger, total_steps: int, description: str = ""):
        self.logger = logger
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = datetime.now()
        
        if description:
            self.logger.info(f"Starting: {description}")
    
    def step(self, message: str = ""):
        """Increment progress and log message"""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        elapsed = datetime.now() - self.start_time
        
        if message:
            self.logger.info(f"[{percentage:.1f}%] {message}")
        else:
            self.logger.info(f"Progress: {self.current_step}/{self.total_steps} ({percentage:.1f}%)")
    
    def complete(self, message: str = ""):
        """Mark progress as complete"""
        elapsed = datetime.now() - self.start_time
        if message:
            self.logger.info(f"Completed: {message} (took {elapsed.total_seconds():.2f}s)")
        else:
            self.logger.info(f"Progress complete (took {elapsed.total_seconds():.2f}s)")

# Global logger instances
loggers: Dict[str, EnhancedLogger] = {}

def get_logger(name: str, gui_widget=None) -> EnhancedLogger:
    """Get or create a logger instance"""
    if name not in loggers:
        loggers[name] = EnhancedLogger(name, gui_widget)
    return loggers[name]