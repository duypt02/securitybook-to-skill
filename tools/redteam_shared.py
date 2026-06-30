"""Shared constants and utilities for Red Team skill tools.

This module is the single source of truth for data that both
``generate_redteam_skill.py`` (legacy comparison baseline) and
``evaluate_redteam_skill.py`` (harness quality gate) need to agree on.

Keeping them here prevents the evaluator from depending on the legacy
generator at import time.
"""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

REQUIRED_SECTION_TITLES: dict[str, str] = {
    "skill_name": "Skill Name",
    "objective": "Objective",
    "context": "Context",
    "preconditions": "Preconditions",
    "procedure": "Procedure",
    "tools_commands": "Tools Commands",
    "expected_outputs": "Expected Outputs",
    "safety_constraints": "Safety Constraints",
    "references": "References",
}

REQUIRED_GENERATED_ARTIFACTS: list[str] = [
    "SKILL.md",
    "chapters",
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
]

# ---------------------------------------------------------------------------
# Taxonomy — 40+ Red Team / Pentest concept categories
# ---------------------------------------------------------------------------

TAXONOMY: list[dict] = [
    # web_pentest ─────────────────────────────────────────────────────────
    {
        "key": "information-gathering",
        "name": "Information Gathering",
        "category": "web_pentest",
        "aliases": ["Information Gathering", "Reconnaissance", "Target Identification"],
    },
    {
        "key": "configuration-deployment-management-testing",
        "name": "Configuration and Deployment Management Testing",
        "category": "web_pentest",
        "aliases": ["Configuration and Deployment Management Testing", "Configuration Management"],
    },
    {
        "key": "identity-management-testing",
        "name": "Identity Management Testing",
        "category": "web_pentest",
        "aliases": ["Identity Management Testing", "Account Enumeration"],
    },
    {
        "key": "authentication-testing",
        "name": "Authentication Testing",
        "category": "web_pentest",
        "aliases": ["Authentication Testing", "Default Credentials", "Login Testing"],
    },
    {
        "key": "authorization-testing",
        "name": "Authorization Testing",
        "category": "web_pentest",
        "aliases": ["Authorization Testing", "Access Control", "Permission Testing", "Role-Based Access Control"],
    },
    {
        "key": "session-management-testing",
        "name": "Session Management Testing",
        "category": "web_pentest",
        "aliases": ["Session Management Testing", "Session Timeout", "Cookie"],
    },
    {
        "key": "input-validation-testing",
        "name": "Input Validation Testing",
        "category": "web_pentest",
        "aliases": ["Input Validation Testing", "Cross Site Scripting", "SQL Injection"],
    },
    {
        "key": "testing-for-error-handling",
        "name": "Testing for Error Handling",
        "category": "web_pentest",
        "aliases": ["Testing for Error Handling", "Error Handling"],
    },
    {
        "key": "testing-for-weak-cryptography",
        "name": "Testing for weak Cryptography",
        "category": "web_pentest",
        "aliases": ["Testing for weak Cryptography", "Weak Cryptography", "TLS", "SSL"],
    },
    {
        "key": "business-logic-testing",
        "name": "Business Logic Testing",
        "category": "web_pentest",
        "aliases": ["Business Logic Testing", "Business Logic"],
    },
    {
        "key": "client-side-testing",
        "name": "Client Side Testing",
        "category": "web_pentest",
        "aliases": ["Client Side Testing", "Client-Side Testing", "JavaScript"],
    },
    # api / mobile / cloud ────────────────────────────────────────────────
    {
        "key": "api-pentest",
        "name": "API Pentest",
        "category": "api_pentest",
        "aliases": ["API Testing", "Endpoint", "Rate Limiting", "REST", "GraphQL"],
    },
    {
        "key": "mobile-pentest",
        "name": "Mobile Pentest",
        "category": "mobile_pentest",
        "aliases": ["Mobile Testing", "Static Analysis", "Dynamic Analysis", "Local Storage"],
    },
    {
        "key": "cloud-container-pentest",
        "name": "Cloud and Container Pentest",
        "category": "cloud_container_pentest",
        "aliases": ["Cloud", "Container", "Kubernetes", "IAM", "Misconfiguration"],
    },
    # methodology (NIST SP 800-115) ────────────────────────────────────────
    {
        "key": "information-security-assessment-methodology",
        "name": "Information Security Assessment Methodology",
        "category": "methodology",
        "aliases": ["Information Security Assessment Methodology", "Assessment Methodology"],
    },
    {
        "key": "technical-assessment-techniques",
        "name": "Technical Assessment Techniques",
        "category": "methodology",
        "aliases": ["Technical Assessment Techniques", "Assessment Techniques"],
    },
    {
        "key": "review-techniques",
        "name": "Review Techniques",
        "category": "methodology",
        "aliases": ["Review Techniques", "Documentation Review", "Log Review"],
    },
    {
        "key": "target-identification-analysis-techniques",
        "name": "Target Identification and Analysis Techniques",
        "category": "methodology",
        "aliases": ["Target Identification and Analysis Techniques", "Target Identification"],
    },
    {
        "key": "target-vulnerability-validation-techniques",
        "name": "Target Vulnerability Validation Techniques",
        "category": "methodology",
        "aliases": ["Target Vulnerability Validation Techniques", "Vulnerability Validation"],
    },
    {
        "key": "security-assessment-planning",
        "name": "Security Assessment Planning",
        "category": "methodology",
        "aliases": ["Security Assessment Planning", "Assessment Planning"],
    },
    {
        "key": "security-assessment-execution",
        "name": "Security Assessment Execution",
        "category": "methodology",
        "aliases": ["Security Assessment Execution", "Assessment Execution"],
    },
    {
        "key": "post-testing-activities",
        "name": "Post-Testing Activities",
        "category": "methodology",
        "aliases": ["Post-Testing Activities", "Post Testing"],
    },
    {
        "key": "rules-of-engagement",
        "name": "Rules of Engagement",
        "category": "safety",
        "aliases": ["Rules of Engagement", "ROE", "Authorized Scope", "Written Authorization", "Engagement Scope"],
    },
    {
        "key": "logistics",
        "name": "Logistics",
        "category": "methodology",
        "aliases": ["Logistics", "Resources Selection", "Assessment Logistics", "Engagement Logistics"],
    },
    {
        "key": "technical-tools-resources-selection",
        "name": "Technical Tools and Resources Selection",
        "category": "tooling",
        "aliases": ["Technical Tools and Resources Selection", "Tools and Resources", "Tool Selection"],
    },
    {
        "key": "final-report",
        "name": "Final Report",
        "category": "reporting",
        "aliases": ["Final Report", "Report", "Reporting", "Findings"],
    },
    # classic pentest (PEN200 / OSCP) ──────────────────────────────────────
    {
        "key": "network-port-scanning",
        "name": "Network and Port Scanning",
        "category": "classic_pentest",
        "aliases": ["TCP/UDP Port Scanning Theory", "Port Scanning with Nmap", "Network Scanning", "Port Scanning"],
    },
    {
        "key": "service-enumeration",
        "name": "Service Enumeration",
        "category": "classic_pentest",
        "aliases": ["Whois Enumeration", "DNS Enumeration", "SMB Enumeration", "SMTP Enumeration", "SNMP Enumeration"],
    },
    {
        "key": "vulnerability-scanning",
        "name": "Vulnerability Scanning",
        "category": "classic_pentest",
        "aliases": ["Vulnerability Scanning", "Vulnerability Scanning Theory", "Vulnerability Scanning with Nessus", "Vulnerability Scanning with Nmap"],
    },
    {
        "key": "web-application-attacks",
        "name": "Web Application Attacks",
        "category": "classic_pentest",
        "aliases": ["Introduction to Web Application Attacks", "Common Web Application Attacks", "Web Application Enumeration"],
    },
    {
        "key": "exploit-research-and-adaptation",
        "name": "Exploit Research and Adaptation",
        "category": "classic_pentest",
        "aliases": ["Fixing Exploits", "Locating Public Exploits", "Online Exploit Resources", "Exploiting a Target"],
    },
    {
        "key": "password-attacks",
        "name": "Password Attacks",
        "category": "classic_pentest",
        "aliases": ["Password Attacks", "Password Cracking Fundamentals", "Working with Password Hashes", "Abusing Password Authentication"],
    },
    {
        "key": "windows-privilege-escalation",
        "name": "Windows Privilege Escalation",
        "category": "classic_pentest",
        "aliases": ["Windows Privilege Escalation", "Enumerating Windows", "Leveraging Windows Services", "Abusing Other Windows Components"],
    },
    {
        "key": "linux-privilege-escalation",
        "name": "Linux Privilege Escalation",
        "category": "classic_pentest",
        "aliases": ["Linux Privilege Escalation", "Enumerating Linux", "Understanding Files and Users Privileges on Linux"],
    },
    {
        "key": "port-redirection-and-tunneling",
        "name": "Port Redirection and Tunneling",
        "category": "classic_pentest",
        "aliases": ["Port Redirection and SSH Tunneling", "Why Port Redirection and Tunneling", "Port Forwarding with Linux Tools", "SSH Tunneling"],
    },
    {
        "key": "metasploit-framework",
        "name": "Metasploit Framework",
        "category": "classic_pentest",
        "aliases": ["The Metasploit Framework", "Using Metasploit Payloads", "Post-Exploitation with Metasploit", "Pivoting with Metasploit"],
    },
    {
        "key": "active-directory-enumeration",
        "name": "Active Directory Enumeration",
        "category": "classic_pentest",
        "aliases": ["Active Directory Introduction and Enumeration", "Active Directory - Manual Enumeration", "AD Enumeration with PowerView", "Active Directory - Automated Enumeration"],
    },
    {
        "key": "active-directory-attacks",
        "name": "Active Directory Attacks",
        "category": "classic_pentest",
        "aliases": ["Attacking Active Directory Authentication", "Performing Attacks on Active Directory Authentication", "Active Directory Lateral Movement Techniques", "Active Directory Persistence"],
    },
    {
        "key": "lateral-movement",
        "name": "Lateral Movement",
        "category": "classic_pentest",
        "aliases": ["Lateral Movement in Active Directory", "Lateral Movement Techniques", "Lateral Movement"],
    },
    {
        "key": "post-exploitation",
        "name": "Post-Exploitation",
        "category": "classic_pentest",
        "aliases": ["Performing Post-Exploitation with Metasploit", "Core Meterpreter Post-Exploitation Features", "Post-Exploitation Modules"],
    },
    # AI Red Team (OFFSEC AI-300) ──────────────────────────────────────────
    {
        "key": "ai-threat-modeling",
        "name": "AI Threat Modeling",
        "category": "ai_redteam",
        "aliases": ["Threat Modeling for AI-Enabled Targets", "AI Threat Modeling", "Trust Zones", "Escalation Paths"],
    },
    {
        "key": "ai-reconnaissance",
        "name": "AI Target Reconnaissance",
        "category": "ai_redteam",
        "aliases": ["Reconnaissance for AI Targets", "AI Reconnaissance", "AI Target Reconnaissance"],
    },
    {
        "key": "ai-agent-attacks",
        "name": "AI Agent Attacks",
        "category": "ai_redteam",
        "aliases": ["Attacking AI Agents", "AI Agents", "Agent Systems", "Agent Token"],
    },
    {
        "key": "multi-agent-a2a-attacks",
        "name": "Multi-Agent and A2A Attacks",
        "category": "ai_redteam",
        "aliases": ["Attacking MultiAgent Systems and A2A Protocol", "Multi-Agent", "A2A Protocol"],
    },
    {
        "key": "rag-pipeline-exploitation",
        "name": "RAG Pipeline Exploitation",
        "category": "ai_redteam",
        "aliases": ["Exploiting RAG Pipelines", "RAG Pipelines", "Retrieval-Augmented Generation", "Retrieval Hijacking"],
    },
    {
        "key": "embedding-attacks",
        "name": "Embedding Attacks",
        "category": "ai_redteam",
        "aliases": ["Attacking Embeddings", "Embedding Attack", "Embedding Inversion", "Vector Databases"],
    },
    {
        "key": "mcp-tool-surface-attacks",
        "name": "MCP and Tool Surface Attacks",
        "category": "ai_redteam",
        "aliases": ["Attacking MCP and Tool Surfaces", "MCP Server", "MCP Tools", "Tool Surfaces"],
    },
    {
        "key": "ai-supply-chain-attacks",
        "name": "AI/ML Supply Chain Attacks",
        "category": "ai_redteam",
        "aliases": ["Supply Chain Attacks on AI/ML Systems", "ML Supply Chain", "AI Supply Chain", "Model Registry"],
    },
    {
        "key": "ai-infrastructure-deployment-exploits",
        "name": "AI Infrastructure and Deployment Exploits",
        "category": "ai_redteam",
        "aliases": ["AI Infrastructure and Deployment Exploits", "Model Hosting", "MLflow", "Kubernetes"],
    },
    {
        "key": "ai-capstone-red-team",
        "name": "AI Capstone Red Team",
        "category": "ai_redteam",
        "aliases": ["Assembling The Pieces Capstone Red Team", "Capstone Red Team", "Challenge Lab"],
    },
]

