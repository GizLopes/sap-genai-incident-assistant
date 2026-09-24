"""Human-in-the-Loop decision controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass


CRITICAL_ACTIONS = {
    "release_purchase_order",
    "post_goods_receipt",
    "post_invoice",
    "change_configuration",
    "change_authorization",
    "change_master_data",
    "execute_financial_posting",
}

@dataclass
class HITLDecision:
    human_validation_required: bool
    reason: str | None
    allowed_ai_action: str

def evaluate_hitl(
    confidence_level: str,
    has_evidence: bool,
    requested_action: str | None = None,
    conflicting_evidence: bool = False,
    process: str | None = None,
) -> HITLDecision:
    action = (requested_action or "").strip().lower()
    normalized_process = (process or "").strip().lower()

    if action in CRITICAL_ACTIONS:
        return HITLDecision(
            human_validation_required=True,
            reason="The requested action changes SAP state or has operational risk.",
            allowed_ai_action="RECOMMEND_ONLY",
        )

    if conflicting_evidence:
        return HITLDecision(
            human_validation_required=True,
            reason="Supporting evidence is conflicting.",
            allowed_ai_action="SUMMARIZE_AND_ESCALATE",
        )

    if normalized_process == "authorization":
        return HITLDecision(
            human_validation_required=True,
            reason="Authorization-related incidents require human validation.",
            allowed_ai_action="PROVIDE_GROUNDED_RECOMMENDATION_WITH_HUMAN_VALIDATION",
        )

    if not has_evidence or confidence_level.upper() == "LOW":
        return HITLDecision(
            human_validation_required=True,
            reason="Evidence or confidence is insufficient for autonomous guidance.",
            allowed_ai_action="REQUEST_CONTEXT_OR_ESCALATE",
        )

    return HITLDecision(
        human_validation_required=False,
        reason=None,
        allowed_ai_action="PROVIDE_GROUNDED_RECOMMENDATION",
    )