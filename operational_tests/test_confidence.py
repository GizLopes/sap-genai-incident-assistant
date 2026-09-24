from app.confidence import calculate_confidence


def test_high_confidence_from_strong_inputs():
    result = calculate_confidence(
        retrieval_score=0.95,
        completeness_score=0.95,
        evidence_coverage=0.90,
        source_agreement=1.0,
    )
    assert result.level == "HIGH"
    assert result.score >= 0.80


def test_medium_confidence():
    result = calculate_confidence(
        retrieval_score=0.70,
        completeness_score=0.70,
        evidence_coverage=0.65,
        source_agreement=0.80,
    )
    assert result.level == "MEDIUM"
    assert 0.60 <= result.score < 0.80


def test_low_confidence():
    result = calculate_confidence(
        retrieval_score=0.30,
        completeness_score=0.40,
        evidence_coverage=0.20,
        source_agreement=0.50,
    )
    assert result.level == "LOW"
    assert result.score < 0.60


def test_confidence_is_application_calculated():
    result = calculate_confidence(
        retrieval_score=1.0,
        completeness_score=1.0,
        evidence_coverage=1.0,
        source_agreement=1.0,
    )
    assert result.score == 1.0
    assert result.level == "HIGH"
