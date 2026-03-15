"""
Health Insight Engine — Section 7.2 & 7.3.
Skin Health Score (SHS), severity tier, and rule-based recommendation engine.
Supports HAM10000 conditions (7 lesion types) and legacy 5-condition set.
"""
from typing import NamedTuple

# HAM10000 condition IDs (1–7) — matches Member 3 AI output
CONDITION_IDS = {
    0: "Unknown",
    1: "Actinic keratosis",
    2: "Basal cell carcinoma",
    3: "Benign keratosis",
    4: "Dermatofibroma",
    5: "Melanoma",
    6: "Melanocytic nevus",
    7: "Vascular lesion",
}

# Severity tiers and colours (Section 7.2)
SEVERITY_BANDS = [
    (80, 100, "Good", "#27AE60"),
    (60, 79, "Fair", "#F39C12"),
    (40, 59, "Poor", "#E74C3C"),
    (20, 39, "Poor", "#E74C3C"),
    (0, 19, "Severe", "#922B21"),
]


def compute_skin_health_score(
    top_condition: str,
    top_confidence: float,
    quality_score: float = 1.0,
    predictions: list[dict] | None = None,
) -> int:
    """
    Composite Skin Health Score 0–100.
    Base 100, subtract penalties for dominant condition confidence and severity.
    """
    base = 100.0
    # Benign / low concern
    if top_condition in ("Melanocytic nevus", "Dermatofibroma", "Benign keratosis") and top_confidence >= 0.7:
        return min(100, int(base - (1 - top_confidence) * 25))
    # High concern: melanoma, BCC — heavy penalty
    penalty = top_confidence * 50
    if top_condition == "Melanoma":
        penalty *= 1.4
    if top_condition == "Basal cell carcinoma":
        penalty *= 1.3
    if top_condition in ("Actinic keratosis", "Vascular lesion"):
        penalty *= 1.1
    score = base - penalty - (1 - quality_score) * 15
    return max(0, min(100, int(round(score))))


def get_severity_tier(score: int) -> tuple[str, str]:
    """Return (tier_label, hex_color)."""
    if score >= 80:
        return "Good", "#27AE60"
    if score >= 60:
        return "Fair", "#F39C12"
    if score >= 40:
        return "Poor", "#E74C3C"
    if score >= 20:
        return "Poor", "#E74C3C"
    return "Severe", "#922B21"


def get_recommendations(
    top_condition: str,
    top_confidence: float,
    score: int,
    predictions: list[dict],
) -> list[dict]:
    """
    Rule-based recommendation engine for HAM10000 conditions.
    Returns list of { category, content, priority_rank }.
    """
    recs: list[dict] = []
    rank = 0

    def add(category: str, content: str):
        nonlocal rank
        rank += 1
        recs.append({"category": category, "content": content, "priority_rank": rank})

    # Urgent: melanoma or BCC
    if top_condition == "Melanoma" and top_confidence > 0.3:
        add("Medical Referral", "Urgent: possible melanoma. See a dermatologist within 1–2 days for evaluation.")
    if top_condition == "Basal cell carcinoma" and top_confidence > 0.4:
        add("Medical Referral", "Possible basal cell carcinoma. Book a dermatology appointment within 2 weeks.")

    # Actinic keratosis — sun damage, precancerous
    if top_condition == "Actinic keratosis":
        add("Skincare Routine", "Use broad-spectrum SPF 50+ daily; avoid prolonged sun exposure.")
        add("Medical Referral", "Actinic keratosis can be precancerous. Have a dermatologist review.")

    # Benign keratosis
    if top_condition == "Benign keratosis":
        add("Skincare Routine", "Gentle cleansing; moisturise. No treatment required unless changing or symptomatic.")

    # Dermatofibroma — benign
    if top_condition == "Dermatofibroma":
        add("Skincare Routine", "Benign lesion; no action needed unless it changes or bothers you.")

    # Melanocytic nevus (mole)
    if top_condition == "Melanocytic nevus":
        add("Lifestyle", "Monitor for changes (asymmetry, border, colour, diameter). Use SPF when outdoors.")

    # Vascular lesion
    if top_condition == "Vascular lesion":
        add("Skincare Routine", "Usually benign (e.g. angioma). See a doctor if it bleeds or grows quickly.")

    # General
    add("Skincare Routine", "Use a gentle, fragrance-free cleanser and moisturiser.")
    add("Hydration", "Drink 2–3 litres of water daily; use a humidifier in dry environments.")

    # Lower score or high-confidence concerning finding
    if score < 40:
        add("Medical Referral", "Consult a certified dermatologist for a full skin check.")
    if top_condition == "Melanoma" and top_confidence > 0.5:
        add("Medical Referral", "Do not delay: melanoma requires prompt professional evaluation.")

    return recs
