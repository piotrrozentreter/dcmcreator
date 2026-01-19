# Building DICOM Creator as an Executable

This guide explains how to build a standalone executable (.exe) file that can run on Windows computers without Python installed.

## Important: What to Distribute

**The build process now automatically creates a ZIP file!**

- [x] **Best option**: Use the auto-generated `DICOM Creator.zip` file
- [x] **Alternative**: Distribute the entire `dist\DICOM Creator\` folder
- [ ] **DON'T distribute**: Just the `DICOM Creator.exe` alone (needs libraries)

## Version 0.4.0+ Changes

Starting with v0.4.0, the build now includes **additional optional modules** for testing and performance analysis:

| Module | Features |
|--------|----------|
| **connection_validator** | Network connectivity testing |
| **stress_tester** | Load testing and stress simulation |
| **transmission_history** | Transmission tracking and statistics |
| **performance_benchmarking** | Performance measurements |
| **parallel_transmission** | Multi-threaded DICOM sending |

**Good news**: These are automatically bundled into the executable. No additional steps needed!

## Quick Start

### Option 1: Using Batch Script (Easiest on Windows)

1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```cmd
   cd C:\path\to\dcmcreator
   ```
3. Run the build script:
   ```cmd
   build.bat
   ```
4. Wait for the build to complete (takes 5-10 minutes)
5. **Two distribution options are created**:
   - `DICOM Creator.zip` (60-70 MB) - For email/upload
   - `dist\DICOM Creator\` folder (150-200 MB) - For direct sharing

### Option 2: Using Python Script

1. Open Command Prompt or PowerShell
2. Navigate to the project directory:
   ```cmd
   cd C:\path\to\dcmcreator
   ```
3. Run the build script:
   ```cmd
   python build.py
   ```
4. Wait for the build to complete
5. **Two distribution options are created**:
   - `DICOM Creator.zip` (60-70 MB) - For email/upload
   - `dist\DICOM Creator\` folder (150-200 MB) - For direct sharing

## What Gets Built

### Automatic ZIP Creation
The build script now automatically creates `DICOM Creator.zip` containing:
- `DICOM Creator.exe` - Main executable (~25 MB)
- `_internal\` - All Python libraries (required!) - PyDICOM, PyNetDICOM, NumPy, Pillow, etc.
- `src\` - Application source code
- **Total ZIP size**: 60-70 MB (compressed)

### Also Available
- **Distribution folder**: `dist\DICOM Creator\` (150-200 MB uncompressed)
- **For direct folder sharing** or USB distribution

### Compression Savings
- Folder size: 150-200 MB
- ZIP size: 60-70 MB
- **Compression: 55-65%**

## What's Included

### Core Features (Always Included)
- Patient/Study/Series metadata editing
- DICOM file creation and loading
- Image loading and preview
- Remote DICOM transmission (C-STORE)
- Server preset management

### New in v0.4.0+ (Now Bundled)
- **Connection Testing**: TCP connection verification, latency testing
- **Stress Testing**: Load testing with configurable parameters
- **Transmission History**: Track and analyze past transmissions
- **Performance Benchmarking**: Measure throughput and latency
- **Parallel Transmission**: Multi-threaded file sending (1-10 workers)

All test features are available via the **View** menu ? **Test Tabs**.

## Distribution

### Recommended: Use the ZIP File

**Best for:**
- Email distribution (small file)
- GitHub releases
- Website downloads
- Cloud storage uploads

**User instructions:**
1. Download `DICOM Creator.zip`
2. Extract anywhere
3. Double-click `DICOM Creator.exe`
4. Done!

### Alternative: Use the Folder

**Best for:**
- USB drives
- Network shares
- Direct folder copying
- Internal IT deployment

**User instructions:**
1. Copy `dist\DICOM Creator\` folder
2. Extract or copy to destination
3. Double-click `DICOM Creator.exe`
4. Done!

## Create a Compressed Archive (If Needed)

If the automatic ZIP wasn't created or you want to regenerate it:

```cmd
# Using Windows built-in compression
Right-click dist\DICOM Creator -> Send to -> Compressed (zipped) folder
# Creates DICOM Creator.zip (60-70 MB)

# Or using PowerShell
powershell -Command "Add-Type -AssemblyName 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('dist\DICOM Creator', 'DICOM Creator.zip')"

