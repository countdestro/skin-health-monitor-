"""
Health Insight Engine — Section 7.2 & 7.3.
Skin Health Score (SHS), severity tier, and rule-based recommendation engine.
"""
from typing import NamedTuple

# Condition class IDs per document (Section 6.2)
CONDITION_IDS = {
    0: "Healthy",
    1: "Acne",
    2: "Eczema",
    3: "Psoriasis",
    4: "Rosacea",
    5: "Pigmentation",
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
    if top_condition == "Healthy" and top_confidence >= 0.7:
        return min(100, int(base - (1 - top_confidence) * 20))
    # Penalty: higher confidence in a condition → lower score
    penalty = top_confidence * 45  # e.g. 0.9 conf → -40.5
    if top_condition == "Psoriasis":
        penalty *= 1.2
    if top_condition in ("Eczema", "Rosacea"):
        penalty *= 1.1
    score = base - penalty - (1 - quality_score) * 15
    return max(0, min(100, int(round(score))))


def get_severity_tier(score: int) -> tuple[str, str]:
    """Return (tier_label, hex_color). Section 7.2: 0–19 Severe, 20–39/40–59 Poor, 60–79 Fair, 80–100 Good."""
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
    Rule-based recommendation engine — Section 7.3.
    Returns list of { category, content, priority_rank }.
    """
    recs: list[dict] = []
    rank = 0

    def add(category: str, content: str):
        nonlocal rank
        rank += 1
        recs.append({"category": category, "content": content, "priority_rank": rank})

    # Skincare — any condition
    add("Skincare Routine", "Use a gentle, fragrance-free cleanser twice daily")
    if top_condition == "Acne":
        add("Skincare Routine", "Apply non-comedogenic SPF 30+ moisturiser in the morning")
    if top_condition in ("Eczema", "Psoriasis"):
        add("Skincare Routine", "Apply emollient cream within 3 minutes of showering")

    # Diet
    if top_condition == "Acne" and top_confidence > 0.5:
        add("Diet & Nutrition", "Reduce high-glycaemic foods; increase omega-3 intake")
    if top_condition == "Rosacea":
        add("Diet & Nutrition", "Avoid spicy foods, alcohol, and extreme temperatures")

    # Hydration
    add("Hydration", "Drink 2–3 litres of water daily; use a humidifier in dry environments")

    # Medical referral
    if score < 40 or (top_condition == "Psoriasis" and top_confidence > 0.6):
        add("Medical Referral", "Consult a certified dermatologist within 2 weeks")

    # Lifestyle
    if top_condition in ("Rosacea", "Eczema"):
        add("Lifestyle", "Manage stress: consider mindfulness or yoga to reduce flare-ups")

    return recs
