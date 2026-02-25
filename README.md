# DICOM Creator

A professional DICOM file creation, editing, and transmission tool with comprehensive testing, validation, and performance analysis capabilities.

![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [What's New in v0.9.0](#whats-new-in-v090)
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

### Query/Retrieve PACS Features (NEW)
- **C-FIND Query** - Search for patients, studies, and series on remote PACS
- **Multiple Query Levels** - Patient, Study, Series, and Image level searches
- **Query Models** - Support for Patient Root and Study Root Query/Retrieve models
- **Search Filters** - Filter by patient name, ID, date range, modality, and more
- **C-MOVE Retrieval** - Download selected studies/series from PACS to local storage
- **C-GET Retrieval** - Direct DICOM retrieval with automatic storage
- **Query Results Display** - Hierarchical view of query results (Patient → Study → Series → Images)
- **Batch Operations** - Download multiple studies in parallel

### Hospital Integration Features (NEW)
- **HL7 ADT Parser** - Parse admission/discharge/transfer messages for patient data
- **HL7 ORM Parser** - Extract order information for DICOM studies
- **HL7 ORU Builder** - Create result messages from DICOM studies
- **MLLP Protocol** - Secure hospital standard messaging protocol
- **FHIR R4 Client** - Query and update patient resources from FHIR servers
- **Automatic Mapping** - Convert between HL7, FHIR, and DICOM formats
- **EHR Integration** - Bidirectional communication with hospital systems

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

## What's New in v0.9.0

**Release Date**: January 2025

### 🔍 Query/Retrieve PACS (NEW)
- Full C-FIND implementation for querying remote PACS
- C-MOVE and C-GET support for retrieving studies
- Multi-level queries (Patient, Study, Series, Image)
- Support for both Patient Root and Study Root models
- Advanced filtering and hierarchical result display
- Parallel retrieval for improved performance

### 🏥 HL7/FHIR Hospital Integration (NEW)
- Complete HL7 v2.x message parsing (ADT, ORM, ORU)
- FHIR R4 REST client for patient management
- MLLP protocol for secure hospital communication
- Automatic demographic mapping to DICOM metadata
- Bidirectional EHR ↔ DICOM synchronization
- Support for multiple healthcare integration patterns

### 🔒 Enhanced Security
- SSL/TLS support for Query/Retrieve operations
- Certificate-based secure transmission
- MLLP protocol encryption support
- Enhanced TLS settings for PACS connections

### 📖 Documentation Improvements
- Comprehensive Query/Retrieve usage guide
- HL7 integration examples and tutorials
- Updated all version references to 0.9.0
- Improved security and privacy documentation

### ✅ Additional Enhancements
- Better error handling and logging for network operations
- Improved connection quality assessment
- Enhanced TLS configuration management
- Better user guidance for enterprise features

### 📋 Previous Releases
- **v0.8.0** - Enhancements and bug fixes
- **v0.7.0** - Major update with SSL/TLS support

**Full Details:** See [CHANGELOG_v0.9.0.md](doc/CHANGELOG_v0.9.0.md)

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

### Querying PACS (NEW)

1. Go to **Query/Retrieve** tab
2. Enter PACS server IP, port, and AE Titles
3. Select query level: **Patient**, **Study**, **Series**, or **Image**
4. Enter search criteria:
   - **Patient Name** (wildcard: `*`)
   - **Patient ID** (exact or prefix)
   - **Study Date** (range or specific date)
   - **Modality** (CT, MR, XC, etc.)
5. Click **Query PACS**
6. Review results in hierarchical tree view
7. Select studies/series and click **Retrieve (C-GET)** or **Retrieve (C-MOVE)**

#### Example Queries
- Find all CT studies from January 2025: Set Study Date range, Modality=CT
- Find patient by ID: Set Patient ID, click Query at Patient level
- Find all studies for a patient: Set Patient Name, click Query at Study level

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

### Hospital Integration with HL7 (NEW)

#### Receiving Patient Data from EHR
1. Go to **HL7** tab
2. Configure MLLP server settings (listening port)
3. Start listening for incoming HL7 messages
4. Received ADT messages auto-populate patient demographics
5. Data automatically maps to DICOM Patient form

#### Sending DICOM Results as HL7
1. Create or load DICOM study
2. Go to **HL7** tab → **Build ORU**
3. Review extracted patient and study information
4. Click **Send ORU Message** to transmit results to EHR
5. Monitor delivery status in history

#### FHIR Server Integration
1. Go to **HL7** tab → **FHIR Settings**
2. Enter FHIR server URL
3. Use **Get Patient** to retrieve patient demographics from FHIR server
4. Use **Post Patient** to create/update patient records
5. Automatic conversion between FHIR and DICOM formats

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
- Optional: Network access for PACS, FHIR servers, and HL7 MLLP connections

### For Python
- Python 3.9+
- Cross-platform: Windows, macOS, Linux
- 500 MB disk space
- 500 MB RAM minimum

### Network Requirements
- For PACS Query/Retrieve: DICOM C-FIND, C-MOVE, C-GET support
- For HL7 Integration: Port access for MLLP protocol (typically port 2575)
- For FHIR Integration: HTTPS access to FHIR server
- For remote transmission: Port 104 (default DICOM) or custom ports
- Optional: SSL/TLS certificates for secure connections

### Dependencies
All dependencies are automatically installed with:
```bash
pip install -r requirements.txt
```

**Core Libraries:**
- `pydicom>=2.4.0` - DICOM file handling and network operations
- `pynetdicom>=2.0.0` - DICOM network communication (C-STORE, C-FIND, C-MOVE, C-GET)
- `Pillow>=10.0.0` - Image processing (PNG, JPG, BMP)
- `numpy>=1.24.0` - Numerical array operations
- `requests>=2.28.0` - HTTP client for FHIR REST operations

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
- **[doc/QUERY_RETRIEVE_GUIDE.md](doc/QUERY_RETRIEVE_GUIDE.md)** - Query/Retrieve PACS guide (NEW)
- **[doc/CGET_CMOVE_GUIDE.md](doc/CGET_CMOVE_GUIDE.md)** - C-GET and C-MOVE implementation (NEW)
- **[doc/CGET_CMOVE_IMPLEMENTATION.md](doc/CGET_CMOVE_IMPLEMENTATION.md)** - C-GET/C-MOVE technical details (NEW)
- **[doc/HL7_INTEGRATION_GUIDE.md](doc/HL7_INTEGRATION_GUIDE.md)** - HL7 and hospital integration (NEW)
- **[doc/TLS_SETUP.md](doc/TLS_SETUP.md)** - SSL/TLS certificate setup

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
- **[doc/CHANGELOG_v0.9.0.md](doc/CHANGELOG_v0.9.0.md)** - v0.9.0 release notes (Current) - Query/Retrieve PACS and HL7 Integration
- **[doc/CHANGELOG_v0.8.0.md](doc/CHANGELOG_v0.8.0.md)** - v0.8.0 release notes
- **[doc/CHANGELOG_v0.7.0.md](doc/CHANGELOG_v0.7.0.md)** - v0.7.0 release notes
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

### v0.9.0 (February 2026) - Current
- Query/Retrieve PACS integration with C-FIND, C-MOVE, C-GET support
- HL7 v2.x message parsing (ADT, ORM, ORU)
- FHIR R4 REST client for patient management
- MLLP protocol support for hospital integration
- Multi-level PACS queries (Patient, Study, Series, Image)
- Advanced search filtering and hierarchical result display
- Parallel retrieval for improved performance
- Comprehensive documentation updates
- All character encoding issues resolved

### v0.8.0 (February 2026)
- Code refactoring and clean up
- Performance improvements
- Bug fixes and stability enhancements

### v0.7.0 (February 2026)
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

### v0.6.0 (January 2026)
- Real-time VR validation system
- Validation report dialogs
- DICOMDIR support
- Private tag preservation
- Pre-save and pre-send validation

### v0.5.0 (January 2026)
- Enhanced LazyImport system
- Better class detection for modules
- Improved module loading reliability

### v0.4.0 (December 2025)
- Connection testing and validation
- Stress testing capabilities
- Transmission history tracking
- Performance benchmarking
- Parallel transmission manager

### v0.3.0
- Server Presets management
- Tag Viewer with search/export
- VR Validator
- Random DICOM Generator

### v0.2.0
- Remote DICOM transmission (C-STORE)
- DICOM file loading and organization
- Image loading and preview

### v0.1.0
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

### Query/Retrieve PACS Issues (NEW)
- **Query returns no results**: Verify PACS AE Title matches server configuration
- **C-FIND fails**: Check PACS accepts Query/Retrieve operations
- **C-MOVE/C-GET fails**: Ensure storage SCP is configured and accessible
- **Timeout during retrieval**: Increase timeout setting or reduce dataset size
- **Connection refused**: Verify PACS firewall allows DICOM connections

### HL7 Integration Issues (NEW)
- **MLLP listener won't start**: Check port is not in use; try different port
- **ADT messages not parsing**: Verify message format is HL7 v2.x
- **No patient data populated**: Check PID segment exists in message
- **FHIR server connection fails**: Verify FHIR server URL and network access
- **ORU message delivery fails**: Check HL7 receiving system is accepting messages

### SSL/TLS Certificate Issues
- Ensure certificate files are in correct format (PEM, CRT, KEY, etc.)
- Certificate and key files must match
- Verify certificate is not expired
- Check certificate path is accessible
- Try testing certificate with **TLS Settings** dialog

