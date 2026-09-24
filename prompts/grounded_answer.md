Analyze the SAP MM incident using the supplied ticket, SAP context, and retrieved evidence.

Return exactly one JSON object with this structure:

{
  "summary": "string",
  "possible_causes": [
    "string"
  ],
  "recommended_checks": [
    "string"
  ],
  "missing_information": [
    "string"
  ]
}

Field requirements:

summary:
- Summarize the observed issue.
- Use confirmed facts from the supplied context.
- Do not introduce unsupported SAP configuration details.

possible_causes:
- Include only explanations supported by the supplied evidence.
- Describe them as possible causes unless explicitly confirmed by SAP context.
- Return an empty list when no supported cause can be identified.

recommended_checks:
- Provide diagnostic or read-only verification steps.
- Do not instruct the assistant to perform SAP state-changing operations.
- Human-controlled actions may be mentioned only as requiring authorized human execution.

missing_information:
- Identify information required for a stronger diagnosis.
- Return an empty list when the supplied context is sufficient.

Do not return:
- confidence scores;
- confidence levels;
- grounding scores;
- HITL decisions;
- invented citations;
- invented SAP values;
- Markdown;
- text outside the JSON object.