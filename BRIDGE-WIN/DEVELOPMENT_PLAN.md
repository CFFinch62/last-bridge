# BRIDGE-WIN Development Plan

**Project**: Windows Virtual Null Modem Bridge with Serial Sniffing  
**Language**: Python 3.11+  
**GUI Framework**: PyQt6  
**Target Platform**: Windows 10/11  
**Start Date**: 2025-11-08  

---

## Project Overview

BRIDGE-WIN is a Windows port of the Linux BRIDGE application, providing virtual null modem functionality using com0com as the backend, with advanced serial data sniffing capabilities for marine electronics and protocol analysis.

---

## Technology Stack

- **Language**: Python 3.13.0 (3.11+ compatible)
- **GUI**: PyQt6 6.10.0
- **Serial**: pyserial 3.5
- **Windows Integration**: pywin32 311
- **Virtual Ports**: com0com (external dependency)
- **Packaging**: PyInstaller
- **Configuration**: JSON-based settings

---

## Development Phases

### Phase 1: Project Setup & Foundation
**Estimated Time**: 3-4 hours
**Status**: ✅ **COMPLETE** (2025-11-08)

- [x] Create project directory structure
- [x] Set up Python virtual environment (Python 3.13.0)
- [x] Create requirements.txt with dependencies
- [x] Create core documentation (3 files: priorities, plan, changelog)
- [x] Set up .gitignore for Python project
- [x] Create main application entry point (bridge_win.py)
- [x] Create utility modules (logger.py, settings.py)
- [x] Install all dependencies (PyQt6, pyserial, pywin32)
- [x] Test application successfully

**Deliverables**: ✅
- Working project structure
- Runnable skeleton application
- Documentation for setup
- All dependencies installed and tested

---

### Phase 2: com0com Backend Integration
**Estimated Time**: 6-8 hours
**Status**: ✅ **COMPLETE** (2025-11-08)

#### 2.1 com0com Manager Module
- [x] Create `backend/com0com_manager.py` (287 lines)
- [x] Implement com0com detection (check if installed)
- [x] Implement setupc.exe path discovery (registry, common paths, PATH)
- [x] Create function to list existing port pairs
- [x] Create function to install new port pair
- [x] Create function to remove port pair
- [x] Add error handling for com0com operations
- [x] Add logging for all com0com operations

#### 2.2 Virtual Port Management
- [x] Create `backend/virtual_ports.py` (272 lines)
- [x] Implement port pair creation logic with validation
- [x] Implement port pair deletion logic
- [x] Implement port status checking
- [x] Add port validation (check if ports are in use)
- [x] Create port enumeration (list available COM ports)
- [x] Add automatic port number selection
- [x] Create test script (`test_backend.py`)
- [x] Test backend integration successfully

**Deliverables**: ✅
- Functional com0com integration
- Ability to create/delete virtual port pairs
- Robust error handling
- Automatic port selection
- Comprehensive testing

---

### Phase 3: Basic GUI Implementation
**Estimated Time**: 8-10 hours
**Status**: ✅ COMPLETE

#### 3.1 Main Window Structure
- [x] Create `gui/main_window.py`
- [x] Design main window layout (800x600 default)
- [x] Create menu bar (File, Tools, Help)
- [x] Create tab widget for different sections
- [x] Add status bar at bottom
- [x] Implement window icon
- [x] Add window close event handling

#### 3.2 Configuration Tab
- [x] Create `gui/config_tab.py`
- [x] Add port pair configuration section
  - [x] COM port 1 selection (dropdown)
  - [x] COM port 2 selection (dropdown)
  - [x] Auto-select port option
  - [x] Port pair creation UI
- [x] Add control buttons
  - [x] "Create Port Pair" button
  - [x] "Delete Port Pair" button
  - [x] "Refresh Ports" button
  - [ ] "Start Bridge" button (deferred to Phase 4)
  - [ ] "Stop Bridge" button (deferred to Phase 4)
- [x] Add port status display
  - [x] Show active port pairs in table
  - [x] Show port parameters
  - [x] Show com0com status
- [x] Connect UI to backend functions

