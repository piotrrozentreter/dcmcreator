# DICOM Creator v0.7.0 - Quick Summary

**Version**: 0.7.0  
**Release Date**: March 2026  
**Type**: Production Release

## What Changed

### Certificate Management (NEW)
- Full SSL/TLS certificate support for secure DICOM transmission
- Added to `.gitignore`: `*.crt`, `*.key`, `*.pem`, `*.pfx`, `*.p12`, `*.cer`, `*.cert`
- Enhanced TLS settings dialog with better certificate handling
- Support for multiple certificate formats

### Documentation
- Updated all documentation to v0.7.0
- New CHANGELOG_v0.7.0.md with complete release notes
- Improved documentation index

### Security
- Prevents accidental certificate file commits
- Better certificate validation
- Enhanced error reporting for SSL/TLS operations

---

## Upgrade Path

**v0.6.1 to v0.7.0**: Drop-in replacement
- 100% backward compatible
- All presets and settings preserved
- No action required unless using certificates

---

## Key Features Still Included

- DICOM creation and editing
- Server presets management
- Remote DICOM transmission
- Connection testing
- Stress testing
- Performance benchmarking
- Parallel transmission
- Transmission history tracking
- DICOM validation
- Tag viewer

---

## Quick Start

1. **Download v0.7.0** from releases
2. **Run the installer** (Windows) or extract (Linux/macOS)
3. **Launch DICOM Creator**
4. **Use as before** - all your presets load automatically

### For Certificate Support
1. Go to **Remote -> TLS Settings...**
2. Configure your certificate paths
3. Enable **"Use TLS/SSL"** on Remote tab
4. Send DICOM securely

---

## Resources

- [Full Release Notes](CHANGELOG_v0.7.0.md)
- [Documentation Index](INDEX.md)
- [Getting Started](GETTING_STARTED.md)
- [Build Instructions](BUILD_INSTRUCTIONS.md)

---

## FAQ

**Q: Do I need to do anything after upgrading?**  
A: No. Just download and run. All your presets and settings load automatically.

**Q: Will my certificates be automatically imported?**  
A: No. You'll need to configure them manually in TLS Settings (this is intentional for security).

**Q: Is this backward compatible?**  
A: Yes, 100%. It's a drop-in replacement for v0.6.1.

**Q: What if I find a bug?**  
A: Report it on [GitHub Issues](https://github.com/piotrrozentreter/dcmcreator/issues).

---

**Document Version**: 0.7.0  
**Last Updated**: March 2026
