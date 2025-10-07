"""
Input Validation and Sanitization Module
Provides secure validation for all external inputs
"""
import ipaddress
import os
import re
from typing import Optional
from pathlib import Path


class InputValidator:
    """Centralized input validation and sanitization"""
    
    # Allowed Cognex DMCC commands (whitelist)
    ALLOWED_DMCC_COMMANDS = {
        'DEVICE.BACKUP',
        'CONFIG.LOAD',
        'CONFIG.SAVE', 
        'REBOOT',
        'BEEP'
    }
    
    # Allowed PLC tag patterns
    ALLOWED_TAG_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_\.\[\]:\-]*$')
    
    @staticmethod
    def validate_ip_address(ip: str) -> tuple[bool, str]:
        """
        Validate IP address format
        
        Args:
            ip: IP address string to validate
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not ip or not isinstance(ip, str):
            return False, "IP address cannot be empty"
        
        ip = ip.strip()
        
        try:
            # Validate IPv4 or IPv6
            ip_obj = ipaddress.ip_address(ip)
            
            # Check for private/reserved ranges if needed
            if ip_obj.is_loopback:
                return False, "Loopback addresses are not allowed"
            
            if ip_obj.is_multicast:
                return False, "Multicast addresses are not allowed"
            
            return True, ""
            
        except ValueError as e:
            return False, f"Invalid IP address format: {e}"
    
    @staticmethod
    def validate_port(port: int) -> tuple[bool, str]:
        """
        Validate port number
        
        Args:
            port: Port number to validate
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not isinstance(port, int):
            try:
                port = int(port)
            except (ValueError, TypeError):
                return False, "Port must be a number"
        
        if port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
        
        # Check for common privileged ports (optional warning)
        if port < 1024:
            return True, "Warning: Using privileged port"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = False, 
                          allowed_extensions: Optional[list] = None) -> tuple[bool, str]:
        """
        Validate file path for security issues
        
        Args:
            file_path: File path to validate
            must_exist: If True, file must exist
            allowed_extensions: List of allowed file extensions (e.g., ['.cfg', '.csv'])
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not file_path or not isinstance(file_path, str):
            return False, "File path cannot be empty"
        
        try:
            path = Path(file_path).resolve()
            
            # Check for path traversal attempts
            if '..' in file_path:
                return False, "Path traversal detected"
            
            # Check if file exists when required
            if must_exist and not path.exists():
                return False, f"File does not exist: {file_path}"
            
            # Validate file extension if specified
            if allowed_extensions:
                if not any(str(path).endswith(ext) for ext in allowed_extensions):
                    return False, f"File extension must be one of: {', '.join(allowed_extensions)}"
            
            # Check for symbolic links (security concern)
            if path.is_symlink():
                return False, "Symbolic links are not allowed"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid file path: {e}"
    
    @staticmethod
    def sanitize_dmcc_command(command: str) -> tuple[bool, str, str]:
        """
        Sanitize and validate Cognex DMCC commands
        
        Args:
            command: DMCC command to validate
            
        Returns:
            (is_valid, sanitized_command, error_message) tuple
        """
        if not command or not isinstance(command, str):
            return False, "", "Command cannot be empty"
        
        command = command.strip().upper()
        
        # Extract base command (before any parameters)
        base_command = command.split()[0] if ' ' in command else command
        base_command = base_command.replace('||>', '').strip()
        
        # Check against whitelist
        if base_command not in InputValidator.ALLOWED_DMCC_COMMANDS:
            return False, "", f"Command not allowed: {base_command}"
        
        # Additional validation for CONFIG.LOAD (has size parameter)
        if base_command == 'CONFIG.LOAD':
            if ' ' not in command:
                return False, "", "CONFIG.LOAD requires size parameter"
            try:
                parts = command.split()
                size = int(parts[1])
                if size < 0 or size > 50 * 1024 * 1024:  # 50MB limit
                    return False, "", "CONFIG.LOAD size must be between 0 and 50MB"
            except (IndexError, ValueError):
                return False, "", "CONFIG.LOAD size parameter invalid"
        
        # Additional validation for BEEP (has parameters)
        if base_command == 'BEEP':
            if ' ' in command:
                # BEEP can have parameters like "3,2"
                parts = command.split(None, 1)
                if len(parts) > 1:
                    param = parts[1].replace(',', '').replace(' ', '')
                    if not param.isdigit():
                        return False, "", "BEEP parameters must be numeric"
        
        return True, command, ""
    
    @staticmethod
    def validate_plc_tag(tag: str) -> tuple[bool, str]:
        """
        Validate PLC tag name
        
        Args:
            tag: PLC tag name to validate
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not tag or not isinstance(tag, str):
            return False, "Tag name cannot be empty"
        
        tag = tag.strip()
        
        # Check length
        if len(tag) > 200:
            return False, "Tag name too long (max 200 characters)"
        
        # Check pattern (alphanumeric, underscores, dots, brackets, colons, hyphens)
        if not InputValidator.ALLOWED_TAG_PATTERN.match(tag):
            return False, "Invalid tag name format"
        
        # Check for injection attempts
        dangerous_chars = [';', '|', '&', '$', '`', '\n', '\r']
        if any(char in tag for char in dangerous_chars):
            return False, "Tag name contains dangerous characters"
        
        return True, ""
    
    @staticmethod
    def validate_timeout(timeout: float, min_val: float = 0.1, 
                        max_val: float = 300.0) -> tuple[bool, str]:
        """
        Validate timeout value
        
        Args:
            timeout: Timeout value in seconds
            min_val: Minimum allowed timeout
            max_val: Maximum allowed timeout
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            timeout = float(timeout)
        except (ValueError, TypeError):
            return False, "Timeout must be a number"
        
        if timeout < min_val or timeout > max_val:
            return False, f"Timeout must be between {min_val} and {max_val} seconds"
        
        return True, ""
    
    @staticmethod
    def validate_interval(interval: float, min_val: float = 0.1, 
                         max_val: float = 60.0) -> tuple[bool, str]:
        """
        Validate monitoring interval value
        
        Args:
            interval: Interval value in seconds
            min_val: Minimum allowed interval
            max_val: Maximum allowed interval
            
        Returns:
            (is_valid, error_message) tuple
        """
        try:
            interval = float(interval)
        except (ValueError, TypeError):
            return False, "Interval must be a number"
        
        if interval < min_val or interval > max_val:
            return False, f"Interval must be between {min_val} and {max_val} seconds"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to remove dangerous characters
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove path separators
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
