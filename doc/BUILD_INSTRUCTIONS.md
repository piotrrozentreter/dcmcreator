# Building DICOM Creator as an Executable

This guide explains how to build a standalone executable (.exe) file that can run on Windows computers without Python installed.

## Important: What to Distribute

**The build process now automatically creates a ZIP file!**

- [x] **Best option**: Use the auto-generated `DICOM Creator.zip` file
- [x] **Alternative**: Distribute the entire `dist\DICOM Creator\` folder
- [ ] **DON'T distribute**: Just the `DICOM Creator.exe` alone (needs libraries)

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
4. Wait for the build to complete (takes 3-5 minutes)
5. **Two distribution options are created**:
   - `DICOM Creator.zip` (15-20 MB) - For email/upload
   - `dist\DICOM Creator\` folder (53 MB) - For direct sharing

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
   - `DICOM Creator.zip` (15-20 MB) - For email/upload
   - `dist\DICOM Creator\` folder (53 MB) - For direct sharing

## What Gets Built

### Automatic ZIP Creation
The build script now automatically creates `DICOM Creator.zip` containing:
- `DICOM Creator.exe` - Main executable (18.19 MB)
- `_internal\` - All Python libraries (required!)
- `src\` - Application source code
- **Total ZIP size**: 15-20 MB (compressed)

### Also Available
- **Distribution folder**: `dist\DICOM Creator\` (53.49 MB uncompressed)
- **For direct folder sharing** or USB distribution

### Compression Savings
- Folder size: 53.49 MB
- ZIP size: 15-20 MB
- **Compression: 60-70%**

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
# Creates DICOM Creator.zip (15-20 MB)

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
|       |   |-- pydicom/
|       |   |-- pynetdicom/
|       |   |-- PIL/
|       |   |-- numpy/
|       |   |-- tcl8/, tk8/
|       |   |-- [many more DLLs]
|       |-- src/                    (Application source)
|-- build/                          (Temporary - can delete)
|-- dcmcreator.spec                 (Build configuration)
|-- build.bat                       (Windows batch build script)
|-- build.py                        (Python build script)
|-- create_icon.py                  (Icon generator)
|-- app.ico                         (Generated icon)
|-- ...
```

## Troubleshooting

### Issue: "Python is not installed or not in PATH"
**Solution**: Install Python and make sure to check "Add Python to PATH" during installation

### Issue: "pip: command not found"
**Solution**: Make sure Python is properly installed. Try:
```cmd
python -m pip install --upgrade pip
```

### Issue: Build takes too long or freezes
**Solution**: This is normal! The first build can take 5-10 minutes. Be patient.

### Issue: "PyInstaller not found"
**Solution**: The build script will install it automatically. If not:
```cmd
pip install PyInstaller>=6.0.0
```

### Issue: ".exe file won't start when distributed"
**Solution**: 
1. Make sure you're distributing the ZIP file or entire folder
2. Never send just the EXE without the `_internal\` folder
3. The `_internal\` folder contains all Python libraries needed

### Issue: "Missing DLL" or "ModuleNotFoundError"
**Solution**:
1. If using ZIP: Users must extract the entire ZIP file
2. If using folder: Distribute the entire `dist\DICOM Creator\` folder
3. Never delete or modify files in the `_internal\` folder

### Issue: ZIP creation failed
**Solution**:
1. The executable was still built successfully
2. Manually create ZIP:
   ```cmd
   Right-click dist\DICOM Creator -> Send to -> Compressed (zipped) folder
   ```
3. Or use PowerShell command provided above

## Build Customization

### Modify Icon

1. Create your own icon (256x256 PNG works well)
2. Replace `create_icon.py` with your own icon generation
3. Rebuild using the build script

### Single File Executable (Not Recommended)

To create a single `.exe` file instead of a folder:

Edit `dcmcreator.spec` and change:
```python
# From:
coll = COLLECT(...)

# To:
# Just use exe without COLLECT
```

Then rebuild. **Note**: 
- Single file executables are **much slower** to start (30-60 seconds first run)
- File size is larger (80-100 MB)
- We recommend the folder/ZIP distribution instead

## Clean Build

To start fresh:

```cmd
# Windows
rmdir /s /q build dist __pycache__
del DICOM\ Creator.zip

# Or just run build script again (it cleans automatically)
build.bat
```

## Performance

- **Distribution size (ZIP)**: 15-20 MB (compressed)
- **Distribution size (folder)**: 53.49 MB (uncompressed)
- **Extract/Copy time**: 1-2 minutes on typical system
- **First run**: 10-15 seconds (unpacking and initializing)
- **Subsequent runs**: 5-10 seconds
- **Memory usage**: 150-200 MB (normal for Python applications)

## Signing the EXE (Optional)

For production use, you may want to digitally sign the executable:

1. Obtain a code signing certificate
2. Sign the EXE before distribution:
   ```cmd
   signtool sign /f certificate.pfx /p password /t http://timestamp.server /fd SHA256 "dist\DICOM Creator\DICOM Creator.exe"
   ```
3. Then create the ZIP with the signed EXE

## Support

If you encounter issues:

1. Check that all dependencies are installed:
   ```cmd
   pip list | findstr pydicom
   ```

2. Verify Python version (3.9 or higher required):
   ```cmd
   python --version
   ```

3. Try rebuilding from scratch:
   ```cmd
   rmdir /s /q build dist
   del DICOM\ Creator.zip
   build.bat
   ```

4. For ZIP creation issues, manually create using:
   ```cmd
   powershell -Command "Add-Type -AssemblyName 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('dist\DICOM Creator', 'DICOM Creator.zip')"
   ```

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Python Official Website](https://www.python.org/)
- [DICOM Creator GitHub](https://github.com/piotrrozentreter/dcmcreator)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [Distribution Guide](DISTRIBUTION_GUIDE.md)
- [Which EXE to Distribute](WHICH_EXE_TO_DISTRIBUTE.md)
