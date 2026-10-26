"""
Storage Commitment test peer for AcuoMed (VNA-17060).

listen: SCU-side endpoint that AcuoMed connects to when it sends the N-EVENT-REPORT.
        Modes: silent (never answer), delay (answer late), abort, normal.
action: sends a Storage Commitment N-ACTION request to AcuoMed.
"""
import argparse
import ssl
import time
import threading

from pydicom.dataset import Dataset
from pydicom.uid import UID
from pynetdicom import AE, evt
from pynetdicom.sop_class import StorageCommitmentPushModel

PUSH_MODEL_INSTANCE = "1.2.840.10008.1.20.1.1"


def make_server_context(args):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert, args.key)
    if args.ca:
        context.load_verify_locations(args.ca)
        context.verify_mode = ssl.CERT_REQUIRED
    return context


def make_client_context(args):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    if args.client_cert:
        context.load_cert_chain(args.client_cert, args.client_key)
    return context


def listen(args):
    release = threading.Event()

    def on_event_report(event):
        print(f"{time.strftime('%X')} N-EVENT-REPORT received, mode={args.mode}", flush=True)
        if args.mode == "silent":
            release.wait()
        elif args.mode == "delay":
            time.sleep(args.delay)
        elif args.mode == "abort":
            event.assoc.abort()
        status = Dataset()
        status.Status = 0x0000
        return status, None

    ae = AE(ae_title=args.ae)
    ae.network_timeout = 3600
    ae.acse_timeout = 3600
    ae.dimse_timeout = 3600
    # AcuoMed requests the association and proposes the SCP role, so we act as the SCU.
    ae.add_supported_context(StorageCommitmentPushModel, scu_role=True, scp_role=True)
    handlers = [
        (evt.EVT_N_EVENT_REPORT, on_event_report),
        (evt.EVT_ACCEPTED, lambda e: print(f"{time.strftime('%X')} association accepted from {e.address}", flush=True)),
        (evt.EVT_CONN_CLOSE, lambda e: print(f"{time.strftime('%X')} connection closed", flush=True)),
    ]
    context = make_server_context(args) if args.tls else None
    print(f"Listening on {args.host}:{args.port} AE={args.ae} TLS={args.tls} mode={args.mode}", flush=True)
    try:
        ae.start_server((args.host, args.port), evt_handlers=handlers, ssl_context=context)
    except KeyboardInterrupt:
        release.set()


def action(args):
    ae = AE(ae_title=args.ae)
    ae.add_requested_context(StorageCommitmentPushModel)

    request = Dataset()
    request.TransactionUID = UID(args.transaction_uid)
    sequence = []
    for pair in args.instance:
        sop_class, sop_instance = pair.split(",")
        item = Dataset()
        item.ReferencedSOPClassUID = sop_class
        item.ReferencedSOPInstanceUID = sop_instance
        sequence.append(item)
    request.ReferencedSOPSequence = sequence

    context = make_client_context(args) if args.tls else None
    association = ae.associate(args.host, args.port, ae_title=args.called_ae,
                               tls_args=(context, args.host) if context else None)
    if not association.is_established:
        raise SystemExit("Association with AcuoMed was not established")
    status, _ = association.send_n_action(request, 1, StorageCommitmentPushModel, PUSH_MODEL_INSTANCE)
    print(f"N-ACTION status: {status}")
    association.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    peer = sub.add_parser("listen")
    peer.add_argument("--host", default="0.0.0.0")
    peer.add_argument("--port", type=int, default=2763)
    peer.add_argument("--ae", default="DICOMTEST_SC", help="AE title AcuoMed is configured to call")
    peer.add_argument("--mode", choices=["silent", "delay", "abort", "normal"], default="silent")
    peer.add_argument("--delay", type=float, default=200, help="seconds, for --mode delay")
    peer.add_argument("--tls", action="store_true")
    peer.add_argument("--cert", default="server_cert.pem")
    peer.add_argument("--key", default="server_key.pem")
    peer.add_argument("--ca", help="require and verify a client certificate")
    peer.set_defaults(run=listen)

    act = sub.add_parser("action")
    act.add_argument("--host", required=True)
    act.add_argument("--port", type=int, required=True)
    act.add_argument("--ae", default="DICOMTEST_SC", help="our calling AE; must match the AcuoMed external device")
    act.add_argument("--called-ae", required=True)
    act.add_argument("--instance", action="append", required=True, metavar="SOPCLASS,SOPINSTANCE",
                     help="previously stored instance; repeatable")
    act.add_argument("--transaction-uid", default="1.2.826.0.1.3680043.8.498.17060")
    act.add_argument("--tls", action="store_true")
    act.add_argument("--client-cert")
    act.add_argument("--client-key")
    act.set_defaults(run=action)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
