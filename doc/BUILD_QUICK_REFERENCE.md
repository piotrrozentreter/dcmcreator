# Quick Build Reference - v0.4.0

## Pre-Build Check
```bash
python verify_build.py
```
? All checks must pass before building

## Build Commands

### Windows (Recommended)
```cmd
build.bat
```

### Python Script
```bash
python build.py
```

### Manual PyInstaller
```bash
python -m PyInstaller dcmcreator.spec
```

## What Gets Built

```
DICOM Creator.zip (60-80 MB)
> dist/DICOM Creator/
    > DICOM Creator.exe      25 MB
    > _internal/             120 MB (libraries)
    > src/
        > VR.xml             7 MB   CRITICAL
        > vr_validator.py
        > validation_dialog.py
        > tag.py
        > tag_dialog.py
        > ... (other modules)
```

## Quick Test After Build

```bash
cd "dist\DICOM Creator"
"DICOM Creator.exe"
```

Test these features:
1. **DICOM ? View VRs** - Should show 4000+ elements
2. **DICOM ? View All Tags** - Load DICOM and view tags
3. **File ? Validate** (Ctrl+Shift+V) - Validate form data
4. Load DICOM file - Check auto-validation

## Critical Files Checklist

### In Repository
- [x] `src/VR.xml` (7 MB) - DICOM dictionary
- [x] `src/vr_validator.py` - Validation engine
- [x] `src/validation_dialog.py` - Validation UI
- [x] `src/tag.py` - Tag utilities
- [x] `src/tag_dialog.py` - Tag viewer UI

### In dcmcreator.spec
- [x] Hidden imports: `vr_validator`, `validation_dialog`, `tag`, `tag_dialog`
- [x] Data files: `('src/VR.xml', 'src')`

### In Distribution
- [x] `dist/DICOM Creator/DICOM Creator.exe`
- [x] `dist/DICOM Creator/_internal/` (all libraries)
- [x] `dist/DICOM Creator/src/VR.xml`  MUST EXIST
- [x] `DICOM Creator.zip` (auto-created)

## Common Errors

### "VR.xml not found"
```bash
# Check if file exists
dir src\VR.xml
# Should be ~7 MB

# If missing, build will fail at Step 3.5

# FIXED in v0.4.0: Added get_resource_path() for PyInstaller compatibility
# VR.xml is now found correctly in both dev and packaged environments
```

### "VR Viewer empty / no data"
```bash
# This was fixed in v0.4.0
# Cause: Path resolution issue with PyInstaller
# Solution: Uses sys._MEIPASS for packaged apps
# See: doc/VR_XML_PATH_FIX.md for details
```

### "VR Validator not available"
```python
# Check dcmcreator.spec hiddenimports
'vr_validator',      # Must be present
'validation_dialog',
'tag',
'tag_dialog',
```

### "Module not found" during runtime
```bash
# Rebuild with updated spec file
python build.py
```

## Distribution

### Email / Upload
```
Share: DICOM Creator.zip (60-80 MB)
Extract ? Run DICOM Creator.exe
```

### USB / Network
```
Copy: dist\DICOM Creator\ folder (150-200 MB)
Run: DICOM Creator.exe
```

## Full Documentation

- Build Instructions: `doc/BUILD_INSTRUCTIONS.md`
- Build Checklist: `doc/BUILD_CHECKLIST.md`
- Changes Summary: `doc/BUILD_CHANGES_v0.4.0.md`

## Support

### Verification Failed?
```bash
python verify_build.py
# Fix reported issues
# Re-run until all checks pass
```

### Build Failed?
```bash
# Check build.py output
# Look for Step X failure
# Fix the specific issue
# Run build.py again
```

### Runtime Errors?
```bash
# Run from command line to see errors
cd "dist\DICOM Creator"
"DICOM Creator.exe"
# Check console output
```

---

**Quick Start**: `python verify_build.py` ? `python build.py` ? Test features ? Distribute ZIP

**Version**: 0.4.0 | **Updated**: 2025-01-19
