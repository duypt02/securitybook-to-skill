---
name: securitybook-to-skill
description: Generate a source-grounded Red Team/Pentest Agent Skill from security documents. Use when the user provides security books, OWASP/NIST/OFFSEC/PEN material, lab manuals, methodology guides, or asks to convert documents into a reusable skill with citations, commands, workflows, safety, and evaluator checks.
---

# Securitybook-to-Skill

Run **Phase 1** of the securitybook-to-skill workflow: generate a reusable Agent
Skill from source documents. Do not confuse this with Phase 2, where an already
generated skill is used during another task.

## Inputs

The user should provide one or more source paths and may provide an output slug.

Examples:

```text
$securitybook-to-skill books_test/OWASP_Testing_Guide_v4.pdf redteam-owasp-wstg
$securitybook-to-skill "books_test/OffSec - AI-300 Advanced AI Red Teaming" redteam-ai300
$securitybook-to-skill /tmp/book_skill_work/full_text.txt /tmp/book_skill_work/metadata.json redteam-owasp-direct
```

If no output slug is provided, derive one from the source filename or folder.

## Workflow

1. **Validate inputs**
   - Treat existing files, directories, and globs as source inputs.
   - Treat the final non-path argument as `output-slug` when present.
   - Use `profiles/redteam` unless the user explicitly requests another profile.

2. **Choose input mode**
   - If the inputs include both an existing `full_text.txt` and `metadata.json`, use **Direct extracted-input mode**:
     - Skip extraction.
     - Do not call `tools/generate_redteam_skill.py`.
     - Use those two files as the source of truth.
   - Otherwise, use **Source-document mode**:
     - Run extraction first to produce `full_text.txt` and `metadata.json`.
     - Then continue with Direct extracted-input mode using the extracted pair.

3. **Extract source text and metadata** *(Source-document mode only)*
   - For security, Red Team, Pentest, lab, methodology, or command-heavy sources, use technical extraction:

   ```bash
   python3 scripts/extract.py <source-paths> --mode technical --no-install-missing
   ```

   This writes:
   - `/tmp/book_skill_work/full_text.txt`
   - `/tmp/book_skill_work/metadata.json`

4. **Generate skill artifacts directly**
   Generate artifacts yourself from `full_text.txt` and `metadata.json`; do not
   call `tools/generate_redteam_skill.py` for the main path.
   - Read `metadata.json` first to identify source title, format, extraction method, token size, and source filename.
   - Use targeted searches over `full_text.txt` instead of loading the whole file when it is large.
   - Build a concept plan from source headings and Red Team/Pentest taxonomy.
   - Write the required output files directly under `outputs/<output-slug>/`.
   - Create `coverage.json` and `citations.json` manually from the concepts and line ranges you actually used.
   - Do not invent commands, credentials, targets, exploit objectives, citations, or unsupported claims.
   - Every command must keep context of use, preconditions, expected output, safety note, and source reference.
   - Mark missing details as `not found in source` or `context incomplete`.
   - Preserve authorized-use, scope-control, prohibited-use, and human-oversight constraints.

5. **Required output contract**
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

6. **Evaluate**

   ```bash
   python3 tools/evaluate_redteam_skill.py \
     outputs/<output-slug> \
     --profile profiles/redteam \
     --source /tmp/book_skill_work/full_text.txt \
     --metadata /tmp/book_skill_work/metadata.json
   ```

7. **Fix evaluator failures**
   - Fix `FAIL` items without weakening safety constraints.
   - Re-run the evaluator until it passes or unresolved issues are clearly reported.

8. **Report**
   - Output folder.
   - Evaluator pass/fail.
   - Any unresolved warnings/failures.
   - Whether sensitive source material appears to require redaction.

## Boundaries

- This skill generates skill artifacts from source documents; it does not perform penetration testing.
- Generated commands are reference material for authorized lab, education, defense, owned, or explicitly approved assessment environments only.
- If source text contains credentials, tokens, hashes, or lab secrets, flag the output for redaction before sharing.
