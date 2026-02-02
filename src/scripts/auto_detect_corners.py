#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-detection script for top-right corner markers using template matching.

Uses cropped QC square images from samples/top_right/ as templates to find
corner locations in full images from samples/original/.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm

def load_templates(template_dir):
    """Load all template images from the template directory."""
    templates = []
    
    template_files = [f for f in os.listdir(template_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    for template_file in template_files:
        template_path = os.path.join(template_dir, template_file)
        template = cv2.imread(template_path)
        if template is not None:
            # Convert to grayscale for template matching
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            templates.append({
                'image': template_gray,
                'name': template_file,
                'original': template
            })
    
    print(f"Loaded {len(templates)} template images")
    return templates

def detect_corner_with_templates(image, templates, search_region=None, scales=[0.5, 0.75, 1.0, 1.25, 1.5]):
    """
    Detect corner using multiple templates and scales.
    
    Args:
        image: Full image to search in
        templates: List of template images
        search_region: (x, y, width, height) to limit search area, or None for full image
        scales: List of scales to try for multi-scale matching
    
    Returns:
        (x, y, confidence) or (None, None, 0.0) if not found
    """
    if image is None:
        return None, None, 0.0
    
    # Convert to grayscale
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Limit search to top-right quadrant if no region specified
    if search_region is None:
        h, w = image_gray.shape
        search_region = (w // 2, 0, w // 2, h // 2)  # Top-right quadrant
    
    x_start, y_start, region_w, region_h = search_region
    search_area = image_gray[y_start:y_start+region_h, x_start:x_start+region_w]
    
    best_match = None
    best_confidence = 0.0
    best_location = (None, None)
    
    # Try each template
    for template_info in templates:
        template = template_info['image']
        t_h, t_w = template.shape
        
        # Try different scales
        for scale in scales:
            # Resize template
            scaled_w = int(t_w * scale)
            scaled_h = int(t_h * scale)
            
            if scaled_w > region_w or scaled_h > region_h:
                continue
            
            scaled_template = cv2.resize(template, (scaled_w, scaled_h))
            
            # Perform template matching
            result = cv2.matchTemplate(search_area, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Update best match
            if max_val > best_confidence:
                best_confidence = max_val
                # Convert back to full image coordinates
                best_location = (max_loc[0] + x_start + scaled_w // 2, 
                                max_loc[1] + y_start + scaled_h // 2)
                best_match = {
                    'template': template_info['name'],
                    'scale': scale,
                    'confidence': max_val
                }

    return best_location[0], best_location[1], best_confidence

def auto_detect_corners(template_dir, image_dir, output_file, confidence_threshold=0.5):
    """
    Auto-detect corners in all images using templates.
    
    Args:
        template_dir: Directory containing template QC square images
        image_dir: Directory containing full images to search
        output_file: Path to save annotations JSON
        confidence_threshold: Minimum confidence to accept a detection
    """
    # Load templates
    templates = load_templates(template_dir)
    if len(templates) == 0:
        print(f"Error: No templates found in {template_dir}")
        return
    
    # Get all images
    image_files = [f for f in os.listdir(image_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Filter out distorted images (we want original images)
    image_files = [f for f in image_files if '_distorted' not in f]
    
    print(f"Processing {len(image_files)} images...")
    
    annotations = {}
    detected_count = 0
    low_confidence_count = 0
    
    for image_file in tqdm(image_files):
        image_path = os.path.join(image_dir, image_file)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Warning: Could not load {image_file}")
            continue
        
        # Detect corner
        x, y, confidence = detect_corner_with_templates(image, templates)
        
        if x is not None and y is not None and confidence >= confidence_threshold:
            annotations[image_file] = {
                'x': float(x),
                'y': float(y),
                'confidence': float(confidence)
            }
            detected_count += 1
        elif confidence > 0:
            # Low confidence detection - still save but mark it
            annotations[image_file] = {
                'x': float(x) if x is not None else None,
                'y': float(y) if y is not None else None,
                'confidence': float(confidence),
                'needs_review': True
            }
            low_confidence_count += 1
        else:
            # No detection
            annotations[image_file] = {
                'x': None,
                'y': None,
                'confidence': 0.0,
                'needs_review': True
            }
            low_confidence_count += 1
    
    # Save annotations
    with open(output_file, 'w') as f:
        json.dump(annotations, f, indent=2)
    
    print(f"\nDetection complete:")
    print(f"  High confidence detections: {detected_count}")
    print(f"  Low confidence/needs review: {low_confidence_count}")
    print(f"  Annotations saved to: {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Auto-detect corner markers using template matching')
    parser.add_argument('--template_dir', type=str, 
                       default='../samples/top_right',
                       help='Directory containing template QC square images')
    parser.add_argument('--image_dir', type=str,
                       default='../samples/original',
                       help='Directory containing full images to search')
    parser.add_argument('--output', type=str,
                       default='auto_annotations.json',
                       help='Output JSON file for annotations')
    parser.add_argument('--confidence_threshold', type=float,
                       default=0.5,
                       help='Minimum confidence threshold (0.0-1.0)')
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    template_dir = os.path.abspath(args.template_dir)
    image_dir = os.path.abspath(args.image_dir)
    output_file = os.path.abspath(args.output)
    
    if not os.path.exists(template_dir):
        print(f"Error: Template directory not found: {template_dir}")
        return
    
    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found: {image_dir}")
        return
    
    auto_detect_corners(template_dir, image_dir, output_file, args.confidence_threshold)

if __name__ == '__main__':
    main()