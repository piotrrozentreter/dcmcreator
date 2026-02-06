# DICOM Creator v0.6.0 Release Notes

**Release Date**: January 2025

**Version**: 0.6.0

---

## Overview

Version 0.6.0 introduces a comprehensive validation system for DICOM data, significantly improving data quality assurance and user experience. This release focuses on validation capabilities, better error reporting, and enhanced UI for a more robust DICOM creation and transmission workflow.

## Major Features

### 1. Real-Time VR Validation System

**What's New:**
- Comprehensive DICOM Value Representation (VR) validation for all form fields
- Field-level validation with specific error messages
- Support for validating:
  - Data types (string, numeric, date, time, etc.)
  - Value ranges and limits
  - Format specifications (DICOM standard compliance)
  - Mandatory vs optional fields
  - VR-specific constraints

**How to Use:**
```
File Menu  Validate
```

**Example Validation Checks:**
- Patient Name: Max 64 characters (PN - Person Name)
- Patient Birth Date: Format YYYYMMDD (DA - Date)
- Patient Sex: Must be M, F, or O (CS - Code String)
- Patient Age: Format like "032Y" (AS - Age String)
- Study Instance UID: Must be valid UID format (UI)

### 2. Validation Report Dialogs

**What's New:**
- Interactive validation report dialog with detailed error information
- Color-coded error vs warning indicators
- Field-by-field error descriptions
- Remediation suggestions for invalid values
- Option to continue with warnings or abort save/send operations

**Features:**
- **Error Summary** - Count of errors and warnings at top
- **Field Details** - Specific description of validation issues
- **VR Information** - Display the DICOM VR type and constraints
- **Suggested Fixes** - Help text explaining how to fix issues

**Dialog Modes:**
- **Save Mode** - Shows before saving DICOM files
- **Send Mode** - Shows before sending to remote server
- **Load Mode** - Shows when loading DICOM with errors
- **Manual Mode** - Accessible via File menu ? Validate

### 3. DICOMDIR File Support

**What's New:**
- Load and process DICOMDIR files (DICOM Directory structures)
- Automatic expansion of DICOMDIR references to actual datasets
- Support for hierarchical DICOMDIR structures

**How to Use:**
```
Load DICOM Tab ? Load DICOM File(s)
Select a DICOMDIR file, and it will automatically load all referenced DICOM files
```

**Benefits:**
- Easy import of DICOM folders organized with DICOMDIR
- Automatic parsing of directory structures
- Support for mixed DICOMDIR + individual DICOM files

### 4. Private Tag Preservation

**What's New:**
- Automatic preservation of private DICOM tags during save operations
- Maintains manufacturer-specific and application-specific tags
- Ensures data integrity when editing and re-saving DICOM files

**Features:**
- Private tags (odd group numbers) are preserved
- Optional tags are maintained as-is
- Group Length tags cleaned up (DICOM 2008+ compliance)
- Post-save verification of tag integrity

**How It Works:**
- When loading a DICOM file, private tags are stored
- When saving/modifying, private tags are merged with new data
- Final DICOM maintains all original private tags

### 5. Group Length Cleanup

**What's New:**
- Automatic removal of deprecated Group Length tags (0x0000 elements)
- Ensures DICOM 2008+ standard compliance
- Improves compatibility with modern DICOM systems

**Why This Matters:**
- Group Length tags (GGGG,0000) were deprecated in DICOM 2008
- Some modern DICOM systems may reject files with these tags
- v0.6.0 automatically removes them during save
- Pre-save warning notifies users of this cleanup

**Technical Details:**
- Affects elements like (0002,0000), (0008,0000), etc.
- Only Group Length tags are removed (element 0000)
- All data-bearing tags are preserved
- User is warned before saving

### 6. Enhanced Load-Time Validation

**What's New:**
- Automatic DICOM validation when loading files
- Detailed error reporting in validation dialogs
- Option to continue despite validation errors
- All loaded data is validated against VR specifications

**Workflow:**
1. Select DICOM file(s) to load
2. Application validates all tags and metadata
3. If errors found, validation dialog appears
4. Review errors/warnings and choose to continue or cancel
5. Form fields populate with loaded data

