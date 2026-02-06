# Server Presets - Developer's Guide

## Overview

This guide is for developers who want to understand, extend, or modify the Server Presets feature.

## Architecture Overview

```
┌─────────────────────┐
│   appgui.py         │
│   (GUI Layer)       │
└──────────┬──────────┘
           │ Uses
           │
┌──────────▼──────────────────────────────────┐
│  presets.py                                 │
│  (ServerPresetsManager class)               │
│                                             │
│  Public Methods:                            │
│  • save_preset(name, config_dict)           │
│  • load_preset(name)                        │
│  • delete_preset(name)                      │
│  • list_presets()                           │
│  • has_presets()                            │
│                                             │
│  Private Methods:                           │
│  • _load_presets() - Read from file         │
│  • _save_presets() - Write to file          │
└──────────┬──────────────────────────────────┘
           │ Reads/Writes
           │
┌──────────▼──────────────────────────────────┐
│  ~/.dcmcreator/server_presets.json          │
│  (JSON Configuration File)                  │
└─────────────────────────────────────────────┘
```

## Class Reference

### ServerPresetsManager

**File:** `src/presets.py`

**Purpose:** Manage DICOM server configuration presets with JSON storage

**Initialization:**
```python
manager = ServerPresetsManager(config_dir=None)
# config_dir defaults to ~/.dcmcreator/
```

**Attributes:**
```python
manager.config_dir      # Config directory path
manager.presets_file    # Full path to presets JSON file
manager.presets         # Dict of loaded presets {name: config}
```

**Public Methods:**

#### `save_preset(name, config_dict)`
Saves a preset to the configuration.

**Parameters:**
- `name` (str): Preset name
- `config_dict` (dict): Configuration with keys: server, port, calling_ae, called_ae

**Returns:** bool (True if successful)

**Example:**
```python
manager.save_preset("MyServer", {
    'server': '192.168.1.1',
    'port': 4321,
    'calling_ae': 'DCMCREATOR',
    'called_ae': 'PACS01'
})
```

#### `load_preset(name)`
Retrieves a preset by name.

**Parameters:**
- `name` (str): Preset name

**Returns:** dict with configuration or None if not found

**Example:**
```python
preset = manager.load_preset("MyServer")
if preset:
    print(preset['server'])  # '192.168.1.1'
```

#### `delete_preset(name)`
Removes a preset from configuration.

**Parameters:**
- `name` (str): Preset name to delete

**Returns:** bool (True if successful)

**Example:**
```python
if manager.delete_preset("MyServer"):
    print("Preset deleted")
```

#### `list_presets()`
Gets all preset names.

**Returns:** list of preset names (sorted alphabetically)

**Example:**
```python
presets = manager.list_presets()
# ['Hospital PACS', 'Remote Clinic', 'Test Server']
```

#### `has_presets()`
Checks if any presets exist.

**Returns:** bool

**Example:**
```python
if manager.has_presets():
    print("Presets are available")
```

## GUI Integration

### DicomCreatorApp Class (appgui.py)

**Initialization:**
```python
class DicomCreatorApp(tk.Tk):
    def __init__(self):
        # ...
        if ServerPresetsManager:
            self.presets_manager = ServerPresetsManager()
        else:
            self.presets_manager = None
```

### Remote Variables (remote_vars)

```python
self.remote_vars = {
    "server": tk.StringVar(),
    "port": tk.StringVar(value="4321"),
    "calling_ae": tk.StringVar(value="DCMCREATOR"),
    "called_ae": tk.StringVar(value="AcuoMed1"),
    "preset_name": tk.StringVar(),  # Current preset name
}
```

### UI Components

**Preset Combobox:**
```python
self.preset_combo = ttk.Combobox(
    parent,
    textvariable=self.remote_vars["preset_name"],
    state="readonly"
)
self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)
```

**Buttons:**
```python
ttk.Button(parent, text="Load", command=self._load_preset)
ttk.Button(parent, text="Save Current", command=self._save_current_preset)
ttk.Button(parent, text="Delete", command=self._delete_preset)
```

## Event Flow

### Saving a Preset

