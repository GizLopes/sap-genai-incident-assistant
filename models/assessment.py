"""Structured assessment returned by the assistant pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .evidence import EvidenceItem


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AssessmentStatus(str, Enum):
    COMPLETED = "COMPLETED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    HUMAN_VALIDATION_REQUIRED = "HUMAN_VALIDATION_REQUIRED"


@dataclass
class Assessment:
    request_id: str
    status: AssessmentStatus
    sap_module: str
    process: str | None
    summary: str

    missing_information: list[str] = field(default_factory=list)
    possible_causes: list[str] = field(default_factory=list)
    recommended_checks: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)

    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_score: float = 0.0

    human_validation_required: bool = False
    human_validation_reason: str | None = None
    ai_action: str = "RECOMMEND_ONLY"

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.confidence_score = max(
            0.0, min(1.0, float(self.confidence_score))
        )

        # A response without evidence must never expose diagnostic causes as
        # grounded conclusions.
        if not self.evidence:
            self.possible_causes = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "sap_module": self.sap_module,
            "process": self.process,
            "summary": self.summary,
            "missing_information": self.missing_information,
            "possible_causes": self.possible_causes,
            "recommended_checks": self.recommended_checks,
            "evidence": [item.to_dict() for item in self.evidence],
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "human_validation_required": self.human_validation_required,
            "human_validation_reason": self.human_validation_reason,
            "ai_action": self.ai_action,
            "metadata": self.metadata,
        }
