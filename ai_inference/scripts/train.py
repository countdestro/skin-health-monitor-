"""
Train skin classifier on folder dataset:
  data_root/
    Acne/
    Eczema/
    Psoriasis/
    Rosacea/
    Pigmentation/
Each folder contains images (jpg/png). Uses HAM10000-style mapping if you remap classes to these 5 names.

Usage:
  python scripts/train.py --data_dir "C:/data/skin" --epochs 10 --out weights/skin_model.keras
"""

from __future__ import annotations

import argparse
import os
import sys

# Project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tensorflow as tf
from tensorflow import keras

from src.classifier import SKIN_CONDITIONS, build_model, IMG_SIZE


def make_datasets(data_dir: str, val_split: float = 0.2, batch_size: int = 16, seed: int = 42):
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
    return train_ds, val_ds


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, help="Folder with subfolders per class (Acne, Eczema, ...)")
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch_size", type=int, default=16)
    p.add_argument("--out", default=os.path.join(ROOT, "weights", "skin_model.weights.h5"))
    p.add_argument("--finetune", action="store_true", help="Unfreeze MobileNet for last epochs")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    train_ds, val_ds = make_datasets(args.data_dir, batch_size=args.batch_size)
    model = build_model(trainable_base=False)

    best_path = args.out.replace(".h5", "_best.h5") if args.out.endswith(".h5") else args.out + "_best"
    callbacks = [
        keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(
            best_path, save_best_only=True, save_weights_only=True, monitor="val_accuracy"
        ),
    ]

    model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)
    model.load_weights(best_path)

    if args.finetune:
        model = build_model(trainable_base=True, dropout=0.2)
        model.load_weights(best_path)
        model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=max(5, args.epochs // 2),
            callbacks=[
                keras.callbacks.ModelCheckpoint(
                    best_path, save_best_only=True, save_weights_only=True, monitor="val_accuracy"
                )
            ],
        )
        model.load_weights(best_path)

    model.save_weights(args.out)
    print("Saved:", args.out)


if __name__ == "__main__":
    main()
