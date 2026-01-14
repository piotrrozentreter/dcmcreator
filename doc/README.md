# DICOM Creator v0.3.1

A professional DICOM file creation, editing, and transmission tool with comprehensive testing and validation capabilities.

## ? Features

### Core Features
- **DICOM Metadata Management** - Create and edit patient, study, and series metadata
- **Image Support** - Load and preview images (PNG, JPG, BMP) as DICOM pixel data
- **DICOM File Operations** - Load, save, and organize DICOM files and folders
- **Remote Transmission** - Send DICOM files to remote DICOM SCP servers using C-STORE
- **Server Presets** - Save and manage server connection profiles

### Advanced Testing System (v0.3.1)

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
- **Bulk Generation** - Generate multiple files with configurable sizes
- **Integrated Testing** - Generate and immediately send test files

## ?? Quick Start

### Installation
```bash
git clone https://github.com/piotrrozentreter/dcmcreator.git
cd dcmcreator
pip install -r requirements.txt
```

### Running the Application
```bash
python src/app.py
```

## ?? 13 Application Tabs

| Tab | Purpose |
|-----|---------|
| **Patient** | Patient metadata (name, ID, age, sex, etc.) |
| **Study** | Study metadata (date, description, accession) |
| **Series/Modality** | Series metadata (modality, description, protocol) |
| **Image** | Image loading and preview |
| **Load DICOM** | Load and browse DICOM files/folders |
| **Save** | Save DICOM files |
| **Remote** | Configure server and send DICOM |
| **Test/Generate** | Generate test DICOMs and transmission tests |
| **Connection Test** | Validate server connectivity |
| **Stress Test** | Simulate high-load scenarios |
| **Transmission History** | Track and analyze transmission history |
| **Benchmarking** | Performance analysis and reporting |
| **Parallel Send** | Multi-threaded transmission management |

## ?? Testing System

### Test Execution Workflow

1. **Connection Validation**
   ```
   Connection Test Tab ? Test TCP/Quality/Latency
   ```

2. **DICOM Generation**
   ```
   Test/Generate Tab ? Generate DICOMs ? Creates test files
   ```

3. **Stress Testing**
   ```
   Stress Test Tab ? Create Plan ? Start Test ? Analyze Results
   ```

4. **Transmission**
   ```
   Test/Generate Tab ? Send All Generated ? Transmission History
   ```

### Quick Test Execution

See `doc/QUICK_TEST_EXECUTION_GUIDE.md` for step-by-step testing procedures.

See `doc/WHERE_TO_RUN_TESTS.md` for recommended test environments.

## ?? Documentation

### Getting Started
- [Getting Started Guide](doc/GETTING_STARTED.md)
- [Build Instructions](doc/BUILD_INSTRUCTIONS.md)

### Features & Usage
- [Index & Navigation](doc/INDEX.md)
- [Server Presets Guide](doc/SERVER_PRESETS.md)
- [Random DICOM Generator](doc/RANDOM_DICOM_GENERATOR.md)
- [Quick Start - Presets](doc/QUICK_START_PRESETS.md)
- [Quick Start - DICOM Generator](doc/QUICK_START_RANDOM_DICOM.md)

### Testing & Development
- [Complete Test Execution Reference](doc/COMPLETE_TEST_EXECUTION_REFERENCE.md)
- [Quick Test Execution Guide](doc/QUICK_TEST_EXECUTION_GUIDE.md)
- [Where to Run Tests](doc/WHERE_TO_RUN_TESTS.md)
- [Developer Guide - Presets](doc/DEVELOPER_GUIDE_PRESETS.md)

### Project Info
- [Project Structure](doc/ORGANIZATION.md)
- [Changelog](doc/CHANGELOG_v0.3.0.md)
- [Distribution Guide](doc/DISTRIBUTION_GUIDE.md)

## ?? System Requirements

- **Python** 3.7+
- **pydicom** - DICOM file handling
- **Pillow** - Image processing
- **numpy** - Numerical operations
- **pynetdicom** - DICOM networking (optional, for remote send)

## ?? Project Structure

```
dcmcreator/
??? src/
?   ??? app.py                          # Main application entry point
?   ??? appgui.py                       # GUI implementation (13 tabs)
?   ??? dcm.py                          # DICOM operations
?   ??? presets.py                      # Server presets manager
?   ??? random_dicom.py                 # Test DICOM generator
?   ??? connection_validator.py         # Connection testing
?   ??? stress_tester.py                # Stress testing
?   ??? transmission_history.py         # Transmission tracking
?   ??? performance_benchmarking.py     # Performance testing
?   ??? parallel_transmission.py        # Parallel sending
?   ??? dcmlogger.py                    # Logging utilities
??? doc/                                # Complete documentation
??? requirements.txt                    # Dependencies
??? README.md                           # This file
```

## ?? Use Cases

### Clinical Testing
- Validate DICOM SCP server connectivity
- Test remote DICOM transmission
- Performance benchmarking under load

### Development
- Generate test DICOM files
- Stress test DICOM servers
- Performance analysis and optimization

### Quality Assurance
- Transmission history tracking
- Success rate monitoring
- Latency and throughput analysis

## ?? Key Metrics

- **Transmission Tracking** - Track all sent/received DICOMs
- **Performance Analysis** - Measure latency, throughput, success rates
- **Stress Testing** - Simulate up to 50 files/second
- **Parallel Performance** - Up to 10x improvement with worker threads

## ?? Version History

### v0.3.1 (Current)
- ? Connection Testing System
- ? Stress Testing Framework
- ? Transmission History Tracking
- ? Performance Benchmarking
- ? Parallel Transmission Manager
- ? Complete Test Execution Reference

### v0.3.0
- DICOM creation and editing
- Server presets management
- Remote DICOM transmission
- Random DICOM generator

## ?? Contributing

For development guidelines, see `doc/DEVELOPER_GUIDE_PRESETS.md`.

## ?? License

See LICENSE file for details.

## ?? Author

Written by Piotr Rozentreter  
© 2025-2026 Hyland

---

## ?? Next Steps

1. **First Time Users** ? Read [Getting Started Guide](doc/GETTING_STARTED.md)
2. **Test System Users** ? Read [Complete Test Execution Reference](doc/COMPLETE_TEST_EXECUTION_REFERENCE.md)
3. **Developers** ? Read [Developer Guide](doc/DEVELOPER_GUIDE_PRESETS.md)
4. **Deployment** ? Read [Distribution Guide](doc/DISTRIBUTION_GUIDE.md)

