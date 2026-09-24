# SAP MM Knowledge Base

## Purpose

This directory contains the controlled grounding corpus used by the SAP GenAI Incident Assistant.

The knowledge base supports Retrieval-Augmented Generation (RAG) for SAP Materials Management (MM) ticket analysis. Its purpose is to provide explicit evidence for diagnostic guidance and reduce unsupported or invented answers.

The assistant must not treat model pretraining knowledge as sufficient evidence for a diagnostic conclusion. Operational guidance must be grounded in the ticket, approved knowledge-base content, read-only SAP context, or a combination of these sources.

## Directory Structure

```text
knowledge_base/
├── README.md
├── sap_mm/
│   ├── purchase_requisition.md
│   ├── purchase_order.md
│   ├── release_strategy.md
│   ├── goods_receipt.md
│   ├── invoice_verification.md
│   ├── price_variance.md
│   ├── authorization_errors.md
│   └── mm_fi_integration.md
└── policies/
    ├── ai_scope.md
    ├── human_approval.md
    └── escalation_rules.md
```

## SAP MM Documents

The `sap_mm/` directory contains process-oriented troubleshooting knowledge.

| Document | Purpose |
|---|---|
| `purchase_requisition.md` | Purchase Requisition analysis and common diagnostic checks |
| `purchase_order.md` | Purchase Order troubleshooting and document relationships |
| `release_strategy.md` | Release/approval analysis and evidence boundaries |
| `goods_receipt.md` | Goods Receipt troubleshooting and quantity/document checks |
| `invoice_verification.md` | Invoice Verification analysis across PO, GR, and invoice context |
| `price_variance.md` | Evidence-based analysis of PO/invoice price differences |
| `authorization_errors.md` | Safe investigation of SAP authorization incidents |
| `mm_fi_integration.md` | MM/FI boundary analysis for purchasing-related accounting issues |

## Policy Documents

The `policies/` directory contains mandatory behavioral and governance rules.

### AI Scope

`ai_scope.md` defines:

- supported SAP MM processes;
- allowed AI activities;
- prohibited autonomous actions;
- grounding requirements;
- out-of-scope behavior;
- security boundaries.

### Human Approval

`human_approval.md` defines when Human-in-the-Loop validation is mandatory, including:

- insufficient evidence;
- conflicting evidence;
- low confidence;
- state-changing SAP operations;
- financial impact;
- authorization changes;
- configuration changes;
- master-data changes.

### Escalation Rules

`escalation_rules.md` defines the decision path for:

- out-of-scope requests;
- unclear scope;
- incomplete tickets;
- missing evidence;
- conflicting evidence;
- low or medium confidence;
- critical SAP actions;
- authorization incidents;
- MM/FI cross-functional issues.

Policy documents have higher operational importance than ordinary troubleshooting content. Retrieved knowledge must never be interpreted as permission to bypass a policy.

## Metadata

Knowledge documents use YAML front matter to provide retrieval metadata.

Example:

```yaml
---
document_id: KB-MM-005
module: MM
process: Invoice Verification
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---
```

Policy documents follow the same approach:

```yaml
---
document_id: POLICY-HITL-001
document_type: policy
policy: Human Approval
module: MM
risk_level: CRITICAL
requires_human_approval: true
priority: mandatory
---
```

These fields support metadata filtering, traceability, evidence attribution, risk handling, and future Knowledge Base ingestion.

## Document IDs

The current convention is:

```text
KB-MM-001 ... KB-MM-008
```

for SAP MM process knowledge, and:

```text
POLICY-AI-001
POLICY-HITL-001
POLICY-ESC-001
```

for governance policies.

Document IDs should remain stable after publication because evaluation results and audit records may reference them.

## Retrieval Strategy

A user ticket is analyzed through the following conceptual flow:

```text
SAP Ticket
  -> Scope Classification
  -> Process Classification
  -> Retrieval Query
  -> Knowledge Base
  -> Ranked Evidence
  -> Evidence Gate
  -> Confidence Calculation
  -> Grounded Recommendation or Escalation
```

