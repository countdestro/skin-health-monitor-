"""
Dataset configuration for skin lesion classification.
HAM10000: 7 classes, 10k+ images — use for production-style training.
"""

# HAM10000 diagnosis codes (order must match training label indices)
DX_CODES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

# Human-readable names (same order as DX_CODES)
HAM10000_CLASSES = [
    "Actinic keratosis",
    "Basal cell carcinoma",
    "Benign keratosis",
    "Dermatofibroma",
    "Melanoma",
    "Melanocytic nevus",
    "Vascular lesion",
]

DX_TO_IDX = {dx: i for i, dx in enumerate(DX_CODES)}
IDX_TO_NAME = {i: name for i, name in enumerate(HAM10000_CLASSES)}


def dx_to_label(dx: str) -> int:
    """Map HAM10000 dx code to class index (0–6)."""
    return DX_TO_IDX.get(dx.lower(), 0)


def idx_to_display_name(idx: int) -> str:
    """Map class index to display name."""
    return HAM10000_CLASSES[idx] if 0 <= idx < len(HAM10000_CLASSES) else "Unknown"
