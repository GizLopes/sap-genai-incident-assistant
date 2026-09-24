"""Amazon Bedrock Runtime adapter.

The client uses the Bedrock Converse API and validates the response structure.
AWS credentials are resolved by boto3's standard credential provider chain and
are never stored in source code.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None
    BotoCoreError = ClientError = Exception

from app.config import settings


class BedrockClientError(RuntimeError):
    """Raised when Amazon Bedrock invocation or response validation fails."""


@dataclass(frozen=True)
class BedrockResponse:
    text: str
    model_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    stop_reason: str | None = None


class BedrockClient:
    def __init__(
        self,
        *,
        region: str | None = None,
        model_id: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.region = region or settings.aws_region
        self.model_id = model_id or settings.bedrock_model_id

        if client is not None:
            self.client = client
        else:
            if boto3 is None:
                raise BedrockClientError(
                    "boto3 is required to use Amazon Bedrock Runtime."
                )

            self.client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
            )

    def converse(
        self,
        *,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1200,
    ) -> BedrockResponse:
        user_message = user_message.strip()
        system_prompt = system_prompt.strip()

        if not user_message:
            raise ValueError("user_message cannot be empty.")

        if not system_prompt:
            raise ValueError("system_prompt cannot be empty.")

        started_at = time.perf_counter()

        try:
            response = self.client.converse(
                modelId=self.model_id,
                system=[
                    {
                        "text": system_prompt,
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": user_message,
                            }
                        ],
                    }
                ],
                inferenceConfig={
                    "temperature": temperature,
                    "maxTokens": max_tokens,
                },
            )

        except (ClientError, BotoCoreError) as exc:
            raise BedrockClientError(
                "Bedrock model invocation failed."
            ) from exc

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000
        )

        blocks = (
            response.get("output", {})
            .get("message", {})
            .get("content", [])
        )

        text = "\n".join(
            block.get("text", "")
            for block in blocks
            if isinstance(block, dict) and block.get("text")
        ).strip()

        if not text:
            raise BedrockClientError(
                "Bedrock returned no text content."
            )

        usage = response.get("usage", {})

        input_tokens = int(
            usage.get("inputTokens", 0)
        )
        output_tokens = int(
            usage.get("outputTokens", 0)
        )
        total_tokens = int(
            usage.get(
                "totalTokens",
                input_tokens + output_tokens,
            )
        )

        return BedrockResponse(
            text=text,
            model_id=self.model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            stop_reason=response.get("stopReason"),
        )

    def converse_json(
        self,
        *,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1200,
    ) -> tuple[dict[str, Any], BedrockResponse]:
        """Request structured JSON and tolerate harmless model wrappers."""

        structured_instruction = (
            f"{system_prompt.strip()}\n\n"
            "Return exactly one valid JSON object. "
            "Do not use Markdown fences. "
            "Do not include text before or after the JSON object."
        )

        result = self.converse(
            user_message=user_message,
            system_prompt=structured_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        payload = self._parse_json_object(result.text)
        return payload, result

    @staticmethod
    def _parse_json_object(text: str) -> dict[str, Any]:
        """Parse one JSON object while tolerating harmless Claude wrappers."""
        candidate = text.strip()

        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            payload = BedrockClient._extract_json_object(candidate)

        if not isinstance(payload, dict):
            raise BedrockClientError(
                "Bedrock structured response must be a JSON object."
            )

        return payload

    @staticmethod
    def _extract_json_object(text: str) -> dict[str, Any]:
        """Extract a single decodable JSON object from surrounding text."""
        decoder = json.JSONDecoder()

        for index, character in enumerate(text):
            if character != "{":
                continue

            try:
                payload, _ = decoder.raw_decode(text[index:])
            except json.JSONDecodeError:
                continue

            if isinstance(payload, dict):
                return payload

            raise BedrockClientError(
                "Bedrock structured response must be a JSON object."
            )

        raise BedrockClientError(
            "Bedrock response did not contain a valid JSON object."
        )