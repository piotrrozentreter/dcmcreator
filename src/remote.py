"""
Remote DICOM sending utilities.

Implements C-STORE for all loaded datasets (grouped by Study/Series).
All-or-nothing: aborts on first error.
"""
from typing import Callable, Dict, Any

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
    config: {server, port, calling_ae, called_ae}
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

    # Associate
    if on_message:
        on_message(f"Connecting to {server}:{port} as {calling_ae} -> {called_ae} ...")
    
    try:
        assoc = ae.associate(server, port, ae_title=called_ae.encode("ascii", errors="ignore"))
    except Exception as e:
        # Network/connection error before association could be attempted
        error_msg = f"Connection error to {server}:{port}: {e}"
        if logger:
            logger.error(error_msg)
        if on_message:
            on_message(f"? {error_msg}")
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
        
        error_msg = f"Association failed to {server}:{port} ({calling_ae} ? {called_ae}): {reject_reason}"
        
        if logger:
            logger.error(error_msg)
        if on_message:
            on_message(f"? {error_msg}")
        
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
                    on_message(f"  ? {sop_name}")
                except Exception:
                    pass
        except Exception:
            on_message("Association established")

    try:
        # Send a C-ECHO first (optional health check)
        # Note: Some servers may close association after C-ECHO, skip if needed
        if VerificationSOPClass is not None:
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
