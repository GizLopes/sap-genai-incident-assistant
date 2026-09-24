"""Run the live evaluation suite against SAPIncidentAssistant."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.assistant import SAPIncidentAssistant
from metrics import calculate_all

DEFAULT_DATASET = ROOT / "evaluation" / "dataset.json"
DEFAULT_RESULTS = ROOT / "evidence" / "test_results.json"
DEFAULT_OUTPUT = ROOT / "evidence" / "evaluation_results.json"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_live(dataset: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assistant = SAPIncidentAssistant()
    results: list[dict[str, Any]] = []

    for case in dataset:
        started = time.perf_counter()
        response = assistant.analyze_ticket(case["ticket"])
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        result = response.to_dict()
        result["case_id"] = case["case_id"]
        result["ticket_id"] = case["ticket_id"]
        result["response_time_ms"] = elapsed_ms

        model: dict[str, Any] = {}
        try:
            client = getattr(assistant.audit_logger, "client", None)
            if client is not None:
                item = client.get_audit_record(response.request_id)
                if item:
                    model = item.get("model", {}) or {}
        except Exception:
            model = {}

        result["bedrock_latency_ms"] = model.get("latency_ms")
        result["input_tokens"] = model.get("input_tokens")
        result["output_tokens"] = model.get("output_tokens")
        result["total_tokens"] = model.get("total_tokens")
        result["model_id"] = model.get("model_id")
        results.append(result)

    return results


def build_records(
    dataset: list[dict[str, Any]],
    results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_ticket = {str(item.get("ticket_id")): item for item in results}
    return [
        {
            "case_id": case["case_id"],
            "ticket_id": case["ticket_id"],
            "category": case["category"],
            "expected": case["expected"],
            "actual": by_ticket.get(case["ticket_id"], {}),
        }
        for case in dataset
    ]


def per_case_summary(record: dict[str, Any]) -> dict[str, Any]:
    expected = record["expected"]
    actual = record["actual"]
    return {
        "case_id": record["case_id"],
        "ticket_id": record["ticket_id"],
        "category": record["category"],
        "expected_status": expected.get("status"),
        "actual_status": actual.get("status"),
        "status_match": str(expected.get("status", "")).lower()
        == str(actual.get("status", "")).lower(),
        "expected_process": expected.get("process"),
        "actual_process": actual.get("process"),
        "process_match": str(expected.get("process", "")).lower()
        == str(actual.get("process", "")).lower(),
        "expected_human_validation": expected.get("human_validation_required"),
        "actual_human_validation": actual.get("human_validation_required"),
        "response_time_ms": actual.get("response_time_ms"),
        "bedrock_latency_ms": actual.get("bedrock_latency_ms"),
        "total_tokens": actual.get("total_tokens"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--results-output", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()

    dataset = load_json(args.dataset)
    results = run_live(dataset)

    args.results_output.parent.mkdir(parents=True, exist_ok=True)
    args.results_output.write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    records = build_records(dataset, results)
    metrics = calculate_all(records)

    output = {
        "evaluation_mode": "LIVE",
        "dataset": str(args.dataset),
        "results_source": str(args.results_output),
        "case_count": len(records),
        "metrics": metrics,
        "cases": [per_case_summary(record) for record in records],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(metrics, indent=2))
    print(f"\nRaw results written to: {args.results_output}")
    print(f"Evaluation written to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())