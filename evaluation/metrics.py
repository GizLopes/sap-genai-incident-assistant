"""Deterministic evaluation metrics for the SAP GenAI Incident Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _response_text(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("summary", "message", "human_validation_reason"):
        parts.append(str(result.get(key, "")))

    for key in ("possible_causes", "recommended_checks", "missing_information"):
        value = result.get(key, [])
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parts.extend(str(v) for v in item.values())
                else:
                    parts.append(str(item))
    return " ".join(parts).lower()


def classification_accuracy(records: Iterable[dict[str, Any]]) -> float:
    records = list(records)
    if not records:
        return 0.0
    correct = sum(
        _norm(r["actual"].get("process")) == _norm(r["expected"].get("process"))
        for r in records
    )
    return correct / len(records)


def status_accuracy(records: Iterable[dict[str, Any]]) -> float:
    records = list(records)
    if not records:
        return 0.0
    correct = sum(
        _norm(r["actual"].get("status")) == _norm(r["expected"].get("status"))
        for r in records
    )
    return correct / len(records)


def escalation_accuracy(records: Iterable[dict[str, Any]]) -> float:
    records = list(records)
    if not records:
        return 0.0
    correct = sum(
        bool(r["actual"].get("human_validation_required"))
        == bool(r["expected"].get("human_validation_required"))
        for r in records
    )
    return correct / len(records)


def citation_coverage(records: Iterable[dict[str, Any]]) -> float:
    required_total = 0
    cited_total = 0

    for record in records:
        required = set(record["expected"].get("required_evidence_ids", []))
        actual_sources = record["actual"].get("sources", [])
        actual_ids = set()

        for source in actual_sources:
            if isinstance(source, dict):
                actual_ids.add(
                    str(
                        source.get("document_id")
                        or source.get("id")
                        or source.get("source_id")
                        or ""
                    )
                )
            else:
                actual_ids.add(str(source))

        required_total += len(required)
        cited_total += len(required.intersection(actual_ids))

    return cited_total / required_total if required_total else 1.0


def grounded_answer_rate(records: Iterable[dict[str, Any]]) -> float:
    records = list(records)
    if not records:
        return 0.0

    grounded = 0
    for record in records:
        expected = record["expected"]
        actual = record["actual"]
        required = set(expected.get("required_evidence_ids", []))

        if not required:
            if not actual.get("possible_causes"):
                grounded += 1
            continue

        sources = actual.get("sources", [])
        actual_ids = {
            str(s.get("document_id") or s.get("id") or s.get("source_id") or "")
            if isinstance(s, dict)
            else str(s)
            for s in sources
        }

        if required.intersection(actual_ids):
            grounded += 1

    return grounded / len(records)


def hallucination_rate(records: Iterable[dict[str, Any]]) -> float:
    records = list(records)
    if not records:
        return 0.0

    violating = 0
    for record in records:
        text = _response_text(record["actual"])
        forbidden = [
            _norm(claim)
            for claim in record["expected"].get("forbidden_claims", [])
        ]
        if any(claim and claim in text for claim in forbidden):
            violating += 1

    return violating / len(records)


def clarification_accuracy(records: Iterable[dict[str, Any]]) -> float:
    relevant = [
        r for r in records
        if r["expected"].get("required_questions")
    ]
    if not relevant:
        return 1.0

    passed = 0
    for record in relevant:
        text = _response_text(record["actual"])
        required = [_norm(q) for q in record["expected"]["required_questions"]]
        aliases = {
            "purchase order": ("purchase order", "pedido de compra", "po"),
            "error message": ("error message", "mensagem de erro", "erro exato"),
        }
        if all(
            any(alias in text for alias in aliases.get(q, (q,)))
            for q in required
        ):
            passed += 1
    return passed / len(relevant)


def human_approval_compliance(records: Iterable[dict[str, Any]]) -> float:
    relevant = [
        r for r in records
        if r["expected"].get("human_validation_required")
    ]
    if not relevant:
        return 1.0

    compliant = 0
    execution_terms = (
        "released successfully",
        "release completed",
        "posted successfully",
        "configuration changed",
        "role changed successfully",
    )

    for record in relevant:
        actual = record["actual"]
        text = _response_text(actual)
        if (
            actual.get("human_validation_required") is True
            and not any(term in text for term in execution_terms)
        ):
            compliant += 1

    return compliant / len(relevant)


def average_response_time_ms(records: Iterable[dict[str, Any]]) -> float:
    values = [
        float(r["actual"]["response_time_ms"])
        for r in records
        if r["actual"].get("response_time_ms") is not None
    ]
    return sum(values) / len(values) if values else 0.0


def average_bedrock_latency_ms(records: Iterable[dict[str, Any]]) -> float:
    values = [
        float(r["actual"]["bedrock_latency_ms"])
        for r in records
        if r["actual"].get("bedrock_latency_ms") is not None
    ]
    return sum(values) / len(values) if values else 0.0


def average_total_tokens(records: Iterable[dict[str, Any]]) -> float:
    values = [
        float(r["actual"]["total_tokens"])
        for r in records
        if r["actual"].get("total_tokens") is not None
    ]
    return sum(values) / len(values) if values else 0.0


def calculate_all(records: Iterable[dict[str, Any]]) -> dict[str, float]:
    records = list(records)
    return {
        "classification_accuracy": classification_accuracy(records),
        "status_accuracy": status_accuracy(records),
        "grounded_answer_rate": grounded_answer_rate(records),
        "citation_coverage": citation_coverage(records),
        "hallucination_rate": hallucination_rate(records),
        "clarification_accuracy": clarification_accuracy(records),
        "escalation_accuracy": escalation_accuracy(records),
        "human_approval_compliance": human_approval_compliance(records),
        "average_response_time_ms": average_response_time_ms(records),
        "average_bedrock_latency_ms": average_bedrock_latency_ms(records),
        "average_total_tokens": average_total_tokens(records),
    }