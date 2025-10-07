"""
Configuration settings for SPP All-In-One Toolkit
"""
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class NetworkConfig:
    """Network validation configuration"""
    default_probes: int = 3
    default_retries: int = 2
    default_timeout_ms: int = 700
    require_min_replies: int = 1
    arp_warmup_delay: float = 0.08
    backoff_delay: float = 0.3

@dataclass
class PLCConfig:
    """PLC communication configuration"""
    default_ip: str = "11.200.0.10"
    connection_timeout: float = 5.0
    read_timeout: float = 10.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class CognexConfig:
    """Cognex device configuration"""
    telnet_port: int = 23
    connect_timeout: float = 5.0
    idle_read_timeout: float = 1.0
    overall_read_limit: float = 20.0
    max_backup_bytes: int = 50 * 1024**2
    sleep_between_commands: float = 0.2
    socket_timeout: float = 3.0

@dataclass
class EStopConfig:
    """E Stop monitoring configuration"""
    default_monitor_interval: float = 1.0
    change_detection_enabled: bool = True
    log_all_changes: bool = True
    max_history_size: int = 1000
    auto_start_monitoring: bool = False

@dataclass
class UIConfig:
    """User interface configuration"""
    window_size: str = "1120x760"
    window_title: str = "SPP All-In-One Toolkit — Enhanced"
    log_max_lines: int = 10000
    auto_scroll: bool = True
    theme: str = "dark"

@dataclass
class AppConfig:
    """Main application configuration"""
    network: NetworkConfig = field(default_factory=NetworkConfig)
    plc: PLCConfig = field(default_factory=PLCConfig)
    cognex: CognexConfig = field(default_factory=CognexConfig)
    estop: EStopConfig = field(default_factory=EStopConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    # File paths
    backup_dir: str = "backups"
    config_dir: str = "config"
    logs_dir: str = "logs"
    
    # Default files
    default_faults_docx: str = "faults321.docx"
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        for directory in [self.backup_dir, self.config_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

# Global configuration instance
config = AppConfig()