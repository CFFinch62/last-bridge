"""
BRIDGE-WIN Logging Utilities
Centralized logging configuration and helper functions
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)


def setup_logger(
    name: str = "BRIDGE-WIN",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True,
    colored: bool = True,
) -> logging.Logger:
    """
    Set up and configure a logger
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        console: Enable console logging
        colored: Use colored output for console (Windows 10+ only)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
        
        if colored and sys.platform == "win32":
            # Enable ANSI colors on Windows 10+
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                formatter = ColoredFormatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
            except Exception:
                # Fallback to non-colored
                formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        else:
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(LOG_LEVELS.get(level.upper(), logging.INFO))
        file_formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "BRIDGE-WIN") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        setup_logger(name)
    
    return logger


def create_log_file_path(base_dir: Optional[Path] = None) -> Path:
    """
    Create a timestamped log file path
    
    Args:
        base_dir: Base directory for log files (default: current directory)
    
    Returns:
        Path to log file
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"bridge_win_{timestamp}.log"
    
    return base_dir / log_filename


# Module-level logger for this package
_module_logger = get_logger(__name__)


if __name__ == "__main__":
    # Test logging functionality
    test_logger = setup_logger("TEST", level="DEBUG", colored=True)
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")
    
    print("\nLogger test complete!")

