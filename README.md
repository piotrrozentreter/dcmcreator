# DICOM Creator

A professional DICOM file creation, editing, and transmission tool with comprehensive testing, validation, and performance analysis capabilities.

## Features

### Core Features
- **DICOM Metadata Management** - Create and edit patient, study, and series metadata
- **Image Support** - Load and preview images (PNG, JPG, BMP) as DICOM pixel data
- **DICOM File Operations** - Load, save, and organize DICOM files and folders
- **Remote Transmission** - Send DICOM files to remote DICOM SCP servers using C-STORE
- **Server Presets** - Save and manage server connection profiles
- **DICOM Tag Viewer** - View all DICOM tags including private tags with search and export
- **VR Validator** - Validate DICOM data against Value Representation specifications

### Advanced Features (v0.3+)

#### **Server Presets**
- Save frequently used DICOM server configurations
- Quick load and apply with one click
- Persistent storage across sessions
- Multi-server profile management

#### **Connection Testing & Validation**
- TCP connection validation to DICOM servers
- Connection quality assessment
- Latency variation analysis
- Real-time network performance metrics

#### **Stress Testing**
- Load simulation and capacity planning
- Configurable test parameters (files/sec, duration, file size)
- Multi-worker support for parallel testing
- Performance metrics collection

#### **Transmission History & Analytics**
- Track all DICOM transmissions with timestamps
- Success/failure statistics and reporting
- Throughput analysis
- JSON export for external reporting

#### **Performance Benchmarking**
- File size performance analysis
- Latency benchmarking
- Throughput measurements
- Performance trend visualization

#### **Parallel Transmission**
- Multi-threaded transmission manager
- 1-10 configurable worker threads
- 3-5x speed improvement over sequential sending
- Real-time progress tracking

#### **Test Data Generation**
- Random DICOM Generator - Create test files with random metadata
- Bulk generation with configurable sizes
- Integrated testing workflow
- Immediate test and send capabilities

## Quick Start

### Option 1: Run as EXE (Windows, No Python Required)

**Download & Extract:**
1. Get the `DICOM Creator` folder from `dist/`
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

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/app.py
```

**Dependencies:**
- `pydicom` - DICOM file handling
- `pynetdicom` >= 2.0.0 - DICOM network communication
- `pillow` (PIL) - Image processing
- `numpy` - Numerical arrays

## Building Your Own EXE

Want to build a standalone executable yourself?

### Build Requirements

Starting with **v0.4.0+**, the build includes additional optional modules for testing. Make sure you have all dependencies:

```bash
# Install build dependencies (updated for v0.4.0+)
pip install -r build-requirements.txt
```

**build-requirements.txt** now includes:
- `PyInstaller>=6.0.0` - EXE builder
- `pillow>=10.0.0` - Image processing
- `pydicom>=2.4.0` - DICOM library (analysis)
- `pynetdicom>=2.0.0` - Network DICOM (analysis)
- `numpy>=1.20.0` - Array processing (analysis)

### Build Process

```bash
# Create icon (generates app.ico)
python create_icon.py

