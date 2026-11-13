# DICOM Receiver

Receive outbound DICOM transfers from an archive such as ACUO VNA using the
internal Python Storage SCP. No external executable is required.

## Quick Start

1. Run DICOM Creator and select **View > DICOM Receiver**.
2. In **Listener**, set **Bind IPv4 address** to this workstation's network IPv4
   address. The default `127.0.0.1` accepts local tests only; `0.0.0.0` listens on
   all IPv4 interfaces. Configure a port, for example `11112`.
3. Keep or change **Called AE title** (`DCMCREATOR_SCP`). Matching is required.
4. Choose an **Output directory**. Optionally enter allowed calling AE titles and
   source IPv4 addresses, separated by commas. Blank lists allow any sender;
   when both are supplied, both restrictions must match.
5. If required, configure **TLS** as described below, then select **Start**.
6. Configure an outbound destination in your VNA with this workstation's reachable
   IP address, the same port, and the same called AE title. Do not configure the
   VNA to send to `127.0.0.1` or `0.0.0.0` on another machine.
7. Allow inbound TCP traffic on that port through the workstation firewall,
   restricted to the VNA's source address where possible. Test C-ECHO from the
   VNA if available, then export a small synthetic study to this destination.
8. Check the receive log, saved files, counters, and the VNA's outbound results.
   Select **Stop** when finished; this also aborts active transfers.

ACUO destination configuration and export controls depend on your installation.
Confirm its calling AE, actual sending nodes/IPs, TLS policy, SOP Classes, and
transfer syntaxes with your administrator or conformance statement. No
ACUO-specific compatibility has been certified by this feature.

## GUI

- **Listener / TLS** settings are locked while starting, listening, or stopping.
- **Prefer RLE Lossless** selects RLE (`1.2.840.10008.1.2.5`) first when the
  sender offers it together with other syntaxes in the same presentation context.
  It is off by default; uncompressed-only senders still work when it is on.
  This changes negotiation preference only, not the encoding of received images.
- **Start / Stop** run network lifecycle operations outside the GUI thread.
- The receive log shows source IP, calling AE, SOP Instance UID, negotiated
  transfer syntax, saved path, and status. Scroll horizontally for all columns.
- Received/failed/byte/association counters accumulate until the application is
  closed. Bytes measure saved file sizes, including file metadata, not wire bytes.
- **Clear Log** clears only visible rows, not counters or saved files. The view
  retains 500 rows; the event queue holds 1,000 events. Queue overflow increments
  **Log events dropped** without blocking transfers or affecting counters.
- Hiding the tab does not stop reception. Exiting the application does.

## Files and Status

Received instances are stored as Part 10 `.dcm` files with file metadata. Filenames
contain a validated SOP Instance UID and a random suffix. Receiving the same UID
again creates another file; no deduplication or replacement is performed.
Temporary `.part` files are renamed after writing and flushing. A process crash
can leave a partial file; do not treat `.part` files as completed instances.

The receiver advertises the installed pynetdicom version's standard Storage SOP
Classes and pydicom transfer syntaxes, plus Verification. Unknown/private SOP
Classes are not implicitly accepted. Compressed pixel payloads are saved without
pixel decoding or transcoding. Receiving a compressed object does not establish
that it can be displayed or that its compressed image stream is valid.

| C-STORE response | Meaning |
| --- | --- |
| `0x0000` | File successfully written, flushed, and renamed |
| `0xA700` | File write/storage resource failure |
| `0xA900` | Dataset SOP UIDs do not match request or negotiated SOP Class |
| `0xC210` | Missing/invalid SOP UIDs or malformed dataset |
| `0xC211` | Other dataset processing failure |

This is a test destination, not a production archive or full DICOM IOD validator.
C-STORE success is not Storage Commitment. There is no automatic complete-study
determination: compare received instance UIDs/counts with an expected manifest or
the VNA's export report. Duplicate receipts increase the received count.

