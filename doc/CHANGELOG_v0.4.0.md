# Release Notes - Version 0.4.0

## Version 0.4.0 - DICOM Tag Viewer & Enhanced Validation

###  Overview
Version 0.4.0 introduces powerful DICOM inspection and validation capabilities, making it easier to view, analyze, and validate DICOM data.

---

##  New Features

### DICOM Tag Viewer
View all DICOM tags from any file, including private vendor-specific tags.

#### Key Capabilities
- **Complete Tag Display** - View all public and private DICOM tags
- **Hierarchical View** - Nested sequences displayed with proper indentation
- **Search & Filter** - Find tags by tag number, name, or value
- **Private Tag Support** - Color-coded display of private tags (blue)
- **Export** - Save tags to text file for documentation
- **Statistics** - View summary of tag counts and VR distribution
- **Sortable Columns** - Click any column header to sort

#### Tag Information Displayed
- Tag number (GGGG,EEEE)
- Element name
- Value Representation (VR)
- Value Multiplicity (VM)
- Data value (truncated if long)
- Type (Public/Private)

#### How to Access
1. **From Menu**: DICOM ? View All Tags
2. **With Loaded File**: Automatically shows tags from current dataset
3. **Select File**: Prompted to select a DICOM file if none loaded

#### New Files
- `src/tag.py` - Core tag extraction logic
- `src/tag_dialog.py` - Tag viewer dialog UI
- `doc/TAG_VIEWER_FEATURE.md` - Complete documentation
- `test_tag_viewer.py` - Test script

---

### Value Representation Validator
Enhanced validation for DICOM data elements against VR specifications.

#### Features
- **Automatic Validation** - Validates form fields on save/send
- **VR Dictionary** - Built-in DICOM VR specifications from PS3.5
- **Validation Report** - Detailed error and warning messages
- **Interactive Prompts** - Option to continue or cancel on validation issues

#### Validation Triggers
- Manual: File ? Validate (Ctrl+V)
- Automatic: Before Save or Send operations
- On Load: Warnings for loaded DICOM with issues

---

### UI Enhancements

#### DICOM Menu
New menu items added:
- **View VRs** - Browse DICOM Value Representations
- **View All Tags** - Open Tag Viewer dialog

#### Validation Integration
- Validation dialog with detailed error/warning display
- Color-coded messages (red for errors, yellow for warnings)
- Statistics summary at top of validation report

---

##  Technical Improvements

### LazyImport Enhancements
- Improved class extraction for modules with multiple classes
- Better handling of ConnectionValidator and other complex modules
- Explicit class prioritization for ambiguous imports

### Code Organization
- New validation framework
- Separation of concerns (tag logic vs. UI)
- Enhanced error handling throughout

---

##  Documentation Updates

### New Documentation
- **TAG_VIEWER_FEATURE.md** - Complete Tag Viewer guide
  - Usage examples
  - Feature descriptions
  - Technical details
  - Troubleshooting

### Updated Documentation
- **README.md** - Added Tag Viewer to core features
- **INDEX.md** - New section for DICOM inspection tools
- **Project Structure** - Updated with new modules

---

##  Compatibility

### Requirements
- Python 3.9+
- pydicom (required for tag reading)
- tkinter (standard library)
- All existing dependencies remain unchanged

### Backward Compatibility
-  Fully backward compatible with v0.3.x
-  Existing presets and configurations preserved
-  No breaking changes to existing features

---

##  Bug Fixes

### LazyImport
- Fixed ConnectionValidator loading issue
- Improved error reporting for failed imports
- Better class detection in modules

### UI
- Fixed VR Viewer dialog styling
- Improved error messages for missing modules

---

##  File Changes

### New Files
```
src/
 tag.py                   (Tag extraction logic)
 tag_dialog.py           (Tag viewer UI)
 vr_validator.py         (VR validation logic)
 validation_dialog.py    (Validation UI)

doc/
 TAG_VIEWER_FEATURE.md   (Tag viewer documentation)

test_tag_viewer.py          (Test suite)
```

### Modified Files
```
src/appgui.py               (Added Tag Viewer menu & integration)
src/import_helper.py        (Enhanced LazyImport)
README.md                   (Updated features & structure)
doc/INDEX.md                (Added new documentation links)
```

---

##  Usage Examples

### View All Tags
```python
# In the application
1. Load a DICOM file (File ? Load)
2. Click DICOM ? View All Tags
3. Browse, search, and export tags
```

### Export Tags
```python
# In Tag Viewer dialog
1. Click "Export to Text"
2. Select destination file
3. Tags saved as formatted text
```

### Validate Data
```python
# Manual validation
1. Fill in form fields
2. Click File ? Validate (Ctrl+V)
3. Review validation report
```

---

##  Learning Resources

### For Users
- Read [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md) for complete guide
- Try viewing tags from sample DICOM files
- Experiment with search and filter features

### For Developers
- Review `src/tag.py` for tag extraction API
- Study `src/tag_dialog.py` for UI patterns
- Check `test_tag_viewer.py` for usage examples

---

##  Future Enhancements

### Planned for Future Versions
- Edit tag values directly in viewer
- Compare tags between files
- Tag validation against VR specifications
- Bulk export multiple files
- Tag value copy to clipboard

---

##  Statistics

- **New Features**: 2 (Tag Viewer, VR Validator)
- **New Files**: 5
- **Modified Files**: 4
- **Documentation**: 2 new docs, 3 updated
- **Lines of Code**: ~1,500 added
- **Test Coverage**: New test suite added

---

##  Acknowledgments

Special thanks to the DICOM community for PS3.5 and PS3.6 specifications.

---

##  Support

### Issues & Questions
- Check [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md) for troubleshooting
- Review error messages in the application log
- Ensure pydicom is installed and up to date

### Known Limitations
- Very large DICOM files (>500 tags) may load slowly
- Some proprietary private tags may not have descriptive names
- Sequence nesting display is limited to visual indentation

---

## Version Info

- **Version**: 0.4.0
- **Release Date**: 2025-2026
- **Status**: Production Ready
- **Author**: Piotr Rozentreter (Hyland)
- **Previous Version**: 0.3.0 (Server Presets)

---

## Quick Links

- [Main README](../README.md)
- [Tag Viewer Documentation](TAG_VIEWER_FEATURE.md)
- [Documentation Index](INDEX.md)
- [Previous Release (v0.3.0)](CHANGELOG_v0.3.0.md)
