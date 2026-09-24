# Production Evolution

## Objective

The POC is designed so its control model can evolve into a production SAP support assistant without preserving unnecessary prototype constraints.

## POC Baseline

```text
User
-> Streamlit on EC2
-> Python Orchestrator
-> Bedrock
-> Bedrock Knowledge Bases
-> S3 Knowledge
-> SAP Mock
-> Evidence / Confidence / HITL Controls
-> DynamoDB Audit
```

## Phase 1: Real SAP Read Integration

Replace `SAPMockClient` with an authenticated read provider.

Preserve the `SAPClient` interface so the orchestration layer does not depend on SAP transport details.

Initial production integration should remain read-only.

Candidate capabilities:

```text
Read PO
Read PR
Read GR
Read Invoice
Read Vendor
Read Release Status
Read relevant authorization diagnostics where approved
```

## Phase 2: Enterprise Identity and Access

Add:

- enterprise SSO;
- user identity propagation;
- role-based application access;
- environment separation;
- least-privilege IAM;
- approved SAP technical-user or OAuth model.

The assistant should know which user is requesting analysis without using that identity to bypass SAP authorization.

## Phase 3: Knowledge Governance

Expand the corpus to approved sources such as:

- internal SAP operating procedures;
- customer configuration documentation;
- approved SAP support documentation;
- resolved-ticket knowledge;
- architecture and integration documentation.

Introduce:

- ownership;
- versioning;
- approval;
- effective dates;
- access classification;
- stale-content management.

## Phase 4: Evaluation Expansion

Build a representative labeled dataset from historical incidents.

Measure:

- process classification;
- retrieval recall/precision;
- grounded-answer quality;
- citation quality;
- hallucination;
- clarification;
- escalation;
- expert acceptance;
- response time;
- cost.

Segment metrics by SAP process and incident type.

## Phase 5: Observability and Operations

Introduce production telemetry for:

- request volume;
- latency;
- model failures;
- retrieval failures;
- escalation rate;
- confidence distribution;
- token usage;
- cost;
- user feedback;
- audit events.

Define operational ownership and incident response.

## Phase 6: Controlled Actions

Only introduce write operations when a business case justifies them.

Use explicit action contracts and authorization.

Example pattern:

```text
AI Recommendation
-> Human Approval
-> Authorized Action Service
-> SAP API
-> Execution Result
-> Audit
```

The LLM should never obtain unrestricted SAP mutation access.

## Controlled Action Requirements

Before enabling any state-changing action:

- action must be explicitly enumerated;
- authorization must be validated outside the LLM;
- required human approval must be recorded;
- inputs must be validated;
- execution must be idempotent where applicable;
- result must be auditable;
- rollback or recovery behavior must be defined.

## Architecture Evolution

Production may justify decomposition into managed services based on measured requirements.

Possible additions include:

- load-balanced web/API tier;
- container platform;
- asynchronous processing;
- centralized observability;
- private networking;
- secrets management;
- workflow orchestration;
- dedicated evaluation pipeline.

These should be introduced because of operational requirements, not because GenAI inherently requires them.

## Success Metrics

Production success should measure business outcomes in addition to model quality:

- mean time to initial diagnosis;
- mean time to resolution;
- percentage of tickets requiring clarification;
- percentage escalated correctly;
- first-response quality;
- SAP specialist acceptance;
- repeated-incident reduction;
- analyst time saved;
- cost per resolved or assisted ticket.

## Deployment Principle

Production evolution should preserve the POC's strongest boundary:

```text
LLM = reasoning and language
Application = controls
SAP = system of record
Human = authority for protected decisions
```
