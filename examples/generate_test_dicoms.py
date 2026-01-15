#!/usr/bin/env python3
"""
Example: Generate Test DICOM Files
Ready-to-run script - just execute: python examples/generate_test_dicoms.py
"""

import sys
import os
from src.random_dicom import RandomDicomGenerator
from src.dcmlogger import setup_logging

def main():
    """Generate test DICOM files."""
    logger = setup_logging()
    
    # Configuration - EDIT THESE
    OUTPUT_DIR = "./test_dicom_output"  # Where to save generated files
    FILE_COUNT = 10                      # How many files to generate
    FILE_SIZE_MB = 1.0                   # Size of each file in MB
    
    print("\n" + "="*60)
    print("DICOM Generator")
    print("="*60 + "\n")
    
    try:
        # Create output directory if needed
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Output directory: {OUTPUT_DIR}")
        
        # Generate files
        print(f"\nGenerating {FILE_COUNT} DICOM files ({FILE_SIZE_MB} MB each)...")
        print("This may take a moment...\n")
        
        generator = RandomDicomGenerator(logger=logger)
        files = generator.generate_with_sizes(
            count=FILE_COUNT,
            size_mb=FILE_SIZE_MB,
            output_dir=OUTPUT_DIR
        )
        
        # Report results
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        print("="*60)
        print(f"? Generated {len(files)} DICOM files")
        print(f"? Location: {os.path.abspath(OUTPUT_DIR)}")
        print(f"? Total size: {len(files) * FILE_SIZE_MB:.1f} MB")
        
        print("\nGenerated files:")
        for i, filepath in enumerate(files[:5], 1):
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath) / (1024*1024)
            print(f"  {i}. {filename} ({filesize:.2f} MB)")
        
        if len(files) > 5:
            print(f"  ... and {len(files)-5} more files")
        
        print("\nYou can now:")
        print(f"  1. Load files in GUI from: {OUTPUT_DIR}")
        print(f"  2. Send files to remote server")
        print(f"  3. Run parallel transmission test")
        print(f"  4. Run load/stress test")
        
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"? Error: {e}")
        logger.exception("DICOM generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
