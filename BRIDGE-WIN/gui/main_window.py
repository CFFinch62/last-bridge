"""
Main Window Module

This module provides the main application window for BRIDGE-WIN.
Includes menu bar, tab widget, and status bar.

Author: BRIDGE-WIN Development Team
License: GPL
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon

from utils.logger import get_logger
from utils.settings import SettingsManager

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window for BRIDGE-WIN."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.settings = SettingsManager()
        self.tabs = {}
        
        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._restore_window_state()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("BRIDGE-WIN - Virtual Null Modem Bridge")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        logger.debug("UI initialized")
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # File -> Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Tools -> Refresh Ports
        refresh_action = QAction("&Refresh Ports", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh COM port list")
        refresh_action.triggered.connect(self._on_refresh_ports)
        tools_menu.addAction(refresh_action)
        
        tools_menu.addSeparator()
        
        # Tools -> Settings
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self._on_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # Help -> About
        about_action = QAction("&About", self)
        about_action.setStatusTip("About BRIDGE-WIN")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
        # Help -> About Qt
        about_qt_action = QAction("About &Qt", self)
        about_qt_action.setStatusTip("About Qt")
        about_qt_action.triggered.connect(self._on_about_qt)
        help_menu.addAction(about_qt_action)
        
        logger.debug("Menu bar created")
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Set initial status
        self.status_bar.showMessage("Ready")
        
        logger.debug("Status bar created")
    
    def add_tab(self, widget, title, name=None):
        """
        Add a tab to the tab widget.
        
        Args:
            widget: The widget to add as a tab
            title: The tab title
            name: Optional internal name for the tab
        """
        index = self.tab_widget.addTab(widget, title)
        
        if name:
            self.tabs[name] = widget
        
        logger.debug(f"Added tab: {title}")
        return index
    
    def set_status(self, message, timeout=0):
        """
        Set the status bar message.
        
        Args:
            message: The message to display
            timeout: Timeout in milliseconds (0 = permanent)
        """
        self.status_bar.showMessage(message, timeout)
    
    def _restore_window_state(self):
        """Restore window size and position from settings."""
        try:
            # Get saved window size
            width = self.settings.get('window_width', 1000)
            height = self.settings.get('window_height', 700)
            self.resize(width, height)

            # Get saved position
            x = self.settings.get('window_x', -1)
            y = self.settings.get('window_y', -1)

            if x >= 0 and y >= 0:
                self.move(x, y)
                logger.debug(f"Window position restored: ({x}, {y})")
            else:
                logger.debug("Using default window position (centered)")

            logger.debug(f"Window size restored: {width}x{height}")
        except Exception as e:
            logger.warning(f"Failed to restore window state: {e}")
            self.resize(1000, 700)

    def _save_window_state(self):
        """Save window size and position to settings."""
        try:
            # Save window size
            self.settings.set('window_width', self.width())
            self.settings.set('window_height', self.height())

            # Save window position
            self.settings.set('window_x', self.x())
            self.settings.set('window_y', self.y())

            self.settings.save()
            logger.debug("Window state saved")
        except Exception as e:
            logger.warning(f"Failed to save window state: {e}")
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: The close event
        """
        logger.info("Application closing")
        
        # Save window state
        self._save_window_state()
        
        # Accept the close event
        event.accept()
    
    def _on_refresh_ports(self):
        """Handle refresh ports action."""
        logger.info("Refreshing ports")
        self.set_status("Refreshing ports...", 2000)
        
        # Emit signal to refresh ports in config tab
        if 'config' in self.tabs:
            self.tabs['config'].refresh_ports()
    
    def _on_settings(self):
        """Handle settings action."""
        logger.info("Opening settings")
        self.set_status("Settings not yet implemented", 3000)
        
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog will be implemented in a future version."
        )
    
    def _on_about(self):
        """Handle about action."""
        logger.info("Showing about dialog")
        
        about_text = """
        <h2>BRIDGE-WIN</h2>
        <p><b>Virtual Null Modem Bridge for Windows</b></p>
        <p>Version: 0.1.0-dev</p>
        <p>A Windows port of the BRIDGE application for creating and managing 
        virtual serial port pairs using com0com.</p>
        <p>Features:</p>
        <ul>
            <li>Create/delete virtual COM port pairs</li>
            <li>Serial data sniffing and monitoring</li>
            <li>TCP output for remote monitoring</li>
            <li>Real-time logging and statistics</li>
        </ul>
        <p><b>License:</b> MIT</p>
        <p><b>Author:</b> Fragillidae Software - Chuck Finch</p>
        """
        
        QMessageBox.about(self, "About BRIDGE-WIN", about_text)
    
    def _on_about_qt(self):
        """Handle about Qt action."""
        QMessageBox.aboutQt(self, "About Qt")

