# Test Scripts

This directory contains test and verification scripts for the DICOM Creator application.

## Test Scripts

### test_build.py
**Purpose**: Build system test script  
**Description**: Tests the PyInstaller build process and verifies the executable is created correctly.  
**Usage**:
```bash
python test/test_build.py
```
**Dependencies**: PyInstaller, build environment

---

### test_hierarchical_generation.py
**Purpose**: Hierarchical DICOM generation test  
**Description**: Tests the new hierarchical DICOM generation feature, verifying that:
- Proper hierarchy is created (Patient ? Study ? Series ? Instance)
- UIDs are consistent within hierarchy levels
- Correct number of files are generated
- All files belong to the same patient

**Usage**:
```bash
python test/test_hierarchical_generation.py
```
**Dependencies**: pydicom, numpy

**Expected Output**:
```
============================================================
Testing Hierarchical DICOM Generation
============================================================

Generating hierarchy:
  Studies: 2
  Series per study: 3
  Instances per series: 2
  Total files: 12

? Generated 12 datasets
Verifying hierarchy...
  Studies found: 2
  ? All files belong to same patient
  ? Correct number of studies: 2
  ? Study has correct number of series: 3
  ? Series has correct number of instances: 2

============================================================
? All tests passed!
============================================================
```

---

### test_tag_viewer.py
**Purpose**: DICOM tag viewer dialog test  
**Description**: Tests the tag viewer dialog functionality for displaying DICOM tags.  
**Usage**:
```bash
python test/test_tag_viewer.py
```
**Dependencies**: pydicom, tkinter, GUI environment

---

### verify_build.py
**Purpose**: Build verification script  
**Description**: Verifies the built executable and checks:
- File exists and is executable
- Size is reasonable
- Version information is correct
- Required dependencies are bundled

**Usage**:
```bash
python test/verify_build.py
```
**Dependencies**: None (standalone verification)

---

## Running All Tests

To run all tests in sequence:

```bash
# Windows PowerShell
Get-ChildItem -Path test -Filter "test_*.py" | ForEach-Object { python $_.FullName }

# Windows Command Prompt
for %f in (test\test_*.py) do python %f

# Linux/Mac
for f in test/test_*.py; do python "$f"; done
```

## Test Categories

### Unit Tests
- `test_hierarchical_generation.py` - Tests DICOM generation logic

### Integration Tests
- `test_tag_viewer.py` - Tests GUI component integration

### Build Tests
- `test_build.py` - Tests build process
- `verify_build.py` - Verifies build output

## Adding New Tests

When adding new test scripts:

1. **Name**: Use `test_*.py` prefix for test files
2. **Location**: Place in this `test/` directory
3. **Documentation**: Update this README with test description
4. **Exit Code**: Return 0 for success, non-zero for failure
5. **Output**: Print clear success/failure messages

### Test Template

```python
"""
Test script for [feature name].

Description: [what this test does]
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_feature():
    """Test the feature."""
    print("=" * 60)
    print("Testing [Feature Name]")
    print("=" * 60)
    
    try:
        # Test logic here
        
        print("\n? All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n? Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_feature()
    sys.exit(0 if success else 1)
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python test/test_hierarchical_generation.py
    python test/test_build.py
```

## Dependencies

Most tests require:
- Python 3.8+
- pydicom
- numpy
- tkinter (for GUI tests)

Install with:
```bash
pip install pydicom numpy pillow
```

## Test Coverage

Current test coverage:
- ? DICOM generation
- ? Build process
- ? Tag viewer
- ? Build verification

Planned tests:
- [ ] Remote transmission tests
- [ ] Validation tests
- [ ] Performance tests
- [ ] Load/save tests

## See Also

- `doc/COMPLETE_TEST_EXECUTION_REFERENCE.md` - Complete testing guide
- `doc/QUICK_TEST_EXECUTION_GUIDE.md` - Quick testing reference
- `doc/WHERE_TO_RUN_TESTS.md` - Test execution environments
- `examples/` - Example scripts (not tests)

