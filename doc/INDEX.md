# Documentation Index

Welcome to DICOM Creator documentation! Find what you need below.

## ?? User Guides

### Getting Started
- **[QUICK_START_PRESETS.md](QUICK_START_PRESETS.md)** ? **START HERE**
  - Quick reference for Server Presets feature
  - 5-minute quick start guide
  - Common questions answered

- **[README.md](../README.md)**
  - Main project documentation
  - Installation instructions
  - Usage overview

### DICOM Inspection & Validation
- **[QUICK_START_TAG_VIEWER.md](QUICK_START_TAG_VIEWER.md)** ? **QUICK START**
  - 5-minute Tag Viewer guide
  - Common use cases
  - Pro tips and shortcuts

- **[TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md)**
  - Complete Tag Viewer documentation
  - View all DICOM tags including private tags
  - Search, filter, and export capabilities
  - Usage examples and troubleshooting

### Server Presets Feature
- **[SERVER_PRESETS.md](SERVER_PRESETS.md)**
  - Comprehensive Server Presets documentation
  - Detailed usage instructions
  - Configuration guide
  - Troubleshooting

### Build & Distribution
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)**
  - How to build the EXE yourself
  - Step-by-step build guide
  - Troubleshooting build issues

- **[DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md)**
  - Distribution instructions
  - Deployment guide

---

## ????? Developer Guides

- **[DEVELOPER_GUIDE_PRESETS.md](DEVELOPER_GUIDE_PRESETS.md)**
  - Architecture and design
  - API reference
  - Extension points
  - Testing guidance

---

## ?? Reference

- **[CHANGELOG_v0.4.0.md](CHANGELOG_v0.4.0.md)** ??
  - What's new in v0.4.0
  - Tag Viewer feature
  - VR Validator enhancements
  - Bug fixes and improvements

- **[CHANGELOG_v0.3.0.md](CHANGELOG_v0.3.0.md)**
  - What's new in v0.3.0
  - Server Presets feature
  - Known limitations
  - Future enhancements

---

## ??? Navigation Guide

### By Role

**I'm a User:**
1. Read [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md) (5 min)
2. Try using the feature
3. Refer to [SERVER_PRESETS.md](SERVER_PRESETS.md) for details

**I'm a System Administrator:**
1. Review [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md)
2. Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for deployment
3. See [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md) for release

**I'm a Developer:**
1. Read [DEVELOPER_GUIDE_PRESETS.md](DEVELOPER_GUIDE_PRESETS.md)
2. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
3. Examine source code in `src/`

**I'm Contributing:**
1. Read [DEVELOPER_GUIDE_PRESETS.md](DEVELOPER_GUIDE_PRESETS.md)
2. Check [CHANGELOG_v0.3.0.md](CHANGELOG_v0.3.0.md)
3. See development guidelines in code

---

## ?? Quick Reference

### Common Tasks

**How do I view all tags in a DICOM file?**
? See [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md) "How to Use"

**How do I export DICOM tags?**
? See [TAG_VIEWER_FEATURE.md](TAG_VIEWER_FEATURE.md) "Export to Text"

**How do I save a preset?**
? See [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md) "Save Your First Preset"

**How do I load a preset?**
? See [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md) "Load a Preset"

**Where are my presets stored?**
? See [QUICK_START_PRESETS.md](QUICK_START_PRESETS.md) "Where Are My Presets?"

**How do I build the EXE?**
? See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

**How do I extend the code?**
? See [DEVELOPER_GUIDE_PRESETS.md](DEVELOPER_GUIDE_PRESETS.md) "Extension Points"

---

## ?? File Organization

```
dcmcreator/
??? doc/
?   ??? INDEX.md (this file)
?   ??? User Guides:
?   ?   ??? QUICK_START_PRESETS.md
?   ?   ??? SERVER_PRESETS.md
?   ?   ??? BUILD_INSTRUCTIONS.md
?   ?   ??? DISTRIBUTION_GUIDE.md
?   ?   ??? CHANGELOG_v0.3.0.md
?   ??? Developer Guides:
?       ??? DEVELOPER_GUIDE_PRESETS.md
?       ??? IMPLEMENTATION_SUMMARY.md
??? src/
?   ??? app.py
?   ??? appgui.py
?   ??? dcm.py
?   ??? presets.py
?   ??? dcmlogger.py
??? README.md (main documentation)
??? LICENSE
??? ... other project files
```

---

## ?? Need Help?

1. **Check the documentation** - Most questions are answered in the guides
2. **Review examples** - See how features work
3. **Check error messages** - They usually tell you what's wrong
4. **Check the code** - Comments explain the implementation

---

## ?? Version Info

- **Current Version:** 0.4.0
- **Release Date:** 2025-2026
- **Status:** Production Ready
- **Latest Feature:** DICOM Tag Viewer

---

Last updated: January 2026

