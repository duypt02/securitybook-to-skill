# Generate Red Team SKILL.md

Generate the main Red Team Skill entry-point file from a technical document.

The output must include these schema sections:
- Skill Name
- Objective
- Context
- Preconditions
- Procedure
- Tools Commands
- Expected Outputs
- Safety Constraints
- References

Optional sections may include:
- Inputs
- Decision Points
- Troubleshooting
- Reporting Notes
- Related Skills
- Concept Chapters (index of generated chapter files)

Quality requirements:
- `Skill Name:` — use the exact source title from `metadata.json` (field `filename`
  or document title found in `full_text.txt`). Do not invent a name.
- `Objective:` — one sentence stating what the source teaches and what a practitioner
  can do after reading the generated skill.
- `Context:` — describe the document type (methodology guide, courseware, testing
  standard, etc.), extraction method, and intended use domain. 2–3 sentences.
- `Preconditions:` — list authorization requirements, environmental prerequisites,
  and legal/ethical prerequisites *before any procedure step*. Scope and written
  authorization must appear as the first items.
- `Procedure:` — numbered steps that guide the practitioner through using the skill.
  Reference the generated artifact files by name (e.g. “Review `safety.md` first”,
  “Use `checklist.md` for pre-engagement checks”, “Look up a concept in `chapters/`”).
- `Tools Commands:` — list the 5–10 most important commands from `commands.md`.
  Use the exact command strings extracted from source, with a brief source context.
- `Safety Constraints:` — 2–3 sentence summary; state that full constraints are in
  `safety.md`. Must mention: authorized use only, scope control, prohibited use.
- `References:` — list the source filename(s) from `metadata.json`.
- Add a `## Concept Chapters` index section listing all generated chapter files
  with their concept category.
- Keep the total file under 4,000 tokens. Put the most important content first
  (compaction may truncate from the end).

Rules:
- Use only the provided source content.
- Prefer concise operational structure over long summaries.
- Do not present the Skill as an autonomous attack tool.
- Do not invent commands, target systems, credentials, or objectives.
- State that all use requires explicit authorization and controlled scope.
