from app.hitl import evaluate_hitl


def test_po_release_requires_human():
    result = evaluate_hitl(
        requested_action="release_purchase_order",
        confidence_level="HIGH",
        has_evidence=True,
        conflicting_evidence=False,
    )
    assert result.human_validation_required is True


def test_financial_posting_requires_human():
    result = evaluate_hitl(
        requested_action="execute_financial_posting",
        confidence_level="HIGH",
        has_evidence=True,
        conflicting_evidence=False,
    )
    assert result.human_validation_required is True


def test_conflicting_evidence_requires_human():
    result = evaluate_hitl(
        requested_action=None,
        confidence_level="MEDIUM",
        has_evidence=True,
        conflicting_evidence=True,
    )
    assert result.human_validation_required is True


def test_grounded_read_only_recommendation_can_continue():
    result = evaluate_hitl(
        requested_action=None,
        confidence_level="HIGH",
        has_evidence=True,
        conflicting_evidence=False,
    )
    assert result.human_validation_required is False


def test_authorization_process_requires_human_even_with_grounded_evidence():
    result = evaluate_hitl(
        requested_action=None,
        confidence_level="MEDIUM",
        has_evidence=True,
        conflicting_evidence=False,
        process="Authorization",
    )

    assert result.human_validation_required is True
    assert result.allowed_ai_action == (
        "PROVIDE_GROUNDED_RECOMMENDATION_WITH_HUMAN_VALIDATION"
    )


def test_grounded_non_authorization_read_only_recommendation_can_continue():
    result = evaluate_hitl(
        requested_action=None,
        confidence_level="HIGH",
        has_evidence=True,
        conflicting_evidence=False,
        process="Invoice Verification",
    )

    assert result.human_validation_required is False

