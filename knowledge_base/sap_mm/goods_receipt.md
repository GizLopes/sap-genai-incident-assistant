---
document_id: KB-MM-004
module: MM
process: Goods Receipt
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---

# Goods Receipt

Goods Receipt (GR) records the receipt of materials or services against the relevant purchasing process. In an MM purchasing flow, the receipt can affect inventory, purchasing history, and subsequent invoice verification.

## Information Required

For GR troubleshooting, collect:

- Purchase Order number and item;
- material document number when one exists;
- material or service;
- quantity ordered;
- quantity previously received;
- quantity currently being received;
- plant or receiving location when relevant;
- exact SAP error message.

## Common Issues

### Receipt cannot be posted

Possible causes include:

- incorrect PO or item reference;
- no remaining quantity available for the attempted receipt;
- document status does not support the attempted operation;
- required data is missing;
- user authorization prevents posting;
- purchasing or inventory configuration requires specialist review.

### Quantity differs from the Purchase Order

A difference between ordered and received quantities requires investigation of the document history and applicable business rules.

Do not assume a configured tolerance value unless that value is explicitly available as evidence.

## Recommended Checks

1. Confirm the PO and item.
2. Compare ordered, previously received, and attempted quantities.
3. Review purchasing-document history.
4. Capture the exact SAP error.
5. Check whether the issue is authorization-related.
6. Escalate if resolution requires posting, reversal, configuration change, or business approval.

## Human-Control Boundary

Posting or reversing a Goods Receipt changes SAP state and can affect inventory and accounting. These actions require an authorized human.
