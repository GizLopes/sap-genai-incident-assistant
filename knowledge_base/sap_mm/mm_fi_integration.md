---
document_id: KB-MM-008
module: MM
process: MM/FI Integration
document_type: knowledge
risk_level: HIGH
requires_human_approval: true
---

# MM/FI Integration

SAP MM purchasing activities can create or depend on accounting consequences. Goods movements and invoice-related processes may therefore require analysis across the MM and FI boundary.

For this POC, an MM/FI issue remains in scope when the originating business process is an SAP MM purchasing, receipt, or invoice-verification process.

## Typical Symptoms

Examples include:

- MM operation completed differently from the expected accounting result;
- accounting document was not created as expected;
- invoice processing encounters an accounting-related error;
- Goods Receipt or invoice processing requires investigation of account determination;
- purchasing data and accounting outcome appear inconsistent.

## Diagnostic Information

Collect:

- originating MM document;
- PO and item when applicable;
- material or service context;
- Goods Receipt or invoice document;
- accounting document number when one exists;
- exact SAP error;
- relevant company code, plant, or valuation context only when required and available.

## Diagnostic Checks

1. Confirm the originating MM transaction or process.
2. Trace the relationship among the purchasing, material, invoice, and accounting documents that are available.
3. Capture the exact accounting-related error.
4. Determine whether the issue concerns missing data, document status, account determination, or another documented integration rule.
5. Use approved configuration evidence before attributing the issue to customizing.
6. Escalate to the appropriate MM/FI functional owners when resolution crosses module ownership.

## Grounding Rules

Do not invent:

- G/L accounts;
- account-determination configuration;
- valuation classes;
- movement-type configuration;
- posting keys;
- tax configuration;
- accounting-document status.

These values must come from SAP data or approved documentation.

## Human-Control Boundary

Financial posting, reversal, account-determination changes, G/L changes, and production configuration changes require authorized human execution.
