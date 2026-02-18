"""
TLS DICOM Storage SCP Server with Mutual Authentication
Receives DICOM files over secure TLS connection with client certificate verification
"""
from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import Verification
import ssl
import os

def handle_store(event):
    """Handle incoming C-STORE requests"""
    ds = event.dataset
    
    # Create output directory
    os.makedirs("received", exist_ok=True)
    
    # Save file
    filename = f"received/{ds.SOPInstanceUID}.dcm"
    ds.save_as(filename, write_like_original=False)
    
    # Print info
    print(f"? Received: {filename}")
    print(f"  Patient: {getattr(ds, 'PatientName', 'N/A')}")
    print(f"  Study: {getattr(ds, 'StudyDescription', 'N/A')}")
    print(f"  SOP Class: {ds.SOPClassUID}")
    print()
    
    return 0x0000  # Success

def handle_echo(event):
    """Handle incoming C-ECHO requests"""
    print("? Received C-ECHO request")
    return 0x0000  # Success

def handle_accepted(event):
    """Handle when an association is accepted"""
    print(f"? Association accepted from {event.address}:{event.port}")
    print(f"  Calling AE: {event.assoc.requestor.ae_title.decode('ascii', 'replace')}")
    print(f"  Called AE: {event.assoc.acceptor.ae_title.decode('ascii', 'replace')}")
    
    # Show client certificate info if available
    try:
        peer_cert = event.assoc.requestor.ssl_context.getpeercert() if hasattr(event.assoc.requestor, 'ssl_context') else None
        if peer_cert:
            subject = dict(x[0] for x in peer_cert['subject'])
            print(f"  Client Cert: {subject.get('commonName', 'N/A')}")
    except:
        pass
    
    print()

def handle_released(event):
    """Handle when an association is released"""
    print("? Association released")
    print()

def handle_rejected(event):
    """Handle when an association is rejected"""
    print(f"? Association rejected")
    print(f"  Reason: {event.result}")
    print()

def handle_aborted(event):
    """Handle when an association is aborted"""
    print(f"? Association aborted")
    print()

def main():
    print("="*60)
    print("TLS DICOM Storage SCP Server (MUTUAL TLS)")
    print("="*60)
    print()
    
    # Configure TLS with mutual authentication
    print("Configuring TLS with mutual authentication...")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Load server certificate and key
    ssl_context.load_cert_chain('server_cert.pem', 'server_key.pem')
    
    # Load CA certificate to verify client certificates
    ssl_context.load_verify_locations('ca_cert.pem')
    
    # Require client certificate verification
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = False
    
    print("? TLS configured with client certificate verification")
    print()
    
    # Setup DICOM AE
    ae = AE(ae_title=b'DCMSERVER')
    
    # Add all storage presentation contexts
    ae.supported_contexts = StoragePresentationContexts
    
    # Add verification (C-ECHO) support
    ae.add_supported_context(Verification)
    
    # Set up event handlers
    handlers = [
        (evt.EVT_C_STORE, handle_store),
        (evt.EVT_C_ECHO, handle_echo),
        (evt.EVT_ACCEPTED, handle_accepted),
        (evt.EVT_RELEASED, handle_released),
        (evt.EVT_REJECTED, handle_rejected),
        (evt.EVT_ABORTED, handle_aborted),
    ]
    
    print("="*60)
    print("Server Configuration:")
    print("="*60)
    print(f"  AE Title:    DCMSERVER")
    print(f"  Port:        4321 (TLS)")
    print(f"  Bind:        0.0.0.0 (all interfaces)")
    print(f"  Output Dir:  ./received/")
    print(f"  TLS:         Enabled (SHA256)")
    print(f"  Mutual Auth: REQUIRED (client cert verified)")
    print(f"  Contexts:    {len(ae.supported_contexts)} presentation contexts")
    print("="*60)
    print()
    print("Waiting for connections... (Press Ctrl+C to stop)")
    print()
    
    # Start server - bind to all interfaces
    ae.start_server(
        ('0.0.0.0', 4321),
        evt_handlers=handlers,
        ssl_context=ssl_context
    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
