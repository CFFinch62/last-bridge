"""
com0com Manager Module

This module provides an interface to the com0com virtual serial port driver.
It handles detection, configuration, and management of virtual port pairs.

Key Features:
- Detect com0com installation
- Locate setupc.exe utility
- Create/remove virtual port pairs
- List existing port pairs
- Configure port parameters (baud rate emulation, overrun, etc.)

Author: BRIDGE-WIN Development Team
License: GPL (matching com0com license)
"""

import os
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import winreg

from utils.logger import get_logger

logger = get_logger(__name__)


class Com0comManager:
    """Manager class for com0com virtual serial port driver operations."""
    
    def __init__(self):
        """Initialize the com0com manager."""
        self.setupc_path: Optional[Path] = None
        self.is_installed: bool = False
        self._detect_installation()
    
    def _detect_installation(self) -> None:
        """
        Detect if com0com is installed and locate setupc.exe.
        
        Checks:
        1. Registry for installation path
        2. Common installation directories
        3. PATH environment variable
        """
        logger.info("Detecting com0com installation...")
        
        # Method 1: Check registry
        setupc_path = self._find_setupc_in_registry()
        if setupc_path:
            self.setupc_path = setupc_path
            self.is_installed = True
            logger.info(f"com0com found via registry: {setupc_path}")
            return
        
        # Method 2: Check common installation directories
        common_paths = [
            Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'com0com',
            Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')) / 'com0com',
            Path('C:\\Program Files\\com0com'),
            Path('C:\\Program Files (x86)\\com0com'),
        ]
        
        for path in common_paths:
            setupc = path / 'setupc.exe'
            if setupc.exists():
                self.setupc_path = setupc
                self.is_installed = True
                logger.info(f"com0com found in common path: {setupc}")
                return
        
        # Method 3: Check PATH environment variable
        setupc_path = self._find_setupc_in_path()
        if setupc_path:
            self.setupc_path = setupc_path
            self.is_installed = True
            logger.info(f"com0com found in PATH: {setupc_path}")
            return
        
        logger.warning("com0com not detected on this system")
        self.is_installed = False
    
    def _find_setupc_in_registry(self) -> Optional[Path]:
        """Find setupc.exe path from Windows registry."""
        try:
            # Try to find com0com installation path in registry
            key_paths = [
                r"SOFTWARE\com0com",
                r"SOFTWARE\WOW6432Node\com0com",
            ]
            
            for key_path in key_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                        setupc = Path(install_dir) / 'setupc.exe'
                        if setupc.exists():
                            return setupc
                except FileNotFoundError:
                    continue
        except Exception as e:
            logger.debug(f"Registry search failed: {e}")
        
        return None
    
    def _find_setupc_in_path(self) -> Optional[Path]:
        """Find setupc.exe in PATH environment variable."""
        try:
            result = subprocess.run(
                ['where', 'setupc.exe'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                return Path(path)
        except Exception as e:
            logger.debug(f"PATH search failed: {e}")
        
        return None
    
    def _run_setupc(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """
        Run setupc.exe with given arguments.
        
        Args:
            args: List of command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.is_installed:
            raise RuntimeError("com0com is not installed")
        
        cmd = [str(self.setupc_path)] + args
        logger.debug(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout after {timeout}s: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Command failed: {e}")
            raise
    
    def list_port_pairs(self) -> List[Dict[str, str]]:
        """
        List all existing com0com port pairs.
        
        Returns:
            List of dictionaries with port pair information.
            Each dict contains: 'port_a', 'port_b', 'params_a', 'params_b'
        """
        if not self.is_installed:
            logger.warning("Cannot list ports: com0com not installed")
            return []
        
        returncode, stdout, stderr = self._run_setupc(['list'])
        
        if returncode != 0:
            logger.error(f"Failed to list ports: {stderr}")
            return []
        
        # Parse output
        # Format: "CNCA0 PortName=COM8,EmuBR=yes"
        #         "CNCB0 PortName=COM9"
        pairs = []
        lines = stdout.strip().split('\n')
        
        for i in range(0, len(lines), 2):
            if i + 1 < len(lines):
                port_a_line = lines[i].strip()
                port_b_line = lines[i + 1].strip()
                
                if port_a_line and port_b_line:
                    # Parse port name and parameters
                    port_a_match = re.match(r'(\S+)\s*(.*)', port_a_line)
                    port_b_match = re.match(r'(\S+)\s*(.*)', port_b_line)
                    
                    if port_a_match and port_b_match:
                        pairs.append({
                            'port_a': port_a_match.group(1),
                            'params_a': port_a_match.group(2),
                            'port_b': port_b_match.group(1),
                            'params_b': port_b_match.group(2),
                        })
        
        logger.info(f"Found {len(pairs)} port pair(s)")
        return pairs
    
    def install_port_pair(
        self,
        port_a_name: Optional[str] = None,
        port_b_name: Optional[str] = None,
        port_a_params: Optional[Dict[str, str]] = None,
        port_b_params: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Install a new virtual port pair.
        
        Args:
            port_a_name: Name for port A (e.g., 'COM8', 'CNCA0', or 'COM#' for auto)
            port_b_name: Name for port B (e.g., 'COM9', 'CNCB0', or '-' for default)
            port_a_params: Additional parameters for port A (e.g., {'EmuBR': 'yes'})
            port_b_params: Additional parameters for port B
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_installed:
            logger.error("Cannot install port pair: com0com not installed")
            return False
        
        # Build install command
        args = ['install']
        
        # Port A specification
        port_a_spec = port_a_name or '-'
        if port_a_params:
            params_str = ','.join(f"{k}={v}" for k, v in port_a_params.items())
            port_a_spec = f"{port_a_name or '0'},{params_str}"
        args.append(port_a_spec)
        
        # Port B specification
        port_b_spec = port_b_name or '-'
        if port_b_params:
            params_str = ','.join(f"{k}={v}" for k, v in port_b_params.items())
            port_b_spec = f"{port_b_name or '0'},{params_str}"
        args.append(port_b_spec)
        
        logger.info(f"Installing port pair: {port_a_spec} <-> {port_b_spec}")
        
        try:
            returncode, stdout, stderr = self._run_setupc(args)
            
            if returncode == 0:
                logger.info(f"Port pair installed successfully")
                logger.debug(f"Output: {stdout}")
                return True
            else:
                logger.error(f"Failed to install port pair: {stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception during port pair installation: {e}")
            return False
    
    def remove_port_pair(self, port_name: str) -> bool:
        """
        Remove a virtual port pair by specifying one port of the pair.
        
        Args:
            port_name: Name of one port in the pair (e.g., 'CNCA0', 'COM8')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_installed:
            logger.error("Cannot remove port pair: com0com not installed")
            return False
        
        logger.info(f"Removing port pair containing: {port_name}")
        
        try:
            returncode, stdout, stderr = self._run_setupc(['remove', port_name])
            
            if returncode == 0:
                logger.info(f"Port pair removed successfully")
                return True
            else:
                logger.error(f"Failed to remove port pair: {stderr}")
                return False
        except Exception as e:
            logger.error(f"Exception during port pair removal: {e}")
            return False

