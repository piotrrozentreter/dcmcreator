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
    
    def _validate_preset_name(self, name):
        """Validate preset name.
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not name:
            return False, "Preset name cannot be empty"
        
        name = str(name).strip()
        
        if not name:
            return False, "Preset name cannot be empty or whitespace only"
        
        if len(name) > 100:
            return False, "Preset name is too long (max 100 characters)"
        
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in name:
                return False, f"Preset name cannot contain: {char}"
        
        return True, ""
    
    def _validate_server_config(self, config_dict):
        """Validate server configuration.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not config_dict or not isinstance(config_dict, dict):
            return False, "Configuration must be a dictionary"
        
        # Check required fields
        if 'server' not in config_dict or not config_dict['server']:
            return False, "Server address is required"
        
        server = str(config_dict['server']).strip()
        if not server:
            return False, "Server address cannot be empty"
        
        # Validate port
        try:
            port = int(config_dict.get('port', 4321))
            if port < 1 or port > 65535:
                return False, "Port must be between 1 and 65535"
        except (ValueError, TypeError):
            return False, "Port must be a valid number"
        
        return True, ""
    
    def create_preset(self, name, server, port, calling_ae=None, called_ae=None, use_tls=False, tls_config=None):
        """Create and save a new preset with full validation.
        
        Args:
            name: Preset name
            server: Server IP or hostname
            port: Server port (int or str)
            calling_ae: Calling AE title (optional, defaults to DCMCREATOR)
            called_ae: Called AE title (optional, defaults to ANY-SCP)
            use_tls: Whether to use TLS/SSL (optional, defaults to False)
            tls_config: TLS configuration dictionary (optional)
            
        Returns:
            Tuple: (success, message)
        """
        # Validate name
        valid, error = self._validate_preset_name(name)
        if not valid:
            return False, error
        
        name = name.strip()
        
        # Check if preset already exists
        if name in self.presets:
            return False, f"Preset '{name}' already exists. Use update_preset to modify it."
        
        # Validate server config
        config_dict = {
            'server': server,
            'port': port,
            'calling_ae': calling_ae or 'DCMCREATOR',
            'called_ae': called_ae or 'ANY-SCP',
            'use_tls': use_tls,
            'tls_config': tls_config
        }
        
        valid, error = self._validate_server_config(config_dict)
        if not valid:
            return False, error
        
        # Try to save
        try:
            port = int(port)
            self.presets[name] = {
                'server': str(server).strip(),
                'port': port,
                'calling_ae': str(calling_ae or 'DCMCREATOR').strip(),
                'called_ae': str(called_ae or 'ANY-SCP').strip(),
                'use_tls': use_tls,
                'tls_config': tls_config
            }
            
            if self._save_presets():
                return True, f"Preset '{name}' created successfully"
            else:
                del self.presets[name]  # Rollback on save failure
                return False, "Failed to save preset to file"
        except Exception as e:
            return False, f"Error creating preset: {str(e)}"
    
    def update_preset(self, name, server=None, port=None, calling_ae=None, called_ae=None, use_tls=None, tls_config=None):
        """Update an existing preset.
        
        Args:
            name: Preset name to update
            server: New server (optional)
            port: New port (optional)
            calling_ae: New calling AE (optional)
            called_ae: New called AE (optional)
            use_tls: Whether to use TLS/SSL (optional)
            tls_config: TLS configuration dictionary (optional)
            
        Returns:
            Tuple: (success, message)
        """
        if name not in self.presets:
            return False, f"Preset '{name}' not found"
        
        # Get current values
        current = self.presets[name]
        
        # Use provided values or keep current
        new_config = {
            'server': server if server else current['server'],
            'port': port if port is not None else current['port'],
            'calling_ae': calling_ae if calling_ae else current['calling_ae'],
            'called_ae': called_ae if called_ae else current['called_ae'],
            'use_tls': use_tls if use_tls is not None else current.get('use_tls', False),
            'tls_config': tls_config if tls_config is not None else current.get('tls_config')
        }
        
        # Validate
        valid, error = self._validate_server_config(new_config)
        if not valid:
            return False, error
        
        try:
            port_int = int(new_config['port'])
            self.presets[name] = {
                'server': str(new_config['server']).strip(),
                'port': port_int,
                'calling_ae': str(new_config['calling_ae']).strip(),
                'called_ae': str(new_config['called_ae']).strip(),
                'use_tls': new_config['use_tls'],
                'tls_config': new_config['tls_config']
            }
            
            if self._save_presets():
                return True, f"Preset '{name}' updated successfully"
            else:
                self.presets[name] = current  # Rollback
                return False, "Failed to save preset to file"
        except Exception as e:
            return False, f"Error updating preset: {str(e)}"
    
    def save_preset(self, name, config_dict):
        """Save a server configuration preset (legacy method).
        
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
            Tuple: (success, message)
        """
        if name not in self.presets:
            return False, f"Preset '{name}' not found"
        
        try:
            del self.presets[name]
            if self._save_presets():
                return True, f"Preset '{name}' deleted successfully"
            else:
                # Rollback on save failure
                self._load_presets()
                return False, "Failed to save changes to file"
        except Exception as e:
            return False, f"Error deleting preset: {str(e)}"
    
    def rename_preset(self, old_name, new_name):
        """Rename a preset.
        
        Args:
            old_name: Current preset name
            new_name: New preset name
            
        Returns:
            Tuple: (success, message)
        """
        # Validate new name
        valid, error = self._validate_preset_name(new_name)
        if not valid:
            return False, error
        
        new_name = new_name.strip()
        
        if old_name not in self.presets:
            return False, f"Preset '{old_name}' not found"
        
        if new_name in self.presets:
            return False, f"Preset '{new_name}' already exists"
        
        try:
            self.presets[new_name] = self.presets.pop(old_name)
            if self._save_presets():
                return True, f"Preset renamed from '{old_name}' to '{new_name}'"
            else:
                # Rollback
                self._load_presets()
                return False, "Failed to save changes to file"
        except Exception as e:
            return False, f"Error renaming preset: {str(e)}"
    
    def duplicate_preset(self, source_name, new_name):
        """Create a copy of an existing preset with a new name.
        
        Args:
            source_name: Name of preset to copy
            new_name: Name for the new preset
            
        Returns:
            Tuple: (success, message)
        """
        if source_name not in self.presets:
            return False, f"Preset '{source_name}' not found"
        
        config = self.presets[source_name].copy()
        return self.create_preset(
            new_name,
            config['server'],
            config['port'],
            config['calling_ae'],
            config['called_ae']
        )
    
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
    
    def get_all_presets(self):
        """Get all presets with their full configuration.
        
        Returns:
            Dict mapping preset name -> configuration dict
        """
        return {name: config.copy() for name, config in self.presets.items()}
    
    def has_presets(self):
        """Check if any presets exist."""
        return len(self.presets) > 0
    
    def preset_exists(self, name):
        """Check if a specific preset exists.
        
        Args:
            name: Preset name
            
        Returns:
            Boolean
        """
        return name in self.presets
    
    def get_preset_count(self):
        """Get total number of presets.
        
        Returns:
            Integer count
        """
        return len(self.presets)
