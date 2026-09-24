# Solution Decisions

## Objective

The prototype demonstrates a safe and grounded GenAI assistant for SAP MM support-ticket analysis. The solution prioritizes diagnostic quality, evidence traceability, bounded autonomy, and a clear path to production integration.

## Selected SAP Scope

The POC focuses on SAP Materials Management (MM), specifically:

- Purchase Requisition;
- Purchase Order;
- Release Strategy;
- Goods Receipt;
- Invoice Verification;
- purchasing authorization issues;
- MM/FI integration issues originating from the MM process.

A narrow functional boundary makes evaluation objective and reduces unsupported cross-module reasoning.

## Deployment Model

Amazon EC2 hosts the Streamlit UI and Python application.

This is appropriate for the technical challenge because the POC needs:

- an interactive UI;
- Python orchestration;
- AWS SDK access;
- deterministic control logic;
- a simple deployment model.

The POC does not require a distributed microservice architecture.

## LLM

Amazon Bedrock provides managed model inference.

The model is used for language interpretation and grounded diagnostic synthesis. Business controls remain in application code.

The exact Bedrock model identifier is configuration-driven and must be selected from models available in the target AWS account and Region at deployment time.

## RAG

Amazon Bedrock Knowledge Bases is the target managed retrieval layer.

Amazon S3 stores the controlled SAP MM knowledge corpus.

For local development, the repository includes a lightweight lexical retriever so grounding behavior can be exercised without requiring an AWS Knowledge Base for every test.

## SAP Data

The challenge does not require a real SAP connection.

The POC therefore uses a read-only SAP abstraction backed by deterministic JSON mock data.

This provides realistic PO, PR, GR, invoice, vendor, release-status, and user context while avoiding unsafe or unnecessary system integration.

## Confidence

The LLM does not declare authoritative confidence.

Application confidence is calculated from:

- retrieval quality;
- information completeness;
- evidence coverage;
- source agreement.

This makes the confidence mechanism explicit, testable, and independent from model self-assessment.

## Evidence Gate

Diagnostic generation is constrained by an Evidence Gate.

The gate checks whether evidence exists, whether retrieval quality is sufficient, and whether sources conflict.

When the evidence is inadequate, the application requests more context or escalates instead of forcing a diagnosis.

## Human-in-the-Loop

The AI is advisory.

Human authorization remains mandatory for SAP state-changing actions, including:

- PO/PR approval or release;
- Goods Receipt posting or reversal;
- invoice posting or release;
- financial postings;
- configuration changes;
- authorization changes;
- master-data changes.

## Multi-Agent Decision

A multi-agent architecture is intentionally excluded from the POC.

The workflow is bounded and sequential:

```text
Scope
-> Classification
-> Retrieval
-> Evidence Validation
-> Diagnostic Reasoning
-> HITL Decision
```

Multiple autonomous agents would add orchestration complexity, latency, cost, and additional failure modes without providing material value for this challenge.

## Logging

Basic request, response, evidence-reference, confidence, and HITL metadata can be stored in DynamoDB.

The audit design avoids requiring the model itself to remember prior decisions.

## Services Intentionally Excluded

The POC does not add services solely to increase architectural complexity.

Examples intentionally excluded unless a production requirement justifies them:

- Step Functions;
- AgentCore;
- API Gateway;
- Lambda orchestration;
- OpenSearch managed directly by the application;
- container orchestration;
- multi-region infrastructure.

## Design Principle

The architecture places intelligence in the model and authority in deterministic application controls and authorized humans.