```
User clicks "Save Current" button
    ?
_save_current_preset() called
    ?
Get preset name from preset_name field
    ?
Collect server config from remote_vars
    ?
Call manager.save_preset()
    ?
manager.save_preset() validates config
    ?
manager._save_presets() writes to JSON file
    ?
_refresh_presets_list() updates dropdown
    ?
User sees confirmation message
```

### Loading a Preset

```
User selects preset from dropdown
    ?
_on_preset_selected() triggered (auto-load)
    ?
Call manager.load_preset(selected_name)
    ?
Apply loaded config to remote_vars
    ?
Server fields automatically update in UI
```

### Deleting a Preset

```
User clicks "Delete" button
    ?
_delete_preset() called
    ?
Get selected preset name
    ?
Show confirmation dialog
    ?
If confirmed:
  Call manager.delete_preset()
  manager.delete_preset() writes to JSON
  _refresh_presets_list() updates dropdown
    ?
User sees success message
```

## Data Flow

### File I/O

**Reading Presets on Startup:**
```
ServerPresetsManager.__init__()
    ?
_load_presets()
    ?
Check if ~/.dcmcreator/server_presets.json exists
    ?
If exists: json.load(file)
If not: Create empty presets dict
    ?
presets dict loaded into memory
```

**Writing Presets:**
```
_save_presets()
    ?
Open ~/.dcmcreator/server_presets.json for writing
    ?
json.dump(presets, file) with indent=2
    ?
Close file
    ?
Return True/False based on success
```

## Extension Points

### Adding New Preset Fields

To add new fields to presets:

**1. Update ServerPresetsManager:**
```python
def save_preset(self, name, config_dict):
    self.presets[name] = {
        'server': str(config_dict.get('server', '')).strip(),
        'port': int(config_dict.get('port', 4321)),
        'calling_ae': str(config_dict.get('calling_ae', 'DCMCREATOR')).strip(),
        'called_ae': str(config_dict.get('called_ae', 'ANY-SCP')).strip(),
        'new_field': str(config_dict.get('new_field', '')).strip(),  # ADD HERE
    }
```

**2. Update UI in appgui.py:**
```python
def _build_remote_ui(self):
    self.remote_vars["new_field"] = tk.StringVar()
    self._add_labeled_entry(config_frame, "New Field", 
                           self.remote_vars["new_field"], 4)
```

**3. Update preset collection:**
```python
def _save_current_preset(self):
    preset = {
        'server': self.remote_vars["server"].get().strip(),
        'port': self.remote_vars["port"].get().strip(),
        'calling_ae': self.remote_vars["calling_ae"].get().strip(),
        'called_ae': self.remote_vars["called_ae"].get().strip(),
        'new_field': self.remote_vars["new_field"].get().strip(),  # ADD HERE
    }
```

### Adding Preset Encryption

**Example: Using cryptography library**

```python
from cryptography.fernet import Fernet

class ServerPresetsManager:
    def __init__(self, config_dir=None, password=None):
        # ...
        self.cipher = self._init_cipher(password) if password else None
    
    def _init_cipher(self, password):
        key = Fernet.generate_key()
        return Fernet(key)
    
    def _save_presets(self):
        data = json.dumps(self.presets)
        if self.cipher:
            data = self.cipher.encrypt(data.encode()).decode()
        with open(self.presets_file, 'w') as f:
            f.write(data)
```

### Adding Preset Categories

**Example: Organizing presets by category**

```python
# File structure:
{
  "categories": {
    "Hospital": {
      "Main PACS": {...},
      "Radiology": {...}
    },
    "Remote": {
      "Clinic A": {...}
    }
  }
}

# Manager method:
def get_presets_by_category(self, category):
    return self.presets.get('categories', {}).get(category, {})
```

### Adding UI Customization

**Example: Color coding by server type**

```python
def _on_preset_selected(self, event=None):
    name = self.preset_combo.get()
    preset = self.presets_manager.load_preset(name)
    
    if preset:
        # Color code based on preset type
        if 'clinic' in preset['server'].lower():
            bg_color = '#FFE0B2'  # Orange
        elif 'archive' in preset['server'].lower():
            bg_color = '#E0E0E0'  # Gray
        else:
            bg_color = '#C8E6C9'  # Green
        
        self.config_frame.configure(background=bg_color)
```

## Testing

