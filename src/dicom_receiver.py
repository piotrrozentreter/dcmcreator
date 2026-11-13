"""Internal DICOM Storage SCP for testing outbound archive transfers."""

import ipaddress
import os
from pathlib import Path
import queue
import re
import ssl
import tempfile
import threading
from datetime import datetime
from uuid import uuid4

import pydicom
from pydicom.uid import AllTransferSyntaxes, RLELossless, UID
from pynetdicom import AE, AllStoragePresentationContexts, evt
from pynetdicom.sop_class import Verification


class DicomReceiver:
    """Receive DICOM instances without decoding or transcoding pixel data.

    Counters are cumulative for this object's lifetime. The bounded event queue
    contains operational metadata only, never patient demographics or datasets.
    """

    def __init__(self):
        self.events = queue.Queue(maxsize=1000)
        self._server = None
        self._ae = None
        self._output = None
        self._allowed_ips = set()
        self._lifecycle_lock = threading.Lock()
        self._storage_lock = threading.Lock()
        self._stats_lock = threading.Lock()
        self._stats = dict(received=0, failed=0, bytes=0, associations=0,
                           dropped_events=0)

    @property
    def running(self):
        """Whether the listening server has been started."""
        return self._server is not None

    @property
    def address(self):
        """Actual bound address, including an OS-assigned test port."""
        return self._server.server_address if self._server else None

    @property
    def stats(self):
        """Return a thread-safe copy of cumulative counters."""
        with self._stats_lock:
            return dict(self._stats)

    @staticmethod
    def _ae_title(value):
        value = str(value).strip()
        if not value or len(value) > 16 or any(
            ord(character) < 32 or ord(character) > 126 or character == "\\"
            for character in value
        ):
            raise ValueError("AE titles must contain 1-16 printable ASCII characters without backslash")
        return value

    @staticmethod
    def _uid(value):
        text = str(value)
        if (len(text) > 64 or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", text)
                or any(len(part) > 1 and part.startswith("0") for part in text.split("."))
                or not UID(text).is_valid):
            raise ValueError("Invalid SOP UID")
        return text

    def start(self, output_dir, host="127.0.0.1", port=11112,
              ae_title="DCMCREATOR_SCP", allowed_calling_aes=(),
              allowed_ips=(), tls_cert=None, tls_key=None, tls_ca=None,
              prefer_rle=False):
        """Start a non-blocking IPv4 listener with strict called-AE matching.

        Port 0 requests an ephemeral port for tests. Empty sender restrictions
        allow any sender. TLS requires a certificate and key; supplying a CA
        additionally requires and verifies a client certificate.
        prefer_rle chooses RLE first when it is offered alongside other syntaxes
        in one presentation context; it does not compress or transcode data.
        """
        with self._lifecycle_lock:
            if self.running:
                raise RuntimeError("Receiver is already running")
            host = str(ipaddress.IPv4Address(host))
            port = int(port)
            if not 0 <= port <= 65535:
                raise ValueError("Port must be between 0 and 65535")
            ae_title = self._ae_title(ae_title)
            callers = [self._ae_title(value) for value in allowed_calling_aes]
            addresses = {str(ipaddress.IPv4Address(value)) for value in allowed_ips}
            if not str(output_dir).strip():
                raise ValueError("Output directory is required")
            output = Path(output_dir).expanduser().resolve()
            output.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=str(output)):
                pass

            context = None
            if tls_cert or tls_key or tls_ca:
                if not tls_cert or not tls_key:
                    raise ValueError("TLS requires both a certificate and private key")
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                context.load_cert_chain(tls_cert, tls_key, password=lambda: "")
                if tls_ca:
                    context.load_verify_locations(cafile=tls_ca)
                    context.verify_mode = ssl.CERT_REQUIRED

            application = AE(ae_title=ae_title)
            application.require_called_aet = True
            application.require_calling_aet = callers
            application.maximum_associations = 10
            application.acse_timeout = 30
            application.dimse_timeout = 60
            application.network_timeout = 60
            transfer_syntaxes = list(AllTransferSyntaxes)
            if prefer_rle:
                transfer_syntaxes.remove(RLELossless)
                transfer_syntaxes.insert(0, RLELossless)
            for presentation in AllStoragePresentationContexts:
                application.add_supported_context(presentation.abstract_syntax,
                                                  transfer_syntaxes)
            application.add_supported_context(Verification)
            self._output = output
            self._allowed_ips = addresses
            handlers = [(evt.EVT_C_STORE, self._handle_store),
                        (evt.EVT_C_ECHO, self._handle_echo),
                        (evt.EVT_CONN_OPEN, self._connected),
                        (evt.EVT_CONN_CLOSE, self._disconnected),
                        (evt.EVT_REQUESTED, self._requested),
                        (evt.EVT_ACCEPTED, self._accepted),
                        (evt.EVT_REJECTED, self._rejected),
                        (evt.EVT_RELEASED, self._released),
                        (evt.EVT_ABORTED, self._aborted)]
            self._server = application.start_server(
                (host, port), block=False, ssl_context=context, evt_handlers=handlers)
            self._ae = application
            self._emit("listening", detail="TLS" if context else "Plain TCP")

    def stop(self):
        """Stop listening, abort active associations, and finish current writes."""
        with self._lifecycle_lock:
            if not self._server:
                return
            for association in self._ae.active_associations:
                association.abort()
            self._server.shutdown()
            self._server.server_close()
            with self._storage_lock:
                self._server = None
                self._ae = None
            self._emit("stopped")

    def _emit(self, kind, **values):
        record = dict(time=datetime.now().strftime("%H:%M:%S"), kind=kind, **values)
        try:
            self.events.put_nowait(record)
        except queue.Full:
            with self._stats_lock:
                self._stats["dropped_events"] += 1

    @staticmethod
    def _peer(event):
        requestor = event.assoc.requestor
        calling_ae = requestor.ae_title
        if not calling_ae:
            calling_ae = getattr(requestor.primitive, "calling_ae_title", "")
        return dict(peer=str(requestor.address), calling_ae=str(calling_ae))

    def _connected(self, event):
        self._emit("connected", detail="TCP connection opened", **self._peer(event))

    def _disconnected(self, event):
        self._emit("disconnected", detail="TCP connection closed", **self._peer(event))

    def _requested(self, event):
        request = event.assoc.requestor.primitive
        self._emit("requested", detail=f"Called AE: {request.called_ae_title}",
                   **self._peer(event))
        if self._allowed_ips and event.assoc.requestor.address not in self._allowed_ips:
            self._emit("blocked", detail="Source IP not allowed", **self._peer(event))
            event.assoc.abort()

    def _accepted(self, event):
        with self._stats_lock:
            self._stats["associations"] += 1
        self._emit("association", detail=f"Accepted contexts: {len(event.assoc.accepted_contexts)}",
                   **self._peer(event))
        for context in event.assoc.accepted_contexts:
            self._emit("context", transfer_syntax=str(context.transfer_syntax[0]),
                   detail=(f"Context ID: {context.context_id}; "
                       f"SOP Class: {context.abstract_syntax}"),
                   **self._peer(event))

    def _rejected(self, event):
        response = event.assoc.acceptor.primitive
        self._emit("rejected", detail=(f"Association rejected: result={response.result}, "
                                      f"source={response.result_source}, diagnostic={response.diagnostic}"),
                   **self._peer(event))

    def _released(self, event):
        self._emit("released", detail="Association released", **self._peer(event))

    def _aborted(self, event):
        self._emit("aborted", detail="Association aborted", **self._peer(event))

    def _handle_echo(self, event):
        self._emit("echo", status="0x0000", **self._peer(event))
        return 0x0000

    def _handle_store(self, event):
        with self._storage_lock:
            temporary = None
            instance_uid = ""
            try:
                dataset = event.dataset
                instance_uid = self._uid(dataset.SOPInstanceUID)
                class_uid = self._uid(dataset.SOPClassUID)
                if (instance_uid != str(event.request.AffectedSOPInstanceUID)
                        or class_uid != str(event.request.AffectedSOPClassUID)
                        or class_uid != str(event.context.abstract_syntax)):
                    return self._failure(event, 0xA900, "SOP UID mismatch")
                dataset.file_meta = event.file_meta
                target = self._output / f"{instance_uid}_{uuid4().hex}.dcm"
                descriptor, name = tempfile.mkstemp(suffix=".part", dir=str(self._output))
                temporary = Path(name)
                with os.fdopen(descriptor, "wb") as stream:
                    pydicom.dcmwrite(stream, dataset, write_like_original=False)
                    stream.flush()
                    os.fsync(stream.fileno())
                size = temporary.stat().st_size
                os.replace(str(temporary), str(target))
                temporary = None
                with self._stats_lock:
                    self._stats["received"] += 1
                    self._stats["bytes"] += size
                self._emit("stored", uid=instance_uid, path=str(target), bytes=size,
                           transfer_syntax=str(event.context.transfer_syntax),
                           status="0x0000", **self._peer(event))
                return 0x0000
            except (ValueError, AttributeError, KeyError):
                return self._failure(event, 0xC210, "Invalid or missing SOP UIDs / dataset")
            except OSError:
                return self._failure(event, 0xA700, "Unable to write received file")
            except Exception:
                return self._failure(event, 0xC211, "Unable to process received dataset")
            finally:
                if temporary is not None:
                    try:
                        temporary.unlink()
                    except OSError:
                        pass

    def _failure(self, event, status, detail):
        with self._stats_lock:
            self._stats["failed"] += 1
        self._emit("failed", status=f"0x{status:04X}", detail=detail, **self._peer(event))
        return status