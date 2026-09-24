# Security

## Objective

The POC applies least privilege, read-only SAP access, controlled grounding, and explicit Human-in-the-Loop boundaries.

## AWS Identity

Application credentials must not be embedded in source code.

On EC2, the preferred mechanism is an IAM role attached to the instance.

The application uses the standard AWS credential provider chain.

## IAM

The EC2 role should receive only the permissions required by the POC, such as:

- invoking the selected Bedrock model;
- retrieving from the configured Bedrock Knowledge Base;
- reading approved S3 knowledge objects where directly required;
- writing and reading the dedicated DynamoDB audit table.

Wildcard permissions should be avoided where practical.

## SAP Access

The POC SAP interface is read-only.

The mock client exposes reads for:

- Purchase Orders;
- Purchase Requisitions;
- Goods Receipts;
- invoices;
- vendors;
- release status.

State-changing methods are not part of the mock execution interface.

The higher-level SAP client explicitly denies protected mutation operations.

## Production SAP Credentials

A production SAP integration should use enterprise authentication appropriate to the selected SAP API.

Credentials and secrets should be stored in an approved secret-management service, such as AWS Secrets Manager, rather than application configuration files.

## Data Minimization

Only data required for diagnosis should be sent to the model.

Production implementation should classify SAP fields and prevent unnecessary exposure of:

- personal data;
- payment data;
- credentials;
- secrets;
- sensitive commercial information.

## Logging

Audit logging should avoid storing unnecessary sensitive payloads.

The repository includes basic redaction behavior for sensitive keys.

Production logging should define:

- approved fields;
- retention;
- encryption;
- access controls;
- deletion requirements;
- audit ownership.

## Encryption

Production deployment should use encryption in transit and at rest for applicable services.

AWS-managed or customer-managed KMS keys can be selected according to enterprise policy.

## Prompt Injection

Knowledge Base content and ticket text are untrusted inputs.

They must not override:

- system instructions;
- scope controls;
- evidence requirements;
- security policy;
- HITL controls.

The application should treat retrieved instructions as document content rather than executable authority.

## Authorization

The assistant may identify evidence related to authorization issues.

It must not:

- grant access;
- bypass SAP authorization;
- recommend credential sharing;
- recommend broad emergency permissions as a default fix;
- claim that a role or authorization was changed.

## Human-in-the-Loop

State-changing actions remain outside autonomous AI control.

This is a security control as well as a business-process control.

## Network Security

The POC can use standard secured EC2 networking.

Production requirements may introduce:

- private subnets;
- controlled egress;
- VPC endpoints where supported and required;
- enterprise ingress controls;
- WAF or reverse proxy;
- private connectivity to SAP.

These controls should follow the customer's actual network topology.

## Dependency Security

Python dependencies should be pinned and scanned in CI/CD.

Production pipelines should include:

- dependency vulnerability scanning;
- secret scanning;
- static analysis;
- artifact integrity controls.

## Threats Considered

The POC explicitly considers:

- hallucinated SAP state;
- prompt injection;
- unauthorized action execution;
- excessive IAM permissions;
- sensitive-data leakage;
- malicious or stale knowledge documents;
- manipulated ticket content;
- audit-data exposure.

## POC Limitation

The technical challenge demonstrates security boundaries but is not a production security certification or complete threat model.
