from __future__ import annotations

import json
from dataclasses import dataclass
import boto3
from app.config import settings

@dataclass(frozen=True)
class EmbeddingResult:
    embedding: list[float]
    input_text_token_count: int | None = None

class TitanEmbeddingClient:
    def __init__(self, model_id: str | None = None, region_name: str | None = None) -> None:
        self.model_id = model_id or settings.embedding_model_id
        self.region_name = region_name or settings.aws_region
        self.client = boto3.client("bedrock-runtime", region_name=self.region_name)

    def embed(self, text: str) -> EmbeddingResult:
        normalized = " ".join(text.split()).strip()
        if not normalized:
            raise ValueError("Embedding input cannot be empty.")

        response = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": normalized, "normalize": True}),
        )
        payload = json.loads(response["body"].read())
        embedding = payload.get("embedding")
        if not embedding:
            raise RuntimeError("Titan returned no embedding.")
        return EmbeddingResult(
            embedding=embedding,
            input_text_token_count=payload.get("inputTextTokenCount"),
        )
