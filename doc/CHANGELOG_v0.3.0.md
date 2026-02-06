# Server Presets Feature - Release Notes

## Version 0.3.0 - Server Presets Implementation

### New Feature: Server Presets

Save and manage frequently used DICOM server configurations with the new **Server Presets** feature.

#### What's New

- **Save Presets:** Store server configurations (IP/hostname, port, AE titles) with a custom name
- **Load Presets:** Quickly load saved configurations with a single click
- **Manage Presets:** Delete presets you no longer need
- **Auto-Load:** Presets auto-apply when selected from the dropdown
- **Persistent Storage:** Presets are stored locally in JSON format and persist across app restarts

#### User Interface Changes

**Remote Tab Enhancements:**
- New "Server Presets" section at the top with:
  - Preset dropdown (shows all saved presets)
  - **Load** button - Manual load selected preset
  - **Save Current** button - Save current server configuration as preset
  - **Delete** button - Remove selected preset
- Reorganized "Server Configuration" section below presets for clearer workflow

#### New Files

- `src/presets.py` - ServerPresetsManager class for preset management
- `SERVER_PRESETS.md` - Comprehensive documentation
- `QUICK_START_PRESETS.md` - Quick reference guide

#### How to Use

1. **Save a Preset:**
   - Fill in server details (Server, Port, Calling AE, Called AE)
   - Enter preset name
   - Click "Save Current"

2. **Load a Preset:**
   - Click dropdown and select preset
   - (Optional) Click "Load" button
   - Configuration auto-applies

3. **Delete a Preset:**
   - Select preset from dropdown
   - Click "Delete"
   - Confirm deletion

#### Storage Location

Presets are stored in:
- **Windows:** `C:\Users\[Username]\.dcmcreator\server_presets.json`
- **macOS:** `/Users/[Username]/.dcmcreator/server_presets.json`
- **Linux:** `/home/[Username]/.dcmcreator/server_presets.json`

#### Technical Implementation

**New Class: ServerPresetsManager**

Located in `src/presets.py`:

```python
manager = ServerPresetsManager()
manager.save_preset(name, config_dict)      # Save preset
manager.load_preset(name)                   # Load preset
manager.delete_preset(name)                 # Delete preset
manager.list_presets()                      # Get all preset names
manager.has_presets()                       # Check if any presets exist
```

**Integration in appgui.py:**

- `_build_remote_ui()` - Enhanced with preset UI components
- `_on_preset_selected()` - Auto-loads preset on selection
- `_load_preset()` - Manual preset loading
- `_save_current_preset()` - Saves current configuration
- `_delete_preset()` - Deletes selected preset
- `_refresh_presets_list()` - Refreshes dropdown

#### Validation

- Server: Required, non-empty
- Port: Required, valid integer
- Calling AE: Optional, defaults to "DCMCREATOR"
- Called AE: Optional, defaults to "ANY-SCP"
- Preset Name: Required, unique

#### Error Handling

- Graceful degradation if presets manager unavailable
- User-friendly error messages for all operations
- Confirmation dialogs for destructive operations (delete)
- Validation of preset names and server configuration

#### Features by Use Case

**For System Administrators:**
- Create presets for each department's DICOM server
- Share preset names (but not credentials) with staff
- Reduce configuration errors through standardization

**For Clinical Staff:**
- Quick access to commonly used servers
- No need to remember server addresses and ports
- Less prone to typos and configuration errors

**For Research Teams:**
- Save presets for different research study servers
- Quickly switch between multiple DICOM servers
- Maintain different AE titles for different studies

#### Future Enhancements (Potential)

-  Credential encryption for saved presets
-  Import/Export presets to CSV/JSON
-  Organize presets with categories/tags
-  Preset favorites/pinning
-  Preset usage statistics and history
-  Cloud backup integration
-  Sync presets across multiple devices
-  Server connection testing/validation

#### Testing Notes

Feature tested with:
-  Create multiple presets
-  Load presets from dropdown
-  Manual load button
-  Delete presets with confirmation
-  Preset persistence across restarts
-  Empty preset list handling
-  Invalid configuration validation
-  File I/O error handling

#### Migration Notes

**For Users Upgrading from v0.2.x:**

- No action required
- Existing server settings are NOT automatically converted to presets
- You can manually create presets from your commonly used configurations
- No breaking changes to existing functionality

#### Documentation

See:
- `SERVER_PRESETS.md` - Full feature documentation
- `QUICK_START_PRESETS.md` - Quick reference guide
- `README.md` - Updated with presets feature

#### Known Limitations

- Presets are stored in plain text JSON (not encrypted)
- No built-in preset import/export (manual JSON editing possible)
- No preset categories or groups (future enhancement)
- No cloud sync (future enhancement)

#### Troubleshooting

**Presets not appearing:**
- Restart application
- Check file permissions on `~/.dcmcreator/` directory

**"Presets manager not available" error:**
- Ensure `presets.py` exists in `src/` directory
- Check Python import paths

**Corrupted preset file:**
- Delete `server_presets.json` and recreate presets
- File can be manually edited (JSON format)

---

### Issue Fixes in v0.3.0

- Fixed user-loaded image disappearing when selecting DICOM instance (image_source tracking)
- Improved remote UI layout and organization
- Enhanced error messages and user feedback

### Version Compatibility

- **Python:** 3.9+
- **Windows:** 7 or newer (64-bit)
- **macOS:** 10.14 or newer
- **Linux:** Ubuntu 18.04 or newer

### Credits

Feature developed as part of ongoing DICOM Creator enhancements for Hyland.

---

**Total Changes in v0.3.0:**
- 1 new file: `src/presets.py`
- 2 documentation files: `SERVER_PRESETS.md`, `QUICK_START_PRESETS.md`
- Modified: `src/appgui.py` (preset UI and methods)
- Lines added: ~400 lines of code + documentation

