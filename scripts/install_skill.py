#!/usr/bin/env python3
"""
install_skill.py — Install securitybook-to-skill into AI harnesses.

TWO MODES:

  MODE 1 — Install the TOOL itself (default, no --output flag):
    python3 scripts/install_skill.py [options]
    python3 scripts/install_skill.py --tool [options]

    Installs the securitybook-to-skill workflow skill so agents can invoke
    it with /securitybook-to-skill or $securitybook-to-skill.
    Source: .agents/skills/securitybook-to-skill/SKILL.md (this project)

  MODE 2 — Install a GENERATED OUTPUT skill:
    python3 scripts/install_skill.py --output <slug> [options]

    Installs a skill previously generated under outputs/<slug>/ into
    harnesses so agents can query it by topic/chapter.

Harnesses:
    copilot   → ~/.agents/skills/<name>/SKILL.md
    claude    → ~/.claude/skills/<name>/SKILL.md + ~/.claude/commands/<name>.md
    opencode  → ~/.config/opencode/skills/<name>/SKILL.md
    codex     → ~/.codex/skills/<name>/SKILL.md
    local     → .agents/skills/<name>/SKILL.md + .claude/commands/<name>.md (CWD)

Options:
    --harness   copilot,claude,opencode,codex,local,all  (default: all)
    --name      Override install name
    --dry-run   Print actions without writing
    --force     Overwrite existing files
    --copy-chapters  Copy chapters/ dir (--output mode only)

Examples:
    # Install the TOOL itself into all harnesses (primary use)
    python3 scripts/install_skill.py

    # Install tool into claude + codex only
    python3 scripts/install_skill.py --harness claude,codex

    # Install a generated output skill
    python3 scripts/install_skill.py --output redteam-pen200-harness --copy-chapters

    # Dry-run preview
    python3 scripts/install_skill.py --dry-run
    python3 scripts/install_skill.py --output redteam-owasp-wstg-docling --dry-run

    # List detected harnesses
    python3 scripts/install_skill.py --list-harnesses
"""

import argparse
import re
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# HARNESS CONFIGURATIONS
# ---------------------------------------------------------------------------

