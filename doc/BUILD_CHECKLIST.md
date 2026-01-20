# Build Checklist for v0.4.0+

## Pre-Build Verification

### 1. Source Files Check
- [ ] All core modules present in `src/`
  - [ ] `app.py` - Entry point
  - [ ] `appgui.py` - Main GUI
  - [ ] `app_logic.py` - Business logic
  - [ ] `dcm.py` - DICOM operations
  - [ ] `remote.py` - Remote transmission
  
### 2. New v0.4.0 Modules Check
- [ ] Validation modules present
  - [ ] `src/vr_validator.py` - VR validation engine
  - [ ] `src/validation_dialog.py` - Validation UI dialog
  - [ ] `src/tag.py` - Tag parsing utilities
  - [ ] `src/tag_dialog.py` - Tag viewer dialog
  - [ ] `src/VR.xml` - DICOM data dictionary (7MB+)

### 3. PyInstaller Configuration Check
- [ ] `dcmcreator.spec` exists
- [ ] Hidden imports include:
  - [ ] `vr_validator`
  - [ ] `validation_dialog`
  - [ ] `tag`
  - [ ] `tag_dialog`
- [ ] Data files include:
  - [ ] `('src', 'src')` - Source directory
  - [ ] `('src/VR.xml', 'src')` - DICOM dictionary

### 4. Dependencies Check
- [ ] `requirements.txt` up to date
- [ ] `build-requirements.txt` includes PyInstaller
- [ ] All packages installed:
  ```bash
  pip install -r requirements.txt
  pip install -r build-requirements.txt
  ```

## Build Process

### 5. Run Verification Script
```bash
python verify_build.py
```
- [ ] All checks pass
- [ ] No missing files reported
- [ ] VR.xml verified (7MB+, thousands of elements)

### 6. Execute Build
```bash
python build.py
```
or
```bash
build.bat
```

Expected output:
- [ ] Step 1: Python version check ?
- [ ] Step 2: Dependencies installed ?
- [ ] Step 3: Icon created ?
- [ ] Step 3.5: VR.xml verified ?
- [ ] Step 4: Previous builds cleaned ?
- [ ] Step 5: PyInstaller build completed ?
- [ ] Step 6: ZIP distribution created ?

## Post-Build Verification

### 7. Distribution Structure Check
- [ ] `dist/DICOM Creator/` folder exists
- [ ] `DICOM Creator.zip` file created
- [ ] ZIP size: 60-80 MB (compressed)
- [ ] Folder size: 150-200 MB (uncompressed)

### 8. Distribution Contents Check
```
dist/DICOM Creator/
??? DICOM Creator.exe       (~25 MB)
??? _internal/              (Python libraries)
?   ??? pydicom/
?   ??? pynetdicom/
?   ??? PIL/
?   ??? numpy/
?   ??? ...
??? src/                    (Application code)
    ??? VR.xml              (7 MB - CRITICAL!)
    ??? vr_validator.py
    ??? validation_dialog.py
    ??? tag.py
    ??? tag_dialog.py
    ??? ...
```

- [ ] `DICOM Creator.exe` present and ~25MB
- [ ] `_internal/` folder with all libraries
- [ ] `src/` folder with all source files
- [ ] **CRITICAL**: `src/VR.xml` present (7MB+)

### 9. Functional Testing
- [ ] Launch `DICOM Creator.exe`
- [ ] Test core features:
  - [ ] Load DICOM file
  - [ ] View patient/study/series data
  - [ ] Load image
  - [ ] Create new DICOM
  
- [ ] Test v0.4.0 features:
  - [ ] **DICOM** ? **View VRs** (opens VR viewer with data from VR.xml)
  - [ ] **DICOM** ? **View All Tags** (opens tag viewer)
  - [ ] **File** ? **Validate** (Ctrl+Shift+V) - validation dialog
  - [ ] Load DICOM and check automatic validation
  - [ ] Try to save with invalid data (should show validation)
  
- [ ] Check for errors:
  - [ ] No "VR.xml not found" errors
  - [ ] No "Module not found" errors
  - [ ] VR Validator loads successfully
  - [ ] Tag viewer displays DICOM tags

### 10. Error Scenarios to Test
- [ ] Load invalid DICOM data ? validation report shows
- [ ] Enter invalid values ? validation catches them
- [ ] Manual validate (Ctrl+Shift+V) ? dialog appears
- [ ] View VRs ? shows 4000+ DICOM data elements
- [ ] View Tags on empty file ? prompts to select file

## Distribution Checklist

### 11. Package for Distribution
- [ ] Choose distribution method:
  - [ ] **ZIP file**: `DICOM Creator.zip` (60-80 MB)
  - [ ] **Folder**: `dist/DICOM Creator/` (150-200 MB)

### 12. Test on Clean Windows Machine
- [ ] Copy ZIP/folder to test machine
- [ ] Extract (if ZIP)
- [ ] Run `DICOM Creator.exe`
- [ ] Verify all features work
- [ ] Check console for errors (run from cmd if issues)

### 13. Documentation Check
- [ ] README.md updated with v0.4.0 features
- [ ] CHANGELOG.md includes all changes
- [ ] BUILD_INSTRUCTIONS.md reflects new modules
- [ ] User documentation mentions:
  - [ ] VR validation
  - [ ] Tag viewer
  - [ ] Validation dialog

## Known Issues & Solutions

### Issue: VR.xml not found
**Solution**: Ensure VR.xml is:
1. Present in `src/VR.xml` (7MB+)
2. Listed in `dcmcreator.spec` datas section
3. Verified in Step 3.5 of build process

### Issue: Validation not working
**Symptoms**: 
- "VR Validator is not available" error
- LazyImport returns None for VRValidator

**Solution**: 
1. Check `vr_validator` in hiddenimports
2. Verify `ConnectionValidator` class name priority (not CEchoValidator)
3. Check copilot-instructions.md for LazyImport rules

### Issue: Tag Viewer crashes
**Solution**: 
1. Ensure `tag.py` and `tag_dialog.py` in hiddenimports
2. Verify pydicom is properly bundled
3. Test with various DICOM files

## Build Success Criteria

? Build is successful if:
1. [ ] No build errors during PyInstaller
2. [ ] ZIP file created successfully
3. [ ] `DICOM Creator.exe` launches without errors
4. [ ] VR Viewer shows 4000+ data elements
5. [ ] Tag Viewer displays DICOM tags
6. [ ] Validation works on form data
7. [ ] No missing file errors in logs
8. [ ] All core + v0.4.0 features functional

## Version Control

### 14. Git Commit
```bash
git add .
git commit -m "Build v0.4.0 with VR validation and tag viewer"
git tag v0.4.0
git push origin 0.4
git push --tags
```

### 15. GitHub Release
- [ ] Create release on GitHub
- [ ] Attach `DICOM Creator.zip`
- [ ] Include release notes:
  - New features
  - Bug fixes
  - Known issues
  - System requirements

## Support Information

**System Requirements**:
- Windows 7 or newer (64-bit)
- ~100 MB disk space (extracted)
- No Python required
- No external dependencies

**Distribution Size**:
- ZIP: 60-80 MB (download)
- Extracted: 150-200 MB (installed)

**Features Count** (v0.4.0):
- Core features: 6
- Validation features: 4
- Testing features: 5
- Total: 15 features

---

**Last Updated**: 2025-01-19 (v0.4.0)
**Next Review**: Before each major release
