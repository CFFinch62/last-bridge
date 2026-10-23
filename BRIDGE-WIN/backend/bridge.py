"""
Serial Bridge Module

This module implements the core serial bridge functionality, passing data
bidirectionally between two COM ports using threading.

Author: BRIDGE-WIN Development Team
License: GPL
"""

import threading
import time
from typing import Optional, Callable
from enum import Enum

import serial
from serial import Serial

from utils.logger import get_logger

logger = get_logger(__name__)


class BridgeState(Enum):
    """Bridge state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class SerialBridge:
    """
    Serial bridge that passes data bidirectionally between two COM ports.
    
    This class creates two threads:
    - One thread reads from port A and writes to port B
    - Another thread reads from port B and writes to port A
    """
    
    def __init__(self, 
                 port_a: str,
                 port_b: str,
                 baudrate: int = 9600,
                 data_callback: Optional[Callable] = None):
        """
        Initialize the serial bridge.
        
        Args:
            port_a: First COM port name (e.g., "COM10")
            port_b: Second COM port name (e.g., "COM11")
            baudrate: Baud rate for both ports (default: 9600)
            data_callback: Optional callback for data sniffing (direction, data)
        """
        self.port_a_name = port_a
        self.port_b_name = port_b
        self.baudrate = baudrate
        self.data_callback = data_callback
        
        self.port_a: Optional[Serial] = None
        self.port_b: Optional[Serial] = None
        
        self.state = BridgeState.STOPPED
        self.running = False
        
        self.thread_a_to_b: Optional[threading.Thread] = None
        self.thread_b_to_a: Optional[threading.Thread] = None
        
        self.bytes_a_to_b = 0
        self.bytes_b_to_a = 0
        self.start_time: Optional[float] = None
        
        self.error_message: Optional[str] = None
        
        logger.info(f"SerialBridge initialized: {port_a} <-> {port_b} @ {baudrate} baud")
    
    def start(self) -> bool:
        """
        Start the serial bridge.
        
        Returns:
            True if bridge started successfully, False otherwise
        """
        if self.state == BridgeState.RUNNING:
            logger.warning("Bridge is already running")
            return False
        
        logger.info(f"Starting bridge: {self.port_a_name} <-> {self.port_b_name}")
        self.state = BridgeState.STARTING
        self.error_message = None
        
        try:
            # Open serial ports
            logger.debug(f"Opening {self.port_a_name}...")
            self.port_a = Serial(
                port=self.port_a_name,
                baudrate=self.baudrate,
                timeout=0.1,  # 100ms timeout for non-blocking reads
                write_timeout=1.0
            )
            
            logger.debug(f"Opening {self.port_b_name}...")
            self.port_b = Serial(
                port=self.port_b_name,
                baudrate=self.baudrate,
                timeout=0.1,
                write_timeout=1.0
            )
            
            # Reset statistics
            self.bytes_a_to_b = 0
            self.bytes_b_to_a = 0
            self.start_time = time.time()
            
            # Start bridge threads
            self.running = True
            
            self.thread_a_to_b = threading.Thread(
                target=self._bridge_thread,
                args=(self.port_a, self.port_b, "A→B"),
                daemon=True,
                name="Bridge-A-to-B"
            )
            
            self.thread_b_to_a = threading.Thread(
                target=self._bridge_thread,
                args=(self.port_b, self.port_a, "B→A"),
                daemon=True,
                name="Bridge-B-to-A"
            )
            
            self.thread_a_to_b.start()
            self.thread_b_to_a.start()
            
            self.state = BridgeState.RUNNING
            logger.info(f"✓ Bridge started: {self.port_a_name} <-> {self.port_b_name}")
            return True
            
        except serial.SerialException as e:
            self.error_message = f"Serial port error: {str(e)}"
            logger.error(f"Failed to start bridge: {self.error_message}")
            self.state = BridgeState.ERROR
            self._cleanup()
            return False
            
        except Exception as e:
            self.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Failed to start bridge: {self.error_message}")
            self.state = BridgeState.ERROR
            self._cleanup()
            return False
    
    def stop(self) -> bool:
        """
        Stop the serial bridge.
        
        Returns:
            True if bridge stopped successfully, False otherwise
        """
        if self.state == BridgeState.STOPPED:
            logger.warning("Bridge is already stopped")
            return False
        
        logger.info("Stopping bridge...")
        self.state = BridgeState.STOPPING
        
        # Signal threads to stop
        self.running = False
        
        # Wait for threads to finish (with timeout)
        if self.thread_a_to_b and self.thread_a_to_b.is_alive():
            self.thread_a_to_b.join(timeout=2.0)
        
        if self.thread_b_to_a and self.thread_b_to_a.is_alive():
            self.thread_b_to_a.join(timeout=2.0)
        
        # Cleanup
        self._cleanup()
        
        self.state = BridgeState.STOPPED
        logger.info("✓ Bridge stopped")
        return True
    
    def _bridge_thread(self, source: Serial, dest: Serial, direction: str):
        """
        Bridge thread that reads from source and writes to destination.
        
        Args:
            source: Source serial port
            dest: Destination serial port
            direction: Direction label for logging (e.g., "A→B")
        """
        logger.debug(f"Bridge thread started: {direction}")
        
        try:
            while self.running:
                # Read data from source
                if source.in_waiting > 0:
                    data = source.read(source.in_waiting or 1)
                    
                    if data:
                        # Write to destination
                        dest.write(data)
                        dest.flush()
                        
                        # Update statistics
                        if direction == "A→B":
                            self.bytes_a_to_b += len(data)
                        else:
                            self.bytes_b_to_a += len(data)
                        
                        # Call data callback for sniffing
                        if self.data_callback:
                            try:
                                self.data_callback(direction, data)
                            except Exception as e:
                                logger.error(f"Data callback error: {e}")
                        
                        logger.debug(f"{direction}: {len(data)} bytes")
                else:
                    # Small sleep to avoid busy waiting
                    time.sleep(0.01)
                    
        except serial.SerialException as e:
            logger.error(f"Serial error in {direction} thread: {e}")
            self.error_message = f"Serial error in {direction}: {str(e)}"
            self.state = BridgeState.ERROR
            
        except Exception as e:
            logger.error(f"Unexpected error in {direction} thread: {e}")
            self.error_message = f"Error in {direction}: {str(e)}"
            self.state = BridgeState.ERROR
        
        logger.debug(f"Bridge thread stopped: {direction}")
    
    def _cleanup(self):
        """Clean up serial ports."""
        if self.port_a and self.port_a.is_open:
            try:
                self.port_a.close()
                logger.debug(f"Closed {self.port_a_name}")
            except Exception as e:
                logger.error(f"Error closing {self.port_a_name}: {e}")
        
        if self.port_b and self.port_b.is_open:
            try:
                self.port_b.close()
                logger.debug(f"Closed {self.port_b_name}")
            except Exception as e:
                logger.error(f"Error closing {self.port_b_name}: {e}")
        
        self.port_a = None
        self.port_b = None
    
    def get_statistics(self) -> dict:
        """
        Get bridge statistics.
        
        Returns:
            Dictionary with statistics
        """
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            'state': self.state.value,
            'port_a': self.port_a_name,
            'port_b': self.port_b_name,
            'baudrate': self.baudrate,
            'bytes_a_to_b': self.bytes_a_to_b,
            'bytes_b_to_a': self.bytes_b_to_a,
            'total_bytes': self.bytes_a_to_b + self.bytes_b_to_a,
            'uptime_seconds': uptime,
            'error_message': self.error_message
        }
    
    def is_running(self) -> bool:
        """Check if bridge is running."""
        return self.state == BridgeState.RUNNING
    
    def __del__(self):
        """Destructor - ensure ports are closed."""
        if self.running:
            self.stop()