# Or using 7-Zip or WinRAR for even better compression
```

## Professional Installer (Optional)

For enterprise deployment, create an installer using NSIS:
- Includes uninstall functionality
- Creates Start Menu shortcuts
- Registers file associations
- Professional appearance

See [NSIS Documentation](https://nsis.sourceforge.io/) for details.

## Common Mistakes

### Mistake 1: Distributing just the EXE
```
WRONG: Send only DICOM Creator.exe
Result: Won't work! Missing _internal\ folder with libraries
```

### Solution 1: Use the ZIP file
```
CORRECT: Send DICOM Creator.zip
Result: Works perfectly! ZIP includes everything needed
```

### Mistake 2: Distributing just the EXE from ZIP
```
WRONG: Extract ZIP, then send only DICOM Creator.exe
Result: Won't work! Missing _internal\ folder
```

### Solution 2: Send the entire extracted folder or use ZIP as-is
```
CORRECT: Send DICOM Creator.zip directly (users extract)
or send entire dist\DICOM Creator\ folder
Result: Works perfectly!
```

## File Structure After Build

```
dcmcreator/
|-- DICOM Creator.zip              <-- AUTO-CREATED! Use this for distribution
|-- dist/
|   |-- DICOM Creator/              <-- ALTERNATIVE distribution folder
|       |-- DICOM Creator.exe       (Main executable)
|       |-- _internal/              <-- REQUIRED! All libraries
|       |   |-- pydicom/            (DICOM library - core functionality)
|       |   |-- pynetdicom/         (Network DICOM - transmission)
|       |   |-- PIL/                (Image processing)
|       |   |-- numpy/              (Array processing)
|       |   |-- [other DLLs]
|       |-- src/                    (Application source)
|-- build/                          (Temporary - can delete)
|-- dcmcreator.spec                 (Build configuration - UPDATED for v0.4.0+)
|-- build.bat                       (Windows batch build script)
|-- build.py                        (Python build script)
|-- create_icon.py                  (Icon generator)
|-- app.ico                         (Generated icon)
|-- requirements.txt                (Runtime dependencies - for source installs)
|-- build-requirements.txt          (Build dependencies - UPDATED for v0.4.0+)
|-- ...
```

## Build Configuration (v0.4.0+)

### Updated Files

**build-requirements.txt** - Dependencies for building:
```
PyInstaller>=6.0.0
pillow>=10.0.0
pydicom>=2.4.0
pynetdicom>=2.0.0
numpy>=1.20.0
```

**dcmcreator.spec** - PyInstaller configuration:
- Includes 9 optional application modules
- Automatically bundles all test features
- No manual configuration needed

### Why These Changes?

PyInstaller uses static analysis to find modules. The new optional modules use lazy imports (only load when needed), making them "invisible" to PyInstaller. The updated spec file explicitly declares them so they're bundled automatically.

**Result**: Users get all features without needing to install anything extra!

## Troubleshooting

### Issue: "Python is not installed or not in PATH"
**Solution**: Install Python and make sure to check "Add Python to PATH" during installation

### Issue: "pip: command not found"
**Solution**: Make sure Python is properly installed. Try:
```cmd
python -m pip install --upgrade pip
```

### Issue: Build takes too long or freezes
**Solution**: This is normal! First builds can take 5-10 minutes (was 3-5 in v0.3.x due to additional modules). Be patient.

### Issue: "PyInstaller not found"
**Solution**: The build script will install it automatically. If not:
```cmd
pip install PyInstaller>=6.0.0
```

### Issue: "Module not found" during build (v0.4.0+)
**Solution**: Install build dependencies:
```cmd
pip install -r build-requirements.txt
```

### Issue: ".exe file won't start when distributed"
**Solution**: 
1. Make sure you're distributing the ZIP file or entire folder
2. Never send just the EXE without the `_internal\` folder
3. The `_internal\` folder contains all Python libraries needed

### Issue: "Missing DLL" or "ModuleNotFoundError"
**Solution**:
1. If using ZIP: Users must extract the entire ZIP file
2. If distributing folder: Ensure `_internal\` folder is included
3. Test before distributing by running from dist folder

### Issue: Test tabs show "not available" (v0.4.0+)
**Solution**: This shouldn't happen with the new build process:
- Verify you built with updated `dcmcreator.spec`
- Check that `build-requirements.txt` was installed
- Run `python check_modules.py` to verify all modules load
- Rebuild with `python build.py`

## First Time Build Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] Navigated to project directory
- [ ] Run: `pip install -r build-requirements.txt`
- [ ] Run: `python build.py`
- [ ] Wait 5-10 minutes for completion
- [ ] Check `DICOM Creator.zip` file created
- [ ] Extract ZIP and test `DICOM Creator.exe`
- [ ] Verify View menu ? Show All shows all 13 tabs
- [ ] Test a core feature (File ? New or Remote ? Send)
- [ ] Ready to distribute!

## For Developers

If modifying the build process:

1. **Adding new optional modules**: Update `dcmcreator.spec` hiddenimports list
2. **Adding new dependencies**: Update `build-requirements.txt` AND `requirements.txt`
3. **Testing module availability**: Run `python check_modules.py`
4. **Rebuilding**: Always clean before rebuilding: `python build.py`

## See Also

- [README.md](../README.md) - Project overview
- [requirements.txt](../requirements.txt) - Runtime dependencies for source installs
- [build-requirements.txt](../build-requirements.txt) - Build environment dependencies
- [dcmcreator.spec](../dcmcreator.spec) - PyInstaller configuration
- [build.py](../build.py) - Build orchestration script
