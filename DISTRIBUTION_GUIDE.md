# ?? Distribution Guide

## What to Distribute

### ? CORRECT: Distribute the entire folder

```
dist\DICOM Creator\                    ? Package THIS entire folder (53.49 MB)
?
??? DICOM Creator.exe                 ? Users run this
??? _internal\                        ? MUST include (all Python libraries)
?   ??? pydicom\
?   ??? pynetdicom\
?   ??? PIL\
?   ??? numpy\
?   ??? tcl8\, tk8\
?   ??? api-ms-win-core-*.dll
?   ??? [~100+ other library files]
??? src\                              ? Application source
??? [other support files]
```

### ? WRONG: Don't distribute just the EXE

```
DICOM Creator.exe                      ? ALONE: Won't work!
                                          Missing libraries = Application crash
```

---

## Distribution Methods

### Method 1: ZIP Archive (Recommended)

**Steps:**
1. Right-click `dist\DICOM Creator\` folder
2. Select "Send to" ? "Compressed (zipped) folder"
3. Creates `DICOM Creator.zip` (~15-20 MB)

**Pros:**
- ? Smaller file size (compression)
- ? Easy to email or upload
- ? Users just extract and run
- ? Standard format

**Distribution:**
- Email as attachment
- Upload to cloud storage
- GitHub release download
- Website download

---

### Method 2: Direct Folder Copy

**Steps:**
1. Copy `dist\DICOM Creator\` folder
2. Share via USB drive, cloud storage, or network share

**Pros:**
- ? No compression overhead
- ? Works on slow internet
- ? Simple to understand
- ? Users can run immediately after copy

**Distribution:**
- USB drive
- Network share
- Cloud storage (Google Drive, OneDrive, Dropbox)

---

### Method 3: Professional Installer (Optional)

**Steps:**
1. Install NSIS (Nullsoft Scriptable Install System)
2. Create `.nsi` installer script
3. Build installer EXE

**Pros:**
- ? Professional appearance
- ? Uninstall support
- ? Start Menu shortcuts
- ? File associations
- ? Better user experience

**For enterprise deployment**

---

## Quick Distribution Checklist

Before sending to users:

- [ ] Confirm entire folder is included (53.49 MB)
- [ ] `_internal\` folder exists and has libraries
- [ ] `DICOM Creator.exe` is present
- [ ] `src\` folder is included
- [ ] Test on clean Windows machine
- [ ] Create compressed archive if emailing
- [ ] Document system requirements (Windows 7+, 64-bit)
- [ ] Include README or QUICK_START guide

---

## User Instructions Template

Share this with end users:

```
DICOM Creator - Installation & Running

1. Extract the DICOM Creator folder anywhere
2. Open the folder
3. Double-click DICOM Creator.exe
4. Application will start!

No installation needed. No Python required.

System Requirements:
- Windows 7 or newer (64-bit)
- ~100 MB disk space
- ~300 MB RAM

For help, see QUICK_START.md or README.md
```

---

## Folder Size Reference

| Component | Size |
|-----------|------|
| `DICOM Creator.exe` | 18.19 MB |
| `_internal\` (libraries) | ~35 MB |
| `src\` (source code) | ~1 MB |
| **Total** | **53.49 MB** |
| **Compressed (ZIP)** | **15-20 MB** |

---

## Distribution Scenarios

### Scenario 1: Email Distribution
```
1. Create: DICOM Creator.zip (~15-20 MB)
2. Send via email
3. User extracts zip file
4. User runs DICOM Creator.exe
5. Works perfectly!
```

### Scenario 2: GitHub Release
```
1. Create: DICOM Creator.zip
2. Upload as GitHub Release asset
3. Users download and extract
4. Users run DICOM Creator.exe
5. Works perfectly!
```

### Scenario 3: Website Download
```
1. Upload: DICOM Creator.zip to web server
2. Users download from website
3. Users extract zip file
4. Users run DICOM Creator.exe
5. Works perfectly!
```

### Scenario 4: USB Drive
```
1. Copy: dist\DICOM Creator\ folder to USB
2. Give USB to user
3. User copies folder to their computer
4. User runs DICOM Creator.exe
5. Works perfectly!
```

### Scenario 5: Network Share
```
1. Copy: dist\DICOM Creator\ folder to network share
2. Users access shared folder
3. Users copy folder locally (or run from share)
4. Users run DICOM Creator.exe
5. Works perfectly!
```

---

## What NOT to Do

### ? DON'T: Send only the EXE
**Result**: Won't work! Missing libraries.

### ? DON'T: Delete _internal\ folder
**Result**: Won't work! Missing libraries.

### ? DON'T: Modify files in _internal\ folder
**Result**: May crash or behave unexpectedly.

### ? DON'T: Distribute from build\ folder
**Result**: Incomplete and won't work.

### ? DON'T: Rename _internal\ folder
**Result**: Won't work! Application looks for this exact folder name.

---

## Common Issues & Solutions

### Issue: User says "File not found" or "Missing DLL"
**Cause**: They probably have just the EXE without the `_internal\` folder
**Solution**: Re-send the entire `dist\DICOM Creator\` folder

### Issue: User says "Slow to start"
**Cause**: Normal - first run unpacks files (~15-30 sec)
**Solution**: Subsequent runs are faster (5-10 sec)

### Issue: User says "Antivirus is blocking it"
**Cause**: Unsigned executables trigger warnings
**Solution**: 
- Option A: Sign the EXE (code signing certificate needed)
- Option B: User approves "Unknown Publisher" warning
- Option C: Add exception to antivirus

### Issue: User on Windows 7 says "Can't run"
**Cause**: May need Windows API updates
**Solution**: User updates Windows or uses Windows 10+

---

## Final Verification

After building, verify the distribution:

```cmd
cd dist\DICOM Creator

# Check EXE exists
dir DICOM*.exe

# Check _internal folder exists with many files
dir _internal | find /c /v ""    (should show 100+ items)

# Check src folder exists
dir src

# Try running
DICOM Creator.exe
```

---

## Ready to Distribute!

? Your `dist\DICOM Creator\` folder is ready for distribution.

Users can run it on any Windows 7+ (64-bit) computer without Python installed.

**Distribute the entire folder, not just the EXE!**
