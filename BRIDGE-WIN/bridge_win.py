#!/usr/bin/env python3
"""
BRIDGE-WIN - Virtual Null Modem Bridge for Windows
Main application entry point

Author: LAST BRIDGE Development Team
Version: 0.1.0-dev
Platform: Windows 10/11
License: TBD
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def check_python_version():
    """Verify Python version meets minimum requirements"""
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    gui_available = False

    # Try PyQt6 first (test actual import, not just package)
    try:
        from PyQt6.QtWidgets import QApplication
        gui_available = True
        print("✓ PyQt6 available")
    except ImportError:
        print("⚠ PyQt6 not available")
        print("  Note: Python 3.14 is very new, PyQt6 may not support it yet")
        print("  Recommendation: Use Python 3.11-3.13 for full GUI support")
        missing_deps.append("PyQt6 (optional for GUI)")

    try:
        import serial
        print("✓ pyserial available")
    except ImportError:
        missing_deps.append("pyserial (required)")

    try:
        import win32api
        print("✓ pywin32 available")
    except ImportError:
        missing_deps.append("pywin32 (required)")

    if any("required" in dep for dep in missing_deps):
        print("\nERROR: Missing required dependencies:")
        for dep in missing_deps:
            if "required" in dep:
                print(f"  - {dep}")
        print("\nInstall dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    return gui_available

def main():
    """Main application entry point"""
    print("=" * 60)
    print("BRIDGE-WIN - Virtual Null Modem Bridge for Windows")
    print("Version: 0.1.0-dev")
    print("=" * 60)
    print()

    # Check Python version
    check_python_version()
    print(f"✓ Python version: {sys.version.split()[0]}")
    print()

    # Check dependencies
    gui_available = check_dependencies()
    print()

    if gui_available:
        print("✓ All dependencies installed (including GUI)")
        print()
        print("Starting GUI application...")
        print()

        # Import PyQt6 after dependency check
        from PyQt6.QtWidgets import QApplication, QMessageBox

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("BRIDGE-WIN")
        app.setOrganizationName("LAST BRIDGE")
        app.setApplicationVersion("0.1.0-dev")
        app.setStyle("Fusion")

        # Show message that GUI is not yet implemented
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("BRIDGE-WIN")
        msg.setText("BRIDGE-WIN is starting...")
        msg.setInformativeText(
            "Project structure created successfully!\n\n"
            "GUI implementation coming in Phase 3.\n\n"
            "Current Status: Phase 1 - Foundation Complete"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    else:
        print("⚠ Running in backend-only mode (no GUI)")
        print()
        print("Project structure created successfully!")
        print()
        print("Current Status: Phase 1 - Foundation Complete")
        print()

    print("Application initialized successfully!")
    print()
    print("Next steps:")
    print("  1. Implement com0com backend (Phase 2)")
    print("  2. Create GUI components (Phase 3)")
    print("  3. Add sniffing functionality (Phase 4)")
    print()

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

