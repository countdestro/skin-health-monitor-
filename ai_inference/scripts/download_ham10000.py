"""
Download HAM10000 from Kaggle (requires Kaggle API: pip install kaggle, then place
kaggle.json in ~/.kaggle/ or set KAGGLE_USERNAME/KAGGLE_KEY).

Usage:
  python scripts/download_ham10000.py --out_dir "C:/data/ham10000"

After download, you should have:
  out_dir/
    HAM10000_images_part1.zip (and part2)
    hmnist_28_28_L.csv  (optional, MNIST-style)
  Or use dataset: eliocordeiropereira/skin-cancer-the-ham10000-dataset (single zip with images + metadata)

Alternative (no Kaggle): download manually from
  https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000
  or https://www.kaggle.com/datasets/eliocordeiropereira/skin-cancer-the-ham10000-dataset
  Extract to --out_dir so you have: out_dir/images/*.jpg and out_dir/HAM10000_metadata.csv (or similar).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main():
    p = argparse.ArgumentParser(description="Download HAM10000 from Kaggle")
    p.add_argument("--out_dir", default=os.path.join(ROOT, "data", "ham10000"), help="Output directory")
    p.add_argument("--dataset", default="kmader/skin-cancer-mnist-ham10000", help="Kaggle dataset slug")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-p", args.out_dir, "--unzip", args.dataset],
            check=True,
            capture_output=True,
            text=True,
        )
        print("Downloaded and extracted to", args.out_dir)
    except FileNotFoundError:
        print(
            "Kaggle CLI not found. Install: pip install kaggle\n"
            "Then add API key: https://www.kaggle.com/settings -> Create New Token,\n"
            "save kaggle.json to %USERPROFILE%\\.kaggle\\ (Windows) or ~/.kaggle/ (Mac/Linux).",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Kaggle download failed:", e.stderr or e, file=sys.stderr)
        sys.exit(1)

    # If zip was not auto-unzipped
    for f in os.listdir(args.out_dir):
        if f.endswith(".zip"):
            path = os.path.join(args.out_dir, f)
            print("Unzipping", path)
            with zipfile.ZipFile(path, "r") as z:
                z.extractall(args.out_dir)
    print("Done. Next: python scripts/train_ham10000.py --data_dir", args.out_dir)


if __name__ == "__main__":
    main()
