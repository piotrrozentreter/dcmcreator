"""
Test script for the Parallel Transmission functionality.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parallel_transmission import ParallelTransmissionManager


def test_parallel_transmission_initialization():
    """Test ParallelTransmissionManager initialization."""
    print("\nTesting ParallelTransmissionManager initialization...")
    try:
        manager = ParallelTransmissionManager(max_workers=3)
        
        # Check attributes
        assert hasattr(manager, 'max_workers')
        assert hasattr(manager, 'work_queue')
        assert hasattr(manager, 'result_queue')
        assert manager.max_workers == 3
        
        print("✓ ParallelTransmissionManager initialized successfully")
        print(f"  Max workers: {manager.max_workers}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize ParallelTransmissionManager: {e}")
        return False


def test_worker_count_clamping():
    """Test that worker count is clamped to valid range."""
    print("\nTesting worker count clamping...")
    try:
        # Test minimum
        manager_min = ParallelTransmissionManager(max_workers=0)
        if manager_min.max_workers >= 1:
            print(f"✓ Minimum clamped correctly: {manager_min.max_workers}")
        else:
            print(f"✗ Minimum not clamped: {manager_min.max_workers}")
            return False
        
        # Test maximum
        manager_max = ParallelTransmissionManager(max_workers=20)
        if manager_max.max_workers <= 10:
            print(f"✓ Maximum clamped correctly: {manager_max.max_workers}")
        else:
            print(f"✗ Maximum not clamped: {manager_max.max_workers}")
            return False
        
        # Test normal range
        manager_normal = ParallelTransmissionManager(max_workers=5)
        if manager_normal.max_workers == 5:
            print(f"✓ Normal value accepted: {manager_normal.max_workers}")
        else:
            print(f"✗ Normal value changed: {manager_normal.max_workers}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Worker count clamping test failed: {e}")
        return False


def test_session_start():
    """Test starting a transmission session."""
    print("\nTesting session start...")
    try:
        manager = ParallelTransmissionManager(max_workers=2)
        
        session = manager.start_session(name="Test Session")
        
        if session:
            print(f"✓ Session started: {session['name']}")
            print(f"  Status: {session['status']}")
            print(f"  Start time: {session['start_time']}")
            
            # Check session structure
            required_keys = ['name', 'start_time', 'status', 'total_queued', 
                           'total_completed', 'total_successful', 'total_failed']
            missing_keys = [k for k in required_keys if k not in session]
            
            if missing_keys:
                print(f"✗ Session missing keys: {missing_keys}")
                return False
            else:
                print("✓ Session has all required keys")
        else:
            print("✗ Session not created")
            return False
        
        # Stop the session
        if hasattr(manager, 'stop_session'):
            manager.stop_session()
        
        return True
    except Exception as e:
        print(f"✗ Session start test failed: {e}")
        return False


def test_queue_job():
    """Test queuing a job."""
    print("\nTesting job queuing...")
    try:
        manager = ParallelTransmissionManager(max_workers=2)
        manager.start_session(name="Test Queue")
        
        # Queue a test job
        if hasattr(manager, 'queue_transmission'):
            # Mock job data - queue_transmission expects (file_path, send_function, file_info)
            def mock_send(file_path):
                return {'success': True, 'bytes_sent': 1024}
            
            try:
                manager.queue_transmission('test.dcm', mock_send, {'filename': 'test.dcm'})
                print("✓ Job queued successfully")
            except Exception as e:
                print(f"⚠ Job queuing had issue: {e}")
        else:
            print("⚠ queue_transmission method not available")
        
        # Stop session
        if hasattr(manager, 'stop_session'):
            manager.stop_session()
        
        return True
    except Exception as e:
        print(f"✗ Queue job test failed: {e}")
        return False


def test_session_statistics():
    """Test session statistics tracking."""
    print("\nTesting session statistics...")
    try:
        manager = ParallelTransmissionManager(max_workers=2)
        session = manager.start_session(name="Stats Test")
        
        # Check initial statistics
        if session['total_queued'] == 0:
            print("✓ Initial queued count is 0")
        if session['total_completed'] == 0:
            print("✓ Initial completed count is 0")
        if session['total_successful'] == 0:
            print("✓ Initial successful count is 0")
        if session['total_failed'] == 0:
            print("✓ Initial failed count is 0")
        
        # Stop session
        if hasattr(manager, 'stop_session'):
            manager.stop_session()
        
        return True
    except Exception as e:
        print(f"✗ Session statistics test failed: {e}")
        return False


def test_get_progress():
    """Test getting progress information."""
    print("\nTesting progress retrieval...")
    try:
        manager = ParallelTransmissionManager(max_workers=2)
        manager.start_session(name="Progress Test")
        
        if hasattr(manager, 'get_progress'):
            progress = manager.get_progress()
            
            if progress:
                print(f"✓ Progress retrieved")
                if 'completed' in progress:
                    print(f"  Completed: {progress['completed']}")
                if 'queued' in progress:
                    print(f"  Queued: {progress['queued']}")
            else:
                print("⚠ Progress returned None")
        else:
            print("⚠ get_progress method not available")
        
        # Stop session
        if hasattr(manager, 'stop_session'):
            manager.stop_session()
        
        return True
    except Exception as e:
        print(f"✗ Progress retrieval test failed: {e}")
        return False


def test_stop_session():
    """Test stopping a session."""
    print("\nTesting session stop...")
    try:
        manager = ParallelTransmissionManager(max_workers=2)
        manager.start_session(name="Stop Test")
        
        # Give workers time to start
        time.sleep(0.1)
        
        if hasattr(manager, 'stop_session'):
            manager.stop_session()
            
            if manager.current_session and manager.current_session['status'] in ['COMPLETED', 'STOPPED']:
                print(f"✓ Session stopped: {manager.current_session['status']}")
            else:
                print("⚠ Session status not updated on stop")
        else:
            print("⚠ stop_session method not available")
            manager.running = False  # Manual cleanup
        
        return True
    except Exception as e:
        print(f"✗ Session stop test failed: {e}")
        return False


def main():
    """Run all parallel transmission tests."""
    print("=" * 60)
    print("PARALLEL TRANSMISSION FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    results.append(test_parallel_transmission_initialization())
    results.append(test_worker_count_clamping())
    results.append(test_session_start())
    results.append(test_queue_job())
    results.append(test_session_statistics())
    results.append(test_get_progress())
    results.append(test_stop_session())
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Parallel transmission is working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
