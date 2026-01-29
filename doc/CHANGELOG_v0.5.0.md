# DICOM Creator v0.5.0 - Changelog

**Release Date**: January 2025

## Overview

Version 0.5.0 focuses on improving module loading reliability and fixing critical import issues that affected optional testing modules.

## What's New

### Enhanced LazyImport System

**Improved Class Detection:**
- Better handling of modules with multiple classes
- Prioritizes main/public class during class extraction
- Enhanced `_load_class()` method with fallback mechanisms
- Explicit class selection for ambiguous modules

**Example:**
```python
# connection_validator.py now correctly loads ConnectionValidator
# even when CEchoValidator appears first in inspect results
ConnectionValidator = LazyImport(".connection_validator", "connection_validator")
```

### Better Error Diagnostics

**Comprehensive Error Reporting:**
- Detailed error messages for module loading failures
- Enhanced logging for troubleshooting
- Clear distinction between missing modules and import errors
- Direct import fallback with error capture

**Example Log Output:**
```
[ERROR] LazyImport._load_class() returned None for connection_validator
[INFO] Attempting direct import...
[ERROR] Direct import failed: ModuleNotFoundError
```

### Improved Module Loading

**Reliability Improvements:**
- Try direct import when LazyImport returns None
- Better exception handling throughout import chain
- More robust fallback mechanisms
- Clearer user feedback on missing features

## Bug Fixes

### Critical Fixes

1. **ConnectionValidator Loading Issue** ?
   - **Issue**: ConnectionValidator class was not loading correctly
   - **Cause**: Module has multiple classes (CEchoValidator, ConnectionValidator)
   - **Fix**: Enhanced LazyImport to prioritize main class
   - **Impact**: Connection Testing tab now works reliably

2. **VRValidator Initialization** ?
   - **Issue**: VRValidator sometimes failed to initialize
   - **Cause**: Import errors not properly captured
   - **Fix**: Added comprehensive error capture and reporting
   - **Impact**: Validation features more reliable

3. **Module Import Reliability** ?
   - **Issue**: Optional modules sometimes silently failed
   - **Cause**: Insufficient error handling in LazyImport
   - **Fix**: Added fallback to direct import with error details
   - **Impact**: Better user experience with missing dependencies

## Improvements

### Code Quality

- Enhanced error handling throughout application
- Better logging for debugging
- Improved code documentation
- More consistent import patterns

### Performance

- Faster module loading with improved caching
- Reduced redundant import attempts
- Better memory management for lazy-loaded modules

### Developer Experience

- Updated Copilot instructions for LazyImport usage
- Better guidelines for handling multi-class modules
- Improved troubleshooting documentation

## Known Issues

### Minor Issues

1. **First-time startup may be slow**
   - **Workaround**: Normal behavior for PyInstaller executables
   - **Status**: Expected behavior, not a bug

2. **Windows Defender may flag EXE**
   - **Workaround**: Add to exclusions or click "Run anyway"
   - **Status**: Common for unsigned executables

## Upgrade Notes

### From v0.4.0 to v0.5.0

**No Breaking Changes** - All existing features remain compatible.

**Recommended Actions:**
1. Update to Python 3.9+ if not already
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Rebuild EXE if using custom build: `python build.py`

**New Files:**
- None - all changes are code improvements

**Modified Files:**
- `src/appgui.py` - Enhanced LazyImport usage
- `src/import_helper.py` - Improved class detection
- `.github/copilot-instructions.md` - Updated guidelines
- `README.md` - Version updates and screenshots
- `doc/CHANGELOG_v0.5.0.md` - This file

## Testing

### Tested Configurations

? **Windows 10/11 (64-bit)**
- Python 3.9, 3.10, 3.11, 3.12
- PyInstaller EXE
- All features working

? **Windows 7 (64-bit)**
- Python 3.9
- PyInstaller EXE
- All features working

?? **macOS / Linux**
- Not officially tested this release
- Should work with Python source
- EXE build is Windows-only

### Test Coverage

- ? Module loading (all optional modules)
- ? ConnectionValidator initialization
- ? VRValidator initialization
- ? LazyImport with multiple classes
- ? Error handling and reporting
- ? Direct import fallback mechanism

## Migration Guide

### For End Users

**No migration needed!** Simply download and run v0.5.0.

Your existing data is preserved:
- Server presets
- Transmission history
- Configuration files

### For Developers

**Update LazyImport Usage:**

**Old Pattern (v0.4.0):**
```python
ConnectionValidator = LazyImport(".connection_validator", "connection_validator")
# May fail silently if multiple classes exist
```

**New Pattern (v0.5.0):**
```python
ConnectionValidator = LazyImport(".connection_validator", "connection_validator")
# Now handles multiple classes correctly
# Falls back to direct import if LazyImport fails
# Provides detailed error messages
```

**Enhanced Error Handling:**
```python
# v0.5.0 automatically tries direct import
try:
    validator_cls = ConnectionValidator._load_class()
    if validator_cls is None:
        # v0.5.0 provides detailed error in vr_validator_error
        logger.error(f"Failed to load: {self.vr_validator_error}")
except Exception as e:
    logger.exception("Error loading validator")
```

## Documentation Updates

### New Documents
- `doc/CHANGELOG_v0.5.0.md` - This changelog

### Updated Documents
- `README.md` - Version 0.5.0 updates and screenshots
- `.github/copilot-instructions.md` - LazyImport best practices
- `doc/INDEX.md` - Navigation updates

### Screenshot Placeholders Added
- Main interface (Patient/Study/Series tabs)
- Image loading and preview
- DICOM tree view
- Remote transmission
- Server presets
- Tag viewer
- VR viewer
- Validation dialog
- Test generation
- Connection testing
- Stress testing
- Transmission history

## Contributors

- **Piotr Rozentreter** - Lead Developer, Hyland Software

## Special Thanks

- GitHub Copilot for development assistance
- PyDICOM team for excellent DICOM library
- PyNetDICOM team for network DICOM support

## Next Release (v0.6.0 - Planned)

### Planned Features
- ?? Batch DICOM editing
- ?? Advanced analytics dashboard
- ?? Secure transmission (TLS)
- ?? Multi-language support
- ?? Web interface (optional)

### Under Consideration
- Cloud storage integration
- Database backend for history
- REST API for automation
- Plugin system for extensions

## Feedback

We welcome your feedback!

- ?? **Report bugs**: [GitHub Issues](https://github.com/HylandSoftware/dcmcreator/issues)
- ?? **Feature requests**: [GitHub Discussions](https://github.com/HylandSoftware/dcmcreator/discussions)
- ?? **Internal support**: Contact Hyland development team

---

**Thank you for using DICOM Creator v0.5.0!**

[Back to README](../README.md) | [Documentation Index](INDEX.md)
