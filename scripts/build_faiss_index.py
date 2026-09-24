from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import faiss
import numpy as np

from integrations.embedding_client import TitanEmbeddingClient


DOCUMENT_IDS = {
    "purchase_requisition": "KB-MM-001",
    "purchase_order": "KB-MM-002",
    "release_strategy": "KB-MM-003",
    "goods_receipt": "KB-MM-004",
    "invoice_verification": "KB-MM-005",
    "price_variance": "KB-MM-006",
    "authorization_errors": "KB-MM-007",
    "mm_fi_integration": "KB-MM-008",
    "ai_scope": "KB-POL-001",
    "human_approval": "KB-POL-002",
    "escalation_rules": "KB-POL-003",
}


def title_from_markdown(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.replace("_", " ").title()


def chunk_markdown(text: str, max_chars: int = 1800) -> list[str]:
    """Small deterministic chunker that prefers Markdown section boundaries."""
    sections = re.split(r"(?=^##?\s)", text, flags=re.MULTILINE)
    chunks: list[str] = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= max_chars:
            chunks.append(section)
            continue

        paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = paragraph
            else:
                current = candidate
        if current:
            chunks.append(current)

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="knowledge_base")
    parser.add_argument("--index", default="data/faiss.index")
    parser.add_argument("--metadata", default="data/faiss_metadata.json")
    args = parser.parse_args()

    source_root = Path(args.source)
    files = sorted(
        p for p in source_root.rglob("*.md")
        if p.name.lower() != "readme.md"
    )

    if not files:
        raise SystemExit(f"No Markdown documents found under {source_root}")

    client = TitanEmbeddingClient()
    vectors: list[list[float]] = []
    metadata: list[dict] = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        title = title_from_markdown(text, file_path.stem)
        document_id = DOCUMENT_IDS.get(
            file_path.stem.lower(),
            f"KB-{file_path.stem.upper()}",
        )

        for chunk_number, chunk in enumerate(chunk_markdown(text), start=1):
            result = client.embed(chunk)
            vectors.append(result.embedding)
            metadata.append(
                {
                    "document_id": document_id,
                    "chunk_id": f"{document_id}-C{chunk_number:03d}",
                    "title": title,
                    "source": file_path.as_posix(),
                    "content": chunk,
                    "sha256": hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
                }
            )
            print(
                f"Embedded {document_id} chunk {chunk_number}: "
                f"{len(result.embedding)} dimensions"
            )

    matrix = np.asarray(vectors, dtype="float32")
    faiss.normalize_L2(matrix)

    # Inner product over normalized vectors = cosine similarity.
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)

    index_path = Path(args.index)
    metadata_path = Path(args.metadata)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(index_path))
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"FAISS index created: {index_path}")
    print(f"Metadata created: {metadata_path}")
    print(f"Vectors indexed: {index.ntotal}")
    print(f"Dimensions: {index.d}")


if __name__ == "__main__":
    main()
