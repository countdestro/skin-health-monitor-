"""
CNN skin disease classifier: MobileNetV2 backbone + classification head.
Aligned with workflow: Acne, Eczema, Psoriasis, Rosacea, Pigmentation.
"""

from __future__ import annotations

import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
except ImportError as e:
    raise ImportError("Install tensorflow: pip install tensorflow") from e

# Must match training labels order
SKIN_CONDITIONS = [
    "Acne",
    "Eczema",
    "Psoriasis",
    "Rosacea",
    "Pigmentation",
]

IMG_SIZE = (224, 224)


def build_model(
    num_classes: int | None = None,
    trainable_base: bool = False,
    dropout: float = 0.3,
) -> keras.Model:
    """
    Processed image -> MobileNetV2 features -> Dense -> softmax over skin conditions.
    """
    num_classes = num_classes or len(SKIN_CONDITIONS)
    base = keras.applications.MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
        pooling="avg",
    )
    base.trainable = trainable_base

    inputs = keras.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = layers.Dropout(dropout)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(dropout * 0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="skin_conditions")(x)

    model = keras.Model(inputs, outputs, name="skin_disease_mobilenet_v2")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4 if not trainable_base else 1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def preprocess_array(rgb: np.ndarray) -> np.ndarray:
    """rgb: HWC uint8 or float [0,255]. Returns batch (1,224,224,3) for model."""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("Expected RGB image shape (H, W, 3)")
    x = tf.image.resize(rgb, IMG_SIZE)
    x = preprocess_input(x.numpy() if hasattr(x, "numpy") else np.asarray(x))
    return np.expand_dims(x, axis=0)
