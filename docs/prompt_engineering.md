# Prompt Engineering

## Objective

Prompt engineering constrains the LLM to produce evidence-based SAP MM diagnostic assistance without inventing system state, configuration, authorization, or root causes.

## Prompt Layers

The repository separates prompts by responsibility:

```text
prompts/
├── system_prompt.md
├── ticket_analysis.md
├── clarification.md
├── grounded_answer.md
└── scope_classification.md
```

This separation makes behavior easier to test and version.

## System Prompt

The system prompt establishes permanent POC rules:

- supported SAP MM scope;
- grounding requirements;
- prohibited assumptions;
- HITL boundaries;
- security rules;
- confidence ownership.

The model is explicitly instructed not to invent:

- SAP document status;
- configuration values;
- release thresholds;
- approvers;
- tolerance values;
- authorization assignments;
- transaction results;
- root causes;
- sources.

## Ticket Analysis Prompt

The analysis prompt receives:

```text
Ticket
SAP Module
Classified Process
Intent
Read-Only SAP Context
Retrieved Evidence
```

The output is structured JSON.

Possible causes and recommended checks must reference supporting evidence identifiers.

This supports programmatic validation before the answer is shown to the user.

## Clarification Prompt

The clarification prompt is used when required information is missing.

Its purpose is to ask the minimum diagnostic questions needed to continue.

It must not diagnose the issue while the required context is absent.

Example:

```text
Missing:
- Purchase Order number
- exact SAP error message

Allowed:
- ask for these values

Not allowed:
- assume release strategy failure
- assume authorization failure
```

## Grounded Answer Prompt

The grounded-answer stage receives an already validated assessment.

It formats:

- analysis;
- possible causes;
- recommended checks;
- sources;
- confidence;
- human-validation requirement.

It cannot introduce new causes that were not present in the validated assessment.

## Scope Classification

Scope classification separates supported SAP MM issues from unsupported modules.

Expected outputs are constrained to:

```text
IN_SCOPE
OUT_OF_SCOPE
UNCLEAR
```

A request should not be forced into MM merely because it mentions SAP.

## Structured Output

JSON is preferred between model and application because it enables validation of:

- required fields;
- evidence IDs;
- missing-information fields;
- escalation flags;
- prohibited actions.

The UI can then render a stable response format.

## Hallucination Controls

Prompt-level controls include:

1. explicit source boundaries;
2. prohibition against inventing SAP values;
3. evidence identifiers for causes;
4. distinction between facts and hypotheses;
5. mandatory uncertainty when evidence is insufficient;
6. mandatory escalation for conflicts;
7. explicit prohibition against claiming execution.

Prompt controls are only one layer. Application-level Evidence Gate, confidence, scope, and HITL logic remain authoritative.

## Prompt Injection

Retrieved documents are treated as data, not instructions.

Knowledge content must not override:

- system instructions;
- scope rules;
- security controls;
- HITL rules.

Production ingestion should additionally validate and govern the source corpus.

## Temperature

Diagnostic workflows benefit from low variability.

The Bedrock client should use a low temperature unless testing demonstrates a reason to change it.

Deterministic application controls remain necessary regardless of temperature.

## Versioning

Production audit records should include a prompt version.

Example:

```text
prompt_version: sap-mm-analysis-v1.0
```

Prompt changes should trigger regression evaluation against the fixed evaluation dataset.

## Evaluation

Prompt quality is measured through behavior, including:

- classification accuracy;
- grounded-answer rate;
- citation coverage;
- hallucination regression checks;
- clarification accuracy;
- escalation accuracy;
- human-approval compliance.
