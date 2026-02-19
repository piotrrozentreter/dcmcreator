"""
Remote DICOM sending utilities.

Implements C-STORE for all loaded datasets (grouped by Study/Series).
All-or-nothing: aborts on first error.
"""
from typing import Callable, Dict, Any
import ssl
import os

try:
    from .sop_utils import get_sop_name
except ImportError:
    from sop_utils import get_sop_name

_pynetdicom_import_error = None
_pydicom_import_error = None

# Try to use pynetdicom if available
try:
    from pynetdicom import AE
    try:
        # pynetdicom >=3 uses `Verification`
        from pynetdicom.sop_class import Verification as VerificationSOPClass
    except ImportError:
        # Older versions expose `VerificationSOPClass`
        from pynetdicom.sop_class import VerificationSOPClass  # type: ignore
    try:
        from pynetdicom.sop_class import StorageSOPClassList
    except ImportError:
        StorageSOPClassList = []
except ImportError as e:
    AE = None
    VerificationSOPClass = None
    StorageSOPClassList = []
    _pynetdicom_import_error = str(e)

try:
    import pydicom
except ImportError as e:
    pydicom = None
    _pydicom_import_error = str(e)


def _ensure_dependencies():
    if AE is None or pydicom is None:
        raise RuntimeError("pynetdicom and pydicom are required for remote sending")

def is_remote_available() -> bool:
    """Return True if required dependencies for remote sending are available."""
    return AE is not None and pydicom is not None

def remote_unavailable_reason() -> str:
    """Return a human-readable reason why remote is unavailable."""
    reasons = []
    if AE is None:
        reasons.append("pynetdicom not importable" + (f" ({_pynetdicom_import_error})" if _pynetdicom_import_error else ""))
    if pydicom is None:
        reasons.append("pydicom not importable" + (f" ({_pydicom_import_error})" if _pydicom_import_error else ""))
    return ", ".join(reasons) or "unknown"


