# Request Flow

## Purpose

This flow describes how an SAP support ticket moves through the assistant from submission to a grounded response, clarification request, controlled abstention, or human escalation.

## Flow

```text
User
  -> [submits ticket]
Streamlit UI
  -> [creates request]
Application Orchestrator
  -> [checks module/process boundary]
Scope Guard

Scope Guard
  -> [out of scope]
Out-of-Scope Response
  -> [applies AI scope policy]
POLICY-AI-001
  -> [routes request]
User / Appropriate SAP Support Queue

Scope Guard
  -> [in scope]
Classification
  -> [identifies SAP MM process and intent]
Completeness Check

Completeness Check
  -> [required context missing]
Clarification Response
  -> [asks minimum diagnostic questions]
User

Completeness Check
  -> [enough context]
SAP Read-Only Client
  -> [loads relevant mock SAP object]
SAP Mock Data

Application Orchestrator
  -> [combines classified process + ticket]
Retrieval Query
  -> [creates query embedding]
Amazon Titan Text Embeddings V2
  -> [searches normalized vectors]
FAISS Index · Amazon EC2
  -> [returns ranked SAP MM evidence]
Evidence Gate

Evidence Gate
  -> [no sufficient evidence]
Insufficient Evidence Response
  -> [applies escalation policy]
POLICY-ESC-001
  -> [requests context or specialist review]
User / SAP Specialist

Evidence Gate
  -> [conflicting evidence]
HITL Escalation
  -> [preserves conflicting sources]
POLICY-ESC-001
  -> [requires human validation]
SAP Specialist

Evidence Gate
  -> [evidence accepted]
Confidence Engine
  -> [calculates application confidence]
Application Policy Engine
  -> [applies AI scope, HITL and escalation rules]
Grounded Prompt Context
  -> [ticket + SAP context + retrieved evidence]
Amazon Bedrock · Claude Sonnet 4.6
  -> [generates structured JSON analysis]
Response Builder
  -> [validates structured payload and attaches controlled sources]
HITL Gate
  -> [checks process, requested action, evidence and risk]

HITL Gate
  -> [read-only recommendation allowed]
Streamlit UI
  -> [shows analysis, checks, sources and confidence]
User

HITL Gate
  -> [authorization case or protected action]
POLICY-HITL-001
  -> [requires human validation]
Human Validation Required
  -> [shows recommendation without execution]
Authorized SAP Specialist

Application Orchestrator
  -> [logs request, response, sources and model telemetry]
Amazon DynamoDB
```

## Processing Order

The application uses the following control order:

1. scope;
2. process classification;
3. information completeness;
4. read-only SAP context;
5. process-aware retrieval query;
6. Titan embedding and FAISS retrieval;
7. evidence sufficiency;
8. evidence consistency;
9. application confidence;
10. deterministic policy evaluation;
11. grounded structured generation;
12. structured-response validation;
13. HITL/action-risk decision;
14. response;
15. audit logging.

Some terminal branches, such as out-of-scope or missing-information responses, return before model generation.

## Retrieval Flow

Runtime retrieval is explicit and local to the application:

```text
Ticket + Classified Process
  -> Retrieval Query
  -> Titan Text Embeddings V2
  -> FAISS
  -> Ranked Evidence
  -> Evidence Gate
```

The current minimum grounding score is `0.50`.

Functional SAP evidence is retrieved semantically. Mandatory AI scope, HITL and escalation policies are applied deterministically rather than retrieved through FAISS.

## Missing Information

The assistant asks for additional context before diagnosis when critical information is absent.

Examples:

- Purchase Order number;
- Purchase Requisition number;
- invoice number;
- exact SAP error message;
- transaction or application context;
- relevant item number.

The assistant should ask for the minimum information required to continue.

## Grounded Diagnosis

Possible causes must be supported by retrieved evidence or supplied SAP context.

A hypothesis remains a hypothesis until the available evidence supports stronger wording.

The application exposes controlled source references so the user can inspect the basis for the recommendation. The LLM does not invent source IDs.

## Structured Generation

Claude Sonnet 4.6 receives only the context assembled by the application and returns a bounded JSON payload containing:

```text
summary
possible_causes
recommended_checks
missing_information
```

Confidence, source attribution and HITL status are application responsibilities.

The Bedrock adapter validates structured output. Harmless wrappers around an otherwise valid JSON object can be normalized; invalid structured output remains a controlled model failure.

## Failure Behavior

The workflow prefers abstention, clarification, or escalation when:

- the request is outside SAP MM scope;
- required information is missing;
- retrieval produces insufficient evidence;
- evidence conflicts;
- confidence is low;
- the case is authorization-sensitive;
- the requested operation changes SAP state;
- model output cannot satisfy the required structured contract.

This behavior is intentional and is part of the POC's hallucination-control and autonomy-control strategy.

## Audit

The application records the request outcome together with available evidence, policy sources, confidence, HITL decision and Bedrock telemetry in Amazon DynamoDB.

Audit logging is independent of the model's narrative response.
