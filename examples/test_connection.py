#!/usr/bin/env python3
"""
Example: Test Connection to DICOM Server
Ready-to-run script - just execute: python examples/test_connection.py
"""

import sys
from src.connection_validator import ConnectionValidator
from src.dcmlogger import setup_logging

def main():
    """Test connection to DICOM server."""
    logger = setup_logging()
    
    # Configuration - EDIT THESE
    SERVER_IP = "192.168.1.100"  # Change to your server IP
    SERVER_PORT = 4321           # Change to your server port
    ATTEMPTS = 5                 # Number of latency test attempts
    
    print("\n" + "="*60)
    print("DICOM Connection Tester")
    print("="*60 + "\n")
    
    try:
        validator = ConnectionValidator(logger=logger)
        
        # Test 1: Basic TCP Connection
        print("1. Testing TCP Connection...")
        print(f"   Target: {SERVER_IP}:{SERVER_PORT}")
        result = validator.test_tcp_connection(SERVER_IP, SERVER_PORT)
        print(f"   ? Success: {result['success']}")
        if result['success']:
            print(f"   ? Latency: {result['latency_ms']:.2f} ms")
        else:
            print(f"   ? Error: {result['error']}")
        
        # Test 2: Connection Quality
        print("\n2. Testing Connection Quality...")
        quality = validator.get_connection_quality(SERVER_IP, SERVER_PORT)
        print(f"   ? Status: {quality['status']}")
        print(f"   ? Level: {quality['level']}")
        print(f"   ? Description: {quality['description']}")
        print(f"   ? Recommendation: {quality['recommendation']}")
        if quality.get('latency_ms'):
            print(f"   ? Latency: {quality['latency_ms']:.2f} ms")
        
        # Test 3: Latency Variations
        print(f"\n3. Testing Latency Variations ({ATTEMPTS} attempts)...")
        variations = validator.test_latency_variations(SERVER_IP, SERVER_PORT, attempts=ATTEMPTS)
        print(f"   ? Successful: {variations['successful']}/{variations['attempts']}")
        print(f"   ? Min Latency: {variations['min']:.2f} ms")
        print(f"   ? Max Latency: {variations['max']:.2f} ms")
        print(f"   ? Avg Latency: {variations['avg']:.2f} ms")
        print(f"   ? Std Dev: {variations['std_dev']:.2f} ms")
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        if result['success'] and quality['status'] == "OK":
            print("? Server is reachable and responding well!")
        elif result['success']:
            print("? Server is reachable but quality may be degraded")
            print(f"  Recommendation: {quality['recommendation']}")
        else:
            print("? Server is NOT reachable")
            print("  Check:")
            print("  - Server IP address is correct")
            print("  - Server port is correct")
            print("  - Network connectivity")
            print("  - Firewall settings")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"? Error: {e}")
        logger.exception("Connection test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
