# Generate Red Team Reporting Guide

Generate reporting guidance from the technical document.

The output must include:
1. Evidence to capture
2. Finding structure
3. Reproduction-context fields
4. Risk and impact notes
5. Remediation or defensive follow-up
6. Chain-of-custody and data-handling notes

Quality requirements:
- `Evidence to capture:` list the specific artifact types the source recommends
  collecting (screenshots, request/response pairs, tool output, timestamps,
  hashes, log entries). Derive from the actual assessment procedures and
  chapter content — not from introductory, overview, or learning-objective
  sections of the source.
  **Do NOT copy** learning objectives ("Understand the differences between...",
  "Learn how...", "Become familiar with..."), numbered course outlines
  ("1. Low probability events"), module structure sentences
  ("In this Module, we will cover..."), or any bullet that describes what a
  student should learn rather than what a tester should collect as evidence.
  If the source has no specific evidence collection guidance, write
  3–5 generic bullets appropriate for the document's domain, each labelled
  `(generic default)`.
- `Finding structure:` provide a template finding with labeled fields.
  Required fields: Title, Severity, Asset/Scope, Reproduction steps,
  Observed result, Expected result, Impact, Remediation, Evidence references,
  Citation (cite the chapter and citation ID from citations.json).
- `Reproduction-context fields:` must include: authorization reference,
  environment (lab/prod/staging), tester, date, tool version, and scope
  boundary. These fields ensure traceability.
- `Risk and impact notes:` derive from source content. If the source does not
  characterize impact, write "not documented in source". Do not invent CVE
  numbers, CVSS scores, or real-world impact estimates not present in the source.
- `Chain-of-custody:` note how evidence files should be named, stored, and
  protected. If source is silent, include one generic default labeled
  "(generic default)".

Rules:
- Use only the provided source content for technical claims.
- Do not include sensitive real-world target data.
- Frame all reporting for authorized assessment, education, defense, or lab work.
