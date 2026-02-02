# DICOM Creator v0.6.0

A professional DICOM file creation, editing, and transmission tool with comprehensive validation, testing, and transmission capabilities.

## Quick Links

- **[Main README](../README.md)** - Complete project documentation
- **[INDEX.md](INDEX.md)** - Full documentation index
- **[Changelog v0.6.0](CHANGELOG_v0.6.0.md)** - Release notes and new features
- **[Build Instructions](BUILD_INSTRUCTIONS.md)** - How to build the EXE

## Features

### Core Features
- **DICOM Metadata Management** - Create and edit patient, study, and series metadata
- **Image Support** - Load and preview images (PNG, JPG, BMP) as DICOM pixel data
- **DICOM File Operations** - Load, save, and organize DICOM files and folders
- **Remote Transmission** - Send DICOM files to remote DICOM SCP servers using C-STORE
- **Server Presets** - Save and manage server connection profiles

### Data Validation & Compliance (v0.6.0)

#### **Real-Time VR Validation**
- Comprehensive validation of all DICOM data elements
- Field-level validation with specific error messages
- Support for all DICOM Value Representation types
- Reference to DICOM PS3.6 standard

#### **Validation Report Dialogs**
- Interactive validation dialogs with error details
- Color-coded errors vs warnings
- Remediation suggestions for invalid values
- Options to review and continue or abort

#### **Load-Time Validation**
- Automatic validation when loading DICOM files
- Detailed error reporting in validation dialogs
- Option to continue with warnings or cancel

#### **Pre-Save Validation**
- Validation check before saving DICOM files
- Prevents saving invalid DICOM files
- Clear error messages with how to fix

#### **Pre-Send Validation**
- Validation before transmitting to remote server
- Ensures server receives compliant DICOM
- Automatic validation before transmission

#### **DICOMDIR Support**
- Load and process DICOMDIR files
- Automatic expansion of directory references
- Support for hierarchical structures

#### **Private Tag Preservation**
- Maintains manufacturer-specific tags during save
- Ensures data integrity through edit/save cycles
- Group Length cleanup for DICOM 2008+ compliance

### Advanced Testing System (v0.3.1+)

#### **Connection Testing Tab**
- TCP connection validation
- Connection quality assessment  
- Latency variation analysis
- Real-time performance metrics

#### **Stress Testing Tab**
- Load simulation and planning
- Configurable test parameters (files/sec, duration, file size)
- Multi-worker support for parallel testing
- Performance metrics collection

#### **Transmission History Tab**
- Track all DICOM transmissions
- Success/failure statistics
- Throughput analysis
- JSON export for reporting

#### **Performance Benchmarking Tab**
- File size performance analysis
- Latency benchmarking
- Throughput measurements
- Performance trend analysis

#### **Parallel Transmission Tab**
- Multi-threaded transmission manager
- 1-10 configurable worker threads
- 3-5x speed improvement over sequential
- Real-time progress tracking

### Test Data Generation
- **Random DICOM Generator** - Create test DICOM files with random metadata
- **Hierarchical Generation** - Patient → Study → Series → Instances structure
- **Bulk Generation** - Generate multiple files with configurable sizes
- **Integrated Testing** - Generate and immediately send test files

### DICOM Inspection & Analytics
- **DICOM Tag Viewer** - View all DICOM tags including private tags
- **Tag Search & Filter** - Find tags by name, keyword, or number
- **Tag Export** - Export tag information to text files
- **VR Information** - Display VR types and constraints for each tag

---

## What's New in v0.6.0

### Validation System (Major Feature)

**Real-Time VR Validation:**
- Validates form data against DICOM standards
- Comprehensive field-level error detection
- Integration with all save/send workflows

**New Dialogs:**
- Validation Report Dialog for detailed error information
- Load Validation Dialog for DICOM file loading
- Pre-Save Validation for file operations
- Pre-Send Validation for remote transmission

**DICOM Compliance:**
- Full DICOM PS3.6 standard support
- VR type enforcement
- Value range validation
- Format compliance checking

### DICOM Operations

**DICOMDIR Support:**
- Load DICOMDIR files with automatic reference expansion
- Hierarchical dataset organization
- Full compatibility with DICOM directory structures

**Private Tag Preservation:**
- Maintains all manufacturer-specific tags
- Ensures data integrity through edit cycles
- Group Length cleanup for modern systems

### User Interface

**Tab Visibility Management:**
- Hide/show test tabs via View menu
- Cleaner UI with optional features
- Quick "Show All" / "Hide Test Tabs" options

**Enhanced Context Menus:**
- Right-click on DICOM instances
- Quick image viewing
- Easy navigation to Image tab

**Better Error Messages:**
- Clear, actionable error descriptions
- Reference to DICOM standards
- Suggestions for fixing issues

**Improved Image Preview:**
- Better handling of various dimensions
- Improved resizing and aspect ratio
- Support for more image formats

### Developer Features

**Enhanced LazyImport:**
- Better detection of main classes in multi-class modules
- Explicit class selection support
- Improved error diagnostics

