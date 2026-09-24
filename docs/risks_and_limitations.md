# Risks and Limitations

## POC Scope

The solution is a bounded technical prototype for SAP MM support-ticket analysis.

It is not a production SAP support platform.

## Mock SAP Data

The POC uses simulated SAP records.

Risk:

The mock dataset cannot reproduce all SAP customizing, document relationships, authorization behavior, exits, BAdIs, workflows, or customer-specific configuration.

Mitigation:

A production implementation should retrieve authoritative data through approved SAP APIs.

## Small Knowledge Corpus

The RAG corpus contains a deliberately small set of SAP MM process documents and AI-control policies.

Risk:

Real incidents may require SAP Notes, customer procedures, customizing documentation, or cross-module knowledge not represented in the POC.

Mitigation:

Introduce governed enterprise knowledge sources and retrieval evaluation.

## LLM Error

Grounding reduces hallucination risk but does not eliminate it.

Risk:

The model can still misinterpret evidence or generate unsupported language.

Mitigation:

- Evidence Gate;
- structured outputs;
- citations;
- deterministic confidence;
- forbidden-action controls;
- HITL;
- regression evaluation.

## Retrieval Error

Relevant knowledge may fail to rank highly enough.

Risk:

A correct document can exist but not be retrieved.

Mitigation:

Measure retrieval recall and precision, improve metadata and chunking, and tune retrieval using labeled cases.

## Conflicting Evidence

SAP data, tickets, and documentation may disagree.

Risk:

Automatically selecting one source can create an incorrect diagnosis.

Mitigation:

Detect conflict, reduce confidence, preserve source references, and escalate.

## Confidence Is Not Probability

The application confidence score is a control heuristic.

Risk:

Users may interpret `0.85` as an 85% probability that the diagnosis is correct.

Mitigation:

Display confidence as a decision-support level and explain its inputs.

## Authorization Complexity

SAP authorization analysis can depend on roles, profiles, authorization objects, organizational levels, and runtime context.

Risk:

The POC cannot reproduce full SAP authorization trace behavior.

Mitigation:

Route actual authorization changes and complex diagnosis to SAP security specialists.

## Cross-Module Incidents

Some MM incidents involve FI, SD, PP, WM/EWM, QM, or external systems.

Risk:

A narrow MM scope may abstain on valid business issues.

Mitigation:

Explicit routing and future domain expansion.

## No Autonomous Execution

The POC intentionally does not perform state-changing SAP operations.

This is a functional limitation and a safety property.

## Evaluation Dataset

The initial evaluation dataset is small and scenario-driven.

Risk:

Perfect results on the baseline do not establish general accuracy.

Mitigation:

Expand with real anonymized historical tickets, edge cases, adversarial cases, and SAP expert labels.

## Baseline Evidence

Repository evidence files are deterministic baseline artifacts.

They are not live Bedrock execution results.

Live deployment should generate separately versioned evidence.

## Latency and Cost

The repository baseline does not measure real model latency or cost.

Production evaluation should capture:

- model latency;
- retrieval latency;
- total response time;
- input/output tokens;
- cost per request.

## Availability

The POC does not define production SLA/SLO, high availability, disaster recovery, or multi-region operation.

## Data Privacy

The mock dataset contains fictitious data.

Production implementation requires customer-specific data classification, retention, privacy, and access policies.

## Model Changes

Managed models can evolve or be replaced.

Risk:

Behavior can change after model or prompt updates.

Mitigation:

Pin configuration where possible, record model identifiers, and run regression evaluation before promotion.

## Final Boundary

The assistant is a diagnostic decision-support tool. Authorized SAP professionals remain responsible for business decisions and execution.
