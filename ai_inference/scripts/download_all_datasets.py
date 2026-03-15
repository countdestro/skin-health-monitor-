"""
Download multiple skin lesion datasets from Kaggle (and optionally NIH/ISIC).
Requires: pip install kaggle, then set up kaggle.json in ~/.kaggle/ or %USERPROFILE%\.kaggle\

Datasets downloaded:
  1. HAM10000 (kmader/skin-cancer-mnist-ham10000) — 10k images, 7 classes
  2. Skin Disease Detection HAM10000+ISIC (nour12347653) — extra images, same 7 classes
  3. Melanoma 10k (hasnainjaved/melanoma-skin-cancer-dataset-of-10000-images) — if 7-class or we map

Usage:
  python scripts/download_all_datasets.py --out_dir "C:/data/skin_combined"
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Kaggle dataset slugs: (dataset_slug, subdir_name, expected_csv, expected_images_dir)
KAGGLE_DATASETS = [
    ("kmader/skin-cancer-mnist-ham10000", "ham10000", "HAM10000_metadata.csv", "ham10000_images_part1"),
    ("nour12347653/skin-disease-detection-dataset-ham10000-isic", "ham10000_isic", None, None),  # structure may vary
    ("hasnainjaved/melanoma-skin-cancer-dataset-of-10000-images", "melanoma10k", None, None),
]


def run_kaggle(dataset_slug: str, out_path: str, unzip: bool = True) -> bool:
    cmd = ["kaggle", "datasets", "download", "-p", out_path]
    if unzip:
        cmd.append("--unzip")
    cmd.append(dataset_slug)
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  Failed {dataset_slug}: {e}", file=sys.stderr)
        return False


def main():
    p = argparse.ArgumentParser(description="Download multiple skin datasets from Kaggle")
    p.add_argument("--out_dir", default=os.path.join(ROOT, "data", "skin_combined"), help="Base output directory")
    p.add_argument("--datasets", nargs="*", default=["ham10000"], help="Which to download: ham10000, ham10000_isic, melanoma10k, all")
    p.add_argument("--no_unzip", action="store_true", help="Do not unzip after download")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if "all" in args.datasets:
        to_download = [d[0] for d in KAGGLE_DATASETS]
        names = [d[1] for d in KAGGLE_DATASETS]
    else:
        name_to_slug = {d[1]: d[0] for d in KAGGLE_DATASETS}
        to_download = [name_to_slug[n] for n in args.datasets if n in name_to_slug]
        names = [n for n in args.datasets if n in name_to_slug]

    if not to_download:
        print("No valid datasets. Use: ham10000, ham10000_isic, melanoma10k, or all", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["kaggle", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print(
            "Kaggle CLI not found. Install: pip install kaggle\n"
            "Then add API key from https://www.kaggle.com/settings (Create New Token)\n"
            "Save kaggle.json to %USERPROFILE%\\.kaggle\\ (Windows) or ~/.kaggle/ (Linux/Mac).",
            file=sys.stderr,
        )
        sys.exit(1)

    for slug, name in zip(to_download, names):
        dest = os.path.join(args.out_dir, name)
        os.makedirs(dest, exist_ok=True)
        print(f"Downloading {slug} -> {dest} ...")
        if run_kaggle(slug, dest, unzip=not args.no_unzip):
            print(f"  OK: {name}")
        else:
            print(f"  Skip: {name}")

    # Unzip any .zip left
    for name in names:
        dest = os.path.join(args.out_dir, name)
        for f in os.listdir(dest):
            if f.endswith(".zip"):
                path = os.path.join(dest, f)
                print(f"Unzipping {path} ...")
                try:
                    with zipfile.ZipFile(path, "r") as z:
                        z.extractall(dest)
                except Exception as e:
                    print(f"  Unzip error: {e}", file=sys.stderr)

    print("\nDone. Next: merge and train.")
    print("  python scripts/merge_datasets.py --data_dir", repr(args.out_dir))
    print("  python scripts/train_advanced.py --data_dir", repr(os.path.join(args.out_dir, "merged")))
