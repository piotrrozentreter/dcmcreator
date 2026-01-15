"""
Remote DICOM sending utilities.

Implements C-STORE for all loaded datasets (grouped by Study/Series).
All-or-nothing: aborts on first error.
"""
from typing import Callable, Dict, Any

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

    sop_uids = set()
    for series_map in grouped.values():
        for instances in series_map.values():
            for ds, _ in instances:
                uid = getattr(ds, 'SOPClassUID', None)
                if uid:
                    sop_uids.add(uid)

    # Report and request contexts for each SOP Class UID present in datasets
    if on_message:
        on_message(f"Preparing presentation contexts for {len(sop_uids)} SOP classes")
    for sop_uid in sop_uids:
        if common_ts:
            ae.add_requested_context(sop_uid, transfer_syntax=common_ts)
        else:
            ae.add_requested_context(sop_uid)

    # Optionally add Verification SOP for echo
    if VerificationSOPClass is not None:
        ae.add_requested_context(VerificationSOPClass)

    # Associate
    if on_message:
        on_message(f"Connecting to {server}:{port} as {calling_ae} -> {called_ae} ...")
    assoc = ae.associate(server, port, ae_title=called_ae.encode("ascii", errors="ignore"))
    if not assoc.is_established:
        if logger:
            logger.error("Association to %s:%s as %s -> %s failed", server, port, calling_ae, called_ae)
        if on_message:
            on_message("Association failed")
        raise RuntimeError("Association failed")
    if on_message:
        try:
            accepted = getattr(assoc, 'accepted_contexts', [])
            on_message(f"Association established, {len(accepted)} presentation contexts accepted")
        except Exception:
            on_message("Association established")

    try:
        # Send a C-ECHO first (optional health check)
        if VerificationSOPClass is not None:
            if on_message:
                on_message("Verifying connectivity (C-ECHO)...")
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

        # Iterate through grouped datasets and send each via C-STORE
        total = 0
        # Pre-compute total count for nicer progress messages
        total_count = sum(len(instances) for series_map in grouped.values() for instances in series_map.values())
        sent_count = 0
        import time
        for study_uid, series_map in grouped.items():
            for series_uid, instances in series_map.items():
                for ds, _ in instances:
                    # Ensure dataset has file meta and SOP UIDs; if not, try to fix minimally
                    if not hasattr(ds, 'SOPClassUID') or not hasattr(ds, 'SOPInstanceUID'):
                        raise RuntimeError("Dataset missing SOP UIDs")
                    # Estimate bytes to send (best effort)
                    size_bytes = _estimate_dataset_bytes(ds)
                    sent_count += 1
                    if on_message:
                        uid = getattr(ds, 'SOPInstanceUID', '')
                        on_message(f"Sending {sent_count}/{total_count} SOPInstanceUID={uid} (~{size_bytes} bytes)...")
                    # Send with timing
                    start_time = time.time()
                    status = assoc.send_c_store(ds)
                    duration = time.time() - start_time
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
                            on_message(f"OK {status_code_str}")
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
