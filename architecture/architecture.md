# Architecture

## Overview

The SAP GenAI Incident Assistant is a bounded SAP MM diagnostic POC deployed as a lightweight application on Amazon EC2.

The design separates:

- user interaction;
- orchestration and deterministic control logic;
- LLM inference;
- embedding generation and vector retrieval;
- read-only SAP mock access;
- evidence and confidence controls;
- deterministic application policies;
- Human-in-the-Loop enforcement;
- audit and traceability.

## Logical Architecture

```text
User
  -> [submits SAP MM support ticket]
Streamlit UI on Amazon EC2
  -> [creates request]
Python Application Orchestrator
  -> [checks functional boundary]
Scope Guard
  -> [classifies SAP MM process and intent]
Classification
  -> [checks required context]
Completeness Check
  -> [reads ticket-related SAP objects]
Read-Only SAP Client
  -> [queries simulated records]
SAP Mock Data
  -> [provides PO, PR, GR, invoice, vendor and user context]

Application Orchestrator
  -> [builds process-aware retrieval query]
Amazon Titan Text Embeddings V2
  -> [creates normalized query embedding]
FAISS on Amazon EC2
  -> [searches local vector index]
SAP MM Evidence
  -> [returns ranked evidence]
Evidence Gate
  -> [validates score, sufficiency and consistency]
Confidence Engine
  -> [calculates deterministic confidence]
Application Policy Engine
  -> [applies AI scope, HITL and escalation rules]
Amazon Bedrock · Claude Sonnet 4.6
  -> [generates grounded structured analysis]
Response Builder
  -> [validates structured output and attaches controlled sources]
HITL Gate
  -> [returns recommendation or human-validation status]
Streamlit UI
  -> [displays analysis, evidence, confidence and HITL status]
User / SAP Specialist

Application Orchestrator
  -> [records request, response, sources and model telemetry]
Amazon DynamoDB
```

Knowledge preparation:

```text
Curated SAP MM Markdown Documents
  -> [source repository]
Amazon S3 / Repository Corpus
  -> [chunks documents]
Index Builder
  -> [embeds chunks]
Amazon Titan Text Embeddings V2
  -> [1024-dimensional normalized vectors]
FAISS Index on Amazon EC2
```

## AWS Components

### Amazon EC2

Hosts the POC application:

- Streamlit UI;
- Python orchestration;
- deterministic control logic;
- FAISS vector index;
- AWS SDK clients;
- SAP mock adapter.

EC2 was selected because it provides a simple environment for an interactive POC while keeping the application components together.

### Amazon Bedrock

Provides access to the models used by the POC.

Claude Sonnet 4.6 is invoked through the Bedrock Converse API for grounded analysis and structured response generation.

```text
us.anthropic.claude-sonnet-4-6
```

Amazon Titan Text Embeddings V2 generates embeddings for the SAP MM corpus and runtime retrieval queries.

```text
amazon.titan-embed-text-v2:0
```

The application supplies controlled context to Claude. The model does not receive authority to execute SAP changes, assign confidence, authorize actions, or create source references.

### FAISS

FAISS provides local vector retrieval on Amazon EC2.

The current implementation uses:

- 1024-dimensional Titan embeddings;
- normalized vectors;
- inner-product similarity;
- ranked evidence retrieval;
- application grounding threshold of `0.50`.

The threshold is a POC control value and requires calibration against a larger production evaluation set.

### Amazon S3

Stores or distributes the curated SAP MM knowledge documents used to build the vector index.

The functional knowledge corpus is separated from mandatory application policies. Policy enforcement does not depend on semantic retrieval.

### Amazon DynamoDB

Stores audit records including, where available:

- request ID;
- request metadata;
- response;
- evidence and policy source references;
- model identifier;
- input, output and total token counts;
- Bedrock latency;
- stop reason;
- confidence;
- Evidence Gate decision;
- HITL decision.

Sensitive audit fields are redacted before persistence.

## RAG and Grounding Boundary

The architecture deliberately separates three kinds of context:

```text
SAP MM Knowledge
  -> expected process behavior and diagnostic evidence

SAP Mock Data
  -> state of the specific SAP business object

Application Policies
  -> mandatory AI scope, escalation and human-control rules
```

The FAISS corpus contains functional SAP MM evidence such as `KB-MM-001` through `KB-MM-008`.