## TLS and Privacy

Enable TLS and supply a server certificate and **unencrypted** private key in PEM
format. The receiver uses TLS 1.2 or newer. Protect the private key with filesystem
permissions; encrypted-key prompting is not supported. Configure the VNA to trust
the server certificate and verify its identity according to your site's policy.

Supplying **Client CA** also requires a valid client certificate signed by a
trusted CA (mutual TLS). Without it, TLS encrypts the connection but does not
authenticate the sender by client certificate. AE/IP restrictions are not a
substitute for cryptographic authentication.

Plain TCP is the initial local-test setting. Use the security policy required by
your environment before exposing the listener. The receiver does not log patient
names or patient IDs, but saved files retain their original data and UIDs/paths in
the UI may still be sensitive. Use synthetic data for tests and control access to
the output directory. No anonymization or automatic deletion is performed.

## Troubleshooting

- **Cannot connect:** confirm the listener is started, the bind IP belongs to this
  workstation, routing works, and the firewall allows the chosen inbound port.
- **Address already in use:** stop the other listener or choose another port.
- **Association rejected/aborted:** compare called/calling AEs and source IPs;
  check the VNA's proposed SOP Classes and transfer syntaxes. Limits are 10
  concurrent associations, 30-second ACSE and 60-second DIMSE/network timeouts.
- **Association request timed out:** inspect the receiver log during a fresh
  attempt. `connected` means a TCP connection reached the listener; `requested`
  means a DICOM association request was decoded, with the called AE in **Detail**.
  `association` means acceptance and includes the accepted context count.
  `rejected` includes DICOM result/source/diagnostic codes; `released`, `aborted`,
  and `disconnected` show how the session ended. No `connected` event suggests
  checking the endpoint, listener state, and transport path, but missing events
  can also result from log clearing, queue overflow, or a stale application.
  A connection without `requested` requires checking sender/receiver transport
  settings (including TLS) and the sender's association trace. A Python C-ECHO
  success alone does not establish that the VNA's Storage request succeeds.
- **TLS failure:** check certificate/key pairing, CA trust, validity, peer identity,
  and whether a client certificate is required. Do not disable verification to
  bypass the error.
- **Store failed:** check disk space and output-directory permissions. Failed
  writes must not be reported as successful by the sender.

### ACUO RLE Context Lookup Failure

An ACUO `GetContextID` / `DILIB_ERROR_CONTEXTID_NOT_LOCATED` error during send is
different from an association timeout: the sender could not select an accepted
presentation context for its outgoing message. The error by itself does not
identify whether the missing match is a SOP Class, transfer syntax, role, or
sender-side conversion/selection issue.

For an RLE test, restart DICOM Creator after updating the source, enable
**Prefer RLE Lossless** in **Listener**, and start the receiver. Establish a fresh
association by retrying one synthetic export from ACUO. Each `context` event now
shows its context ID and SOP Class in **Detail**, and its accepted transfer syntax
in **Transfer Syntax UID**. Confirm that the outgoing object's actual SOP Class
has an accepted RLE context; modality alone does not determine its SOP Class.

The default syntax preference can select an uncompressed syntax when ACUO offers
both it and RLE in one context. DICOM accepts only one transfer syntax per
presentation context. Enabling this option favors RLE in that case, but cannot
create an RLE context if ACUO never proposes one. ACUO can also propose separate
contexts for the same SOP Class with different transfer syntaxes.

If the matching RLE context is accepted and ACUO still fails, compare that accepted
context with ACUO's `GetContextID` trace for the intended SOP Class, transfer syntax,
and role. No ACUO source or destination policy is changed by this receiver option.

## Tests

From the repository root, using the project's configured Python environment:

```console
python -m unittest test.test_dicom_receiver test.test_dicom_receiver_tab -v
```

Tests use synthetic data and ephemeral loopback ports. GUI tests need a Tk display
and skip if none is available. Actual VNA acceptance testing remains necessary.