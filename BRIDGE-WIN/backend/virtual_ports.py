"""
Virtual Port Management Module

This module provides high-level virtual serial port management functionality.
It builds on top of com0com_manager to provide port enumeration, validation,
and intelligent port pair creation.

Key Features:
- Enumerate all available COM ports on the system
- Validate port availability
- Automatic port number selection
- Port pair creation with validation
- Port status checking

Author: BRIDGE-WIN Development Team
License: GPL
"""

import re
from typing import List, Optional, Set, Tuple
import serial.tools.list_ports

from backend.com0com_manager import Com0comManager
from utils.logger import get_logger

logger = get_logger(__name__)


class VirtualPortManager:
    """High-level manager for virtual serial port operations."""
    
    def __init__(self):
        """Initialize the virtual port manager."""
        self.com0com = Com0comManager()
    
    def is_com0com_available(self) -> bool:
        """
        Check if com0com is installed and available.
        
        Returns:
            True if com0com is available, False otherwise
        """
        return self.com0com.is_installed
    
    def get_all_ports(self) -> List[str]:
        """
        Get a list of all COM ports on the system (real and virtual).
        
        Returns:
            List of port names (e.g., ['COM1', 'COM3', 'COM8'])
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        
        logger.debug(f"Found {len(ports)} COM port(s): {ports}")
        return sorted(ports, key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)
    
    def get_available_port_numbers(self, start: int = 1, end: int = 256) -> Set[int]:
        """
        Get a set of available (unused) COM port numbers.
        
        Args:
            start: Starting port number to check (default: 1)
            end: Ending port number to check (default: 256)
            
        Returns:
            Set of available port numbers
        """
        used_ports = self.get_all_ports()
        used_numbers = set()
        
        for port in used_ports:
            match = re.search(r'COM(\d+)', port, re.IGNORECASE)
            if match:
                used_numbers.add(int(match.group(1)))
        
        available = set(range(start, end + 1)) - used_numbers
        logger.debug(f"Available port numbers: {len(available)} in range {start}-{end}")
        return available
    
    def find_next_available_port_pair(
        self,
        start: int = 10,
        end: int = 256
    ) -> Optional[Tuple[int, int]]:
        """
        Find the next two consecutive available COM port numbers.
        
        Args:
            start: Starting port number to search from (default: 10)
            end: Ending port number to search to (default: 256)
            
        Returns:
            Tuple of (port_a_number, port_b_number) or None if not found
        """
        available = self.get_available_port_numbers(start, end)
        
        # Find two consecutive available ports
        for num in range(start, end):
            if num in available and (num + 1) in available:
                logger.info(f"Found available port pair: COM{num}, COM{num+1}")
                return (num, num + 1)
        
        # If no consecutive ports, find any two available
        available_list = sorted(available)
        if len(available_list) >= 2:
            port_a = available_list[0]
            port_b = available_list[1]
            logger.info(f"Found available port pair (non-consecutive): COM{port_a}, COM{port_b}")
            return (port_a, port_b)
        
        logger.warning("No available port pairs found")
        return None
    
    def is_port_available(self, port_name: str) -> bool:
        """
        Check if a specific port is available (not in use).
        
        Args:
            port_name: Port name to check (e.g., 'COM8')
            
        Returns:
            True if port is available, False if in use
        """
        used_ports = self.get_all_ports()
        available = port_name.upper() not in [p.upper() for p in used_ports]
        
        logger.debug(f"Port {port_name} available: {available}")
        return available
    
    def create_port_pair(
        self,
        port_a: Optional[str] = None,
        port_b: Optional[str] = None,
        enable_baud_emulation: bool = True,
        enable_overrun: bool = True
    ) -> Optional[Tuple[str, str]]:
        """
        Create a new virtual port pair with recommended settings.
        
        Args:
            port_a: Name for port A (e.g., 'COM10' or None for auto)
            port_b: Name for port B (e.g., 'COM11' or None for auto)
            enable_baud_emulation: Enable baud rate emulation (recommended)
            enable_overrun: Enable buffer overrun emulation (recommended)
            
        Returns:
            Tuple of (port_a_name, port_b_name) if successful, None otherwise
        """
        if not self.com0com.is_installed:
            logger.error("Cannot create port pair: com0com not installed")
            return None
        
        # Auto-select ports if not specified
        if port_a is None or port_b is None:
            pair = self.find_next_available_port_pair()
            if pair is None:
                logger.error("Cannot create port pair: no available ports")
                return None
            port_a = f"COM{pair[0]}"
            port_b = f"COM{pair[1]}"
        
        # Validate ports are available
        if not self.is_port_available(port_a):
            logger.error(f"Port {port_a} is already in use")
            return None
        if not self.is_port_available(port_b):
            logger.error(f"Port {port_b} is already in use")
            return None
        
        # Build parameters
        params_a = {}
        params_b = {}
        
        if enable_baud_emulation:
            params_a['EmuBR'] = 'yes'
            params_b['EmuBR'] = 'yes'
        
        if enable_overrun:
            params_a['EmuOverrun'] = 'yes'
            params_b['EmuOverrun'] = 'yes'
        
        # Create the port pair
        logger.info(f"Creating port pair: {port_a} <-> {port_b}")
        success = self.com0com.install_port_pair(
            port_a_name=f"PortName={port_a}",
            port_b_name=f"PortName={port_b}",
            port_a_params=params_a,
            port_b_params=params_b
        )
        
        if success:
            logger.info(f"Port pair created successfully: {port_a} <-> {port_b}")
            return (port_a, port_b)
        else:
            logger.error(f"Failed to create port pair: {port_a} <-> {port_b}")
            return None
    
    def remove_port_pair(self, port_name: str) -> bool:
        """
        Remove a virtual port pair.
        
        Args:
            port_name: Name of one port in the pair (e.g., 'COM10')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.com0com.is_installed:
            logger.error("Cannot remove port pair: com0com not installed")
            return False
        
        logger.info(f"Removing port pair containing: {port_name}")
        return self.com0com.remove_port_pair(port_name)
    
    def list_virtual_port_pairs(self) -> List[dict]:
        """
        List all virtual port pairs created by com0com.
        
        Returns:
            List of dictionaries with port pair information
        """
        if not self.com0com.is_installed:
            logger.warning("Cannot list port pairs: com0com not installed")
            return []
        
        pairs = self.com0com.list_port_pairs()
        logger.info(f"Listed {len(pairs)} virtual port pair(s)")
        return pairs
    
    def get_port_pair_info(self, port_name: str) -> Optional[dict]:
        """
        Get information about the port pair containing the specified port.
        
        Args:
            port_name: Name of one port in the pair
            
        Returns:
            Dictionary with port pair info or None if not found
        """
        pairs = self.list_virtual_port_pairs()
        
        for pair in pairs:
            # Check if port_name matches either port in the pair
            port_a = self._extract_port_name(pair.get('params_a', ''))
            port_b = self._extract_port_name(pair.get('params_b', ''))
            
            if (port_name.upper() == port_a.upper() or 
                port_name.upper() == port_b.upper() or
                port_name.upper() == pair['port_a'].upper() or
                port_name.upper() == pair['port_b'].upper()):
                return pair
        
        return None
    
    def _extract_port_name(self, params: str) -> str:
        """
        Extract the real port name from parameter string.
        
        Args:
            params: Parameter string (e.g., 'PortName=COM10,EmuBR=yes')
            
        Returns:
            Port name or empty string
        """
        match = re.search(r'PortName=([^,\s]+)', params)
        if match:
            return match.group(1)
        return ''

