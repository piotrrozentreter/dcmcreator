# Quick Start: DICOM Tag Viewer

## ?? Overview
View all DICOM tags from any file in seconds, including private vendor-specific tags.

---

## ? Quick Access

### From Menu
```
DICOM ? View All Tags
```

### Keyboard Shortcut
*Coming soon*

---

## ?? Common Use Cases

### 1. View Tags from Loaded File
**Steps:**
1. Load DICOM file (File ? Load)
2. Click **DICOM** ? **View All Tags**
3. Tags display automatically ?

**Result:** All tags from the current dataset appear in the viewer

---

### 2. View Tags from Any File
**Steps:**
1. Click **DICOM** ? **View All Tags**
2. Click "Yes" when prompted to select a file
3. Browse and select DICOM file
4. Tags display automatically ?

**Result:** Selected file's tags appear in the viewer

---

### 3. Search for Specific Tags
**Steps:**
1. Open Tag Viewer
2. Type in Search box (e.g., "Patient", "0010", "Study")
3. Results filter in real-time ?

**Searches:**
- Tag numbers (e.g., "0010,0010")
- Tag names (e.g., "PatientName")
- Tag values (e.g., "John Doe")

---

### 4. View Private Tags Only
**Steps:**
1. Open Tag Viewer
2. Look for tags in **blue** color
3. These are private/vendor-specific tags ?

**Tip:** Uncheck "Show Private Tags" to hide them

---

### 5. Export Tags to Text File
**Steps:**
1. Open Tag Viewer
2. Click **Export to Text**
3. Choose filename and location
4. File saved ?

**Format:** Clean, readable text format with all tag information

---

## ?? Understanding the Display

### Tag Viewer Columns

| Column | Description | Example |
|--------|-------------|---------|
| **Tag** | DICOM tag number | (0010,0010) |
| **Name** | Element name | PatientName |
| **VR** | Value Representation | PN |
| **VM** | Value Multiplicity | 1 |
| **Value** | Actual data | DOE^JOHN |
| **Type** | Public or Private | Public |

### Color Coding
- **Black text** = Public tags (standard DICOM)
- **Blue text** = Private tags (vendor-specific)

---

## ?? Pro Tips

### Sorting
**Click any column header to sort by that column**
- Click once: Sort ascending
- Click again: Sort descending

### Filtering
**Combine search with private tag filter:**
1. Uncheck "Show Private Tags"
2. Type search term
3. See only matching public tags

### Statistics
**Click "Statistics" button to see:**
- Total tag count
- Public vs. Private breakdown
- Top 10 Value Representations

---

## ?? Common Questions

### Q: Why are some tags empty?
**A:** Empty tags show `<empty>` - this is normal for optional elements

### Q: What are private tags?
**A:** Vendor-specific tags (odd group numbers like 0009, 0011) used by manufacturers

### Q: Can I edit tags?
**A:** Not yet - view-only in v0.4.0 (editing planned for future)

### Q: How do I copy a tag value?
**A:** Export to text, then copy from the file (clipboard coming soon)

### Q: What does [Sequence with N items] mean?
**A:** The tag contains nested datasets (N items inside)

---

## ?? Next Steps

### Learn More
- Read [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md) for complete documentation
- Check [CHANGELOG_v0.4.0.md](CHANGELOG_v0.4.0.md) for all features

### Try It Out
1. Load a sample DICOM file
2. Open Tag Viewer
3. Search for "Patient"
4. Export tags to text
5. View statistics

---

## ?? Need Help?

### Troubleshooting
- **"No tags to display"** ? File may not be valid DICOM
- **"pydicom not available"** ? Install with `pip install pydicom`
- **Slow loading** ? Large files (>500 tags) take a few seconds

### Documentation
- Full guide: [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md)
- Main docs: [INDEX.md](INDEX.md)

---

## Version Info
- Feature introduced in v0.4.0
- Status: Production Ready ?
