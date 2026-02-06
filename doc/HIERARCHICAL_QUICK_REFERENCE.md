# Hierarchical DICOM Generation - Quick Reference

## UI Quick Start

### Test/Generate Tab Layout
```
??????????????????????????????????????????????????????
? Studies/Patient:    [1]    Series/Study:      [1]  ?
? Instances/Series:   [1]    Size/File (MB):    [1.0]?
? Total Files:         1     (auto-calculated)       ?
? Output Dir:         [________________] [Browse]    ?
? [Generate DICOMs] [Generate & Send]               ?
??????????????????????????????????????????????????????
```

## Common Configurations

### Single DICOM File
```
Studies: 1 | Series: 1 | Instances: 1 = 1 file
```

### CT Scan (50 slices)
```
Studies: 1 | Series: 1 | Instances: 50 = 50 files
```

### MRI Study (4 sequences, 25 slices each)
```
Studies: 1 | Series: 4 | Instances: 25 = 100 files
```

### Patient Follow-ups (3 visits, 2 series each, 20 images)
```
Studies: 3 | Series: 2 | Instances: 20 = 120 files
```

### Stress Test Dataset
```
Studies: 10 | Series: 5 | Instances: 20 = 1000 files
```

## File Structure

### Generated Hierarchy
```
Patient: TEST123456
??? Study 1 (StudyUID_A)
?   ??? Series 1 (SeriesUID_A1)
?   ?   ??? Instance 1
?   ?   ??? Instance 2
?   ?   ??? Instance 3
?   ??? Series 2 (SeriesUID_A2)
?       ??? Instance 1
?       ??? Instance 2
??? Study 2 (StudyUID_B)
    ??? Series 1 (SeriesUID_B1)
        ??? Instance 1
        ??? Instance 2
```

### File Names
```
patient_TEST123456_study_01_series_01_inst_001.dcm
patient_TEST123456_study_01_series_01_inst_002.dcm
patient_TEST123456_study_01_series_02_inst_001.dcm
patient_TEST123456_study_02_series_01_inst_001.dcm
```

## Python API

### Basic Usage
```python
from src.random_dicom import RandomDicomGenerator

gen = RandomDicomGenerator()
files = gen.generate_hierarchical(
    studies_per_patient=2,
    series_per_study=3,
    instances_per_series=5,
    size_mb=1.0,
    output_dir="./output"
)
# Result: 30 files (2×3×5)
```

### Custom Patient
```python
files = gen.generate_hierarchical(
    studies_per_patient=1,
    series_per_study=1,
    instances_per_series=10,
    size_mb=1.0,
    output_dir="./output",
    patient_name="John Doe",
    patient_id="PATIENT001"
)
```

### In-Memory Generation
```python
# No output_dir = returns dataset objects
datasets = gen.generate_hierarchical(
    studies_per_patient=1,
    series_per_study=2,
    instances_per_series=5,
    size_mb=0.5,
    output_dir=None  # In-memory
)
```

## Verification

### Load and Check Structure
```python
from src.dcm import load_dicom_grouped

grouped = load_dicom_grouped("./output")

# Print structure
for study_uid, series_map in grouped.items():
    print(f"Study: {study_uid[:20]}...")
    for series_uid, instances in series_map.items():
        print(f"  Series: {series_uid[:20]}... ({len(instances)} files)")
```

### Expected Output
```
Study: 1.2.840.113619.2...
  Series: 1.2.840.113619.2... (5 files)
  Series: 1.2.840.113619.2... (5 files)
Study: 1.2.840.113619.2...
  Series: 1.2.840.113619.2... (5 files)
```

## Performance Guide

### Generation Speed
| Files | Size    | Time  |
|-------|---------|-------|
| 10    | 1 MB    | < 1s  |
| 100   | 1 MB    | ~5s   |
| 1000  | 1 MB    | ~50s  |

### File Size Formula
```
0.5 MB ? ~512×512 pixels
1.0 MB ? ~720×720 pixels
2.0 MB ? ~1024×1024 pixels
5.0 MB ? ~1616×1616 pixels
```

## Use Cases

### Testing Viewer Organization
```
Studies: 1 | Series: 5 | Instances: 20
• Tests series grouping in viewer
```

### Testing PACS Archive
```
Studies: 10 | Series: 3 | Instances: 10
• Tests multi-study storage
```

### Testing Transmission
```
Studies: 2 | Series: 4 | Instances: 25
• Tests hierarchical C-STORE
```

### Load Testing
```
Studies: 20 | Series: 5 | Instances: 10
• Generates 1000 files for stress test
```

## Troubleshooting

### Problem: Total shows "?"
**Solution**: Enter valid numbers in all three fields

### Problem: Generation too slow
**Solutions**:
- Reduce file size (e.g., 0.5 MB instead of 5 MB)
- Generate fewer files
- Check disk speed

### Problem: Files not grouped correctly
**Solution**: Use `load_dicom_grouped()` to properly load hierarchy

### Problem: Out of memory
**Solution**: Always specify `output_dir` for large generations

## Keyboard Shortcuts

In GUI:
- `Ctrl+N` - New file
- `Ctrl+O` - Load DICOM file(s)
- `Ctrl+Shift+O` - Load folder
- `Ctrl+S` - Save DICOM
- `Ctrl+R` - Send to remote

## Related Documentation

- **doc/HIERARCHICAL_GENERATION.md** - Complete user guide
- **doc/HIERARCHICAL_IMPLEMENTATION.md** - Technical details
- **doc/RANDOM_DICOM_GENERATOR.md** - Generator documentation
