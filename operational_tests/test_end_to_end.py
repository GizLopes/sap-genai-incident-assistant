from app.assistant import SAPIncidentAssistant
from app.policy_registry import (
    POLICY_AI_SCOPE,
    POLICY_ESCALATION,
    POLICY_HITL,
)


class FailingLLM:
    def converse_json(self, *args, **kwargs):
        raise AssertionError("LLM should not be invoked in this deterministic test.")


class GroundedRecommendationLLM:
    """Stub used when grounded analysis is allowed but execution remains human-controlled."""

    def converse_json(self, *args, **kwargs):
        payload = {
            "summary": (
                "The purchase order is pending release according to the supplied SAP context."
            ),
            "possible_causes": [
                "A release step may still be pending."
            ],
            "recommended_checks": [
                "Review the pending release status with an authorized SAP user."
            ],
            "missing_information": [],
        }

        class ModelResponse:
            model_id = "test-model"
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            latency_ms = 0
            stop_reason = "end_turn"

        return payload, ModelResponse()


def _source_ids(response):
    return {source["document_id"] for source in response.sources}


def test_policy_registry_has_canonical_ids():
    assert POLICY_AI_SCOPE.document_id == "POLICY-AI-001"
    assert POLICY_HITL.document_id == "POLICY-HITL-001"
    assert POLICY_ESCALATION.document_id == "POLICY-ESC-001"


def test_out_of_scope_stops_before_mm_diagnosis():
    assistant = SAPIncidentAssistant(llm_client=FailingLLM())
    response = assistant.analyze_ticket(
        "SAP SD sales order 7000012345 is blocked for delivery."
    )
    assert response.status == "OUT_OF_SCOPE"
    assert response.process is None
    assert response.human_validation_required is False
    assert "POLICY-AI-001" in _source_ids(response)


def test_po_release_execution_requires_hitl_policy():
    assistant = SAPIncidentAssistant(
        llm_client=GroundedRecommendationLLM()
    )
    response = assistant.analyze_ticket(
        "PO 4500012345 is pending release. "
        "Please release the purchase order so the buyer can continue."
    )
    assert response.status == "HUMAN_VALIDATION_REQUIRED"
    assert response.process == "Release Strategy"
    assert response.human_validation_required is True
    assert "POLICY-HITL-001" in _source_ids(response)
    assert "released successfully" not in response.summary.lower()
    assert "release completed" not in response.summary.lower()


def test_authorization_incident_requires_hitl_policy():
    assistant = SAPIncidentAssistant(llm_client=GroundedRecommendationLLM())
    response = assistant.analyze_ticket(
        "User USR-LIMITED-01 cannot release PO 4500012345. "
        "The user can display the PO but cannot perform the release."
    )
    assert response.status == "HUMAN_VALIDATION_REQUIRED"
    assert response.process == "Authorization"
    assert response.human_validation_required is True
    assert "KB-MM-007" in _source_ids(response)
    assert "POLICY-HITL-001" in _source_ids(response)


def test_conflicting_evidence_requires_escalation_policy():
    assistant = SAPIncidentAssistant(llm_client=FailingLLM())
    response = assistant.analyze_ticket(
        "Invoice 5100002002 is blocked, but a support note says "
        "there is no price difference for this invoice."
    )
    assert response.status == "HUMAN_VALIDATION_REQUIRED"
    assert response.process == "Invoice Verification"
    assert response.human_validation_required is True
    assert "POLICY-ESC-001" in _source_ids(response)