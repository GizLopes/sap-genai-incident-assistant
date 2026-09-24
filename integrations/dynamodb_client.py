"""DynamoDB persistence adapter for immutable POC audit records."""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None
    BotoCoreError = ClientError = Exception

from app.config import settings


class DynamoDBAuditError(RuntimeError):
    pass


def _dynamodb_safe(value: Any) -> Any:
    """Convert floats recursively because DynamoDB does not accept Python float."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _dynamodb_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_dynamodb_safe(item) for item in value]
    return value


class DynamoDBAuditClient:
    def __init__(
        self,
        *,
        table_name: str | None = None,
        region: str | None = None,
        resource: Any | None = None,
    ) -> None:
        self.table_name = table_name or settings.dynamodb_table
        self.region = region or settings.aws_region

        if resource is not None:
            self.resource = resource
        else:
            if boto3 is None:
                raise DynamoDBAuditError(
                    "boto3 is required to use DynamoDB."
                )
            self.resource = boto3.resource(
                "dynamodb",
                region_name=self.region,
            )

        self.table = self.resource.Table(self.table_name)

    def put_audit_record(self, record: dict[str, Any]) -> None:
        if not record.get("request_id"):
            raise ValueError("Audit record requires request_id.")

        try:
            self.table.put_item(Item=_dynamodb_safe(record))
        except (ClientError, BotoCoreError) as exc:
            raise DynamoDBAuditError(
                "Unable to persist audit record."
            ) from exc

    def get_audit_record(self, request_id: str) -> dict[str, Any] | None:
        try:
            response = self.table.get_item(
                Key={"request_id": request_id},
                ConsistentRead=False,
            )
        except (ClientError, BotoCoreError) as exc:
            raise DynamoDBAuditError(
                "Unable to read audit record."
            ) from exc

        return response.get("Item")
