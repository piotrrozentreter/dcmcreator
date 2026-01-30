# ?? Distribution Guide

## Version 0.4.0+ Update

Starting with v0.4.0, the application includes additional optional modules:
- Connection Testing & Validation
- Stress Testing capabilities
- Transmission History tracking
- Performance Benchmarking
- Parallel Transmission support

**These are automatically bundled** - nothing extra to do for distribution!

File sizes have increased:
- **Old (v0.3.x)**: ~53 MB uncompressed, ~15-20 MB ZIP
- **New (v0.4.0+)**: ~150-200 MB uncompressed, ~60-70 MB ZIP

All test features are available in the ZIP distribution automatically.

---

## What to Distribute

### ? CORRECT: Distribute the entire folder

```
dist\DICOM Creator\                    ? Package THIS entire folder (150-200 MB)
?
??? DICOM Creator.exe                 ? Users run this
??? _internal\                        ? MUST include (all Python libraries)
?   ??? pydicom\                       ? DICOM file handling
?   ??? pynetdicom\                    ? Network DICOM C-STORE
?   ??? PIL\                           ? Image processing
?   ??? numpy\                         ? Array processing
?   ??? tcl8\, tk8\                    ? Tkinter GUI libraries
?   ??? api-ms-win-core-*.dll          ? Windows runtime libraries
?   ??? [~150+ other library files]
??? src\                              ? Application source
??? [other support files]
```

### ? WRONG: Don't distribute just the EXE

```
DICOM Creator.exe                      ? ALONE: Won't work!
                                          Missing libraries = Application crash
```

---

## Distribution Methods

### Method 1: ZIP Archive (Recommended)

**Steps:**
1. Right-click `dist\DICOM Creator\` folder
2. Select "Send to" ? "Compressed (zipped) folder"
3. Creates `DICOM Creator.zip` (~60-70 MB)

OR use the auto-created ZIP from the build process (recommended!)

**Pros:**
- ? Smaller file size (compression 55-65%)
- ? Easy to email or upload
- ? Users just extract and run
- ? Standard format
- ? Includes all test features automatically

**File sizes:**
- ZIP: 60-70 MB
- Uncompressed: 150-200 MB after extraction

**Distribution:**
- Email as attachment
- Upload to cloud storage
- GitHub release download
- Website download link

```bash
# The build process creates this automatically:
python build.py
# ? Generates: DICOM Creator.zip (60-70 MB)
# ? Use this for distribution!
```

### Method 2: Direct Folder Distribution

**Best for:**
- USB drives
- Network shares
- Internal IT distribution
- Direct copying

**Steps:**
1. Copy entire `dist\DICOM Creator\` folder
2. Paste to destination
3. Users double-click `DICOM Creator.exe`

**Considerations:**
- Larger transfer (~150-200 MB)
- No compression overhead
- Useful for local deployment

### Method 3: Professional Installer

For enterprise deployments, create an NSIS installer:
- Uninstall functionality
- Start Menu shortcuts
- File associations
- Professional appearance

See [NSIS Documentation](https://nsis.sourceforge.io/) for details.

---

## Pre-Distribution Checklist

Before distributing, verify:

- [ ] Built with `python build.py` (v0.4.0+ process)
- [ ] `DICOM Creator.zip` file created (60-70 MB)
- [ ] All test tabs visible (View menu ? Show All)
- [ ] Connection Test tab loads
- [ ] Stress Test tab loads
- [ ] Transmission History tab loads
- [ ] Benchmarking tab loads
- [ ] Parallel Send tab loads
- [ ] Core features work (load, save, remote)
- [ ] No error messages or missing modules

If any test tab shows "not available", rebuild:
```bash
python build.py
```

---

## User Instructions

### For ZIP Distribution

**Instructions to give users:**

1. **Download and Extract**
   - Download `DICOM Creator.zip`
   - Right-click ? Extract all
   - Choose destination folder

2. **Run**
   - Open extracted folder
   - Double-click `DICOM Creator.exe`
   - Application launches!

3. **No Installation**
   - No admin rights needed
   - No system changes
   - Can run from USB drive
   - Can delete folder to uninstall

### For Folder Distribution

**Instructions to give users:**

1. **Copy Folder**
   - Copy `DICOM Creator` folder
   - Paste to desired location

2. **Run**
   - Open folder
   - Double-click `DICOM Creator.exe`

3. **Done**
   - Application launches immediately
   - Can move folder anytime

---

## Size Reference

| Version | Uncompressed | ZIP | Increase |
|---------|-------------|-----|----------|
| v0.3.x | ~53 MB | ~15-20 MB | - |
| v0.4.0+ | ~150-200 MB | ~60-70 MB | +3x (includes new test modules) |

**Note**: Size increase is due to:
- PyNetDICOM library (+30 MB)
- Additional test modules (+20-30 MB)
- Expanded PyDICOM (+10 MB)

All are required for the new testing and performance features.

---

## Troubleshooting Distribution Issues

### Problem: User gets "DLL not found" error

**Solution:**
- Verify they extracted the ENTIRE ZIP file
- The `_internal\` folder must be present
- All library DLLs are in `_internal\`

### Problem: Application crashes on startup

**Solution:**
- Ensure full folder was distributed (not just EXE)
- Check all files extracted correctly
- Try re-extracting the ZIP
- Verify Windows has required runtime (Windows 7+)

### Problem: ZIP file is too large

**Solution:**
- This is normal for v0.4.0+ (60-70 MB)
- Compression is already applied
- Use 7-Zip or WinRAR for slight additional compression
- Alternative: Distribute uncompressed folder (150-200 MB)

### Problem: Test tabs not working in distributed version

**Solution:**
- Verify you built with `python build.py` (v0.4.0+ process)
- Check that all test tabs show in View menu
- Rebuild if needed and re-distribute
- Ensure `dcmcreator.spec` has new modules (auto-updated)

---

## Final Verification

After building, verify the distribution:

```cmd
cd dist\DICOM Creator

# Check EXE exists
dir DICOM*.exe

# Check _internal folder exists with many files
dir _internal | find /c /v ""    (should show 150+ items)

# Check src folder exists
dir src

# Try running
DICOM Creator.exe
```

---

## Ready to Distribute!

? Your `dist\DICOM Creator\` folder is ready for distribution.

Users can run it on any Windows 7+ (64-bit) computer without Python installed.

**Distribute the entire folder, not just the EXE!**
