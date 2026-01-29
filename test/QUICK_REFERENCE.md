# Test Scripts - Quick Reference

## Quick Commands

### Run All Tests
```bash
# Windows
run_tests.bat

# Linux/Mac
./run_tests.sh

# Cross-platform
python test/run_all_tests.py
```

### Run Individual Tests
```bash
python test/test_hierarchical_generation.py
python test/test_build.py
python test/verify_build.py
python test/test_tag_viewer.py
```

## Test Files

| File | Purpose | Time |
|------|---------|------|
| `test_hierarchical_generation.py` | Tests DICOM hierarchy generation | < 1s |
| `test_build.py` | Tests PyInstaller build | 2-5m |
| `verify_build.py` | Verifies build output | < 1s |
| `test_tag_viewer.py` | Tests tag viewer GUI | GUI |

## Expected Output

### Successful Test Run
```
======================================================================
Running 4 test script(s)
======================================================================

======================================================================
Running: test_build.py
======================================================================
[Test output...]
? test_build.py PASSED

======================================================================
Running: test_hierarchical_generation.py
======================================================================
[Test output...]
? test_hierarchical_generation.py PASSED

======================================================================
TEST SUMMARY
======================================================================
? PASSED     test_build.py
? PASSED     test_hierarchical_generation.py
? PASSED     test_tag_viewer.py
? PASSED     verify_build.py

======================================================================
Total: 4 | Passed: 4 | Failed: 0
======================================================================
```

## Test Requirements

### All Tests
- Python 3.9+

### DICOM Tests
- pydicom
- numpy

### Build Tests
- PyInstaller

### GUI Tests
- tkinter
- GUI environment (X11/Windows)

## Common Issues

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt
```

### GUI Tests Fail
- Run on machine with GUI
- Or skip GUI tests in headless environment

### Build Tests Fail
```bash
# Install build dependencies
pip install -r build-requirements.txt
```

## Adding New Tests

1. Create `test/test_yourtest.py`
2. Use template from `test/README.md`
3. Return 0 for success, non-zero for failure
4. Update `test/README.md`

## Test Template

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_feature():
    print("=" * 60)
    print("Testing Feature")
    print("=" * 60)
    
    try:
        # Test logic
        print("\n? All tests passed!")
        return True
    except Exception as e:
        print(f"\n? Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_feature()
    sys.exit(0 if success else 1)
```

## See Also

- `test/README.md` - Full test documentation
- `doc/COMPLETE_TEST_EXECUTION_REFERENCE.md` - Complete testing guide
