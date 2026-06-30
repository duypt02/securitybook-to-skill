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
   - Mark missing details as `not found in source` or `context incomplete`.
   - Preserve authorized-use, scope-control, prohibited-use, and human-oversight constraints.

   **Per-chapter command extraction (required):**
   For each concept chapter, search the source text *within that concept's section* for
   commands, code blocks, shell prompts, tool invocations, and example calls. Specifically
   look for:
   - Lines starting with shell prompts: `kali@kali:~$`, `PS C:\>`, `msf6>`, `meterpreter>`
   - Lines inside fenced code blocks (``` or ~~~)
   - Inline tool invocations: `nmap`, `impacket-*`, `crackmapexec`, `mimikatz`, `rubeus`,
     `bloodhound`, `chisel`, `hashcat`, `hydra`, `msfconsole`, `searchsploit`, etc.
   If the section contains them, list them in the chapter's `Related Commands` block and in
   `commands.md`. Do not copy commands from unrelated sections. If a section genuinely
   has no commands after a thorough search, state `No commands documented in source for this concept.` — do not
   write `No source-supported commands detected` as a catch-all.

   **Source Summary formatting (required):**
   Each bullet in `## Source Summary` must be a clean prose sentence or concise extracted
   fact. Strip all raw markdown heading markers (`##`, `###`, `####`) from extracted text
   before writing bullets. Never start a bullet with `- ## Heading Name` or
   `- ### Sub-heading`. Rewrite the heading as a prose sentence if the information is
   relevant (e.g. `- The source covers X in section Y.`).
   Also filter out:
   - Truncated sentences that end mid-word or without punctuation (Docling extraction
     artifacts, e.g. `- Next, we'll get  famil` — skip these entirely)
   - Footnote or reference lines (e.g. `- 1068 (Microsoft, 2003), https://...`)
   - Learning objective bullets (`- Understand X`, `- Learn how to Y`, `- Become familiar with Z`)
   - Course structure bullets (`- In this Module, we will cover...`, `- This Learning Unit covers...`)
   Only include bullets that convey substantive technical content about the concept.

   **Source-Derived Procedure specificity (required):**
   Steps in `## Source-Derived Procedure` must be derived from the actual test cases,
   numbered procedures, tool sequences, or methodological steps found in *that concept's
   section* of the source. Avoid repeating the same generic 6-step template across all
   chapters. Reference the specific tests, tool names, or numbered steps the source uses.
   If the source has no procedure for a concept, write a single step:
   `No explicit procedure documented; treat as reference-only knowledge.`

   **Command metadata quality (required):**
   - `Purpose:` — one sentence describing *what the command accomplishes* (e.g. "Enumerate
     open ports on a target host" or "Test for HTTP method support on a web server"). Never
     write "Source-supported command or tool invocation."
   - `Context of use:` — state *when, where, and why* this command is used in the
     assessment workflow. Minimum 25 words. Do not copy a raw sentence fragment from the
     source that describes output or response, not usage context.
   - `Expected output:` — describe the expected output if the source provides it; otherwise
     write `not documented in source`.

5. **Per-artifact prompt guidance (required for quality)**
   Before writing each artifact, read its prompt template from
   `profiles/redteam/prompts/` if one exists:

   | Artifact | Prompt file |
   |----------|-------------|
   | `SKILL.md` | `profiles/redteam/prompts/generate_skill.md` |
   | `checklist.md` | `profiles/redteam/prompts/generate_checklist.md` |
   | `commands.md` | `profiles/redteam/prompts/generate_commands.md` |
   | `workflows.md` | `profiles/redteam/prompts/generate_workflows.md` |
   | `troubleshooting.md` | `profiles/redteam/prompts/generate_troubleshooting.md` |
   | `reporting.md` | `profiles/redteam/prompts/generate_reporting.md` |
   | `safety.md` | `profiles/redteam/prompts/generate_safety.md` |
   | `references.md` | `profiles/redteam/prompts/generate_references.md` |

   Each prompt defines the required sections, quality rules, and output
   constraints for that artifact. The rules in those files are in addition
   to the quality requirements in Step 4 above — not instead of them.
   For artifacts without a prompt file (`glossary.md`, `patterns.md`,
   `cheatsheet.md`, `coverage.json`, `citations.json`), use the description
   in `profiles/redteam/artifacts.yaml` as guidance.

6. **Required output contract**
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

7. **Evaluate**

   ```bash
   python3 tools/evaluate_redteam_skill.py \
     outputs/<output-slug> \
     --profile profiles/redteam \
     --source /tmp/book_skill_work/full_text.txt \
     --metadata /tmp/book_skill_work/metadata.json
   ```

8. **Fix evaluator failures**
   - Fix `FAIL` items without weakening safety constraints.
   - Re-run the evaluator until it passes or unresolved issues are clearly reported.

9. **Report**
   - Output folder.
   - Evaluator pass/fail.
   - Any unresolved warnings/failures.
   - Whether sensitive source material appears to require redaction.

## Boundaries

- This skill generates skill artifacts from source documents; it does not perform penetration testing.
- Generated commands are reference material for authorized lab, education, defense, owned, or explicitly approved assessment environments only.
- If source text contains credentials, tokens, hashes, or lab secrets, flag the output for redaction before sharing.
