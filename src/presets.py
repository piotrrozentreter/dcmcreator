"""
Server presets manager for saving and loading frequently used DICOM server configurations.
"""
import json
import os
from pathlib import Path


class ServerPresetsManager:
    """Manage server configuration presets stored in JSON format."""
    
    def __init__(self, config_dir=None):
        """Initialize the presets manager.
        
        Args:
            config_dir: Directory to store presets. Defaults to user's home directory.
        """
        if config_dir is None:
            config_dir = os.path.join(Path.home(), '.dcmcreator')
        
        self.config_dir = config_dir
        self.presets_file = os.path.join(config_dir, 'server_presets.json')
        self.presets = {}
        
        # Ensure config directory exists
        try:
            os.makedirs(config_dir, exist_ok=True)
        except Exception:
            pass
        
        # Load existing presets
        self._load_presets()
    
    def _load_presets(self):
        """Load presets from JSON file."""
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
            except Exception:
                self.presets = {}
        else:
            self.presets = {}
    
    def _save_presets(self):
        """Save presets to JSON file."""
        try:
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def save_preset(self, name, config_dict):
        """Save a server configuration preset.
        
        Args:
            name: Preset name (must be non-empty)
            config_dict: Dict with server, port, calling_ae, called_ae
            
        Returns:
            True if successful, False otherwise
        """
        if not name or not name.strip():
            return False
        
        name = name.strip()
        
        # Validate required fields
        if not config_dict or 'server' not in config_dict:
            return False
        
        try:
            # Handle both full config_dict and explicit parameters
            if isinstance(config_dict, dict):
                port = config_dict.get('port', '4321')
                try:
                    port = int(port)
                except (ValueError, TypeError):
                    return False
                
                self.presets[name] = {
                    'server': str(config_dict.get('server', '')).strip(),
                    'port': port,
                    'calling_ae': str(config_dict.get('calling_ae', 'DCMCREATOR')).strip(),
                    'called_ae': str(config_dict.get('called_ae', 'ANY-SCP')).strip(),
                }
            else:
                return False
        except Exception:
            return False
        
        return self._save_presets()
    
    def load_preset(self, name):
        """Get a preset by name.
        
        Returns:
            Dict with keys: server, port, calling_ae, called_ae. None if not found.
        """
        return self.presets.get(name)
    
    def get_preset(self, name):
        """Alias for load_preset for backward compatibility."""
        return self.load_preset(name)
    
    def delete_preset(self, name):
        """Delete a preset by name.
        
        Returns:
            True if successful, False otherwise
        """
        if name not in self.presets:
            return False
        
        del self.presets[name]
        return self._save_presets()
    
    def list_presets(self):
        """Get list of all preset names, sorted alphabetically.
        
        Returns:
            List of preset names
        """
        return sorted(self.presets.keys())
    
    def get_all_preset_names(self):
        """Get list of all preset names, sorted alphabetically.
        
        Returns:
            List of preset names
        """
        return self.list_presets()
    
    def has_presets(self):
        """Check if any presets exist."""
        return len(self.presets) > 0
