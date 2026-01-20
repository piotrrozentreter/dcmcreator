"""Centralized import management for handling optional and flexible imports."""

from importlib import import_module
import sys
import os
import inspect

# Add src directory to path for absolute imports to work
_src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


class LazyImport:
    """Lazy import wrapper to defer imports until first access.
    
    This solves the "package argument required" error by deferring imports
    until they're actually used, at which point the proper context exists.
    
    Automatically extracts the main class from modules.
    
    Usage:
        ServerPresets = LazyImport(".presets", "presets")
        # Later, when you actually need it:
        manager = ServerPresets()  # Automatically gets ServerPresetsManager class
        # Or explicitly:
        presets_cls = ServerPresets._load_class()
    """
    
    def __init__(self, relative_path: str, absolute_path: str, debug=False):
        """Initialize lazy import wrapper.
        
        Args:
            relative_path: Module path for relative import (e.g., ".app_logic")
            absolute_path: Module path for absolute import (e.g., "app_logic")
            debug: Print debug info if True
        """
        self.relative_path = relative_path
        self.absolute_path = absolute_path
        self.debug = debug
        self._module = None
        self._class = None
        self._load_attempted = False
        self._class_load_attempted = False
        self._error = None
    
    def _load(self):
        """Load the module if not already loaded."""
        if self._load_attempted:
            return self._module
        
        self._load_attempted = True
        
        # Try relative import first
        try:
            self._module = import_module(self.relative_path)
            if self.debug:
                print(f"[IMPORT] ✓ Successfully imported: {self.relative_path}")
            return self._module
        except (ImportError, ModuleNotFoundError) as e:
            self._error = str(e)
            if self.debug:
                print(f"[IMPORT] ✗ Relative import failed: {self.relative_path}")
                print(f"         Error: {e}")
        except TypeError as e:
            self._error = str(e)
            if self.debug:
                print(f"[IMPORT] ✗ Relative import not available: {self.relative_path}")
                print(f"         Error: {e}")
        except Exception as e:
            self._error = str(e)
            if self.debug:
                print(f"[IMPORT] ✗ Unexpected error: {type(e).__name__}: {e}")
        
        # Try absolute import
        try:
            self._module = import_module(self.absolute_path)
            if self.debug:
                print(f"[IMPORT] ✓ Successfully imported: {self.absolute_path}")
            return self._module
        except (ImportError, ModuleNotFoundError) as e:
            self._error = str(e)
            if self.debug:
                print(f"[IMPORT] ✗ Absolute import failed: {self.absolute_path}")
                print(f"         Error: {e}")
        except Exception as e:
            self._error = str(e)
            if self.debug:
                print(f"[IMPORT] ✗ Unexpected error: {type(e).__name__}: {e}")
        
        if self.debug:
            print(f"[IMPORT] ✗ FAILED: Could not import {self.relative_path} or {self.absolute_path}")
            if self._error:
                print(f"         Last error: {self._error}")
        return None
    
    def _load_class(self):
        """Load and extract the main class from the module."""
        if self._class_load_attempted:
            return self._class

        self._class_load_attempted = True
        module = self._load()

        if module is None:
            return None

        # Try to find the main class in the module
        # Look for classes defined in this module (not imported from elsewhere)
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                # Skip private/internal classes
                if not name.startswith('_'):
                    classes.append((name, obj))

        if not classes:
            if self.debug:
                print(f"[IMPORT] ✗ No classes found in module: {module.__name__}")
            return None

        # If there's only one class, use it
        if len(classes) == 1:
            self._class = classes[0][1]
            if self.debug:
                print(f"[IMPORT] ✓ Extracted class: {classes[0][0]}")
            return self._class

        # If multiple classes, prefer the one with most public methods
        # This helps when there's a main class and helper classes
        class_scores = []
        for class_name, class_obj in classes:
            # Count public methods (don't count dunder methods)
            public_methods = len([m for m in dir(class_obj) 
                                 if not m.startswith('_') and callable(getattr(class_obj, m))])
            class_scores.append((public_methods, class_name, class_obj))
        
        # Sort by public method count (descending) and take the one with most methods
        class_scores.sort(reverse=True, key=lambda x: x[0])
        self._class = class_scores[0][2]
        
        if self.debug:
            print(f"[IMPORT] ✓ Extracted class (most methods): {class_scores[0][1]} ({class_scores[0][0]} methods)")
        
        return self._class
    
    def get_error(self):
        """Get the last import error message."""
        if not self._load_attempted:
            self._load()
        return self._error
    
    def __call__(self, *args, **kwargs):
        """Allow calling as a class/function - automatically extracts the class."""
        cls = self._load_class()
        if cls is None:
            raise ImportError(f"Module or class not available: {self.relative_path} or {self.absolute_path}\nError: {self._error}")
        return cls(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate attribute access to the loaded module or class."""
        # Try to get from class first
        cls = self._load_class()
        if cls is not None:
            try:
                return getattr(cls, name)
            except AttributeError:
                pass
        
        # Fall back to module
        module = self._load()
        if module is None:
            raise ImportError(f"Module not available: {self.relative_path} or {self.absolute_path}\nError: {self._error}")
        return getattr(module, name)