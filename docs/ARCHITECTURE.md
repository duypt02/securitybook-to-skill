# Architecture

securitybook-to-skill keeps the original **deterministic extractor** (Python) and
adds a Red Team/Pentest **profile-driven generator**. The extractor turns technical
documents into clean text + metadata; the Red Team profile turns that into
source-grounded security artifacts.

```
            ┌─────────────────────────── EXTRACTOR (Python, deterministic) ──┐
 documents  │  scripts/extract.py  →  extractor/                              │
 (pdf/epub/ │    ├─ utils.py        CLI parse · multi-source resolve · runner │
  docx/...) │    ├─ config.py       supported extensions · paths · deps map   │
     │      │    ├─ dependencies.py optional-dep probing · --check report     │
     ▼      │    └─ parsers/        pdf · epub · docx · html · rtf · calibre · │
 ───────────│                        text  (best tool first, stdlib fallback) │
            │  output → <tempdir>/book_skill_work/                            │
            │    full_text.txt   (all sources merged, source-marked)          │
            │    metadata.json   (pages, words, tokens, chapters, ToC)        │
            └────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
            ┌──────────────────── RED TEAM SKILL GENERATION ─────────────────┐
            │  profiles/redteam/schema.yaml     required fields + safety      │
            │  profiles/redteam/artifacts.yaml  output + prompt contract      │
            │  profiles/redteam/prompts/        artifact prompt templates     │
            │  Codex / Claude Code                                            │
            │    ├─ reads full_text.txt + metadata.json                       │
            │    ├─ plans concepts · commands · workflows · citations         │
            │    ├─ writes Markdown artifacts + coverage/citation JSON        │
            │    └─ fixes evaluator failures without weakening safety         │
            │  tools/generate_redteam_skill.py  optional baseline/fallback    │
            │  tools/evaluate_redteam_skill.py  quality + coverage checks     │
            └────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                outputs/<skill-name>/
                  SKILL.md             main Red Team/Pentest skill
                  chapters/*.md        source-grounded section files
                  glossary.md          terms
                  patterns.md          techniques and procedures
                  cheatsheet.md        quick reference
                  checklist.md         testing and assessment checklist
                  commands.md          commands with context and safety notes
                  workflows.md         phase-oriented workflows
                  troubleshooting.md   failure modes and fixes
                  reporting.md         evidence and finding guidance
                  safety.md            authorized-use constraints
                  references.md        source references
                  coverage.json        benchmark coverage data
                  citations.json       citation map
                  evaluation.json      evaluator result and messages
                  quality_report.md    human-readable quality summary
                  prompt_runs/*.md     optional prompt-bundle helper output
```

## Generation paths

The intended high-quality harness path does not call
`tools/generate_redteam_skill.py`. Codex or Claude Code should read the extracted
pair directly:

```text
/tmp/book_skill_work/full_text.txt
/tmp/book_skill_work/metadata.json
```

Then the harness writes the artifacts, `coverage.json`, and `citations.json`
itself, preserving source grounding and safety constraints.

`tools/generate_redteam_skill.py` remains as an optional deterministic baseline,
prompt-bundle helper, and regression fallback:

| Mode | Responsibility split |
|------|----------------------|
| `rule` | Python writes all artifacts with the existing deterministic renderers. |
| `agent` | Python renders source-grounded prompt bundles. Use only when you want prompt bundles instead of direct extracted-input generation. |
| `hybrid` | Python performs extraction-derived planning, command discovery, citations, coverage, schema checks, and safety checks; a provider supplies Markdown prose. Use this as a fallback/demo path unless a real LLM provider is wired in. |

The current providers are deliberately local:

| Provider | Behavior |
|----------|----------|
| `mock` | Deterministic provider for tests and reproducible demos. It returns evaluator-safe Markdown from the existing renderers. |
| `manual` | Writes rendered prompt bundles under `outputs/<skill>/prompt_runs/` for Codex CLI, Claude Code, or another human-steered agent to execute. In non-dry-run mode it also writes deterministic fallback Markdown so the output remains complete. |

The provider interface accepts `artifact_name`, `prompt`, `source_context`,
`schema`, and `metadata`, and returns Markdown. Future API providers can plug
into this interface without changing `profiles/redteam/schema.yaml` or
`artifacts.yaml`.

## Quality loop

For the recommended Codex/Claude Code flow, the harness writes artifacts directly
from `full_text.txt` and `metadata.json`, then runs
`tools/evaluate_redteam_skill.py`. For non-dry-run fallback flows, the helper
generator writes artifacts, runs the evaluator internally, and records results in
`evaluation.json` and `quality_report.md`.

The safety layer also scans source text for likely credentials, tokens,
passwords, and lab secrets. Matches set `sensitive_source_material: true` in the
quality report so generated artifacts can be reviewed and redacted before
publication.

## Design principles

1. **Extract structure, not summaries** — named frameworks, decision rules,
   anti-patterns; never raw passages.
2. **Compile-time over runtime** — pay navigation/structuring once; at query time
   load only the relevant chapter. See [PERFORMANCE.md](PERFORMANCE.md).
3. **On-demand chapters** — `SKILL.md` stays small; chapter files cost tokens only
   when read.
4. **Front-loaded `SKILL.md`** — most important content first (compaction truncates
   from the end).
5. **Graceful degradation** — every format has a stdlib fallback; one bad source is
   skipped, not fatal.

## Key components

| Path | Responsibility |
|------|----------------|
| `scripts/extract.py` | thin entrypoint wrapper |
| `scripts/extractor/utils.py` | CLI parsing, multi-source resolution, chapter/ToC detection, runner |
| `scripts/extractor/parsers/` | one module per format |
| `scripts/extractor/dependencies.py` | optional-dependency probing + `--check` |
| `tools/discovery_tax.py` | measures token cost vs context-dump / discovery loop |
| `tools/validate_skill.py` | checks a generated SKILL.md against host rules (`--lens claude|copilot|amp`) |
| `tools/generate_redteam_skill.py` | optional deterministic baseline, prompt-bundle helper, and fallback artifact generator |
| `tools/evaluate_redteam_skill.py` | evaluates required artifacts, schema sections, safety, references, citations, and benchmark coverage |
| `profiles/redteam/` | Red Team/Pentest schema, artifact contract, prompts, and benchmark expectations |
| `SKILL.md` | the original generator spec plus the Red Team/Pentest profile mode |

## Extending

- **New format** → add `parsers/<fmt>.py`, register its extension in `config.py`,
  wire dependency probing in `dependencies.py`, branch in `utils.extract_single_file`.
- **New Red Team/Pentest behavior** → edit `profiles/redteam/schema.yaml`,
  `profiles/redteam/artifacts.yaml`, the prompt templates, or the generator/evaluator
  tools; keep changes backed by benchmark evidence.
