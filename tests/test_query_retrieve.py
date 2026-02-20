"""
Test script for C-FIND Query/Retrieve functionality.
Run this to verify the query module works correctly.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_module_import():
    """Test that the query module can be imported."""
    print("Testing module import...")
    try:
        from query_retrieve import DicomQueryHandler, QueryResult
        print("✓ Module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import module: {e}")
        return False

def test_handler_creation():
    """Test creating a query handler instance."""
    print("\nTesting handler creation...")
    try:
        from query_retrieve import DicomQueryHandler
        handler = DicomQueryHandler()
        print(f"✓ Handler created successfully")
        print(f"  Available: {handler.is_available()}")
        return True
    except Exception as e:
        print(f"✗ Failed to create handler: {e}")
        return False

def test_query_dataset_builder():
    """Test building query datasets."""
    print("\nTesting query dataset builder...")
    try:
        from query_retrieve import DicomQueryHandler, PYNETDICOM_AVAILABLE
        handler = DicomQueryHandler()

        if not PYNETDICOM_AVAILABLE:
            print("⚠ Skipping (pynetdicom not available)")
            return True

        # Test STUDY level query
        criteria = {
            'PatientName': 'DOE^JOHN',
            'StudyDate': '20240101-20240131',
            'Modality': 'CT'
        }

        ds = handler._build_query_dataset('STUDY', criteria)
        print("✓ Query dataset built successfully")
        print(f"  Query Level: {ds.QueryRetrieveLevel}")
        print(f"  Patient Name: {ds.PatientName}")
        print(f"  Study Date: {ds.StudyDate}")
        print(f"  Modality: {ds.Modality}")
        return True
    except Exception as e:
        print(f"✗ Failed to build query dataset: {e}")
        return False

def test_mock_query():
    """Test query with mock data (no actual PACS connection)."""
    print("\nTesting mock query...")
    try:
        from query_retrieve import DicomQueryHandler, QueryResult
        
        handler = DicomQueryHandler()
        
        # Create mock result
        result = QueryResult(
            level='STUDY',
            patient_id='12345',
            patient_name='DOE^JOHN',
            study_date='20240115',
            study_description='CT CHEST',
            modality='CT',
            accession_number='ACC123456'
        )
        
        print("✓ Mock query result created")
        print(f"  Patient: {result.patient_name} (ID: {result.patient_id})")
        print(f"  Study: {result.study_description}")
        print(f"  Date: {result.study_date}")
        print(f"  Modality: {result.modality}")
        
        # Test to_dict
        result_dict = result.to_dict()
        print(f"  Dict keys: {list(result_dict.keys())[:5]}...")
        
        return True
    except Exception as e:
        print(f"✗ Failed mock query: {e}")
        return False

def test_gui_integration():
    """Test that GUI can import and use the query module."""
    print("\nTesting GUI integration...")
    try:
        # Test LazyImport pattern
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        from import_helper import LazyImport
        
        DicomQueryHandler = LazyImport(".query_retrieve", "query_retrieve")
        
        # Try to load the class
        handler_cls = DicomQueryHandler._load_class()
        
        if handler_cls:
            print("✓ GUI LazyImport works correctly")
            handler = handler_cls()
            print(f"  Handler available: {handler.is_available()}")
            return True
        else:
            print("✗ LazyImport returned None")
            return False
            
    except Exception as e:
        print(f"✗ GUI integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("C-FIND Query/Retrieve Module Tests")
    print("=" * 60)
    
    tests = [
        test_module_import,
        test_handler_creation,
        test_query_dataset_builder,
        test_mock_query,
        test_gui_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Module is ready to use.")
        print("\nNext steps:")
        print("1. Configure PACS server in Query PACS tab")
        print("2. Try a simple STUDY query")
        print("3. Check logs if connection fails")
        return 0
    else:
        print("\n✗ Some tests failed. Check errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
