"""
Test script for the Tag Viewer functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tag_module():
    """Test the tag module."""
    print("Testing tag module...")
    try:
        from src.tag import get_all_tags_from_file, get_tag_statistics, format_tag_list
        print("? Tag module imported successfully")
        return True
    except Exception as e:
        print(f"? Failed to import tag module: {e}")
        return False

def test_tag_dialog_module():
    """Test the tag_dialog module."""
    print("\nTesting tag_dialog module...")
    try:
        from src.tag_dialog import TagViewerDialog, show_tag_viewer
        print("? Tag dialog module imported successfully")
        return True
    except Exception as e:
        print(f"? Failed to import tag_dialog module: {e}")
        return False

def test_appgui_integration():
    """Test that appgui has the new method."""
    print("\nTesting appgui integration...")
    try:
        from src.appgui import DicomCreatorApp
        
        # Check if show_tag_viewer method exists
        if hasattr(DicomCreatorApp, 'show_tag_viewer'):
            print("? show_tag_viewer method exists in DicomCreatorApp")
            return True
        else:
            print("? show_tag_viewer method not found in DicomCreatorApp")
            return False
    except Exception as e:
        print(f"? Failed to test appgui integration: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TAG VIEWER FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = []
    results.append(test_tag_module())
    results.append(test_tag_dialog_module())
    results.append(test_appgui_integration())
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n? All tests passed! The tag viewer is ready to use.")
        print("\nTo use the tag viewer:")
        print("  1. Run the application: python main.py")
        print("  2. Go to DICOM menu > View All Tags")
        print("  3. Select a DICOM file or load one first")
    else:
        print("\n? Some tests failed. Please check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
