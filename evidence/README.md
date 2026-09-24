# Evidence

## Purpose

This directory stores test and evaluation evidence for the SAP GenAI Incident Assistant POC.

```text
evidence/
├── README.md
├── test_results.json
└── evaluation_results.json
```

## test_results.json

Contains structured baseline results for the eight core scenarios: grounded PO analysis, invoice variance, missing information, insufficient evidence, out-of-scope handling, mandatory HITL, authorization handling, and conflicting evidence.

The initial artifact is a deterministic repository baseline. It demonstrates the expected behavior encoded by the test and evaluation assets. It is not evidence of a live Amazon Bedrock invocation.

`response_time_ms` is therefore set to `0`.

## evaluation_results.json

Contains the metrics calculated against `evaluation/dataset.json`:

- Classification Accuracy
- Status Accuracy
- Grounded Answer Rate
- Citation Coverage
- Hallucination Rate
- Clarification Accuracy
- Escalation Accuracy
- Human Approval Compliance
- Average Response Time

## Evidence Flow

```text
Test Cases
  -> Assistant / Baseline Execution
  -> Structured Results
  -> test_results.json
  -> Evaluation Metrics
  -> evaluation_results.json
```

## Live Evidence

After deployment, replace or version the baseline results with outputs captured from the running application and rerun:

```bash
python evaluation/evaluate.py --results evidence/test_results.json
```

Live evidence should additionally capture model version, prompt version, Knowledge Base version, timestamps, latency, token usage, and cost where available.

## Hallucination Control

The evaluation dataset defines known forbidden claims, including invented tolerance thresholds, invented approvers, unsupported authorization guidance, autonomous execution claims, and arbitrary resolution of conflicting evidence.

The deterministic check is a regression mechanism and cannot detect every possible unsupported statement.

## HITL Evidence

The expected behavior preserves human control for PO/PR approval, Goods Receipt posting or reversal, invoice posting or release, financial postings, authorization changes, configuration changes, and master-data changes.

## Limitation

Passing this evidence set demonstrates expected behavior for the bounded technical-challenge scenarios. It does not establish general accuracy across all SAP MM incidents or production readiness.
