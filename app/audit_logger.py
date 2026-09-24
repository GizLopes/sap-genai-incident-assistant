"""Audit logging for SAP GenAI assistant requests and responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from integrations.dynamodb_client import (
    DynamoDBAuditClient,
    DynamoDBAuditError,
)

SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "access_token",
    "authorization",
    "api_key",
    "aws_secret_access_key",
}


def _redact(value: Any) -> Any:
    """Recursively redact known sensitive fields."""

    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if key.lower() in SENSITIVE_KEYS
                else _redact(item)
            )
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_redact(item) for item in value]

    return value


class AuditLogger:
    """Persist immutable audit records in Amazon DynamoDB."""

    def __init__(
        self,
        client: DynamoDBAuditClient | None = None,
    ) -> None:
        self.client = client or DynamoDBAuditClient()

    def log(
        self,
        *,
        request_id: str,
        request: dict[str, Any],
        response: dict[str, Any],
        sources: list[dict[str, Any]] | None = None,
        model: dict[str, Any] | None = None,
    ) -> None:
        record = {
            "request_id": request_id,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "request": _redact(request),
            "response": _redact(response),
            "sources": _redact(sources or []),
            "model": _redact(model or {}),
        }

        self.client.put_audit_record(record)


class NullAuditLogger:
    """Drop-in logger used when audit persistence is disabled."""

    def log(self, **_: Any) -> None:
        return None