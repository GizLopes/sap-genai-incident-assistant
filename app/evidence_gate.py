"""Evidence-quality gate used before diagnostic recommendations are returned."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass
class EvidenceGateResult:
    passed: bool
    decision: str
    reasons: list[str]
    evidence_count: int
    best_score: float
    conflicting_evidence: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _get_score(item: Any) -> float:
    if hasattr(item, "retrieval_score"):
        return float(item.retrieval_score)
    if hasattr(item, "score"):
        return float(item.score)
    return 0.0


def evaluate_evidence(
    evidence: Iterable[Any],
    minimum_score: float = 0.65,
    minimum_sources: int = 1,
    conflicting_evidence: bool = False,
) -> EvidenceGateResult:
    items = list(evidence)
    best_score = max((_get_score(item) for item in items), default=0.0)
    reasons: list[str] = []

    if len(items) < minimum_sources:
        reasons.append("Insufficient number of supporting sources.")

    if best_score < minimum_score:
        reasons.append(
            f"Best retrieval score {best_score:.2f} is below "
            f"the required threshold {minimum_score:.2f}."
        )

    if conflicting_evidence:
        reasons.append(
            "Ticket or SAP context conflicts with the available evidence and requires human validation."
        )

    passed = not reasons

    if conflicting_evidence:
        decision = "HUMAN_VALIDATION_REQUIRED"
    elif not items:
        decision = "INSUFFICIENT_EVIDENCE"
    elif not passed:
        decision = "REQUEST_MORE_CONTEXT_OR_ESCALATE"
    else:
        decision = "GROUNDED_RESPONSE_ALLOWED"

    return EvidenceGateResult(
        passed=passed,
        decision=decision,
        reasons=reasons,
        evidence_count=len(items),
        best_score=round(best_score, 4),
        conflicting_evidence=conflicting_evidence,
    )