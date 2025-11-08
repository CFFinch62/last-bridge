@echo off
REM BRIDGE-WIN Setup Script
REM Automated setup for Windows development environment

echo ============================================================
echo BRIDGE-WIN - Setup Script
echo ============================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

python --version
echo.

REM Check Python version
echo [2/5] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.11 or higher is required
    python -c "import sys; print(f'Current version: {sys.version}')"
    pause
    exit /b 1
)
echo Python version OK
echo.

REM Create virtual environment
echo [3/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment and install dependencies
echo [4/5] Installing dependencies...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Check com0com installation
echo [5/5] Checking com0com installation...
if exist "C:\Program Files (x86)\com0com\setupc.exe" (
    echo com0com found: C:\Program Files (x86)\com0com\setupc.exe
) else if exist "C:\Program Files\com0com\setupc.exe" (
    echo com0com found: C:\Program Files\com0com\setupc.exe
) else (
    echo WARNING: com0com not found in standard locations
    echo Please install com0com from: http://com0com.sourceforge.net/
    echo.
    echo Note: On Windows 10/11 x64, you may need to enable test-signing:
    echo   bcdedit /set testsigning on
    echo   (Requires administrator privileges and reboot)
)
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run application: python bridge_win.py
echo.
echo If com0com is not installed:
echo   1. Download from: http://com0com.sourceforge.net/
echo   2. Install as Administrator
echo   3. Enable test-signing if needed (see README.md)
echo.
pause

