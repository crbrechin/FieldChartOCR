#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Standalone Python script to batch process images with random contrast and white balance distortions.
Uses PIL/Pillow instead of GIMP for easier execution.

Usage:
python distort_images_pil.py <input_folder> [suffix]
"""

from PIL import Image, ImageEnhance
import os
import random
import sys

def distort_images(input_folder, suffix="_distorted"):
    """
    Process all JPG images in the specified folder with random contrast and white balance adjustments.
    
    Parameters:
    input_folder: Path to folder containing images
    suffix: Suffix to add to output filenames (before extension)
    """
    # Ensure we have a valid folder
    if not os.path.exists(input_folder):
        print(f"Error: Folder {input_folder} does not exist!")
        return
    
    # Get all JPG files
    jpg_files = [f for f in os.listdir(input_folder) 
                 if f.lower().endswith(('.jpg', '.jpeg'))]
    
    if not jpg_files:
        print(f"No JPG files found in {input_folder}")
        return
    
    # Filter out files that already have the suffix to avoid reprocessing
    jpg_files = [f for f in jpg_files if suffix not in f]
    
    processed = 0
    errors = 0
    
    print(f"Found {len(jpg_files)} images to process in {input_folder}")
    
    for filename in jpg_files:
        try:
            input_path = os.path.join(input_folder, filename)
            
            # Generate output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}{suffix}{ext}"
            output_path = os.path.join(input_folder, output_filename)
            
            # Skip if output already exists
            if os.path.exists(output_path):
                print(f"Skipping {filename} - output already exists")
                continue
            
            # Load the image
            image = Image.open(input_path)
            
            # Generate random distortion values
            # Contrast: 0.5 to 1.5 (PIL uses 0.0 to 2.0, where 1.0 is no change)
            contrast_factor = random.uniform(0.5, 1.5)
            
            # White balance: adjust RGB channels independently
            # We'll use color enhancement with random factors
            wb_red = random.uniform(0.7, 1.3)
            wb_green = random.uniform(0.7, 1.3)
            wb_blue = random.uniform(0.7, 1.3)
            
            # Apply contrast adjustment
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast_factor)
            
            # Apply white balance by adjusting RGB channels
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Split into channels
            r, g, b = image.split()
            
            # Apply white balance adjustments
            r = ImageEnhance.Brightness(r).enhance(wb_red)
            g = ImageEnhance.Brightness(g).enhance(wb_green)
            b = ImageEnhance.Brightness(b).enhance(wb_blue)
            
            # Merge channels back
            image = Image.merge('RGB', (r, g, b))
            
            # Save the processed image
            image.save(output_path, quality=95)
            
            processed += 1
            print(f"Processed: {filename} -> {output_filename} (contrast: {contrast_factor:.2f}, WB: R{wb_red:.2f} G{wb_green:.2f} B{wb_blue:.2f})")
            
        except Exception as e:
            errors += 1
            print(f"Error processing {filename}: {str(e)}")
    
    print(f"\nProcessing complete: {processed} images processed, {errors} errors")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python distort_images_pil.py <input_folder> [suffix]")
        print("Example: python distort_images_pil.py samples/top_right _distorted")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) > 2 else "_distorted"
    
    distort_images(input_folder, suffix)
