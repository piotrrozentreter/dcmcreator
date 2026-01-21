# Hierarchical DICOM Generation

## Overview

The `RandomDicomGenerator` now supports **hierarchical DICOM generation**, which creates a realistic DICOM structure where files are properly organized into:

- **Patient** ? contains multiple **Studies**
- **Study** ? contains multiple **Series**
- **Series** ? contains multiple **Instances** (images)

## Features

### Proper DICOM Hierarchy

- All instances in the same series share the **same SeriesInstanceUID**
- All series in the same study share the **same StudyInstanceUID**
- All studies for the same patient share the **same PatientID and PatientName**

### File Naming Convention

Generated files follow this naming pattern:
```
patient_{PatientID}_study_{num}_series_{num}_inst_{num}.dcm
```

Example:
```
patient_TEST123456_study_01_series_01_inst_001.dcm
patient_TEST123456_study_01_series_01_inst_002.dcm
patient_TEST123456_study_01_series_02_inst_001.dcm
...
```

## Usage

### Python API

```python
from src.random_dicom import RandomDicomGenerator

generator = RandomDicomGenerator(logger=your_logger)

# Generate hierarchical DICOM structure
files = generator.generate_hierarchical(
    studies_per_patient=2,      # Generate 2 studies
    series_per_study=3,          # 3 series per study
    instances_per_series=5,      # 5 instances per series
    size_mb=1.0,                 # 1MB per file
    output_dir="./output",       # Save to directory
    patient_name="Test Patient", # Optional: custom patient name
    patient_id="TEST001"         # Optional: custom patient ID
)

# Total files = 2 × 3 × 5 = 30 files
print(f"Generated {len(files)} files")
```

### GUI Usage (Test/Generate Tab)

1. Open the application
2. Go to **View** ? **Test/Generate** to show the tab
3. In the Test/Generate tab:
   - **Studies/Patient**: Number of studies (default: 1)
   - **Series/Study**: Number of series per study (default: 1)
   - **Instances/Series**: Number of instances per series (default: 1)
   - **Size/File (MB)**: File size in megabytes (default: 1.0)
   - **Total Files**: Auto-calculated (Studies × Series × Instances)
4. Click **Browse** to select output directory
5. Click **Generate DICOMs**

### Example Scenarios

#### Simple Single Series (Default)
```
Studies/Patient: 1
Series/Study: 1
Instances/Series: 1
Total Files: 1
```
Generates 1 DICOM file.

#### Multiple Images in One Series
```
Studies/Patient: 1
Series/Study: 1
Instances/Series: 10
Total Files: 10
```
Generates 10 images all belonging to the same series.

#### Multiple Series in One Study
```
Studies/Patient: 1
Series/Study: 5
Instances/Series: 20
Total Files: 100
```
Generates 100 images organized into 5 series (20 images each).

#### Multiple Studies for One Patient
```
Studies/Patient: 3
Series/Study: 2
Instances/Series: 10
Total Files: 60
```
Generates 60 images organized into:
- 3 studies
- Each study has 2 series
- Each series has 10 instances

#### Large Test Dataset
```
Studies/Patient: 10
Series/Study: 5
Instances/Series: 20
Total Files: 1000
```
Generates 1000 images with realistic hierarchy for stress testing.

## Benefits

### 1. Realistic Testing
Generated files mimic real-world DICOM structures from medical imaging systems.

### 2. Load/Display Verification
Test how your DICOM viewer handles:
- Studies with multiple series
- Series with multiple instances
- Patient-level aggregation

### 3. Transmission Testing
Test DICOM transmission with proper study/series structure:
```python
# After generating hierarchical DICOMs
from src.dcm import load_dicom_grouped

# Load with proper grouping
grouped = load_dicom_grouped("./output")

# grouped structure:
# {
#   'StudyUID1': {
#     'SeriesUID1': [(dataset, pixel_array), ...],
#     'SeriesUID2': [(dataset, pixel_array), ...]
#   },
#   'StudyUID2': { ... }
# }
```

### 4. Query/Retrieve Testing
Test PACS query/retrieve functionality:
- Query at Patient level
- Query at Study level
- Query at Series level
- Retrieve specific series or entire studies

## Implementation Details

### UIDs and Consistency

The `generate_hierarchical()` method ensures:

