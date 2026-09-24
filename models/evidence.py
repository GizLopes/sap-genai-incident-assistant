"""Evidence domain models used by RAG and SAP mock retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EvidenceType(str, Enum):
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    SAP_RECORD = "SAP_RECORD"
    POLICY = "POLICY"
    USER_CONTEXT = "USER_CONTEXT"


@dataclass
class EvidenceItem:
    document_id: str
    title: str
    content: str
    source: str
    evidence_type: EvidenceType = EvidenceType.KNOWLEDGE_BASE
    retrieval_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.retrieval_score = max(0.0, min(1.0, float(self.retrieval_score)))

    @property
    def is_grounded(self) -> bool:
        return bool(self.content.strip() and self.source.strip())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_type"] = self.evidence_type.value
        return data
