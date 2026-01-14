"""
DICOM Connection Validator - C-ECHO and advanced connection testing.

Provides utilities to test DICOM server connectivity using the C-ECHO protocol
and perform various connection validation checks.
"""

import socket
import threading
import time


class ConnectionValidator:
    """Validate DICOM server connections using TCP and C-ECHO."""
    
    def __init__(self, logger=None):
        """Initialize validator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
        self.last_latency = None
        self.last_result = None
    
    def test_tcp_connection(self, host, port, timeout=5):
        """Test basic TCP connection to server.
        
        Args:
            host: Server IP or hostname
            port: Server port
            timeout: Connection timeout in seconds
            
        Returns:
            dict with keys: success, latency_ms, error
        """
        result = {
            'success': False,
            'latency_ms': None,
            'error': None,
            'timestamp': time.time()
        }
        
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            sock.connect((host, port))
            sock.close()
            
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            result['success'] = True
            result['latency_ms'] = round(elapsed, 2)
            
            if self.logger:
                self.logger.warning(
                    f"TCP connection successful: {host}:{port} ({elapsed:.2f}ms)"
                )
        
        except socket.timeout:
            result['error'] = "Connection timeout"
            if self.logger:
                self.logger.warning(f"TCP connection timeout: {host}:{port}")
        except socket.gaierror:
            result['error'] = "Hostname resolution failed"
            if self.logger:
                self.logger.warning(f"Hostname resolution failed: {host}")
        except ConnectionRefusedError:
            result['error'] = "Connection refused"
            if self.logger:
                self.logger.warning(f"Connection refused: {host}:{port}")
        except Exception as e:
            result['error'] = str(e)
            if self.logger:
                self.logger.exception(f"TCP connection failed: {e}")
        
        self.last_result = result
        self.last_latency = result['latency_ms']
        return result
    
    def test_port_open(self, host, port, timeout=2):
        """Quick check if port is open.
        
        Args:
            host: Server IP or hostname
            port: Server port
            timeout: Timeout in seconds
            
        Returns:
            Boolean indicating if port is open
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def test_multiple_ports(self, host, ports, timeout=2):
        """Test multiple ports on a server.
        
        Args:
            host: Server IP or hostname
            ports: List of ports to test
            timeout: Timeout in seconds
            
        Returns:
            dict mapping port -> boolean (open/closed)
        """
        results = {}
        for port in ports:
            results[port] = self.test_port_open(host, port, timeout)
        return results
    
    def test_latency_variations(self, host, port, attempts=5, timeout=5):
        """Test latency with multiple attempts to check consistency.
        
        Args:
            host: Server IP or hostname
            port: Server port
            attempts: Number of test attempts
            timeout: Timeout in seconds
            
        Returns:
            dict with keys: min, max, avg, std_dev, attempts
        """
        latencies = []
        
        for _ in range(attempts):
            result = self.test_tcp_connection(host, port, timeout)
            if result['success'] and result['latency_ms'] is not None:
                latencies.append(result['latency_ms'])
            time.sleep(0.1)  # Small delay between attempts
        
        if not latencies:
            return {
                'min': None,
                'max': None,
                'avg': None,
                'std_dev': None,
                'attempts': attempts,
                'successful': 0
            }
        
        import statistics
        
        return {
            'min': round(min(latencies), 2),
            'max': round(max(latencies), 2),
            'avg': round(statistics.mean(latencies), 2),
            'std_dev': round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
            'attempts': attempts,
            'successful': len(latencies)
        }
    
    def get_connection_quality(self, host, port, timeout=5):
        """Assess overall connection quality.
        
        Returns:
            dict with quality assessment
        """
        result = self.test_tcp_connection(host, port, timeout)
        
        if not result['success']:
            quality = {
                'status': 'FAILED',
                'level': 'CRITICAL',
                'description': result['error'],
                'recommendation': 'Check server is running, IP/port are correct'
            }
        elif result['latency_ms'] < 10:
            quality = {
                'status': 'EXCELLENT',
                'level': 'LOW LATENCY',
                'latency_ms': result['latency_ms'],
                'description': 'Very fast connection',
                'recommendation': 'Ideal for transmission'
            }
        elif result['latency_ms'] < 50:
            quality = {
                'status': 'GOOD',
                'level': 'NORMAL',
                'latency_ms': result['latency_ms'],
                'description': 'Good connection',
                'recommendation': 'Suitable for transmission'
            }
        elif result['latency_ms'] < 200:
            quality = {
                'status': 'ACCEPTABLE',
                'level': 'HIGH LATENCY',
                'latency_ms': result['latency_ms'],
                'description': 'Slower connection',
                'recommendation': 'Transmission may be slow'
            }
        else:
            quality = {
                'status': 'POOR',
                'level': 'VERY HIGH LATENCY',
                'latency_ms': result['latency_ms'],
                'description': 'Very slow connection',
                'recommendation': 'Check network, consider retrying'
            }
        
        return quality
    
    def validate_address(self, host):
        """Validate if address is resolvable.
        
        Args:
            host: Hostname or IP address
            
        Returns:
            dict with keys: valid, resolved_ip, error
        """
        result = {
            'valid': False,
            'resolved_ip': None,
            'error': None
        }
        
        try:
            # Try to resolve
            resolved_ip = socket.gethostbyname(host)
            result['valid'] = True
            result['resolved_ip'] = resolved_ip
            
            if self.logger:
                self.logger.warning(f"Resolved {host} -> {resolved_ip}")
        
        except socket.gaierror as e:
            result['error'] = f"Resolution failed: {e}"
            if self.logger:
                self.logger.warning(f"Failed to resolve {host}: {e}")
        except Exception as e:
            result['error'] = str(e)
        
        return result


