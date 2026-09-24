"""Application-level confidence calculation.

Confidence is derived from evidence and ticket completeness instead of asking
the LLM to invent a confidence percentage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ConfidenceResult:
    level: str
    score: float
    retrieval_score: float
    completeness_score: float
    evidence_coverage: float
    source_agreement: float

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_confidence(
    retrieval_score: float,
    completeness_score: float,
    evidence_coverage: float,
    source_agreement: float,
) -> ConfidenceResult:
    values = [
        retrieval_score,
        completeness_score,
        evidence_coverage,
        source_agreement,
    ]
    values = [max(0.0, min(1.0, float(value))) for value in values]

    # Retrieval and evidence coverage have the largest weight because this POC
    # prioritizes grounded diagnostic guidance.
    score = (
        values[0] * 0.35
        + values[1] * 0.20
        + values[2] * 0.30
        + values[3] * 0.15
    )

    if score >= 0.80:
        level = "HIGH"
    elif score >= 0.60:
        level = "MEDIUM"
    else:
        level = "LOW"

    return ConfidenceResult(
        level=level,
        score=round(score, 4),
        retrieval_score=values[0],
        completeness_score=values[1],
        evidence_coverage=values[2],
        source_agreement=values[3],
    )
