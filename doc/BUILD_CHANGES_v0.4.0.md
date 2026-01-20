# Build Process Changes for v0.4.0

## Summary
Updated the build process to include new validation and tag viewer modules introduced in v0.4.0.

## Changes Made

### 1. PyInstaller Spec File (`dcmcreator.spec`)

#### Added Hidden Imports
```python
hiddenimports = [
    # ... existing imports ...
    'vr_validator',        # NEW: VR validation engine
    'validation_dialog',   # NEW: Validation UI
    'tag',                 # NEW: Tag parsing
    'tag_dialog',         # NEW: Tag viewer UI
]
```

#### Added Data Files
```python
datas = [
    ('src', 'src'),
    ('src/VR.xml', 'src'),  # NEW: DICOM data dictionary (7MB)
]
```

### 2. Build Script (`build.py`)

#### Added VR.xml Verification Step
```python
# Step 3.5: Verify VR.xml exists
print("\nStep 3.5: Verifying DICOM data dictionary...")
vr_xml_path = Path("src/VR.xml")
if not vr_xml_path.exists():
    print(f"ERROR: VR.xml not found at {vr_xml_path}")
    return False
```

#### Enhanced Build Summary
Added feature list showing all new v0.4.0 features:
- VR validation with PS3.6 data dictionary
- Tag viewer for all DICOM tags
- Validation dialog with detailed reports
- Plus existing features

### 3. Build Verification Script (`verify_build.py`) - NEW

Created comprehensive pre-build verification:
- Checks all source files exist
- Verifies spec file configuration
- Validates Python dependencies
- Checks VR.xml integrity
- Confirms build configuration files

Usage:
```bash
python verify_build.py
```

### 4. Documentation Updates

#### `doc/BUILD_INSTRUCTIONS.md`
- Added v0.4.0 modules to features table
- Documented new validation and viewer features
- Updated "What's Included" section
- Added menu navigation instructions

#### `doc/BUILD_CHECKLIST.md` - NEW
Complete build checklist with:
- Pre-build verification steps
- Build process checklist
- Post-build verification
- Functional testing procedures
- Known issues and solutions
- Distribution checklist

## New Files Created

1. **`verify_build.py`**
   - Pre-build verification script
   - Checks all requirements before building
   - Prevents common build errors

2. **`doc/BUILD_CHECKLIST.md`**
   - Step-by-step build verification
   - Quality assurance procedures
   - Testing guidelines

## Critical Changes

### VR.xml Inclusion
**CRITICAL**: The 7MB `VR.xml` file MUST be included in the build:
- Contains complete DICOM data dictionary from PS3.6
- Required for VR validation
- Required for VR viewer
- Must be present in `src/VR.xml`

### PyInstaller Path Resolution
**IMPORTANT**: Added `get_resource_path()` helper function for PyInstaller compatibility:
```python
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    import sys
    import os
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running in PyInstaller bundle
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)
```

This ensures VR.xml and other resources can be found whether running:
- In development environment
- From PyInstaller executable
- From any location after extraction

### Module Dependencies
New modules depend on each other:
```
vr_validator.py
    ??> Loads VR.xml for validation rules
    
validation_dialog.py
    ??> Uses vr_validator for displaying results
    
tag.py
    ??> Core tag parsing utilities
    
tag_dialog.py
    ??> Uses tag.py for displaying tag data
    ??> Can use VR.xml for tag descriptions
```

## Build Process Flow

```
1. Pre-Build Verification (NEW)
   ??> python verify_build.py
       ??> Check source files
       ??> Check spec file config
       ??> Check dependencies
       ??> Verify VR.xml
       ??> Check build config

2. Build Execution
   ??> python build.py
       ??> Step 1: Check Python
       ??> Step 2: Install dependencies
       ??> Step 3: Create icon
       ??> Step 3.5: Verify VR.xml (NEW)
       ??> Step 4: Clean previous builds
       ??> Step 5: Build with PyInstaller
       ??> Step 6: Create ZIP distribution

3. Post-Build Testing (NEW - see checklist)
   ??> Verify distribution structure
   ??> Test VR Viewer
   ??> Test Tag Viewer
   ??> Test Validation
   ??> Verify no missing file errors
```

## Testing Requirements

### Minimum Testing for v0.4.0 Build

After building, test these features:

1. **VR Viewer** (DICOM ? View VRs)
   - Should show 4000+ DICOM data elements
   - Should load from VR.xml
   - Should allow searching

2. **Tag Viewer** (DICOM ? View All Tags)
   - Should display tags from loaded DICOM
   - Should show tag details
   - Should handle private tags

3. **Validation** (File ? Validate or Ctrl+Shift+V)
   - Should validate form fields
   - Should show validation dialog
   - Should catch VR errors

4. **Auto-Validation**
   - Load DICOM with errors
   - Should show validation warnings
   - Should allow continue/cancel

## Known Issues & Solutions

### Issue: "VR Validator is not available"
**Cause**: LazyImport not loading vr_validator correctly
**Solution**: 
1. Check `vr_validator` in hiddenimports
2. Follow copilot-instructions.md for LazyImport priority
3. Ensure ConnectionValidator is main class

### Issue: "VR.xml not found"
**Cause**: VR.xml not included in build OR path resolution issue
**Solution**:
1. Verify VR.xml in src/ (7MB+)
2. Check dcmcreator.spec datas section includes: `('src/VR.xml', 'src')`
3. Ensure Step 3.5 passes during build
4. **FIXED**: Updated VRViewerDialog to use `sys._MEIPASS` for PyInstaller paths

### Issue: Tag Viewer empty
**Cause**: pydicom not properly bundled
**Solution**:
1. Verify pydicom in hiddenimports
2. Check _internal/pydicom exists
3. Test with valid DICOM file

## Distribution Checklist

- [ ] `DICOM Creator.zip` created (60-80 MB)
- [ ] Contains `DICOM Creator.exe` (~25 MB)
- [ ] Contains `_internal/` with libraries
- [ ] Contains `src/` with all .py files
- [ ] **CRITICAL**: Contains `src/VR.xml` (7 MB)
- [ ] Tested on clean Windows machine
- [ ] All v0.4.0 features work
- [ ] No "file not found" errors

## Size Expectations

| Component | Size | Notes |
|-----------|------|-------|
| DICOM Creator.exe | ~25 MB | Main executable |
| _internal/ | ~120 MB | Python libraries |
| src/ | ~15 MB | Application code |
| src/VR.xml | ~7 MB | DICOM dictionary |
| **Total Folder** | **150-200 MB** | Uncompressed |
| **ZIP File** | **60-80 MB** | Compressed |

## Version Control

```bash
# Commit build changes
git add dcmcreator.spec build.py verify_build.py doc/
git commit -m "Update build process for v0.4.0 validation and tag viewer features"

# Tag release
git tag v0.4.0
git push origin 0.4
git push --tags
```

## Next Steps

1. Run verification: `python verify_build.py`
2. Fix any issues reported
3. Run build: `python build.py`
4. Follow `doc/BUILD_CHECKLIST.md` for testing
5. Distribute `DICOM Creator.zip`

## References

- PyInstaller spec file: `dcmcreator.spec`
- Build script: `build.py`
- Verification script: `verify_build.py`
- Build instructions: `doc/BUILD_INSTRUCTIONS.md`
- Build checklist: `doc/BUILD_CHECKLIST.md`
- Copilot instructions: `.github/copilot-instructions.md`

---

**Date**: 2025-01-19
**Version**: 0.4.0
**Author**: Build Process Update