### Unit Tests

**Testing save/load/delete:**
```python
import tempfile
import os

def test_save_preset():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ServerPresetsManager(config_dir=tmpdir)
        
        config = {
            'server': '192.168.1.1',
            'port': 4321,
            'calling_ae': 'TEST',
            'called_ae': 'TEST-SCP'
        }
        
        assert manager.save_preset("TestPreset", config)
        assert manager.get_preset("TestPreset") == config

def test_delete_preset():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ServerPresetsManager(config_dir=tmpdir)
        
        manager.save_preset("Test", {'server': '1.1.1.1', 'port': 4321})
        assert manager.delete_preset("Test")
        assert manager.get_preset("Test") is None
```

### Integration Tests

**Testing with GUI:**
```python
def test_preset_ui_integration():
    app = DicomCreatorApp()
    
    # Simulate save
    app.remote_vars["server"].set("192.168.1.1")
    app.remote_vars["port"].set("4321")
    app.remote_vars["preset_name"].set("TestUI")
    app._save_current_preset()
    
    # Verify preset saved
    assert app.presets_manager.get_preset("TestUI") is not None
    
    # Simulate load
    app._load_preset()
    assert app.remote_vars["server"].get() == "192.168.1.1"
```

## Performance Considerations

### Large Preset Files

For users with many presets (100+):

**Current Implementation:**
- All presets loaded into memory on startup
- Linear search on load/delete operations
- O(1) save operation

**Optimization for Future:**
```python
# Index-based lookup for faster operations
def _build_index(self):
    self.name_index = {name: i for i, name in enumerate(self.presets.keys())}

# Binary search for large lists
import bisect

def list_presets_binary_search(self, pattern):
    matching = [name for name in self.presets 
                if pattern.lower() in name.lower()]
    return sorted(matching)
```

### File I/O Optimization

**Current:** Write entire file on each save

**Future Optimization:**
```python
# Batch writes
def save_presets_batch(self, presets_list):
    for name, config in presets_list:
        self.presets[name] = config
    self._save_presets()  # Single write operation
```

## Debugging

### Logging

Enable debug logging:
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# In ServerPresetsManager methods:
logger.debug(f"Loading presets from {self.presets_file}")
logger.debug(f"Preset '{name}' saved successfully")
```

### Common Issues & Solutions

| Issue | Debug Step | Solution |
|-------|-----------|----------|
| Presets not loading | Check file exists | Verify file path |
| JSON decode error | Print raw file content | Validate JSON format |
| Permission denied | Check file permissions | Fix directory permissions |
| Duplicate presets | Check preset names | Trim whitespace |

## Best Practices

### For Developers

1. **Always validate input** before passing to manager
2. **Handle exceptions** gracefully
3. **Test file I/O** with temporary directories
4. **Keep presets.py independent** - minimal dependencies
5. **Document all changes** to JSON format
6. **Backward compatibility** - don't break old presets

### For Code Maintenance

1. Use type hints in Python 3.9+
2. Add docstrings to all public methods
3. Include error logging
4. Write unit tests for new features
5. Update documentation

### For UI Integration

1. Always call `_refresh_presets_list()` after changes
2. Show user feedback for all operations
3. Confirm destructive operations
4. Handle manager availability gracefully
5. Test with empty preset list

## Future Roadmap

### Phase 2: Enhanced Presets
- [ ] Preset encryption support
- [ ] Import/export functionality
- [ ] Preset categories/tags
- [ ] Preset usage history

### Phase 3: Advanced Features
- [ ] Cloud sync (Dropbox, OneDrive)
- [ ] Team preset sharing
- [ ] Server validation/testing
- [ ] Automatic backup

### Phase 4: Integration
- [ ] LDAP directory integration
- [ ] Multi-user support
- [ ] Audit logging
- [ ] REST API for presets

## Related Documentation

- `SERVER_PRESETS.md` - User documentation
- `QUICK_START_PRESETS.md` - Quick reference
- `PRESET_EXAMPLES.md` - Configuration examples
- `CHANGELOG_v0.3.0.md` - Release notes

## Support & Questions

For development questions:
1. Review this guide and class reference
2. Check existing code comments
3. Run test cases
4. Refer to related documentation

