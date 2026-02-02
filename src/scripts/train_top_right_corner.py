#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Training script for top-right corner detection model.
Wrapper around FieldChartOCR/train_chart.py with appropriate parameters.

Usage:
    python src/scripts/train_top_right_corner.py [--cfg_file CornerNetTopRight] [--data_dir ./data] [--cache_path ./cache]
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Top-Right Corner Detection Model")
    parser.add_argument("--cfg_file", dest="cfg_file", help="config file", 
                       default="CornerNetTopRight", type=str)
    parser.add_argument("--iter", dest="start_iter", help="train at iteration i", 
                       default=0, type=int)
    parser.add_argument("--threads", dest="threads", default=1, type=int)
    parser.add_argument('--cache_path', dest="cache_path", type=str, default=None)
    parser.add_argument("--data_dir", dest="data_dir", default=None, type=str)
    
    args = parser.parse_args()
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_root = os.path.dirname(script_dir)
    repo_root = os.path.dirname(src_root)
    fieldchart_dir = os.path.join(src_root, "FieldChartOCR")
    
    if args.data_dir is None:
        args.data_dir = os.path.join(repo_root, "data")
    
    if args.cache_path is None:
        args.cache_path = os.path.join(fieldchart_dir, "cache")
    
    print("=" * 50)
    print("Top-Right Corner Detection Training")
    print("=" * 50)
    print(f"Config file: {args.cfg_file}")
    print(f"Data directory: {args.data_dir}")
    print(f"Cache directory: {args.cache_path}")
    print(f"Starting from iteration: {args.start_iter}")
    print("=" * 50)
    
    # Build command to run train_chart.py
    train_script = os.path.join(fieldchart_dir, "train_chart.py")
    cmd = [
        sys.executable,
        train_script,
        "--cfg_file", args.cfg_file,
        "--iter", str(args.start_iter),
        "--threads", str(args.threads),
        "--data_dir", args.data_dir,
        "--cache_path", args.cache_path
    ]
    
    # Change to FieldChartOCR directory and run
    os.chdir(fieldchart_dir)
    try:
        subprocess.run(cmd, check=True)
    finally:
        os.chdir(repo_root)
