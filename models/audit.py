"""Audit record model for traceability of GenAI decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditRecord:
    request_id: str
    ticket_id: str
    request: dict[str, Any]
    response: dict[str, Any]

    sources: list[dict[str, Any]] = field(default_factory=list)
    model_id: str | None = None
    prompt_version: str | None = None
    knowledge_base_id: str | None = None

    evidence_gate_decision: str | None = None
    confidence_level: str | None = None
    confidence_score: float | None = None
    human_validation_required: bool = False

    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "ticket_id": self.ticket_id,
            "request": self.request,
            "response": self.response,
            "sources": self.sources,
            "model_id": self.model_id,
            "prompt_version": self.prompt_version,
            "knowledge_base_id": self.knowledge_base_id,
            "evidence_gate_decision": self.evidence_gate_decision,
            "confidence_level": self.confidence_level,
            "confidence_score": self.confidence_score,
            "human_validation_required": self.human_validation_required,
            "metadata": self.metadata,
        }
