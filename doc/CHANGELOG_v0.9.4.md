# DICOM Creator v0.9.4 - Release Notes

**Version**: 0.9.4

## Features

- Internal DICOM Receiver tab for outbound VNA testing with C-ECHO and C-STORE.
- Optional TLS/mutual TLS, calling-AE/source-IP restrictions, duplicate-safe
  storage, bounded live results, and clean listener shutdown.
- Optional RLE Lossless negotiation preference and connection-stage diagnostics,
  including accepted presentation context IDs, SOP Classes, and transfer syntaxes.

## Fixes

- Selecting a DICOM instance now updates its image and selected metadata instead
  of leaving a previous preview displayed. Ordinary selection does not switch tabs.

## Packaging and Tests

- The bundle includes all source modules, the VR dictionary, README, license,
  and documentation, including the [receiver usage guide](DICOM_RECEIVER.md).
- Added synthetic receiver, GUI, preview-selection, and packaging regressions.
- RLE tests use asymmetric 16-bit pixel patterns to detect orientation errors.
- Received test images are excluded from version control and build resources.

## Limitations

This is a test receiver, not a production archive or full IOD validator. C-STORE
success is not Storage Commitment or proof of a complete study. Interoperability
and TLS must be verified for the target environment. External ACUO source changes
are not included in this release.