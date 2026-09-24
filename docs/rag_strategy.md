# RAG Strategy

## Objective

RAG grounds SAP MM diagnostic reasoning in a controlled knowledge corpus instead of relying only on the LLM's pretrained knowledge.

## Knowledge Sources

The POC corpus contains two categories.

### SAP MM Knowledge

```text
KB-MM-001  Purchase Requisition
KB-MM-002  Purchase Order
KB-MM-003  Release Strategy
KB-MM-004  Goods Receipt
KB-MM-005  Invoice Verification
KB-MM-006  Price Variance
KB-MM-007  Authorization Errors
KB-MM-008  MM/FI Integration
```

### Control Policies

```text
POLICY-AI-001    AI Scope
POLICY-HITL-001  Human Approval
POLICY-ESC-001   Escalation Rules
```

## Separation of Knowledge and SAP State

The architecture deliberately distinguishes:

```text
Knowledge Base
= how the process should work

SAP Data
= what is happening to a specific business object
```

Example:

```text
Knowledge:
Invoice price variance may contribute to an invoice block.

SAP mock evidence:
PO unit price = 500 USD
Invoice unit price = 620 USD
Invoice status = BLOCKED
```

The model combines these evidence types without treating generic process documentation as proof of a specific system state.

## Retrieval Flow

```text
Ticket
-> Scope Classification
-> SAP Process Classification
-> Retrieval Query
-> Knowledge Base
-> Ranked Evidence
-> Evidence Gate
-> Grounded Analysis
```

## Retrieval Query

The retrieval query should include relevant ticket concepts and the classified process.

It should avoid adding unsupported assumptions to the query.

Example:

```text
Ticket:
Invoice 5100002002 is blocked and price differs from PO.

Process:
Invoice Verification

Query concepts:
invoice blocked
price difference
purchase order
invoice verification
```

## Managed Retrieval

The AWS deployment targets Amazon Bedrock Knowledge Bases over documents stored in Amazon S3.

The integration layer normalizes Bedrock retrieval results into a common evidence model.

This allows the rest of the application to remain independent from the retrieval provider.

## Local Retrieval

A lightweight lexical retriever is included for local development and operational tests.

It is not presented as equivalent to production semantic retrieval.

Its purpose is to:

- exercise grounding logic locally;
- support deterministic tests;
- reduce development dependency on AWS resources.

## Metadata

Knowledge documents use stable IDs and metadata such as:

```text
document_id
module
process
document_type
risk_level
requires_human_approval
```

Stable IDs allow citations and regression tests to reference documents independently from generated text.

## Evidence Gate

Retrieval does not automatically authorize generation.

Retrieved evidence is evaluated for:

- presence;
- score;
- source coverage;
- consistency.

Low-quality or conflicting retrieval can trigger clarification or human review.

## Citation Strategy

Diagnostic causes should carry evidence identifiers.

The final response exposes the source references used to support the recommendation.

A citation proves the origin of a statement. It does not prove that the statement is correct if the underlying source is incorrect.

## Corpus Governance

Production ingestion should define:

- approved source owners;
- document version;
- effective date;
- retention rules;
- access classification;
- review cadence;
- superseded-document handling.

Only authorized knowledge should enter the retrieval corpus.

## Retrieval Evaluation

Production evaluation should expand beyond end-answer metrics to include:

- retrieval recall;
- retrieval precision;
- relevance;
- source coverage;
- stale-document rate;
- conflicting-document detection.

## Limitations

The POC corpus is intentionally small.

It demonstrates the grounding mechanism and control strategy. It does not represent the complete SAP Help Portal, customer customizing, OSS Notes, or customer-specific operating procedures.
