#!/usr/bin/env python3
"""Evaluate generated Red Team/Pentest Skill artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from redteam_shared import (
    REQUIRED_GENERATED_ARTIFACTS,
    REQUIRED_SECTION_TITLES,
    TAXONOMY,
    load_profile_yaml,
    pdf_sources,
)


DEFAULT_PROFILE = Path("profiles/redteam")
OUTPUT_MARKERS = (
    "HTTP/",
    "Content-Length:",
    "Server:",
    "Last-Modified:",
    " open ",
    " closed ",
    " Listing ",
    " Figure ",
    "404 page not found",
    " VRFY ",
    " 220 mail",
    "220 mail",
    "Recipient address rejected",
)
SEMANTIC_TERMS = {
    "api-pentest": ("api", "endpoint", "rest", "graphql", "rate limit", "service interface"),
    "mobile-pentest": ("mobile", "android", "ios", "apk", "ipa", "local storage", "static analysis", "dynamic analysis"),
    "cloud-container-pentest": ("cloud", "container", "kubernetes", "iam", "namespace", "pod", "docker"),
    "authentication-testing": ("authentication", "credential", "login", "password", "account", "default credentials"),
    "authorization-testing": ("authorization", "access control", "privilege", "role", "permission"),
    "session-management-testing": ("session", "cookie", "token", "logout", "timeout"),
    "input-validation-testing": ("input validation", "xss", "sql injection", "injection", "parameter"),
    "ai-threat-modeling": ("threat model", "trust zone", "escalation path", "ai-enabled", "target"),
    "ai-reconnaissance": ("reconnaissance", "ai target", "intelligence", "enumeration", "discovery"),
    "ai-agent-attacks": ("agent", "tool", "orchestrator", "memory", "token"),
    "multi-agent-a2a-attacks": ("multi-agent", "a2a", "agent-to-agent", "orchestrator", "protocol"),
    "rag-pipeline-exploitation": ("rag", "retrieval", "pipeline", "vector", "knowledge base"),
    "embedding-attacks": ("embedding", "vector", "inversion", "vector database", "qdrant"),
    "mcp-tool-surface-attacks": ("mcp", "tool", "json-rpc", "vault", "tool invocation"),
    "ai-supply-chain-attacks": ("supply chain", "model registry", "mlflow", "pipeline", "dependency"),
    "ai-infrastructure-deployment-exploits": ("infrastructure", "deployment", "kubernetes", "model server", "mlflow"),
    "ai-capstone-red-team": ("capstone", "red team", "challenge lab", "engagement", "operation"),
    "network-port-scanning": ("port scanning", "tcp", "udp", "nmap", "network"),
    "service-enumeration": ("enumeration", "dns", "smb", "smtp", "snmp", "whois"),
    "vulnerability-scanning": ("vulnerability scanning", "scanner", "nessus", "nmap", "scan"),
    "web-application-attacks": ("web application", "enumeration", "attack", "directory traversal", "xss"),
    "exploit-research-and-adaptation": ("exploit", "exploit database", "compile", "fixing", "target"),
    "password-attacks": ("password", "hash", "cracking", "credential", "authentication"),
    "windows-privilege-escalation": ("windows", "privilege", "service", "powershell", "access control"),
    "linux-privilege-escalation": ("linux", "privilege", "users", "kernel", "enumeration"),
    "port-redirection-and-tunneling": ("tunneling", "port forwarding", "ssh", "socat", "chisel"),
    "metasploit-framework": ("metasploit", "meterpreter", "payload", "module", "session"),
    "active-directory-enumeration": ("active directory", "enumeration", "powershell", "powerview", "domain"),
    "active-directory-attacks": ("active directory", "authentication", "kerberos", "lateral movement", "persistence"),
    "lateral-movement": ("lateral movement", "active directory", "remote", "session", "credential"),
    "post-exploitation": ("post-exploitation", "meterpreter", "session", "module", "pivoting"),
}


def normalize_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def markdown_headings(text: str) -> set[str]:
    headings = set()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            headings.add(normalize_heading(match.group(1)))
    return headings


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def command_lines(skill_dir: Path) -> list[str]:
    commands_md = skill_dir / "commands.md"
    if not commands_md.exists():
        return []
    return [
        line.split("`", 2)[1]
        for line in commands_md.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.startswith("- Command:") and "`" in line
    ]


def load_benchmark(profile_dir: Path, document_profile: str) -> dict | None:
    benchmark_path = profile_dir / "benchmarks" / "gold_set.json"
    if not benchmark_path.exists():
        return None
    data = read_json(benchmark_path)
    benchmark = data.get("benchmarks", {}).get(document_profile)
    return benchmark if isinstance(benchmark, dict) else None


def contains_authorized_use_constraints(text: str) -> bool:
    lowered = text.lower()
    has_authorized = any(term in lowered for term in ("authorized", "authorization", "permission"))
    has_constraint = any(term in lowered for term in ("prohibited", "scope", "explicit", "approved"))
    has_environment = any(term in lowered for term in ("lab", "training", "owned", "defense", "research"))
    has_oversight = any(term in lowered for term in ("human oversight", "human operator", "review"))
    return has_authorized and has_constraint and has_environment and has_oversight


def check_docling_metadata(metadata_path: Path | None, messages: list[str]) -> bool:
    if metadata_path is None:
        messages.append("WARN metadata not provided; Docling extraction method not verified")
        return True
    metadata = read_json(metadata_path)
    bad_sources = [
        src.get("filename") or src.get("source_file") or "unknown PDF"
        for src in pdf_sources(metadata)
        if src.get("extraction_method") != "docling"
    ]
    if bad_sources:
        messages.append(f"FAIL non-Docling PDF extraction detected: {', '.join(map(str, bad_sources))}")
        return False
    messages.append("PASS Docling extraction requirement satisfied")
    return True


def check_required_artifacts(skill_dir: Path, profile_dir: Path, messages: list[str]) -> bool:
    ok = True
    artifacts_config = load_profile_yaml(profile_dir / "artifacts.yaml")
    configured = [
        str(artifact.get("name"))
        for artifact in artifacts_config.get("artifacts", [])
        if isinstance(artifact, dict) and artifact.get("required")
    ]
    required = sorted(set(configured + REQUIRED_GENERATED_ARTIFACTS))
    for name in required:
        path = skill_dir / name
        if path.exists():
            messages.append(f"PASS required artifact exists: {name}")
        else:
            ok = False
            messages.append(f"FAIL missing required artifact: {name}")
    chapters_dir = skill_dir / "chapters"
    if chapters_dir.is_dir() and any(chapters_dir.glob("*.md")):
        messages.append("PASS chapters directory contains concept chapters")
    else:
        ok = False
        messages.append("FAIL chapters directory has no concept chapter files")
    return ok


def check_skill_sections(skill_dir: Path, profile_dir: Path, messages: list[str]) -> bool:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        messages.append("FAIL SKILL.md is missing")
        return False
    ok = True
    headings = markdown_headings(skill_md.read_text(encoding="utf-8", errors="ignore"))
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    for field in schema.get("skill", {}).get("required_fields", []):
        title = REQUIRED_SECTION_TITLES.get(field, str(field).replace("_", " ").title())
        if normalize_heading(title) in headings:
            messages.append(f"PASS SKILL.md section exists: {title}")
        else:
            ok = False
            messages.append(f"FAIL SKILL.md missing section: {title}")
    return ok


def check_coverage(skill_dir: Path, source_path: Path | None, messages: list[str]) -> bool:
    coverage_path = skill_dir / "coverage.json"
    if not coverage_path.exists():
        messages.append("FAIL coverage.json is missing")
        return False
    coverage = read_json(coverage_path)
    found = coverage.get("found_concepts", [])
    weak = coverage.get("weak_references", [])
    if found:
        messages.append(f"PASS coverage.json records {len(found)} found concept(s)")
    else:
        messages.append("FAIL coverage.json records no found concepts")
        return False
    if weak:
        messages.append(f"INFO coverage.json keeps {len(weak)} weak reference(s) out of chapters")

    if source_path is None:
        messages.append("WARN source not provided; source-term coverage not calculated")
        return True

    source = source_path.read_text(encoding="utf-8", errors="ignore").lower()
    output = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in skill_dir.rglob("*.md")).lower()
    taxonomy = coverage.get("taxonomy") or TAXONOMY
    expected = []
    for item in taxonomy:
        if any(alias.lower() in source for alias in item["aliases"]):
            expected.append(item["name"])
    retained_names = {str(item.get("name", "")).lower() for item in found + weak if isinstance(item, dict)}
    present = [name for name in expected if name.lower() in output or name.lower() in retained_names]
    if not expected:
        messages.append("WARN source contains no known taxonomy concept")
        return True
    score = len(present) / len(expected)
    messages.append(f"INFO concept coverage score: {len(present)}/{len(expected)} ({score:.0%})")
    if score >= 0.9:
        messages.append("PASS concept coverage target met")
        return True
    missing = sorted(set(expected) - set(present))
    messages.append(f"FAIL concept coverage below 90%; missing: {', '.join(missing)}")
    return False


def check_citations(skill_dir: Path, messages: list[str]) -> bool:
    citations_path = skill_dir / "citations.json"
    if not citations_path.exists():
        messages.append("FAIL citations.json is missing")
        return False
    citations = read_json(citations_path).get("citations", [])
    if not citations:
        messages.append("FAIL citations.json contains no citations")
        return False
    ok = True
    for citation in citations:
        chapter = skill_dir / "chapters" / f"{citation.get('concept_key')}.md"
        if not chapter.exists():
            ok = False
            messages.append(f"FAIL missing chapter for citation: {citation.get('id')}")
            continue
        content = chapter.read_text(encoding="utf-8", errors="ignore")
        if str(citation.get("id")) not in content:
            ok = False
            messages.append(f"FAIL chapter missing citation id: {citation.get('id')}")
    if ok:
        messages.append(f"PASS citations linked to {len(citations)} chapter(s)")
    return ok


def check_chapter_substance(skill_dir: Path, messages: list[str]) -> bool:
    citations_path = skill_dir / "citations.json"
    if not citations_path.exists():
        messages.append("FAIL cannot check chapter substance without citations.json")
        return False
    citations = read_json(citations_path).get("citations", [])
    ok = True
    required_sections = [
        "Source Summary",
        "Source-Derived Procedure",
        "Evidence To Collect",
        "Reporting Notes",
        "Decision Points",
        "Safety Constraints",
        "Citation",
    ]
    for citation in citations:
        chapter = skill_dir / "chapters" / f"{citation.get('concept_key')}.md"
        if not chapter.exists():
            ok = False
            continue
        content = chapter.read_text(encoding="utf-8", errors="ignore")
        for section in required_sections:
            if f"## {section}" not in content:
                ok = False
                messages.append(f"FAIL chapter {chapter.name} missing section: {section}")
        source_summary = content.split("## Source Summary", 1)[-1].split("## Source-Derived Procedure", 1)[0]
        summary_items = [line for line in source_summary.splitlines() if line.startswith("- ")]
        if len(summary_items) < 2:
            ok = False
            messages.append(f"FAIL chapter {chapter.name} has shallow source summary")
        if citation.get("confidence") == "toc_only":
            ok = False
            messages.append(f"FAIL chapter {chapter.name} citation confidence is toc_only")
        if citation.get("confidence") == "weak_mention":
            ok = False
            messages.append(f"FAIL chapter {chapter.name} weak mention was promoted to chapter")
    if ok:
        messages.append("PASS chapter substance checks")
    return ok


def check_semantic_alignment(skill_dir: Path, messages: list[str]) -> bool:
    citations_path = skill_dir / "citations.json"
    if not citations_path.exists():
        messages.append("FAIL cannot check semantic alignment without citations.json")
        return False
    citations = read_json(citations_path).get("citations", [])
    ok = True
    for citation in citations:
        concept_key = str(citation.get("concept_key", ""))
        required_terms = SEMANTIC_TERMS.get(concept_key)
        if not required_terms:
            continue
        chapter = skill_dir / "chapters" / f"{concept_key}.md"
        if not chapter.exists():
            ok = False
            continue
        content = chapter.read_text(encoding="utf-8", errors="ignore").lower()
        source_summary = content.split("## source summary", 1)[-1].split("## source-derived procedure", 1)[0]
        if not any(term in source_summary for term in required_terms):
            ok = False
            messages.append(f"FAIL chapter {chapter.name} lacks semantic evidence for {concept_key}")
    if ok:
        messages.append("PASS semantic alignment checks")
    return ok


def check_commands(skill_dir: Path, messages: list[str]) -> bool:
    commands_md = skill_dir / "commands.md"
    if not commands_md.exists():
        messages.append("FAIL commands.md is missing")
        return False
    text = commands_md.read_text(encoding="utf-8", errors="ignore")
    lowered = text.lower()
    ok = True
    if "context of use" in lowered:
        messages.append("PASS commands.md includes command context")
    else:
        ok = False
        messages.append("FAIL commands.md missing command context")
    if "safety note" in lowered:
        messages.append("PASS commands.md includes safety notes")
    else:
        ok = False
        messages.append("FAIL commands.md missing safety notes")
    for line in text.splitlines():
        if not line.startswith("- Command:"):
            continue
        if any(marker.lower() in line.lower() for marker in OUTPUT_MARKERS):
            ok = False
            messages.append(f"FAIL command appears polluted by output: {line}")
    if ok:
        messages.append("PASS command quality checks")
    return ok


GENERIC_PURPOSE_TEXT = "source-supported command or tool invocation"
GENERIC_CONTEXT_TEXT = {"how to test", "context incomplete"}


def check_command_purpose_quality(skill_dir: Path, messages: list[str]) -> bool:
    """Verify command Purpose and Context fields are not generic template text."""
    commands_md = skill_dir / "commands.md"
    if not commands_md.exists():
        return True  # already caught by check_commands
    lines = commands_md.read_text(encoding="utf-8", errors="ignore").splitlines()
    generic_purpose_count = 0
    weak_context_count = 0
    total_commands = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("- Command:"):
            total_commands += 1
            # Check Purpose on following lines
            for j in range(i + 1, min(i + 6, len(lines))):
                if lines[j].startswith("- Purpose:"):
                    if GENERIC_PURPOSE_TEXT in lines[j].lower():
                        generic_purpose_count += 1
                if lines[j].startswith("- Context of use:"):
                    ctx = lines[j].replace("- Context of use:", "").strip().lower()
                    if len(ctx) < 20 or ctx in GENERIC_CONTEXT_TEXT:
                        weak_context_count += 1
        i += 1
    if total_commands == 0:
        return True
    ok = True
    if generic_purpose_count > 0:
        ok = False
        messages.append(
            f"FAIL {generic_purpose_count}/{total_commands} commands have generic Purpose text "
            f"('Source-supported command or tool invocation'); write what the command accomplishes"
        )
    else:
        messages.append("PASS command Purpose fields are specific")
    if weak_context_count > 0:
        messages.append(
            f"WARN {weak_context_count}/{total_commands} commands have weak Context of use "
            f"(< 20 chars or generic); describe when/where/why the command is used"
        )
    else:
        messages.append("PASS command Context of use fields are meaningful")
    return ok


def check_source_summary_cleanliness(skill_dir: Path, messages: list[str]) -> bool:
    """Check that chapter source summaries do not contain raw markdown heading artifacts."""
    chapters_dir = skill_dir / "chapters"
    if not chapters_dir.is_dir():
        return True
    heading_artifact_re = re.compile(r"^- #{1,6} ")
    dirty_chapters: list[str] = []
    for chapter in sorted(chapters_dir.glob("*.md")):
        text = chapter.read_text(encoding="utf-8", errors="ignore")
        in_source_summary = False
        for line in text.splitlines():
            if line.strip() == "## Source Summary":
                in_source_summary = True
                continue
            if line.startswith("## ") and in_source_summary:
                in_source_summary = False
            if in_source_summary and heading_artifact_re.match(line):
                dirty_chapters.append(chapter.name)
                break
    if dirty_chapters:
        messages.append(
            f"FAIL {len(dirty_chapters)} chapter(s) have raw markdown heading artifacts in "
            f"Source Summary (e.g. '- ## Section Name'): {', '.join(dirty_chapters)}; "
            f"strip heading markers and write clean prose bullets"
        )
        return False
    messages.append("PASS source summary cleanliness checks")
    return True


def check_chapter_command_coverage(skill_dir: Path, messages: list[str]) -> bool:
    """Report per-chapter command coverage; warn when most chapters lack commands."""
    chapters_dir = skill_dir / "chapters"
    if not chapters_dir.is_dir():
        return True
    chapters = sorted(chapters_dir.glob("*.md"))
    if not chapters:
        return True
    no_commands: list[str] = []
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8", errors="ignore")
        has_commands = (
            "```" in text
            or "- Command:" in text
            or "no source-supported commands" not in text.lower()
            and any(c in text for c in ("$", "#!", "nmap", "curl", "python", "nc ", "openssl"))
        )
        if not has_commands or "no source-supported commands" in text.lower():
            no_commands.append(chapter.name)
    ratio = len(no_commands) / len(chapters)
    messages.append(
        f"INFO chapter command coverage: {len(chapters) - len(no_commands)}/{len(chapters)} "
        f"chapters contain commands"
    )
    if ratio > 0.7:
        messages.append(
            f"WARN {len(no_commands)}/{len(chapters)} chapters have no commands; "
            f"for each concept section, extract commands, code blocks, and tool invocations "
            f"found in that section of the source"
        )
        return True  # WARN only; chapter command coverage is informational, not a hard failure
    messages.append("PASS chapter command coverage within acceptable range")
    return True


def check_safety(skill_dir: Path, messages: list[str]) -> bool:
    safety_md = skill_dir / "safety.md"
    if not safety_md.exists():
        messages.append("FAIL safety.md is missing")
        return False
    safety_text = safety_md.read_text(encoding="utf-8", errors="ignore")
    if contains_authorized_use_constraints(safety_text):
        messages.append("PASS safety.md includes authorized-use constraints")
        return True
    messages.append("FAIL safety.md missing authorized-use constraints")
    return False


def check_rubric(skill_dir: Path, profile_dir: Path, messages: list[str]) -> bool:
    coverage_path = skill_dir / "coverage.json"
    citations_path = skill_dir / "citations.json"
    if not coverage_path.exists() or not citations_path.exists():
        messages.append("WARN rubric skipped; coverage.json or citations.json is missing")
        return True
    coverage = read_json(coverage_path)
    document_profile = str(coverage.get("document_profile", ""))
    benchmark = load_benchmark(profile_dir, document_profile)
    if not benchmark:
        messages.append(f"WARN rubric benchmark not configured for profile: {document_profile or 'unknown'}")
        return True

    found = coverage.get("found_concepts", [])
    weak = coverage.get("weak_references", [])
    found_keys = {str(item.get("key", "")) for item in found if isinstance(item, dict)}
    retained_keys = found_keys | {str(item.get("key", "")) for item in weak if isinstance(item, dict)}
    required = set(benchmark.get("required_concepts", []))
    required_present = required & retained_keys

    commands = command_lines(skill_dir)
    command_blob = "\n".join(commands).lower()
    command_terms = [str(term).lower() for term in benchmark.get("required_command_terms", [])]
    command_terms_present = [term for term in command_terms if term in command_blob]

    citations = read_json(citations_path).get("citations", [])
    chapters_with_domain_steps = 0
    for concept_key in found_keys:
        chapter = skill_dir / "chapters" / f"{concept_key}.md"
        if not chapter.exists():
            continue
        chapter_text = chapter.read_text(encoding="utf-8", errors="ignore").lower()
        if any(term in chapter_text for term in ("authorized", "evidence", "source", "citation")):
            chapters_with_domain_steps += 1

    min_found = int(benchmark.get("min_found_concepts", 1))
    min_commands = int(benchmark.get("min_command_count", 0))
    min_score = int(benchmark.get("min_score", 75))

    coverage_score = min(1.0, len(found) / max(min_found, 1))
    required_score = len(required_present) / max(len(required), 1)
    command_count_score = min(1.0, len(commands) / max(min_commands, 1)) if min_commands else 1.0
    command_term_score = len(command_terms_present) / max(len(command_terms), 1) if command_terms else 1.0
    citation_score = min(1.0, len(citations) / max(len(found), 1))
    chapter_score = min(1.0, chapters_with_domain_steps / max(len(found), 1))

    score = round(
        100
        * (
            0.25 * coverage_score
            + 0.25 * required_score
            + 0.15 * command_count_score
            + 0.10 * command_term_score
            + 0.15 * citation_score
            + 0.10 * chapter_score
        )
    )
    messages.append(
        "INFO rubric score: "
        f"{score}/100 for {document_profile} "
        f"(required concepts {len(required_present)}/{len(required)}, "
        f"commands {len(commands)}/{min_commands}, command terms {len(command_terms_present)}/{len(command_terms)})"
    )
    if score >= min_score:
        messages.append(f"PASS rubric benchmark target met ({score} >= {min_score})")
        return True
    missing_required = sorted(required - required_present)
    missing_terms = sorted(set(command_terms) - set(command_terms_present))
    messages.append(
        "FAIL rubric benchmark target not met; "
        f"missing concepts: {', '.join(missing_required) or 'none'}; "
        f"missing command terms: {', '.join(missing_terms) or 'none'}"
    )
    return False


def evaluate(skill_dir: Path, profile_dir: Path, source_path: Path | None = None, metadata_path: Path | None = None) -> tuple[bool, list[str]]:
    messages: list[str] = []
    checks = [
        check_required_artifacts(skill_dir, profile_dir, messages),
        check_skill_sections(skill_dir, profile_dir, messages),
        check_docling_metadata(metadata_path, messages),
        check_coverage(skill_dir, source_path, messages),
        check_citations(skill_dir, messages),
        check_chapter_substance(skill_dir, messages),
        check_semantic_alignment(skill_dir, messages),
        check_commands(skill_dir, messages),
        check_command_purpose_quality(skill_dir, messages),
        check_source_summary_cleanliness(skill_dir, messages),
        check_chapter_command_coverage(skill_dir, messages),
        check_safety(skill_dir, messages),
        check_rubric(skill_dir, profile_dir, messages),
    ]
    return all(checks), messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate generated Red Team/Pentest Skill artifacts.")
    parser.add_argument("skill_dir", type=Path, help="Generated Skill output directory")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Profile directory")
    parser.add_argument("--source", type=Path, help="Source full_text.txt for concept coverage checks")
    parser.add_argument("--metadata", type=Path, help="metadata.json for Docling extraction checks")
    args = parser.parse_args()

    ok, messages = evaluate(args.skill_dir, args.profile, source_path=args.source, metadata_path=args.metadata)
    for message in messages:
        print(message)
    print("RESULT: PASS" if ok else "RESULT: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
