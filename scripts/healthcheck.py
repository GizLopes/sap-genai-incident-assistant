#!/usr/bin/env python3
"""Check local POC assets and, optionally, AWS connectivity."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Allow execution as: python scripts/healthcheck.py
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import settings


def item(name, ok, detail):
    return {"check": name, "ok": ok, "detail": detail}


def local_checks():
    checks = []

    required = [
        ROOT / "app" / "ui.py",
        ROOT / "app" / "assistant.py",
        ROOT / "app" / "faiss_retrieval.py",
        ROOT / "knowledge_base",
        ROOT / "mock_data",
        ROOT / "evaluation" / "dataset.json",
        ROOT / "data" / "faiss.index",
        ROOT / "data" / "faiss_metadata.json",
    ]

    for path in required:
        checks.append(
            item(
                f"path:{path.relative_to(ROOT)}",
                path.exists(),
                "available" if path.exists() else "missing",
            )
        )

    json_files = list((ROOT / "mock_data").glob("*.json")) + [
        ROOT / "evaluation" / "dataset.json",
        ROOT / "data" / "faiss_metadata.json",
    ]

    for path in json_files:
        try:
            with path.open(encoding="utf-8") as file:
                json.load(file)
            checks.append(item(f"json:{path.name}", True, "valid JSON"))
        except Exception as exc:
            checks.append(item(f"json:{path.name}", False, str(exc)))

    sap_docs = list((ROOT / "knowledge_base" / "sap_mm").glob("*.md"))
    checks.append(
        item(
            "sap_mm_knowledge_documents",
            bool(sap_docs),
            f"{len(sap_docs)} Markdown documents",
        )
    )

    policy_docs = list((ROOT / "knowledge_base" / "policies").glob("*.md"))
    checks.append(
        item(
            "policy_documents",
            bool(policy_docs),
            f"{len(policy_docs)} Markdown documents",
        )
    )

    try:
        import faiss

        index_path = ROOT / "data" / "faiss.index"
        if index_path.exists():
            index = faiss.read_index(str(index_path))
            checks.append(
                item(
                    "faiss_index",
                    index.ntotal > 0,
                    f"{index.ntotal} vectors, {index.d} dimensions",
                )
            )
    except ImportError:
        checks.append(item("faiss", False, "faiss is not installed"))
    except Exception as exc:
        checks.append(item("faiss_index", False, str(exc)))

    return checks


def aws_checks():
    try:
        import boto3
    except ImportError:
        return [item("boto3", False, "boto3 is not installed")]

    region = settings.aws_region
    model_id = settings.bedrock_model_id
    embedding_model_id = settings.embedding_model_id
    table = settings.dynamodb_table
    checks = []

    try:
        ident = boto3.client("sts", region_name=region).get_caller_identity()
        checks.append(
            item(
                "aws_credentials",
                True,
                f"account {ident.get('Account')}",
            )
        )
    except Exception as exc:
        return [item("aws_credentials", False, str(exc))]

    checks.append(
        item(
            "bedrock_model_configuration",
            bool(model_id),
            model_id or "Bedrock model ID not configured",
        )
    )

    checks.append(
        item(
            "embedding_model_configuration",
            bool(embedding_model_id),
            embedding_model_id or "Embedding model ID not configured",
        )
    )

    runtime = boto3.client("bedrock-runtime", region_name=region)

    if model_id:
        try:
            response = runtime.converse(
                modelId=model_id,
                system=[{"text": "Return only the word OK."}],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Health check."}],
                    }
                ],
                inferenceConfig={
                    "temperature": 0.0,
                    "maxTokens": 8,
                },
            )
            blocks = (
                response.get("output", {})
                .get("message", {})
                .get("content", [])
            )
            text_output = " ".join(
                block.get("text", "")
                for block in blocks
                if isinstance(block, dict)
            ).strip()

            checks.append(
                item(
                    "bedrock_llm_invocation",
                    bool(text_output),
                    f"{model_id}: invocation succeeded",
                )
            )
        except Exception as exc:
            checks.append(
                item(
                    "bedrock_llm_invocation",
                    False,
                    str(exc),
                )
            )

    if embedding_model_id:
        try:
            response = runtime.invoke_model(
                modelId=embedding_model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "inputText": "SAP MM health check",
                        "dimensions": 1024,
                        "normalize": True,
                    }
                ),
            )

            payload = json.loads(response["body"].read())
            embedding = payload.get("embedding", [])

            checks.append(
                item(
                    "titan_embedding_invocation",
                    len(embedding) == 1024,
                    (
                        f"{embedding_model_id}: "
                        f"{len(embedding)} dimensions"
                    ),
                )
            )
        except Exception as exc:
            checks.append(
                item(
                    "titan_embedding_invocation",
                    False,
                    str(exc),
                )
            )

    try:
        response = boto3.client(
            "dynamodb",
            region_name=region,
        ).describe_table(TableName=table)

        status = response["Table"]["TableStatus"]
        checks.append(
            item(
                "dynamodb_audit_table",
                status == "ACTIVE",
                f"{table}: {status}",
            )
        )
    except Exception as exc:
        checks.append(
            item(
                "dynamodb_audit_table",
                False,
                str(exc),
            )
        )

    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aws", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks = local_checks() + (aws_checks() if args.aws else [])
    healthy = all(check["ok"] for check in checks)

    if args.json:
        print(
            json.dumps(
                {"healthy": healthy, "checks": checks},
                indent=2,
            )
        )
    else:
        for check in checks:
            status = "PASS" if check["ok"] else "FAIL"
            print(
                f"[{status}] "
                f"{check['check']}: {check['detail']}"
            )
        print(
            "\nOverall:",
            "HEALTHY" if healthy else "UNHEALTHY",
        )

    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())