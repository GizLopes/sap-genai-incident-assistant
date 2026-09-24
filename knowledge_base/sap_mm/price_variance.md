---
document_id: KB-MM-006
module: MM
process: Invoice Verification
topic: Price Variance
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---

# Price Variance

A price variance exists when the invoice price being evaluated differs from the relevant purchasing price used for comparison.

Whether a variance causes a block depends on the organization's SAP configuration and business rules. The assistant must never invent a tolerance threshold.

## Diagnostic Evidence

Useful evidence includes:

- PO item price;
- invoice item price;
- quantity;
- currency;
- unit of measure;
- invoice status;
- documented tolerance configuration when explicitly available.

## Analysis

If the PO and invoice contain different comparable prices, the assistant may state that a price difference exists.

The assistant may identify price variance as a possible explanation for an invoice block only when:

1. the invoice is actually blocked; and
2. the price difference is supported by the supplied data or retrieved evidence.

Without documented tolerance settings, the assistant must not claim that the difference exceeds a configured tolerance.

## Recommended Checks

1. Confirm that PO and invoice prices are comparable.
2. Confirm currency and unit of measure.
3. Review whether commercial conditions changed after PO creation.
4. Review the invoice blocking reason when available.
5. Consult approved configuration documentation for applicable tolerance rules.
6. Escalate any commercial correction, invoice release, or configuration change.

## Example Reasoning Boundary

Supported:

"The PO price and invoice price differ. Price variance is therefore a relevant diagnostic area."

Unsupported without additional evidence:

"The invoice was blocked because the configured tolerance is 5%."

## Human-Control Boundary

The AI does not change PO prices, release invoices, adjust tolerance configuration, or post accounting corrections.