# Build the executable (includes all optional modules)
python build.py
```

Your standalone EXE will be created in `dist/DICOM Creator/` with:
- ? All core DICOM features
- ? All connection testing features (NEW in v0.4.0+)
- ? All stress testing features (NEW in v0.4.0+)
- ? All transmission history features (NEW in v0.4.0+)
- ? All performance benchmarking features (NEW in v0.4.0+)
- ? All parallel transmission features (NEW in v0.4.0+)

**See [doc/BUILD_INSTRUCTIONS.md](doc/BUILD_INSTRUCTIONS.md) for detailed build guide.**

### What's Bundled (v0.4.0+)

The build now automatically includes:

| Component | Size | Purpose |
|-----------|------|---------|
| PyDICOM | ~40 MB | DICOM file handling |
| PyNetDICOM | ~30 MB | Network DICOM C-STORE |
| NumPy | ~30 MB | Array processing |
| PIL/Pillow | ~10 MB | Image processing |
| Application | ~5 MB | GUI and logic |
| **Total** | **150-200 MB** | Uncompressed |
| **ZIP** | **60-70 MB** | Compressed distribution |

All optional test modules are automatically included in the build - no extra configuration needed!

## Usage

### Creating DICOM Files
1. Fill in Patient, Study, Series metadata
2. (Optional) Load an image via Image tab
3. Click "Save" to save as DICOM

### Loading DICOM Files
1. Go to "Load DICOM" tab
2. Click "Load DICOM File(s)" or "Load DICOM Folder"
3. Select studies/series from the tree
4. Metadata auto-populates in the forms

### Sending to Remote Server
1. Fill in Server IP/hostname and Port
2. Optionally adjust AE Titles
3. Click "Send All Loaded DICOM"
4. Monitor progress in Messages area

#### Using Server Presets
1. Go to "Remote" tab
2. (Optional) Select a preset from dropdown to auto-load settings
3. Or manually enter server details and click "Save Current" to save as preset
4. Select preset and click "Load" or simply select and it auto-applies
5. Click "Send All Loaded DICOM"

### Testing & Validation

#### DICOM Data Validation & Inspection
- Go to "File" menu ? "Validate" to check current form data
- Go to "DICOM" menu ? "View VRs" to browse DICOM Value Representations
- Go to "DICOM" menu ? "View All Tags" to inspect all tags in a DICOM file:
  - View all public and private tags
  - Search and filter tags
  - Export tags to text file
  - View tag statistics
  - Color-coded private tags

#### Connection Testing
- Go to "Connection Test" tab
- Enter server details
- Click "Test Connection" to validate
- Review latency and connection quality metrics

#### Stress Testing
- Go to "Stress Test" tab
- Configure test parameters (number of files, duration, worker threads)
- Click "Start Stress Test"
- Monitor real-time performance metrics

#### Transmission History
- Go to "Transmission History" tab
- View all past transmissions
- See success/failure rates
- Export data as JSON

#### Performance Benchmarking
- Go to "Performance Benchmark" tab
- Run benchmarks for file size and latency analysis
- Review throughput trends

#### Parallel Transmission
- Go to "Parallel Transmission" tab
- Configure number of worker threads (1-10)
- Select files and destination
- Transmit with improved performance

### Loading Images
1. Go to Image tab
2. Click "Load Image"
3. Select PNG, JPG, or BMP file
4. Image converts to grayscale and displays preview

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

### User Documentation
- **[doc/INDEX.md](doc/INDEX.md)** - Complete documentation index and navigation
- **[doc/QUICK_START_TAG_VIEWER.md](doc/QUICK_START_TAG_VIEWER.md)** - Tag Viewer quick start guide
- **[doc/TAG_VIEWER_FEATURE.md](doc/TAG_VIEWER_FEATURE.md)** - Complete Tag Viewer documentation
- **[doc/QUICK_START_PRESETS.md](doc/QUICK_START_PRESETS.md)** - Server Presets quick start guide
- **[doc/SERVER_PRESETS.md](doc/SERVER_PRESETS.md)** - Comprehensive Server Presets documentation
- **[doc/QUICK_START_RANDOM_DICOM.md](doc/QUICK_START_RANDOM_DICOM.md)** - Random DICOM generator quick start
- **[doc/RANDOM_DICOM_GENERATOR.md](doc/RANDOM_DICOM_GENERATOR.md)** - Detailed DICOM generator guide

### Advanced Testing Guides
- **[doc/PARALLEL_TRANSMISSION_GUIDE.md](doc/PARALLEL_TRANSMISSION_GUIDE.md)** - Parallel transmission setup and tuning
- **[doc/QUICK_TEST_EXECUTION_GUIDE.md](doc/QUICK_TEST_EXECUTION_GUIDE.md)** - Testing workflow guide
- **[doc/COMPLETE_TEST_EXECUTION_REFERENCE.md](doc/COMPLETE_TEST_EXECUTION_REFERENCE.md)** - Complete testing reference

### Developer Documentation
- **[doc/DEVELOPER_GUIDE_PRESETS.md](doc/DEVELOPER_GUIDE_PRESETS.md)** - Developer guide for Server Presets
- **[doc/EXTERNAL_SCRIPT_USAGE.md](doc/EXTERNAL_SCRIPT_USAGE.md)** - Using DICOM Creator as a library

### Build & Deployment
- **[doc/BUILD_INSTRUCTIONS.md](doc/BUILD_INSTRUCTIONS.md)** - Complete guide to building the EXE
- **[doc/DISTRIBUTION_GUIDE.md](doc/DISTRIBUTION_GUIDE.md)** - Distribution and deployment guide

### Additional Resources
- **[examples/](examples/)** - Example scripts for common tasks
- **[doc/QUICK_START_TAG_VIEWER.md](doc/QUICK_START_TAG_VIEWER.md)** - Tag Viewer 5-minute guide
- **[doc/TAG_VIEWER_FEATURE.md](doc/TAG_VIEWER_FEATURE.md)** - Complete Tag Viewer documentation
- **[doc/CHANGELOG_v0.4.0.md](doc/CHANGELOG_v0.4.0.md)** - Release notes for v0.4.0
- **[doc/CHANGELOG_v0.3.0.md](doc/CHANGELOG_v0.3.0.md)** - Release notes for v0.3.0+

## Project Structure

```
dcmcreator/
??? src/
?   ??? app.py                      (Entry point)
?   ??? appgui.py                   (Main GUI application)
?   ??? app_logic.py                (Core application logic)
?   ??? dcm.py                      (DICOM creation/loading)
?   ??? remote.py                   (DICOM C-STORE sending)
?   ??? presets.py                  (Server Presets management)
?   ??? connection_validator.py     (Connection testing)
?   ??? stress_tester.py            (Stress testing)
?   ??? transmission_history.py     (Transmission tracking)
?   ??? performance_benchmarking.py (Performance analysis)
?   ??? parallel_transmission.py    (Multi-threaded sending)
?   ??? random_dicom.py             (Test DICOM generator)
?   ??? test_runner.py              (Testing framework)
?   ??? dcmlogger.py                (Logging setup)
??? examples/                       (Example scripts for features)
??? doc/                            (Comprehensive documentation)
??? dist/                           (Distribution EXE folder)
??? build.py                        (Python build script)
??? build.bat                       (Windows build script)
??? dcmcreator.spec                 (PyInstaller configuration)
??? create_icon.py                  (Icon generator)
??? requirements.txt                (Runtime dependencies)
??? build-requirements.txt          (Build dependencies)
??? README.md                       (This file)
```

## Version

- **Current Version**: 0.4.0
- **Release Date**: 2025-2026
- **Status**: Active Development

## Author

Written by **Piotr Rozentreter** for **Hyland**

## License

[Insert License Information Here]

## Support & Contributing

- **GitHub**: https://github.com/piotrrozentreter/dcmcreator
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: GitHub Discussions for questions

## Troubleshooting

### EXE Won't Start
- Windows may block unsigned executables - click "More info" -> "Run anyway"
- Check antivirus software settings
- Run from command line for error messages

### Slow Startup
- First run takes 15-30 seconds (unpacking files)
- Subsequent runs are faster (5-10 seconds)

### Dependencies Missing
- Ensure Python 3.9+ is installed
- Run `pip install -r requirements.txt` to install dependencies
- Check that pydicom and pynetdicom are properly installed

### Connection Issues
- Use "Connection Test" tab to validate server connectivity
- Check firewall and network settings
- Verify server IP and port are correct
- Try saving and loading a Server Preset
