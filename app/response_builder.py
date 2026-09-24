"""Builds the final user-facing response from controlled application outputs."""

from __future__ import annotations

from typing import Any

from .confidence import ConfidenceResult
from .hitl import HITLDecision
from .retrieval import Evidence


def build_response(
    *,
    request_id: str,
    process: str,
    summary: str,
    possible_causes: list[str],
    recommended_checks: list[str],
    missing_information: list[str],
    evidence: list[Evidence],
    confidence: ConfidenceResult,
    hitl: HITLDecision,
) -> dict[str, Any]:
    """Create a stable response contract consumed by the UI and audit logger."""
    return {
        "request_id": request_id,
        "sap_module": "MM",
        "process": process,
        "summary": summary,
        "missing_information": missing_information,
        "possible_causes": possible_causes if evidence else [],
        "recommended_checks": recommended_checks if evidence else [],
        "sources": [
            {
                "document_id": item.document_id,
                "title": item.title,
                "reference": item.source,
                "retrieval_score": item.score,
            }
            for item in evidence
        ],
        "confidence": confidence.level,
        "confidence_details": confidence.to_dict(),
        "human_validation_required": hitl.required,
        "human_validation_reason": hitl.reason,
        "ai_action": hitl.allowed_ai_action,
        "disclaimer": (
            "AI output is diagnostic guidance. SAP state-changing actions require "
            "authorized human execution."
        ),
    }
