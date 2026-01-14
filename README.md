# DICOM Creator GUI App

A simple yet powerful GUI application to create, edit, and transmit DICOM files.

## Features

### Patient Metadata
- Patient Name, ID, Birth Date, Sex, Age, Weight, Height
- Extended fields: Family Name, Prefix, Given Name, Middle Name, Suffix
- Mother's Birth Name, Death DateTime

### Study Metadata
- Study Instance UID, Date, Time, Description
- Accession Number, Study ID
- Referring Physician, Reading Physician
- Reason for Study, Admitting Diagnoses, Patient Location

### Series Metadata
- Series Instance UID, Number, Date, Time
- Modality, Series Description
- Body Part Examined, Protocol Name
- Performing Physician, Operator's Name, Laterality

### Image & DICOM Operations
- Load images (PNG, JPG, BMP) and preview
- Save as DICOM files (.dcm)
- Load existing DICOM files
- Batch load DICOM folders
- DICOMDIR support
- Edit loaded DICOM metadata

### Remote DICOM Transmission
- Send DICOM to remote DICOM SCP servers
- C-STORE protocol support
- Live transmission progress
- Automatic association handling
- Per-instance transmission status

### Additional Features
- Centralized logging (console + dcmcreator.log)
- Confirmation dialogs for destructive operations
- Multi-bit depth image support (8-bit, 16-bit, etc.)
- Robust error handling with user-friendly messages

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

```bash
# Install build dependencies
pip install -r build-requirements.txt

# Create icon (generates app.ico)
python create_icon.py

# Build the executable
python build.py
```

Your standalone EXE will be created in `dist/DICOM Creator/`

**See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build guide.**

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

- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Complete guide to building the EXE
- **[BUILD_SUCCESS.md](BUILD_SUCCESS.md)** - Build details and troubleshooting
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide

## Project Structure

```
dcmcreator/
|-- src/
|   |-- app.py              (Entry point)
|   |-- appgui.py           (Main GUI application)
|   |-- dcm.py              (DICOM creation/loading)
|   |-- remote.py           (DICOM C-STORE sending)
|   +-- dcmlogger.py        (Logging setup)
|-- dist/                   (Distribution EXE folder)
|-- build.py                (Python build script)
|-- build.bat               (Windows build script)
|-- dcmcreator.spec         (PyInstaller configuration)
|-- create_icon.py          (Icon generator)
|-- requirements.txt        (Runtime dependencies)
|-- build-requirements.txt  (Build dependencies)
+-- README.md              (This file)
```

## Version

- **Current Version**: 0.2.4
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
- Normal for Python/PyInstaller applications

### Python Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python -c "import pydicom; import PIL; import numpy; print('All OK!')"
```

### DICOM Load Issues
- Ensure files are valid DICOM format
- Check file permissions
- Try loading single files before batch operations

## Performance Notes

- **Memory**: 150-200 MB typical usage
- **Startup**: 5-10 seconds (Python), 10-15 seconds (EXE first run)
- **Remote Send**: Depends on network speed and image size
- **Image Processing**: Real-time for typical medical images

## Related Tools

- [PyDICOM](https://github.com/pydicom/pydicom) - Python DICOM library
- [PyNetDICOM](https://github.com/pydicom/pynetdicom) - DICOM networking
- [DCMTK](https://dicom.offis.de/dcmtk.php.en) - Command-line DICOM tools

## Changelog

### v0.2.4 (Latest)
- Fixed logger initialization
- Improved DICOM pixel data handling (preserves bit depth)
- Enhanced remote send to always use current form values
- Improved image preview for unusual array shapes
- Better file filtering and DICOM detection
- Created standalone EXE builds
- Fixed image preview with proper PhotoImage reference handling
- Enhanced PIL/Pillow plugin support

### v0.2.3
- Previous version features

See commit history for full details.

---

**Ready to use! Download the EXE or run from Python source.**
