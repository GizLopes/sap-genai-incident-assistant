# Prompt — SAP Scope Classification

Classify whether the ticket belongs to the supported SAP MM scope.

## Supported Scope

SAP Materials Management (MM):

- Purchase Requisition
- Purchase Order
- Release Strategy
- Goods Receipt
- Invoice Verification
- Purchasing-related vendor/material issues
- MM authorization issues
- MM/FI integration directly related to purchasing

## Explicitly Unsupported for this POC

Examples include:

- SAP HR/HCM;
- SAP SD issues unrelated to MM;
- SAP PP issues unrelated to MM;
- unrelated IT support;
- general questions without a SAP MM relationship.

A process touching FI may remain in scope when the reported issue originates from the MM purchasing or invoice-verification flow.

## Ticket

{{ticket_text}}

## Task

Classify the ticket using only the information explicitly available.

If there is not enough information to determine scope, return `UNCLEAR` rather than guessing.

## Required JSON Output

{
  "classification": "IN_SCOPE | OUT_OF_SCOPE | UNCLEAR",
  "sap_module": "MM | OTHER | UNKNOWN",
  "process": "string or null",
  "reason": "string",
  "matched_indicators": [
    "string"
  ]
}

## Rules

- Do not diagnose the incident.
- Do not invent a SAP module from weak contextual clues.
- `UNCLEAR` is valid when the ticket lacks sufficient process information.
- Return JSON only.
