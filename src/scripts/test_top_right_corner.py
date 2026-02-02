#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testing/inference script for top-right corner detection model.
"""

import os
import sys
import cv2
import json
import numpy as np
import torch
import argparse
from pathlib import Path

# Add FieldChartOCR to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
fieldchart_dir = os.path.join(project_root, "FieldChartOCR")
sys.path.insert(0, fieldchart_dir)

from config import system_configs
from utils import crop_image
from db.datasets import datasets
from nnet.py_factory import NetworkFactory

def _rescale_points(dets, ratios, borders, sizes):
    xs, ys = dets[:, :, 2], dets[:, :, 3]
    xs    /= ratios[0, 1]
    ys    /= ratios[0, 0]
    xs    -= borders[0, 2]
    ys    -= borders[0, 0]
    np.clip(xs, 0, sizes[0, 1], out=xs)
    np.clip(ys, 0, sizes[0, 0], out=ys)

def kp_decode(nnet, images, K, ae_threshold=0.5, kernel=3):
    with torch.no_grad():
        detections, time_backbone, time_psn = nnet.test([images], ae_threshold=ae_threshold, K=K, kernel=kernel)
        detections_tl = detections[0]
        detections_br = detections[1]
        detections_tl = detections_tl.data.cpu().numpy().transpose((2, 1, 0))
        detections_br = detections_br.data.cpu().numpy().transpose((2, 1, 0))
        return detections_tl, detections_br, True

def kp_detection(image, db, nnet, debug=False, decode_func=kp_decode, cuda_id=0):
    K = db.configs["top_k"]
    ae_threshold = db.configs["ae_threshold"]
    nms_kernel = db.configs["nms_kernel"]
    
    categories = db.configs["categories"]
    nms_threshold = db.configs["nms_threshold"]
    max_per_image = db.configs["max_per_image"]
    
    height, width = image.shape[0:2]
    
    detections_point_tl = []
    detections_point_br = []
    scale = 1.0
    new_height = int(height * scale)
    new_width  = int(width * scale)
    new_center = np.array([new_height // 2, new_width // 2])
    
    inp_height = new_height | 127
    inp_width  = new_width  | 127
    images  = np.zeros((1, 3, inp_height, inp_width), dtype=np.float32)
    ratios  = np.zeros((1, 2), dtype=np.float32)
    borders = np.zeros((1, 4), dtype=np.float32)
    sizes   = np.zeros((1, 2), dtype=np.float32)
    
    out_height, out_width = (inp_height + 1) // 4, (inp_width + 1) // 4
    height_ratio = out_height / inp_height
    width_ratio  = out_width  / inp_width
    
    resized_image = cv2.resize(image, (new_width, new_height))
    resized_image, border, offset = crop_image(resized_image, new_center, [inp_height, inp_width])
    
    resized_image = resized_image / 255.
    
    images[0]  = resized_image.transpose((2, 0, 1))
    borders[0] = border
    sizes[0]   = [int(height * scale), int(width * scale)]
    ratios[0]  = [height_ratio, width_ratio]
    
    if torch.cuda.is_available():
        images = torch.from_numpy(images).cuda(cuda_id)
    else:
        images = torch.from_numpy(images)
    
    dets_tl, dets_br, flag = decode_func(nnet, images, K, ae_threshold=ae_threshold, kernel=nms_kernel)
    _rescale_points(dets_tl, ratios, borders, sizes)
    _rescale_points(dets_br, ratios, borders, sizes)
    
    detections_point_tl.append(dets_tl)
    detections_point_br.append(dets_br)
    detections_point_tl = np.concatenate(detections_point_tl, axis=1)
    detections_point_br = np.concatenate(detections_point_br, axis=1)
    
    classes_p_tl = detections_point_tl[:, 0, 1]
    classes_p_br = detections_point_br[:, 0, 1]
    
    # Reject detections with negative scores
    keep_inds_p = (detections_point_tl[:, 0, 0] > 0)
    detections_point_tl = detections_point_tl[keep_inds_p, 0]
    classes_p_tl = classes_p_tl[keep_inds_p]
    
    keep_inds_p = (detections_point_br[:, 0, 0] > 0)
    detections_point_br = detections_point_br[keep_inds_p, 0]
    classes_p_br = classes_p_br[keep_inds_p]
    
    top_points_tl = {}
    top_points_br = {}
    for j in range(categories):
        keep_inds_p = (classes_p_tl == j)
        top_points_tl[j + 1] = detections_point_tl[keep_inds_p].astype(np.float32)
        keep_inds_p = (classes_p_br == j)
        top_points_br[j + 1] = detections_point_br[keep_inds_p].astype(np.float32)
    
    # Filter by max_per_image
    scores = np.hstack([top_points_tl[j][:, 0] for j in range(1, categories + 1)])
    if len(scores) > max_per_image:
        kth = len(scores) - max_per_image
        thresh = np.partition(scores, kth)[kth]
        for j in range(1, categories + 1):
            keep_inds = (top_points_tl[j][:, 0] >= thresh)
            top_points_tl[j] = top_points_tl[j][keep_inds]
    
    scores = np.hstack([top_points_br[j][:, 0] for j in range(1, categories + 1)])
    if len(scores) > max_per_image:
        kth = len(scores) - max_per_image
        thresh = np.partition(scores, kth)[kth]
        for j in range(1, categories + 1):
            keep_inds = (top_points_br[j][:, 0] >= thresh)
            top_points_br[j] = top_points_br[j][keep_inds]
    
    return top_points_tl, top_points_br

def visualize_detection(image, detections_tl, detections_br, output_path=None):
    """Visualize detected corners on image."""
    vis_image = image.copy()
    
    # Draw top-left corners (we'll use these for top-right corner detection)
    for cat_id, points in detections_tl.items():
        for point in points:
            score, class_id, x, y = point
            cv2.circle(vis_image, (int(x), int(y)), 10, (0, 255, 0), 2)
            cv2.circle(vis_image, (int(x), int(y)), 3, (0, 255, 0), -1)
            cv2.putText(vis_image, f"{score:.2f}", (int(x)+15, int(y)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    if output_path:
        cv2.imwrite(output_path, vis_image)
    
    return vis_image

def test_model(cfg_file, test_iter, data_dir, cache_dir, test_split="valchart", 
               output_dir=None, visualize=True):
    """Test the trained model."""
    os.chdir(fieldchart_dir)
    
    # Load config
    cfg_path = os.path.join(system_configs.config_dir, cfg_file + ".json")
    with open(cfg_path, "r") as f:
        import json
        configs = json.load(f)
    
    configs["system"]["data_dir"] = data_dir
    configs["system"]["cache_dir"] = cache_dir
    system_configs.update_config(configs["system"])
    
    # Load dataset
    dataset = system_configs.dataset
    test_db = datasets[dataset](configs["db"], test_split)
    
    # Load model
    print("Loading model...")
    nnet = NetworkFactory(test_db)
    nnet.load_params(test_iter)
    nnet.cuda()
    nnet.eval_mode()
    
    print(f"Testing on {len(test_db.db_inds)} images...")
    
    # Create output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        vis_dir = os.path.join(output_dir, "visualizations")
        os.makedirs(vis_dir, exist_ok=True)
    
    results = []
    correct = 0
    total = 0
    
    for db_ind in range(len(test_db.db_inds)):
        image_file = test_db.image_file(db_ind)
        image = cv2.imread(image_file)
        
        if image is None:
            print(f"Warning: Could not load {image_file}")
            continue
        
        # Get ground truth
        gt_detections = test_db.detections(db_ind)
        
        # Run detection
        detections_tl, detections_br = kp_detection(image, test_db, nnet)
        
        # Evaluate (simple distance-based metric)
        if len(gt_detections) > 0:
            gt_point = gt_detections[0]  # [x1, y1, x2, y2, category]
            gt_x = (gt_point[0] + gt_point[2]) / 2
            gt_y = (gt_point[1] + gt_point[3]) / 2
            
            # Get best detection
            best_det = None
            best_score = 0
            for cat_id, points in detections_tl.items():
                for point in points:
                    if point[0] > best_score:
                        best_score = point[0]
                        best_det = point
            
            if best_det is not None:
                pred_x, pred_y = best_det[2], best_det[3]
                distance = np.sqrt((pred_x - gt_x)**2 + (pred_y - gt_y)**2)
                
                # Consider correct if within 20 pixels
                if distance < 20:
                    correct += 1
                total += 1
                
                results.append({
                    'image': os.path.basename(image_file),
                    'gt': (gt_x, gt_y),
                    'pred': (pred_x, pred_y),
                    'distance': distance,
                    'score': best_score,
                    'correct': distance < 20
                })
        
        # Visualize
        if visualize and output_dir:
            vis_image = visualize_detection(image, detections_tl, detections_br)
            output_path = os.path.join(vis_dir, os.path.basename(image_file))
            cv2.imwrite(output_path, vis_image)
    
    # Print results
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    if total > 0:
        accuracy = correct / total * 100
        print(f"Accuracy: {accuracy:.2f}% ({correct}/{total})")
        avg_distance = np.mean([r['distance'] for r in results])
        print(f"Average distance: {avg_distance:.2f} pixels")
    else:
        print("No valid detections found")
    
    # Save results
    if output_dir:
        results_file = os.path.join(output_dir, "test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
        if visualize:
            print(f"Visualizations saved to: {vis_dir}")

def main():
    parser = argparse.ArgumentParser(description="Test Top-Right Corner Detection Model")
    parser.add_argument("--cfg_file", type=str, default="CornerNetTopRight",
                       help="Config file name (without .json)")
    parser.add_argument("--test_iter", type=int, default=-1,
                       help="Model iteration to test (-1 for latest)")
    parser.add_argument("--data_dir", type=str, default=None,
                       help="Data directory")
    parser.add_argument("--cache_dir", type=str, default=None,
                       help="Cache directory")
    parser.add_argument("--test_split", type=str, default="valchart",
                       help="Test split (valchart or testchart)")
    parser.add_argument("--output_dir", type=str, default=None,
                       help="Output directory for results")
    parser.add_argument("--no_visualize", action="store_true",
                       help="Don't save visualizations")
    
    args = parser.parse_args()
    
    # Set defaults
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if args.data_dir is None:
        args.data_dir = os.path.join(project_root, "data")
    
    if args.cache_dir is None:
        args.cache_dir = os.path.join(fieldchart_dir, "cache")
    
    if args.output_dir is None:
        args.output_dir = os.path.join(project_root, "test_results")
    
    # Find latest model if test_iter is -1
    if args.test_iter == -1:
        snapshot_dir = os.path.join(fieldchart_dir, "outputs", args.cfg_file)
        if os.path.exists(snapshot_dir):
            snapshots = [f for f in os.listdir(snapshot_dir) if f.endswith('.pkl')]
            if snapshots:
                snapshots.sort(reverse=True)
                latest = snapshots[0]
                args.test_iter = int(latest.split('_')[-1].split('.')[0])
                print(f"Using latest model: iteration {args.test_iter}")
            else:
                print("Error: No model snapshots found")
                return
        else:
            print("Error: Snapshot directory not found")
            return
    
    test_model(args.cfg_file, args.test_iter, args.data_dir, args.cache_dir,
               args.test_split, args.output_dir, not args.no_visualize)

if __name__ == "__main__":
    main()
