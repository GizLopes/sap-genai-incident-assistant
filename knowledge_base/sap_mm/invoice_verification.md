---
document_id: KB-MM-005
module: MM
process: Invoice Verification
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---

# Invoice Verification

Invoice Verification in SAP MM compares supplier invoice information with the purchasing documents and, where applicable, receipt information.

The purchasing flow may involve a relationship among:

- Purchase Order;
- Goods Receipt;
- supplier invoice.

## Information Required

Collect:

- invoice or reference number;
- PO number and item;
- supplier;
- invoice amount and relevant item values;
- PO price and quantity;
- Goods Receipt information when applicable;
- current invoice status;
- exact error or blocking message.

## Common Issues

### Invoice is blocked

Potential causes include:

- price difference requiring review;
- quantity difference requiring review;
- missing or inconsistent purchasing reference;
- expected Goods Receipt information is unavailable;
- duplicate or document-reference concerns;
- configuration or tolerance rules requiring functional validation.

A blocked invoice does not prove a specific cause. The relevant document values and evidence must be inspected.

### Invoice cannot be posted

Possible diagnostic areas include:

- purchasing-document reference;
- quantity and price relationships;
- supplier/document data;
- Goods Receipt history;
- authorization;
- MM/FI integration.

## Recommended Checks

1. Confirm invoice and PO references.
2. Compare PO, receipt, and invoice quantities.
3. Compare relevant price values.
4. Review the invoice status and exact blocking/error message.
5. Review purchasing-document history.
6. Escalate when correction requires posting, release, financial adjustment, or configuration change.

## Human-Control Boundary

Invoice posting, release, reversal, and financial correction require authorized human execution.
