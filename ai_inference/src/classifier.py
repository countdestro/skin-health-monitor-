"""
Skin lesion classifier: EfficientNetB0 (default) or MobileNetV2 backbone.
Supports HAM10000 (7 classes). Use EfficientNet for best accuracy.
"""

from __future__ import annotations

import os
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
    from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
except ImportError as e:
    raise ImportError("Install tensorflow: pip install tensorflow") from e

from .dataset_config import HAM10000_CLASSES

SKIN_CONDITIONS = HAM10000_CLASSES

IMG_SIZE = (224, 224)

# Which backbone to use (set SKIN_BACKBONE=efficientnetb0 or mobilenetv2)
BACKBONE_ENV = os.environ.get("SKIN_BACKBONE", "efficientnetb0").lower()


def _get_preprocess(backbone: str):
    if backbone == "efficientnetb0":
        return efficientnet_preprocess
    return mobilenet_preprocess


def build_model(
    num_classes: int | None = None,
    trainable_base: bool = False,
    dropout: float = 0.3,
    backbone: str | None = None,
) -> keras.Model:
    """
    Build classifier. Default: EfficientNetB0 for best accuracy.
    Use backbone="mobilenetv2" for faster, lighter model.
    """
    backbone = (backbone or BACKBONE_ENV).lower()
    num_classes = num_classes or len(SKIN_CONDITIONS)

    if backbone == "efficientnetb0":
        base = keras.applications.EfficientNetB0(
            input_shape=(*IMG_SIZE, 3),
            include_top=False,
            weights="imagenet",
            pooling="avg",
        )
        lr = 1e-4 if not trainable_base else 5e-6
    else:
        base = keras.applications.MobileNetV2(
            input_shape=(*IMG_SIZE, 3),
            include_top=False,
            weights="imagenet",
            pooling="avg",
        )
        lr = 1e-4 if not trainable_base else 1e-5

    base.trainable = trainable_base

    inputs = keras.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.Dropout(dropout)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(dropout * 0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="skin_conditions")(x)

    name = f"skin_disease_{backbone}"
    model = keras.Model(inputs, outputs, name=name)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=lr),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def get_preprocess_fn(backbone: str | None = None):
    """Return the preprocessing function for the given backbone (for inference)."""
    return _get_preprocess(backbone or BACKBONE_ENV)


def preprocess_array(rgb: np.ndarray, backbone: str | None = None) -> np.ndarray:
    """rgb: HWC uint8 [0,255]. Returns batch (1,224,224,3) for model."""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("Expected RGB image shape (H, W, 3)")
    backbone = backbone or BACKBONE_ENV
    x = tf.image.resize(rgb, IMG_SIZE)
    x = tf.cast(x, tf.float32)
    preprocess_fn = _get_preprocess(backbone)
    x = preprocess_fn(x.numpy() if hasattr(x, "numpy") else np.asarray(x))
    return np.expand_dims(x, axis=0)
