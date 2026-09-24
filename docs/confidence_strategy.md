# Confidence Strategy

## Objective

Confidence is an application control used to determine how strongly the assistant may present a grounded assessment and when human review is required.

The LLM does not assign its own authoritative confidence score.

## Inputs

The POC combines four signals:

```text
Retrieval Quality
Completeness
Evidence Coverage
Source Agreement
```

## Formula

The current implementation uses:

```text
Confidence =
    0.35 * Retrieval Quality
  + 0.20 * Completeness
  + 0.30 * Evidence Coverage
  + 0.15 * Source Agreement
```

Each input is normalized between `0.0` and `1.0`.

## Levels

```text
HIGH    >= 0.80
MEDIUM  >= 0.60 and < 0.80
LOW     < 0.60
```

## Retrieval Quality

Represents the strength of the retrieved knowledge evidence.

A high retrieval score alone is insufficient for HIGH confidence because the request may still be incomplete or sources may disagree.

## Completeness

Represents whether the information required to analyze the ticket is available.

Examples of missing information:

- document number;
- exact error message;
- relevant item;
- transaction context.

Missing critical context lowers confidence and can trigger clarification before generation.

## Evidence Coverage

Represents how much of the diagnostic conclusion is supported by available evidence.

A response with several unsupported causal claims should not receive high coverage.

## Source Agreement

Represents whether the relevant evidence sources are mutually consistent.

Conflicting evidence lowers this signal and can independently trigger HITL.

## Confidence vs. Action Authority

Confidence does not grant execution authority.

Example:

```text
Confidence = HIGH
Action = Release Purchase Order
Result = HUMAN VALIDATION REQUIRED
```

Protected SAP actions remain human-controlled regardless of confidence.

## Confidence vs. Evidence Gate

The Evidence Gate and confidence serve different purposes.

```text
Evidence Gate
-> Is there enough acceptable evidence to continue?

Confidence
-> How strong is the resulting grounded assessment?
```

A request can fail the Evidence Gate before a meaningful confidence value is used.

## Display

The UI should expose:

- level;
- score where useful;
- evidence sources;
- reason for escalation.

The score should not be presented as a statistical probability that the diagnosis is correct.

## Calibration

The current thresholds are POC design thresholds.

Production calibration should use labeled SAP support cases and compare confidence bands with observed diagnostic quality.

Calibration should evaluate whether:

- HIGH cases actually have lower error rates;
- LOW cases are correctly escalated;
- thresholds create excessive or insufficient escalation.

## Audit

Production audit records should retain the confidence inputs and resulting level so decisions can be reconstructed.
