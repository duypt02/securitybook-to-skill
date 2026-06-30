# Generate Red Team Workflows

Generate workflow guidance from the source document.

Each workflow entry must include:
1. Workflow name
2. Goal
3. Scope assumptions
4. Inputs
5. Steps (numbered)
6. Decision points
7. Expected outputs
8. Safety controls
9. Source reference

Quality requirements:
- Generate one workflow per major concept that has a clear procedural flow
  in the source (e.g. a testing methodology, an attack sequence, an assessment
  phase). Do not generate a single generic workflow for the whole document.
- `Steps:` must be numbered and source-derived. Do not write generic steps
  like “Plan the engagement” unless the source explicitly describes that step.
  Reference the actual tools, commands, or techniques the source names.
- `Decision points:` use the format: `If [condition] → [action]`.
  Example: `If target does not respond to ICMP → try TCP SYN scan on common ports`.
- `Source reference:` cite the concept chapter file (e.g. `chapters/information-gathering.md`)
  and the source line range from `citations.json` if available.
- If a workflow is incomplete in the source, mark the gap explicitly:
  `[GAP: source does not document this step — treat as reference-only]`.
- `Safety controls:` must include an authorization check as the first safety
  control. Never omit this item.

Rules:
- Use only the provided source content for technical steps.
- Keep workflows bounded to authorized environments.
- If a workflow is incomplete in the source, mark gaps explicitly.