1. **Patient Level**:
   - Same `PatientID` for all files
   - Same `PatientName` for all files
   - Consistent demographics (birth date, sex, etc.)

2. **Study Level**:
   - Unique `StudyInstanceUID` per study
   - Same `StudyDate` and `StudyTime` for all series in study
   - Same `AccessionNumber` per study
   - Consistent study metadata

3. **Series Level**:
   - Unique `SeriesInstanceUID` per series
   - Sequential `SeriesNumber` (1, 2, 3, ...)
   - Same `Modality` for all instances in series
   - Consistent series metadata

4. **Instance Level**:
   - Unique `SOPInstanceUID` per instance
   - Sequential `InstanceNumber` (1, 2, 3, ...)
   - Unique pixel data per instance

### File Size Calculation

The `size_mb` parameter determines image dimensions:
```
target_pixels = size_mb × 1024 × 1024 / 2
dimension = sqrt(target_pixels)
dimension = round_to_nearest_16(dimension)
dimension = clamp(256, 4096)
```

Examples:
- 0.5 MB ? ~512×512 pixels
- 1.0 MB ? ~724×724 ? 720×720 pixels
- 2.0 MB ? ~1024×1024 pixels
- 5.0 MB ? ~1616×1616 ? 1616×1616 pixels

### Metadata Variation

To create realistic test data, the generator adds variation:

- **Patient**: Age, weight, height, sex
- **Study**: Date (random within last year), time, description
- **Series**: Modality, body part, protocol
- **Operators**: Random physician/operator names

## Comparison with Flat Generation

### Old Method (`generate_with_sizes`)
```python
# Flat generation - each file is independent
files = generator.generate_with_sizes(
    count=30,
    size_mb=1.0,
    output_dir="./output"
)
# Result: 30 independent DICOM files
# Each has different PatientID, StudyUID, SeriesUID
```

### New Method (`generate_hierarchical`)
```python
# Hierarchical generation - proper structure
files = generator.generate_hierarchical(
    studies_per_patient=2,
    series_per_study=3,
    instances_per_series=5,
    size_mb=1.0,
    output_dir="./output"
)
# Result: 30 DICOM files with proper hierarchy
# 1 Patient ? 2 Studies ? 3 Series each ? 5 Instances each
```

## Testing the Feature

To test hierarchical generation:

1. **Via GUI**:
   ```
   - Open DICOM Creator
   - Enable Test/Generate tab (View ? Test/Generate)
   - Set: Studies=2, Series=3, Instances=5
   - Generate
   - Check Load DICOM tab to verify structure
   ```

2. **Via Python**:
   ```python
   from src.random_dicom import RandomDicomGenerator
   from src.dcm import load_dicom_grouped
   
   # Generate
   gen = RandomDicomGenerator()
   files = gen.generate_hierarchical(2, 3, 5, 1.0, "./test_output")
   
   # Verify structure
   grouped = load_dicom_grouped("./test_output")
   print(f"Studies: {len(grouped)}")
   for study_uid, series_map in grouped.items():
       print(f"  Series in study: {len(series_map)}")
       for series_uid, instances in series_map.items():
           print(f"    Instances in series: {len(instances)}")
   ```

3. **Expected Output**:
   ```
   Studies: 2
     Series in study: 3
       Instances in series: 5
       Instances in series: 5
       Instances in series: 5
     Series in study: 3
       Instances in series: 5
       Instances in series: 5
       Instances in series: 5
   ```

## Performance Considerations

### Generation Speed

Approximate generation speeds:

| Files | Size/File | Time    |
|-------|-----------|---------|
| 10    | 1 MB      | < 1s    |
| 100   | 1 MB      | ~5s     |
| 1000  | 1 MB      | ~50s    |
| 10    | 10 MB     | ~2s     |
| 100   | 10 MB     | ~20s    |

### Memory Usage

Memory scales with:
- Number of files (if generating in-memory)
- File size (larger dimensions = more pixel data)

For large datasets, use `output_dir` to save directly to disk.

## See Also

- `src/random_dicom.py` - Generator implementation
- `src/dcm.py` - DICOM loading and grouping
- `doc/RANDOM_DICOM_GENERATOR.md` - Complete generator documentation
- `doc/COMPLETE_TEST_EXECUTION_REFERENCE.md` - Testing guide
