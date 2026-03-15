"""
Train skin lesion classifier on HAM10000 (CSV + image folder or folder-per-class).
Supports: (1) CSV with columns image_id, dx and an images/ folder; (2) folder layout class_name/*.jpg.

Usage (CSV + images):
  python scripts/train_ham10000.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images

Usage (folder per class, after prepare_ham10000_folders.py):
  python scripts/train_ham10000.py --data_dir "C:/data/ham10000/train" --use_folders

Output: weights/skin_model.weights.h5 (copy to ai_inference/weights/ for the API).
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess

from src.classifier import build_model, IMG_SIZE
from src.dataset_config import DX_CODES, DX_TO_IDX, HAM10000_CLASSES

# For flow_from_dataframe: use dx (string) as label so order matches DX_CODES
CLASS_MODE_ORDER = DX_CODES  # categorical one-hot order


def train_from_dataframe(
    data_dir: str,
    csv_path: str,
    images_dir: str,
    batch_size: int = 32,
    epochs: int = 20,
    val_split: float = 0.2,
    seed: int = 42,
    out_path: str | None = None,
):
    """Train using CSV + image directory (flow_from_dataframe)."""
    csv_full = os.path.join(data_dir, csv_path) if not os.path.isabs(csv_path) else csv_path
    img_dir = os.path.join(data_dir, images_dir) if not os.path.isabs(images_dir) else images_dir
    if not os.path.isfile(csv_full):
        raise FileNotFoundError(f"CSV not found: {csv_full}")
    if not os.path.isdir(img_dir):
        raise FileNotFoundError(f"Images dir not found: {img_dir}")

    df = pd.read_csv(csv_full)
    # HAM10000 metadata often has 'image_id' and 'dx'; some use 'filename'
    id_col = "image_id" if "image_id" in df.columns else "filename"
    if id_col not in df.columns:
        id_col = df.columns[0]
    dx_col = "dx" if "dx" in df.columns else "label"
    if dx_col not in df.columns:
        dx_col = [c for c in df.columns if c != id_col][0]

    df = df[[id_col, dx_col]].dropna()
    df["dx"] = df[dx_col].astype(str).str.strip().str.lower()
    df = df[df["dx"].isin(DX_TO_IDX)]
    # Some CSVs have image_id without extension
    df["filename"] = df[id_col].astype(str)
    if not df["filename"].iloc[0].lower().endswith((".jpg", ".jpeg", ".png")):
        df["filename"] = df["filename"] + ".jpg"

    n = len(df)
    idx = df.index.tolist()
    tf.random.set_seed(seed)
    shuffled = tf.random.shuffle(idx).numpy()
    cut = int(n * (1 - val_split))
    train_idx = shuffled[:cut]
    val_idx = shuffled[cut:]
    train_df = df.loc[train_idx].copy()
    val_df = df.loc[val_idx].copy()

    train_gen = ImageDataGenerator(
        preprocessing_function=mobilenet_preprocess,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        shear_range=0.1,
        zoom_range=0.2,
        fill_mode="nearest",
    )
    val_gen = ImageDataGenerator(preprocessing_function=mobilenet_preprocess)

    # y_col="dx": labels are akiec, bcc, ...; class_names order = one-hot index order
    train_flow = train_gen.flow_from_dataframe(
        train_df,
        directory=img_dir,
        x_col="filename",
        y_col="dx",
        target_size=IMG_SIZE,
        batch_size=batch_size,
        class_mode="categorical",
        class_names=CLASS_MODE_ORDER,
        shuffle=True,
        seed=seed,
    )
    val_flow = val_gen.flow_from_dataframe(
        val_df,
        directory=img_dir,
        x_col="filename",
        y_col="dx",
        target_size=IMG_SIZE,
        batch_size=batch_size,
        class_mode="categorical",
        class_names=CLASS_MODE_ORDER,
        shuffle=False,
    )

    model = build_model(num_classes=len(HAM10000_CLASSES), trainable_base=False)
    out_path = out_path or os.path.join(ROOT, "weights", "skin_model.weights.h5")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    best = out_path.replace(".h5", "_best.h5") if out_path.endswith(".h5") else out_path + "_best.h5"

    model.fit(
        train_flow,
        validation_data=val_flow,
        epochs=epochs,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
            keras.callbacks.ModelCheckpoint(best, save_best_only=True, save_weights_only=True, monitor="val_accuracy"),
        ],
    )
    model.load_weights(best)
    model.save_weights(out_path)
    print("Saved:", out_path)
    return out_path


def train_from_folders(
    data_dir: str,
    batch_size: int = 32,
    epochs: int = 20,
    val_split: float = 0.2,
    seed: int = 42,
    out_path: str | None = None,
):
    """Train using folder-per-class layout (e.g. train/Actinic keratosis/*.jpg)."""
    from src.classifier import SKIN_CONDITIONS


    train_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=SKIN_CONDITIONS,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        validation_split=val_split,
        subset="training",
        seed=seed,
    )
    val_ds = keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="categorical",
        class_names=SKIN_CONDITIONS,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        validation_split=val_split,
        subset="validation",
        seed=seed,
    )
    norm = keras.applications.mobilenet_v2.preprocess_input

    def prep(x, y):
        return norm(tf.cast(x, tf.float32)), y

    train_ds = train_ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)

    model = build_model(num_classes=len(SKIN_CONDITIONS), trainable_base=False)
    out_path = out_path or os.path.join(ROOT, "weights", "skin_model.weights.h5")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    best = out_path.replace(".h5", "_best.h5") if out_path.endswith(".h5") else out_path + "_best.h5"

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
            keras.callbacks.ModelCheckpoint(best, save_best_only=True, save_weights_only=True, monitor="val_accuracy"),
        ],
    )
    model.load_weights(best)
    model.save_weights(out_path)
    print("Saved:", out_path)
    return out_path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, help="Root dir containing CSV + images/ or folder-per-class")
    p.add_argument("--csv", default="HAM10000_metadata.csv", help="Metadata CSV filename (relative to data_dir)")
    p.add_argument("--images_dir", default="images", help="Images subfolder name (relative to data_dir)")
    p.add_argument("--use_folders", action="store_true", help="Use folder-per-class layout instead of CSV")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--val_split", type=float, default=0.2)
    p.add_argument("--out", default=os.path.join(ROOT, "weights", "skin_model.weights.h5"))
    args = p.parse_args()

    if args.use_folders:
        train_from_folders(
            args.data_dir,
            batch_size=args.batch_size,
            epochs=args.epochs,
            val_split=args.val_split,
            out_path=args.out,
        )
    else:
        train_from_dataframe(
            args.data_dir,
            csv_path=args.csv,
            images_dir=args.images_dir,
            batch_size=args.batch_size,
            epochs=args.epochs,
            val_split=args.val_split,
            out_path=args.out,
        )


if __name__ == "__main__":
    main()