**Error Types:**
- **Errors** - Critical issues that may affect functionality
- **Warnings** - Non-critical issues that should be reviewed
- **Informational** - Status updates (not blocking)

### 7. Pre-Save Validation

**What's New:**
- Validation check before saving DICOM files
- Prevents saving invalid DICOM files
- Clear error messages with remediation suggestions
- Option to cancel save and fix issues

**Validation Checks:**
- All required fields present
- All data types correct (strings, dates, numbers, etc.)
- Value ranges within specifications
- Format compliance (dates, UIDs, etc.)
- No conflicting values

**User Experience:**
- If validation passes: File saves immediately
- If only warnings: User can choose to save or cancel
- If errors: Save is blocked with detailed error messages

### 8. Pre-Send Validation

**What's New:**
- Validation before transmitting DICOM to remote server
- Ensures server receives compliant DICOM files
- Prevents network transmission of invalid data

**Checks Before Send:**
- Patient ID should be present
- Required metadata is populated
- No critical validation errors
- All data types are correct

**User Flow:**
```
1. Configure remote server
2. Click "Send All Loaded DICOM"
3. Validation runs automatically
4. If errors: Dialog shows issues, send is blocked
5. If OK: Transmission proceeds
6. Progress shown in Messages area
```

### 9. Improved Tab Visibility Management

**What's New:**
- View menu to toggle test tabs on/off
- Cleaner UI with optional advanced features hidden by default
- Save your preference across sessions

**Menu Options:**
```
View Menu:
 Core Tabs (disabled label)
 Patient (checkbox)
 Study (checkbox)
 Series/Modality (checkbox)
 Image (checkbox)
 Load DICOM (checkbox)
 Save (checkbox)
 Remote (checkbox)
 (separator)
 Test Tabs (disabled label)
 Test/Generate (checkbox)
 Connection Test (checkbox)
 Stress Test (checkbox)
 Transmission History (checkbox)
 Benchmarking (checkbox)
 Parallel Send (checkbox)
 (separator)
 Show All
 Hide Test Tabs
```

**Quick Actions:**
- **Show All** - Display all tabs at once
- **Hide Test Tabs** - Hide advanced testing features

### 10. Enhanced DICOM Tag Viewer

**What's New:**
- Better search and filtering capabilities
- Improved tag information display
- Enhanced UI for better usability
- Support for viewing all DICOM dictionary tags

**Features:**
- **Full DICOM Dictionary** - Browse all PS3.6 data elements
- **Search** - Find tags by number, name, or keyword
- **Sort** - Click columns to sort by any field
- **Filter** - Real-time filtering as you type
- **Export** - Export tag information to text file

**Display Columns:**
- Tag (GGGG,EEEE format)
- Name (full DICOM element name)
- Keyword (programmatic name)
- VR (Value Representation)
- VM (Value Multiplicity)
- Status (Standard/Retired)

## Enhanced Features

### 1. Better Error Messages

**What's New:**
- Clearer, more actionable error messages
- Specific guidance on how to fix issues
- Reference to DICOM standards where applicable

**Example:**
```
BEFORE:
Error: Invalid value

AFTER:
Error: Patient Birth Date must be in YYYYMMDD format (DA - Date)
  Current Value: "1980/01/15"
  Expected Format: "19800115"
  Fix: Use format YYYYMMDD, e.g., 19800115 for January 15, 1980
```

### 2. Improved Context Menus

**What's New:**
- Right-click on DICOM instances in tree view
- Quick access to common operations
- "Show Image" to display pixel data

**Context Menu:**
```
Right-click on instance:
 Show Image
    (Displays image in Image tab with auto-switch)
```

### 3. Better Image Preview

**What's New:**
- Improved handling of various image dimensions
- Better resizing and aspect ratio preservation
- Support for more image formats
- Error handling for unsupported formats

**Features:**
- Auto-scale to preview area
- Maintain aspect ratio
- Handle multi-dimensional arrays
- Graceful degradation for unsupported formats

### 4. Enhanced Session Tracking

**What's New:**
- Better tracking of validation operations
- Session-level statistics
- Improved logging for debugging

## Technical Improvements

### 1. LazyImport Enhancements

