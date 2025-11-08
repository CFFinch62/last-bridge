"""
Status Tab Module

This module provides the status/logging tab with real-time log viewer.
Includes log filtering, clearing, and saving functionality.

Author: BRIDGE-WIN Development Team
License: GPL
"""

import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QColor

from utils.logger import get_logger

logger = get_logger(__name__)


class LogHandler(logging.Handler):
    """Custom logging handler that emits to a signal."""
    
    def __init__(self, callback):
        """
        Initialize the log handler.
        
        Args:
            callback: Function to call with log records
        """
        super().__init__()
        self.callback = callback
    
    def emit(self, record):
        """
        Emit a log record.
        
        Args:
            record: The log record to emit
        """
        try:
            msg = self.format(record)
            self.callback(record.levelname, msg)
        except Exception:
            self.handleError(record)


class StatusTab(QWidget):
    """Status and logging tab."""
    
    def __init__(self, parent=None):
        """Initialize the status tab."""
        super().__init__(parent)
        
        self.log_buffer = []
        self.max_buffer_size = 1000
        self.current_filter = "ALL"
        
        self._init_ui()
        self._setup_logging()
        
        logger.info("Status tab initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Controls row
        controls_layout = QHBoxLayout()
        
        # Log level filter
        controls_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addSpacing(20)
        
        # Clear button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self._on_clear_log)
        controls_layout.addWidget(self.clear_button)
        
        # Save button
        self.save_button = QPushButton("Save Log")
        self.save_button.clicked.connect(self._on_save_log)
        controls_layout.addWidget(self.save_button)
        
        controls_layout.addStretch()
        
        # Log count label
        self.count_label = QLabel("0 entries")
        controls_layout.addWidget(self.count_label)
        
        layout.addLayout(controls_layout)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Set monospace font
        font = self.log_viewer.font()
        font.setFamily("Consolas, Courier New, monospace")
        font.setPointSize(9)
        self.log_viewer.setFont(font)
        
        layout.addWidget(self.log_viewer)
    
    def _setup_logging(self):
        """Set up logging to capture application logs."""
        # Create custom handler
        handler = LogHandler(self._add_log_entry)
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        
        logger.debug("Logging handler attached to status tab")
    
    def _add_log_entry(self, level, message):
        """
        Add a log entry to the viewer.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
        """
        # Add to buffer
        self.log_buffer.append((level, message))
        
        # Trim buffer if too large
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
        
        # Update display if filter matches
        if self.current_filter == "ALL" or self.current_filter == level:
            self._append_to_viewer(level, message)
        
        # Update count
        self._update_count()
    
    def _append_to_viewer(self, level, message):
        """
        Append a message to the log viewer with color coding.
        
        Args:
            level: Log level
            message: Log message
        """
        # Get color for level
        color = self._get_level_color(level)
        
        # Move cursor to end
        cursor = self.log_viewer.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Insert colored text
        self.log_viewer.setTextCursor(cursor)
        self.log_viewer.setTextColor(color)
        self.log_viewer.append(message)
        
        # Scroll to bottom
        scrollbar = self.log_viewer.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _get_level_color(self, level):
        """
        Get color for log level.
        
        Args:
            level: Log level
            
        Returns:
            QColor for the level
        """
        colors = {
            'DEBUG': QColor(128, 128, 128),      # Gray
            'INFO': QColor(0, 0, 0),             # Black
            'WARNING': QColor(255, 140, 0),      # Orange
            'ERROR': QColor(255, 0, 0),          # Red
            'CRITICAL': QColor(139, 0, 0),       # Dark red
        }
        return colors.get(level, QColor(0, 0, 0))
    
    def _update_count(self):
        """Update the log entry count label."""
        if self.current_filter == "ALL":
            count = len(self.log_buffer)
        else:
            count = sum(1 for level, _ in self.log_buffer if level == self.current_filter)
        
        self.count_label.setText(f"{count} entries")
    
    def _on_filter_changed(self, filter_text):
        """
        Handle filter change.
        
        Args:
            filter_text: New filter text
        """
        self.current_filter = filter_text
        self._refresh_display()
        logger.debug(f"Log filter changed to: {filter_text}")
    
    def _refresh_display(self):
        """Refresh the log display based on current filter."""
        # Clear viewer
        self.log_viewer.clear()
        
        # Re-add filtered entries
        for level, message in self.log_buffer:
            if self.current_filter == "ALL" or self.current_filter == level:
                self._append_to_viewer(level, message)
        
        # Update count
        self._update_count()
    
    def _on_clear_log(self):
        """Handle clear log button click."""
        reply = QMessageBox.question(
            self,
            "Clear Log",
            "Are you sure you want to clear the log?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_buffer.clear()
            self.log_viewer.clear()
            self._update_count()
            logger.info("Log cleared")
    
    def _on_save_log(self):
        """Handle save log button click."""
        # Get save file name
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            f"bridge-win-log-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_name:
            try:
                # Write log to file
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(f"BRIDGE-WIN Log File\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Filter: {self.current_filter}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for level, message in self.log_buffer:
                        if self.current_filter == "ALL" or self.current_filter == level:
                            f.write(f"{message}\n")
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Log saved to:\n{file_name}"
                )
                logger.info(f"Log saved to: {file_name}")
                
            except Exception as e:
                logger.error(f"Failed to save log: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save log:\n{str(e)}"
                )

