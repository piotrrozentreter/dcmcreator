# DICOM Creator v0.9.2 - Release Notes

**Version**: 0.9.2  
**Release Date**: October 26, 2026

## Overview

Version 0.9.2 adds a Storage Commitment Push Model request to the Remote tab. Use it to ask a DICOM peer to take responsibility for instances that have already been stored there.

## New Feature: Storage Commitment N-ACTION

- Request commitment for loaded DICOM instances using the Storage Commitment Push Model.
- Use the existing Remote tab server address, port, calling/called AE titles, and optional TLS settings.
- Enter a Transaction UID; a UID is generated automatically when available.
- Validate the Transaction UID and referenced SOP Class and Instance UIDs before sending, and remove duplicate references.
- Display the N-ACTION response and report association or peer errors.

### Important Behavior

The instances must already have been sent to and stored by the peer. The Storage Commitment action only sends references; it does not transmit the DICOM files.

A successful N-ACTION response means the peer accepted the request, not that it completed commitment. The final result is normally delivered later in an N-EVENT-REPORT. DICOM Creator does not receive that report, so confirm the final outcome through the peer's workflow or logs.

The remote DICOM peer must support the Storage Commitment Push Model and be configured to process N-ACTION requests. TLS uses the existing Remote tab TLS configuration.

## Usage

1. Load the DICOM instances whose commitment you want to request.
2. Send those instances to the remote peer using the Remote tab, if they are not already stored there.
3. Configure the Remote tab with the peer address, port, AE titles, and TLS settings as needed.
4. Confirm or replace the Storage Commitment Transaction UID.
5. Select **Request Storage Commitment for Loaded Instances** and review the response message.

## Compatibility

No DICOM file format changes are introduced. The feature depends on Storage Commitment support at the remote peer; existing send and query workflows remain unchanged.