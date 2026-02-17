# DICOM Creator

A professional DICOM file creation, editing, and transmission tool with comprehensive testing, validation, and performance analysis capabilities.

![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [What's New in v0.7.0](#whats-new-in-v070)
- [Quick Start](#quick-start)
- [Building Your Own EXE](#building-your-own-exe)
- [Usage](#usage)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Version History](#version-history)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Screenshots

### Main Application Interface

![Main Interface](pic1.png)

![Pic2](pic2.png)

![Pic 3](pic3.png)

![Pic 4](pic4.png)

## Features

### Core DICOM Features
- **DICOM Metadata Management** - Create and edit patient, study, and series metadata with validation
- **Image Support** - Load and preview images (PNG, JPG, BMP) as DICOM pixel data
- **DICOM File Operations** - Load, save, and organize DICOM files and folders with DICOMDIR support
- **Remote Transmission** - Send DICOM files to remote servers using C-STORE with SSL/TLS support
- **VR Validation** - Real-time validation against DICOM Value Representation specifications
- **Tag Viewer** - View all DICOM tags including private tags with search and export

### Testing & Performance Features
- **Server Presets** - Save and manage server connection profiles
- **Connection Testing** - TCP validation, latency analysis, and connection quality assessment
- **Stress Testing** - Load simulation with configurable parameters and multi-worker support
- **Transmission History** - Track all transmissions with statistics and JSON export
- **Performance Benchmarking** - File size analysis, latency benchmarks, and throughput measurements
- **Parallel Transmission** - Multi-threaded sending with 3-5x speed improvements

### Test Data Generation
- **Random DICOM Generator** - Create test files with hierarchical structure (Patient → Study → Series → Instances)
- **Bulk Generation** - Generate multiple files with configurable sizes
- **Integrated Testing** - Generate and send in one workflow

## What's New in v0.7.0

**Release Date**: March 2026

### 🔒 SSL/TLS Certificate Support
- Full certificate-based secure DICOM transmission
- Support for PEM, CRT, KEY, PKCS#12, and CER formats
- Enhanced TLS settings dialog with certificate configuration
- Certificate file patterns added to `.gitignore` for security

### 📖 Documentation Improvements
- Streamlined documentation structure
- Removed obsolete quick start guide (consolidated into feature-specific guides)
- Updated all version references to 0.7.0
- Improved certificate management guidance

### ✅ Enhancements
- Better error handling and logging for SSL/TLS operations
- Improved certificate validation before transmission
- Enhanced TLS configuration management
- Better user guidance for secure connections

### 📋 Previous Releases
- **v0.6.1** - LazyImport fixes, improved module loading
- **v0.6.0** - VR validation system, validation dialogs, DICOMDIR support
- **v0.5.0** - Enhanced LazyImport, better class detection
- **v0.4.0** - Connection testing, stress testing, performance benchmarking
- **v0.3.0** - Server presets, tag viewer, random DICOM generator

**Full Details:** See [CHANGELOG_v0.7.0.md](doc/CHANGELOG_v0.7.0.md)

## Quick Start

### Option 1: Run as EXE (Windows, No Python Required)

[![Download Badge](https://img.shields.io/badge/download-Windows%20EXE-blue.svg)](https://github.com/piotrrozentreter/dcmcreator/releases)

**Download & Extract:**
1. Get the `DICOM Creator` folder from `dist/` or releases page
2. Extract anywhere on Windows
3. Double-click `DICOM Creator.exe`

**No installation required!** Everything is packaged inside.

### Option 2: Run from Python Source

**Requirements:**
- Python 3.9 or higher
- Windows, macOS, or Linux

**Installation:**
```bash
# Clone the repository
git clone https://github.com/piotrrozentreter/dcmcreator
cd dcmcreator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py
```

**Dependencies:**
- `pydicom>=2.4.0` - DICOM file handling
- `pynetdicom>=2.0.0` - DICOM network communication
- `pillow>=10.0.0` - Image processing
- `numpy>=1.20.0` - Numerical arrays

## Building Your Own EXE

Want to build a standalone executable yourself?

### Build Requirements

```bash
# Install build dependencies
pip install -r build-requirements.txt
```

**build-requirements.txt** includes:
- `PyInstaller>=6.0.0` - EXE builder
- `pillow>=10.0.0` - Image processing
- `pydicom>=2.4.0` - DICOM library
- `pynetdicom>=2.0.0` - Network DICOM
- `numpy>=1.20.0` - Array processing

### Build Process

```bash
# Create icon (generates app.ico)
python create_icon.py

# Build the executable
python build.py
```

For Windows, you can also run:
```bat
build.bat
```

Your standalone EXE will be created in `dist/DICOM Creator/` with all features included.

**See [doc/BUILD_INSTRUCTIONS.md](doc/BUILD_INSTRUCTIONS.md) for detailed build guide.**

### What's Bundled

| Component | Size | Purpose |
|-----------|------|---------|
| PyDICOM | ~40 MB | DICOM file handling |
| PyNetDICOM | ~30 MB | Network DICOM C-STORE |
| NumPy | ~30 MB | Array processing |
| PIL/Pillow | ~10 MB | Image processing |
| Application | ~5 MB | GUI and logic |
| **Total** | **150-200 MB** | Uncompressed |
| **ZIP** | **60-70 MB** | Compressed distribution |

## Usage

### Creating DICOM Files

1. Fill in Patient, Study, Series metadata
2. (Optional) Load an image via Image tab
3. Click **File → Validate** to check your data
4. Click **File → Save** to save as DICOM

### Loading DICOM Files

1. Go to **Load DICOM** tab
2. Click **Load DICOM File(s)** or **Load DICOM Folder**
3. Select studies/series from the tree
4. Metadata auto-populates in the forms
5. Validation is performed automatically

### Sending to Remote Server

1. Fill in Server IP/hostname and Port
2. Optionally adjust AE Titles
3. For secure transmission, enable **Use TLS/SSL** and configure certificates via **Remote → TLS Settings**
4. Click **Send All Loaded DICOM**
5. Monitor progress in Messages area

#### Using Server Presets
1. Go to **Remote** tab
2. Select a preset from dropdown to auto-load settings
3. Or enter server details and click **Save Current** to save as preset
4. Click **Send All Loaded DICOM**

### Data Validation & VR Compliance

#### Validate Form Data
- Go to **File → Validate** to check all form fields
- View detailed validation report with specific errors
- Get remediation suggestions for invalid values
- Continue with warnings if needed

#### DICOM Data Inspection
- Go to **DICOM → View VRs** to browse complete DICOM Value Representations
- Go to **DICOM → View All Tags** to inspect all tags in a DICOM file:
  - View all public and private tags
  - Search and filter tags
  - Export tags to text file
  - View tag statistics

### Testing & Performance

#### Connection Testing
- Go to **Connection Test** tab
- Enter server details
- Click **Test Connection** to validate
- Review latency and connection quality metrics

#### Stress Testing
- Go to **Stress Test** tab
- Configure test parameters (files, duration, workers)
- Click **Start Stress Test**
- Monitor real-time performance metrics

#### Transmission History
- Go to **Transmission History** tab
- View all past transmissions
- See success/failure rates
- Export data as JSON

#### Parallel Transmission
- Go to **Parallel Send** tab
- Configure worker threads (1-10)
- Select files and destination
- Transmit with 3-5x performance improvement

## System Requirements

### For EXE (Windows Only)
- Windows 7 or newer (64-bit)
- 100 MB disk space
- 300 MB RAM minimum

### For Python
- Python 3.9+
- Cross-platform: Windows, macOS, Linux
- 500 MB disk space
- 500 MB RAM minimum

## Documentation

### Quick Start Guides
- **[doc/INDEX.md](doc/INDEX.md)** - Complete documentation index
- **[doc/GETTING_STARTED.md](doc/GETTING_STARTED.md)** - Getting started guide
- **[doc/QUICK_START_TAG_VIEWER.md](doc/QUICK_START_TAG_VIEWER.md)** - Tag Viewer quick start
- **[doc/QUICK_START_PRESETS.md](doc/QUICK_START_PRESETS.md)** - Server Presets quick start
- **[doc/QUICK_START_RANDOM_DICOM.md](doc/QUICK_START_RANDOM_DICOM.md)** - DICOM generator quick start

### Feature Documentation
- **[doc/TAG_VIEWER_FEATURE.md](doc/TAG_VIEWER_FEATURE.md)** - Complete Tag Viewer documentation
- **[doc/SERVER_PRESETS.md](doc/SERVER_PRESETS.md)** - Server Presets documentation
- **[doc/RANDOM_DICOM_GENERATOR.md](doc/RANDOM_DICOM_GENERATOR.md)** - DICOM generator guide

### Testing Guides
- **[doc/PARALLEL_TRANSMISSION_GUIDE.md](doc/PARALLEL_TRANSMISSION_GUIDE.md)** - Parallel transmission setup
- **[doc/QUICK_TEST_EXECUTION_GUIDE.md](doc/QUICK_TEST_EXECUTION_GUIDE.md)** - Testing workflow
- **[doc/COMPLETE_TEST_EXECUTION_REFERENCE.md](doc/COMPLETE_TEST_EXECUTION_REFERENCE.md)** - Complete testing reference
- **[doc/HIERARCHICAL_GENERATION.md](doc/HIERARCHICAL_GENERATION.md)** - Hierarchical DICOM generation
- **[test/README.md](test/README.md)** - Test scripts documentation

### Developer Documentation
- **[doc/DEVELOPER_GUIDE_PRESETS.md](doc/DEVELOPER_GUIDE_PRESETS.md)** - Developer guide for Server Presets
- **[doc/EXTERNAL_SCRIPT_USAGE.md](doc/EXTERNAL_SCRIPT_USAGE.md)** - Using DICOM Creator as a library
- **[doc/BUILD_INSTRUCTIONS.md](doc/BUILD_INSTRUCTIONS.md)** - Building the EXE
- **[doc/DISTRIBUTION_GUIDE.md](doc/DISTRIBUTION_GUIDE.md)** - Distribution guide

### Release Notes
- **[doc/CHANGELOG_v0.7.0.md](doc/CHANGELOG_v0.7.0.md)** - v0.7.0 release notes (Current)
- **[doc/CHANGELOG_v0.6.1.md](doc/CHANGELOG_v0.6.1.md)** - v0.6.1 release notes
- **[doc/CHANGELOG_v0.6.0.md](doc/CHANGELOG_v0.6.0.md)** - v0.6.0 release notes
- **[doc/CHANGELOG_v0.5.0.md](doc/CHANGELOG_v0.5.0.md)** - v0.5.0 release notes
- **[doc/CHANGELOG_v0.4.0.md](doc/CHANGELOG_v0.4.0.md)** - v0.4.0 release notes

### Running Tests
```bash
# Run all tests
python test/run_all_tests.py

# Run individual tests
python test/test_hierarchical_generation.py
python test/test_build.py
python test/verify_build.py
```

## Project Structure

```
dcmcreator/
├── src/
│   ├── app.py                      # Entry point
│   ├── appgui.py                   # Main GUI (v0.7.0)
│   ├── app_logic.py                # Core application logic
│   ├── import_helper.py            # LazyImport system
│   ├── dcm.py                      # DICOM creation/loading
│   ├── remote.py                   # DICOM C-STORE sending
│   ├── presets.py                  # Server Presets
│   ├── connection_validator.py     # Connection testing
│   ├── stress_tester.py            # Stress testing
│   ├── transmission_history.py     # Transmission tracking
│   ├── performance_benchmarking.py # Performance analysis
│   ├── parallel_transmission.py    # Multi-threaded sending
│   ├── random_dicom.py             # Test DICOM generator
│   ├── vr_validator.py             # VR validation
│   ├── validation_dialog.py        # Validation UI
│   ├── tag_dialog.py               # Tag viewer UI
│   ├── tls_dialog.py               # TLS settings dialog
│   └── dcmlogger.py                # Logging setup
├── test/                           # Test scripts
│   ├── test_build.py
│   ├── test_hierarchical_generation.py
│   ├── test_tag_viewer.py
│   ├── verify_build.py
│   ├── run_all_tests.py
│   └── README.md
├── examples/                       # Example scripts
├── doc/                            # Documentation
├── dist/                           # Distribution EXE
├── build.py                        # Build script
├── build.bat                       # Windows build script
├── dcmcreator.spec                 # PyInstaller config
├── create_icon.py                  # Icon generator
├── requirements.txt                # Runtime dependencies
├── build-requirements.txt          # Build dependencies
├── .gitignore                      # Git ignore (includes certificates)
└── README.md                       # This file
```

## Version History

### v0.7.0 (March 2026) - Current
- SSL/TLS certificate support for secure DICOM transmission
- Enhanced security with certificate file protection in `.gitignore`
- Improved TLS settings dialog with certificate configuration
- Documentation cleanup and streamlining
- Better error handling for SSL/TLS operations

### v0.6.1 (February 2026)
- Fixed LazyImport class loading for ConnectionValidator
- Enhanced error reporting and logging
- Improved module loading reliability
- 100% backward compatible with v0.6.0

### v0.6.0 (January 2025)
- Real-time VR validation system
- Validation report dialogs
- DICOMDIR support
- Private tag preservation
- Pre-save and pre-send validation

### v0.5.0 (January 2025)
- Enhanced LazyImport system
- Better class detection for modules
- Improved module loading reliability

### v0.4.0 (December 2024)
- Connection testing and validation
- Stress testing capabilities
- Transmission history tracking
- Performance benchmarking
- Parallel transmission manager

### v0.3.0 (November 2024)
- Server Presets management
- Tag Viewer with search/export
- VR Validator
- Random DICOM Generator

### v0.2.0 (October 2024)
- Remote DICOM transmission (C-STORE)
- DICOM file loading and organization
- Image loading and preview

### v0.1.0 (September 2024)
- Initial release
- Basic DICOM creation
- Patient/Study/Series metadata

## Author

Written by **Piotr Rozentreter**

## License

MIT License. See `LICENSE` for details.

## Support & Contributing

- **GitHub**: https://github.com/piotrrozentreter/dcmcreator
- **Issues**: Report bugs via GitHub Issues

## Troubleshooting

### EXE Won't Start
- Windows may block unsigned executables - click "More info" → "Run anyway"
- Check antivirus software settings
- Run from command line for error messages: `"DICOM Creator.exe"`

### Connection Issues
- Use **Connection Test** tab to validate server connectivity
- Check firewall and network settings
- Verify server IP and port are correct
- Try saving and loading a Server Preset

### SSL/TLS Certificate Issues (v0.7.0)
- Ensure certificate files are in correct format (PEM, CRT, KEY, etc.)
- Verify certificate paths in TLS Settings dialog
- Check that certificates are valid and not expired
- Review error messages for specific certificate validation issues

### Validation Issues
- Check that `src/VR.xml` exists in your installation
- Review validation error messages for specific issues
- Common issues: incorrect date format (YYYYMMDD), invalid VR values
- Fields with warnings can still be saved if needed

### Dependencies Missing
- Ensure Python 3.9+ is installed
- Run `pip install -r requirements.txt` to install dependencies
- For building: `pip install -r build-requirements.txt`

### Module Loading Issues
- Check log files for detailed error messages
- Verify all dependencies are installed
- Try reinstalling: `pip install -r requirements.txt --force-reinstall`
- Update to latest version for LazyImport fixes

---

**Happy DICOM Creating! 🏥**

