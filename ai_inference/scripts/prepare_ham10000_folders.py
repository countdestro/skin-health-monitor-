"""
Create folder-per-class layout from HAM10000 CSV + images.
Use when you have HAM10000_metadata.csv and an images/ folder. Run once, then train with --use_folders.

Usage:
  python scripts/prepare_ham10000_folders.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
from src.dataset_config import DX_TO_IDX, HAM10000_CLASSES

# dx code -> display name for folder
DX_TO_NAME = {dx: HAM10000_CLASSES[i] for dx, i in DX_TO_IDX.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True)
    p.add_argument("--csv", default="HAM10000_metadata.csv")
    p.add_argument("--images_dir", default="images")
    p.add_argument("--out", default=None, help="Output base dir (default: data_dir/train)")
    args = p.parse_args()

    csv_path = os.path.join(args.data_dir, args.csv) if not os.path.isabs(args.csv) else args.csv
    img_dir = os.path.join(args.data_dir, args.images_dir) if not os.path.isabs(args.images_dir) else args.images_dir
    out_base = args.out or os.path.join(args.data_dir, "train")

    df = pd.read_csv(csv_path)
    id_col = "image_id" if "image_id" in df.columns else "filename"
    dx_col = "dx" if "dx" in df.columns else "label"
    df["dx"] = df[dx_col].astype(str).str.strip().str.lower()
    df = df[df["dx"].isin(DX_TO_NAME)]
    df["filename"] = df[id_col].astype(str)
    if not df["filename"].iloc[0].lower().endswith((".jpg", ".jpeg", ".png")):
        df["filename"] = df["filename"] + ".jpg"
    df["class_name"] = df["dx"].map(DX_TO_NAME)

    for name in HAM10000_CLASSES:
        os.makedirs(os.path.join(out_base, name), exist_ok=True)

    for _, row in df.iterrows():
        fname = os.path.basename(str(row["filename"]))
        src = os.path.join(img_dir, row["filename"])
        dst_dir = os.path.join(out_base, row["class_name"])
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dst_dir, fname))
        else:
            for ext in [".jpg", ".jpeg", ".png"]:
                s = os.path.join(img_dir, str(row[id_col]) + ext)
                if os.path.isfile(s):
                    shutil.copy2(s, os.path.join(dst_dir, fname))
                    break

    print("Created folder layout at", out_base)
    print("Train with: python scripts/train_ham10000.py --data_dir", repr(out_base), "--use_folders")


if __name__ == "__main__":
    main()
