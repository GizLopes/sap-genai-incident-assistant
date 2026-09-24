---
document_id: POLICY-ESC-001
document_type: policy
policy: Escalation Rules
module: MM
risk_level: HIGH
requires_human_approval: true
priority: mandatory
---

# Escalation Rules

## Purpose

This policy defines when the SAP GenAI Incident Assistant must stop normal diagnostic guidance and route the case for clarification or human review.

## Decision Order

Evaluate escalation in the following order:

1. scope;
2. ticket completeness;
3. evidence availability;
4. evidence consistency;
5. application confidence;
6. requested or recommended action risk;
7. functional ownership.

A higher-risk rule takes precedence over a lower-risk rule.

## Rule 1 — Out of Scope

### Condition

The request clearly belongs outside the supported SAP MM POC scope.

### Assistant Action

- classify as `OUT_OF_SCOPE`;
- identify the detected module or area when evidence supports it;
- do not perform MM diagnostic reasoning;
- recommend routing to the appropriate support queue or functional owner.

### Human Validation

Not required merely to state that a clearly unsupported request is outside the POC scope.

---

## Rule 2 — Scope Unclear

### Condition

The assistant cannot reliably determine whether the incident belongs to SAP MM.

### Assistant Action

- classify as `UNCLEAR`;
- request the minimum information needed to identify the process;
- do not guess the SAP module.

### Escalation

Escalate if clarification does not provide sufficient information.

---

## Rule 3 — Ticket Incomplete

### Condition

Information necessary for meaningful diagnosis is missing.

Examples include:

- no affected document or process when one is required;
- missing exact error message;
- missing current status;
- insufficient description of observed versus expected behavior.

### Assistant Action

Return `NEEDS_CLARIFICATION` and request only the information required for the next diagnostic step.

---

## Rule 4 — No Supporting Evidence

### Condition

No reliable knowledge-base or SAP evidence supports a diagnostic conclusion.

### Assistant Action

- return `INSUFFICIENT_EVIDENCE`;
- do not generate possible root causes as facts;
- identify which evidence is missing;
- route for human analysis when additional evidence cannot be obtained.

### Human Validation

Required before operational guidance is acted upon.

---

## Rule 5 — Conflicting Evidence

### Condition

Two or more relevant evidence sources materially disagree.

### Assistant Action

- preserve both evidence references;
- explain the conflict;
- do not choose a source arbitrarily;
- return `HUMAN_VALIDATION_REQUIRED`.

### Human Validation

Mandatory.

---

## Rule 6 — Low Confidence

### Condition

Application-calculated confidence is `LOW`.

### Assistant Action

- state that the available evidence does not support sufficiently reliable guidance;
- present verified facts and sources only;
- request context when additional information can improve the assessment;
- otherwise escalate.

### Human Validation

Mandatory.

---

## Rule 7 — Medium Confidence

### Condition

Application-calculated confidence is `MEDIUM`.

### Assistant Action

The assistant may provide grounded diagnostic guidance while clearly identifying uncertainty.

If missing information can materially change the diagnosis, request clarification before recommending consequential action.

### Human Validation

Required when the recommended next step has operational, financial, security, approval, master-data, or configuration impact.

---

## Rule 8 — Critical or State-Changing Action

### Condition

The case involves or requests:

- PO or PR approval/release;
- Goods Receipt posting or reversal;
- invoice posting, release, or reversal;
- financial posting or reversal;
- SAP configuration;
- authorization or role changes;
- master-data changes.

### Assistant Action

Provide evidence-supported diagnostic information only.

### Human Validation

Mandatory regardless of confidence level.

---

## Rule 9 — Authorization/Security Issue

### Condition

The incident indicates a SAP authorization failure or requests access changes.

### Assistant Action

- capture the exact authorization error when available;
- recommend approved diagnostic procedures;
- do not recommend bypasses or broad access grants;
- route access changes to the responsible authorization/security team.

### Human Validation

Mandatory for any role, authorization, or access change.

---

## Rule 10 — MM/FI Cross-Functional Issue

### Condition

The incident originates in MM but resolution depends on accounting behavior, account determination, financial posting, or FI-owned configuration.

### Assistant Action

- preserve the MM evidence;
- identify the MM/FI boundary;
- avoid inventing FI configuration;
- route the case to the appropriate MM/FI functional owners.

### Human Validation

Mandatory for financial corrections or configuration changes.

---

## Escalation Output

When escalation is triggered, the response should provide:

- escalation reason;
- identified SAP process;
- verified facts;
- missing information;
- evidence references;
- application confidence;
- recommended receiving team or role;
- actions explicitly reserved for humans.

## Priority Principle

Safety, evidence quality, authorization controls, and business-impact boundaries take precedence over completing an automated answer.
