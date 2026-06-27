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
            ┌──────────────────── RED TEAM PROFILE GENERATOR ────────────────┐
            │  profiles/redteam/schema.yaml     required fields + safety      │
            │  profiles/redteam/artifacts.yaml  output artifact contract      │
            │  profiles/redteam/prompts/        artifact templates            │
            │  tools/generate_redteam_skill.py  sections, concepts, commands  │
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
```

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
| `tools/generate_redteam_skill.py` | generates Red Team/Pentest artifacts from extracted text and metadata |
| `tools/evaluate_redteam_skill.py` | evaluates required artifacts, schema sections, safety, references, citations, and benchmark coverage |
| `profiles/redteam/` | Red Team/Pentest schema, artifact contract, prompts, and benchmark expectations |
| `SKILL.md` | the original generator spec plus the Red Team/Pentest profile mode |

## Extending

- **New format** → add `parsers/<fmt>.py`, register its extension in `config.py`,
  wire dependency probing in `dependencies.py`, branch in `utils.extract_single_file`.
- **New Red Team/Pentest behavior** → edit `profiles/redteam/schema.yaml`,
  `profiles/redteam/artifacts.yaml`, the prompt templates, or the generator/evaluator
  tools; keep changes backed by benchmark evidence.
