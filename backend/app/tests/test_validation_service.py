from app.services.validation_service import clamp_score, validate_emotion_analysis


def test_clamp_score_within_range():
    assert clamp_score(5.5) == 5.5


def test_clamp_score_above_ten():
    assert clamp_score(15.7) == 10.0


def test_clamp_score_below_zero():
    assert clamp_score(-3) == 0.0


def test_clamp_score_invalid_value_uses_default():
    assert clamp_score("not-a-number", default=3.0) == 3.0


def test_validate_emotion_analysis_clamps_scores():
    result = validate_emotion_analysis(
        {"stress_score": 99, "anxiety_score": -5, "detected_emotions": ["happy"]}
    )
    assert result["stress_score"] == 10.0
    assert result["anxiety_score"] == 0.0


def test_validate_emotion_analysis_normalizes_emotions():
    result = validate_emotion_analysis(
        {
            "stress_score": 4,
            "anxiety_score": 3,
            "detected_emotions": ["Happy", "HAPPY", "  calm  "],
            "analysis": "Test",
            "recommendation": "Rest",
        }
    )
    assert result["detected_emotions"] == ["happy", "calm"]


def test_validate_emotion_analysis_fills_missing_text_fields():
    result = validate_emotion_analysis(
        {"stress_score": 2, "anxiety_score": 1, "detected_emotions": []}
    )
    assert result["analysis"] == "Analysis unavailable."
    assert result["recommendation"] == "Consider rest and mindfulness exercises."
    assert result["detected_emotions"] == ["neutral"]
