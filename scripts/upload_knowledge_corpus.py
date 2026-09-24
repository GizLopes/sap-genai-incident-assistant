#!/usr/bin/env python3
"""Upload the local SAP MM knowledge corpus to S3 and optionally start Bedrock KB ingestion."""
from __future__ import annotations
import argparse, hashlib, mimetypes, sys
from pathlib import Path
try:
    import boto3
except ImportError:
    boto3 = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "knowledge_base"

def checksum(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def documents(source):
    allowed = {".md", ".txt", ".pdf", ".html", ".htm", ".doc", ".docx", ".csv"}
    return [p for p in sorted(source.rglob("*")) if p.is_file() and p.suffix.lower() in allowed]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--bucket", required=True)
    p.add_argument("--prefix", default="sap-genai-assistant/knowledge_base")
    p.add_argument("--region", default="us-east-1")
    p.add_argument("--knowledge-base-id")
    p.add_argument("--data-source-id")
    p.add_argument("--sync", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    source = a.source.resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    docs = documents(source)
    if not docs:
        raise RuntimeError("No supported knowledge documents found.")
    if boto3 is None and not a.dry_run:
        raise RuntimeError("boto3 is required.")

    s3 = None if a.dry_run else boto3.client("s3", region_name=a.region)
    for path in docs:
        rel = path.relative_to(source).as_posix()
        key = f"{a.prefix.strip('/')}/{rel}" if a.prefix.strip("/") else rel
        print(f"{'[DRY RUN] ' if a.dry_run else ''}s3://{a.bucket}/{key}")
        if s3:
            s3.upload_file(str(path), a.bucket, key, ExtraArgs={
                "ContentType": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "Metadata": {"source-path": rel, "sha256": checksum(path)}
            })

    print(f"Documents processed: {len(docs)}")

    if a.sync:
        if a.dry_run:
            print("[DRY RUN] Knowledge Base ingestion skipped.")
        else:
            if not a.knowledge_base_id or not a.data_source_id:
                raise ValueError("--knowledge-base-id and --data-source-id are required with --sync.")
            client = boto3.client("bedrock-agent", region_name=a.region)
            r = client.start_ingestion_job(
                knowledgeBaseId=a.knowledge_base_id,
                dataSourceId=a.data_source_id,
                description="SAP GenAI Incident Assistant knowledge synchronization"
            )
            job = r["ingestionJob"]
            print(f"Ingestion job: {job['ingestionJobId']} ({job['status']})")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
