"""
Configuration Tab Module

This module provides the configuration tab for managing virtual port pairs.
Includes port selection, creation/deletion, and status display.

Author: BRIDGE-WIN Development Team
License: GPL
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from backend.virtual_ports import VirtualPortManager
from backend.bridge import SerialBridge, BridgeState
from utils.logger import get_logger

logger = get_logger(__name__)


class ConfigTab(QWidget):
    """Configuration tab for port pair management."""
    
    # Signals
    status_message = pyqtSignal(str, int)  # message, timeout
    
    def __init__(self, parent=None):
        """Initialize the configuration tab."""
        super().__init__(parent)

        self.port_manager = VirtualPortManager()
        self.bridge: Optional[SerialBridge] = None

        self._init_ui()
        self._check_com0com()
        self.refresh_ports()

        logger.info("Configuration tab initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # com0com status group
        self._create_status_group(layout)

        # Bridge control group
        self._create_bridge_group(layout)

        # Port pair creation group
        self._create_creation_group(layout)

        # Existing port pairs group
        self._create_pairs_group(layout)

        # Add stretch to push everything to the top
        layout.addStretch()
    
    def _create_status_group(self, parent_layout):
        """Create the com0com status group."""
        group = QGroupBox("com0com Status")
        layout = QHBoxLayout(group)

        self.status_label = QLabel("Checking...")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        parent_layout.addWidget(group)

    def _create_bridge_group(self, parent_layout):
        """Create the bridge control group."""
        group = QGroupBox("Serial Bridge Control")
        layout = QVBoxLayout(group)

        # Bridge status row
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Bridge Status:"))

        self.bridge_status_label = QLabel("Stopped")
        self.bridge_status_label.setStyleSheet("font-weight: bold; color: gray;")
        status_layout.addWidget(self.bridge_status_label)

        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Statistics row
        stats_layout = QHBoxLayout()
        self.bridge_stats_label = QLabel("No data")
        stats_layout.addWidget(self.bridge_stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Control buttons row
        button_layout = QHBoxLayout()

        self.start_bridge_button = QPushButton("Start Bridge")
        self.start_bridge_button.clicked.connect(self._on_start_bridge)
        self.start_bridge_button.setEnabled(False)
        button_layout.addWidget(self.start_bridge_button)

        self.stop_bridge_button = QPushButton("Stop Bridge")
        self.stop_bridge_button.clicked.connect(self._on_stop_bridge)
        self.stop_bridge_button.setEnabled(False)
        button_layout.addWidget(self.stop_bridge_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        parent_layout.addWidget(group)
    
    def _create_creation_group(self, parent_layout):
        """Create the port pair creation group."""
        group = QGroupBox("Create New Port Pair")
        layout = QVBoxLayout(group)
        
        # Port selection row
        port_layout = QHBoxLayout()
        
        # Port A selection
        port_layout.addWidget(QLabel("Port A:"))
        self.port_a_combo = QComboBox()
        self.port_a_combo.setMinimumWidth(100)
        port_layout.addWidget(self.port_a_combo)
        
        port_layout.addSpacing(20)
        
        # Port B selection
        port_layout.addWidget(QLabel("Port B:"))
        self.port_b_combo = QComboBox()
        self.port_b_combo.setMinimumWidth(100)
        port_layout.addWidget(self.port_b_combo)
        
        port_layout.addStretch()
        
        layout.addLayout(port_layout)
        
        # Options row
        options_layout = QHBoxLayout()
        
        # Auto-select checkbox (future feature)
        # For now, we'll always use auto-select
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Buttons row
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Port Pair")
        self.create_button.clicked.connect(self._on_create_port_pair)
        button_layout.addWidget(self.create_button)
        
        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self.refresh_ports)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        parent_layout.addWidget(group)
    
    def _create_pairs_group(self, parent_layout):
        """Create the existing port pairs group."""
        group = QGroupBox("Existing Virtual Port Pairs")
        layout = QVBoxLayout(group)
        
        # Table for port pairs
        self.pairs_table = QTableWidget()
        self.pairs_table.setColumnCount(4)
        self.pairs_table.setHorizontalHeaderLabels([
            "Port A", "Port B", "Parameters", "Actions"
        ])
        
        # Set column resize modes
        header = self.pairs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set table properties
        self.pairs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pairs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pairs_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.pairs_table)
        
        parent_layout.addWidget(group)
    
    def _check_com0com(self):
        """Check if com0com is installed."""
        if self.port_manager.is_com0com_available():
            self.status_label.setText("✓ com0com is installed and ready")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.create_button.setEnabled(True)
        else:
            self.status_label.setText("✗ com0com is NOT installed")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.create_button.setEnabled(False)
            
            # Show warning message
            QMessageBox.warning(
                self,
                "com0com Not Found",
                "com0com virtual serial port driver is not installed.\n\n"
                "Please download and install com0com from:\n"
                "https://sourceforge.net/projects/com0com/\n\n"
                "Port pair creation will be disabled until com0com is installed."
            )
    
    def refresh_ports(self):
        """Refresh the list of available COM ports."""
        logger.info("Refreshing port list")
        
        try:
            # Get available ports
            available = self.port_manager.get_available_port_numbers(1, 256)
            
            # Update port A combo
            self.port_a_combo.clear()
            self.port_a_combo.addItem("Auto-select", None)
            for num in sorted(available)[:20]:  # Show first 20 available
                self.port_a_combo.addItem(f"COM{num}", num)
            
            # Update port B combo
            self.port_b_combo.clear()
            self.port_b_combo.addItem("Auto-select", None)
            for num in sorted(available)[:20]:  # Show first 20 available
                self.port_b_combo.addItem(f"COM{num}", num)
            
            # Refresh existing pairs table
            self._refresh_pairs_table()
            
            self.status_message.emit("Ports refreshed", 2000)
            logger.debug(f"Found {len(available)} available port numbers")
            
        except Exception as e:
            logger.error(f"Failed to refresh ports: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh ports:\n{str(e)}"
            )
    
    def _refresh_pairs_table(self):
        """Refresh the existing port pairs table."""
        try:
            # Get existing pairs
            pairs = self.port_manager.list_virtual_port_pairs()

            # Update table
            self.pairs_table.setRowCount(len(pairs))

            for row, pair in enumerate(pairs):
                # Port A
                self.pairs_table.setItem(row, 0, QTableWidgetItem(pair['port_a']))

                # Port B
                self.pairs_table.setItem(row, 1, QTableWidgetItem(pair['port_b']))

                # Parameters (combine both)
                params = f"A: {pair['params_a']}\nB: {pair['params_b']}"
                self.pairs_table.setItem(row, 2, QTableWidgetItem(params))

                # Delete button
                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(
                    lambda checked, p=pair['port_a']: self._on_delete_port_pair(p)
                )
                self.pairs_table.setCellWidget(row, 3, delete_btn)

            # Enable/disable start bridge button based on port pairs
            self.start_bridge_button.setEnabled(len(pairs) > 0 and not (self.bridge and self.bridge.is_running()))

            logger.debug(f"Refreshed pairs table: {len(pairs)} pair(s)")

        except Exception as e:
            logger.error(f"Failed to refresh pairs table: {e}")
    
    def _on_create_port_pair(self):
        """Handle create port pair button click."""
        logger.info("Creating port pair")
        
        try:
            # Get selected ports
            port_a_num = self.port_a_combo.currentData()
            port_b_num = self.port_b_combo.currentData()
            
            # Build port names
            port_a = f"COM{port_a_num}" if port_a_num else None
            port_b = f"COM{port_b_num}" if port_b_num else None
            
            # Create the port pair
            result = self.port_manager.create_port_pair(
                port_a=port_a,
                port_b=port_b,
                enable_baud_emulation=True,
                enable_overrun=True
            )
            
            if result:
                port_a_name, port_b_name = result
                QMessageBox.information(
                    self,
                    "Success",
                    f"Port pair created successfully:\n{port_a_name} <-> {port_b_name}"
                )
                self.status_message.emit(f"Created {port_a_name} <-> {port_b_name}", 3000)
                
                # Refresh the display
                self.refresh_ports()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to create port pair.\n\n"
                    "This operation requires administrator privileges.\n"
                    "Please run BRIDGE-WIN as administrator."
                )
                
        except Exception as e:
            logger.error(f"Failed to create port pair: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create port pair:\n{str(e)}\n\n"
                "Make sure you are running as administrator."
            )
    
    def _on_delete_port_pair(self, port_name):
        """
        Handle delete port pair button click.
        
        Args:
            port_name: Name of the port to delete
        """
        logger.info(f"Deleting port pair: {port_name}")
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the port pair containing {port_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.port_manager.remove_port_pair(port_name)
                
                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Port pair deleted successfully"
                    )
                    self.status_message.emit(f"Deleted port pair", 3000)
                    
                    # Refresh the display
                    self.refresh_ports()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to delete port pair.\n\n"
                        "This operation requires administrator privileges.\n"
                        "Please run BRIDGE-WIN as administrator."
                    )
                    
            except Exception as e:
                logger.error(f"Failed to delete port pair: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete port pair:\n{str(e)}\n\n"
                    "Make sure you are running as administrator."
                )

    def _on_start_bridge(self):
        """Handle start bridge button click."""
        logger.info("Starting bridge")

        try:
            # Get existing port pairs
            pairs = self.port_manager.list_virtual_port_pairs()

            if not pairs:
                QMessageBox.warning(
                    self,
                    "No Port Pairs",
                    "No virtual port pairs found.\n\n"
                    "Please create a port pair first."
                )
                return

            # Use the first port pair
            pair = pairs[0]
            port_a = pair['port_a']
            port_b = pair['port_b']

            # Create and start bridge
            self.bridge = SerialBridge(port_a, port_b, baudrate=9600)

            if self.bridge.start():
                self.bridge_status_label.setText("Running")
                self.bridge_status_label.setStyleSheet("font-weight: bold; color: green;")
                self.start_bridge_button.setEnabled(False)
                self.stop_bridge_button.setEnabled(True)
                self.status_message.emit(f"Bridge started: {port_a} <-> {port_b}", 3000)

                # Start statistics update timer
                self.stats_timer = QTimer()
                self.stats_timer.timeout.connect(self._update_bridge_stats)
                self.stats_timer.start(1000)  # Update every second

                logger.info(f"Bridge started: {port_a} <-> {port_b}")
            else:
                error_msg = self.bridge.error_message or "Unknown error"
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to start bridge:\n{error_msg}"
                )
                self.bridge = None

        except Exception as e:
            logger.error(f"Failed to start bridge: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start bridge:\n{str(e)}"
            )
            self.bridge = None

    def _on_stop_bridge(self):
        """Handle stop bridge button click."""
        logger.info("Stopping bridge")

        if self.bridge:
            try:
                # Stop statistics timer
                if hasattr(self, 'stats_timer'):
                    self.stats_timer.stop()

                # Stop bridge
                self.bridge.stop()

                self.bridge_status_label.setText("Stopped")
                self.bridge_status_label.setStyleSheet("font-weight: bold; color: gray;")
                self.start_bridge_button.setEnabled(True)
                self.stop_bridge_button.setEnabled(False)
                self.bridge_stats_label.setText("No data")
                self.status_message.emit("Bridge stopped", 3000)

                self.bridge = None
                logger.info("Bridge stopped")

            except Exception as e:
                logger.error(f"Failed to stop bridge: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to stop bridge:\n{str(e)}"
                )

    def _update_bridge_stats(self):
        """Update bridge statistics display."""
        if self.bridge and self.bridge.is_running():
            stats = self.bridge.get_statistics()

            uptime = int(stats['uptime_seconds'])
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60

            stats_text = (
                f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d} | "
                f"A→B: {stats['bytes_a_to_b']} bytes | "
                f"B→A: {stats['bytes_b_to_a']} bytes | "
                f"Total: {stats['total_bytes']} bytes"
            )

            self.bridge_stats_label.setText(stats_text)
