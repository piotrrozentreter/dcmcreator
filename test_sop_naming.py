"""
Diagnostic script to test SOP name lookup functionality.
Run this to see if SOP names are being loaded correctly.
"""

import sys
import os

# Add src to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_sop_utils():
    """Test the SOP utilities module."""
    print("=" * 70)
    print("SOP UTILS DIAGNOSTIC TEST")
    print("=" * 70)
    print()
    
    # Test 1: Import
    print("1. Testing import...")
    try:
        from sop_utils import load_sop_classes, get_sop_name, get_sop_name_only
        print("   ? Import successful")
    except Exception as e:
        print(f"   ? Import failed: {e}")
        return
    print()
    
    # Test 2: Load cache
    print("2. Loading SOP cache...")
    try:
        cache = load_sop_classes()
        print(f"   ? Cache loaded: {len(cache)} entries")
        
        # Show first 10 entries
        if cache:
            print("   First 10 entries:")
            for i, (uid, name) in enumerate(list(cache.items())[:10]):
                print(f"     {uid}: {name}")
        else:
            print("   ? WARNING: Cache is empty!")
    except Exception as e:
        print(f"   ? Failed to load cache: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 3: Test specific UIDs
    print("3. Testing specific SOP Class lookups...")
    test_uids = [
        '1.2.840.10008.5.1.4.1.1.2',    # CT Image Storage
        '1.2.840.10008.5.1.4.1.1.7',    # Secondary Capture
        '1.2.840.10008.5.1.4.1.1.6',    # Ultrasound
        '1.2.840.10008.1.1',             # Verification
        '1.2.840.10008.5.1.4.1.1.4',    # MR Image Storage
        '1.2.999.999.999'                # Unknown (for testing)
    ]
    
    for uid in test_uids:
        try:
            full_name = get_sop_name(uid)
            short_name = get_sop_name_only(uid)
            print(f"   {uid}")
            print(f"     Full:  {full_name}")
            print(f"     Short: {short_name}")
        except Exception as e:
            print(f"   ? Error looking up {uid}: {e}")
    print()
    
    # Test 4: Check pynetdicom version
    print("4. Checking pynetdicom installation...")
    try:
        import pynetdicom
        print(f"   ? pynetdicom version: {pynetdicom.__version__}")
        
        # Try different import methods
        print("   Trying import methods:")
        
        # Method 1
        try:
            from pynetdicom.uid import UID_dictionary
            print(f"     ? UID_dictionary available ({len(UID_dictionary)} entries)")
        except Exception as e:
            print(f"     ? UID_dictionary: {e}")
        
        # Method 2
        try:
            from pynetdicom._uid_dict import STANDARD_UID_DICT
            print(f"     ? STANDARD_UID_DICT available ({len(STANDARD_UID_DICT)} entries)")
        except Exception as e:
            print(f"     ? STANDARD_UID_DICT: {e}")
        
        # Method 3
        try:
            from pynetdicom import sop_class
            sop_classes = [attr for attr in dir(sop_class) if not attr.startswith('_')]
            print(f"     ? sop_class module available ({len(sop_classes)} classes)")
        except Exception as e:
            print(f"     ? sop_class: {e}")
            
    except ImportError:
        print("   ? pynetdicom not installed")
    print()
    
    # Test 5: Test with actual DICOM file (if available)
    print("5. Testing with loaded DICOM files...")
    try:
        import pydicom
        print("   ? pydicom available")
        
        # Check if there are any test files
        test_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.dcm'):
                    test_files.append(os.path.join(root, file))
                    if len(test_files) >= 3:
                        break
            if test_files:
                break
        
        if test_files:
            print(f"   Found {len(test_files)} DICOM file(s) to test:")
            for filepath in test_files:
                try:
                    ds = pydicom.dcmread(filepath)
                    sop_uid = str(ds.SOPClassUID)
                    sop_name = get_sop_name(sop_uid)
                    print(f"     File: {os.path.basename(filepath)}")
                    print(f"       SOP UID: {sop_uid}")
                    print(f"       SOP Name: {sop_name}")
                except Exception as e:
                    print(f"     ? Error reading {filepath}: {e}")
        else:
            print("   ? No DICOM files found for testing")
    except ImportError:
        print("   ? pydicom not installed")
    print()
    
    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_sop_utils()
