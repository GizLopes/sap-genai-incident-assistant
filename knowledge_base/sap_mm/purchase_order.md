---
document_id: KB-MM-002
module: MM
process: Purchase Order
document_type: knowledge
risk_level: MEDIUM
requires_human_approval: true
---

# Purchase Order

A Purchase Order (PO) is a formal purchasing document used to order materials or services from a supplier. It can reference a Purchase Requisition or other purchasing source.

## Typical Analysis Context

For a PO incident, collect:

- PO number and item;
- supplier;
- material or service;
- quantity and price;
- delivery date;
- plant and purchasing organization when relevant;
- release status;
- Goods Receipt status;
- invoice status;
- exact error message.

## Common Issues

### PO is blocked or cannot progress

Potential causes include:

- release or approval is pending;
- document data is incomplete;
- supplier or material data is inconsistent with the purchasing process;
- quantity or price conditions require review;
- the PO has a status that prevents the requested downstream operation;
- the user lacks authorization for the attempted activity.

### Downstream document cannot reference the PO

Check whether:

- the correct PO and item are being referenced;
- the item remains relevant for receipt or invoice processing;
- quantities already received or invoiced affect the remaining quantity;
- the purchasing document status supports the requested operation.

## Recommended Checks

1. Confirm PO number and item.
2. Inspect the PO status and release information.
3. Review relevant quantities, prices, and document relationships.
4. Check Goods Receipt and invoice history.
5. Review the exact error returned by SAP.
6. Escalate when the required correction changes commercial terms, approvals, configuration, or financial postings.

## Human-Control Boundary

The assistant must not release, modify, close, delete, or otherwise change a Purchase Order. It provides read-only diagnostic guidance.
