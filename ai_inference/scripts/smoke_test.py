"""Quick test: build model + predict on a blank image (no trained weights)."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

import numpy as np
from PIL import Image

from src.inference import predict_pil

img = Image.fromarray(np.zeros((224, 224, 3), dtype=np.uint8) + 128)
r = predict_pil(img)
print("Smoke test OK:", r["condition"], r["confidence"], "model_ready=", r["model_ready"])