#### 3.3 Status & Logging Tab
- [x] Create `gui/status_tab.py`
- [x] Add log viewer (QTextEdit with scrolling)
- [x] Add log level filtering (ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [x] Add clear log button
- [x] Add save log to file button
- [x] Implement real-time log updates
- [x] Add timestamp to log entries
- [x] Color-code log levels

**Deliverables**:
- ✅ Functional GUI with tabs
- ✅ Working port creation/deletion from GUI (requires admin)
- ✅ Real-time status updates and logging

---

### Phase 4: Serial Bridge & Sniffing
**Estimated Time**: 10-12 hours
**Status**: ⏳ IN PROGRESS (Bridge complete, sniffing pending)

#### 4.0 Serial Bridge Engine ✅ DONE (Session 8)
- [x] Create `backend/bridge.py` (289 lines)
- [x] Implement bidirectional threading (A→B and B→A)
- [x] Add real-time statistics tracking
- [x] Add data callback for sniffing integration
- [x] Update `gui/config_tab.py` with bridge controls (496 lines)
- [x] Add Start/Stop bridge buttons
- [x] Add bridge status and statistics display
- [ ] Test bridge functionality with virtual port pairs

#### 4.1 Core Sniffing Engine
- [ ] Create `backend/sniffing.py`
- [ ] Implement data capture from bridge callback
- [ ] Add data direction filtering (RX/TX/Both)
- [ ] Add data format conversion (Raw/Hex/Text)
- [ ] Implement circular buffer for data
- [ ] Add statistics tracking (bytes RX/TX, packets)

#### 4.2 TCP Output
- [ ] Implement TCP server for data streaming
- [ ] Add configurable TCP port (default 8888)
- [ ] Support multiple simultaneous clients
- [ ] Add client connection/disconnection handling
- [ ] Implement data broadcasting to all clients
- [ ] Add TCP server start/stop controls

#### 4.3 File Logging
- [ ] Implement file output for captured data
- [ ] Add configurable file path
- [ ] Support different file formats (raw, hex dump, text)
- [ ] Add file rotation options (size-based)
- [ ] Implement timestamp in filenames
- [ ] Add append vs overwrite options

#### 4.4 Windows Named Pipes
- [ ] Implement Windows named pipe creation
- [ ] Add configurable pipe name
- [ ] Handle pipe client connections
- [ ] Implement data writing to pipe
- [ ] Add pipe error handling
- [ ] Support multiple pipe readers

#### 4.5 Sniffing GUI Tab
- [ ] Create `gui/sniffing_tab.py`
- [ ] Add sniffing enable/disable toggle
- [ ] Add output method checkboxes
  - [ ] TCP output (with port configuration)
  - [ ] File output (with path selection)
  - [ ] Named pipe output (with pipe name)
- [ ] Add data direction radio buttons (RX/TX/Both)
- [ ] Add data format radio buttons (Raw/Hex/Text)
- [ ] Add statistics display
  - [ ] Bytes received
  - [ ] Bytes transmitted
  - [ ] Active clients (TCP)
  - [ ] Capture duration
- [ ] Add real-time data preview window
- [ ] Add start/stop sniffing buttons

**Deliverables**:
- Full sniffing functionality
- Multiple output methods working
- Professional sniffing GUI

---

### Phase 5: Settings & Configuration
**Estimated Time**: 4-5 hours  
**Status**: Not Started

#### 5.1 Settings Management
- [ ] Create `utils/settings.py`
- [ ] Implement JSON-based settings storage
- [ ] Add default settings
- [ ] Create settings load/save functions
- [ ] Add settings validation
- [ ] Implement settings migration (version updates)

#### 5.2 Settings to Persist
- [ ] Last used port pair configuration
- [ ] Window size and position
- [ ] Sniffing preferences
- [ ] TCP/UDP port numbers
- [ ] File output paths
- [ ] Log level preferences
- [ ] Theme preferences (if applicable)

#### 5.3 Settings GUI
- [ ] Create settings dialog (QDialog)
- [ ] Add general settings tab
- [ ] Add sniffing defaults tab
- [ ] Add appearance settings tab
- [ ] Add OK/Cancel/Apply buttons
- [ ] Connect settings to application behavior

**Deliverables**:
- Persistent settings across sessions
- User-friendly settings dialog

---

### Phase 6: Error Handling & Robustness
**Estimated Time**: 5-6 hours  
**Status**: Not Started

- [ ] Add comprehensive error handling
  - [ ] com0com not installed
  - [ ] Port already in use
  - [ ] Permission errors
  - [ ] Network errors (TCP/UDP)
  - [ ] File I/O errors
- [ ] Implement user-friendly error messages
- [ ] Add error recovery mechanisms
- [ ] Create error logging system
- [ ] Add validation for all user inputs
- [ ] Implement graceful shutdown
- [ ] Add cleanup on application exit
- [ ] Handle unexpected disconnections
- [ ] Add timeout handling for operations

**Deliverables**:
- Robust application with proper error handling
- Clear error messages for users

---

### Phase 7: Testing & Integration
**Estimated Time**: 6-8 hours  
**Status**: Not Started

#### 7.1 Unit Testing
- [ ] Test com0com integration
- [ ] Test port creation/deletion
- [ ] Test sniffing engine
- [ ] Test data format conversions
- [ ] Test settings persistence

#### 7.2 Integration Testing
- [ ] Test with LAST application
- [ ] Test with real serial devices
- [ ] Test TCP client connections
- [ ] Test file logging
- [ ] Test named pipe communication
- [ ] Test multiple simultaneous operations

#### 7.3 User Acceptance Testing
- [ ] Test on clean Windows 10 system
- [ ] Test on Windows 11 system
- [ ] Test with different com0com versions
- [ ] Test with various serial devices
- [ ] Verify all GUI elements work correctly
- [ ] Test edge cases and error conditions

**Deliverables**:
- Tested and verified application
- Bug fixes for discovered issues

---

### Phase 8: Documentation & Polish
**Estimated Time**: 4-5 hours  
**Status**: Not Started

#### 8.1 User Documentation
- [ ] Create comprehensive README.md
- [ ] Write installation guide
- [ ] Create user manual
- [ ] Add screenshots to documentation
- [ ] Create quick start guide
- [ ] Document com0com installation
- [ ] Add troubleshooting section
- [ ] Create FAQ

#### 8.2 Developer Documentation
- [ ] Add code comments
- [ ] Create API documentation
- [ ] Document architecture
- [ ] Add contribution guidelines
- [ ] Document build process

#### 8.3 UI Polish
- [ ] Add application icon
- [ ] Improve layout spacing
- [ ] Add tooltips to all controls
- [ ] Implement keyboard shortcuts
- [ ] Add about dialog
- [ ] Improve visual feedback
- [ ] Add progress indicators

**Deliverables**:
- Complete documentation
- Polished user interface

---

### Phase 9: Packaging & Distribution
**Estimated Time**: 3-4 hours  
**Status**: Not Started

#### 9.1 PyInstaller Setup
- [ ] Create PyInstaller spec file
- [ ] Configure build options
- [ ] Include all dependencies
- [ ] Add application icon
- [ ] Test standalone executable
- [ ] Optimize executable size

#### 9.2 Installer Creation
- [ ] Create installer script (NSIS or Inno Setup)
- [ ] Add com0com installation check
- [ ] Create uninstaller
- [ ] Add desktop shortcut option
- [ ] Add start menu entry
- [ ] Test installer on clean system

#### 9.3 Distribution Package
- [ ] Create release notes
- [ ] Package documentation
- [ ] Create version numbering scheme
- [ ] Prepare distribution archive
- [ ] Test complete installation process

**Deliverables**:
- Standalone executable
- Professional installer
- Distribution package

---

## Total Estimated Time

**Total Development Time**: 49-62 hours  
**Recommended Schedule**: 2-3 weeks (part-time) or 1-2 weeks (full-time)

---

## Success Criteria

- ✅ Application creates virtual COM port pairs using com0com
- ✅ Virtual ports work with LAST and other serial applications
- ✅ Sniffing captures serial data in real-time
- ✅ TCP output streams data to network clients
- ✅ File logging saves captured data
- ✅ Named pipes work for IPC
- ✅ GUI is intuitive and responsive
- ✅ Settings persist across sessions
- ✅ Application handles errors gracefully
- ✅ Standalone executable runs on Windows 10/11
- ✅ Documentation is complete and clear

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| com0com compatibility issues | Medium | High | Test with multiple versions, provide fallback options |
| PyQt6 learning curve | Low | Medium | Use extensive documentation, examples |
| Serial port access conflicts | Medium | Medium | Implement proper port locking, clear error messages |
| Windows permissions issues | Medium | High | Document admin requirements, handle gracefully |
| Packaging complexity | Low | Medium | Use proven PyInstaller configurations |

---

## Notes

- Keep Linux BRIDGE compatibility in mind for potential future cross-platform version
- Consider adding UDP output in future version (not in initial release)
- May add GUI themes in future update
- Consider adding protocol analyzers in future (NMEA, Modbus, etc.)

---

**Last Updated**: 2025-11-08  
**Version**: 1.0

