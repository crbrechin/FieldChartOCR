#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GIMP Python-Fu script to batch process images with random contrast, saturation, exposure, and white balance distortions.
This script is designed to be run via GIMP's batch mode for data augmentation.

Usage from command line:
gimp -i -b "(python-fu-distort-images RUN-NONINTERACTIVE \"path/to/folder\" \"_distorted\")" -b "(gimp-quit 0)"
"""

from gimpfu import *
import os
import random

def distort_images(input_folder, suffix="_distorted"):
    """
    Process all JPG images in the specified folder with random contrast, saturation, exposure, and white balance adjustments.
    
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
            image = pdb.gimp_file_load(input_path, input_path)
            drawable = pdb.gimp_image_get_active_layer(image)
            
            # Generate random distortion values
            # Contrast: -50 to +50 (will be scaled to GIMP's -127 to 127 range)
            contrast_adjustment = random.uniform(-50, 50)
            
            # Saturation: -50% to +50% (GIMP uses -100 to 100 range)
            saturation_adjustment = random.uniform(-50, 50)
            
            # Exposure: -1.0 to +1.0 stops (GIMP uses -3.0 to 3.0 range)
            exposure_adjustment = random.uniform(-1.0, 1.0)
            
            # White balance: -30% to +30% for each channel
            wb_red = random.uniform(-30, 30)
            wb_green = random.uniform(-30, 30)
            wb_blue = random.uniform(-30, 30)
            
            # Apply contrast adjustment using brightness-contrast
            # GIMP brightness-contrast uses -127 to 127 range
            contrast_scaled = int(contrast_adjustment * 127 / 50)
            pdb.gimp_brightness_contrast(drawable, 0, contrast_scaled)
            
            # Apply saturation adjustment using hue-saturation
            # GIMP hue-saturation uses -100 to 100 range for saturation
            # hue_range: 0 = all colors, hue_offset: 0 = no hue shift, lightness: 0 = no change
            saturation_scaled = int(saturation_adjustment * 100 / 50)
            pdb.gimp_hue_saturation(drawable, 0, 0, 0, saturation_scaled)
            
            # Apply exposure adjustment
            # GIMP exposure uses -3.0 to 3.0 range for exposure stops
            # offset: 0 = no offset, gamma: 1.0 = no gamma change
            exposure_scaled = exposure_adjustment * 3.0 / 1.0
            pdb.gimp_exposure(drawable, exposure_scaled, 0.0, 1.0)
            
            # Apply white balance using color balance
            # GIMP color balance uses -100 to 100 range for each channel
            # Scale our -30 to 30 range to -100 to 100
            wb_red_scaled = int(wb_red * 100 / 30)
            wb_green_scaled = int(wb_green * 100 / 30)
            wb_blue_scaled = int(wb_blue * 100 / 30)
            
            # Apply to midtones (most visible effect)
            pdb.gimp_color_balance(
                drawable,
                1,  # Transfer mode: midtones (0=shadows, 1=midtones, 2=highlights)
                True,  # Preserve luminosity
                wb_red_scaled,
                wb_green_scaled,
                wb_blue_scaled
            )
            
            # Also apply slightly to highlights for more natural look
            pdb.gimp_color_balance(
                drawable,
                2,  # Transfer mode: highlights
                True,  # Preserve luminosity
                int(wb_red_scaled * 0.5),  # Half strength for highlights
                int(wb_green_scaled * 0.5),
                int(wb_blue_scaled * 0.5)
            )
            
            # Save the processed image
            pdb.gimp_file_save(image, drawable, output_path, output_path)
            
            # Clean up
            pdb.gimp_image_delete(image)
            
            processed += 1
            print(f"Processed: {filename} -> {output_filename} (contrast: {contrast_adjustment:.1f}, saturation: {saturation_adjustment:.1f}, exposure: {exposure_adjustment:.2f}, WB: R{wb_red:.1f} G{wb_green:.1f} B{wb_blue:.1f})")
            
        except Exception as e:
            errors += 1
            print(f"Error processing {filename}: {str(e)}")
            try:
                if 'image' in locals():
                    pdb.gimp_image_delete(image)
            except:
                pass
    
    print(f"Processing complete: {processed} images processed, {errors} errors")

# Register the script as a GIMP plugin
register(
    "python-fu-distort-images",
    "Batch process images with random contrast, saturation, exposure, and white balance distortions",
    "Processes all JPG images in a folder, applying random contrast, saturation, exposure, and white balance adjustments for data augmentation",
    "DTSA-5506",
    "DTSA-5506",
    "2025",
    "Distort Images (Batch)",
    "",
    [
        (PF_STRING, "input_folder", "Input folder", ""),
        (PF_STRING, "suffix", "Output filename suffix", "_distorted"),
    ],
    [],
    distort_images
)

# Only register if this is being loaded as a GIMP plug-in
# When executed directly via python-fu-eval, we can call distort_images() directly
try:
    main()
except Exception as e:
    # If registration fails (e.g., when called directly), that's okay
    # The function is still available to be called directly
    pass

