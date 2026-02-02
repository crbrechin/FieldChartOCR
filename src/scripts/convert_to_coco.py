#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert verified annotations to COCO format for training.
"""

import os
import json
import shutil
import cv2
import numpy as np
from pathlib import Path
from collections import defaultdict

def create_coco_structure(annotations_file, image_dir, output_dir, train_ratio=0.8, val_ratio=0.1):
    """
    Convert annotations to COCO format and organize images into train/val/test splits.
    
    Args:
        annotations_file: Path to verified annotations JSON
        image_dir: Directory containing full images
        output_dir: Output directory for COCO dataset
        train_ratio: Ratio of images for training
        val_ratio: Ratio of images for validation (test gets the rest)
    """
    # Load annotations
    with open(annotations_file, 'r') as f:
        annotations = json.load(f)
    
    # Filter out images without valid annotations
    valid_annotations = {}
    for img_file, ann in annotations.items():
        if ann.get('x') is not None and ann.get('y') is not None:
            valid_annotations[img_file] = ann
    
    print(f"Found {len(valid_annotations)} valid annotations out of {len(annotations)} total")
    
    # Create directory structure
    data_dir = os.path.join(output_dir, "top_right")
    images_dir = os.path.join(data_dir, "images")
    annotations_dir = os.path.join(data_dir, "annotations")
    
    train_dir = os.path.join(images_dir, "train2019")
    val_dir = os.path.join(images_dir, "val2019")
    test_dir = os.path.join(images_dir, "test2019")
    
    for d in [train_dir, val_dir, test_dir, annotations_dir]:
        os.makedirs(d, exist_ok=True)
    
    # Split images
    image_files = sorted(list(valid_annotations.keys()))
    np.random.seed(42)  # For reproducibility
    np.random.shuffle(image_files)
    
    n_total = len(image_files)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    train_files = image_files[:n_train]
    val_files = image_files[n_train:n_train+n_val]
    test_files = image_files[n_train+n_val:]
    
    print(f"Split: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test")
    
    # Create COCO format for each split
    splits = {
        'train2019': train_files,
        'val2019': val_files,
        'test2019': test_files
    }
    
    for split_name, files in splits.items():
        coco_data = {
            "info": {
                "description": "Top-right corner detection dataset",
                "version": "1.0",
                "year": 2025
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [
                {
                    "id": 0,
                    "name": "top_right_corner",
                    "supercategory": "corner"
                }
            ]
        }
        
        image_id = 0
        annotation_id = 0
        
        for img_file in files:
            # Copy image to split directory
            src_path = os.path.join(image_dir, img_file)
            dst_path = os.path.join(images_dir, split_name, img_file)
            
            if not os.path.exists(src_path):
                print(f"Warning: Image not found: {src_path}")
                continue
            
            shutil.copy2(src_path, dst_path)
            
            # Get image dimensions
            img = cv2.imread(src_path)
            if img is None:
                print(f"Warning: Could not read image: {src_path}")
                continue
            
            height, width = img.shape[:2]
            
            # Add image info
            coco_data["images"].append({
                "id": image_id,
                "file_name": img_file,
                "width": width,
                "height": height
            })
            
            # Add annotation
            ann = valid_annotations[img_file]
            x = float(ann['x'])
            y = float(ann['y'])
            
            # COCO format for point detection: [x, y, 6, 6] (small bounding box around point)
            coco_data["annotations"].append({
                "id": annotation_id,
                "image_id": image_id,
                "category_id": 0,
                "bbox": [x - 3, y - 3, 6, 6],  # [x, y, width, height] format
                "area": 36.0,
                "iscrowd": 0
            })
            
            image_id += 1
            annotation_id += 1
        
        # Save COCO JSON
        output_file = os.path.join(annotations_dir, f"instancesTopRight_{split_name}.json")
        with open(output_file, 'w') as f:
            json.dump(coco_data, f, indent=2)
        
        print(f"Created {split_name}: {len(coco_data['images'])} images, {len(coco_data['annotations'])} annotations")
        print(f"  Saved to: {output_file}")
    
    print(f"\nCOCO dataset created in: {data_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert annotations to COCO format')
    parser.add_argument('--annotations', type=str,
                       default='verified_annotations.json',
                       help='Input verified annotations JSON file')
    parser.add_argument('--image_dir', type=str,
                       default='../samples/original',
                       help='Directory containing full images')
    parser.add_argument('--output_dir', type=str,
                       default='../data',
                       help='Output directory for COCO dataset')
    parser.add_argument('--train_ratio', type=float,
                       default=0.8,
                       help='Ratio of images for training (default: 0.8)')
    parser.add_argument('--val_ratio', type=float,
                       default=0.1,
                       help='Ratio of images for validation (default: 0.1)')
    
    args = parser.parse_args()
    
    annotations_file = os.path.abspath(args.annotations)
    image_dir = os.path.abspath(args.image_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    if not os.path.exists(annotations_file):
        print(f"Error: Annotations file not found: {annotations_file}")
        return
    
    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found: {image_dir}")
        return
    
    create_coco_structure(annotations_file, image_dir, output_dir, 
                         args.train_ratio, args.val_ratio)

if __name__ == '__main__':
    main()
