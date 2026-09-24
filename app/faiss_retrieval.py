from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from integrations.embedding_client import TitanEmbeddingClient
from models.evidence import EvidenceItem, EvidenceType


class FAISSKnowledgeRetriever:
    """Vector retriever backed by a local FAISS index and Titan embeddings."""

    def __init__(
        self,
        index_path: str = "data/faiss.index",
        metadata_path: str = "data/faiss_metadata.json",
        embedding_client: TitanEmbeddingClient | None = None,
    ) -> None:
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.embedding_client = embedding_client or TitanEmbeddingClient()

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}. "
                "Run scripts/build_faiss_index.py first."
            )
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"FAISS metadata not found: {self.metadata_path}")

        self.index = faiss.read_index(str(self.index_path))
        self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

        if self.index.ntotal != len(self.metadata):
            raise RuntimeError(
                "FAISS index and metadata are inconsistent: "
                f"{self.index.ntotal} vectors vs {len(self.metadata)} metadata records."
            )

    def retrieve(self, query: str, limit: int = 5) -> list[Evidence]:
        query = query.strip()
        if not query:
            return []

        result = self.embedding_client.embed(query)
        vector = np.asarray([result.embedding], dtype="float32")
        faiss.normalize_L2(vector)

        k = min(limit, self.index.ntotal)
        scores, indexes = self.index.search(vector, k)

        evidence: list[EvidenceItem] = []
        for score, idx in zip(scores[0], indexes[0]):
            if idx < 0:
                continue

            item = self.metadata[idx]
            evidence.append(
                EvidenceItem(
                    document_id=item["document_id"],
                    title=item["title"],
                    source=item["source"],
                    content=item["content"],
                    evidence_type=EvidenceType.KNOWLEDGE_BASE,
                    retrieval_score=max(0.0, min(1.0, float(score))),
                    metadata={
                        "chunk_id": item.get("chunk_id"),
                        "sha256": item.get("sha256"),
                        "retrieval_method": "FAISS_COSINE",
                    },
                )
            )

        return evidence
