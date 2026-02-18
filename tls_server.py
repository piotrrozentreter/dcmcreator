"""
TLS DICOM Storage SCP Server
Receives DICOM files over secure TLS connection
"""
from pynetdicom import AE, evt, StoragePresentationContexts, ALL_TRANSFER_SYNTAXES
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
    print(f"✓ Received: {filename}")
    print(f"  Patient: {getattr(ds, 'PatientName', 'N/A')}")
    print(f"  Study: {getattr(ds, 'StudyDescription', 'N/A')}")
    print(f"  SOP Class: {ds.SOPClassUID}")
    print()
    
    return 0x0000  # Success

def handle_echo(event):
    """Handle incoming C-ECHO requests"""
    print("✓ Received C-ECHO request")
    return 0x0000  # Success

def handle_accepted(event):
    """Handle when an association is accepted"""
    print(f"✓ Association accepted from {event.address}:{event.port}")
    print(f"  Calling AE: {event.assoc.requestor.ae_title.decode('ascii', 'replace')}")
    print(f"  Called AE: {event.assoc.acceptor.ae_title.decode('ascii', 'replace')}")
    print()

def handle_released(event):
    """Handle when an association is released"""
    print("✓ Association released")
    print()

def handle_rejected(event):
    """Handle when an association is rejected"""
    print(f"✗ Association rejected")
    print(f"  Source: {event.address if hasattr(event, 'address') else 'unknown'}:{event.port if hasattr(event, 'port') else '?'}")
    print(f"  Reason: {event.result if hasattr(event, 'result') else 'unknown'}")
    
    # Try to get more details
    try:
        if hasattr(event, 'assoc'):
            assoc = event.assoc
            print(f"  Calling AE: {assoc.requestor.ae_title if hasattr(assoc.requestor, 'ae_title') else 'unknown'}")
            print(f"  Called AE: {assoc.acceptor.ae_title if hasattr(assoc.acceptor, 'ae_title') else 'unknown'}")
            
            # Check presentation contexts
            if hasattr(assoc, 'requested_contexts'):
                print(f"  Requested contexts: {len(assoc.requested_contexts)}")
    except Exception as e:
        print(f"  (Could not get details: {e})")
    
    print()

def handle_aborted(event):
    """Handle when an association is aborted"""
    print(f"✗ Association aborted")
    print(f"  Source: {event.address if hasattr(event, 'address') else 'unknown'}:{event.port if hasattr(event, 'port') else '?'}")
    print()

def handle_connection_opened(event):
    """Handle when a connection is opened (before association)"""
    print(f"→ TCP connection opened from {event.address}:{event.port}")
    print()

def handle_connection_closed(event):
    """Handle when a connection is closed"""
    print(f"← TCP connection closed from {event.address if hasattr(event, 'address') else 'unknown'}")
    print()

def main():
    print("="*60)
    print("TLS DICOM Storage SCP Server")
    print("="*60)
    print()
    
    # Configure TLS
    print("Configuring TLS...")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain('server_cert.pem', 'server_key.pem')
    
    # For self-signed testing: don't verify client certificates
    # In production: use CERT_REQUIRED with proper CA validation
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE  # Changed from CERT_OPTIONAL
    
    print("✓ TLS configured (client verification disabled for testing)")
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
        (evt.EVT_CONN_OPEN, handle_connection_opened),
        (evt.EVT_CONN_CLOSE, handle_connection_closed),
    ]
    
    print("="*60)
    print("Server Configuration:")
    print("="*60)
    print(f"  AE Title:    DCMSERVER")
    print(f"  Port:        4321 (TLS)")
    print(f"  Bind:        0.0.0.0 (all interfaces)")
    print(f"  Output Dir:  ./received/")
    print(f"  TLS:         Enabled (SHA256)")
    print(f"  Contexts:    {len(ae.supported_contexts)} presentation contexts")
    print("="*60)
    print()
    print("Waiting for connections... (Press Ctrl+C to stop)")
    print()
    
    # Start server - bind to all interfaces
    ae.start_server(
        ('0.0.0.0', 4321),  # Explicitly bind to all interfaces
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