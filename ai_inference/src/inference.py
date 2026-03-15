"""Load weights and run disease prediction on processed images (from Member 2)."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

from .classifier import SKIN_CONDITIONS, build_model, preprocess_array

# Default path relative to project root
_DEFAULT_WEIGHTS = Path(__file__).resolve().parent.parent / "weights" / "skin_model.weights.h5"


_model = None
_weights_loaded = False


def _load_backbone_from_config(weights_path: Path) -> str | None:
    """If weights were saved with train_advanced, config specifies backbone."""
    config_path = weights_path.parent / (weights_path.stem + "_config.json")
    if not config_path.exists():
        config_path = weights_path.parent / "skin_model_config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f).get("backbone")
        except Exception:
            pass
    return None


def load_trained_weights(weights_path: str | Path | None = None) -> None:
    """Load fine-tuned weights. Uses saved config for backbone (e.g. efficientnetb0) if present."""
    global _model, _weights_loaded
    path = Path(weights_path or os.environ.get("SKIN_MODEL_WEIGHTS", _DEFAULT_WEIGHTS))
    backbone = _load_backbone_from_config(path)
    if backbone:
        os.environ["SKIN_BACKBONE"] = backbone
    _model = build_model()
    if path.is_file():
        _model.load_weights(path)
        _weights_loaded = True
    else:
        _weights_loaded = False


def _get_model():
    global _model
    if _model is None:
        load_trained_weights()
    return _model


def _pil_to_rgb(pil: Image.Image) -> np.ndarray:
    if pil.mode != "RGB":
        pil = pil.convert("RGB")
    return np.asarray(pil)


def predict_image_path(image_path: str | Path) -> dict:
    pil = Image.open(image_path)
    return predict_pil(pil)


def predict_image_bytes(data: bytes) -> dict:
    pil = Image.open(io.BytesIO(data))
    return predict_pil(pil)


def predict_pil(pil: Image.Image) -> dict:
    """
    Returns:
      condition: str
      confidence: float 0-100
      all_scores: list of {condition, probability}
      model_ready: bool (False if no trained weights)
    """
    model = _get_model()
    arr = _pil_to_rgb(pil)
    batch = preprocess_array(arr)
    probs = model.predict(batch, verbose=0)[0]
    idx = int(np.argmax(probs))
    condition = SKIN_CONDITIONS[idx]
    confidence = float(probs[idx] * 100.0)
    all_scores = [
        {"condition": c, "probability": float(p), "percent": float(p * 100.0)}
        for c, p in zip(SKIN_CONDITIONS, probs)
    ]
    all_scores.sort(key=lambda x: x["probability"], reverse=True)
    return {
        "condition": condition,
        "confidence": round(confidence, 2),
        "confidence_fraction": float(probs[idx]),
        "all_scores": all_scores,
        "model_ready": _weights_loaded,
        "disclaimer": (
            "Trained weights not found; output reflects ImageNet backbone only — not for clinical use."
            if not _weights_loaded
            else "For demonstration only — not a medical device."
        ),
    }