# ---------------------------------------------------------------------------
# Profile YAML helpers
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def parse_profile_yaml(text: str) -> dict:
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if lines and lines[0].startswith("artifacts:"):
        artifacts = []
        current: dict | None = None
        for raw in lines[1:]:
            line = raw.strip()
            if line.startswith("- "):
                if current:
                    artifacts.append(current)
                current = {}
                line = line[2:]
                if ":" in line:
                    key, value = line.split(":", 1)
                    current[key.strip()] = parse_scalar(value.strip())
            elif current is not None and ":" in line:
                key, value = line.split(":", 1)
                current[key.strip()] = parse_scalar(value.strip())
        if current:
            artifacts.append(current)
        return {"artifacts": artifacts}

    data: dict[str, object] = {}
    current_top: str | None = None
    current_mid: str | None = None
    for raw in lines:
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0 and line.endswith(":"):
            current_top = line[:-1]
            data[current_top] = {}
            current_mid = None
        elif indent == 2 and line.endswith(":") and current_top:
            current_mid = line[:-1]
            assert isinstance(data[current_top], dict)
            data[current_top][current_mid] = [] if current_mid.endswith("fields") else {}
        elif indent == 4 and line.startswith("- ") and current_top and current_mid:
            assert isinstance(data[current_top], dict)
            items = data[current_top][current_mid]
            if isinstance(items, list):
                items.append(line[2:].strip())
        elif indent == 2 and line.endswith(":") and current_top == "knowledge_types":
            current_mid = line[:-1]
            assert isinstance(data[current_top], dict)
            data[current_top][current_mid] = {}
        elif indent == 4 and ":" in line and current_top and current_mid:
            key, value = line.split(":", 1)
            assert isinstance(data[current_top], dict)
            nested = data[current_top][current_mid]
            if isinstance(nested, dict):
                nested[key.strip()] = parse_scalar(value.strip())
    return data


def load_profile_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return parse_profile_yaml(read_text(path))
    return yaml.safe_load(read_text(path)) or {}


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------


def pdf_sources(metadata: dict) -> list[dict]:
    sources = metadata.get("sources")
    if isinstance(sources, list) and sources:
        return [src for src in sources if isinstance(src, dict) and src.get("format") == "pdf"]
    if metadata.get("format") == "pdf":
        return [metadata]
    return []
