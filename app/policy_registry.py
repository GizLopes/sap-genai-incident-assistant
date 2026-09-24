"""Deterministic policy registry for SAP GenAI assistant controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PolicyDefinition:
    document_id: str
    title: str
    source: str
    risk_level: str
    requires_human_approval: bool
    priority: str = "mandatory"

    def to_source(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "source": self.source,
            "score": 1.0,
        }


POLICY_AI_SCOPE = PolicyDefinition(
    document_id="POLICY-AI-001",
    title="AI Scope Policy",
    source="knowledge_base/policies/ai_scope.md",
    risk_level="HIGH",
    requires_human_approval=False,
)

POLICY_HITL = PolicyDefinition(
    document_id="POLICY-HITL-001",
    title="Human Approval Policy",
    source="knowledge_base/policies/human_approval.md",
    risk_level="CRITICAL",
    requires_human_approval=True,
)

POLICY_ESCALATION = PolicyDefinition(
    document_id="POLICY-ESC-001",
    title="Escalation Rules",
    source="knowledge_base/policies/escalation_rules.md",
    risk_level="HIGH",
    requires_human_approval=True,
)


def append_policy_source(
    sources: list[dict[str, Any]],
    policy: PolicyDefinition,
) -> list[dict[str, Any]]:
    """Append a deterministic policy citation once."""
    if not any(
        source.get("document_id") == policy.document_id
        for source in sources
    ):
        sources.append(policy.to_source())
    return sources