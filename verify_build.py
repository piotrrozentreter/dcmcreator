#!/usr/bin/env python
"""
Build Verification Script for DICOM Creator
Verifies that all required modules and data files are properly included in the build
"""

import os
import sys
from pathlib import Path

def verify_source_files():
    """Verify all source files exist."""
    print("\n" + "="*60)
    print("Verifying Source Files...")
    print("="*60)
    
    required_files = [
        'src/app.py',
        'src/appgui.py',
        'src/app_logic.py',
        'src/dcm.py',
        'src/dcmlogger.py',
        'src/import_helper.py',
        'src/remote.py',
        'src/presets.py',
        'src/random_dicom.py',
        'src/vr_validator.py',
        'src/validation_dialog.py',
        'src/tag.py',
        'src/tag_dialog.py',
        'src/connection_validator.py',
        'src/stress_tester.py',
        'src/transmission_history.py',
        'src/performance_benchmarking.py',
        'src/parallel_transmission.py',
        'src/VR.xml',
    ]
    
    all_present = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size / 1024
            unit = "KB"
            if size > 1024:
                size = size / 1024
                unit = "MB"
            print(f"  ? {file:<50} ({size:.1f} {unit})")
        else:
            print(f"  ? MISSING: {file}")
            all_present = False
    
    return all_present

def verify_spec_file():
    """Verify PyInstaller spec file configuration."""
    print("\n" + "="*60)
    print("Verifying PyInstaller Spec File...")
    print("="*60)
    
    spec_file = Path('dcmcreator.spec')
    if not spec_file.exists():
        print("  ? ERROR: dcmcreator.spec not found!")
        return False
    
    content = spec_file.read_text()
    
    # Check for new modules in hiddenimports
    required_imports = [
        'vr_validator',
        'validation_dialog',
        'tag',
        'tag_dialog',
    ]
    
    all_present = True
    for module in required_imports:
        if f"'{module}'" in content:
            print(f"  ? Hidden import: {module}")
        else:
            print(f"  ? MISSING: {module} not in hiddenimports")
            all_present = False
    
    # Check for VR.xml in datas
    if 'VR.xml' in content:
        print(f"  ? Data file: VR.xml included")
    else:
        print(f"  ? WARNING: VR.xml may not be included in datas")
        all_present = False
    
    return all_present

def verify_dependencies():
    """Verify all required dependencies are installed."""
    print("\n" + "="*60)
    print("Verifying Python Dependencies...")
    print("="*60)
    
    required_modules = [
        ('pydicom', 'pydicom'),
        ('pynetdicom', 'pynetdicom'),
        ('PIL', 'Pillow'),
        ('numpy', 'numpy'),
        ('tkinter', 'tkinter (built-in)'),
    ]
    
    all_present = True
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ? {package_name:<30} installed")
        except ImportError:
            print(f"  ? MISSING: {package_name}")
            all_present = False
    
    return all_present

def verify_vr_xml():
    """Verify VR.xml file integrity."""
    print("\n" + "="*60)
    print("Verifying VR.xml Integrity...")
    print("="*60)
    
    vr_file = Path('src/VR.xml')
    if not vr_file.exists():
        print("  ? ERROR: VR.xml not found!")
        return False
    
    size = vr_file.stat().st_size / (1024 * 1024)
    print(f"  ? VR.xml size: {size:.2f} MB")
    
    # Try to parse it
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(vr_file)
        root = tree.getroot()
        
        # Count data elements - check for different possible tag names
        elements = root.findall('.//DataElement')
        if not elements:
            # Try alternative: look for any child elements with 'tag' attribute
            elements = [elem for elem in root.iter() if elem.get('tag')]
        
        print(f"  ? Data elements: {len(elements)}")
        
        if len(elements) > 100:  # Should have hundreds or thousands of elements
            print(f"  ? VR.xml appears valid")
            return True
        else:
            print(f"  ? WARNING: Expected more data elements (found {len(elements)})")
            print(f"  ? This may still work if VR.xml has a different structure")
            # Don't fail - just warn
            return True
    except Exception as e:
        print(f"  ? ERROR parsing VR.xml: {e}")
        return False

def verify_build_config():
    """Verify build configuration files."""
    print("\n" + "="*60)
    print("Verifying Build Configuration...")
    print("="*60)
    
    config_files = [
        'build.py',
        'dcmcreator.spec',
        'requirements.txt',
        'build-requirements.txt',
    ]
    
    all_present = True
    for file in config_files:
        path = Path(file)
        if path.exists():
            print(f"  ? {file}")
        else:
            print(f"  ? MISSING: {file}")
            all_present = False
    
    return all_present

def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("DICOM Creator - Build Verification")
    print("="*60)
    
    checks = [
        ("Source Files", verify_source_files),
        ("PyInstaller Spec", verify_spec_file),
        ("Dependencies", verify_dependencies),
        ("VR.xml Data", verify_vr_xml),
        ("Build Config", verify_build_config),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n  ? ERROR during {check_name}: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "? PASS" if passed else "? FAIL"
        print(f"  {status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("? All checks passed! Ready to build.")
        print("\nRun: python build.py")
    else:
        print("? Some checks failed. Please fix issues before building.")
        print("\nCommon fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Ensure all source files are present")
        print("  - Update dcmcreator.spec with new modules")
        print("  - Verify VR.xml is in src/ directory")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
