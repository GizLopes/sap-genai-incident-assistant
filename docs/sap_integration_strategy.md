# SAP Integration Strategy

## Objective

The integration strategy isolates SAP connectivity from GenAI reasoning so the assistant can move from deterministic mock data to real SAP APIs without rewriting its business-control layer.

## POC Interface

The application uses a read-oriented contract.

Conceptually:

```text
SAPClient
  -> provider.get_purchase_order()
  -> provider.get_purchase_requisition()
  -> provider.get_goods_receipt()
  -> provider.get_invoice()
  -> provider.get_vendor()
  -> provider.get_release_status()
```

The POC provider is:

```text
SAPMockClient
```

## Why an Abstraction Layer

The assistant should reason over normalized business objects rather than depend directly on a specific SAP protocol.

This provides:

- testability;
- deterministic mock scenarios;
- separation of concerns;
- easier migration to real APIs;
- centralized authorization and error handling.

## Production Provider

A production implementation can introduce a provider such as:

```text
SAPODataProvider
```

or another provider matching the APIs exposed by the customer's SAP landscape.

The implementation depends on whether the customer uses SAP S/4HANA, SAP ECC with an integration layer, SAP BTP services, or another approved exposure mechanism.

## API Preference

Use released and supported SAP APIs whenever available.

Potential mechanisms include:

- OData services;
- REST APIs;
- SOAP services where required;
- SAP BTP integration capabilities;
- RFC/BAPI through an approved enterprise integration layer when necessary.

The specific interface should be selected from the customer's SAP version and supported API catalog.

## Read-Only First

The first production integration should preserve the POC's read-only behavior.

Example:

```text
Ticket
-> Assistant
-> SAP Read API
-> Normalized SAP Object
-> Evidence Gate
-> Recommendation
```

This enables useful diagnosis without giving the model execution authority.

## Normalized Object

The integration layer should map SAP-specific payloads into application objects.

Example:

```json
{
  "po_number": "4500012345",
  "status": "BLOCKED_FOR_RELEASE",
  "release_status": "PENDING",
  "vendor_id": "V1001",
  "items": []
}
```

The model should receive only fields required for the diagnostic task.

## Error Handling

The SAP provider should distinguish:

```text
Object Not Found
Authorization Failure
API Unavailable
Timeout
Invalid Request
Unexpected SAP Response
```

These conditions should not be converted into invented SAP business diagnoses.

## Authentication

Authentication depends on the approved SAP exposure mechanism.

Production design may use:

- OAuth 2.0;
- client certificates;
- enterprise service credentials;
- SAP BTP destinations;
- another customer-approved authentication pattern.

Secrets must not be embedded in prompts or source code.

## Authorization

SAP remains the system of record for business authorization.

The assistant must not infer that application access grants SAP execution rights.

Read and write privileges should be independently controlled.

## Write Operations

Write operations are outside the current POC.

If introduced later, they should use a separate controlled action path.

```text
LLM Recommendation
-> Deterministic Action Request
-> Human Approval
-> Authorization Validation
-> SAP Action API
-> Result Validation
-> Audit
```

The model should not construct and execute arbitrary SAP requests.

## Candidate Controlled Actions

Potential future actions must be individually reviewed.

Examples:

- release a PO;
- post a Goods Receipt;
- release an invoice;
- update master data.

Each action requires explicit authorization and risk analysis.

## SAP Errors and Messages

Real SAP messages should be captured as evidence.

The assistant may explain a message using grounded knowledge, but it should preserve:

- message class where available;
- message number where available;
- original text;
- transaction/application context.

It must not invent missing message identifiers.

## Performance

Production integration should define:

- API timeout;
- retry policy;
- rate limits;
- caching rules;
- circuit-breaking behavior;
- concurrency;
- stale-data policy.

Retries must distinguish transient technical failures from functional SAP errors.

## Audit

For each SAP read, production audit should be able to record:

- request correlation ID;
- object type;
- object identifier where permitted;
- operation;
- timestamp;
- outcome;
- source system;
- evidence reference.

Sensitive SAP payloads should not be copied unnecessarily into audit storage.

## Integration Principle

The assistant consumes SAP evidence. It does not become the SAP system of record.

This boundary keeps diagnostic reasoning, authorization, and execution responsibilities explicit.
