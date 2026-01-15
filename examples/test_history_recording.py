#!/usr/bin/env python3
"""
Test script to verify transmission history recording works.
This script simulates a transmission and checks if it's recorded.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transmission_history import TransmissionHistory
from dcmlogger import setup_logging

def test_transmission_history():
    """Test transmission history recording."""
    logger = setup_logging()
    
    # Create history tracker
    history = TransmissionHistory(logger=logger)
    
    # Record a test transmission
    print("Recording test transmission...")
    history.record_transmission(
        filename="test_sop_instance_001",
        server_ip="192.168.1.100",
        server_port=4321,
        calling_ae="DCMCREATOR",
        called_ae="TEST-SCP",
        success=True,
        bytes_sent=1048576,  # 1MB
        duration_seconds=2.5,
        error_message=None,
        patient_name="Test^Patient",
        patient_id="PAT001",
        study_uid="1.2.3.4.5",
        series_uid="1.2.3.4.5.1"
    )
    
    # Record another one that failed
    print("Recording failed transmission...")
    history.record_transmission(
        filename="test_sop_instance_002",
        server_ip="192.168.1.100",
        server_port=4321,
        calling_ae="DCMCREATOR",
        called_ae="TEST-SCP",
        success=False,
        bytes_sent=0,
        duration_seconds=1.0,
        error_message="Connection refused",
        patient_name="Test^Patient",
        patient_id="PAT001",
        study_uid="1.2.3.4.5",
        series_uid="1.2.3.4.5.1"
    )
    
    # Get recent transmissions
    print("\nRetrieving recent transmissions...")
    recent = history.get_recent_transmissions(limit=10)
    
    print(f"\nFound {len(recent)} transmissions:\n")
    for i, trans in enumerate(recent, 1):
        print(f"{i}. {trans.get('filename')}")
        print(f"   Server: {trans.get('server_ip')}:{trans.get('server_port')}")
        print(f"   Status: {'? SUCCESS' if trans.get('success') else '? FAILED'}")
        print(f"   Bytes: {trans.get('bytes_sent')}")
        print(f"   Duration: {trans.get('duration_seconds')}s")
        print(f"   Timestamp: {trans.get('timestamp')}")
        print()
    
    # Get statistics
    print("\nTransmission Statistics:")
    stats = history.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Check if transmissions were actually recorded
    if len(recent) >= 2:
        print("\n? SUCCESS: Transmissions were recorded in history!")
        return True
    else:
        print(f"\n? FAILED: Expected 2 transmissions, but only found {len(recent)}")
        return False

if __name__ == "__main__":
    success = test_transmission_history()
    sys.exit(0 if success else 1)
