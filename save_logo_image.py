#!/usr/bin/env python3
"""
Script to save the SafeSteps logo image properly.

INSTRUCTIONS:
1. Copy the SafeSteps logo image file to this directory as 'safesteps_logo.png'
2. Or run this script with the path to your logo file:
   python save_logo_image.py /path/to/your/logo.png
"""

import sys
import shutil
import os
from PIL import Image

def save_logo(source_path=None):
    if source_path and os.path.exists(source_path):
        # Copy the provided logo
        shutil.copy2(source_path, 'safesteps_logo.png')
        print(f"Logo copied from {source_path}")
    else:
        print("ERROR: Please provide the actual SafeSteps logo image!")
        print("\nOptions:")
        print("1. Copy your logo image to this directory as 'safesteps_logo.png'")
        print("2. Run: python save_logo_image.py /path/to/your/logo.png")
        return False
    
    # Verify it's a valid image
    try:
        img = Image.open('safesteps_logo.png')
        width, height = img.size
        print(f"✓ Valid image: {width}x{height} pixels, format: {img.format}")
        
        # Test certificate generation
        from certificate_generator_production import generate_certificate_for_app
        pdf = generate_certificate_for_app("Test User", "Test Course", "Pass", "Jul 30, 2025")
        with open("test_with_real_logo.pdf", "wb") as f:
            f.write(pdf)
        print("✓ Test certificate generated: test_with_real_logo.pdf")
        return True
        
    except Exception as e:
        print(f"ERROR: Invalid image file - {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        save_logo(sys.argv[1])
    else:
        save_logo()