**Better Error Handling:**
- Clear diagnostics when modules unavailable
- Graceful fallback mechanisms
- No crashes due to missing optional features

**Enhanced Logging:**
- More detailed debug information
- Better error context
- Improved troubleshooting data

---

## System Requirements

### Minimum Requirements
- Python 3.9 or higher
- Windows 7+, macOS 10.14+, or Linux
- 500 MB RAM minimum
- 100 MB disk space

### Recommended Requirements
- Python 3.10+
- Windows 10+, macOS 11+, or modern Linux
- 1 GB+ RAM
- 500 MB disk space for tests/logs

### Dependencies
- `pydicom >= 2.4.0` - DICOM library
- `pynetdicom >= 2.0.0` - DICOM network communication
- `pillow >= 10.0.0` - Image processing
- `numpy >= 1.20.0` - Array operations

---

## Quick Start

### Option 1: Windows EXE (Recommended for Windows Users)

1. Download from releases
2. Extract to any folder
3. Run `DICOM Creator.exe`
4. No installation required!

### Option 2: Run from Python

```bash
# Install
git clone https://github.com/piotrrozentreter/dcmcreator
cd dcmcreator
pip install -r requirements.txt

# Run
python src/app.py
```

---

## Documentation Structure

```
doc/
├── INDEX.md                              ← START HERE
├── CHANGELOG_v0.6.0.md                   ✨ CURRENT - New validation system
├── CHANGELOG_v0.5.0.md                   - LazyImport enhancements
├── CHANGELOG_v0.4.0.md                   - Testing features
├── CHANGELOG_v0.3.0.md                   - Server presets
│
├── User Guides:
│   ├── QUICK_START_PRESETS.md
│   ├── QUICK_START_TAG_VIEWER.md
│   ├── QUICK_START_RANDOM_DICOM.md
│   ├── SERVER_PRESETS.md
│   ├── TAG_VIEWER_FEATURE.md
│   ├── RANDOM_DICOM_GENERATOR.md
│   ├── QUICK_TEST_EXECUTION_GUIDE.md
│   ├── COMPLETE_TEST_EXECUTION_REFERENCE.md
│   └── PARALLEL_TRANSMISSION_GUIDE.md
│
├── Build & Deployment:
│   ├── BUILD_INSTRUCTIONS.md
│   ├── BUILD_QUICK_REFERENCE.md
│   └── DISTRIBUTION_GUIDE.md
│
└── Developer:
    ├── DEVELOPER_GUIDE_PRESETS.md
    └── EXTERNAL_SCRIPT_USAGE.md
```

---

## Common Tasks

### Validate DICOM Data (NEW in v0.6.0)
```
1. Fill in Patient/Study/Series metadata
2. File Menu → Validate
3. Review validation report
4. Fix any errors or continue with warnings
5. Save or Send DICOM
```

### View DICOM Tags
```
1. Load a DICOM file
2. DICOM Menu → View All Tags
3. Search/filter tags
4. Export to text if needed
```

### Transmit to Server
```
1. Load or create DICOM
2. Go to Remote tab
3. Enter server IP and port
4. Click Send All Loaded DICOM
5. Monitor progress in Messages area
```

### Run Connection Test
```
1. Go to Connection Test tab
2. Enter server IP and port
3. Click "Test TCP" button
4. Review results
```

### Generate Test DICOMs
```
1. Go to Test/Generate tab
2. Set hierarchy (studies/series/instances)
3. Select output directory
4. Click "Generate DICOMs"
5. Files are created and ready to send
```

---

## Troubleshooting

### Common Issues

**"VRValidator not available"**
- Check that `src/VR.xml` exists
- Rebuild or reinstall the application

**"Connection Validator could not be loaded"**
- Update to v0.5.0+
- Verify `connection_validator.py` is present

**"Validation errors found" (v0.6.0)**
- Review error details in validation dialog
- Common: Date format (YYYYMMDD), invalid VR values
- Fix issues or click "Continue" if warnings only

**Module loading issues**
- Check log files for detailed errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Verify all required files are present

---

## Version Information

| Version | Date | Status | Key Features |
|---------|------|--------|--------------|
| **0.6.0** | Jan 2025 | **Current** | ✨ VR Validation, DICOMDIR, dialogs |
| 0.5.0 | Jan 2025 | Stable | LazyImport improvements |
| 0.4.0 | Dec 2024 | Stable | Connection/Stress testing |
| 0.3.0 | Nov 2024 | Stable | Server presets, Tag viewer |
| 0.2.0 | Oct 2024 | Legacy | Remote transmission |
| 0.1.0 | Sep 2024 | Legacy | Basic DICOM creation |

---

## Support

- **Documentation**: See [INDEX.md](INDEX.md)
- **GitHub Issues**: Report bugs
- **GitHub Discussions**: Ask questions
- **Changelog**: [CHANGELOG_v0.6.0.md](CHANGELOG_v0.6.0.md)

---

**Happy DICOM Creating! 🏥📊**

