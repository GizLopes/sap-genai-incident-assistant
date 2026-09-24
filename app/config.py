"""Central application configuration.

Environment variables are used for deploy-time settings so credentials and
environment-specific values are not committed to Git.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv(
        "APP_NAME",
        "SAP GenAI Incident Assistant",
    )
    app_version: str = os.getenv("APP_VERSION", "0.1.0")
    environment: str = os.getenv("APP_ENV", "development")

    # AWS
    aws_region: str = os.getenv(
        "AWS_REGION",
        "us-east-1",
    )

    # Generative AI - Amazon Bedrock
    # Cross-region inference profile validated in the AWS account.
    bedrock_model_id: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "us.anthropic.claude-sonnet-4-6",
    )

    # Embeddings - Amazon Titan Text Embeddings V2
    embedding_model_id: str = os.getenv(
        "EMBEDDING_MODEL_ID",
        "amazon.titan-embed-text-v2:0",
    )

    # Audit
    dynamodb_table: str = os.getenv(
        "DYNAMODB_TABLE",
        "sap-genai-assistant-audit",
    )

    # SAP
    sap_module: str = os.getenv(
        "SAP_MODULE",
        "MM",
    )

    # RAG / Grounding
    max_retrieval_results: int = int(
        os.getenv("MAX_RETRIEVAL_RESULTS", "5")
    )

    minimum_grounding_score: float = float(
        os.getenv("MINIMUM_GROUNDING_SCORE", "0.50")
    )

    # Feature flags
    use_mock_sap: bool = _as_bool(
        os.getenv("USE_MOCK_SAP"),
        default=True,
    )

    enable_audit_logging: bool = _as_bool(
        os.getenv("ENABLE_AUDIT_LOGGING"),
        default=True,
    )

    debug: bool = _as_bool(
        os.getenv("DEBUG"),
        default=False,
    )

settings = Settings()