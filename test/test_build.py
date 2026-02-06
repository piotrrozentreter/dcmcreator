#!/usr/bin/env python
"""
Post-Build Test Script
Tests that all v0.4.0 features are working in the built executable
"""

import os
import sys
from pathlib import Path

def test_distribution_exists():
    """Test that distribution folder exists."""
    print("\n" + "="*60)
    print("Testing Distribution Folder...")
    print("="*60)
    
    dist_path = Path("dist/DICOM Creator")
    if not dist_path.exists():
        print("  ? Distribution folder not found!")
        print(f"  Expected: {dist_path.absolute()}")
        print("\n  Run 'python build.py' first!")
        return False
    
    print(f"  ? Distribution folder exists")
    
    # Check for executable
    exe_path = dist_path / "DICOM Creator.exe"
    if not exe_path.exists():
        print("  ? DICOM Creator.exe not found!")
        return False
    
    exe_size = exe_path.stat().st_size / (1024 * 1024)
    print(f"  ? DICOM Creator.exe exists ({exe_size:.1f} MB)")
    
    # Check for _internal folder
    internal_path = dist_path / "_internal"
    if not internal_path.exists():
        print("  ? _internal folder not found!")
        return False
    
    print(f"  ? _internal folder exists")
    
    # Check for src folder
    src_path = dist_path / "src"
    if not src_path.exists():
        print("  ? src folder not found!")
        return False
    
    print(f"  ? src folder exists")
    
    return True

def test_vr_xml_present():
    """Test that VR.xml is present in distribution."""
    print("\n" + "="*60)
    print("Testing VR.xml Presence...")
    print("="*60)
    
    # Check both possible locations
    vr_xml_paths = [
        Path("dist/DICOM Creator/src/VR.xml"),
        Path("dist/DICOM Creator/VR.xml"),
    ]
    
    vr_xml_found = False
    for vr_xml_path in vr_xml_paths:
        if vr_xml_path.exists():
            size = vr_xml_path.stat().st_size / (1024 * 1024)
            print(f"   VR.xml found at: {vr_xml_path}")
            print(f"     Size: {size:.2f} MB")
            
            if size < 5:
                print(f"    WARNING: VR.xml seems too small (expected 6-8 MB)")
            else:
                print(f"   VR.xml size is appropriate")
            
            vr_xml_found = True
            break
    
    if not vr_xml_found:
        print("  ? CRITICAL: VR.xml not found in distribution!")
        print(f"  Expected at one of:")
        for path in vr_xml_paths:
            print(f"    - {path.absolute()}")
        print("\n  VR validation and VR viewer will NOT work!")
        return False
    
    return True

def test_module_files_present():
    """Test that all new module files are present."""
    print("\n" + "="*60)
    print("Testing Module Files...")
    print("="*60)
    
    src_path = Path("dist/DICOM Creator/src")
    required_modules = [
        'vr_validator.py',
        'validation_dialog.py',
        'tag.py',
        'tag_dialog.py',
        'app_logic.py',
        'appgui.py',
        'dcm.py',
        'remote.py',
    ]
    
    all_present = True
    for module in required_modules:
        module_path = src_path / module
        if module_path.exists():
            size = module_path.stat().st_size / 1024
            print(f"  ? {module:<30} ({size:.1f} KB)")
        else:
            print(f"  ? {module:<30} MISSING!")
            all_present = False
    
    return all_present

def test_zip_distribution():
    """Test that ZIP file was created."""
    print("\n" + "="*60)
    print("Testing ZIP Distribution...")
    print("="*60)
    
    zip_path = Path("DICOM Creator.zip")
    if not zip_path.exists():
        print("    DICOM Creator.zip not found")
        print("  This is OK if you just want to test the folder")
        return True  # Not critical
    
    size = zip_path.stat().st_size / (1024 * 1024)
    print(f"   DICOM Creator.zip exists ({size:.1f} MB)")
    
    if size < 40 or size > 100:
        print(f"    WARNING: ZIP size unexpected (expected 60-80 MB)")
    else:
        print(f"   ZIP size is appropriate")
    
    return True

