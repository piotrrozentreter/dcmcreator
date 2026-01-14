# Server Presets Feature Documentation

## Overview

The **Server Presets** feature allows users to save, load, and manage frequently used DICOM server configurations. This eliminates the need to manually re-enter server details (IP/hostname, port, AE titles) for commonly used DICOM SCP (Service Class Provider) servers.

## Features

### Save Presets
- Save current server configuration with a custom name
- Presets are stored locally in JSON format
- Store unlimited number of presets

### Load Presets
- Quick-load previously saved server configurations
- Auto-select preset from dropdown
- One-click apply to all server fields

### Delete Presets
- Remove presets that are no longer needed
- Confirmation dialog to prevent accidental deletion

### Preset Storage
- Presets stored in: `~/.dcmcreator/server_presets.json`
- Cross-platform compatible (Windows, macOS, Linux)
- Automatically created on first use

## User Interface

### Remote Tab Layout

```
???????????????????????????????????????
?  Server Presets (LabelFrame)        ?
???????????????????????????????????????
?  Preset: [Dropdown v]               ?
?  [Load] [Save Current] [Delete]     ?
???????????????????????????????????????
?  Server Configuration (LabelFrame)  ?
???????????????????????????????????????
?  Server (IP/Name): [_________]      ?
?  Port: [_________]                  ?
?  Calling AE Title: [_________]      ?
?  Called AE Title: [_________]       ?
???????????????????????????????????????
?  [Send All Loaded DICOM]            ?
?                                     ?
?  Messages / Errors:                 ?
?  ????????????????????????????????????
?  ?                                 ??
?  ?                                 ??
?  ????????????????????????????????????
???????????????????????????????????????
```

## Usage Guide

### Saving a Preset

1. Enter server configuration in the "Server Configuration" section:
   - Server (IP or hostname)
   - Port number
   - Calling AE Title
   - Called AE Title

2. Enter a preset name in the "Preset:" field

3. Click "Save Current" button

4. Confirmation message will appear

5. Preset is now available in the dropdown for future use

**Example:**
```
Preset: MyHospitalPACS
Server: 192.168.1.100
Port: 4321
Calling AE Title: DCMCREATOR
Called AE Title: PACS01
```

### Loading a Preset

**Method 1: Using Dropdown**
1. Click the "Preset:" dropdown
2. Select a preset name
3. Configuration automatically loads
4. Click "Load" to confirm (optional)

**Method 2: Using Load Button**
1. Select preset from dropdown
2. Click "Load" button
3. Confirmation message appears

### Deleting a Preset

1. Select preset from dropdown
2. Click "Delete" button
3. Confirmation dialog appears
4. Click "Yes" to confirm deletion
5. Preset is removed from dropdown

## Preset Configuration Format

Presets are stored in JSON format in `~/.dcmcreator/server_presets.json`:

```json
{
  "MyHospitalPACS": {
    "server": "192.168.1.100",
    "port": 4321,
    "calling_ae": "DCMCREATOR",
    "called_ae": "PACS01"
  },
  "RemoteClinic": {
    "server": "clinic.example.com",
    "port": 11112,
    "calling_ae": "DCMCREATOR",
    "called_ae": "REMOTE-PACS"
  }
}
```

## Technical Details

### Module: `src/presets.py`

**Class: `ServerPresetsManager`**

Methods:
- `save_preset(name, config_dict)` - Save a preset
- `load_preset(name)` - Load a preset
- `delete_preset(name)` - Delete a preset
- `list_presets()` - Get all preset names
- `has_presets()` - Check if presets exist

### Integration Points

**In `appgui.py`:**

1. **Initialization:** 
   - `self.presets_manager = ServerPresetsManager()` in `__init__`

2. **UI Methods:**
   - `_build_remote_ui()` - Builds the preset UI components
   - `_on_preset_selected()` - Auto-loads preset when selected
   - `_load_preset()` - Manual preset loading
   - `_save_current_preset()` - Saves current configuration as preset
   - `_delete_preset()` - Deletes selected preset
   - `_refresh_presets_list()` - Refreshes dropdown list

3. **Remote Variables:**
   - `remote_vars["preset_name"]` - Current preset name

## Validation

### Server Configuration Validation

- **Server:** Required, non-empty string
- **Port:** Required, valid integer (1-65535)
- **Calling AE:** Optional, defaults to "DCMCREATOR"
- **Called AE:** Optional, defaults to "ANY-SCP"

### Preset Name Validation

- Required, non-empty string
- Trimmed of whitespace
- Unique (overwrites if duplicate)

## Error Handling

The feature includes comprehensive error handling:

- Missing presets manager ? Graceful degradation
- Invalid preset data ? User notification
- File I/O errors ? Logged and reported
- Empty preset list ? Empty dropdown

## User Messages

### Success Messages
- "Preset '**name**' saved successfully"
- "Preset '**name**' loaded successfully"
- "Preset '**name**' deleted successfully"

### Error Messages
- "No preset selected"
- "Preset name must be provided"
- "Preset '**name**' not found"
- "Failed to save preset '**name**'"
- "Failed to load preset '**name**'"
- "Failed to delete preset '**name**'"

### Remote Messages (in Messages area)
- "Saved preset: **name**"
- "Loaded preset: **name**"
- "Deleted preset: **name**"

## File Storage

**Location:** `~/.dcmcreator/server_presets.json`

**Permissions:** User read/write

**Backup:** Not automatically backed up (users should manually backup if needed)

## Limitations & Future Enhancements

### Current Limitations
- No encryption of stored presets
- No import/export functionality
- No default presets provided

### Potential Enhancements
- Encryption of stored credentials
- Import/export presets to CSV or JSON
- Preset organization with categories/groups
- Preset favorites/pinning
- Automatic backup to cloud storage
- Preset usage statistics

## Testing Checklist

- [ ] Save a preset with valid configuration
- [ ] Load a saved preset
- [ ] Delete a preset with confirmation
- [ ] Verify preset is stored in JSON file
- [ ] Load preset from dropdown selection
- [ ] Handle invalid port number
- [ ] Handle missing required fields
- [ ] Verify presets persist across app restarts
- [ ] Test with multiple presets
- [ ] Test preset name with special characters

## Troubleshooting

### Presets Not Appearing in Dropdown
**Solution:** Restart the application. Presets are loaded on startup.

### Presets Lost After Restart
**Solution:** Check file permissions on `~/.dcmcreator/` directory. Ensure write access.

### "Presets manager not available" Error
**Solution:** Ensure `presets.py` is in the `src/` directory and can be imported.

### Corrupted Preset File
**Solution:** Delete `~/.dcmcreator/server_presets.json` and recreate presets. File is JSON format and can be manually edited if needed.

## API Reference

### ServerPresetsManager

```python
from presets import ServerPresetsManager

# Initialize
manager = ServerPresetsManager()

# Save
success = manager.save_preset(
    name="MyServer",
    config_dict={
        'server': '192.168.1.1',
        'port': 4321,
        'calling_ae': 'DCMCREATOR',
        'called_ae': 'PACS'
    }
)

# Load
preset = manager.load_preset('MyServer')
print(preset)  # {'server': '192.168.1.1', 'port': 4321, ...}

# List
presets = manager.list_presets()
print(presets)  # ['MyServer', 'OtherServer', ...]

# Delete
success = manager.delete_preset('MyServer')

# Check
if manager.has_presets():
    print("Presets available")
```

## Version History

**v0.3.0** - Initial Implementation
- Save/load/delete server presets
- JSON-based storage
- Preset dropdown with auto-load
- Confirmation dialogs

