#!/usr/bin/env python3
"""
Example: View Transmission History and Statistics
Ready-to-run script - just execute: python examples/view_history.py
"""

import sys
import json
from src.transmission_history import TransmissionHistory
from src.dcmlogger import setup_logging

def main():
    """View transmission history."""
    logger = setup_logging()
    
    print("\n" + "="*60)
    print("Transmission History Viewer")
    print("="*60 + "\n")
    
    try:
        history = TransmissionHistory(logger=logger)
        
        # Get statistics
        print("Retrieving statistics...\n")
        stats = history.get_statistics()
        
        print("="*60)
        print("STATISTICS")
        print("="*60)
        print(f"Total Transmissions: {stats.get('total_transmissions', 0)}")
        print(f"Successful: {stats.get('successful', 0)}")
        print(f"Failed: {stats.get('failed', 0)}")
        print(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
        print(f"Total Data Transferred: {stats.get('total_mb_transferred', 0):.2f} MB")
        print(f"Average Throughput: {stats.get('avg_throughput_mbps', 0):.2f} MB/s")
        
        # Get recent transmissions
        print("\n" + "="*60)
        print("RECENT TRANSMISSIONS (Last 10)")
        print("="*60 + "\n")
        
        recent = history.get_recent_transmissions(limit=10)
        
        if recent:
            for i, trans in enumerate(recent, 1):
                status = "? OK" if trans.get('success') else "? FAIL"
                print(f"{i}. {trans.get('filename', 'N/A')}")
                print(f"   Server: {trans.get('server_ip', 'N/A')}:{trans.get('server_port', 'N/A')}")
                print(f"   Status: {status}")
                print(f"   Bytes: {trans.get('bytes_sent', 0):,}")
                print(f"   Time: {trans.get('timestamp', 'N/A')}")
                print()
        else:
            print("No transmission history found.\n")
        
        # Export to JSON
        print("="*60)
        print("EXPORT")
        print("="*60 + "\n")
        
        export_file = "transmission_history.json"
        if history.export_to_json(export_file):
            print(f"? History exported to: {export_file}")
            
            # Show file size
            import os
            filesize = os.path.getsize(export_file) / 1024
            print(f"? File size: {filesize:.2f} KB")
        else:
            print("? Failed to export history")
        
        print("\n" + "="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"? Error: {e}")
        logger.exception("Failed to retrieve history")
        return 1

if __name__ == "__main__":
    sys.exit(main())
