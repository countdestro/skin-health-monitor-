"""
Train a high-accuracy skin lesion classifier (EfficientNetB0, strong augmentation, class weights).
Use after downloading/merging datasets. Saves weights + config so the API loads the right backbone.

Usage (folder-per-class, recommended after merge):
  python scripts/train_advanced.py --data_dir "C:/data/skin_combined/merged/train" --use_folders --epochs 40

Usage (single HAM10000 CSV + images):
  python scripts/train_advanced.py --data_dir "C:/data/ham10000" --csv HAM10000_metadata.csv --images_dir images --epochs 40
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.efficientnet import preprocess_input as eff_preprocess

from src.classifier import build_model, IMG_SIZE, SKIN_CONDITIONS
from src.dataset_config import DX_CODES, DX_TO_IDX, HAM10000_CLASSES

# Use EfficientNet by default for best accuracy
os.environ.setdefault("SKIN_BACKBONE", "efficientnetb0")


def make_augmentation():
    return keras.Sequential([
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
        layers.RandomFlip("horizontal"),
        layers.RandomContrast(0.2),
        layers.RandomBrightness(0.2),
    ])


def train_from_folders(
    data_dir: str,
    batch_size: int = 32,
    epochs: int = 40,
    val_split: float = 0.2,
    seed: int = 42,
    out_path: str | None = None,
    use_class_weights: bool = True,
):
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

    def prep(x, y):
        x = tf.cast(x, tf.float32)
        x = eff_preprocess(x)
        return x, y

    aug = make_augmentation()

    def prep_train(x, y):
        x, y = prep(x, y)
        x = aug(x, training=True)
        return x, y

    train_ds = train_ds.map(prep_train, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)

    class_weights = None
    if use_class_weights:
        counts = {}
        for class_name in os.listdir(data_dir):
            sub = os.path.join(data_dir, class_name)
            if not os.path.isdir(sub):
                continue
            n = sum(1 for f in os.listdir(sub) if f.lower().endswith((".jpg", ".jpeg", ".png")))
            for i, c in enumerate(SKIN_CONDITIONS):
                if c == class_name:
                    counts[i] = n
                    break
        if counts and len(counts) == len(SKIN_CONDITIONS):
            total = sum(counts.values())
            class_weights = {i: total / (len(SKIN_CONDITIONS) * c) for i, c in counts.items()}
            print("Class weights:", class_weights)

    model = build_model(
        num_classes=len(SKIN_CONDITIONS),
        trainable_base=False,
        dropout=0.4,
        backbone="efficientnetb0",
    )
    out_path = out_path or os.path.join(ROOT, "weights", "skin_model.weights.h5")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    best = out_path.replace(".h5", "_best.h5") if out_path.endswith(".h5") else out_path + "_best.h5"

    callbacks = [
        keras.callbacks.EarlyStopping(
            patience=8,
            restore_best_weights=True,
            monitor="val_accuracy",
            min_delta=0.001,
        ),
        keras.callbacks.ModelCheckpoint(
            best,
            save_best_only=True,
            save_weights_only=True,
            monitor="val_accuracy",
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        class_weight=class_weights,
        callbacks=callbacks,
    )
    model.load_weights(best)
    model.save_weights(out_path)

    config_path = out_path.replace(".h5", "_config.json")
    with open(config_path, "w") as f:
        json.dump({"backbone": "efficientnetb0", "num_classes": len(SKIN_CONDITIONS)}, f)
    print("Saved weights:", out_path, "and config:", config_path)
    return out_path


def train_from_csv(
    data_dir: str,
    csv_path: str,
    images_dir: str,
    batch_size: int = 32,
    epochs: int = 40,
    val_split: float = 0.2,
    seed: int = 42,
    out_path: str | None = None,
):
    import pandas as pd
    from tensorflow.keras.preprocessing.image import ImageDataGenerator

    csv_full = os.path.join(data_dir, csv_path) if not os.path.isabs(csv_path) else csv_path
    img_dir = os.path.join(data_dir, images_dir) if not os.path.isabs(images_dir) else images_dir
    df = pd.read_csv(csv_full)
    id_col = "image_id" if "image_id" in df.columns else "filename"
    dx_col = "dx" if "dx" in df.columns else "label"
    df["dx"] = df[dx_col].astype(str).str.strip().str.lower()
    df = df[df["dx"].isin(DX_TO_IDX)]
    df["filename"] = df[id_col].astype(str)
    if not df["filename"].iloc[0].lower().endswith((".jpg", ".jpeg", ".png")):
        df["filename"] = df["filename"] + ".jpg"
    n = len(df)
    idx = tf.random.shuffle(df.index.values).numpy()
    cut = int(n * (1 - val_split))
    train_df = df.iloc[idx[:cut]]
    val_df = df.iloc[idx[cut:]]

    train_gen = ImageDataGenerator(
        preprocessing_function=eff_preprocess,
        rotation_range=25,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        shear_range=0.15,
        zoom_range=0.25,
        brightness_range=[0.8, 1.2],
        fill_mode="reflect",
    )
    val_gen = ImageDataGenerator(preprocessing_function=eff_preprocess)

    train_flow = train_gen.flow_from_dataframe(
        train_df,
        directory=img_dir,
        x_col="filename",
        y_col="dx",
        target_size=IMG_SIZE,
        batch_size=batch_size,
        class_mode="categorical",
        class_names=DX_CODES,
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
        class_names=DX_CODES,
        shuffle=False,
    )

    class_weights = None
    if train_flow.classes is not None:
        from sklearn.utils.class_weight import compute_class_weight
        import numpy as np
        uniq = np.unique(train_flow.classes)
        weights = compute_class_weight(
            "balanced",
            classes=uniq,
            y=train_flow.classes,
        )
        class_weights = dict(zip(uniq, weights))
        print("Class weights:", class_weights)

    model = build_model(num_classes=len(HAM10000_CLASSES), trainable_base=False, dropout=0.4, backbone="efficientnetb0")
    out_path = out_path or os.path.join(ROOT, "weights", "skin_model.weights.h5")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    best = out_path.replace(".h5", "_best.h5") if out_path.endswith(".h5") else out_path + "_best.h5"

    model.fit(
        train_flow,
        validation_data=val_flow,
        epochs=epochs,
        class_weight=class_weights,
        callbacks=[
            keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor="val_accuracy"),
            keras.callbacks.ModelCheckpoint(best, save_best_only=True, save_weights_only=True, monitor="val_accuracy"),
            keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7),
        ],
    )
    model.load_weights(best)
    model.save_weights(out_path)
    config_path = out_path.replace(".h5", "_config.json")
    with open(config_path, "w") as f:
        json.dump({"backbone": "efficientnetb0", "num_classes": len(HAM10000_CLASSES)}, f)
    print("Saved:", out_path, "and", config_path)
    return out_path


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True)
    p.add_argument("--csv", default="HAM10000_metadata.csv")
    p.add_argument("--images_dir", default="images")
    p.add_argument("--use_folders", action="store_true")
    p.add_argument("--epochs", type=int, default=40)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--val_split", type=float, default=0.2)
    p.add_argument("--out", default=os.path.join(ROOT, "weights", "skin_model.weights.h5"))
    p.add_argument("--no_class_weights", action="store_true", help="Disable class weighting")
    args = p.parse_args()

    if args.use_folders:
        train_from_folders(
            args.data_dir,
            batch_size=args.batch_size,
            epochs=args.epochs,
            val_split=args.val_split,
            out_path=args.out,
            use_class_weights=not args.no_class_weights,
        )
    else:
        train_from_csv(
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
