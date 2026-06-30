<p align="center">
  <img src="docs/assets/logo.png" alt="securitybook-to-skill logo" width="120">
</p>

<h1 align="center">securitybook-to-skill</h1>

<p align="center">
  <strong>Extend book-to-skill for Red Team and penetration-testing documents: extract technical sources with Docling, generate source-grounded security skill artifacts, and evaluate coverage, safety, commands, workflows, and references.</strong>
</p>

<p align="center">
  <a href="https://github.com/duypt02/securitybook-to-skill"><img src="https://img.shields.io/badge/Red_Team_Profile-enabled-red?style=for-the-badge" alt="Red Team profile enabled"></a>
  <img src="https://img.shields.io/badge/Agent_Skills-Open_Standard-blueviolet?style=for-the-badge" alt="Agent Skills standard">
  <img src="https://img.shields.io/badge/Docling-required-orange?style=for-the-badge" alt="Docling required">
  <img src="https://img.shields.io/badge/PDF%20%E2%80%A2%20EPUB%20%E2%80%A2%20DOCX%20%E2%80%A2%20MD%20%E2%80%A2%20HTML%20%E2%80%A2%20RTF%20%E2%80%A2%20MOBI-supported-green?style=for-the-badge" alt="Formats supported">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <a href="#-why">Why</a> ·
  <a href="#-what-it-generates">What it generates</a> ·
  <a href="#-red-teampentest-profile-prototype">Red Team/Pentest profile</a> ·
  <a href="#-beyond-books">Beyond books</a> ·
  <a href="#-usage">Usage</a> ·
  <a href="#-requirements">Requirements</a> ·
  <a href="#-how-it-works">How it works</a> ·
  <a href="#-the-discovery-loop-tax">Discovery Loop Tax</a> ·
  <a href="#-faq">FAQ</a> ·
  <a href="#-install">Install</a> ·
  <a href="CHANGELOG.md">Changelog</a> ·
  <a href="docs/PERFORMANCE.md">Performance</a> ·
  <a href="docs/ARCHITECTURE.md">Architecture</a>
</p>

<p align="center">
  <strong>Prototype focus:</strong> Red Team/Pentest Skill artifacts from OWASP, NIST, OFFSEC, PEN200, AI Red Teaming, and similar technical security documents.
</p>

**How it works, in 2 phases:**

1. **Phase 1 — Generate skills from source documents.** This is the focus of `securitybook-to-skill`: extract source text, build source-grounded Red Team/Pentest artifacts, preserve citations, and evaluate quality.
2. **Phase 2 — Use generated skills in Codex, Claude Code, or another compatible agent.** Copy or install the generated skill folder into that agent's skill directory, then invoke it during work.

The tool in this repository is primarily a **Phase 1 generator**. Phase 2 is documented so you know where the generated output goes, but the core value is compiling technical security documents into reusable skills.

---

## 🤔 Why

Red Team and penetration-testing documents are useful, but they are difficult to turn into reusable operational knowledge. A single source may mix methodology, test cases, payloads, commands, evidence requirements, reporting rules, and safety constraints.

The usual workarounds are weak for this use case:
- 📄 Searching the PDF gives isolated matches, not a structured testing workflow.
- 🧠 Asking an agent over raw text can miss source context or invent missing details.
- 📝 Manual notes rarely preserve citations, command context, safety boundaries, and reporting structure together.

**securitybook-to-skill extends the original book-to-skill pipeline with a Red Team/Pentest profile.**

The prototype extracts technical documents, generates domain-specific artifacts, and evaluates whether the output contains the required files, schema sections, commands with safety notes, authorized-use constraints, references, citations, and benchmark concept coverage.

