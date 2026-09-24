from app.evidence_gate import evaluate_evidence
from models.evidence import EvidenceItem, EvidenceType


def _evidence(score=0.90, document_id="KB-MM-001"):
    return EvidenceItem(
        document_id=document_id,
        title="Test evidence",
        content="Grounded SAP MM evidence.",
        source="test",
        evidence_type=EvidenceType.KNOWLEDGE_BASE,
        retrieval_score=score,
        metadata={},
    )


def test_gate_allows_strong_grounded_evidence():
    result = evaluate_evidence(
        [_evidence(0.90)],
        minimum_score=0.65,
        minimum_sources=1,
    )
    assert result.passed is True
    assert result.decision == "GROUNDED_RESPONSE_ALLOWED"


def test_gate_rejects_missing_evidence():
    result = evaluate_evidence(
        [],
        minimum_score=0.65,
        minimum_sources=1,
    )
    assert result.passed is False
    assert result.decision in {
        "INSUFFICIENT_EVIDENCE",
        "HUMAN_VALIDATION_REQUIRED",
        "REQUEST_MORE_CONTEXT_OR_ESCALATE",
    }


def test_gate_rejects_conflicting_evidence():
    result = evaluate_evidence(
        [_evidence(0.95), _evidence(0.92, "KB-MM-002")],
        minimum_score=0.65,
        minimum_sources=1,
        conflicting_evidence=True,
    )
    assert result.passed is False
    assert result.conflicting_evidence is True
    assert result.decision == "HUMAN_VALIDATION_REQUIRED"