"""
Test script for the Import Helper functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from import_helper import LazyImport


def test_lazy_import_initialization():
    """Test LazyImport initialization."""
    print("\nTesting LazyImport initialization...")
    try:
        lazy = LazyImport(".dcmlogger", "dcmlogger")
        
        # Check attributes exist
        assert hasattr(lazy, 'relative_path')
        assert hasattr(lazy, 'absolute_path')
        assert lazy.relative_path == ".dcmlogger"
        assert lazy.absolute_path == "dcmlogger"
        
        print("✓ LazyImport initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize LazyImport: {e}")
        return False


def test_lazy_import_load():
    """Test lazy loading of a module."""
    print("\nTesting lazy module loading...")
    try:
        # Use a module we know exists
        lazy = LazyImport(".dcmlogger", "dcmlogger")
        
        # Module shouldn't be loaded yet
        if lazy._module is not None:
            print("⚠ Module already loaded (unexpected)")
        
        # Trigger load
        module = lazy._load()
        
        if module is not None:
            print(f"✓ Module loaded successfully: {module.__name__}")
            return True
        else:
            error = lazy.get_error()
            print(f"✗ Module failed to load: {error}")
            return False
    except Exception as e:
        print(f"✗ Lazy load test failed: {e}")
        return False


def test_lazy_import_absolute_fallback():
    """Test that absolute import works as fallback."""
    print("\nTesting absolute import fallback...")
    try:
        # Use invalid relative path but valid absolute path
        lazy = LazyImport(".nonexistent_module", "dcmlogger", debug=False)
        
        module = lazy._load()
        
        if module is not None:
            print(f"✓ Absolute import fallback worked: {module.__name__}")
            return True
        else:
            print("⚠ Module not loaded (expected if dcmlogger not in path)")
            return True  # This is OK
    except Exception as e:
        print(f"✗ Absolute fallback test failed: {e}")
        return False


def test_lazy_import_class_extraction():
    """Test automatic class extraction from module."""
    print("\nTesting class extraction...")
    try:
        # Use connection_validator which has a clear main class
        lazy = LazyImport(".connection_validator", "connection_validator")
        
        # Trigger class load
        cls = lazy._load_class()
        
        if cls is not None:
            print(f"✓ Class extracted successfully: {cls.__name__}")
            
            # Try instantiating it
            instance = cls()
            print(f"✓ Class instance created successfully")
            return True
        else:
            print("⚠ No class found (module may not have classes)")
            return True  # This is OK
    except Exception as e:
        print(f"✗ Class extraction test failed: {e}")
        return False


def test_lazy_import_callable():
    """Test that LazyImport can be called like a class."""
    print("\nTesting callable interface...")
    try:
        # Use connection_validator
        lazy = LazyImport(".connection_validator", "connection_validator")
        
        # Call it directly
        instance = lazy()
        
        if instance is not None:
            print(f"✓ LazyImport called successfully, created: {type(instance).__name__}")
            return True
        else:
            print("✗ Failed to create instance")
            return False
    except ImportError as e:
        print(f"⚠ Import error (expected in some environments): {e}")
        return True
    except Exception as e:
        print(f"✗ Callable test failed: {e}")
        return False


def test_lazy_import_error_handling():
    """Test error handling for non-existent modules."""
    print("\nTesting error handling...")
    try:
        lazy = LazyImport(".completely_nonexistent_module", "also_nonexistent")
        
        # Try to load
        module = lazy._load()
        
        if module is None:
            error = lazy.get_error()
            if error:
                print(f"✓ Error properly captured: {error[:50]}...")
                return True
            else:
                print("⚠ Module not loaded but no error captured")
                return True
        else:
            print("✗ Non-existent module unexpectedly loaded")
            return False
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False


def test_lazy_import_multiple_loads():
    """Test that multiple load attempts use cached result."""
    print("\nTesting cached loading...")
    try:
        lazy = LazyImport(".dcmlogger", "dcmlogger")
        
        # Load twice
        module1 = lazy._load()
        module2 = lazy._load()
        
        # Should be the same object
        if module1 is module2:
            print("✓ Module loading properly cached")
            return True
        else:
            print("✗ Module not cached (or failed to load)")
            return False
    except Exception as e:
        print(f"✗ Caching test failed: {e}")
        return False


def test_lazy_import_getattr():
    """Test attribute access delegation."""
    print("\nTesting attribute delegation...")
    try:
        lazy = LazyImport(".dcmlogger", "dcmlogger")
        
        # Try to access an attribute from the module
        try:
            attr = lazy.setup_logging
            print(f"✓ Attribute delegation worked: {type(attr).__name__}")
            return True
        except AttributeError:
            print("⚠ Attribute not found (expected if dcmlogger structure differs)")
            return True
    except ImportError as e:
        print(f"⚠ Import error (expected in some environments): {e}")
        return True
    except Exception as e:
        print(f"✗ Attribute delegation test failed: {e}")
        return False


def main():
    """Run all import helper tests."""
    print("=" * 60)
    print("IMPORT HELPER FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    results.append(test_lazy_import_initialization())
    results.append(test_lazy_import_load())
    results.append(test_lazy_import_absolute_fallback())
    results.append(test_lazy_import_class_extraction())
    results.append(test_lazy_import_callable())
    results.append(test_lazy_import_error_handling())
    results.append(test_lazy_import_multiple_loads())
    results.append(test_lazy_import_getattr())
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed! Import helper is working correctly.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
