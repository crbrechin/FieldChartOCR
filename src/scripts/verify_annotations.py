#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interactive tool for verifying and correcting auto-detected corner annotations.
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path

class AnnotationVerifier:
    def __init__(self, annotations_file, image_dir, output_file):
        self.annotations_file = annotations_file
        self.image_dir = image_dir
        self.output_file = output_file
        
        # Load annotations
        with open(annotations_file, 'r') as f:
            self.annotations = json.load(f)
        
        # Get list of images
        self.image_files = sorted([f for f in self.annotations.keys()])
        self.current_index = 0
        
        # Load images
        self.current_image = None
        self.current_image_file = None
        self.current_point = None
        self.window_name = "Corner Verification - Press 'h' for help"
        
        # Mouse callback state
        self.mouse_point = None
        
        print(f"Loaded {len(self.image_files)} images for verification")
        print("Controls:")
        print("  Click: Set corner location")
        print("  'n' or Right Arrow: Next image")
        print("  'p' or Left Arrow: Previous image")
        print("  'a': Accept current detection")
        print("  'r': Reject/clear current detection")
        print("  's': Save and exit")
        print("  'q': Quit without saving")
        print("  'h': Show help")
    
    def load_image(self, index):
        """Load image at given index."""
        if index < 0 or index >= len(self.image_files):
            return False
        
        self.current_index = index
        self.current_image_file = self.image_files[index]
        image_path = os.path.join(self.image_dir, self.current_image_file)
        
        self.current_image = cv2.imread(image_path)
        if self.current_image is None:
            print(f"Warning: Could not load {self.current_image_file}")
            return False
        
        # Get current annotation
        ann = self.annotations.get(self.current_image_file, {})
        if ann.get('x') is not None and ann.get('y') is not None:
            self.current_point = (int(ann['x']), int(ann['y']))
        else:
            self.current_point = None
        
        self.mouse_point = None
        return True
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to set corner location."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_point = (x, y)
            self.current_point = (x, y)
            self.draw_image()
    
    def draw_image(self):
        """Draw image with current annotation."""
        if self.current_image is None:
            return
        
        display_image = self.current_image.copy()
        
        # Draw current point
        point_to_draw = self.mouse_point if self.mouse_point else self.current_point
        if point_to_draw:
            cv2.circle(display_image, point_to_draw, 10, (0, 255, 0), 2)
            cv2.circle(display_image, point_to_draw, 3, (0, 255, 0), -1)
        
        # Draw confidence info
        ann = self.annotations.get(self.current_image_file, {})
        confidence = ann.get('confidence', 0.0)
        needs_review = ann.get('needs_review', False)
        
        info_text = f"Image {self.current_index + 1}/{len(self.image_files)}: {self.current_image_file}"
        cv2.putText(display_image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        conf_text = f"Confidence: {confidence:.2f}"
        color = (0, 255, 0) if confidence >= 0.5 else (0, 165, 255) if confidence > 0 else (0, 0, 255)
        cv2.putText(display_image, conf_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        if needs_review:
            cv2.putText(display_image, "NEEDS REVIEW", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow(self.window_name, display_image)
    
    def save_annotations(self):
        """Save updated annotations to output file."""
        # Update annotations with current point
        if self.current_image_file:
            ann = self.annotations.get(self.current_image_file, {})
            if self.current_point:
                ann['x'] = float(self.current_point[0])
                ann['y'] = float(self.current_point[1])
                ann['verified'] = True
                if 'needs_review' in ann:
                    del ann['needs_review']
            else:
                ann['x'] = None
                ann['y'] = None
                ann['needs_review'] = True
            self.annotations[self.current_image_file] = ann
        
        with open(self.output_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
        print(f"\nAnnotations saved to {self.output_file}")
    
    def run(self):
        """Run the verification interface."""
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # Load first image
        if not self.load_image(0):
            print("Error: No images to verify")
            return
        
        self.draw_image()
        
        while True:
            key = cv2.waitKey(0) & 0xFF
            
            if key == ord('q'):
                print("Quitting without saving...")
                break
            elif key == ord('s'):
                self.save_annotations()
                break
            elif key == ord('n') or key == 83:  # 'n' or right arrow
                # Save current annotation before moving
                if self.current_image_file and self.current_point:
                    ann = self.annotations.get(self.current_image_file, {})
                    ann['x'] = float(self.current_point[0])
                    ann['y'] = float(self.current_point[1])
                    ann['verified'] = True
                    if 'needs_review' in ann:
                        del ann['needs_review']
                    self.annotations[self.current_image_file] = ann
                
                if self.current_index < len(self.image_files) - 1:
                    self.load_image(self.current_index + 1)
                    self.draw_image()
            elif key == ord('p') or key == 81:  # 'p' or left arrow
                if self.current_index > 0:
                    # Save current annotation before moving
                    if self.current_image_file and self.current_point:
                        ann = self.annotations.get(self.current_image_file, {})
                        ann['x'] = float(self.current_point[0])
                        ann['y'] = float(self.current_point[1])
                        ann['verified'] = True
                        if 'needs_review' in ann:
                            del ann['needs_review']
                        self.annotations[self.current_image_file] = ann
                    
                    self.load_image(self.current_index - 1)
                    self.draw_image()
            elif key == ord('a'):  # Accept
                if self.current_point:
                    ann = self.annotations.get(self.current_image_file, {})
                    ann['x'] = float(self.current_point[0])
                    ann['y'] = float(self.current_point[1])
                    ann['verified'] = True
                    if 'needs_review' in ann:
                        del ann['needs_review']
                    self.annotations[self.current_image_file] = ann
                    print("Accepted")
                self.draw_image()
            elif key == ord('r'):  # Reject/clear
                self.current_point = None
                self.mouse_point = None
                ann = self.annotations.get(self.current_image_file, {})
                ann['x'] = None
                ann['y'] = None
                ann['needs_review'] = True
                self.annotations[self.current_image_file] = ann
                print("Rejected/cleared")
                self.draw_image()
            elif key == ord('h'):  # Help
                print("\nControls:")
                print("  Click: Set corner location")
                print("  'n' or Right Arrow: Next image")
                print("  'p' or Left Arrow: Previous image")
                print("  'a': Accept current detection")
                print("  'r': Reject/clear current detection")
                print("  's': Save and exit")
                print("  'q': Quit without saving")
        
        cv2.destroyAllWindows()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify and correct auto-detected corner annotations')
    parser.add_argument('--annotations', type=str,
                       default='auto_annotations.json',
                       help='Input annotations JSON file')
    parser.add_argument('--image_dir', type=str,
                       default='../samples/original',
                       help='Directory containing full images')
    parser.add_argument('--output', type=str,
                       default='verified_annotations.json',
                       help='Output verified annotations JSON file')
    
    args = parser.parse_args()
    
    annotations_file = os.path.abspath(args.annotations)
    image_dir = os.path.abspath(args.image_dir)
    output_file = os.path.abspath(args.output)
    
    if not os.path.exists(annotations_file):
        print(f"Error: Annotations file not found: {annotations_file}")
        return
    
    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found: {image_dir}")
        return
    
    verifier = AnnotationVerifier(annotations_file, image_dir, output_file)
    verifier.run()

if __name__ == '__main__':
    main()
