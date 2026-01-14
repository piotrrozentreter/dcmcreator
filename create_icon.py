#!/usr/bin/env python
"""
Script to create an icon for the DICOM Creator application.
Generates a simple blue medical/DICOM themed icon.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(output_path="app.ico"):
    """Create a medical-themed icon for DICOM Creator."""
    
    # Create a new image with white background
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue square background
    margin = 10
    draw.rectangle(
        [(margin, margin), (size - margin, size - margin)],
        fill=(30, 90, 150, 255),
        outline=(10, 50, 100, 255),
        width=3
    )
    
    # Draw a cross (medical symbol) in the center in white
    cross_size = size // 3
    cross_x = size // 2
    cross_y = size // 2
    cross_width = 8
    
    # Horizontal bar
    draw.rectangle(
        [(cross_x - cross_size, cross_y - cross_width),
         (cross_x + cross_size, cross_y + cross_width)],
        fill=(255, 255, 255, 255)
    )
    
    # Vertical bar
    draw.rectangle(
        [(cross_x - cross_width, cross_y - cross_size),
         (cross_x + cross_width, cross_y + cross_size)],
        fill=(255, 255, 255, 255)
    )
    
    # Save as ICO
    img.save(output_path)
    print(f"? Icon created: {output_path}")
    
    # Also create smaller sizes for multiple resolutions
    ico_path = output_path
    
    # Create .ico file with multiple sizes
    img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    
    img.save(ico_path, sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print(f"? Multi-resolution icon saved: {ico_path}")
    print(f"  Includes sizes: 256x256, 128x128, 64x64, 32x32, 16x16")

if __name__ == "__main__":
    create_icon()
