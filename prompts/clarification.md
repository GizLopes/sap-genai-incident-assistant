# Prompt — Clarification Request

The SAP MM ticket cannot yet be analyzed reliably.

## Ticket

{{ticket_text}}

## Current Classification

Process: {{process}}

## Information Already Available

{{known_information}}

## Missing Information Identified by the Application

{{missing_information}}

## Task

Generate the smallest set of questions needed to continue the analysis.

Prioritize information that can materially change the diagnosis, such as:

- exact error message;
- affected document number;
- transaction or business process;
- current document status;
- expected behavior;
- relevant purchasing document relationship;
- whether the issue occurs consistently.

Do not request information already present in the ticket.

Do not request passwords, credentials, access tokens, secrets, or unnecessary personal data.

Do not diagnose the incident in this response.

## Required JSON Output

{
  "message": "string",
  "questions": [
    "string"
  ],
  "reason": "string"
}

Return JSON only.
