---
hide:
  - navigation
  - toc
---

# securitybook-to-skill

<p style="font-size: 1.25rem; max-width: 42rem;">
Generate Red Team and penetration-testing skill artifacts from technical security documents. The prototype keeps the original book-to-skill extraction model, adds a `profiles/redteam/` contract, and evaluates generated artifacts for coverage, safety, commands, workflows, and references.
</p>

[Get started](guide.md){ .md-button .md-button--primary }
[Skill reference](skill-reference.md){ .md-button }
[GitHub](https://github.com/duypt02/securitybook-to-skill){ .md-button }

---

## Why securitybook-to-skill

<div class="grid cards" markdown>

-   :material-shield-search:{ .lg .middle } __Red Team/Pentest profile__

    ---

    Domain schema, artifact contract, and prompt templates for OWASP, NIST,
    OFFSEC, PEN200, AI Red Teaming, and similar technical security material.

-   :material-file-document-multiple:{ .lg .middle } __Docling-aware extraction__

    ---

    Technical mode preserves source structure for PDFs and document folders,
    then feeds the profile generator through `full_text.txt` and `metadata.json`.

-   :material-console:{ .lg .middle } __Security artifacts__

    ---

    Generates `SKILL.md`, chapters, checklist, commands, workflows,
    troubleshooting, reporting, safety, references, coverage, and citations.

-   :material-check-decagram:{ .lg .middle } __Evaluator-backed demo__

    ---

    Checks required artifacts, schema sections, command context, authorized-use
    constraints, references, source citations, and benchmark concept coverage.

</div>

## Install

**Clone the Red Team/Pentest prototype:**

```bash
git clone https://github.com/duypt02/securitybook-to-skill.git
cd securitybook-to-skill
python3 scripts/extract.py books_test/OWASP_Testing_Guide_v4.pdf --mode technical --no-install-missing
```

**Generate and evaluate a Red Team skill:**

```bash
python3 tools/generate_redteam_skill.py \
  /tmp/book_skill_work/full_text.txt \
  /tmp/book_skill_work/metadata.json \
  --profile profiles/redteam \
  --out outputs/redteam-owasp-wstg-docling

python3 tools/evaluate_redteam_skill.py \
  outputs/redteam-owasp-wstg-docling \
  --profile profiles/redteam \
  --source /tmp/book_skill_work/full_text.txt \
  --metadata /tmp/book_skill_work/metadata.json
```

## Learn more

<div class="grid cards" markdown>

-   :material-sitemap:{ .lg .middle } __[Architecture](ARCHITECTURE.md)__

    ---

    How the deterministic extractor and the profile-driven generator fit together.

-   :material-speedometer:{ .lg .middle } __[Performance](PERFORMANCE.md)__

    ---

    The measured Discovery Loop Tax and real per-conversion token cost.

-   :material-book-open-page-variant:{ .lg .middle } __[Skill Reference](skill-reference.md)__

    ---

    The full `SKILL.md` spec: every step, depth budget, and quality rule.

-   :material-shield-check:{ .lg .middle } __Red Team profile__

    ---

    See `profiles/redteam/`, `tools/generate_redteam_skill.py`, and
    `tools/evaluate_redteam_skill.py` for the academic prototype implementation.

</div>