**What's New:**
- Better detection of main classes in multi-class modules
- Explicit class selection support
- Improved error handling and diagnostics
- Enhanced logging for troubleshooting

**Example - ConnectionValidator:**
- Module has both ConnectionValidator (main) and internal classes
- v0.6.0 correctly identifies ConnectionValidator as main class
- Falls back to CEchoValidator if primary unavailable
- Clear error messages if loading fails

### 2. Improved Module Loading

**What's New:**
- More reliable import of optional modules
- Better fallback mechanisms
- Clear diagnostics when modules unavailable
- No crashes due to missing dependencies

**Behavior:**
- Core features work even if optional modules unavailable
- Test features gracefully disable if dependencies missing
- User is informed of missing capabilities
- Log files provide detailed troubleshooting info

### 3. Enhanced Logging

**What's New:**
- More detailed debug logging
- Better error context in logs
- Improved troubleshooting information

**Log Information:**
- Module loading attempts and failures
- Validation check details
- DICOM parsing information
- Network operation details

## UI/UX Improvements

### 1. Cleaner Main Interface

**What's New:**
- Test tabs hidden by default (View ? Hide Test Tabs)
- Cleaner main interface for standard users
- Advanced users can show test tabs as needed

**Tabs Now Visible by Default:**
- Patient
- Study
- Series/Modality
- Image
- Load DICOM
- Save
- Remote

**Test Tabs (Optional):**
- Test/Generate
- Connection Test
- Stress Test
- Transmission History
- Benchmarking
- Parallel Send

### 2. Validation Dialog Layout

**What's New:**
- Clear separation of errors vs warnings
- Scrollable list of issues
- Professional report format
- Easy navigation through validation results

**Dialog Components:**
- Header with error/warning counts
- Scrollable issue list with color coding
- Details section for selected issue
- Action buttons (Continue, Cancel, etc.)

### 3. Better Menu Organization

**What's New:**
- Validation-related items in File menu
- Test tabs toggle in View menu
- Organized submenu structure

**File Menu:**
```
 New
 Load
 Load Folder
 Save
 (separator)
 Validate (NEW)
 (separator)
 Exit
```

**DICOM Menu:**
```
 View VRs
 View All Tags
```

## Bug Fixes

### 1. Validation Dialog Issues

**Fixed:**
- Dialog now properly displays validation results
- Error messages render correctly
- Buttons respond to all user actions
- Modal dialog properly blocks interaction with main window

### 2. Image Preview Handling

**Fixed:**
- Better handling of unusual image dimensions
- Improved error handling for unsupported formats
- Graceful fallback for preview failures

### 3. DICOM Loading

**Fixed:**
- DICOMDIR loading now works correctly
- Private tags preserved through load/save cycle
- Metadata population from loaded files is reliable

### 4. Module Loading

**Fixed:**
- ConnectionValidator class loading improved
- Better detection of main classes in modules
- More reliable fallback mechanisms
- Clear error messages when loading fails

## Breaking Changes

None. v0.6.0 is fully backward compatible with v0.5.0 projects and DICOM files.

## Deprecations

**Deprecated:**
- Group Length tags (0000 elements) now removed during save
  - Rationale: Deprecated in DICOM 2008 standard
  - Benefit: Better compatibility with modern systems
  - Timing: Immediate removal, user is warned

**Not Breaking:**
- DICOM files with Group Length tags can still be loaded
- Group Length tags in source files are preserved until save
- User has option to review changes before save

## Known Limitations

### 1. Validation System

**Current Limitation:**
- VR validation based on PS3.6 standard
- Custom private tag validation not supported
- Module dependencies required for full validation

**Workaround:**
- Core validation works even without optional modules
- Manual VR checking available via Tag Viewer
- Refer to DICOM standard for custom tag validation

### 2. DICOMDIR Support

**Current Limitation:**
- Read-only DICOMDIR processing
- Cannot create DICOMDIR files
- Limited to referenced dataset loading

**Workaround:**
- Use external tools to create DICOMDIR
- v0.6.0 can load and work with existing DICOMDIR files
- Full creation support planned for future release

### 3. Image Preview

