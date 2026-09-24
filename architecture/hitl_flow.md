# Human-in-the-Loop Flow

## Purpose

Human-in-the-Loop protects SAP business processes from autonomous state-changing, authorization-sensitive, conflicting, or insufficiently supported AI decisions.

The assistant may analyze and recommend. Protected business actions remain under authorized human control.

## Decision Flow

```text
Grounded Assistant Assessment
  -> [checks evidence]
Evidence Available?

Evidence Available?
  -> [no]
Human Validation Required
  -> [applies escalation policy]
POLICY-ESC-001
  -> [requests additional evidence or specialist review]
SAP Specialist

Evidence Available?
  -> [yes]
Evidence Conflict?

Evidence Conflict?
  -> [yes]
Human Validation Required
  -> [preserves conflicting evidence without choosing arbitrarily]
POLICY-ESC-001
  -> [routes for specialist validation]
SAP Specialist

Evidence Conflict?
  -> [no]
Application Confidence

Application Confidence
  -> [LOW]
Human Validation Required
  -> [presents evidence and uncertainty]
SAP Specialist

Application Confidence
  -> [MEDIUM/HIGH]
SAP Process

SAP Process
  -> [Authorization]
Human Validation Required
  -> [applies conservative authorization rule]
POLICY-HITL-001
  -> [AI provides grounded diagnostics only]
Authorized SAP Specialist

SAP Process
  -> [other supported SAP MM process]
Requested or Recommended Action
  -> [classifies action risk]
Action Risk Gate

Action Risk Gate
  -> [read-only diagnostic check]
AI Recommendation Allowed
  -> [returns checks, evidence and application confidence]
User

Action Risk Gate
  -> [SAP state change or protected action]
Human Approval Required
  -> [applies HITL policy]
POLICY-HITL-001
  -> [AI recommends only]
Authorized SAP Specialist
  -> [reviews evidence and recommendation]
Human Decision
  -> [approve / reject / modify]
Authorized Execution Outside AI
```

## Deterministic HITL Inputs

The HITL decision is application-controlled.

Relevant inputs include:

```text
Evidence Gate result
Evidence conflict
Application confidence
Classified SAP process
Requested action
Action risk
```

The LLM does not decide whether human approval is required.

## Actions the AI May Perform

The assistant may:

- interpret a ticket;
- classify the SAP MM process;
- retrieve controlled documentation;
- read simulated SAP records;
- identify missing information;
- summarize evidence;
- propose evidence-supported possible causes;
- recommend diagnostic checks;
- expose application-controlled sources;
- use application-calculated confidence;
- recommend escalation.

The confidence score itself is calculated by deterministic application logic, not by the AI model.

## Actions Requiring Human Authorization

Human authorization is mandatory for actions such as:

```text
Release Purchase Order
Approve Purchase Requisition
Post or Reverse Goods Receipt
Post or Release Invoice
Execute Financial Posting
Change SAP Configuration
Change User Authorization
Change Master Data
```

The POC does not expose mutation methods for these operations.

## Separation of Responsibilities

```text
AI Recommendation
  -> evidence-supported analysis and diagnostic next steps

Application Controls
  -> evidence, confidence, policy and HITL decisions

Human Decision
  -> approval, rejection or modification of protected recommendations

Execution
  -> performed through an authorized SAP process outside autonomous AI control
```

This separation remains in force even when application confidence is HIGH.

## Evidence Conflict

When sources disagree, the assistant must:

1. identify the conflict;
2. preserve both evidence references;
3. avoid arbitrarily selecting a source as correct;
4. lower confidence where appropriate;
5. escalate for human validation.

The deterministic escalation policy is represented by `POLICY-ESC-001`.

## Authorization Cases

Authorization-classified incidents follow a conservative POC rule: human validation is required even when the evidence is sufficient and confidence is MEDIUM or HIGH.

The assistant may diagnose authorization-related evidence and recommend read-only checks.

It must not:

- grant permissions;
- recommend credential sharing;
- recommend bypassing authorization controls;
- assign broad roles such as SAP_ALL;
- invent required authorization objects or roles;
- claim an authorization change was executed.

Authorization changes are routed to the appropriate SAP security or authorization owner.

## Policy Enforcement

Mandatory controls are applied outside semantic retrieval:

```text
POLICY-AI-001
  -> supported AI scope

POLICY-HITL-001
  -> protected actions and human approval

POLICY-ESC-001
  -> insufficient or conflicting evidence escalation
```

Policies are not dependent on FAISS ranking and cannot be overridden by the LLM.

## Audit

A HITL decision should preserve:

- request ID;
- ticket ID when available;
- evidence references;
- policy references;
- application confidence;
- classified process;
- requested action;
- reason for human validation;
- AI recommendation;
- model telemetry where applicable;
- final human decision when available in a production implementation.

The current POC persists application audit records in Amazon DynamoDB.

## POC Boundary

The current POC demonstrates the decision boundary and escalation behavior.

It does not execute SAP state-changing actions. Any approved execution occurs outside the autonomous AI workflow.
