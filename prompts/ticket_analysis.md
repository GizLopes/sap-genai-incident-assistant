# Prompt — Ticket Analysis

Analyze the SAP support ticket using only the information and evidence supplied below.

## Ticket

{{ticket_text}}

## Application Classification

SAP Module: {{sap_module}}
Process: {{process}}
Intent: {{intent}}

## Read-Only SAP Context

{{sap_context}}

## Retrieved Evidence

{{retrieved_evidence}}

## Task

Determine:

1. Whether the ticket contains enough information for analysis;
2. The SAP MM process involved;
3. Relevant facts explicitly supported by the ticket or SAP context;
4. Missing information;
5. Evidence-supported possible causes;
6. Diagnostic checks that a consultant can perform;
7. Whether the evidence is insufficient or conflicting;
8. Whether human validation is required.

Do not infer a SAP status or root cause that is absent from the supplied information.

Do not invent configuration, master data, transaction results, error codes, document values, or SAP behavior.

When several causes remain possible, preserve them as hypotheses.

## Required JSON Output

Return exactly one JSON object:

{
  "process": "string",
  "summary": "string",
  "facts": [
    "string"
  ],
  "missing_information": [
    "string"
  ],
  "possible_causes": [
    {
      "cause": "string",
      "evidence_ids": ["string"]
    }
  ],
  "recommended_checks": [
    {
      "check": "string",
      "evidence_ids": ["string"],
      "requires_human_execution": true
    }
  ],
  "insufficient_evidence": false,
  "conflicting_evidence": false,
  "human_validation_recommended": false
}

## Constraints

- Every possible cause must reference at least one supplied evidence ID.
- A cause without supporting evidence must be omitted.
- Do not calculate confidence.
- Do not claim that a recommended check has been executed.
- Return JSON only.
