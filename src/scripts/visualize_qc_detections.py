#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visualize QC square detections by overlaying calculated-size rectangles on images.

The rectangle size is calculated from physical dimensions to help detect image
skewness and normalization issues. If the image is skewed, the rectangle will
appear as a non-square, indicating normalization is needed.
"""

import os
import json
import time
import cv2
from tqdm import tqdm

# Physical dimensions constants
QC_SQUARE_SIZE_MM = 6 * 0.975  # 6 cells × 0.975mm = 5.85mm
PAGE_HEIGHT_MM = 279.4  # US Letter: 11 inches = 279.4mm
PAGE_WIDTH_MM = 215.9   # US Letter: 8.5 inches = 215.9mm

def calculate_qc_rectangle_size(image_height, image_width):
    """
    Calculate QC square rectangle size in pixels based on physical dimensions.
    
    Args:
        image_height: Pixel height of the image
        image_width: Pixel width of the image
    
    Returns:
        (width_pixels, height_pixels) tuple
    """
    # #region agent log
    log_path = r'c:\Users\lenovo\Documents\ucboulder\msds\dtsa-5506\.cursor\debug.log'
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B",
                "location": "visualize_qc_detections.py:calculate_qc_rectangle_size:entry",
                "message": "Calculating QC rectangle size",
                "data": {
                    "image_height": image_height,
                    "image_width": image_width,
                    "qc_square_size_mm": QC_SQUARE_SIZE_MM,
                    "page_height_mm": PAGE_HEIGHT_MM,
                    "page_width_mm": PAGE_WIDTH_MM
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Calculate scale factors (mm per pixel)
    scale_height = PAGE_HEIGHT_MM / image_height
    scale_width = PAGE_WIDTH_MM / image_width
    
    # Calculate QC square size in pixels
    qc_square_height_pixels = QC_SQUARE_SIZE_MM / scale_height
    qc_square_width_pixels = QC_SQUARE_SIZE_MM / scale_width
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B",
                "location": "visualize_qc_detections.py:calculate_qc_rectangle_size:calculated",
                "message": "QC rectangle size calculated",
                "data": {
                    "scale_height": scale_height,
                    "scale_width": scale_width,
                    "qc_square_height_pixels": qc_square_height_pixels,
                    "qc_square_width_pixels": qc_square_width_pixels,
                    "qc_width_int": int(qc_square_width_pixels),
                    "qc_height_int": int(qc_square_height_pixels)
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    return int(qc_square_width_pixels), int(qc_square_height_pixels)

def get_confidence_color(confidence):
    """
    Get color based on confidence level.
    
    Args:
        confidence: Confidence value (0.0 to 1.0)
    
    Returns:
        (B, G, R) color tuple for OpenCV
    """
    if confidence >= 0.8:
        return (0, 255, 0)  # Green - high confidence
    elif confidence >= 0.5:
        return (0, 165, 255)  # Orange - medium confidence
    else:
        return (0, 0, 255)  # Red - low confidence

def draw_qc_detection(image, x, y, width, height, confidence):
    """
    Draw QC square detection rectangle on image.
    
    Args:
        image: Image to draw on (will be modified)
        x: X coordinate of detection center
        y: Y coordinate of detection center
        width: Width of rectangle in pixels
        height: Height of rectangle in pixels
        confidence: Confidence value for color coding
    """
    # #region agent log
    log_path = r'c:\Users\lenovo\Documents\ucboulder\msds\dtsa-5506\.cursor\debug.log'
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A",
                "location": "visualize_qc_detections.py:draw_qc_detection:entry",
                "message": "Drawing QC detection rectangle",
                "data": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "confidence": confidence,
                    "image_shape": list(image.shape) if image is not None else None
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Calculate rectangle corners (centered at x, y)
    half_width = width // 2
    half_height = height // 2
    
    pt1 = (int(x - half_width), int(y - half_height))
    pt2 = (int(x + half_width), int(y + half_height))
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A",
                "location": "visualize_qc_detections.py:draw_qc_detection:corners",
                "message": "Rectangle corners calculated",
                "data": {
                    "pt1": list(pt1),
                    "pt2": list(pt2),
                    "half_width": half_width,
                    "half_height": half_height,
                    "actual_width": pt2[0] - pt1[0],
                    "actual_height": pt2[1] - pt1[1]
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Get color based on confidence
    color = get_confidence_color(confidence)
    
    # Draw rectangle
    cv2.rectangle(image, pt1, pt2, color, 2)
    
    # Draw center point
    cv2.circle(image, (int(x), int(y)), 5, color, -1)
    
    # Draw confidence text
    conf_text = f"{confidence:.2f}"
    text_size = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    text_x = int(x + half_width + 10)
    text_y = int(y - half_height)
    
    # Ensure text stays within image bounds
    if text_x + text_size[0] > image.shape[1]:
        text_x = int(x - half_width - text_size[0] - 10)
    if text_y < text_size[1]:
        text_y = int(y + half_height + text_size[1] + 10)
    
    # Draw text with background for readability
    cv2.rectangle(image, 
                  (text_x - 2, text_y - text_size[1] - 2),
                  (text_x + text_size[0] + 2, text_y + 2),
                  (0, 0, 0), -1)
    cv2.putText(image, conf_text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

def visualize_detections(annotations_file, image_dir, output_suffix="_annotated"):
    """
    Visualize QC square detections on images.
    
    Args:
        annotations_file: Path to JSON file with annotations
        image_dir: Directory containing images
        output_suffix: Suffix to add to output filenames
    """
    # Load annotations
    with open(annotations_file, 'r') as f:
        annotations = json.load(f)
    
    # Get all image files
    image_files = [f for f in os.listdir(image_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    # Filter out already annotated images and distorted images
    image_files = [f for f in image_files 
                   if output_suffix not in f and '_distorted' not in f]
    
    print(f"Processing {len(image_files)} images...")
    
    processed_count = 0
    skipped_count = 0
    
    for image_file in tqdm(image_files):
        # Get annotation for this image
        annotation = annotations.get(image_file)
        
        if annotation is None:
            print(f"Warning: No annotation found for {image_file}")
            skipped_count += 1
            continue
        
        x = annotation.get('x')
        y = annotation.get('y')
        confidence = annotation.get('confidence', 0.0)
        
        # Skip if no valid coordinates
        if x is None or y is None:
            print(f"Warning: Invalid coordinates for {image_file}")
            skipped_count += 1
            continue
        
        # Load image
        image_path = os.path.join(image_dir, image_file)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Warning: Could not load {image_file}")
            skipped_count += 1
            continue
        
        # Get image dimensions
        image_height, image_width = image.shape[:2]
        
        # #region agent log
        log_path = r'c:\Users\lenovo\Documents\ucboulder\msds\dtsa-5506\.cursor\debug.log'
        try:
            with open(log_path, 'a') as f:
                log_entry = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "C",
                    "location": "visualize_qc_detections.py:visualize_detections:before_calc",
                    "message": "Before calculating QC rectangle",
                    "data": {
                        "image_file": image_file,
                        "image_height": image_height,
                        "image_width": image_width,
                        "detection_x": x,
                        "detection_y": y,
                        "confidence": confidence
                    },
                    "timestamp": int(time.time() * 1000)
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        
        # Check if coordinates are outside image bounds (indicating cropped image)
        is_cropped_image = (x < 0 or x >= image_width or y < 0 or y >= image_height)
        
        if is_cropped_image:
            # For cropped images, center the annotation and use most of the image
            # The cropped image IS the QC square, so we want to draw a rectangle
            # that covers most of it (with some margin)
            margin_ratio = 0.1  # 10% margin on each side
            qc_width = int(image_width * (1 - 2 * margin_ratio))
            qc_height = int(image_height * (1 - 2 * margin_ratio))
            center_x = image_width // 2
            center_y = image_height // 2
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    log_entry = {
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "D",
                        "location": "visualize_qc_detections.py:visualize_detections:cropped_image",
                        "message": "Detected cropped image, centering annotation",
                        "data": {
                            "image_file": image_file,
                            "original_x": x,
                            "original_y": y,
                            "centered_x": center_x,
                            "centered_y": center_y,
                            "qc_width": qc_width,
                            "qc_height": qc_height
                        },
                        "timestamp": int(time.time() * 1000)
                    }
                    f.write(json.dumps(log_entry) + '\n')
            except Exception:
                pass
            # #endregion
            
            x, y = center_x, center_y
        else:
            # For full page images, calculate QC square size from physical dimensions
            qc_width, qc_height = calculate_qc_rectangle_size(image_height, image_width)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                log_entry = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "C",
                    "location": "visualize_qc_detections.py:visualize_detections:after_calc",
                    "message": "After calculating QC rectangle",
                    "data": {
                        "image_file": image_file,
                        "qc_width": qc_width,
                        "qc_height": qc_height,
                        "final_x": x,
                        "final_y": y,
                        "is_cropped": is_cropped_image
                    },
                    "timestamp": int(time.time() * 1000)
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        
        # Draw detection
        draw_qc_detection(image, x, y, qc_width, qc_height, confidence)
        
        # Save annotated image
        base_name = os.path.splitext(image_file)[0]
        ext = os.path.splitext(image_file)[1]
        output_filename = f"{base_name}{output_suffix}{ext}"
        output_path = os.path.join(image_dir, output_filename)
        
        cv2.imwrite(output_path, image)
        processed_count += 1
    
    print(f"\nVisualization complete:")
    print(f"  Processed: {processed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Output directory: {image_dir}")

def main():
    import argparse
    
    # #region agent log
    log_path = r'c:\Users\lenovo\Documents\ucboulder\msds\dtsa-5506\.cursor\debug.log'
    try:
        with open(log_path, 'a') as f:
            import json
            import time
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A",
                "location": "visualize_qc_detections.py:main:entry",
                "message": "main() function entry",
                "data": {
                    "cwd": os.getcwd(),
                    "script_dir": os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else "unknown"
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    parser = argparse.ArgumentParser(
        description='Visualize QC square detections with calculated-size rectangles'
    )
    parser.add_argument('--annotations', type=str,
                       default='auto_annotations.json',
                       help='Input annotations JSON file')
    parser.add_argument('--image_dir', type=str,
                       default='../samples/original',
                       help='Directory containing full page images (must match annotation coordinates)')
    parser.add_argument('--output_suffix', type=str,
                       default='_annotated',
                       help='Suffix to add to output filenames')
    
    args = parser.parse_args()
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "B",
                "location": "visualize_qc_detections.py:main:args_parsed",
                "message": "Command line arguments parsed",
                "data": {
                    "annotations_arg": args.annotations,
                    "image_dir_arg": args.image_dir,
                    "cwd": os.getcwd()
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Convert relative paths to absolute
    annotations_file = os.path.abspath(args.annotations)
    image_dir = os.path.abspath(args.image_dir)
    
    # #region agent log
    try:
        with open(log_path, 'a') as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "C",
                "location": "visualize_qc_detections.py:main:paths_resolved",
                "message": "Paths resolved to absolute",
                "data": {
                    "annotations_file": annotations_file,
                    "image_dir": image_dir,
                    "annotations_exists": os.path.exists(annotations_file),
                    "image_dir_exists": os.path.exists(image_dir)
                },
                "timestamp": int(time.time() * 1000)
            }
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    if not os.path.exists(annotations_file):
        print(f"Error: Annotations file not found: {annotations_file}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Tried to resolve: {args.annotations}")
        return
    
    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found: {image_dir}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Tried to resolve: {args.image_dir}")
        return
    
    visualize_detections(annotations_file, image_dir, args.output_suffix)

if __name__ == '__main__':
    main()
