---
document_id: KB-MM-003
module: MM
process: Release Strategy
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---

# Release Strategy

Release or approval controls can prevent a purchasing document from progressing until the required authorization steps are completed.

The exact release mechanism depends on the customer's SAP design and configuration. The assistant must not assume approval levels, thresholds, approvers, or release codes that are not present in the supplied evidence.

## Symptoms

Typical ticket descriptions include:

- Purchase Order is blocked;
- Purchase Requisition is awaiting approval;
- document cannot proceed because release is incomplete;
- expected approver cannot release the document;
- release status differs from the user's expectation.

## Diagnostic Checks

1. Identify the purchasing document and item.
2. Read the current release or approval status.
3. Determine whether an approval step remains pending.
4. Check whether the user reports an authorization error.
5. Compare the observed status with documented business rules when those rules are available in the knowledge base.
6. Escalate configuration discrepancies to the responsible SAP functional team.

## Evidence Rules

A pending release status supports the conclusion that approval remains incomplete.

It does not, by itself, prove:

- why a specific strategy was selected;
- which person should approve;
- that configuration is incorrect;
- that a monetary threshold caused the strategy;
- that an authorization assignment is missing.

Those conclusions require additional evidence.

## Human-Control Boundary

Release and approval decisions are human-controlled actions. The AI may identify the observed release status and explain documented rules, but it must never execute or simulate approval.
