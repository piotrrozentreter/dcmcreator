#!/usr/bin/env python3
"""
Example: Parallel Transmission with Config File
Ready-to-run script - just execute: python examples/parallel_send.py
Requires: parallel_config.json (generated from GUI "Save Config" button)
"""

import sys
import json
import os
from src.parallel_transmission import ParallelTransmissionManager
from src.dcmlogger import setup_logging

def load_config():
    """Load configuration from saved file."""
    config_file = "parallel_config.json"
    
    if not os.path.exists(config_file):
        print(f"? Error: {config_file} not found!")
        print("\nTo generate this file:")
        print("  1. Run: python src/app.py")
        print("  2. Go to Parallel Send tab")
        print("  3. Set Worker Threads and Session Name")
        print("  4. Click 'Save Config' button")
        print(f"  5. This will create: {config_file}")
        sys.exit(1)
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"? Error reading {config_file}: {e}")
        sys.exit(1)

def main():
    """Simulate parallel transmission."""
    logger = setup_logging()
    
    print("\n" + "="*60)
    print("Parallel Transmission Simulator")
    print("="*60 + "\n")
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        workers = config["workers"]
        session_name = config["session_name"]
        
        print(f"? Workers: {workers}")
        print(f"? Session: {session_name}")
        
        # Configuration - EDIT THESE
        FILE_COUNT = 50            # How many files to simulate
        FILE_SIZE_MB = 1.0         # Simulated file size
        NETWORK_LATENCY_MS = 10    # Simulated network latency
        
        print("\n" + "="*60)
        print("TRANSMISSION SIMULATION")
        print("="*60)
        print(f"Files to send: {FILE_COUNT}")
        print(f"File size: {FILE_SIZE_MB} MB each")
        print(f"Simulated latency: {NETWORK_LATENCY_MS} ms\n")
        
        # Create manager
        mgr = ParallelTransmissionManager(max_workers=workers, logger=logger)
        session = mgr.start_session(session_name)
        
        # Define mock send function (simulates DICOM transmission)
        def mock_send_dicom(file_path):
            """Simulate DICOM transmission."""
            import time
            # Simulate network latency + transmission
            transmission_time = (NETWORK_LATENCY_MS / 1000.0) + (FILE_SIZE_MB * 0.1)
            time.sleep(transmission_time)
            return True  # Success
        
        # Queue files
        print(f"Queuing {FILE_COUNT} files for transmission...\n")
        file_list = [f"test_file_{i:03d}.dcm" for i in range(FILE_COUNT)]
        mgr.queue_batch(file_list, mock_send_dicom)
        
        # Wait for completion
        print("Starting parallel transmission...")
        mgr.wait_for_completion(timeout=3600)
        
        # Get report
        report = mgr.get_session_report()
        
        print("\n" + "="*60)
        print("TRANSMISSION COMPLETE")
        print("="*60)
        print(f"? Session: {report['session_name']}")
        print(f"? Files sent: {report['files_sent']}")
        print(f"? Success rate: {report['success_rate']:.1f}%")
        print(f"? Duration: {report['duration_seconds']:.2f} seconds")
        print(f"? Throughput: {report['throughput_mbps']:.2f} MB/s")
        print(f"? Workers used: {report['workers_used']}")
        
        # Calculate speedup
        sequential_time = report['duration_seconds'] * workers
        speedup = sequential_time / report['duration_seconds']
        print(f"? Speedup: {speedup:.1f}x (vs sequential)")
        
        print("="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"? Error: {e}")
        logger.exception("Parallel transmission failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