Mandatory policies are applied deterministically:

```text
POLICY-AI-001
  -> AI Scope Policy

POLICY-HITL-001
  -> Human Approval Policy

POLICY-ESC-001
  -> Escalation Rules
```

This prevents mandatory controls from depending on vector similarity ranking.

## SAP Boundary

The POC does not connect to a real SAP environment.

The application uses a read-only interface:

```text
SAPClient
  -> SAPMockClient
```

Supported mock reads include:

```text
get_purchase_order()
get_purchase_requisition()
get_goods_receipt()
get_invoice()
get_vendor()
get_release_status()
```

Mutation operations are intentionally excluded.

A production implementation can replace the mock provider with an authenticated SAP API/OData provider while preserving the assistant's business-control layer.

## Control Plane

The primary controls are implemented outside the LLM.

### Scope Guard

Restricts the POC to the defined SAP MM processes.

Requests clearly belonging to unsupported modules are returned as out of scope.

### Completeness Check

Prevents diagnosis when required ticket context is missing and requests only the minimum additional information needed to continue.

### Evidence Gate

Checks:

- whether evidence exists;
- retrieval score;
- evidence sufficiency;
- evidence conflicts.

Unsupported diagnostic conclusions do not proceed as grounded answers.

### Confidence Engine

Confidence is calculated by application logic:

```text
Retrieval Quality          35%
Information Completeness   20%
Evidence Coverage          30%
Source Agreement           15%
```

Thresholds:

```text
HIGH    >= 0.80
MEDIUM  >= 0.60
LOW     <  0.60
```

The score is a deterministic control signal, not a calibrated probability of correctness. Claude does not assign or override it.

### Application Policy Engine

Mandatory policies control AI scope, escalation and human authorization independently of the LLM and vector retrieval.

This layer ensures that policy behavior remains deterministic even when model output or semantic similarity varies.

### Structured Response Validation

Claude is instructed to return a defined JSON object.

The Bedrock adapter first performs strict JSON parsing and can recover an otherwise valid JSON object from harmless model wrappers. Invalid or unusable structured output remains a controlled model error.

### HITL Gate

Human validation or authorization is mandatory when applicable, including:

- insufficient evidence;
- conflicting evidence;
- low confidence;
- SAP state-changing operations;
- purchasing approvals or releases;
- postings;
- financial-impact actions;
- authorization-sensitive incidents;
- authorization changes;
- configuration changes;
- master-data changes.

Authorization-classified incidents use a conservative POC rule and require human validation even when grounded evidence is available.

## Audit and Traceability

The application records enough execution context to reconstruct the basis of an assessment.

The audit trail can associate:

```text
Request
  -> SAP context
  -> Retrieved evidence
  -> Policy evidence
  -> Confidence
  -> HITL decision
  -> Model telemetry
  -> Response
```

The current POC stores audit records in Amazon DynamoDB using `request_id` as the primary identifier.

## Security Principles

The POC follows these boundaries:

- AWS credentials are obtained through the AWS credential provider chain or EC2 IAM role;
- credentials are not stored in source code;
- SAP access is read-only;
- the LLM cannot directly invoke mutation operations;
- retrieved content cannot override system-level instructions;
- source attribution is controlled by the application;
- protected actions require human authorization;
- sensitive audit fields are redacted;
- requests, evidence and control decisions are auditable.

## Deliberate Architecture Choices

Amazon Bedrock Knowledge Bases is not used by the current implementation. The POC uses Titan Text Embeddings V2 plus a local FAISS index to keep retrieval explicit, lightweight and cost-conscious.

Multi-agent orchestration is also intentionally excluded. The use case is a bounded sequential diagnostic workflow, so additional agents would add latency, cost, orchestration complexity and failure modes without improving the POC objective.

## Production Evolution

A production architecture can evolve the POC by adding:

- authenticated SAP OData/API connectivity;
- enterprise identity integration and SSO;
- private networking where required;
- managed ingress and TLS;
- secrets management;
- production observability;
- expanded audit retention;
- larger golden evaluation datasets;
- retrieval and grounding threshold calibration;
- knowledge governance and document lifecycle;
- SAP functional-owner approval workflows;
- production security and resilience controls;
- managed or distributed vector retrieval if scale exceeds the local FAISS design.

Any future SAP write capability should remain separately authorized, auditable and constrained by enterprise controls.
