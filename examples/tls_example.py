"""
Example: Sending DICOM with TLS/SSL

Demonstrates how to send DICOM files over secure TLS connection.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from remote import send_grouped_dicom, is_remote_available, remote_unavailable_reason
import pydicom
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_with_basic_tls():
    """Example: Send DICOM with basic TLS (server verification only)"""
    
    if not is_remote_available():
        print(f"Error: {remote_unavailable_reason()}")
        return
    
    # Load a DICOM file
    dicom_file = "path/to/your/dicom/file.dcm"
    if not os.path.exists(dicom_file):
        print(f"Error: File not found: {dicom_file}")
        return
    
    ds = pydicom.dcmread(dicom_file)
    
    # Group datasets (required format)
    grouped = {
        ds.StudyInstanceUID: {
            ds.SeriesInstanceUID: [(ds, None)]
        }
    }
    
    # Configure server and TLS
    config = {
        "server": "dicom.example.com",
        "port": 11112,  # TLS port
        "calling_ae": "DCMCREATOR",
        "called_ae": "DEST_AE",
        "use_tls": True,
        "tls_config": {
            # Basic TLS - verify server only
            "verify_server": True,
            "verify_hostname": True,
            "tls_version": "TLSv1.2",
            # Leave client cert empty if not required
            "cert_file": None,
            "key_file": None,
            # Use system CA certificates
            "ca_file": None
        }
    }
    
    # Send
    try:
        send_grouped_dicom(
            grouped=grouped,
            config=config,
            logger=logger,
            on_message=lambda msg: print(f"  {msg}")
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

def send_with_mutual_tls():
    """Example: Send DICOM with mutual TLS (client + server authentication)"""
    
    if not is_remote_available():
        print(f"Error: {remote_unavailable_reason()}")
        return
    
    # Load a DICOM file
    dicom_file = "path/to/your/dicom/file.dcm"
    if not os.path.exists(dicom_file):
        print(f"Error: File not found: {dicom_file}")
        return
    
    ds = pydicom.dcmread(dicom_file)
    
    # Group datasets
    grouped = {
        ds.StudyInstanceUID: {
            ds.SeriesInstanceUID: [(ds, None)]
        }
    }
    
    # Configure server and mutual TLS
    config = {
        "server": "dicom.example.com",
        "port": 11112,
        "calling_ae": "DCMCREATOR",
        "called_ae": "DEST_AE",
        "use_tls": True,
        "tls_config": {
            # Client certificate authentication
            "cert_file": "/path/to/client_certificate.pem",
            "key_file": "/path/to/client_key.pem",
            "key_password": "optional_key_password",  # or None
            # Server verification
            "ca_file": "/path/to/ca_certificate.pem",
            "verify_server": True,
            "verify_hostname": True,
            # TLS settings
            "tls_version": "TLSv1.2",
            "allow_self_signed": False
        }
    }
    
    # Send
    try:
        send_grouped_dicom(
            grouped=grouped,
            config=config,
            logger=logger,
            on_message=lambda msg: print(f"  {msg}")
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

def send_with_self_signed_cert():
    """Example: Send DICOM with self-signed certificate (testing only)"""
    
    if not is_remote_available():
        print(f"Error: {remote_unavailable_reason()}")
        return
    
    # Load a DICOM file
    dicom_file = "path/to/your/dicom/file.dcm"
    if not os.path.exists(dicom_file):
        print(f"Error: File not found: {dicom_file}")
        return
    
    ds = pydicom.dcmread(dicom_file)
    
    # Group datasets
    grouped = {
        ds.StudyInstanceUID: {
            ds.SeriesInstanceUID: [(ds, None)]
        }
    }
    
    # Configure for self-signed certificate (TESTING ONLY)
    config = {
        "server": "test-dicom.local",
        "port": 11112,
        "calling_ae": "DCMCREATOR",
        "called_ae": "TEST_AE",
        "use_tls": True,
        "tls_config": {
            # Accept self-signed certificates
            "allow_self_signed": True,
            "verify_server": False,  # Disable for self-signed
            "verify_hostname": False,  # Disable for self-signed
            "tls_version": "TLSv1.2",
            # Provide self-signed cert as CA
            "ca_file": "/path/to/self_signed_cert.pem",
            # Client cert if needed
            "cert_file": None,
            "key_file": None
        }
    }
    
    print("WARNING: Using self-signed certificate configuration - for testing only!")
    
    # Send
    try:
        send_grouped_dicom(
            grouped=grouped,
            config=config,
            logger=logger,
            on_message=lambda msg: print(f"  {msg}")
        )
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("TLS/SSL DICOM Transmission Examples")
    print("=" * 50)
    
    print("\n1. Basic TLS (server verification only)")
    print("   Uncomment to run:")
    # send_with_basic_tls()
    
    print("\n2. Mutual TLS (client + server authentication)")
    print("   Uncomment to run:")
    # send_with_mutual_tls()
    
    print("\n3. Self-signed certificate (testing only)")
    print("   Uncomment to run:")
    # send_with_self_signed_cert()
    
    print("\nNote: Update file paths and server settings before running!")