The generated `SKILL.md` remains compatible with hosts that support the open [Agent Skills](https://github.com/agentskills/agentskills) standard, while the Red Team profile adds the extra artifacts needed for assessment, demo, and academic evaluation.

---

## 📦 What it generates

Running the Red Team profile generator creates a full output folder under `outputs/<skill-name>/`:

| File | Purpose | Size |
|------|---------|------|
| `SKILL.md` | Core mental models + chapter index | ~4,000 tokens |
| `chapters/ch01-*.md` … | One file per chapter, loaded on-demand | ~1,000 tokens each |
| `glossary.md` | Every key term, alphabetically sorted with chapter refs | ~1,500 tokens |
| `patterns.md` | All techniques, algorithms, and design patterns | ~2,000 tokens |
| `cheatsheet.md` | Decision tables and quick-reference rules | ~1,000 tokens |

For Red Team/Pentest sources, the prototype also generates `checklist.md`, `commands.md`, `workflows.md`, `troubleshooting.md`, `reporting.md`, `safety.md`, `references.md`, `coverage.json`, and `citations.json`.

---

## 🛡️ Red Team/Pentest profile prototype

This repository also contains a minimal profile-based extension for Red Team and penetration-testing documents. The extension is intentionally standalone, so the original book-to-skill pipeline remains intact while the prototype can generate domain-specific artifacts for academic evaluation and demos.

Profile files live in `profiles/redteam/`:

| File | Purpose |
|------|---------|
| `schema.yaml` | Red Team Skill fields, required sections, knowledge types, and safety constraints |
| `artifacts.yaml` | Output artifact contract for the Red Team profile |
| `prompts/` | Prompt templates for each artifact |
| `benchmarks/gold_set.json` | Evaluation expectations for OWASP, NIST, OFFSEC AI-300, and PEN200 style sources |

The Red Team generator writes the standard book-to-skill files plus Red Team-specific artifacts:

| Artifact | Purpose |
|----------|---------|
| `SKILL.md` | Main Red Team/Pentest skill entry point |
| `chapters/` | Source-grounded section files generated from document structure |
| `glossary.md`, `patterns.md`, `cheatsheet.md` | Supporting reference files compatible with the original design |
| `checklist.md` | Testing and assessment checklist |
| `commands.md` | Commands with context, placeholders, citations, and safety notes |
| `workflows.md` | Phase-oriented Red Team/Pentest workflows |
| `troubleshooting.md` | Common failure modes and fixes |
| `reporting.md` | Finding and evidence reporting guidance |
| `safety.md` | Authorized-use, scope, and operational safety constraints |
| `references.md` | Source references and citation map |
| `coverage.json`, `citations.json` | Machine-readable evaluation metadata |

### Phase 1 Demo: Generate a Skill

Use Docling for technical PDFs so tables, code blocks, and document structure are preserved:

```bash
# 1. Extract source text and metadata
python3 scripts/extract.py books_test/OWASP_Testing_Guide_v4.pdf --mode technical --no-install-missing

# 2. Ask Codex or Claude Code to generate artifacts directly from:
#    /tmp/book_skill_work/full_text.txt
#    /tmp/book_skill_work/metadata.json

# 3. Evaluate after artifacts are written
python3 tools/evaluate_redteam_skill.py \
  outputs/redteam-owasp-wstg-docling \
  --profile profiles/redteam \
  --source /tmp/book_skill_work/full_text.txt \
  --metadata /tmp/book_skill_work/metadata.json
```

The result of Phase 1 is a complete generated skill folder under `outputs/<skill-name>/`.

### Phase 2 Preview: Use the Generated Skill

After Phase 1, copy the generated folder into the skill location for your agent:

| Agent | Typical personal skill directory | Project-local skill directory |
|-------|----------------------------------|-------------------------------|
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| GitHub Copilot CLI | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/` or `.agents/skills/` |
| Amp | `~/.agents/skills/` or `~/.config/agents/skills/` | `.agents/skills/` |

Example for Codex project-local usage:

```bash
mkdir -p .agents/skills
cp -R outputs/redteam-owasp-wstg-docling .agents/skills/redteam-owasp-wstg
```

Then restart/open Codex in this repo and ask it to use the generated skill by name.

### Agent runtime upgrade

The Red Team helper script still supports three generation modes, but it is not
the preferred quality path when a capable harness such as Codex or Claude Code is
available:

| Mode | Behavior |
|------|----------|
| `--mode rule` | Preserves the original deterministic Python generator contract. |
| `--mode agent` | Renders profile prompts for artifact generation. Useful when you want prompt bundles instead of direct agent generation. |
| `--mode hybrid` | Python extracts sections, concepts, commands, citations, coverage, and safety checks; a provider supplies artifact Markdown. Use this for fallback/demo runs, not as the preferred quality path. |

Providers are intentionally local by default:

| Provider | Purpose |
|----------|---------|
| `--provider mock` | Deterministic fallback used by tests and demos; no API key or network access required. |
| `--provider manual` | Writes prompt bundles to `outputs/<skill>/prompt_runs/` so Codex CLI, Claude Code, or another agent can generate the final artifacts. |

Recommended Codex/Claude Code setup: call the `securitybook-to-skill` skill with
the extracted pair and let the harness generate artifacts directly.

```text
$securitybook-to-skill /tmp/book_skill_work/full_text.txt /tmp/book_skill_work/metadata.json redteam-owasp-direct
```

Deterministic regression/demo fallback:

```bash
python3 tools/generate_redteam_skill.py \
  /tmp/book_skill_work/full_text.txt \
  /tmp/book_skill_work/metadata.json \
  --profile profiles/redteam \
  --out outputs/redteam-owasp-wstg-mock \
  --mode hybrid \
  --provider mock \
  --max-revisions 1
```

Direct agent generation from `full_text.txt` and `metadata.json` is the preferred quality path because Codex or Claude Code can synthesize richer prose than the rule-based fallback while still preserving source grounding. The `mock` provider exists for reproducible tests, regression checks, and demos where no external agent should write prose.

Use `--mode rule` when you want the original deterministic generator. Use `--provider manual --dry-run-prompts` only when you specifically want prompt bundles instead of direct extracted-input generation.

For an extracted HTML folder such as OFFSEC AI-300:

```bash
python3 scripts/extract.py "books_test/OffSec - AI-300 Advanced AI Red Teaming" --mode technical --no-install-missing
```

### Current benchmark snapshot

The prototype has been tested against representative Red Team/Pentest sources under `books_test/`:

| Source | Expected concept coverage | Weak concepts | Commands extracted | Evaluator result | Notes |
|--------|---------------------------|---------------|--------------------|------------------|-------|
| OWASP Web Security Testing Guide | 12 found | 1 | 11 | PASS, rubric 100/100 | Strong methodology coverage; limited explicit shell commands in source |
| NIST SP 800-115 | 12 found | 0 | 0 real commands | PASS, rubric 100/100 | Methodology document; command count is not a suitable quality metric |
| OFFSEC AI-300 | 13 found | 0 | 80 | PASS, rubric 100/100 | Strong command and AI red-team workflow extraction |
| PEN200/OSCP material | 20 found | 2 | 80 | PASS, rubric 100/100 | Strong lab-oriented command coverage; some concepts need deeper expansion |

Quality caveats for report/demo use:

- Red Team/Pentest documents differ by purpose. NIST-style methodology documents should be evaluated by process, evidence, and reporting quality, not command count.
- Offensive training material may include lab credentials, tokens, or exploit strings from the source. Production use should add a redaction layer before publishing generated artifacts.
- OWASP-style web testing documents contain many procedures and payload examples, but fewer standalone terminal commands. Improving request/payload extraction is a future enhancement.

Supporting development notes and improvement history are kept in `NOTES.md`.

---

## 🏢 Beyond books

The name says "book", but the input is any structured prose. The same extraction works on knowledge you own and re-read constantly:

- **Internal documentation** — architecture decision records, runbooks, onboarding guides. Fold a whole `docs/` folder into one skill and ask it while you code.
- **Brand & design systems** — voice guidelines, tone-of-voice docs, component principles. Turn a brand book into a skill your team queries instead of skimming a 60-page PDF.
- **Research clusters** — a stack of papers plus your own notes, merged into a single unified skill and updated as new material lands (see [Update / fold-in](#-usage)).
- **Specs & standards** — RFCs, API contracts, compliance docs you reference but never memorize.

If you re-open a document often enough to wish you'd memorized it, it's a candidate.

---

## 🚀 Usage

The workflow has two separate phases. `securitybook-to-skill` focuses on **Phase 1: generating the skill**. Phase 2 depends on the host agent that will consume the generated folder.

## Phase 1 — Generate a Skill with securitybook-to-skill

Phase 1 is split into two parts:

1. Python extraction produces `full_text.txt` and `metadata.json`.
2. Codex or Claude Code reads those two files and writes the final skill artifacts directly, then the evaluator checks the result.

This is the recommended quality path because pure rule-based generation is useful for regression tests, but it is too limited for rich skill prose.

### Harness command entrypoints

If you want to start Phase 1 from an agent harness instead of copying the full prompt manually:

Important distinction: installing a workflow into a `skills/` directory makes it
available as a **skill**, not automatically as a top-level `/name` slash command.
Skills are normally invoked through the harness skill UI, an explicit skill
mention such as `$securitybook-to-skill`, or implicit matching. Literal slash
commands such as `/securitybook-to-skill` require a separate command/prompt shim
for the harness.

| Harness | Entrypoint | Setup |
|---------|------------|-------|
| Codex skill | `/skills` then choose `securitybook-to-skill`, or mention `$securitybook-to-skill` | Repo-local skill lives at `.agents/skills/securitybook-to-skill/SKILL.md`. Restart Codex if it does not appear. This is the preferred Codex surface. |
| Claude Code | `/securitybook-to-skill <source-path> [output-slug]` | Repo-local command lives at `.claude/commands/securitybook-to-skill.md`. Restart Claude Code if it does not appear. |

Codex note: the recommended Codex surface is the repo-local skill in `.agents/skills/securitybook-to-skill/`. Use `/skills` or `$securitybook-to-skill` to invoke it.

### 1. Check dependencies

```bash
python3 scripts/extract.py --check
```

For technical PDFs, install Docling first:

```bash
pip3 install docling
```

### 2. Extract a source document

For PDFs with code blocks, tables, commands, or security methodology, use technical mode:

```bash
python3 scripts/extract.py books_test/OWASP_Testing_Guide_v4.pdf --mode technical --no-install-missing
```

For an HTML/document folder such as OFFSEC AI-300:

```bash
python3 scripts/extract.py "books_test/OffSec - AI-300 Advanced AI Red Teaming" --mode technical --no-install-missing
```

Extraction writes:

| File | Purpose |
|------|---------|
| `/tmp/book_skill_work/full_text.txt` | Source-marked extracted text used by Codex/Claude Code or fallback helpers |
| `/tmp/book_skill_work/metadata.json` | Extraction metadata, source list, format, and extraction method |

If you already have those two files, you can skip extraction. In that direct
mode, Codex/Claude Code should generate artifacts directly from the extracted
files and should not call `tools/generate_redteam_skill.py`.

### 3. Generate artifacts directly with Codex or Claude Code

Recommended path when extraction has already produced `full_text.txt` and
`metadata.json`:

```text
$securitybook-to-skill /tmp/book_skill_work/full_text.txt /tmp/book_skill_work/metadata.json redteam-owasp-direct
```

Or tell Codex/Claude Code directly:

```text
Generate a Red Team/Pentest Agent Skill directly from:
- /tmp/book_skill_work/full_text.txt
- /tmp/book_skill_work/metadata.json

Write the output to:
outputs/redteam-owasp-direct/

Do not call tools/generate_redteam_skill.py. Build the concept plan, chapters,
commands, workflows, safety guidance, coverage.json, and citations.json yourself
from the extracted source and metadata. Then run the evaluator and fix FAIL items
without weakening safety constraints.
```

The final output folder should contain:

| Output | Purpose |
|--------|---------|
| `SKILL.md` | Main skill entry point |
| `chapters/*.md` | Source-grounded concept chapters |
| `checklist.md`, `commands.md`, `workflows.md` | Operational artifacts with safety context |
| `troubleshooting.md`, `reporting.md`, `safety.md`, `references.md` | Support, reporting, authorized-use, and citation guidance |
| `coverage.json`, `citations.json` | Machine-readable coverage and source traceability |
| `evaluation.json`, `quality_report.md` | Generation quality result, evaluator messages, revision count, and sensitive-source flag |

### 4. Evaluate explicitly

Run the evaluator manually after Codex/Claude Code writes the artifacts:

```bash
python3 tools/evaluate_redteam_skill.py \
  outputs/redteam-owasp-wstg-docling \
  --profile profiles/redteam \
  --source /tmp/book_skill_work/full_text.txt \
  --metadata /tmp/book_skill_work/metadata.json
```

### 5. Optional helper/fallback modes

| Goal | Command options |
|------|-----------------|
| Recommended quality path | Call `$securitybook-to-skill /tmp/book_skill_work/full_text.txt /tmp/book_skill_work/metadata.json <slug>` and let Codex/Claude Code generate artifacts directly |
| Render prompt bundles instead of direct generation | `--mode agent --provider manual --dry-run-prompts` |
| Deterministic regression/demo run | `--mode hybrid --provider mock --max-revisions 1` |
| Preserve the original deterministic renderer | `--mode rule --provider mock` |
| Save prompt bundles while also writing deterministic fallback artifacts | `--mode hybrid --provider manual` |

Deterministic fallback run:

```bash
python3 tools/generate_redteam_skill.py \
  /tmp/book_skill_work/full_text.txt \
  /tmp/book_skill_work/metadata.json \
  --profile profiles/redteam \
  --out outputs/redteam-owasp-wstg-mock \
  --mode hybrid \
  --provider mock \
  --max-revisions 1
```

Use this fallback when you need reproducible CI output or want to debug extraction/evaluator behavior without relying on Codex/Claude Code prose generation.

### 6. Review before use

Before using or sharing generated artifacts:

- Read `quality_report.md`; if `Result: FAIL`, inspect the evaluator messages.
- If `sensitive_source_material: true`, redact credentials, tokens, passwords, hashes, or lab secrets before publishing.
- Treat `commands.md` as authorized-use reference material only. Every command must keep its context, preconditions, expected output, safety note, and source reference.
- Use generated skills only in lab, education, defense, owned, or explicitly authorized assessment environments.

Supported document formats still come from the original extractor: PDF, EPUB, DOCX, TXT, Markdown, reStructuredText, AsciiDoc, HTML, RTF, MOBI/AZW/AZW3.

## Phase 2 — Use the Generated Skill in an Agent

Phase 2 starts after `outputs/<skill-name>/` exists and has passed review. This phase is not the main generator pipeline; it is how you consume the generated output in Codex, Claude Code, or another compatible agent.

### Codex

Use a project-local skill when you want the generated Red Team/Pentest skill available only inside this repo:

```bash
mkdir -p .agents/skills
cp -R outputs/redteam-owasp-wstg-docling .agents/skills/redteam-owasp-wstg
codex
```

Prompt Codex:

```text
Use the redteam-owasp-wstg skill to help me prepare an authorized web pentest checklist.
Stay within scope, use the skill's safety guidance, and cite the generated artifacts you read.
```

Use a personal skill when you want it available across repos:

```bash
mkdir -p ~/.agents/skills
cp -R outputs/redteam-owasp-wstg-docling ~/.agents/skills/redteam-owasp-wstg
codex
```

Restart Codex if it does not detect the new skill.

### Claude Code

Use a project-local skill:

```bash
mkdir -p .claude/skills
cp -R outputs/redteam-owasp-wstg-docling .claude/skills/redteam-owasp-wstg
```

Or use a personal skill:

```bash
mkdir -p ~/.claude/skills
cp -R outputs/redteam-owasp-wstg-docling ~/.claude/skills/redteam-owasp-wstg
```

Restart Claude Code, then ask it to use the generated skill:

```text
Use the redteam-owasp-wstg skill. Build a scoped, authorized test workflow from its checklist, workflows, commands, and safety artifacts.
```

### Important Boundary

Do not confuse the phases:

- Phase 1 asks Codex/Claude Code to **generate or improve a skill from documents**. That is what this repository automates.
- Phase 2 asks Codex/Claude Code to **use an already generated skill** during another task. That happens after the generated folder is copied into the agent's skill directory.

---

## 🔧 Requirements

The extractor tries tools in order per format and uses the first available. If nothing is installed, it tells you which command to run. Plain text, Markdown, reStructuredText and AsciiDoc need no extra deps.

> **Check your setup in one command:** `python3 scripts/extract.py --check` prints which extractors are installed for every format and the exact command to install anything missing — no file needed.

**PDF — choose by book type:**

| Book type | Tool | Install | Speed |
|-----------|------|---------|-------|
| Text-heavy (prose, few tables) | `pdftotext` (poppler) | `sudo apt install poppler-utils` | ⚡ instant |
| Text-heavy fallback | `pypdf` | `pip3 install pypdf` | ⚡ instant |
| Text-heavy fallback | `pdfminer.six` | `pip3 install pdfminer.six` | ⚡ instant |
| **Technical (code, tables, formulas)** | **`docling`** | `pip3 install docling` | ~1.5s/page |

> Before extraction begins, the skill asks you whether the book is **technical** or **text-heavy** and picks the right tool automatically. Docling preserves markdown tables and code blocks; pdftotext is faster for prose-only books.

**EPUB:**

| Tool | Install | Quality |
|------|---------|---------|
| `ebooklib` + `beautifulsoup4` | `pip3 install ebooklib beautifulsoup4` | ⭐⭐⭐ Best |
| stdlib `zipfile` | built-in — no install needed | ⭐⭐ Always available |

**Other formats:**

| Format | Tool | Install |
|--------|------|---------|
| DOCX | `python-docx` (fallback: stdlib ZIP/XML) | `pip3 install python-docx` |
| HTML | `beautifulsoup4` (fallback: stdlib `html.parser`) | `pip3 install beautifulsoup4` |
| RTF | `striprtf` (fallback: regex) | `pip3 install striprtf` |
| MOBI / AZW / AZW3 | Calibre `ebook-convert` (external app, not pip) | https://calibre-ebook.com/download |
| TXT / Markdown / reStructuredText / AsciiDoc | built-in | — |

---

## ⚙️ How it works

```
Red Team/Pentest source
PDF · HTML folder · DOCX · Markdown · text
     │
     ▼
scripts/extract.py --mode technical
     │
     ├── PDF technical mode → Docling  (tables + code blocks as markdown)
     └── other supported formats → original book-to-skill extractors
     │
     ▼
 /tmp/book_skill_work/full_text.txt
 /tmp/book_skill_work/metadata.json
               │
               ▼
 profiles/redteam/
   schema.yaml      → required sections, fields, safety constraints
   artifacts.yaml   → output artifact contract
   prompts/         → artifact templates
               │
               ▼
 Codex or Claude Code (recommended)
   reads full_text.txt + metadata.json
   writes rich Markdown artifacts directly
   fixes evaluator FAIL items without weakening safety
               │
               ▼
 outputs/<skill-name>/
   SKILL.md · chapters/ · checklist.md · commands.md
   workflows.md · troubleshooting.md · reporting.md
   safety.md · references.md · coverage.json · citations.json
   evaluation.json · quality_report.md
               │
               ▼
 tools/evaluate_redteam_skill.py
   checks required artifacts, schema sections, command context,
   safety constraints, references, citations, and benchmark coverage

 Optional side path:
 tools/generate_redteam_skill.py
   deterministic fallback, CI regression helper, or prompt-bundle renderer
```

**Extraction benchmark** (103-page technical book, CPU only):

| Method | Time | Tokens | Tables | Code blocks |
|--------|------|--------|--------|-------------|
| pdftotext | 0.1s | 27K | 0 | 0 |
| Docling | 164s | 27K (+1.2%) | 48 | 36 |

**Real conversions** (measured: pages, extracted tokens, chapters auto-detected,
estimated one-pass cost on Claude Sonnet 4.5 at \$3/\$15 per MTok):

| Book | Format | Pages | Tokens | Chapters | ~Cost |
|------|--------|------:|-------:|---------:|------:|
| Think Python 2 | PDF | 244 | 119K | 19 | \$0.88 |
| Working Backwards | PDF | 371 | 175K | 10 | \$0.96 |
| Pro Git | PDF | 501 | 229K | — † | \$1.23 |
| Moby-Dick | EPUB | — | 301K | — † | \$1.42 |

† Chapter auto-detection needs explicit `Chapter N` / `Capítulo N` headings. Pro Git
uses section titles and Moby-Dick uses chapter *titles* / roman numerals, so neither
auto-segments — extraction and conversion still work, but you point at sections
manually. A full skill costs roughly **\$1 per book**; far less than re-reading the
PDF every session.

<details>
<summary>Design principles (click to expand)</summary>

1. **Density over completeness** — a 1,000-token summary beats a 10,000-token excerpt
2. **Practitioner voice** — "Use X when Y", not "The book explains X"
3. **Front-loaded SKILL.md** — compaction keeps the first ~5,000 tokens; the most important content comes first
4. **On-demand chapters** — the topic index tells Claude which file to read; chapters load only when needed
5. **Never raw text** — always synthesize, summarize, extract signal from the source

</details>

---

## 🧾 The Discovery Loop Tax

A PDF-reading agent doesn't just read — it *navigates*. Ask it one question and it
fetches the table of contents, notices a term it can't define, pulls more pages,
backtracks. Every one of those hops lands in the conversation history and gets
**re-processed on every subsequent turn**. To stay inside its budget, a sub-agent
is then forced to compress what it read at brutal ratios, handing the main agent a
**degraded summary it can't fact-check** against the source.

The compiled skill format pays the navigation cost **once, at compile time**. At runtime the
assistant loads a small resident core plus the one pre-compiled chapter it needs —
no discovery loop, no compress-to-fit, and the full extracted source stays on disk
for verification.

**Measured, not asserted.** Running [`tools/discovery_tax.py`](tools/discovery_tax.py)
on three real books — tokens entering context to answer a single targeted question
(skill format = resident core + one compiled chapter ≈ 5,000 tokens):

| Book (size) | Context-dump | Discovery loop | skill format | vs dump / loop |
|-------------|-------------:|---------------:|--------------:|:--------------:|
| Think Python 2 (119K, small chapters) | 119,264 | 12,152 | ~5,000 | 24× / **2.4×** |
| Working Backwards (175K, medium chapters) | 175,253 | 33,444 | ~5,000 | 35× / 6.7× |
| AI Engineering (256K, large chapters) | 256,287 | 77,866 | ~5,000 | 51× / **15.6×** |

The advantage **scales with chapter size**: against a context-dump it's consistently
24–51× (and that cost recurs *every turn*); against a one-time discovery loop it
ranges from a modest 2.4× on a book of small chapters to 15.6× on one of large
chapters. Reproduce on your own book:

```bash
python3 tools/discovery_tax.py --full-text /tmp/book_skill_work/full_text.txt --target-chapter 5
```

> **Honest caveats:** (1) the discovery figures are a one-time cost and a *model*
> using the book's real ToC/chapter sizes — a well-tuned agent lands nearer the best
> case; the context-dump cost, by contrast, recurs on **every** turn. (2) The tool
> needs explicit `Chapter N` / `Capítulo N` headings to segment a book; titles-only
> or roman-numeral books (and EPUBs extracted without `ebooklib`) won't segment
> cleanly. A compiled skill wins when you return to the knowledge repeatedly; for a
> single one-off read, a plain PDF agent is fine.

---

## ❓ FAQ

**"Can't I just dump the PDF/EPUB into my Claude project context?"**

You can — but every conversation will burn that token budget upfront. A 400-page book is ~200K tokens. With a skill, only the chapters relevant to your question load — typically a SKILL.md core (~4K) plus the one chapter you asked about (~1K). The rest stays on disk until you need it.

The economics are amortization, not size. Pasting the book pays the full token bill **on every turn of every session, forever**. A compiled skill pays the extraction cost **once** and every future conversation loads only the slice it needs. The bigger your context window, the more this matters — a large window makes the dump *possible*, not *cheap*.

More importantly: raw text injection is retrieval. A skill is reasoning. When you load a chapter file, Claude isn't searching for keyword matches — it's working with pre-extracted named frameworks, principles, and mental models structured for application, not for reading.

---

**"Claude has a 1M-token context window now — can't I just keep the whole book loaded?"**

A bigger window changes what *fits*, not what's *smart*. Three reasons it isn't a substitute:

- **You pay per token, per call.** A 1M window doesn't make those tokens free — it makes a large, recurring bill possible. The skill loads kilobytes, not megabytes.
- **Recall degrades with fill.** Models lose precision retrieving a specific fact buried in a near-full context ("lost in the middle"). A 1K curated chapter beats 200K of raw prose for answering one question.
- **Window ≠ structure.** A full book in context is still raw text the model must re-parse every turn. The skill ships pre-extracted frameworks — reasoning, not retrieval.

Use the big window for what it's good at: a one-off pass over material you'll never need again. Use a skill for knowledge you'll reach for repeatedly.

---

**"Isn't this just RAG?"**

RAG works at query time: chunk the book → embed everything → find similar vectors → inject into prompt. It's optimized for "find me the part that talks about X."

The skill-generation approach works at compile time: one deep analysis run extracts the author's actual frameworks, names them, describes when to use each, captures the anti-patterns. In this prototype, the Red Team/Pentest profile specializes that idea for security testing procedures, commands, workflows, reporting, safety, references, and citations.

RAG answers: *"here are chunks close to your query."*  
A skill answers: *"here are the 12 frameworks this author built, ready to reason with."*

Pick by shape of the job:

- **Wide and shallow** — a library of dozens of books, "find the part that mentions X" → a RAG tool (e.g. CandleKeep) wins.
- **Narrow and deep** — one security guide or a tight cluster of related sources, procedures you apply while you work → securitybook-to-skill wins.

They're complementary, not competing: RAG indexes a shelf, securitybook-to-skill compiles a focused Red Team/Pentest source into a reusable skill.

---

**"Popular books are already in Claude's training data. Why bother?"**

For widely-known books (Clean Code, DDIA, Pragmatic Programmer), Claude has general knowledge — but it's compressed, averaged across the entire internet's discussion of the book, and may hallucinate specific quotes or chapter locations.

securitybook-to-skill works from your actual copy. Every procedure, command, section, and reference is grounded in the text you provided. No training data drift, no hallucinated chapter titles.

It also shines for books Claude doesn't know at all: niche technical references, internal company documentation, recent publications, translated works.

---

**"NotebookLM handles multiple books better."**

Absolutely true — if your workflow is "I have 80 separate books and I want to search across all of them," NotebookLM is the right tool.

securitybook-to-skill is built for a different job: you want to go deep on a specific Red Team/Pentest topic, fold related documents into a single skill, and evaluate whether the generated artifacts contain the required safety, command, reporting, workflow, reference, and citation coverage.

---

## 📥 Install

Clone this prototype repository:

```bash
git clone https://github.com/duypt02/securitybook-to-skill.git
cd securitybook-to-skill
```

Install the required technical PDF extractor:

```bash
pip3 install docling
```

Check the extractor environment:

```bash
python3 scripts/extract.py --check
```

Then run the Red Team/Pentest workflow from the [Usage](#-usage) section.

The original `book-to-skill` Python package metadata is intentionally kept for compatibility with the upstream extractor internals. The Red Team/Pentest extension is exposed through `profiles/redteam/`, `tools/generate_redteam_skill.py`, and `tools/evaluate_redteam_skill.py`.

---

## 📁 Repository structure

```
securitybook-to-skill/
├── SKILL.md              # Skill definition + step-by-step instructions (the generator spec)
├── profiles/redteam/     # Red Team/Pentest schema, artifacts, prompts, and benchmark expectations
├── scripts/
│   ├── extract.py        # Thin entrypoint wrapper
│   └── extractor/        # Modular extraction package
│       ├── config.py     # Extensions, paths, dependency constants
│       ├── dependencies.py  # optional-dep probing + --check
│       ├── exceptions.py # ExtractionError (per-source failures, batch-safe)
│       ├── utils.py      # CLI parsing, multi-source resolution, chapter detection, runner
│       └── parsers/      # Format-specific parsers (pdf, epub, docx, html, rtf, calibre, text)
├── tools/
│   ├── discovery_tax.py  # measures token cost vs context-dump / discovery loop
│   ├── generate_redteam_skill.py   # optional Red Team/Pentest fallback/helper generator
│   ├── evaluate_redteam_skill.py   # Red Team/Pentest quality evaluator
│   └── validate_skill.py # checks a generated SKILL.md against host rules (--lens claude|copilot|amp)
├── tests/                # pytest suite (extraction, detection, discovery tax)
├── docs/
│   ├── PERFORMANCE.md    # measured benchmarks, discovery tax, cost
│   └── ARCHITECTURE.md   # pipeline + component map
├── CHANGELOG.md          # release history (semver)
├── CONTRIBUTING.md       # dev setup, PR conventions, release process
├── SECURITY.md           # vulnerability reporting
└── README.md             # This file
```

---

## ⚖️ Copyright & fair use

securitybook-to-skill ships **no book content** — not a single page. It's a converter you point at files you already own or are authorized to process.

- **Processing is local.** Extraction and analysis run on your machine. Your files are never uploaded by this tool. (If your agent's model runs in the cloud, the text you feed it follows that provider's normal data terms — same as any prompt.)
- **You use your own copy.** Bring a book you bought, docs your company owns, or papers you have the right to read.
- **The output is your notes.** A generated skill is a structured, synthesized derivative — framework names, definitions, takeaways — not a reproduction of the text. The skill explicitly never copies raw passages (see Quality Rule #7). Treat it like handwritten study notes: yours, for personal use.
- **Don't redistribute.** Publishing or sharing a generated skill of a copyrighted work can infringe the rights holder. Keep skills of third-party books private. Internal docs, your own writing, and openly-licensed material are fine to share within the bounds of their license.

When in doubt, follow the license or terms of the source document. This project is a tool; how you use it is on you.

---

## License

MIT — applies to the converter (code + skill definition) in this repository, **not** to any book or document you process with it.