def _create_tls_context(tls_config: Dict[str, Any], logger=None, on_message: Callable[[str], None] = None) -> ssl.SSLContext:
    """
    Create an SSL context from TLS configuration.
    
    Args:
        tls_config: Dictionary with TLS configuration:
            - cert_file: Path to client certificate (PEM)
            - key_file: Path to private key (PEM)
            - key_password: Optional password for private key
            - ca_file: Path to CA certificate for server verification
            - verify_server: Whether to verify server certificate (default True)
            - verify_hostname: Whether to verify server hostname (default True)
            - allow_self_signed: Whether to allow self-signed certificates (default False)
            - tls_version: Minimum TLS version (TLSv1.1, TLSv1.2, TLSv1.3)
            - cipher_suite: Optional cipher suite string
        logger: Optional logger for warnings
        on_message: Optional callback for status messages
    
    Returns:
        ssl.SSLContext configured for TLS connection
    
    Raises:
        RuntimeError: If TLS configuration is invalid
    """
    if not tls_config:
        tls_config = {}
    
    # Create SSL context for TLS client
    # Use PROTOCOL_TLS_CLIENT which supports TLS 1.0+ and auto-negotiates the highest version
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # Get requested minimum TLS version (default: TLSv1.2 per industry standards)
    tls_version = tls_config.get('tls_version', 'TLSv1.2')
    
    # Set minimum TLS version
    if hasattr(ssl, 'TLSVersion'):
        if tls_version == 'TLSv1.3':
            context.minimum_version = ssl.TLSVersion.TLSv1_3
        elif tls_version == 'TLSv1.2':
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        elif tls_version == 'TLSv1.1':
            context.minimum_version = ssl.TLSVersion.TLSv1_1
    
    # Security hardening for enterprise environments
    # Disable SSL compression to prevent CRIME attack (CVE-2012-4929)
    context.options |= ssl.OP_NO_COMPRESSION
    
    # Disable SSLv2 and SSLv3 (known vulnerabilities)
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    
    # Enable post-handshake authentication for TLS 1.3
    if hasattr(ssl, 'OP_NO_TLSv1_3'):
        # Only if TLS 1.3 is supported
        try:
            context.post_handshake_auth = True
        except AttributeError:
            pass  # Not available in older Python versions
    
    # Configure certificate verification mode
    # Priority: allow_self_signed > verify_server settings
    allow_self_signed = tls_config.get('allow_self_signed', False)
    verify_server = tls_config.get('verify_server', True)
    verify_hostname = tls_config.get('verify_hostname', True)
    
    if allow_self_signed:
        # Self-signed mode: disable strict verification (for testing only)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_OPTIONAL
        if on_message:
            on_message("TLS: Self-signed certificates allowed (testing mode)")
    elif verify_server:
        # Production mode: strict verification
        context.check_hostname = verify_hostname
        context.verify_mode = ssl.CERT_REQUIRED
        if on_message:
            msg = "TLS: Server certificate verification enabled"
            if verify_hostname:
                msg += " (with hostname verification)"
            on_message(msg)
    else:
        # No verification (not recommended)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if on_message:
            on_message("TLS: Server certificate verification disabled (not recommended)")
    
    # Load CA certificate for server verification
    ca_file = tls_config.get('ca_file')
    if ca_file:
        if not os.path.exists(ca_file):
            raise RuntimeError(f"CA certificate file not found: {ca_file}")
        try:
            context.load_verify_locations(cafile=ca_file)
            if on_message:
                on_message(f"TLS: Loaded CA certificate from {ca_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to load CA certificate: {e}")
    elif verify_server:
        # Load default system CA certificates
        try:
            context.load_default_certs()
            if on_message:
                on_message("TLS: Using system default CA certificates")
        except Exception as e:
            if logger:
                logger.warning(f"Failed to load default CA certificates: {e}")
    
    # Load client certificate and private key
    cert_file = tls_config.get('cert_file')
    key_file = tls_config.get('key_file')
    key_password = tls_config.get('key_password')
    
    if cert_file or key_file:
        if not cert_file or not key_file:
            raise RuntimeError("Both certificate and private key must be provided for client authentication")
        
        if not os.path.exists(cert_file):
            raise RuntimeError(f"Client certificate file not found: {cert_file}")
        if not os.path.exists(key_file):
            raise RuntimeError(f"Private key file not found: {key_file}")
        
        try:
            context.load_cert_chain(
                certfile=cert_file,
                keyfile=key_file,
                password=key_password if key_password else None
            )
            if on_message:
                on_message(f"TLS: Loaded client certificate from {cert_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to load client certificate/key: {e}")
    
    # Set cipher suite if specified
    cipher_suite = tls_config.get('cipher_suite')
    if cipher_suite:
        try:
            context.set_ciphers(cipher_suite)
            if on_message:
                on_message(f"TLS: Using cipher suite: {cipher_suite}")
        except Exception as e:
            raise RuntimeError(f"Failed to set cipher suite: {e}")
    
    return context



