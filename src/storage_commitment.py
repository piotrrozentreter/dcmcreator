"""Storage Commitment Push Model N-ACTION client."""

import re
from typing import Any, Callable, Dict, Iterable, Tuple

from pydicom.dataset import Dataset
from pydicom.uid import UID
from pynetdicom import AE
from pynetdicom.sop_class import StorageCommitmentPushModel

try:
    from .remote import _create_tls_context
except ImportError:
    from remote import _create_tls_context

PUSH_MODEL_INSTANCE_UID = "1.2.840.10008.1.20.1.1"


def _validated_uid(value: str, label: str) -> UID:
    value = str(value).strip()
    components = value.split(".")
    if (
        len(value) > 64
        or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value)
        or any(len(component) > 1 and component.startswith("0") for component in components)
    ):
        raise ValueError(f"{label} must be a valid DICOM UID")
    uid = UID(value)
    if not uid.is_valid:
        raise ValueError(f"{label} must be a valid DICOM UID")
    return uid


def send_storage_commitment(
    references: Iterable[Tuple[str, str]],
    transaction_uid: str,
    config: Dict[str, Any],
    logger=None,
    on_message: Callable[[str], None] = None,
) -> int:
    """Request Storage Commitment for previously stored SOP instances.

    A successful return is only the N-ACTION response. The final commitment
    outcome is normally reported later using a separate N-EVENT-REPORT.
    """
    transaction_uid = _validated_uid(transaction_uid, "Transaction UID")
    referenced_instances = []
    seen = set()
    for index, (sop_class_uid, sop_instance_uid) in enumerate(references, start=1):
        sop_class_uid = _validated_uid(sop_class_uid, f"SOP Class UID at reference {index}")
        sop_instance_uid = _validated_uid(sop_instance_uid, f"SOP Instance UID at reference {index}")
        pair = (str(sop_class_uid), str(sop_instance_uid))
        if pair in seen:
            continue
        seen.add(pair)
        item = Dataset()
        item.ReferencedSOPClassUID = sop_class_uid
        item.ReferencedSOPInstanceUID = sop_instance_uid
        referenced_instances.append(item)

    if not referenced_instances:
        raise ValueError("At least one stored SOP instance is required")

    server = str(config.get("server") or "").strip()
    port = int(config.get("port") or 104)
    calling_ae = str(config.get("calling_ae") or "DCMCREATOR")
    called_ae = str(config.get("called_ae") or "ANY-SCP")
    if not server:
        raise ValueError("Server address is required")

    request = Dataset()
    request.TransactionUID = transaction_uid
    request.ReferencedSOPSequence = referenced_instances

    ae = AE(ae_title=calling_ae.encode("ascii", errors="ignore"))
    ae.add_requested_context(StorageCommitmentPushModel)

    use_tls = bool(config.get("use_tls", False))
    tls_context = None

    if on_message:
        transport = " with TLS" if use_tls else ""
        on_message(f"Requesting Storage Commitment from {server}:{port}{transport} ({len(referenced_instances)} instances)")

    association = None
    try:
        if use_tls:
            tls_context = _create_tls_context(config.get("tls_config") or {}, logger, on_message)
            server_hostname = server if tls_context.check_hostname else None
            association = ae.associate(
                server,
                port,
                ae_title=called_ae.encode("ascii", errors="ignore"),
                tls_args=(tls_context, server_hostname),
            )
        else:
            association = ae.associate(
                server,
                port,
                ae_title=called_ae.encode("ascii", errors="ignore"),
            )

        if not association.is_established:
            raise RuntimeError(f"Storage Commitment association to {server}:{port} was not established")

        status, _ = association.send_n_action(
            request,
            1,
            StorageCommitmentPushModel,
            PUSH_MODEL_INSTANCE_UID,
        )
        status_code = getattr(status, "Status", None) if status is not None else None
        if status_code != 0x0000:
            detail = getattr(status, "ErrorComment", None) if status is not None else None
            code_text = f"0x{status_code:04X}" if status_code is not None else "no status"
            message = f"Storage Commitment N-ACTION failed ({code_text})"
            if detail:
                message += f": {detail}"
            raise RuntimeError(message)

        if on_message:
            on_message(
                "N-ACTION response success (0x0000): request accepted. "
                "This is not the final commitment result; this app does not receive N-EVENT-REPORT."
            )
        return status_code
    except Exception as error:
        if logger:
            logger.error("Storage Commitment request failed: %s", error)
        if on_message:
            on_message(f"Storage Commitment request failed: {error}")
        raise
    finally:
        if association is not None and association.is_established:
            try:
                association.release()
            except Exception:
                pass