class CEchoValidator:
    """DICOM C-ECHO validation (placeholder for future DICOM echo implementation).
    
    Note: Full C-ECHO implementation requires pynetdicom DICOM protocol support.
    This is a placeholder for architecture completeness.
    """
    
    def __init__(self, logger=None):
        """Initialize C-ECHO validator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger
    
    def test_c_echo(self, host, port, calling_ae="DCMCREATOR", called_ae="ANY-SCP", timeout=5):
        """Test C-ECHO protocol (requires pynetdicom).
        
        Args:
            host: Server IP or hostname
            port: Server port
            calling_ae: Our AE title
            called_ae: Server AE title
            timeout: Timeout in seconds
            
        Returns:
            dict with test result
        """
        result = {
            'success': False,
            'supported': False,
            'latency_ms': None,
            'error': 'Not implemented yet',
            'note': 'Full DICOM C-ECHO requires additional pynetdicom setup'
        }
        
        try:
            # Check if pynetdicom is available
            import pynetdicom
            from pynetdicom.sop_class import Verification
            
            result['supported'] = True
            
            # Future implementation:
            # assoc = pynetdicom.AE().connect(host, port, ...)
            # status = assoc.send_c_echo()
            # assoc.release()
            
            if self.logger:
                self.logger.warning(
                    "C-ECHO test: pynetdicom available but not fully implemented"
                )
        
        except ImportError:
            result['error'] = "pynetdicom not available"
            if self.logger:
                self.logger.warning("C-ECHO test: pynetdicom not installed")
        except Exception as e:
            result['error'] = str(e)
            if self.logger:
                self.logger.exception(f"C-ECHO test failed: {e}")
        
        return result


def format_connection_report(validator_result):
    """Format connection validation result for display.
    
    Args:
        validator_result: Result dict from validator
        
    Returns:
        Formatted string report
    """
    report = []
    
    if validator_result.get('success'):
        report.append("? Connection Test PASSED")
        report.append(f"  Latency: {validator_result.get('latency_ms', 'N/A')} ms")
    else:
        report.append("? Connection Test FAILED")
        report.append(f"  Error: {validator_result.get('error', 'Unknown')}")
    
    return "\n".join(report)