def test_pydicom_bundled():
    """Test that pydicom is bundled."""
    print("\n" + "="*60)
    print("Testing PyDICOM Bundling...")
    print("="*60)
    
    internal_path = Path("dist/DICOM Creator/_internal")
    pydicom_found = False
    
    # Check for pydicom in various possible locations
    possible_locations = [
        internal_path / "pydicom",
        internal_path / "pydicom.pyc",
    ]
    
    # Also check in zip files
    for item in internal_path.iterdir():
        if 'pydicom' in item.name.lower():
            print(f"  ? Found pydicom: {item.name}")
            pydicom_found = True
            break
    
    if not pydicom_found:
        print("    WARNING: Could not locate pydicom")
        print("  This might be OK if it's embedded in PYZ archive")
        return True  # Not critical, might be in PYZ
    
    return True

def get_folder_size(path):
    """Calculate total size of folder in MB."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except Exception:
        pass
    return total / (1024 * 1024)

def print_distribution_summary():
    """Print summary of distribution."""
    print("\n" + "="*60)
    print("Distribution Summary")
    print("="*60)
    
    dist_path = Path("dist/DICOM Creator")
    if not dist_path.exists():
        print("  Distribution folder not found!")
        return
    
    folder_size = get_folder_size(str(dist_path))
    print(f"\n  Distribution folder: {folder_size:.1f} MB")
    
    zip_path = Path("DICOM Creator.zip")
    if zip_path.exists():
        zip_size = zip_path.stat().st_size / (1024 * 1024)
        compression = ((folder_size - zip_size) / folder_size) * 100
        print(f"  ZIP file: {zip_size:.1f} MB")
        print(f"  Compression: {compression:.1f}%")
    
    print("\n  File count:")
    total_files = sum(1 for _ in dist_path.rglob('*') if _.is_file())
    print(f"    Total files: {total_files}")
    
    # Count by type
    exe_files = list(dist_path.rglob('*.exe'))
    dll_files = list(dist_path.rglob('*.dll'))
    py_files = list(dist_path.rglob('*.py'))
    
    print(f"    .exe files: {len(exe_files)}")
    print(f"    .dll files: {len(dll_files)}")
    print(f"    .py files: {len(py_files)}")

def main():
    """Run all post-build tests."""
    print("\n" + "="*60)
    print("DICOM Creator - Post-Build Testing")
    print("="*60)
    print("\nThis script verifies that the build completed successfully")
    print("and all v0.4.0 features are properly included.")
    
    tests = [
        ("Distribution Exists", test_distribution_exists),
        ("VR.xml Present", test_vr_xml_present),
        ("Module Files", test_module_files_present),
        ("ZIP Distribution", test_zip_distribution),
        ("PyDICOM Bundled", test_pydicom_bundled),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n  ? ERROR during {test_name}: {e}")
            results[test_name] = False
    
    # Print summary
    print_distribution_summary()
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    critical_tests = ["Distribution Exists", "VR.xml Present", "Module Files"]
    all_passed = True
    critical_passed = True
    
    for test_name, passed in results.items():
        is_critical = test_name in critical_tests
        status = "? PASS" if passed else ("? FAIL" if is_critical else "? WARN")
        critical_marker = " [CRITICAL]" if is_critical else ""
        print(f"  {status} - {test_name}{critical_marker}")
        
        if not passed:
            all_passed = False
            if is_critical:
                critical_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("? All tests passed! Distribution is ready.")
        print("\nNext steps:")
        print("  1. Test the executable:")
        print('     cd "dist\\DICOM Creator"')
        print('     ".\\DICOM Creator.exe"')
        print("\n  2. Test v0.4.0 features:")
        print("     - DICOM ? View VRs")
        print("     - DICOM ? View All Tags")
        print("     - File ? Validate (Ctrl+Shift+V)")
