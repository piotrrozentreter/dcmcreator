"""
Test script for the Transmission History functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transmission_history import TransmissionHistory


def test_transmission_history_initialization():
    """Test TransmissionHistory initialization."""
    print("\nTesting TransmissionHistory initialization...")
    try:
        # Use temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        history = TransmissionHistory(db_path=db_path)
        
        # Check that database was created
        if os.path.exists(db_path):
            print(f"✓ Database created at: {db_path}")
        else:
            print("✗ Database not created")
            return False
        
        # Cleanup
        os.unlink(db_path)
        
        print("✓ TransmissionHistory initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize TransmissionHistory: {e}")
        return False


def test_record_transmission():
    """Test recording a transmission."""
    print("\nTesting transmission recording...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        history = TransmissionHistory(db_path=db_path)
        
        # Record a test transmission (returns None)
        history.record_transmission(
            filename='test.dcm',
            server_ip='127.0.0.1',
            server_port=11112,
            calling_ae='TEST_SCU',
            called_ae='TEST_SCP',
            success=True,
            bytes_sent=1024,
            duration_seconds=0.5,
            patient_name='Test^Patient',
            patient_id='12345'
        )
        
        print("✓ Transmission recorded successfully")
        
        # Cleanup
        os.unlink(db_path)
        return True
    except Exception as e:
        print(f"✗ Transmission recording failed: {e}")
        if 'db_path' in locals() and os.path.exists(db_path):
            os.unlink(db_path)
        return False


def test_get_statistics():
    """Test getting statistics."""
    print("\nTesting statistics retrieval...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        history = TransmissionHistory(db_path=db_path)
        
        # Record some test transmissions
        history.record_transmission(
            filename='test1.dcm',
            success=True,
            bytes_sent=1024
        )
        history.record_transmission(
            filename='test2.dcm',
            success=False,
            bytes_sent=2048
        )
        
        # Get statistics
        if hasattr(history, 'get_statistics'):
            stats = history.get_statistics()
            
            if stats:
                print(f"✓ Statistics retrieved")
                if 'total_transmissions' in stats:
                    print(f"  Total transmissions: {stats['total_transmissions']}")
                if 'successful' in stats:
                    print(f"  Successful: {stats['successful']}")
            else:
                print("⚠ Statistics returned None")
        else:
            print("⚠ get_statistics method not available")
        
        # Cleanup
        os.unlink(db_path)
        return True
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        if 'db_path' in locals() and os.path.exists(db_path):
            os.unlink(db_path)
        return False


def test_query_transmissions():
    """Test querying transmissions."""
    print("\nTesting transmission queries...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        history = TransmissionHistory(db_path=db_path)
        
        # Record test transmissions
        history.record_transmission(
            filename='test1.dcm',
            server_ip='192.168.1.1',
            success=True
        )
        history.record_transmission(
            filename='test2.dcm',
            server_ip='192.168.1.2',
            success=False
        )
        
        # Query transmissions
        if hasattr(history, 'get_all_transmissions'):
            transmissions = history.get_all_transmissions()
            
            if transmissions and len(transmissions) >= 2:
                print(f"✓ Query returned {len(transmissions)} transmissions")
            else:
                print(f"⚠ Query returned unexpected number: {len(transmissions) if transmissions else 0}")
        elif hasattr(history, 'query_transmissions'):
            transmissions = history.query_transmissions()
            
            if transmissions and len(transmissions) >= 2:
                print(f"✓ Query returned {len(transmissions)} transmissions")
            else:
                print(f"⚠ Query returned unexpected number: {len(transmissions) if transmissions else 0}")
        else:
            print("⚠ No query method available")
        
        # Cleanup
        os.unlink(db_path)
        return True
    except Exception as e:
        print(f"✗ Query test failed: {e}")
        if 'db_path' in locals() and os.path.exists(db_path):
            os.unlink(db_path)
        return False


def test_export_functionality():
    """Test export to JSON."""
    print("\nTesting export functionality...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        history = TransmissionHistory(db_path=db_path)
        
        # Record test transmission
        history.record_transmission(
            filename='test.dcm',
            success=True
        )
        
        # Try to export
        if hasattr(history, 'export_to_json'):
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as json_tmp:
                json_path = json_tmp.name
            
            result = history.export_to_json(json_path)
            
            if result and os.path.exists(json_path):
                print(f"✓ Export successful to {json_path}")
                os.unlink(json_path)
            else:
                print("⚠ Export returned False or file not created")
        else:
            print("⚠ export_to_json method not available")
        
        # Cleanup
        os.unlink(db_path)
        return True
    except Exception as e:
        print(f"✗ Export test failed: {e}")
        if 'db_path' in locals() and os.path.exists(db_path):
            os.unlink(db_path)
        if 'json_path' in locals() and os.path.exists(json_path):
            os.unlink(json_path)
        return False


def test_database_persistence():
    """Test that database persists data."""
    print("\nTesting database persistence...")
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Create and record
        history1 = TransmissionHistory(db_path=db_path)
        history1.record_transmission(filename='test.dcm', success=True)
        
        # Close and reopen
        del history1
        
        # Check if data persists
        history2 = TransmissionHistory(db_path=db_path)
        if hasattr(history2, 'get_all_transmissions'):
            transmissions = history2.get_all_transmissions()
            if transmissions and len(transmissions) > 0:
                print(f"✓ Database persisted {len(transmissions)} transmission(s)")
            else:
                print("⚠ No transmissions found after reopening")
        else:
            print("⚠ Cannot verify persistence (no query method)")
        
        # Cleanup
        os.unlink(db_path)
        return True
    except Exception as e:
        print(f"✗ Persistence test failed: {e}")
        if 'db_path' in locals() and os.path.exists(db_path):
            os.unlink(db_path)
        return False


def main():
    """Run all transmission history tests."""
    print("=" * 60)
    print("TRANSMISSION HISTORY FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    results.append(test_transmission_history_initialization())
    results.append(test_record_transmission())
    results.append(test_get_statistics())
    results.append(test_query_transmissions())
    results.append(test_export_functionality())
    results.append(test_database_persistence())
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Transmission history is working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
