#!/usr/bin/env python3
"""
Example: Using Transmission History to track and analyze DICOM sends.

This example shows how to:
1. Send DICOM files and have them automatically recorded
2. Query transmission history
3. Generate reports
4. Export data for analysis
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from transmission_history import TransmissionHistory
from dcmlogger import setup_logging

def example_1_view_recent_transmissions():
    """View the most recent transmissions."""
    print("=" * 60)
    print("EXAMPLE 1: View Recent Transmissions")
    print("=" * 60)
    
    logger = setup_logging()
    history = TransmissionHistory(logger=logger)
    
    # Get last 10 transmissions
    recent = history.get_recent_transmissions(limit=10)
    
    if not recent:
        print("No transmissions found.")
        return
    
    print(f"\nLast {len(recent)} transmissions:\n")
    for i, trans in enumerate(recent, 1):
        status_icon = "✓" if trans.get('success') else "✗"
        print(f"{i}. [{status_icon}] {trans.get('filename')}")
        print(f"   Patient: {trans.get('patient_name')} (ID: {trans.get('patient_id')})")
        print(f"   Server: {trans.get('server_ip')}:{trans.get('server_port')}")
        print(f"   Size: {trans.get('bytes_sent', 0) / 1024:.1f} KB")
        print(f"   Time: {trans.get('timestamp')}")
        print()

def example_2_statistics():
    """View transmission statistics."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Transmission Statistics")
    print("=" * 60)
    
    logger = setup_logging()
    history = TransmissionHistory(logger=logger)
    
    stats = history.get_statistics()
    
    print("\nStatistics:")
    print(f"  Total Transmissions: {stats.get('total_transmissions', 0)}")
    print(f"  Successful: {stats.get('successful', 0)}")
    print(f"  Failed: {stats.get('failed', 0)}")
    print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
    print(f"  Total Data Transferred: {stats.get('total_mb_transferred', 0):.2f} MB")
    print(f"  Average Throughput: {stats.get('avg_throughput_mbps', 0):.2f} MB/s")

def example_3_server_performance():
    """Analyze performance by server."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Server Performance Analysis")
    print("=" * 60)
    
    logger = setup_logging()
    history = TransmissionHistory(logger=logger)
    
    # Get all transmissions
    all_trans = history.get_recent_transmissions(limit=1000)
    
    # Group by server
    server_stats = {}
    for trans in all_trans:
        key = f"{trans.get('server_ip')}:{trans.get('server_port')}"
        if key not in server_stats:
            server_stats[key] = {
                'count': 0,
                'success': 0,
                'failed': 0,
                'total_bytes': 0,
                'total_time': 0
            }
        
        stats = server_stats[key]
        stats['count'] += 1
        if trans.get('success'):
            stats['success'] += 1
            stats['total_bytes'] += trans.get('bytes_sent', 0)
            stats['total_time'] += trans.get('duration_seconds', 0)
        else:
            stats['failed'] += 1
    
    print("\nPerformance by Server:")
    for server, stats in server_stats.items():
        success_rate = (stats['success'] / stats['count'] * 100) if stats['count'] > 0 else 0
        avg_throughput = (stats['total_bytes'] / 1024 / 1024 / stats['total_time']) if stats['total_time'] > 0 else 0
        
        print(f"\n  {server}:")
        print(f"    Transmissions: {stats['count']}")
        print(f"    Success Rate: {success_rate:.1f}%")
        print(f"    Data Transferred: {stats['total_bytes'] / 1024 / 1024:.2f} MB")
        print(f"    Avg Throughput: {avg_throughput:.2f} MB/s")

def example_4_failed_transmissions():
    """Find and analyze failed transmissions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Failed Transmission Analysis")
    print("=" * 60)
    
    logger = setup_logging()
    history = TransmissionHistory(logger=logger)
    
    # Get failed transmissions
    all_trans = history.get_recent_transmissions(limit=1000)
    failed = [t for t in all_trans if not t.get('success')]
    
    if not failed:
        print("\nNo failed transmissions found.")
        return
    
    print(f"\nFound {len(failed)} failed transmissions:\n")
    for trans in failed:
        print(f"  SOP Instance: {trans.get('filename')}")
        print(f"  Server: {trans.get('server_ip')}:{trans.get('server_port')}")
        print(f"  Error: {trans.get('error_message')}")
        print(f"  Time: {trans.get('timestamp')}")
        print()

def example_5_export_report():
    """Export transmission data for external analysis."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Export Report as JSON")
    print("=" * 60)
    
    logger = setup_logging()
    history = TransmissionHistory(logger=logger)
    
    # Get all recent transmissions
    recent = history.get_recent_transmissions(limit=50)
    
    # Create report structure
    report = {
        'generated_at': datetime.now().isoformat(),
        'transmission_count': len(recent),
        'transmissions': []
    }
    
    for trans in recent:
        report['transmissions'].append({
            'timestamp': trans.get('timestamp'),
            'filename': trans.get('filename'),
            'patient_id': trans.get('patient_id'),
            'server': f"{trans.get('server_ip')}:{trans.get('server_port')}",
            'success': trans.get('success'),
            'bytes_sent': trans.get('bytes_sent'),
            'duration_seconds': trans.get('duration_seconds'),
            'throughput_mbps': trans.get('throughput_mbps'),
            'error': trans.get('error_message')
        })
    
    # Export to JSON
    report_file = 'transmission_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport exported to: {report_file}")
    print(f"Contains {len(recent)} transmissions")
    print("\nFirst transmission in report:")
    if report['transmissions']:
        print(json.dumps(report['transmissions'][0], indent=2))

if __name__ == "__main__":
    # Run all examples
    example_1_view_recent_transmissions()
    example_2_statistics()
    example_3_server_performance()
    example_4_failed_transmissions()
    example_5_export_report()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
