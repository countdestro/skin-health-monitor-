"""
Merge multiple HAM10000-style datasets into one folder with 7 classes.
Expects subdirs (e.g. data/ham10000, data/ham10000_isic) each with CSV (image_id, dx) and images.
Output: data/merged/train/Actinic keratosis/, ... and merged/metadata.csv

Usage:
  python scripts/merge_datasets.py --data_dir "C:/data/skin_combined" --out merged
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

# Common CSV column names across datasets
DX_COL_ALIASES = ["dx", "label", "diagnosis", "target"]
ID_COL_ALIASES = ["image_id", "filename", "image", "id"]


def find_csv_and_images(base: str):
    """Locate first CSV and image folder under base."""
    csv_path = None
    images_dir = None
    for root, _, files in os.walk(base):
        for f in files:
            if f.lower().endswith(".csv") and "metadata" in f.lower() or f.lower() == "hmnist_28_28_L.csv":
                # Prefer metadata CSV
                if "metadata" in f.lower():
                    return os.path.join(root, f), os.path.dirname(root)
                if csv_path is None:
                    csv_path = os.path.join(root, f)
        if csv_path and "metadata" in csv_path:
            break
    if csv_path is None:
        for root, _, files in os.walk(base):
            for f in files:
                if f.lower().endswith(".csv"):
                    csv_path = os.path.join(root, f)
                    break
            if csv_path:
                break
    if csv_path:
        images_dir = os.path.dirname(csv_path)
        # Often images are in a sibling folder
        for d in os.listdir(os.path.dirname(csv_path)):
            full = os.path.join(os.path.dirname(csv_path), d)
            if os.path.isdir(full) and any(f.lower().endswith((".jpg", ".png")) for f in os.listdir(full)[:5]):
                images_dir = full
                break
    return csv_path, images_dir


def load_one_metadata(csv_path: str, images_dir: str) -> pd.DataFrame | None:
    df = pd.read_csv(csv_path, nrows=5)
    dx_col = next((c for c in df.columns if c.lower() in [x.lower() for x in DX_COL_ALIASES]), None)
    id_col = next((c for c in df.columns if c.lower() in [x.lower() for x in ID_COL_ALIASES]), None)
    if not dx_col or not id_col:
        return None
    df = pd.read_csv(csv_path)
    df = df[[id_col, dx_col]].dropna()
    df["dx"] = df[dx_col].astype(str).str.strip().str.lower()
    df = df[df["dx"].isin(DX_TO_IDX)]
    df["image_id"] = df[id_col].astype(str)
    if not df["image_id"].iloc[0].lower().endswith((".jpg", ".jpeg", ".png")):
        df["image_path"] = df["image_id"] + ".jpg"
    else:
        df["image_path"] = df["image_id"]
    df["image_dir"] = images_dir
    return df[["dx", "image_id", "image_path", "image_dir"]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, help="Dir containing ham10000/, ham10000_isic/, etc.")
    p.add_argument("--out", default="merged", help="Output subdir name")
    args = p.parse_args()

    out_base = os.path.join(args.data_dir, args.out)
    train_dir = os.path.join(out_base, "train")
    for c in HAM10000_CLASSES:
        os.makedirs(os.path.join(train_dir, c), exist_ok=True)

    all_rows = []
    subdirs = [d for d in os.listdir(args.data_dir) if os.path.isdir(os.path.join(args.data_dir, d)) and d != args.out]
    for sub in subdirs:
        base = os.path.join(args.data_dir, sub)
        csv_path, images_dir = find_csv_and_images(base)
        if not csv_path or not os.path.isfile(csv_path):
            continue
        df = load_one_metadata(csv_path, images_dir or os.path.dirname(csv_path))
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            src = os.path.join(row["image_dir"], row["image_path"])
            if not os.path.isfile(src):
                for ext in [".jpg", ".jpeg", ".png"]:
                    s = os.path.join(row["image_dir"], row["image_id"] + ext)
                    if os.path.isfile(s):
                        src = s
                        break
            if not os.path.isfile(src):
                continue
            name = HAM10000_CLASSES[DX_TO_IDX[row["dx"]]]
            dst = os.path.join(train_dir, name, os.path.basename(src))
            if not os.path.isfile(dst):
                try:
                    shutil.copy2(src, dst)
                except Exception:
                    pass
            all_rows.append({"image_id": row["image_id"], "dx": row["dx"], "class_name": name})

    if not all_rows:
        print("No data merged. Ensure each subdir has a CSV with dx + image_id and an images folder.", file=sys.stderr)
        sys.exit(1)
    meta = pd.DataFrame(all_rows)
    meta_path = os.path.join(out_base, "metadata.csv")
    meta.to_csv(meta_path, index=False)
    print(f"Merged {len(meta)} rows into {train_dir}. Metadata: {meta_path}")
    print("Train with: python scripts/train_advanced.py --data_dir", repr(train_dir), "--use_folders")


if __name__ == "__main__":
    main()
