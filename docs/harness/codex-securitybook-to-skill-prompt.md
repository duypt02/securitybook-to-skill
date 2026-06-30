---
description: Generate a source-grounded Red Team/Pentest Agent Skill from security documents
argument-hint: "<source-path-or-folder> [output-slug]"
---

You are running Phase 1 of securitybook-to-skill: generate a reusable Agent Skill
from source documents. Do not confuse this with Phase 2, where an already
generated skill is used during another task.

Inputs:
- Source path(s) and optional output slug: `$ARGUMENTS`
- Default profile: `profiles/redteam`
- Default output directory: `outputs/<output-slug>`

Workflow:

1. Parse `$ARGUMENTS`.
   - Treat existing files/directories/globs as source inputs.
   - Treat the final non-path argument as `output-slug` when present.
   - If no output slug is present, derive one from the source filename/folder.

2. Choose input mode.
   - If `$ARGUMENTS` includes both an existing `full_text.txt` and `metadata.json`, use Direct extracted-input mode:
     - Skip extraction.
     - Do not call `tools/generate_redteam_skill.py`.
     - Use those two files as the source of truth.
   - Otherwise, use Source-document mode:
     - Run extraction first to produce `full_text.txt` and `metadata.json`.
     - Then continue with Direct extracted-input mode using the extracted pair.

3. Extract source text and metadata. *(Source-document mode only)*
   - For security, Red Team, Pentest, lab, methodology, or command-heavy sources, use technical extraction:

   ```bash
   python3 scripts/extract.py <source-paths> --mode technical --no-install-missing
   ```

4. Generate skill artifacts directly.
   - Generate artifacts yourself from `full_text.txt` and `metadata.json`; do not call `tools/generate_redteam_skill.py` for the main path.
   - Read `metadata.json` first to identify source title, format, extraction method, token size, and source filename.
   - Use targeted searches over `full_text.txt` instead of loading the whole file when it is large.
   - Build a concept plan from source headings and Red Team/Pentest taxonomy.
   - Write the required output files directly under `outputs/<output-slug>/`.
   - Create `coverage.json` and `citations.json` manually from the concepts and line ranges you actually used.
   - Do not invent commands, credentials, targets, exploit objectives, citations, or unsupported claims.
   - Every command must keep context of use, preconditions, expected output, safety note, and source reference.
   - Missing source details must be marked `not found in source` or `context incomplete`.
   - Preserve authorized-use, scope-control, prohibited-use, and human-oversight constraints.

5. Required output contract.
   Write these files before evaluation:
   - `SKILL.md`
   - `chapters/*.md`
   - `glossary.md`
   - `patterns.md`
   - `cheatsheet.md`
   - `checklist.md`
   - `commands.md`
   - `workflows.md`
   - `troubleshooting.md`
   - `reporting.md`
   - `safety.md`
   - `references.md`
   - `coverage.json`
   - `citations.json`

6. Evaluate the generated skill.

   ```bash
   python3 tools/evaluate_redteam_skill.py \
     outputs/<output-slug> \
     --profile profiles/redteam \
     --source /tmp/book_skill_work/full_text.txt \
     --metadata /tmp/book_skill_work/metadata.json
   ```

7. Fix evaluator `FAIL` items without weakening safety constraints.

8. Report:
   - Output folder.
   - Whether evaluator passed.
   - Any unresolved warnings/failures.
   - Whether sensitive source material appears to require redaction.