def send_grouped_dicom(
    grouped: Dict[str, Dict[str, list]],
    config: Dict[str, Any],
    logger=None,
    on_message: Callable[[str], None] = None,
    transmission_history=None,
) -> None:
    """
    Send all datasets in grouped dict to remote SCP via C-STORE.

    grouped: {study_uid: {series_uid: [ (ds, pixel_arr) ]}}
    config: {
        server, port, calling_ae, called_ae,
        use_tls (bool): Enable TLS/SSL connection,
        tls_config (dict): TLS configuration (cert_file, key_file, ca_file, etc.)
    }
    logger: optional logger for errors
    on_message: optional callback to append status messages
    transmission_history: optional TransmissionHistory instance for recording

    Raises on first error, enforcing all-or-nothing semantics.
    """
    import time
    _ensure_dependencies()

    server = config.get("server")
    port = int(config.get("port") or 104)
    calling_ae = str(config.get("calling_ae") or "DCMCREATOR")
    called_ae = str(config.get("called_ae") or "ANY-SCP")

    # Initialize Application Entity
    ae = AE(ae_title=calling_ae.encode("ascii", errors="ignore"))

    # Build requested presentation contexts from actual datasets
    try:
        from pynetdicom.uid import ExplicitVRLittleEndian as TS_ExplicitLE
        from pynetdicom.uid import ImplicitVRLittleEndian as TS_ImplicitLE
        try:
            from pynetdicom.uid import DeflatedExplicitVRLittleEndian as TS_DeflatedExplicitLE
            common_ts = [TS_ExplicitLE, TS_ImplicitLE, TS_DeflatedExplicitLE]
        except Exception:
            common_ts = [TS_ExplicitLE, TS_ImplicitLE]
    except Exception:
        common_ts = []

    # Collect SOP Class UIDs and their Transfer Syntaxes from datasets
    sop_contexts = {}  # {sop_uid: set(transfer_syntaxes)}
    for series_map in grouped.values():
        for instances in series_map.values():
            for ds, _ in instances:
                sop_uid = getattr(ds, 'SOPClassUID', None)
                if sop_uid:
                    sop_uid_str = str(sop_uid)
                    if sop_uid_str not in sop_contexts:
                        sop_contexts[sop_uid_str] = set()
                    
                    # Get the dataset's transfer syntax
                    try:
                        # Check file_meta first (standard location)
                        if hasattr(ds, 'file_meta') and hasattr(ds.file_meta, 'TransferSyntaxUID'):
                            ts_uid = str(ds.file_meta.TransferSyntaxUID)
                            sop_contexts[sop_uid_str].add(ts_uid)
                        # Fallback: check if dataset itself has it
                        elif hasattr(ds, 'TransferSyntaxUID'):
                            ts_uid = str(ds.TransferSyntaxUID)
                            sop_contexts[sop_uid_str].add(ts_uid)
                        else:
                            # No transfer syntax found, will use common_ts fallback
                            pass
                    except Exception:
                        # If we can't get transfer syntax, fallback to common ones
                        pass

    # Report and request contexts for each SOP Class UID with its transfer syntaxes
    if on_message:
        on_message(f"Preparing presentation contexts for {len(sop_contexts)} SOP classes")
    
    for sop_uid, ts_set in sop_contexts.items():
        sop_name = get_sop_name(sop_uid)
        if on_message:
            on_message(f"  - {sop_name}")
        
        # If we found specific transfer syntaxes, use them; otherwise use common ones
        if ts_set:
            # Add the dataset's actual transfer syntaxes
            transfer_syntaxes = list(ts_set)
            # Also add common uncompressed transfer syntaxes as fallback
            if common_ts:
                transfer_syntaxes.extend(common_ts)
            ae.add_requested_context(sop_uid, transfer_syntax=transfer_syntaxes)
            if on_message and len(ts_set) > 0:
                on_message(f"    Transfer syntaxes: {len(ts_set)} from dataset + {len(common_ts)} fallback")
        elif common_ts:
            # No specific transfer syntax found, use common ones
            ae.add_requested_context(sop_uid, transfer_syntax=common_ts)
        else:
            # No transfer syntaxes available at all
            ae.add_requested_context(sop_uid)

    # Optionally add Verification SOP for echo
    if VerificationSOPClass is not None:
        ae.add_requested_context(VerificationSOPClass)

    # Configure TLS if requested
    use_tls = config.get("use_tls", False)
    tls_context = None
    if use_tls:
        tls_config = config.get("tls_config", {})
        if on_message:
            on_message("Configuring TLS/SSL connection...")
        try:
            tls_context = _create_tls_context(tls_config, logger, on_message)
        except Exception as e:
            error_msg = f"Failed to configure TLS: {e}"
            if logger:
                logger.error(error_msg)
            if on_message:
                on_message(f"X {error_msg}")
            raise RuntimeError(error_msg) from e

    # Associate
    if on_message:
        tls_status = " (TLS/SSL)" if use_tls else ""
        on_message(f"Connecting to {server}:{port}{tls_status} as {calling_ae} -> {called_ae} ...")
    
    try:
        if use_tls and tls_context:
            # Associate with TLS
            # Pass server hostname for certificate verification if check_hostname is enabled
            server_hostname = server if tls_context.check_hostname else None
            assoc = ae.associate(
                server, 
                port, 
                ae_title=called_ae.encode("ascii", errors="ignore"),
                tls_args=(tls_context, server_hostname)  # (ssl_context, server_hostname)
            )
        else:
            # Associate without TLS
            assoc = ae.associate(server, port, ae_title=called_ae.encode("ascii", errors="ignore"))
    except Exception as e:
        # Network/connection error before association could be attempted
        error_msg = f"Connection error to {server}:{port}: {e}"
        if logger:
            logger.error(error_msg)
        if on_message:
            on_message(f"X {error_msg}")
        raise RuntimeError(error_msg) from e
    
    if not assoc.is_established:
        # Association was rejected or failed
        # Try to get more details about why
        reject_reason = "Unknown reason"
        
        try:
            # Get rejection details if available
            if hasattr(assoc, 'rejected'):
                reject_reason = f"Association rejected by server"
            elif hasattr(assoc, 'aborted'):
                reject_reason = f"Association aborted"
            else:
                # Check for common issues
                import socket
                try:
                    # Quick test if server is reachable
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((server, port))
                    sock.close()
                    if result != 0:
                        reject_reason = f"Cannot connect to server (connection refused or timeout)"
                    else:
                        reject_reason = f"Server rejected association (check AE titles)"
                except:
                    reject_reason = f"Network error or server not reachable"
        except:
            pass
        
        error_msg = f"Association failed to {server}:{port} ({calling_ae} -> {called_ae}): {reject_reason}"
        
        if logger:
            logger.error(error_msg)
        if on_message:
            on_message(f"X {error_msg}")
        
        raise RuntimeError(error_msg)
    if on_message:
        try:
            accepted = getattr(assoc, 'accepted_contexts', [])
            on_message(f"Association established, {len(accepted)} presentation contexts accepted")
            # Log which SOPs were accepted
            for ctx in accepted:
                try:
                    sop_uid = str(ctx.abstract_syntax)
                    sop_name = get_sop_name(sop_uid)
                    on_message(f"  + {sop_name}")
                except Exception:
                    pass
        except Exception:
            on_message("Association established")

    # Check if C-ECHO should be skipped
    skip_c_echo = config.get('skip_c_echo', False)
    
    try:
        # Send a C-ECHO first (optional health check)
        # Note: Some servers may close association after C-ECHO, skip if needed
        if not skip_c_echo and VerificationSOPClass is not None:
            if on_message:
                on_message("Verifying connectivity (C-ECHO)...")
            try:
                status = assoc.send_c_echo()
                # Safely get status code
                status_code = getattr(status, 'Status', None) if status else None
                if status and status_code and status_code != 0x0000:
                    msg = f"C-ECHO failed: 0x{status_code:04X}"
                    if logger:
                        logger.error(msg)
                    if on_message:
                        on_message(msg)
                    raise RuntimeError(msg)
                else:
                    if on_message:
                        on_message("C-ECHO OK")
            except Exception as e:
                # If C-ECHO fails but we can still send, log and continue
                if on_message:
                    on_message(f"C-ECHO skipped or failed (continuing with C-STORE): {e}")
                if logger:
                    logger.warning(f"C-ECHO issue, continuing: {e}")
        elif skip_c_echo:
            if on_message:
                on_message("C-ECHO skipped (disabled by user)")
            if logger:
                logger.info("C-ECHO skipped as requested by user configuration")

        # Iterate through grouped datasets and send each via C-STORE
        total = 0
        # Pre-compute total count for nicer progress messages
        total_count = sum(len(instances) for series_map in grouped.values() for instances in series_map.values())
        sent_count = 0
        for study_uid, series_map in grouped.items():
            for series_uid, instances in series_map.items():
                for ds, _ in instances:
                    # Ensure dataset has file meta and SOP UIDs; if not, try to fix minimally
                    if not hasattr(ds, 'SOPClassUID') or not hasattr(ds, 'SOPInstanceUID'):
                        raise RuntimeError("Dataset missing SOP UIDs")
                    
                    sent_count += 1
                    sop_class_uid = str(getattr(ds, 'SOPClassUID', ''))
                    sop_name = get_sop_name(sop_class_uid)
                    
                    if on_message:
                        uid = getattr(ds, 'SOPInstanceUID', '')
                        on_message(f"Sending {sent_count}/{total_count} {sop_name} SOPInstanceUID={uid}...")
                    
                    # Check association is still active before sending
                    if not assoc.is_established:
                        raise RuntimeError("Association was closed by server before C-STORE")
                    
                    # Send with timing (avoid calling _estimate_dataset_bytes before send)
                    start_time = time.time()
                    status = assoc.send_c_store(ds)
                    duration = time.time() - start_time
                    
                    # Estimate size after successful send (for logging)
                    size_bytes = _estimate_dataset_bytes(ds)
                    total += 1
                    
                    if status is None:
                        raise RuntimeError("No response to C-STORE")
                    # Safely get status code
                    status_code = getattr(status, 'Status', None)
                    if status_code != 0x0000:
                        msg = f"C-STORE failed (Status=0x{status_code:04X})" if status_code else f"C-STORE failed (no status code)"
                        msg += f" for SOPInstanceUID={getattr(ds, 'SOPInstanceUID', '')}"
                        if logger:
                            logger.error(msg)
                        if on_message:
                            on_message(msg)
                        # Record failed transmission
                        if transmission_history:
                            transmission_history.record_transmission(
                                filename=getattr(ds, 'SOPInstanceUID', 'unknown'),
                                server_ip=server,
                                server_port=port,
                                calling_ae=calling_ae,
                                called_ae=called_ae,
                                success=False,
                                bytes_sent=0,
                                duration_seconds=duration,
                                error_message=msg,
                                patient_name=str(getattr(ds, 'PatientName', '')),
                                patient_id=str(getattr(ds, 'PatientID', '')),
                                study_uid=study_uid,
                                series_uid=series_uid
                            )
                        raise RuntimeError(msg)
                    else:
                        # Safely format success message
                        status_code_str = f"0x{status_code:04X}" if status_code is not None else "OK"
                        if on_message:
                            on_message(f"OK {status_code_str} (~{size_bytes} bytes, {duration:.2f}s)")
                        # Record successful transmission
                        if transmission_history:
                            transmission_history.record_transmission(
                                filename=getattr(ds, 'SOPInstanceUID', 'unknown'),
                                server_ip=server,
                                server_port=port,
                                calling_ae=calling_ae,
                                called_ae=called_ae,
                                success=True,
                                bytes_sent=size_bytes,
                                duration_seconds=duration,
                                error_message=None,
                                patient_name=str(getattr(ds, 'PatientName', '')),
                                patient_id=str(getattr(ds, 'PatientID', '')),
                                study_uid=study_uid,
                                series_uid=series_uid
                            )
        if on_message:
            on_message(f"Successfully sent {total} instances")
    finally:
        try:
            if on_message:
                on_message("Releasing association...")
            assoc.release()
        except Exception:
            pass

def _estimate_dataset_bytes(ds) -> int:
    """Best-effort estimate of the dataset size in bytes for logging purposes.
    Falls back to PixelData length when full encoding fails.
    """
    try:
        from io import BytesIO
        from pydicom.filewriter import dcmwrite
        bio = BytesIO()
        dcmwrite(bio, ds, write_like_original=False)
        return bio.tell()
    except Exception:
        try:
            px = getattr(ds, 'PixelData', b'')
            return len(px)
        except Exception:
            return 0
