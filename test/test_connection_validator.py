"""
Test script for the Connection Validator functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from connection_validator import ConnectionValidator, CEchoValidator, format_connection_report


def test_validator_initialization():
    """Test ConnectionValidator initialization."""
    print("\nTesting ConnectionValidator initialization...")
    try:
        validator = ConnectionValidator()
        assert validator.last_latency is None
        assert validator.last_result is None
        print("✓ ConnectionValidator initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize ConnectionValidator: {e}")
        return False


def test_validate_address():
    """Test address validation."""
    print("\nTesting address validation...")
    try:
        validator = ConnectionValidator()
        
        # Test localhost
        result = validator.validate_address("localhost")
        if result['valid'] and result['resolved_ip']:
            print(f"✓ localhost resolved to {result['resolved_ip']}")
        else:
            print(f"✗ localhost resolution failed: {result['error']}")
            return False
        
        # Test invalid hostname
        result = validator.validate_address("invalid-hostname-12345.local")
        if not result['valid']:
            print(f"✓ Invalid hostname correctly rejected")
        else:
            print(f"⚠ Invalid hostname was unexpectedly resolved")
        
        return True
    except Exception as e:
        print(f"✗ Address validation test failed: {e}")
        return False


def test_port_open_check():
    """Test port open checking."""
    print("\nTesting port open check...")
    try:
        validator = ConnectionValidator()
        
        # Test a port that's very unlikely to be open
        result = validator.test_port_open("localhost", 65432, timeout=1)
        print(f"✓ Port open check completed (port 65432 open: {result})")
        
        return True
    except Exception as e:
        print(f"✗ Port open check failed: {e}")
        return False


def test_multiple_ports():
    """Test checking multiple ports."""
    print("\nTesting multiple ports check...")
    try:
        validator = ConnectionValidator()
        
        # Test multiple ports
        ports = [80, 443, 65432]
        results = validator.test_multiple_ports("localhost", ports, timeout=1)
        
        if len(results) == len(ports):
            print(f"✓ Multiple ports checked: {len(results)} ports tested")
            for port, is_open in results.items():
                print(f"  Port {port}: {'Open' if is_open else 'Closed'}")
        else:
            print(f"✗ Expected {len(ports)} results, got {len(results)}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Multiple ports check failed: {e}")
        return False


def test_tcp_connection():
    """Test TCP connection (with localhost which should always be available)."""
    print("\nTesting TCP connection...")
    try:
        validator = ConnectionValidator()
        
        # Test connection to a port that likely won't be available
        result = validator.test_tcp_connection("localhost", 65432, timeout=1)
        
        # Check result structure
        required_keys = ['success', 'latency_ms', 'error', 'timestamp']
        if all(key in result for key in required_keys):
            print(f"✓ TCP connection test returned proper structure")
            print(f"  Success: {result['success']}")
            if result['error']:
                print(f"  Error: {result['error']}")
        else:
            print(f"✗ TCP connection result missing required keys")
            return False
        
        # Check that last_result is stored
        if validator.last_result == result:
            print(f"✓ Last result properly stored")
        else:
            print(f"✗ Last result not stored correctly")
            return False
        
        return True
    except Exception as e:
        print(f"✗ TCP connection test failed: {e}")
        return False


def test_connection_quality():
    """Test connection quality assessment."""
    print("\nTesting connection quality assessment...")
    try:
        validator = ConnectionValidator()
        
        # Test with localhost (should fail or be fast)
        quality = validator.get_connection_quality("localhost", 65432, timeout=1)
        
        # Check quality result structure
        required_keys = ['status', 'level', 'description', 'recommendation']
        if all(key in quality for key in required_keys):
            print(f"✓ Connection quality assessment returned proper structure")
            print(f"  Status: {quality['status']}")
            print(f"  Level: {quality['level']}")
            print(f"  Description: {quality['description']}")
        else:
            print(f"✗ Connection quality result missing required keys")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Connection quality test failed: {e}")
        return False


def test_cecho_validator():
    """Test CEchoValidator initialization."""
    print("\nTesting CEchoValidator...")
    try:
        validator = CEchoValidator()
        
        # Test C-ECHO (should indicate not implemented or missing pynetdicom)
        result = validator.test_c_echo("localhost", 11112, timeout=1)
        
        # Check result structure
        if 'success' in result and 'supported' in result:
            print(f"✓ C-ECHO validator initialized and returned result")
            print(f"  Supported: {result['supported']}")
            print(f"  Note: {result.get('note', 'N/A')}")
        else:
            print(f"✗ C-ECHO result missing required keys")
            return False
        
        return True
    except Exception as e:
        print(f"✗ C-ECHO validator test failed: {e}")
        return False


def test_format_connection_report():
    """Test connection report formatting."""
    print("\nTesting connection report formatting...")
    try:
        # Test successful connection report
        success_result = {
            'success': True,
            'latency_ms': 15.5
        }
        report = format_connection_report(success_result)
        
        if "PASSED" in report and "15.5" in report:
            print("✓ Success report formatted correctly")
        else:
            print("✗ Success report format incorrect")
            return False
        
        # Test failed connection report
        failed_result = {
            'success': False,
            'error': 'Connection timeout'
        }
        report = format_connection_report(failed_result)
        
        if "FAILED" in report and "timeout" in report.lower():
            print("✓ Failed report formatted correctly")
        else:
            print("✗ Failed report format incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Report formatting test failed: {e}")
        return False


def main():
    """Run all connection validator tests."""
    print("=" * 60)
    print("CONNECTION VALIDATOR FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    results.append(test_validator_initialization())
    results.append(test_validate_address())
    results.append(test_port_open_check())
    results.append(test_multiple_ports())
    results.append(test_tcp_connection())
    results.append(test_connection_quality())
    results.append(test_cecho_validator())
    results.append(test_format_connection_report())
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Connection validator is working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
