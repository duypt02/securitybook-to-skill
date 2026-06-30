# Generate Red Team Checklist

Generate a checklist from the source document for authorized Red Team work.

The output must include these sections in order:
1. Scope and authorization checks
2. Environment and prerequisites
3. Tooling and command readiness
4. Execution checks
5. Evidence capture checks
6. Reporting and handoff checks
7. Safety and stop conditions

Quality requirements:
- Section 1 (Scope and authorization) must be the FIRST section and must
  appear before any technical or execution checks. Authorization and written
  scope approval must be explicit checklist items — not implied.
- Checklist items must be derived from actual source procedures, test cases,
  and methodology steps. Do not generate a generic checklist that could apply
  to any security assessment.
- Format each item as: `- [ ] <action verb> <specific check>`
  Good: `- [ ] Confirm written authorization covers the target IP range`
  Bad:  `- [ ] Check authorization`
- Where the source documents a specific test, tool, or step, reference it
  directly (e.g. `- [ ] Run nmap port scan per Information Gathering chapter`).
- For items not covered by the source, add the label `(generic default)`.
- Section 7 (Safety and stop conditions) must include at least one explicit
  stop condition: when to halt testing and escalate to the authorizing party.

Rules:
- Use only the provided source content where technical detail is needed.
- Do not invent target systems, credentials, or attack objectives.
- Assume lab, education, defense, or explicitly authorized testing.
- Include "not found in source" where the source lacks a required detail.