**Current Limitation:**
- Preview limited to 2D grayscale or RGB images
- 3D/4D data shown as first frame
- Some unusual formats may not display

**Workaround:**
- Use external viewers for complex image formats
- Image data still saved correctly in DICOM
- Preview-only; actual DICOM data intact

## Migration Guide

### From v0.5.0 to v0.6.0

**No Action Required:**
- All existing DICOM files remain compatible
- No database migration needed
- Settings and presets automatically upgraded

**Optional Enhancements:**
- Test tabs now hidden by default
- Enable via View ? Show All if needed
- Customize visible tabs using View menu

**New Workflow:**
1. Load or create DICOM file
2. Fill in metadata
3. Click File ? Validate to check data
4. Review validation report if needed
5. Save or Send with confidence

### For Developers

**If Using as Library:**
- New validation_dialog module available
- Enhanced vr_validator for more checks
- Better error handling in app_logic

**Import Changes:**
```python
# NEW in v0.6.0
from src.validation_dialog import ValidationDialog
from src.vr_validator import VRValidator

# Enhanced LazyImport
from src.import_helper import LazyImport
```

## Performance Impact

### Expected Performance

- **Load Time**: +0-5% (validation on load is minimal)
- **Save Time**: +2-5% (DICOM writing slightly longer due to verification)
- **UI Responsiveness**: No noticeable change
- **Memory Usage**: +5-10 MB (VR dictionary cache)

### Benchmarks

- Validate 100-field form: ~50ms
- Load and validate DICOM: ~200-500ms (depends on file size)
- Save with validation: ~100-200ms (depends on file size)

## Documentation

### New Documentation

- **[doc/CHANGELOG_v0.6.0.md](doc/CHANGELOG_v0.6.0.md)** (this file)
- Updated [README.md](../README.md) with v0.6.0 features
- Enhanced troubleshooting section with validation tips

### Updated Documentation

- README.md - Version badge and feature list
- Quick Start guides - Validation workflow
- Build Instructions - v0.6.0 build notes

## Testing

### Test Coverage

-  Validation system for all field types
-  DICOMDIR file loading
-  Private tag preservation
-  Group Length cleanup
-  Validation dialogs
-  Pre-save validation
-  Pre-send validation
-  Load validation
-  Error messages and recovery

### Test Commands

```bash
# Run all tests
python test/run_all_tests.py

# Run specific tests
python test/test_vr_validator.py
python test/test_validation_dialog.py
```

## Support & Feedback

### Report Issues

- GitHub Issues: https://github.com/piotrrozentreter/dcmcreator/issues
- Include DICOM Creator version (Help ? About)
- Attach application log file if available
- Describe steps to reproduce issue

### Feature Requests

- GitHub Discussions: https://github.com/piotrrozentreter/dcmcreator/discussions
- Reference v0.6.0 features you'd like enhanced
- Suggest new validation checks or improvements

## What's Next (Planned for v0.7.0+)

- **DICOMDIR Creation** - Generate DICOMDIR files
- **Advanced VR Validation** - Custom private tag validation
- **Performance Profiling** - Built-in performance metrics
- **Extended File Format Support** - Additional image formats
- **Batch Operations** - Process multiple DICOM files at once
- **Custom VR Rules** - User-defined validation rules

---

## Summary

Version 0.6.0 significantly improves DICOM data quality through comprehensive validation, better error reporting, and enhanced user experience. The new validation system helps ensure DICOM compliance, while improved UI and error messages make it easier to work with DICOM files correctly.

**Key Achievements:**
-  Comprehensive VR validation system
-  Better error messages and recovery
-  DICOMDIR support
-  Private tag preservation
-  Enhanced dialogs and UI
-  Improved module reliability
-  Better documentation

**For Users:**
- More confidence in DICOM data quality
- Clearer guidance on fixing issues
- Faster validation and error detection
- Cleaner UI with optional advanced features

**For Developers:**
- Better error handling and diagnostics
- More reliable module loading
- Enhanced logging for debugging
- Improved code structure

---

**Thank you for using DICOM Creator v0.6.0!**

For questions or feedback, please open an issue on GitHub:
https://github.com/piotrrozentreter/dcmcreator/issues
