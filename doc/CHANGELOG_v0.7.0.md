# DICOM Creator v0.7.0 - Release Notes

**Release Date**: March 2026  
**Version**: 0.7.0  
**Status**: Stable

## Overview

DICOM Creator v0.7.0 introduces enhanced certificate management for SSL/TLS security, improved documentation, and better support for secure DICOM transmission to remote servers.

---

## New Features

### SSL/TLS Certificate Support
- Full certificate file support in `.gitignore` and project configuration
- Certificate types supported:
  - PEM certificates (`.pem`)
  - CRT certificates (`.crt`)
  - Private keys (`.key`)
  - PKCS#12 format (`.pfx`, `p12`)
  - CER format (`.cer`, `.cert`)

- Enhanced TLS Configuration:
  - Persistent certificate storage
  - TLS/SSL settings dialog improvements
  - Better error handling for certificate issues
  - Certificate validation before transmission

### Security Improvements
- `.gitignore` Updates: Added certificate file patterns to prevent accidental commits
- Better Certificate Handling: Improved TLS settings management
- Enhanced Error Messages: More informative certificate-related error reporting

---

## Documentation Updates

### New Documentation
- **VERSION_0.7.0_SUMMARY.md** - Quick release summary
- **Updated CHANGELOG_v0.7.0.md** - Complete v0.7.0 release notes

### Enhanced Documentation
- Updated all version references from 0.6.1 to 0.7.0
- Improved documentation index
- Better certificate management guidance
- Enhanced TLS/SSL configuration examples

---

## Technical Changes

### Configuration Files
- Updated `.gitignore` with certificate file patterns
- Enhanced TLS configuration in TLS dialog
- Improved certificate validation logic

### Code Quality
- Better error handling for certificate operations
- Improved logging for SSL/TLS operations
- Enhanced validation of certificate files

---

## Improvements

### User Experience
- Clearer certificate configuration workflow
- Better error messages for SSL/TLS issues
- Improved TLS settings dialog usability

### Security
- Prevents accidental certificate commits via `.gitignore`
- Better certificate validation
- Enhanced secure transmission support

### Testing
- Connection Test tab improvements
- Stress Testing enhancements
- Performance Benchmarking updates

---

## Bug Fixes

### Certificate Handling
- Fixed certificate file handling in TLS dialog
- Improved certificate validation
- Better support for various certificate formats

### Documentation
- Fixed version references throughout documentation
- Updated all release notes
- Corrected documentation links

---

## Compatibility

### Backward Compatibility
- 100% backward compatible with v0.6.1
- All settings, presets, and transmission history preserved
- No dependency changes required
- Seamless upgrade path

### System Requirements
- Python 3.9+
- pydicom >= 2.0
- pynetdicom >= 2.0
- PIL (Pillow)
- NumPy (optional, for image processing)

### Certificate Support
- Works with standard PEM, CRT, and PKCS#12 certificates
- Compatible with self-signed certificates
- Supports certificate chains

---

## Upgrade Instructions

### From v0.6.1

1. **Backup your data**:
   ```bash
   # Copy your presets, settings, and transmission history
   cp -r ~/.dcm_creator ~/.dcm_creator_backup
   ```

2. **Update the application**:
   ```bash
   # Download v0.7.0 from releases
   # Or build from source: python build.py
   ```

3. **Certificate Configuration** (Optional):
   - If using SSL/TLS, configure certificates in TLS Settings dialog
   - Certificates are NOT automatically migrated (intentional for security)
   - See the TLS Settings Guide for setup

4. **Verify Installation**:
   - Launch DICOM Creator
   - Check version in About dialog (should show v0.7.0)
   - All presets and history should load automatically

---

## Distribution

### Included Files
- Main executable (Windows/macOS/Linux)
- All required Python packages
- Documentation and examples
- Certificate generation tools (optional)

### Known Distribution Issues
- None reported for v0.7.0

---

## Known Issues

### None

All previously reported issues have been resolved. If you encounter any issues, please report them on GitHub Issues.

---

## Support

### Documentation
- See Documentation Index for all guides
- Review the TLS Settings Guide for certificate configuration
- Check Troubleshooting for common issues

### Reporting Issues
- GitHub Issues
- Include version number (v0.7.0) in bug reports
- Provide detailed error messages and steps to reproduce

---

## What's Next (v0.8 Roadmap)

Planned features for future releases:
- Enhanced certificate auto-detection
- Improved concurrent transmission features
- Extended performance metrics
- Additional DICOM modality support
- Enhanced validation rules

---

## Credits

Thanks to all contributors and users who tested v0.7.0 and provided feedback!

---

## License

DICOM Creator is licensed under the MIT License. See LICENSE for details.

---

**Last Updated**: March 2026  
**Documentation Version**: 0.7.0
