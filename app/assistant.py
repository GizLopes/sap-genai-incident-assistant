"""Application orchestration for the SAP GenAI assistant."""

from __future__ import annotations
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from integrations.bedrock_client import BedrockClient, BedrockClientError

from .audit_logger import AuditLogger, NullAuditLogger
from .classification import classify_ticket
from .confidence import calculate_confidence
from .config import settings
from .evidence_gate import evaluate_evidence
from .faiss_retrieval import FAISSKnowledgeRetriever
from .hitl import evaluate_hitl
from .policy_registry import (
    POLICY_AI_SCOPE,
    POLICY_ESCALATION,
    POLICY_HITL,
    append_policy_source,
)
from .sap_mock import SAPMockClient, SAPObjectNotFoundError
from .scope_guard import check_scope


@dataclass
class AssistantResponse:
    request_id: str
    status: str
    sap_module: str
    process: str | None
    summary: str
    missing_information: list[str]
    possible_causes: list[str]
    recommended_checks: list[str]
    sources: list[dict[str, Any]]
    confidence: str
    human_validation_required: bool
    human_validation_reason: str | None
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SAPIncidentAssistant:
    """Coordinates grounded SAP MM ticket analysis."""

    def __init__(
        self,
        *,
        llm_client: BedrockClient | None = None,
    ) -> None:
        self.settings = settings
        self.retriever = FAISSKnowledgeRetriever(
            index_path="data/faiss.index",
            metadata_path="data/faiss_metadata.json",
        )
        self.sap = SAPMockClient("mock_data")
        self.llm = llm_client or BedrockClient()
        self.audit_logger = (
            AuditLogger()
            if self.settings.enable_audit_logging
            else NullAuditLogger()
        )
        self.system_prompt = self._load_prompt(
            "prompts/system_prompt.md"
        )
        self.grounded_answer_prompt = self._load_prompt(
            "prompts/grounded_answer.md"
        )

    def analyze_ticket(
        self,
        ticket_text: str,
    ) -> AssistantResponse:
        request_id = str(uuid4())
        ticket_text = ticket_text.strip()
        if not ticket_text:
            response = self._clarification_response(
                request_id,
                [
                    (
                        "Descreva o problema no SAP, a mensagem de erro "
                        "e o processo afetado."
                    )
                ],
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=None,
                response=response,
                sources=[],
                model_metadata=None,
            )
            return response
        if len(ticket_text) < 20:
            response = self._clarification_response(
                request_id,
                [
                    "Forneça mais detalhes sobre o problema.",
                    (
                        "Inclua a transação ou processo, número do documento "
                        "quando disponível e o erro ou comportamento observado."
                    ),
                ],
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=None,
                response=response,
                sources=[],
                model_metadata=None,
            )
            return response

        # 1. Scope
        scope = check_scope(ticket_text)
        if not scope.in_scope:
            response = AssistantResponse(
                request_id=request_id,
                status="OUT_OF_SCOPE",
                sap_module=self.settings.sap_module,
                process=None,
                summary=(
                    "A solicitação está fora do escopo SAP MM desta POC."
                ),
                missing_information=[],
                possible_causes=[],
                recommended_checks=[
                    (
                        "Encaminhe a solicitação para a equipe funcional "
                        "SAP responsável pelo processo."
                    )
                ],
                sources=[POLICY_AI_SCOPE.to_source()],
                confidence="LOW",
                human_validation_required=False,
                human_validation_reason=None,
                created_at=self._now(),
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=None,
                response=response,
                sources=response.sources,
                model_metadata=None,
            )
            return response

        # 2. Classification
        classification = classify_ticket(ticket_text)
        if classification.requires_clarification:
            response = self._clarification_response(
                request_id,
                [
                    (
                        "Identifique o processo ou transação SAP MM "
                        "afetado."
                    )
                ],
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=classification.process,
                response=response,
                sources=[],
                model_metadata=None,
            )
            return response

        # 2a. Required context gate
        if self._requires_context_clarification(
            ticket_text,
            classification.process,
        ):
            response = AssistantResponse(
                request_id=request_id,
                status="NEEDS_CLARIFICATION",
                sap_module=self.settings.sap_module,
                process=classification.process,
                summary="São necessárias informações adicionais antes da análise.",
                missing_information=[
                    "Informe o número do pedido de compra.",
                    "Informe a mensagem de erro exata exibida pelo SAP.",
                ],
                possible_causes=[],
                recommended_checks=[],
                sources=[],
                confidence="LOW",
                human_validation_required=False,
                human_validation_reason=None,
                created_at=self._now(),
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=classification.process,
                response=response,
                sources=[],
                model_metadata=None,
            )
            return response

        # 3. Read-only SAP context
        sap_context = self._get_sap_context(
            ticket_text,
            classification.process,
        )

        # 4. Grounded retrieval
        # Enrich the semantic query with the deterministic process
        # classification so FAISS prioritizes process-relevant evidence.
        retrieval_query = (
            f"{classification.process}. {ticket_text}"
            if classification.process
            else ticket_text
        )
        evidence = self.retriever.retrieve(
            query=retrieval_query,
            limit=self.settings.max_retrieval_results,
        )

        # 5. Evidence gate
        conflicting_evidence = self._detect_conflicting_evidence(
            ticket_text=ticket_text,
            process=classification.process,
            sap_context=sap_context,
        )
        evidence_gate = evaluate_evidence(
            evidence,
            minimum_score=self.settings.minimum_grounding_score,
            minimum_sources=1,
            conflicting_evidence=conflicting_evidence,
        )

        # 6. Application-calculated confidence
        retrieval_score = evidence_gate.best_score
        completeness_score = 1.0 if sap_context else 0.7
        evidence_coverage = (
            1.0
            if evidence_gate.passed
            else 0.5
        )
        source_agreement = (
            1.0
            if evidence
            and not evidence_gate.conflicting_evidence
            else 0.0
        )
        confidence = calculate_confidence(
            retrieval_score=retrieval_score,
            completeness_score=completeness_score,
            evidence_coverage=evidence_coverage,
            source_agreement=source_agreement,
        )

        # 7. Detect requests for state-changing actions
        requested_action = self._detect_requested_action(
            ticket_text
        )

        # 8. HITL decision
        hitl = evaluate_hitl(
            requested_action=requested_action,
            confidence_level=confidence.level,
            has_evidence=evidence_gate.passed,
            conflicting_evidence=evidence_gate.conflicting_evidence,
            process=classification.process,
        )

        # Sources remain controlled by the application.
        sources = [
            {
                "document_id": item.document_id,
                "title": item.title,
                "source": item.source,
                "score": item.retrieval_score,
            }
            for item in evidence
        ]

        # Policies are mandatory application controls, not FAISS retrieval results.
        if evidence_gate.conflicting_evidence:
            append_policy_source(sources, POLICY_ESCALATION)

        if requested_action is not None:
            append_policy_source(sources, POLICY_HITL)

        if classification.process == "Authorization":
            append_policy_source(sources, POLICY_HITL)

        # Conflicting evidence is escalated before any LLM recommendation.
        if evidence_gate.conflicting_evidence:
            response = AssistantResponse(
                request_id=request_id,
                status="HUMAN_VALIDATION_REQUIRED",
                sap_module=self.settings.sap_module,
                process=classification.process,
                summary=(
                    "Há conflito entre as informações do chamado e o estado "
                    "observado no contexto SAP. A divergência requer validação humana."
                ),
                missing_information=[
                    "Confirme a origem, data e documento de referência da informação conflitante."
                ],
                possible_causes=[],
                recommended_checks=[
                    "Compare a informação do chamado com os dados atuais do documento SAP.",
                    "Valide a divergência com um especialista SAP antes de qualquer ação.",
                ],
                sources=sources,
                confidence=confidence.level,
                human_validation_required=True,
                human_validation_reason="Conflicting evidence requires human validation.",
                created_at=self._now(),
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=classification.process,
                response=response,
                sources=sources,
                model_metadata=None,
            )
            return response

        # Do not invoke the LLM when evidence is insufficient.
        if not evidence_gate.passed:
            response = AssistantResponse(
                request_id=request_id,
                status=(
                    "HUMAN_VALIDATION_REQUIRED"
                    if (
                        requested_action is not None
                        or classification.process == "Authorization"
                    )
                    else evidence_gate.decision
                ),
                sap_module=self.settings.sap_module,
                process=classification.process,
                summary=(
                    "O processo SAP MM foi identificado, mas as "
                    "evidências disponíveis são insuficientes para "
                    "um diagnóstico fundamentado."
                ),
                missing_information=[
                    (
                        "Contexto adicional do documento SAP ou detalhes "
                        "específicos do erro."
                    )
                ],
                possible_causes=[],
                recommended_checks=[
                    (
                        "Forneça informações adicionais sobre o documento "
                        "SAP e o comportamento observado."
                    ),
                    (
                        "Encaminhe para um especialista SAP caso as "
                        "evidências permaneçam insuficientes."
                    ),
                ],
                sources=sources,
                confidence=confidence.level,
                human_validation_required=True,
                human_validation_reason=(
                    hitl.reason
                    if requested_action is not None
                    else (
                        "Authorization-related incident requires human validation "
                        "when evidence is insufficient."
                        if classification.process == "Authorization"
                        else "; ".join(evidence_gate.reasons)
                    )
                ),
                created_at=self._now(),
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=classification.process,
                response=response,
                sources=sources,
                model_metadata=None,
            )
            return response

        # 9. Claude Sonnet 4.6 grounded generation
        try:
            generated, model_metadata = (
                self._generate_grounded_response(
                    ticket_text=ticket_text,
                    process=classification.process,
                    sap_context=sap_context,
                    evidence=evidence,
                )
            )
        except BedrockClientError:
            response = AssistantResponse(
                request_id=request_id,
                status="MODEL_ERROR",
                sap_module=self.settings.sap_module,
                process=classification.process,
                summary=(
                    "As evidências foram recuperadas corretamente, "
                    "mas o modelo não conseguiu gerar uma resposta "
                    "estruturada válida."
                ),
                missing_information=[],
                possible_causes=[],
                recommended_checks=[
                    (
                        "Revise as evidências recuperadas e encaminhe "
                        "a análise para validação humana."
                    )
                ],
                sources=sources,
                confidence=confidence.level,
                human_validation_required=True,
                human_validation_reason=(
                    "Bedrock generation or structured response "
                    "validation failed."
                ),
                created_at=self._now(),
            )
            self._audit(
                request_id=request_id,
                ticket_text=ticket_text,
                process=classification.process,
                response=response,
                sources=sources,
                model_metadata=None,
            )
            return response
        status = (
            "HUMAN_VALIDATION_REQUIRED"
            if hitl.human_validation_required
            else "GROUNDED_RECOMMENDATION"
        )
        response = AssistantResponse(
            request_id=request_id,
            status=status,
            sap_module=self.settings.sap_module,
            process=classification.process,
            summary=generated["summary"],
            missing_information=generated[
                "missing_information"
            ],
            possible_causes=generated[
                "possible_causes"
            ],
            recommended_checks=generated[
                "recommended_checks"
            ],
            sources=sources,
            confidence=confidence.level,
            human_validation_required=(
                hitl.human_validation_required
            ),
            human_validation_reason=hitl.reason,
            created_at=self._now(),
        )

        # 10. Audit persistence
        self._audit(
            request_id=request_id,
            ticket_text=ticket_text,
            process=classification.process,
            response=response,
            sources=sources,
            model_metadata=model_metadata,
        )
        return response

    def _generate_grounded_response(
        self,
        *,
        ticket_text: str,
        process: str,
        sap_context: dict[str, Any] | None,
        evidence: list[Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Generate a grounded diagnostic using Claude via Bedrock."""
        evidence_payload = []
        for index, item in enumerate(
            evidence,
            start=1,
        ):
            evidence_payload.append(
                {
                    "source_number": index,
                    "document_id": item.document_id,
                    "title": item.title,
                    "source": item.source,
                    "retrieval_score": (
                        item.retrieval_score
                    ),
                    "content": item.content,
                }
            )
        context = {
            "ticket": ticket_text,
            "sap_module": self.settings.sap_module,
            "classified_process": process,
            "sap_context": sap_context,
            "retrieved_evidence": evidence_payload,
        }
        user_message = (
            f"{self.grounded_answer_prompt}\n\n"
            "INPUT DATA\n"
            f"{json.dumps(context, ensure_ascii=False, indent=2)}"
        )
        payload, model_response = (
            self.llm.converse_json(
                user_message=user_message,
                system_prompt=self.system_prompt,
                temperature=0.0,
                max_tokens=1200,
            )
        )
        validated_payload = (
            self._validate_grounded_payload(
                payload
            )
        )
        model_metadata = {
            "model_id": model_response.model_id,
            "input_tokens": (
                model_response.input_tokens
            ),
            "output_tokens": (
                model_response.output_tokens
            ),
            "total_tokens": (
                model_response.total_tokens
            ),
            "latency_ms": (
                model_response.latency_ms
            ),
            "stop_reason": (
                model_response.stop_reason
            ),
        }
        return (
            validated_payload,
            model_metadata,
        )

    @staticmethod

    def _validate_grounded_payload(
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Validate the JSON contract returned by the LLM."""
        required_fields = {
            "summary",
            "possible_causes",
            "recommended_checks",
            "missing_information",
        }
        missing_fields = (
            required_fields - payload.keys()
        )
        if missing_fields:
            raise BedrockClientError(
                (
                    "Bedrock structured response is "
                    "missing required fields: "
                )
                + ", ".join(
                    sorted(missing_fields)
                )
            )
        summary = payload.get("summary")
        if (
            not isinstance(summary, str)
            or not summary.strip()
        ):
            raise BedrockClientError(
                "Bedrock response contains an invalid summary."
            )
        list_fields = (
            "possible_causes",
            "recommended_checks",
            "missing_information",
        )
        for field_name in list_fields:
            value = payload.get(field_name)
            if not isinstance(value, list):
                raise BedrockClientError(
                    (
                        f"Bedrock response field "
                        f"'{field_name}' must be a list."
                    )
                )
            if not all(
                isinstance(item, str)
                for item in value
            ):
                raise BedrockClientError(
                    (
                        f"Bedrock response field "
                        f"'{field_name}' must contain "
                        "strings only."
                    )
                )
        return {
            "summary": summary.strip(),
            "possible_causes": [
                item.strip()
                for item in payload[
                    "possible_causes"
                ]
                if item.strip()
            ],
            "recommended_checks": [
                item.strip()
                for item in payload[
                    "recommended_checks"
                ]
                if item.strip()
            ],
            "missing_information": [
                item.strip()
                for item in payload[
                    "missing_information"
                ]
                if item.strip()
            ],
        }

    def _audit(
        self,
        *,
        request_id: str,
        ticket_text: str,
        process: str | None,
        response: AssistantResponse,
        sources: list[dict[str, Any]],
        model_metadata: dict[str, Any] | None,
    ) -> None:
        """Persist request, response, evidence and model telemetry."""
        self.audit_logger.log(
            request_id=request_id,
            request={
                "ticket": ticket_text,
                "sap_module": self.settings.sap_module,
                "process": process,
            },
            response=response.to_dict(),
            sources=sources,
            model=model_metadata or {},
        )

    def _get_sap_context(
        self,
        ticket_text: str,
        process: str,
    ) -> dict[str, Any] | None:
        numbers = re.findall(
            r"\b\d{8,12}\b",
            ticket_text,
        )
        if not numbers:
            return None
        try:
            if process in {
                "Purchase Order",
                "Release Strategy",
            }:
                return (
                    self.sap.get_purchase_order(
                        numbers[0]
                    )
                )
            if process == "Purchase Requisition":
                return (
                    self.sap.get_purchase_requisition(
                        numbers[0]
                    )
                )
            if process == "Invoice Verification":
                return self.sap.get_invoice(
                    numbers[0]
                )
            if process == "Goods Receipt":
                return (
                    self.sap.get_goods_receipt(
                        numbers[0]
                    )
                )
        except SAPObjectNotFoundError:
            return None
        return None

    @staticmethod
    def _requires_context_clarification(
        ticket_text: str,
        process: str,
    ) -> bool:
        if process != "Purchase Order":
            return False
        text = ticket_text.lower()
        has_document = bool(re.search(r"\b\d{8,12}\b", text))
        generic_error = "error" in text or "erro" in text
        return generic_error and not has_document

    @staticmethod
    def _detect_conflicting_evidence(
        *,
        ticket_text: str,
        process: str,
        sap_context: dict[str, Any] | None,
    ) -> bool:
        if process != "Invoice Verification" or not sap_context:
            return False

        text = ticket_text.lower()
        denies_price_difference = any(
            phrase in text
            for phrase in (
                "no price difference",
                "sem diferença de preço",
                "sem diferenca de preco",
                "não há diferença de preço",
                "nao ha diferenca de preco",
            )
        )
        if not denies_price_difference:
            return False

        po_price = sap_context.get("po_unit_price")
        invoice_price = sap_context.get("invoice_unit_price")
        return (
            po_price is not None
            and invoice_price is not None
            and po_price != invoice_price
        )

    @staticmethod

    def _detect_requested_action(
        ticket_text: str,
    ) -> str | None:
        text = ticket_text.lower()
        if (
            "release the purchase order" in text
            or "release the po" in text
            or "liberar o pedido" in text
            or "libere o pedido" in text
            or "libera o pedido" in text
        ):
            return "release_purchase_order"
        if (
            "post goods receipt" in text
            or "lançar entrada de mercadoria" in text
            or "registrar entrada de mercadoria" in text
        ):
            return "post_goods_receipt"
        if (
            "post invoice" in text
            or "lançar fatura" in text
            or "registrar fatura" in text
        ):
            return "post_invoice"
        return None

    def _clarification_response(
        self,
        request_id: str,
        missing: list[str],
    ) -> AssistantResponse:
        return AssistantResponse(
            request_id=request_id,
            status="NEEDS_CLARIFICATION",
            sap_module=self.settings.sap_module,
            process=None,
            summary=(
                "São necessárias informações adicionais "
                "antes da análise."
            ),
            missing_information=missing,
            possible_causes=[],
            recommended_checks=[],
            sources=[],
            confidence="LOW",
            human_validation_required=False,
            human_validation_reason=None,
            created_at=self._now(),
        )

    @staticmethod

    def _load_prompt(
        path: str,
    ) -> str:
        prompt_path = Path(path)
        if not prompt_path.exists():
            raise RuntimeError(
                f"Prompt file not found: {path}"
            )
        content = prompt_path.read_text(
            encoding="utf-8"
        ).strip()
        if not content:
            raise RuntimeError(
                f"Prompt file is empty: {path}"
            )
        return content

    @staticmethod

    def _now() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()