"""Scope and safety guard for the SAP MM POC."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re


SUPPORTED_PATTERNS = (
    r"\bsap\b",
    r"\bmm\b",
    r"\bpo\b",
    r"\bpr\b",
    r"\bpurchase order\b",
    r"\bpurchase requisition\b",
    r"\bpurchasing\b",
    r"\bbuyer\b",
    r"\bpedido de compra\b",
    r"\brequisi[cç][aã]o\b",
    r"\bmigo\b",
    r"\bmiro\b",
    r"\bme2[1238]n\b",
    r"\bme5[12]n\b",
    r"\binvoice\b",
    r"\bfatura\b",
    r"\bnota fiscal\b",
    r"\bgoods receipt\b",
    r"\brecebimento\b",
    r"\bentrada de mercadoria\b",
    r"\bvendor\b",
    r"\bfornecedor\b",
    r"\bmaterial\b",
    r"\brelease\b",
    r"\blibera[cç][aã]o\b",
    r"\bauthori[sz]ation\b",
    r"\bautoriza[cç][aã]o\b",
)

UNSUPPORTED_MODULE_PATTERNS = {
    "HR/HCM": r"\b(hr|hcm|human resources|recursos humanos|folha de pagamento)\b",
    "SD": r"\b(sd|sales order|ordem de venda)\b",
    "PP": r"\b(pp|production planning|ordem de produ[cç][aã]o)\b",
}


@dataclass
class ScopeDecision:
    in_scope: bool
    detected_scope: str
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)


def check_scope(ticket_text: str) -> ScopeDecision:
    text = ticket_text.lower().strip()

    for module, pattern in UNSUPPORTED_MODULE_PATTERNS.items():
        if re.search(pattern, text):
            return ScopeDecision(
                in_scope=False,
                detected_scope=module,
                reason=f"The POC is restricted to SAP MM; {module} is outside scope.",
            )

    if any(re.search(pattern, text) for pattern in SUPPORTED_PATTERNS):
        return ScopeDecision(
            in_scope=True,
            detected_scope="SAP MM",
            reason="The request contains SAP MM process indicators.",
        )

    return ScopeDecision(
        in_scope=False,
        detected_scope="Unknown",
        reason="No supported SAP MM process could be identified.",
    )