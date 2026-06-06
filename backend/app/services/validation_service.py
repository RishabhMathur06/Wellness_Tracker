import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

ALLOWED_EMOTIONS_MAX = 10
MAX_TEXT_FIELD_LEN = 500


def clamp_score(value: Any, default: float = 0.0) -> float:
    """Clamp AI score outputs to valid 0–10 range."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default
    return round(max(0.0, min(10.0, score)), 1)


def validate_emotion_analysis(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-process multimodal AI output to reduce hallucination impact.
    Enforces schema bounds and sanitizes free-text fields.
    """
    emotions = raw.get("detected_emotions", [])
    if not isinstance(emotions, list):
        emotions = []
    clean_emotions: List[str] = []
    for item in emotions[:ALLOWED_EMOTIONS_MAX]:
        label = str(item).strip().lower()[:40]
        if label and label not in clean_emotions:
            clean_emotions.append(label)

    analysis = str(raw.get("analysis", "")).strip()[:MAX_TEXT_FIELD_LEN]
    recommendation = str(raw.get("recommendation", "")).strip()[:MAX_TEXT_FIELD_LEN]

    if not analysis:
        analysis = "Analysis unavailable."
    if not recommendation:
        recommendation = "Consider rest and mindfulness exercises."

    validated = {
        "stress_score": clamp_score(raw.get("stress_score"), 5.0),
        "anxiety_score": clamp_score(raw.get("anxiety_score"), 5.0),
        "detected_emotions": clean_emotions or ["neutral"],
        "analysis": analysis,
        "recommendation": recommendation,
    }

    if validated != raw:
        logger.debug("Emotion analysis output was normalized/clamped")

    return validated