The retriever should return a limited set of relevant chunks rather than the entire corpus.

The application may use process and metadata information to improve retrieval precision.

Example:

```text
Ticket:
"Invoice 5100001234 is blocked and the invoice price
is higher than the purchase order."

Classification:
Module  = MM
Process = Invoice Verification

Relevant retrieval targets:
- invoice_verification.md
- price_variance.md
- human_approval.md
```

## Grounding Rules

The assistant may use retrieved evidence to:

- explain documented SAP MM behavior;
- identify supported diagnostic hypotheses;
- recommend documented checks;
- identify required human review;
- cite the source used.

The assistant must not use retrieval results to invent:

- SAP document values;
- customer-specific configuration;
- tolerance thresholds;
- G/L accounts;
- authorization assignments;
- release codes;
- approval hierarchies;
- posting results;
- master-data values;
- undocumented root causes.

Customer-specific values require explicit evidence.

## Evidence Attribution

Every diagnostic cause should be traceable to one or more evidence identifiers.

Example structured representation:

```json
{
  "cause": "A price difference exists between the PO and invoice.",
  "evidence_ids": [
    "KB-MM-005",
    "KB-MM-006"
  ]
}
```

The application should preserve the source identifier through retrieval, assessment, response generation, and audit logging.

## Confidence

The knowledge base does not define or generate an LLM confidence score.

Confidence is calculated by application logic from factors such as:

```text
Retrieval Quality
        +
Ticket Completeness
        +
Evidence Coverage
        +
Source Agreement
        ↓
Application Confidence
```

The LLM receives the resulting confidence level as an application control and must not replace it with a self-generated percentage.

## Human-in-the-Loop

High retrieval relevance does not grant execution authority.

For example:

```text
Strong Evidence
      +
High Confidence
      +
PO Release Required
      ↓
Human Approval Required
```

State-changing SAP operations remain human-controlled regardless of model confidence.

## Local Development

The application includes a local retriever for development and testing.

It can read Markdown documents directly from this directory:

```text
knowledge_base/
```

This allows core retrieval and evaluation logic to be tested without requiring an AWS connection.

## Amazon Bedrock Knowledge Bases

For the AWS-hosted POC, these documents can be uploaded to the configured S3 data source and indexed by Amazon Bedrock Knowledge Bases.

The application integration is isolated in:

```text
integrations/knowledge_base_client.py
```

This separation allows the application to switch between local development retrieval and AWS retrieval without changing the core diagnostic workflow.

Environment-specific identifiers must not be committed to the knowledge documents.

Examples include:

```text
BEDROCK_KNOWLEDGE_BASE_ID
AWS_REGION
```

These values belong in environment configuration.

## Updating the Knowledge Base

When adding or modifying content:

1. use an explicit and stable `document_id`;
2. identify the SAP module and process;
3. distinguish documented facts from diagnostic hypotheses;
4. avoid undocumented customer-specific assumptions;
5. define the risk level;
6. identify whether human approval is required;
7. preserve source traceability;
8. run the evaluation dataset after material changes;
9. review changes before promoting them to the POC environment.

## Content Quality Rules

Knowledge-base content should be:

- concise;
- process-specific;
- evidence-oriented;
- suitable for retrieval;
- explicit about uncertainty;
- explicit about human-control boundaries.

Avoid adding large generic SAP documents when smaller targeted documents provide better retrieval precision.

## Security

Do not store the following in this directory:

- AWS credentials;
- SAP credentials;
- passwords;
- access tokens;
- API keys;
- private keys;
- production secrets;
- unnecessary personal information.

The repository is intended to be publishable without exposing credentials or sensitive operational data.

## POC Limitation

This corpus is intentionally limited to the scenarios required for the technical challenge.

It is not intended to represent complete SAP MM documentation or production support knowledge.

A production implementation would require controlled ingestion of approved enterprise documentation, ownership and review processes, versioning, access controls, evaluation against real support scenarios, and continuous knowledge-quality management.
