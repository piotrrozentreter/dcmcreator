# DICOM Creator v0.9.2 - Quick Summary

**Version**: 0.9.2  
**Release Date**: October 26, 2026

## What's New

Storage Commitment requests are now available from the Remote tab through the DICOM Storage Commitment Push Model N-ACTION operation.

The request references loaded DICOM instances that have already been stored by the configured peer. It reuses the Remote tab connection and TLS settings, validates the transaction and SOP UIDs, and reports the peer's N-ACTION response.

**Important:** An accepted N-ACTION is not the final commitment result. The peer normally returns that result later through N-EVENT-REPORT, which DICOM Creator does not receive.

## Quick Start

1. Load and send the instances to the remote peer, unless they are already stored there.
2. Set the peer address, port, AE titles, and optional TLS settings in the Remote tab.
3. Confirm the Storage Commitment Transaction UID.
4. Click **Request Storage Commitment for Loaded Instances**.
5. Verify the final commitment outcome with the peer; the immediate response only confirms request acceptance.

See [CHANGELOG_v0.9.2.md](CHANGELOG_v0.9.2.md) for details and limitations.