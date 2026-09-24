from pathlib import Path

from app.faiss_retrieval import FAISSKnowledgeRetriever


REPO_ROOT = Path(__file__).resolve().parents[1]


def _retriever():
    return FAISSKnowledgeRetriever(
        index_path=REPO_ROOT / "data" / "faiss.index",
        metadata_path=REPO_ROOT / "data" / "faiss_metadata.json",
    )


def test_faiss_retrieval_finds_invoice_variance_documents():
    retriever = _retriever()
    results = retriever.retrieve(
        "Invoice Verification. invoice blocked because invoice price differs "
        "from purchase order price",
        limit=5,
    )

    assert results
    ids = {item.document_id for item in results}
    assert "KB-MM-005" in ids
    assert "KB-MM-006" in ids


def test_faiss_retrieval_finds_authorization_document():
    retriever = _retriever()
    results = retriever.retrieve(
        "Authorization. User can display PO 4500012345 but cannot release "
        "the purchase order because of authorization.",
        limit=5,
    )

    assert results
    ids = {item.document_id for item in results}
    assert "KB-MM-007" in ids


def test_faiss_retrieval_respects_limit():
    retriever = _retriever()
    results = retriever.retrieve(
        "Release Strategy. purchase order release approval",
        limit=2,
    )
    assert len(results) <= 2


def test_faiss_retrieval_returns_runtime_evidence_shape():
    result = _retriever().retrieve(
        "Invoice Verification. blocked invoice price variance",
        limit=1,
    )[0]

    assert result.document_id.startswith("KB-MM-")
    assert result.source
    assert result.content
    assert 0.0 <= result.retrieval_score <= 1.0
