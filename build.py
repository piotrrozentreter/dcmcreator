#!/usr/bin/env python
"""
Build script for DICOM Creator
Installs dependencies, creates icon, builds the executable, and creates a ZIP distribution
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"\n{description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed")
        return False

def get_folder_size(path):
    """Calculate total size of a folder in MB."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except Exception:
        pass
    return total / (1024 * 1024)

def create_zip_distribution(source_folder, output_zip):
    """Create a ZIP file from the distribution folder."""
    print(f"\nCreating ZIP distribution: {output_zip}")
    print("This may take a minute...")
    
    try:
        # Create ZIP file with compression
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(source_folder))
                    zipf.write(file_path, arcname)
        
        # Get file size
        zip_size = os.path.getsize(output_zip) / (1024 * 1024)
        print(f" ZIP created successfully: {zip_size:.1f} MB")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create ZIP: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("DICOM Creator - Build & Package Script")
    print("="*50)
    
    # Step 1: Check Python
    print("\nStep 1: Checking Python installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f" {result.stdout.strip()}")
    except Exception as e:
        print(f"ERROR: Python not found: {e}")
        return False
    
    # Step 2: Install dependencies
    print("\nStep 2: Installing build dependencies...")
    if not run_command(
        f"{sys.executable} -m pip install -r build-requirements.txt",
        "Installing PyInstaller and Pillow..."
    ):
        print("WARNING: Could not install all dependencies, continuing anyway...")
    else:
        print(" Dependencies installed")
    
    # Step 3: Create icon
    print("\nStep 3: Creating application icon...")
    if not run_command(f"{sys.executable} create_icon.py", "Generating icon..."):
        print("WARNING: Icon creation failed, continuing without custom icon")
    else:
        print(" Icon created successfully")
    
    # Step 3.5: Verify VR.xml exists
    print("\nStep 3.5: Verifying DICOM data dictionary...")
    vr_xml_path = Path("src/VR.xml")
    if not vr_xml_path.exists():
        print(f"ERROR: VR.xml not found at {vr_xml_path}")
        print("The VR validator and tag viewer require this file.")
        print("Please ensure VR.xml is present in the src/ directory.")
        return False
    else:
        vr_size = vr_xml_path.stat().st_size / (1024 * 1024)
        print(f" VR.xml found ({vr_size:.1f} MB)")
    
    # Step 4: Clean previous builds
    print("\nStep 4: Cleaning previous builds...")
    for folder in ['build', 'dist', '__pycache__', '.pytest_cache']:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f" Removed {folder}")
            except Exception as e:
                print(f"Warning: Could not remove {folder}: {e}")
    
    # Step 5: Build executable
    print("\nStep 5: Building executable...")
    print("This may take a few minutes...\n")
    if not run_command(
        f"{sys.executable} -m PyInstaller dcmcreator.spec",
        "Running PyInstaller..."
    ):
        print("\nERROR: Build failed!")
        return False
    
    # Step 6: Create ZIP distribution
    print("\nStep 6: Creating ZIP distribution package...")
    dist_path = Path("dist/DICOM Creator")
    zip_path = Path("DICOM Creator.zip")
    
    if dist_path.exists():
        if create_zip_distribution(str(dist_path), str(zip_path)):
            folder_size = get_folder_size(str(dist_path))
            zip_size = zip_path.stat().st_size / (1024 * 1024)
            
            print(f"\n ZIP distribution created successfully!")
            print(f"  Folder size: {folder_size:.1f} MB")
            print(f"  ZIP size: {zip_size:.1f} MB")
            print(f"  Compression: {((1 - zip_size/folder_size) * 100):.1f}%")
        else:
            print("WARNING: ZIP creation failed, but executable was built successfully")
    else:
        print("ERROR: Distribution folder not found!")
        return False
    
    # Success message
    print("\n" + "="*50)
    print("Build completed successfully!")
    print("="*50)
    print("\n Your application is ready for distribution:")
    print("\nFeatures included in this build:")
    print("   DICOM creation and editing")
    print("   VR validation with PS3.6 data dictionary")
    print("   Tag viewer for all DICOM tags")
    print("   Validation dialog with detailed reports")
    print("   Remote DICOM transmission (C-STORE)")
    print("   Connection testing and stress testing")
    print("   Transmission history tracking")
    print("   Performance benchmarking")
    print("   Parallel transmission support")
    print("\nOptions:")
    print("  1. Share the ZIP file:")
    print(f"      DICOM Creator.zip (~{zip_size:.0f} MB)")
    print("      Users extract and run DICOM Creator.exe")
    print("      Best for email, GitHub, websites")
    print("\n  2. Share the folder directly:")
    print(f"      dist\\DICOM Creator\\ folder (~{folder_size:.0f} MB)")
    print("      Users run DICOM Creator.exe")
    print("      Best for USB drives, network shares")
    print("\nSystem Requirements:")
    print("  - Windows 7 or newer (64-bit)")
    print("  - ~100 MB disk space")
    print("  - No Python required!")
    print("\n" + "="*50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
