"""Deterministic SAP MM ticket classification."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re


@dataclass
class ClassificationResult:
    module: str
    process: str
    intent: str
    matched_terms: list[str]
    requires_clarification: bool

    def to_dict(self) -> dict:
        return asdict(self)


PROCESS_TERMS = {
    "Purchase Requisition": {
        "requisição", "requisicao", "purchase requisition", "me51n", "me52n", "pr"
    },
    "Purchase Order": {
        "pedido de compra", "purchase order", "purchasing", "buyer",
        "me21n", "me22n", "po"
    },
    "Release Strategy": {
        "bloqueado", "bloqueada", "blocked", "pending release",
        "liberação", "liberacao", "release", "approval",
        "aprovação", "aprovacao", "me28"
    },
    "Goods Receipt": {
        "recebimento", "goods receipt", "migo", "gr", "entrada de mercadoria"
    },
    "Invoice Verification": {
        "nota fiscal", "invoice", "miro", "fatura", "invoice verification"
    },
    "Authorization": {
        "autorização", "autorizacao", "authorization", "sem permissão",
        "sem permissao", "not authorized", "cannot release", "cannot perform",
        "su53"
    },
    "MM/FI Integration": {
        "documento contábil", "documento contabil", "accounting document",
        "fi", "contabilização", "contabilizacao"
    },
}

INTENT_TERMS = {
    "Troubleshooting": {"erro", "error", "falha", "failed", "bloqueado", "blocked"},
    "Status Check": {"status", "situação", "situacao", "pendente", "pending"},
    "How-To": {"como", "how", "procedimento", "procedure"},
}

PROCESS_PRIORITY = {
    "Authorization": 6,
    "Release Strategy": 5,
    "Invoice Verification": 4,
    "Goods Receipt": 3,
    "MM/FI Integration": 2,
    "Purchase Requisition": 1,
    "Purchase Order": 0,
}


def _contains_term(text: str, term: str) -> bool:
    if len(term) <= 3 and term.isascii():
        return bool(re.search(rf"\b{re.escape(term)}\b", text))
    return term in text


def classify_ticket(ticket_text: str) -> ClassificationResult:
    text = ticket_text.lower().strip()
    matches: dict[str, list[str]] = {}

    for process, terms in PROCESS_TERMS.items():
        matched = sorted(term for term in terms if _contains_term(text, term))
        if matched:
            matches[process] = matched

    authorization_markers = (
        "cannot release", "cannot perform", "not authorized",
        "sem permissão", "sem permissao", "su53",
        "authorization", "autorização", "autorizacao",
    )
    invoice_markers = (
        "invoice", "invoice verification", "miro", "fatura", "nota fiscal",
    )
    explicit_release_markers = (
        "pending release", "release the purchase order", "release the po",
        "liberar o pedido", "libere o pedido", "liberação", "liberacao",
        "approval", "aprovação", "aprovacao", "me28",
    )
    blocked_markers = ("blocked", "bloqueado", "bloqueada")
    po_markers = ("purchase order", "pedido de compra", "po ")

    if any(marker in text for marker in authorization_markers):
        process = "Authorization"
    elif any(marker in text for marker in invoice_markers):
        process = "Invoice Verification"
    elif any(marker in text for marker in explicit_release_markers):
        process = "Release Strategy"
    elif (
        any(marker in text for marker in blocked_markers)
        and any(marker in text for marker in po_markers)
    ):
        process = "Release Strategy"
    elif matches:
        process = max(
            matches,
            key=lambda name: (len(matches[name]), PROCESS_PRIORITY.get(name, 0)),
        )
    else:
        process = "Unknown"

    matched_terms = matches.get(process, [])

    intent = "General Support"
    for candidate, terms in INTENT_TERMS.items():
        if any(_contains_term(text, term) for term in terms):
            intent = candidate
            break

    return ClassificationResult(
        module="MM",
        process=process,
        intent=intent,
        matched_terms=matched_terms,
        requires_clarification=process == "Unknown",
    )