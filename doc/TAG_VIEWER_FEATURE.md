# DICOM Tag Viewer Feature

## Overview
The DICOM Tag Viewer allows you to view all DICOM tags from a file, including private tags and their corresponding data.

## Files Created
1. **src/tag.py** - Core logic for reading and extracting DICOM tags
2. **src/tag_dialog.py** - Dialog UI for displaying tags
3. **test_tag_viewer.py** - Test script to verify the implementation

## How to Use

### Method 1: From Menu (Recommended)
1. Launch the application: `python main.py`
2. Go to **DICOM** menu ? **View All Tags**
3. Options:
   - If a DICOM file is already loaded, tags will be displayed automatically
   - If no file is loaded, you'll be prompted to select a DICOM file

### Method 2: Load DICOM First
1. Load a DICOM file using **File** ? **Load** or **Load Folder**
2. Select a study/series from the tree view (optional)
3. Go to **DICOM** menu ? **View All Tags**
4. The tags from the selected or first series will be displayed

## Features

### Tag Display
- **Tag Number**: (GGGG,EEEE) format
- **Name**: DICOM element name
- **VR**: Value Representation
- **VM**: Value Multiplicity
- **Value**: Actual data (truncated if too long)
- **Type**: Public or Private tag indicator

### Filtering
- **Show Private Tags**: Toggle checkbox to show/hide private tags
- **Search**: Filter tags by tag number, name, or value
- **Type Indicator**: Private tags are shown in blue color

### Additional Features
- **Export to Text**: Save all tags to a text file
- **Statistics**: View summary of tag counts and VR distribution
- **Sorting**: Click column headers to sort by any field
- **Hierarchical Display**: Sequence items are shown with indentation

## Tag Types

### Public Tags
Standard DICOM tags defined in PS3.6 Data Dictionary
- Example: (0010,0010) Patient Name

### Private Tags
Vendor-specific or custom tags
- Group number is odd (e.g., 0009, 0011, etc.)
- Example: (0009,1001) Private Creator
- Displayed in blue color for easy identification

### Sequence Tags
Tags containing nested datasets
- VR: SQ
- Shows number of items: [Sequence with N item(s)]
- Nested items shown with indentation

## Code Structure

### src/tag.py
Core functions:
- `get_all_tags_from_file(filepath)` - Read tags from a file
- `get_all_tags_from_dataset(ds)` - Extract tags from a dataset
- `extract_tags_from_dataset(ds)` - Recursively extract all tags
- `extract_tag_info(elem)` - Get info from a single element
- `format_tag_list(tags)` - Format tags as text
- `get_tag_statistics(tags)` - Generate statistics

### src/tag_dialog.py
UI components:
- `TagViewerDialog` - Main dialog class
- `show_tag_viewer()` - Helper function to show dialog
- Tree view with sorting and filtering
- Export and statistics features

### src/appgui.py (modified)
Integration:
- Added import for TagViewerDialog
- Added "View All Tags" menu item to DICOM menu
- Added `show_tag_viewer()` method

## Usage Examples

### Example 1: View tags from loaded DICOM
```python
# In the application
# 1. Load DICOM file via File menu
# 2. Click DICOM ? View All Tags
# Tags from the loaded file are displayed
```

### Example 2: View tags from any file
```python
# In the application
# 1. Click DICOM ? View All Tags (without loading a file)
# 2. Select a DICOM file when prompted
# Tags from the selected file are displayed
```

### Example 3: Programmatic usage
```python
from src.tag import get_all_tags_from_file, format_tag_list

# Read tags from file
success, tags = get_all_tags_from_file("path/to/file.dcm")

if success:
    # Print formatted list
    print(format_tag_list(tags))
    
    # Get statistics
    from src.tag import get_tag_statistics
    stats = get_tag_statistics(tags)
    print(f"Total tags: {stats['total']}")
    print(f"Private tags: {stats['private']}")
```

## Technical Details

### Dependencies
- **pydicom**: Required for reading DICOM files
- **tkinter**: For GUI components (standard library)

### Error Handling
- Graceful handling of corrupted tags
- Error messages displayed for problematic elements
- Logger integration for debugging

### Performance
- Efficient recursive extraction for sequences
- Lazy loading of tag data
- Optimized tree view population

## Testing
Run the test script to verify installation:
```bash
python test_tag_viewer.py
```

Expected output: "All tests passed!"

## Troubleshooting

### Issue: "Tag Viewer is not available"
**Solution**: Check that tag_dialog.py is in the src/ directory

### Issue: "No DICOM loaded"
**Solution**: 
- Load a DICOM file first, OR
- Click "Yes" when prompted to select a file

### Issue: Tags not displaying
**Solution**: 
- Ensure pydicom is installed: `pip install pydicom`
- Check that the file is a valid DICOM file

### Issue: Private tags not showing
**Solution**: Ensure "Show Private Tags" checkbox is enabled

## Future Enhancements
Potential improvements:
- Edit tag values directly
- Copy tags to clipboard
- Compare tags between files
- Tag validation against VR specifications
- Bulk export multiple files

## Related Features
- **VR Viewer** (DICOM ? View VRs): View DICOM Value Representations
- **Validation** (File ? Validate): Validate form fields against VR specs

## References
- DICOM PS3.5: Data Structures and Encoding
- DICOM PS3.6: Data Dictionary
- pydicom documentation: https://pydicom.github.io/
