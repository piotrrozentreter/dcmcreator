# Documentation Organization - v0.7.0

## Directory Structure

```
dcmcreator/
??? src/                          # Source code
?   ??? appgui.py                # Main GUI application
?   ??? app_logic.py             # Business logic
?   ??? dcm.py                   # DICOM operations
?   ??? remote.py                # Remote transmission
?   ??? presets.py               # Server presets
?   ??? tls_dialog.py            # TLS configuration
?   ??? import_helper.py          # Module importing
?   ??? ...
??? doc/                          # Documentation (centralized)
?   ??? INDEX.md                 # [*] Navigation hub
?   ??? README.md                # Main docs
?   ??? CHANGELOG_v0.7.0.md      # v0.7.0 release notes (NEW)
?   ??? CHANGELOG_v0.6.1.md      # v0.6.1 release notes
?   ??? VERSION_0.7.0_SUMMARY.md # Quick v0.7.0 summary (NEW)
?   ??? GETTING_STARTED.md       # Quick start guide
?   ??? BUILD_INSTRUCTIONS.md    # Build guide
?   ??? DISTRIBUTION_GUIDE.md    # Distribution guide
?   ??? DEVELOPER_GUIDE_PRESETS.md
?   ??? PARALLEL_TRANSMISSION_GUIDE.md
?   ??? COMPLETE_TEST_EXECUTION_REFERENCE.md
?   ??? ...
??? examples/                     # Example scripts
??? test/                         # Test suite
??? README.md                     # Project root README (v0.7.0)
??? .gitignore                    # Git ignore (updated v0.7.0)
??? LICENSE                       # MIT License

```

## What's New in v0.7.0

### Documentation
- [check] Created CHANGELOG_v0.7.0.md - Complete v0.7.0 release notes
- [check] Created VERSION_0.7.0_SUMMARY.md - Quick reference guide
- [check] Updated INDEX.md - Now highlights v0.7.0 as latest
- [check] Updated GETTING_STARTED.md - Certificate configuration added
- [check] Updated root README.md - New v0.7.0 section
- [check] Updated .gitignore - Certificate file patterns added

### Organization
- All documentation centralized in `doc/` folder
- Clear navigation through INDEX.md
- Version-specific changelog files maintained
- Quick summary guides for new users

---

## Finding What You Need

### I Want To...

**Get started quickly**
-> Read [GETTING_STARTED.md](GETTING_STARTED.md)

**Understand v0.7.0 changes**
-> See [VERSION_0.7.0_SUMMARY.md](VERSION_0.7.0_SUMMARY.md) or [CHANGELOG_v0.7.0.md](CHANGELOG_v0.7.0.md)

**Configure certificates**
-> See [GETTING_STARTED.md](GETTING_STARTED.md) "Certificate Configuration" section

**Build from source**
-> Follow [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

**Create distributions**
-> See [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md)

**Use server presets**
-> Check [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md)

**Run tests**
-> See [COMPLETE_TEST_EXECUTION_REFERENCE.md](COMPLETE_TEST_EXECUTION_REFERENCE.md)

**Navigate all docs**
-> Start at [INDEX.md](INDEX.md)

---

## Documentation Versions

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| 0.7.0 | March 2026 | SSL/TLS certificates, security improvements |
| 0.6.1 | Feb 2026 | LazyImport fixes |
| 0.6.0 | Jan 2025 | Validation system, UI improvements |
| 0.5.0 | | Parallel transmission |
| 0.4.0 | | Benchmarking |
| 0.3.1 | | Test features |
| 0.3.0 | | Server presets |

---

## Maintenance Notes

When adding new documentation:
1. Add entry to [INDEX.md](INDEX.md)
2. Use version in filename: `FEATURE_v0.7.0.md`
3. Include date and version header
4. Add link from appropriate section

When releasing new version:
1. Create `CHANGELOG_v{version}.md`
2. Create `VERSION_{version}_SUMMARY.md`
3. Update [INDEX.md](INDEX.md) with latest version
4. Update root `README.md` with new section

---

**Documentation Version**: 0.7.0  
**Last Updated**: March 2026

