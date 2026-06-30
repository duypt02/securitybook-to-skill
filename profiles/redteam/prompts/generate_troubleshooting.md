# Generate Red Team Troubleshooting Guide

Generate troubleshooting notes from the source document.

Each entry must include:
1. Symptom
2. Likely cause
3. Checks
4. Fix or workaround
5. Safety or scope consideration
6. Source reference

Quality requirements:
- To find troubleshooting content, search `full_text.txt` for keywords:
  `error`, `fail`, `failed`, `timeout`, `denied`, `cannot`, `unexpected`,
  `does not`, `not found`, `rejected`, `exception`, `warning`, `incorrect`.
  Also look for source sections titled "Troubleshooting", "Common Issues",
  "Caveats", or "Limitations".
- Distinguish two types of entries clearly:
  - **Source-supported:** derived from the source text; include source reference.
  - **Prototype default:** inferred generic issue not in source; label it
    `(generic default — not from source)` and keep it minimal.
- `Symptom:` describe the observable failure, error message, or unexpected
  behavior. Be specific; avoid vague phrases like "command fails".
- `Fix or workaround:` if the source provides a solution, quote or paraphrase
  it precisely. If it does not, write `not documented in source`.
- `Safety or scope consideration:` note if the fix could affect scope,
  monitoring, or authorization (e.g. “changing firewall rules may exceed
  authorized scope”).
- Do not suggest bypassing authorization, monitoring, or safety controls.

Rules:
- Use only source-supported errors, warnings, and failure modes when possible.
- Mark inferred generic issues as "prototype default".
- Do not suggest bypassing authorization, monitoring, or safety controls.
