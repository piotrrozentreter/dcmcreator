#!/usr/bin/env python3
"""
Example: Stress Testing Simulation
Ready-to-run script - just execute: python examples/stress_test.py
"""

import sys
from src.stress_tester import StressTestRunner
from src.dcmlogger import setup_logging

def main():
    """Run stress test simulation."""
    logger = setup_logging()
    
    # Configuration - EDIT THESE
    TEST_NAME = "Load Test"
    FILES_PER_SECOND = 50    # Throughput target
    DURATION_SECONDS = 60    # How long to run
    FILE_SIZE_MB = 1.0       # Each file size
    WORKER_THREADS = 5       # Parallel workers
    
    print("\n" + "="*60)
    print("Stress Test Simulator")
    print("="*60 + "\n")
    
    try:
        print("Test Configuration:")
        print(f"  Name: {TEST_NAME}")
        print(f"  Target: {FILES_PER_SECOND} files/sec")
        print(f"  Duration: {DURATION_SECONDS} seconds")
        print(f"  File Size: {FILE_SIZE_MB} MB")
        print(f"  Workers: {WORKER_THREADS}")
        
        # Calculate expected metrics
        total_files = FILES_PER_SECOND * DURATION_SECONDS
        total_mb = total_files * FILE_SIZE_MB
        expected_throughput = total_mb / DURATION_SECONDS
        
        print(f"\nExpected Results:")
        print(f"  Total files: {total_files}")
        print(f"  Total data: {total_mb:.1f} MB")
        print(f"  Expected throughput: {expected_throughput:.2f} MB/s")
        
        # Create test plan
        print("\n" + "="*60)
        print("Creating test plan...")
        runner = StressTestRunner(logger=logger)
        plan = runner.create_test_plan(
            name=TEST_NAME,
            files_per_second=FILES_PER_SECOND,
            duration_seconds=DURATION_SECONDS,
            file_size_mb=FILE_SIZE_MB,
            concurrent_threads=WORKER_THREADS
        )
        
        print("? Plan created:")
        for key, value in plan.items():
            print(f"  {key}: {value}")
        
        # Start test
        print("\n" + "="*60)
        print("Starting stress test simulation...")
        print("(This will take approximately", DURATION_SECONDS // 10, "seconds to simulate)\n")
        
        test = runner.start_stress_test(plan)
        
        # Simulate file transmissions
        import time
        start_time = time.time()
        files_sent = 0
        files_failed = 0
        
        # Calculate delay between files for smooth distribution
        delay_per_file = 1.0 / FILES_PER_SECOND
        simulation_speed = 10  # Accelerate simulation 10x
        actual_delay = delay_per_file / simulation_speed
        
        print(f"Simulating {total_files} files...")
        for i in range(total_files):
            # Simulate send success (95% success rate)
            success = (i % 20) != 0  # 95% success
            bytes_sent = int(FILE_SIZE_MB * 1024 * 1024) if success else 0
            
            runner.record_file_sent(bytes_sent=bytes_sent, success=success)
            
            if success:
                files_sent += 1
            else:
                files_failed += 1
            
            # Print progress every 10%
            progress = (i + 1) / total_files
            if (i + 1) % max(1, total_files // 10) == 0:
                print(f"  {progress*100:.0f}% - {files_sent} sent, {files_failed} failed")
            
            time.sleep(actual_delay)
        
        # End test
        print(f"\nTest completed!")
        runner.end_stress_test("COMPLETED")
        
        # Get report
        report = runner.get_stress_test_report()
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        if report:
            for key, value in report.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n" + "="*60)
        print("ANALYSIS")
        print("="*60)
        
        if files_sent > 0:
            success_rate = (files_sent / (files_sent + files_failed)) * 100
            print(f"? Success Rate: {success_rate:.1f}%")
        
        elapsed = time.time() - start_time
        actual_throughput = (files_sent * FILE_SIZE_MB) / elapsed
        print(f"? Actual Throughput: {actual_throughput:.2f} MB/s")
        
        if actual_throughput > expected_throughput * 0.8:
            print("? Test PASSED - Target throughput achieved")
        else:
            print("? Test DEGRADED - Below target throughput")
        
        print("="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"? Error: {e}")
        logger.exception("Stress test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
