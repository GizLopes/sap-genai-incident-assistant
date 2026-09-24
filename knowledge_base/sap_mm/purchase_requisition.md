---
document_id: KB-MM-001
module: MM
process: Purchase Requisition
document_type: knowledge
risk_level: LOW
requires_human_approval: false
---

# Purchase Requisition

A Purchase Requisition (PR) is an internal request to procure a material or service. It represents a purchasing requirement and normally precedes creation of a Purchase Order.

## Typical Analysis Context

When analyzing a PR-related incident, verify:

- PR number and item;
- purchasing organization or purchasing group when relevant;
- material or service requested;
- quantity and delivery date;
- account assignment when applicable;
- source of supply when applicable;
- release or approval status;
- whether the PR has already been converted into a Purchase Order.

## Common Issues

### PR cannot proceed to purchasing

Possible causes include:

- incomplete mandatory purchasing data;
- missing or inconsistent account assignment;
- release or approval still pending;
- invalid or unavailable source-of-supply information;
- downstream purchasing document already created;
- user authorization restrictions.

These are diagnostic hypotheses. The actual cause must be supported by ticket information, SAP data, or another approved source.

## Recommended Checks

1. Confirm the PR number and affected item.
2. Review the current PR status.
3. Check whether a release or approval is pending.
4. Review mandatory purchasing and account-assignment fields.
5. Verify whether a Purchase Order already references the PR.
6. If an authorization error is reported, obtain the exact error and follow the authorization investigation process.

## Human-Control Boundary

The assistant may explain the PR status and recommend checks. Changes to the PR, approval decisions, release actions, account assignments, or master data must be performed by an authorized SAP user.