HARNESSES = {
    "copilot": {
        "label": "GitHub Copilot / Agents",
        "skill_dir": Path.home() / ".agents" / "skills",
        "adapter": "copilot",
    },
    "claude": {
        "label": "Claude Code",
        "skill_dir": Path.home() / ".claude" / "skills",
        "command_dir": Path.home() / ".claude" / "commands",
        "adapter": "claude",
    },
    "opencode": {
        "label": "OpenCode",
        "skill_dir": Path.home() / ".config" / "opencode" / "skills",
        "adapter": "opencode",
    },
    "codex": {
        "label": "Codex",
        "skill_dir": Path.home() / ".codex" / "skills",
        "adapter": "codex",
    },
    "local": {
        "label": "Local project (.agents/ + .claude/)",
        "skill_dir": Path.cwd() / ".agents" / "skills",
        "command_dir": Path.cwd() / ".claude" / "commands",
        "adapter": "claude",
    },
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def write_file(path: Path, content: str, dry: bool, force: bool) -> bool:
    if dry:
        print(f"  [WRITE] {path}")
        return True
    if path.exists() and not force:
        print(f"  [SKIP]  {path} (exists — use --force to overwrite)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  [OK]    {path}")
    return True


def copy_file(src: Path, dst: Path, dry: bool, force: bool) -> bool:
    if not src.exists():
        return False
    if dry:
        print(f"  [COPY]  {dst}")
        return True
    if dst.exists() and not force:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  [COPY]  {dst}")
    return True


def parse_frontmatter(text: str) -> tuple:
    """Split YAML frontmatter from body. Returns (fm_dict, body)."""
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm_block = text[3:end].strip()
            body = text[end + 3:].lstrip("\n")
            for line in fm_block.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def find_repo_root() -> Path:
    """Find the securitybook-to-skill project root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# MODE 1: TOOL INSTALL
# Install the securitybook-to-skill WORKFLOW SKILL into harnesses
# ---------------------------------------------------------------------------

def _fix_tool_paths(body: str, repo_root: Path) -> str:
    """Replace relative project paths with absolute paths for global installs."""
    rel_to_abs = {
        "profiles/redteam": str(repo_root / "profiles" / "redteam"),
        "scripts/extract.py": str(repo_root / "scripts" / "extract.py"),
        "tools/evaluate_redteam_skill.py": str(repo_root / "tools" / "evaluate_redteam_skill.py"),
        "tools/generate_redteam_skill.py": str(repo_root / "tools" / "generate_redteam_skill.py"),
        "tools/validate_skill.py": str(repo_root / "tools" / "validate_skill.py"),
        ".agents/skills/securitybook-to-skill/SKILL.md": str(
            repo_root / ".agents" / "skills" / "securitybook-to-skill" / "SKILL.md"
        ),
    }
    for rel, abs_path in rel_to_abs.items():
        body = re.sub(
            r'(?<![/\w])' + re.escape(rel),
            abs_path,
            body,
        )
    return body


def make_tool_copilot(name: str, desc: str, body: str) -> str:
    return f"---\nname: {name}\ndescription: >\n  {desc}\n---\n\n{body}"


def make_tool_claude_skill(name: str, desc: str, body: str) -> str:
    fm = (
        f"---\n"
        f"name: {name}\n"
        f"description: {desc}\n"
        f'argument-hint: "<source-path-or-folder> [output-slug]"\n'
        f"---\n"
    )
    return fm + "\n" + body


def make_tool_claude_command(name: str, desc: str, skill_ref: str) -> str:
    return "\n".join([
        "---",
        f"description: {desc}",
        'argument-hint: "<source-path-or-folder> [output-slug]"',
        "---",
        "",
        "<!--",
        f"Dispatch stub for: {name}",
        f"Canonical: {skill_ref}",
        "-->",
        "",
        "Arguments: `$ARGUMENTS`",
        "",
        f"Read `{skill_ref}` and follow every step of the workflow",
        "defined there, substituting `$ARGUMENTS` for the source paths and optional output slug.",
        "",
    ])


def make_tool_opencode(name: str, desc: str, body: str) -> str:
    fm = (
        f"---\n"
        f"name: {name}\n"
        f'description: "{desc}"\n'
        f"trigger: /{name}\n"
        f'argument-hint: "<source-path-or-folder> [output-slug]"\n'
        f"---\n"
    )
    return fm + "\n" + body


def make_tool_codex(name: str, desc: str, body: str, repo_root: Path) -> str:
    fm = (
        f'---\n'
        f'name: "{name}"\n'
        f'description: "{desc}"\n'
        f'metadata:\n'
        f'  short-description: "{desc}"\n'
        f'---\n'
    )
    adapter = "\n".join([
        "<codex_skill_adapter>",
        "## A. Skill Invocation",
        f"- Invoked by mentioning `${name}`.",
        f"- Syntax: `${name} <source-path-or-folder> [output-slug]`",
        "- `<source-path-or-folder>` — PDF, HTML folder, EPUB, or pre-extracted txt+json pair.",
        "- `[output-slug]` — optional name for the output directory under `outputs/`.",
        "",
        "## B. Workflow Translation (Codex)",
        "1. Parse SKILL_ARGS: source path(s) + optional trailing slug.",
        f"2. **Extraction**: run `python3 {repo_root}/scripts/extract.py <paths> --mode technical` via Bash.",
        "3. **Generate artifacts** inline from `full_text.txt` + `metadata.json`.",
        f"4. **Evaluate**: `python3 {repo_root}/tools/evaluate_redteam_skill.py outputs/<slug> --profile {repo_root}/profiles/redteam --source /tmp/book_skill_work/full_text.txt --metadata /tmp/book_skill_work/metadata.json`.",
        "5. Fix FAIL items, re-evaluate until passing.",
        "",
        "## C. Tool Mappings",
        "- `AskUserQuestion` → `request_user_input`",
        "- `Task(subagent_type=X, prompt=Y)` → `spawn_agent(agent_type=X, message=Y)`",
        "- Bash tool for shell commands; Read/Write/Edit for artifacts.",
        "",
        "## D. Safety",
        "- Generated skills are reference material for authorized environments only.",
        "- Do not invent commands, credentials, or exploit objectives not in source.",
        "</codex_skill_adapter>",
        "",
    ])
    return fm + "\n" + adapter + "\n" + body


def install_tool(harness_name, harness_cfg, install_name, skill_md_path, repo_root, dry, force):
    """Install the securitybook-to-skill TOOL into one harness."""
    raw = skill_md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)
    desc = fm.get("description", "Generate a source-grounded Red Team/Pentest skill from security documents.")
    # Do not truncate — the full description is needed for accurate skill triggering.

    body_fixed = _fix_tool_paths(body, repo_root)
    adapter = harness_cfg["adapter"]
    skill_dir = harness_cfg["skill_dir"] / install_name

    print(f"\n  → {harness_cfg['label']}")
    print(f"    {skill_dir}")

    if adapter == "copilot":
        write_file(skill_dir / "SKILL.md", make_tool_copilot(install_name, desc, body_fixed), dry, force)

    elif adapter == "claude":
        write_file(skill_dir / "SKILL.md", make_tool_claude_skill(install_name, desc, body_fixed), dry, force)
        if "command_dir" in harness_cfg:
            if harness_name == "local":
                skill_ref = f".agents/skills/{install_name}/SKILL.md"
            else:
                skill_ref = str(Path.home() / ".claude" / "skills" / install_name / "SKILL.md")
            cmd = make_tool_claude_command(install_name, desc, skill_ref)
            write_file(harness_cfg["command_dir"] / f"{install_name}.md", cmd, dry, force)

    elif adapter == "opencode":
        write_file(skill_dir / "SKILL.md", make_tool_opencode(install_name, desc, body_fixed), dry, force)

    elif adapter == "codex":
        write_file(skill_dir / "SKILL.md", make_tool_codex(install_name, desc, body_fixed, repo_root), dry, force)


# ---------------------------------------------------------------------------
# MODE 2: OUTPUT INSTALL
# Install a generated skill from outputs/<slug>/ into harnesses
# ---------------------------------------------------------------------------

def parse_output_skill(skill_md_path: Path) -> dict:
    content = skill_md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    name_match = re.search(r"^##\s+Skill Name\s*\n(.+?)(?=\n##|\Z)", body, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else fm.get("name", "")

    obj_match = re.search(r"^##\s+Objective\s*\n(.+?)(?=\n##|\Z)", body, re.MULTILINE | re.DOTALL)
    desc = ""
    if obj_match:
        desc = obj_match.group(1).strip().splitlines()[0].strip()
    if not desc:
        desc = fm.get("description", name)
    if len(desc) > 200:
        desc = desc[:197] + "..."

    return {"body": body, "name": name, "description": desc, "slug": slugify(name) if name else ""}


def install_output(harness_name, harness_cfg, install_name, skill, output_dir, copy_chapters, dry, force):
    """Install a generated OUTPUT skill into one harness."""
    adapter = harness_cfg["adapter"]
    skill_dir = harness_cfg["skill_dir"] / install_name
    desc = skill["description"]
    body = skill["body"]

    print(f"\n  → {harness_cfg['label']}")
    print(f"    {skill_dir}")

    # Build content per adapter
    if adapter == "copilot":
        content = f"---\nname: {install_name}\ndescription: >\n  {desc}\n---\n\n{body}\n"
    elif adapter == "claude":
        content = (
            f"---\nname: {install_name}\n"
            f"description: {desc}\n"
            f'argument-hint: "[chapter|topic|keyword]"\n'
            f"---\n\n{body}\n"
        )
    elif adapter == "opencode":
        content = (
            f"---\nname: {install_name}\n"
            f'description: "{desc}"\n'
            f"trigger: /{install_name}\n"
            f"---\n\n{body}\n"
        )
    elif adapter == "codex":
        fm = (
            f'---\nname: "{install_name}"\n'
            f'description: "{desc}"\n'
            f'metadata:\n  short-description: "{desc}"\n'
            f'---\n'
        )
        adapter_block = "\n".join([
            "<codex_skill_adapter>",
            "## A. Skill Invocation",
            f"- Invoked by mentioning `${install_name}`.",
            f"- Treat user text after `${install_name}` as `{{SKILL_ARGS}}`.",
            "- Empty: list chapter index. Chapter name: load that chapter. Keyword: search chapters.",
            "",
            "## B. Tool Mappings",
            "- `AskUserQuestion` → `request_user_input`",
            "- Read chapter files with the Read tool. Do not invent facts.",
            "",
            "## C. Authorization",
            "- All procedures require explicit written authorization and defined scope.",
            "</codex_skill_adapter>",
            "",
        ])
        content = fm + "\n" + adapter_block + "\n" + body + "\n"

    write_file(skill_dir / "SKILL.md", content, dry, force)

    # Command dispatch stub (claude / local only)
    if "command_dir" in harness_cfg:
        cmd = "\n".join([
            "---",
            f"description: {desc}",
            'argument-hint: "[chapter|topic|keyword]"',
            "---",
            "",
            "Arguments: `$ARGUMENTS`",
            "",
            f"Read `.claude/skills/{install_name}/SKILL.md` and follow the workflow,",
            "substituting `$ARGUMENTS` for the chapter, topic, or keyword.",
            "",
        ])
        write_file(harness_cfg["command_dir"] / f"{install_name}.md", cmd, dry, force)

    # Supporting artifacts
    for fname in [
        "cheatsheet.md", "checklist.md", "commands.md", "workflows.md",
        "glossary.md", "safety.md", "troubleshooting.md", "reporting.md",
        "references.md", "patterns.md", "quality_report.md",
        "coverage.json", "citations.json", "evaluation.json",
    ]:
        copy_file(output_dir / fname, skill_dir / fname, dry, force)

    # Chapters
    chapters_src = output_dir / "chapters"
    if chapters_src.is_dir() and copy_chapters:
        chapters_dst = skill_dir / "chapters"
        if dry:
            n = len(list(chapters_src.iterdir()))
            print(f"  [COPY]  {chapters_dst}/ ({n} files)")
        elif not chapters_dst.exists() or force:
            if chapters_dst.exists():
                shutil.rmtree(chapters_dst)
            shutil.copytree(chapters_src, chapters_dst)
            n = len(list(chapters_dst.iterdir()))
            print(f"  [COPY]  {chapters_dst}/ ({n} files)")
    elif chapters_src.is_dir():
        n = len(list(chapters_src.iterdir()))
        note = (
            f"# Chapters Index\n\nSource: `{chapters_src}`\n\n"
            f"This skill has {n} concept chapters.\n"
            f"Use `--copy-chapters` to include them locally.\n\n"
        )
        for ch in sorted(chapters_src.iterdir()):
            note += f"- [{ch.stem}]({chapters_src}/{ch.name})\n"
        write_file(skill_dir / "CHAPTERS_INDEX.md", note, dry, False)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Install securitybook-to-skill into AI harnesses.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode_grp = parser.add_mutually_exclusive_group()
    mode_grp.add_argument("--tool", action="store_true",
                          help="(Default) Install the securitybook-to-skill tool workflow")
    mode_grp.add_argument("--output", metavar="SLUG",
                          help="Install a generated skill from outputs/<SLUG>/")

    parser.add_argument("--harness", default="all",
                        help="copilot,claude,opencode,codex,local,all  (default: all)")
    parser.add_argument("--name", help="Override install name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--copy-chapters", action="store_true",
                        help="Copy chapters/ dir (--output mode only)")
    parser.add_argument("--list-harnesses", action="store_true",
                        help="List harnesses and exit")

    args = parser.parse_args()

    if args.list_harnesses:
        print("Supported harnesses:")
        for k, v in HARNESSES.items():
            p = v["skill_dir"]
            mark = "✓" if p.exists() else "✗"
            print(f"  {k:10s}  {mark}  {v['label']:35s}  → {p}")
        return 0

    repo_root = find_repo_root()
    dry_label = "DRY-RUN" if args.dry_run else "INSTALL"

    # Resolve harness list
    chosen = [h.strip().lower() for h in args.harness.split(",")]
    if "all" in chosen:
        chosen = [h for h in HARNESSES if h != "local"]
    unknown = [h for h in chosen if h not in HARNESSES]
    if unknown:
        print(f"ERROR: Unknown harness(es): {', '.join(unknown)}")
        return 1

    # -----------------------------------------------------------------------
    # MODE 1 — Install the TOOL
    # -----------------------------------------------------------------------
    if not args.output:
        tool_skill = repo_root / ".agents" / "skills" / "securitybook-to-skill" / "SKILL.md"
        if not tool_skill.exists():
            print(f"ERROR: Tool SKILL.md not found:\n  {tool_skill}")
            return 1

        install_name = args.name or "securitybook-to-skill"

        print(f"\n{'='*62}")
        print(f"  securitybook-to-skill :: {dry_label} [TOOL]")
        print(f"{'='*62}")
        print(f"  Source  : {tool_skill}")
        print(f"  Install : {install_name}")
        print(f"  Targets : {', '.join(chosen)}")
        print(f"{'='*62}")

        errors = []
        for h in chosen:
            try:
                install_tool(h, HARNESSES[h], install_name, tool_skill, repo_root,
                             args.dry_run, args.force)
            except Exception as e:
                errors.append((h, e))
                print(f"  [ERROR] {h}: {e}")

        print(f"\n{'='*62}")
        if errors:
            for h, e in errors:
                print(f"  [ERROR] {h}: {e}")
            return 1
        print(f"  Done. Tool '{install_name}' installed into: {', '.join(chosen)}")
        print()
        if "claude" in chosen:
            print(f"    Claude Code : /{install_name} <source-path> [output-slug]")
        if "opencode" in chosen:
            print(f"    OpenCode    : /{install_name} <source-path> [output-slug]")
        if "codex" in chosen:
            print(f"    Codex       : ${install_name} <source-path> [output-slug]")
        if "copilot" in chosen:
            print(f"    Copilot     : invoke skill '{install_name}' with source path")
        print(f"{'='*62}\n")
        return 0

    # -----------------------------------------------------------------------
    # MODE 2 — Install a generated OUTPUT skill
    # -----------------------------------------------------------------------
    slug = args.output
    output_dir = None
    for c in [Path(slug), repo_root / "outputs" / slug, Path("outputs") / slug]:
        if c.is_dir() and (c / "SKILL.md").exists():
            output_dir = c.resolve()
            break

    if not output_dir:
        print(f"ERROR: Cannot find outputs/{slug}/ with a SKILL.md.")
        return 1

    skill = parse_output_skill(output_dir / "SKILL.md")
    if not skill["name"]:
        skill["name"] = slug.replace("redteam-", "").replace("-", " ").title()
        skill["slug"] = slugify(skill["name"])

    install_name = args.name or skill["slug"] or slugify(slug)

    print(f"\n{'='*62}")
    print(f"  securitybook-to-skill :: {dry_label} [OUTPUT SKILL]")
    print(f"{'='*62}")
    print(f"  Source  : {output_dir}")
    print(f"  Skill   : {skill['name']}")
    print(f"  Install : {install_name}")
    print(f"  Targets : {', '.join(chosen)}")
    print(f"  Chapters: {'copy' if args.copy_chapters else 'index-only (use --copy-chapters)'}")
    print(f"{'='*62}")

    errors = []
    for h in chosen:
        try:
            install_output(h, HARNESSES[h], install_name, skill, output_dir,
                           args.copy_chapters, args.dry_run, args.force)
        except Exception as e:
            errors.append((h, e))
            print(f"  [ERROR] {h}: {e}")

    print(f"\n{'='*62}")
    if errors:
        for h, e in errors:
            print(f"  [ERROR] {h}: {e}")
        return 1
    print(f"  Done. Skill '{install_name}' installed into: {', '.join(chosen)}")
    print()
    if "claude" in chosen:
        print(f"    Claude Code : /{install_name} [chapter|topic]")
    if "opencode" in chosen:
        print(f"    OpenCode    : /{install_name} [chapter|topic]")
    if "codex" in chosen:
        print(f"    Codex       : ${install_name} [chapter|topic]")
    if "copilot" in chosen:
        print(f"    Copilot     : skill '{install_name}' auto-available")
    print(f"{'='*62}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
