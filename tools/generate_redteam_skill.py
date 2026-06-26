#!/usr/bin/env python3
"""Generate Red Team/Pentest Skill artifacts from book-to-skill extraction output.

This profile runner deliberately stays outside the core extractor pipeline. For
PDF inputs, it requires Docling-backed extraction metadata by default because
Red Team/Pentest artifacts depend on layout, headings, tables, and code blocks.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from textwrap import shorten


REQUIRED_SECTION_TITLES = {
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


TAXONOMY = [
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

KNOWN_CONCEPTS = [item["name"] for item in TAXONOMY]
PRIMARY_CONFIDENCES = {"primary_section", "body_match"}
SHELL_PROMPT_RE = re.compile(
    r"(?:^|\s)(?:"
    r"[\w.-]+@[\w.-]+(?::[~./\\\w-]+)?[$#]"
    r"|PS\s+[A-Za-z]:\\[^>]*>"
    r"|msf6(?:\s+[^>]+)?>"
    r"|meterpreter\s*>"
    r")\s*"
)
COMMAND_OUTPUT_SPLITS = (
    " Starting Nmap ",
    " Nmap scan report ",
    " Host is up ",
    " Not shown: ",
    " PORT ",
    " Serving HTTP ",
    " listening on ",
    " Enter passphrase ",
    " Welcome to ",
    " Connecting to ",
    " HTTP request sent",
    " Impacket v",
    " CrackMapExec ",
    " SMB         ",
    " payload => ",
    " session => ",
    " LHOST => ",
    " LPORT => ",
    " zsh: ",
    " sudo: ",
    " [sudo] ",
    " [*] ",
    " [+] ",
    " [-] ",
    " Length: ",
    " --202",
    " (UNKNOWN) ",
    " Operation not permitted",
    " permission denied",
    " not found:",
    " 404 page not found",
    " 220 mail",
    "220 mail",
    " VRFY ",
    " Recipient address rejected",
    " descriptive text ",
)
HIGH_VALUE_COMMANDS = {
    "crackmapexec", "curl", "dig", "dnsenum", "dnsrecon", "ffuf", "gobuster",
    "hashcat", "host", "hydra", "john", "msfconsole", "msfvenom", "nc", "netcat",
    "nmap", "proxychains", "python", "python3", "kubectl", "searchsploit",
    "smbclient", "socat", "sqlmap", "ssh2john", "swaks", "whois",
}
MEDIUM_VALUE_COMMANDS = {
    "chmod", "chisel", "git", "impacket-getuserspns", "impacket-ntlmrelayx",
    "impacket-psexec", "iwr", "nslookup", "openssl", "python3", "ssh", "sudo",
    "test-netconnection", "upload", "use", "wget",
}
DOMAIN_PROCEDURE_STEPS = {
    "information-gathering": [
        "Inventory externally visible hosts, names, services, metadata, and public references before active testing.",
        "Separate passive findings from active probes and preserve source evidence for each observation.",
        "Use findings to drive scoped enumeration, not to expand targets beyond authorization.",
    ],
    "configuration-deployment-management-testing": [
        "Identify deployment defaults, exposed administrative paths, backup files, and configuration weaknesses.",
        "Validate each configuration issue with a reproducible request or observable response.",
        "Record affected component, evidence, security impact, and hardening recommendation.",
    ],
    "identity-management-testing": [
        "Review account lifecycle, user enumeration, registration, provisioning, and identity recovery behavior.",
        "Capture evidence showing whether account identifiers, roles, or lifecycle states leak or drift.",
        "Keep user data handling bounded to approved test accounts and scope.",
    ],
    "authentication-testing": [
        "Define approved test accounts, credential policy checks, and lockout constraints before testing.",
        "Verify default credentials, weak password policy, transport protection, and recovery flows only in scope.",
        "Record request/response evidence without exposing reusable secrets in reports.",
    ],
    "authorization-testing": [
        "Map roles, resources, object identifiers, and expected access boundaries before testing.",
        "Test horizontal and vertical access control with approved accounts and non-destructive requests.",
        "Record the exact role, object, request, observed access, and expected denial or approval.",
    ],
    "session-management-testing": [
        "Inspect session cookie attributes, token lifecycle, logout behavior, fixation risk, and timeout policy.",
        "Use controlled sessions and avoid capturing third-party tokens or unrelated user data.",
        "Report token handling evidence with reproduction context and defensive configuration guidance.",
    ],
    "input-validation-testing": [
        "Identify inputs, parameters, encodings, and server-side processing paths before payload testing.",
        "Use safe proof payloads first and escalate only within written authorization.",
        "Preserve request, payload, response, and impact evidence for each validated issue.",
    ],
    "testing-for-error-handling": [
        "Trigger bounded error conditions that reveal stack traces, debug data, or sensitive implementation details.",
        "Avoid destructive malformed input and record only necessary diagnostic evidence.",
        "Map findings to remediation such as generic errors, logging controls, and exception handling.",
    ],
    "testing-for-weak-cryptography": [
        "Review protocol versions, certificate handling, cipher strength, key exposure, and transport headers.",
        "Use source-supported commands to validate observable cryptographic configuration.",
        "Report affected endpoint, observed weakness, business impact, and configuration fix.",
    ],
    "business-logic-testing": [
        "Model intended workflow rules, trust boundaries, transaction states, and abuse cases.",
        "Test logic flaws with approved accounts and avoid actions that alter real business state.",
        "Document preconditions, state transitions, observed bypass, and recommended control.",
    ],
    "client-side-testing": [
        "Review client-side code, browser storage, DOM sinks, script dependencies, and exposed secrets.",
        "Validate whether client-side behavior causes server-side impact or sensitive data exposure.",
        "Capture source location, browser context, payload, and defensive recommendation.",
    ],
    "information-security-assessment-methodology": [
        "Define assessment objectives, scope, assumptions, roles, constraints, and evidence handling before execution.",
        "Organize work into planning, execution, analysis, reporting, and post-assessment activities.",
        "Keep methodology decisions traceable to source guidance and stakeholder authorization.",
    ],
    "technical-assessment-techniques": [
        "Select techniques according to scope, risk, environment constraints, and available evidence.",
        "Pair automated checks with manual validation before reporting results.",
        "Document technique limitations and false-positive handling.",
    ],
    "review-techniques": [
        "Review documentation, logs, configurations, architecture, and procedures relevant to assessment objectives.",
        "Record reviewed artifacts, access constraints, findings, and uncertainty.",
        "Use review evidence to guide testing without overstating unverified assumptions.",
    ],
    "target-identification-analysis-techniques": [
        "Identify assets, owners, boundaries, dependencies, and target criticality before testing.",
        "Confirm target identity and scope with stakeholders before running active checks.",
        "Preserve target selection rationale and exclusions.",
    ],
    "target-vulnerability-validation-techniques": [
        "Validate suspected vulnerabilities with safe, reproducible evidence.",
        "Differentiate scanner output, exploitability evidence, and actual impact.",
        "Record validation method, affected target, limits, and remediation.",
    ],
    "security-assessment-planning": [
        "Define scope, rules of engagement, schedule, staff, tools, communications, and stop conditions.",
        "Confirm authorization, data handling, risk acceptance, and escalation contacts.",
        "Create a test plan that maps objectives to techniques and evidence requirements.",
    ],
    "security-assessment-execution": [
        "Run approved assessment activities according to the plan and operational constraints.",
        "Track findings, evidence, deviations, errors, and stakeholder communications during execution.",
        "Pause or escalate when observed risk exceeds the approved plan.",
    ],
    "post-testing-activities": [
        "Validate findings, clean up artifacts, return access, and protect collected evidence.",
        "Prepare reporting, debriefs, remediation tracking, and lessons learned.",
        "Confirm that test accounts, tools, and temporary changes are handled per agreement.",
    ],
    "ai-threat-modeling": [
        "Map AI assets, trust boundaries, data flows, model interfaces, tools, memory, and escalation paths.",
        "Prioritize attack hypotheses by likely impact, reachability, and control gaps.",
        "Record assumptions, evidence, and unresolved questions for later validation.",
    ],
    "ai-reconnaissance": [
        "Enumerate AI-facing endpoints, models, prompts, tools, vector stores, agents, and deployment metadata.",
        "Separate passive discovery from active probes and keep test prompts within scope.",
        "Preserve endpoint, model, tool, and data-source evidence for reporting.",
    ],
    "ai-agent-attacks": [
        "Identify agent goals, tools, memory, orchestration, authorization model, and human approval points.",
        "Test prompt injection, tool misuse, memory poisoning, and privilege boundaries with scoped payloads.",
        "Record agent reasoning, tool calls, input/output, and downstream impact.",
    ],
    "multi-agent-a2a-attacks": [
        "Map agent-to-agent protocols, message trust, identity, routing, and delegation rules.",
        "Test whether one agent can influence another across trust boundaries.",
        "Record message path, receiving agent behavior, and control failures.",
    ],
    "rag-pipeline-exploitation": [
        "Map ingestion, retrieval, ranking, prompt assembly, and generation stages.",
        "Test poisoning, retrieval hijacking, context injection, and source attribution boundaries.",
        "Record injected source, retrieved context, model output, and mitigation gaps.",
    ],
    "embedding-attacks": [
        "Identify embedding model, vector store, metadata filters, and similarity search behavior.",
        "Test retrieval manipulation and vector data exposure with approved datasets.",
        "Record query, retrieved vectors/documents, and access control implications.",
    ],
    "mcp-tool-surface-attacks": [
        "Enumerate MCP servers, tool schemas, parameters, auth boundaries, and audit logs.",
        "Test tool invocation authorization, parameter validation, and cross-tool data exposure.",
        "Record tool call, response, permission boundary, and control failure.",
    ],
    "ai-supply-chain-attacks": [
        "Review model sources, registries, dependencies, datasets, pipelines, and deployment artifacts.",
        "Test for tampering, dependency confusion, unsafe deserialization, and weak provenance within scope.",
        "Record affected artifact, trust path, validation gap, and remediation.",
    ],
    "ai-infrastructure-deployment-exploits": [
        "Identify model hosting, API gateways, containers, orchestration, secrets, and deployment interfaces.",
        "Validate exposed services and misconfigurations without disrupting model availability.",
        "Record infrastructure path, affected component, impact, and hardening recommendation.",
    ],
    "ai-capstone-red-team": [
        "Combine reconnaissance, threat model, exploitation hypotheses, evidence collection, and reporting.",
        "Track attack chains end to end while respecting scope and stop conditions.",
        "Summarize confirmed impact, assumptions, and recommended defenses.",
    ],
    "network-port-scanning": [
        "Confirm target range, scan type, rate limits, and allowed ports before scanning.",
        "Start with discovery and port scanning that matches the allowed scope.",
        "Record open ports, scan options, timing assumptions, and raw output references.",
    ],
    "service-enumeration": [
        "Map discovered ports to service-specific enumeration tasks.",
        "Use source-supported tools to identify service names, banners, versions, and protocol behavior.",
        "Separate confirmed service facts from guesses based on banners or fingerprints.",
    ],
    "vulnerability-scanning": [
        "Verify scanner authorization, credential use, target scope, and scan intensity.",
        "Run only source-supported scanner workflows and preserve scanner configuration.",
        "Manually validate candidate findings before reporting them as vulnerabilities.",
    ],
    "web-application-attacks": [
        "Identify application routes, inputs, authentication state, and trust boundaries.",
        "Apply source-supported web checks only against approved hosts and paths.",
        "Capture request, response, payload, and impact evidence for each verified issue.",
    ],
    "exploit-research-and-adaptation": [
        "Trace exploit source, target version, assumptions, and required changes before use.",
        "Review and adapt exploit code only in a controlled lab or approved assessment.",
        "Record modifications, compilation steps, execution context, and observed result.",
    ],
    "password-attacks": [
        "Confirm password testing scope, account lockout constraints, and approved wordlists.",
        "Handle captured hashes, credentials, and cracking output as sensitive data.",
        "Report credential exposure with evidence, impact, and remediation guidance.",
    ],
    "windows-privilege-escalation": [
        "Enumerate Windows privileges, services, scheduled tasks, files, and configuration paths.",
        "Validate each escalation path manually before attempting exploitation.",
        "Record the starting user, local permissions, exploited condition, and resulting privilege.",
    ],
    "linux-privilege-escalation": [
        "Enumerate Linux users, groups, sudo rights, services, files, and kernel context.",
        "Prioritize source-supported local checks and avoid destructive changes.",
        "Record the privilege boundary, exploited condition, and resulting access level.",
    ],
    "port-redirection-and-tunneling": [
        "Confirm that pivoting, forwarding, and tunnel endpoints are authorized.",
        "Document local ports, remote ports, routes, credentials, and cleanup steps.",
        "Validate that forwarded traffic remains within approved network boundaries.",
    ],
    "metasploit-framework": [
        "Select modules and payloads only when source context and scope permit their use.",
        "Record module options, payload settings, session IDs, and post-exploitation actions.",
        "Stop if module behavior could affect out-of-scope systems or availability.",
    ],
    "active-directory-enumeration": [
        "Enumerate domain users, groups, computers, sessions, shares, and permissions.",
        "Capture tool output and distinguish readable metadata from exploitable rights.",
        "Protect domain data and credentials as sensitive evidence.",
    ],
    "active-directory-attacks": [
        "Confirm credential, Kerberos, relay, and authentication attack scope before testing.",
        "Run only approved attacks and preserve hashes, tickets, and logs as sensitive evidence.",
        "Report attack path, affected principals, privilege impact, and remediation.",
    ],
    "lateral-movement": [
        "Validate credentials, reachable services, and approved destination hosts.",
        "Document the movement path, tool choice, account used, and resulting access.",
        "Avoid persistence or propagation beyond explicit authorization.",
    ],
    "post-exploitation": [
        "Define post-exploitation objectives, allowed collection, and cleanup expectations.",
        "Collect only evidence required to prove impact within scope.",
        "Record sessions, commands, accessed data classes, and cleanup actions.",
    ],
}
COMMAND_STARTERS = {
    "cat", "cd", "chmod", "chisel", "cp", "crackmapexec", "curl", "dig", "dnsenum",
    "dnsrecon", "docker", "ffuf", "git", "gobuster", "hashcat", "host", "hydra",
    "impacket-getuserspns", "impacket-ntlmrelayx", "impacket-psexec", "iwr", "john",
    "kubectl", "mkdir", "msfconsole", "msfvenom", "mv", "nc", "netcat", "nmap",
    "nslookup", "openssl", "pip", "pip3", "pnpm", "proxychains", "python", "python3",
    "run", "searchsploit", "sessions", "set", "smbclient", "socat", "sqlmap", "ssh",
    "ssh2john", "sudo", "swaks", "test-netconnection", "upload", "use", "wget",
    "whoami", "whois",
}
REQUIRED_GENERATED_ARTIFACTS = [
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


def slugify(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "redteam-section"


def slug_to_title(slug: str) -> str:
    normalized = slug.lower().replace("_", "-")
    if "owasp-testing-guide" in normalized:
        return "OWASP Web Security Testing Guide"
    if "nistspecialpublication800-115" in normalized or "800-115" in normalized:
        return "NIST SP 800-115 Technical Guide"
    words = re.split(r"[-_\s]+", slug.strip())
    return " ".join(word.capitalize() for word in words if word) or "Red Team/Pentest Skill"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_profile_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return parse_profile_yaml(read_text(path))
    return yaml.safe_load(read_text(path)) or {}


def parse_profile_yaml(text: str) -> dict:
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if lines and lines[0].startswith("artifacts:"):
        artifacts = []
        current = None
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
    current_top = None
    current_mid = None
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


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def load_prompts(profile_dir: Path, artifacts: list[dict]) -> dict[str, str]:
    prompts_dir = profile_dir / "prompts"
    prompts = {}
    for artifact in artifacts:
        prompt_name = artifact.get("prompt")
        if not prompt_name:
            continue
        prompt_path = prompts_dir / str(prompt_name)
        if not prompt_path.exists():
            raise FileNotFoundError(f"Missing prompt template: {prompt_path}")
        prompts[str(prompt_name)] = read_text(prompt_path)
    classifier = prompts_dir / "classify_knowledge.md"
    if classifier.exists():
        prompts[classifier.name] = read_text(classifier)
    return prompts


def source_name(metadata: dict, out_dir: Path) -> str:
    filename = metadata.get("filename")
    if isinstance(filename, str) and filename and filename != "multi-source":
        return Path(filename).stem
    return out_dir.name


def metadata_sources(metadata: dict) -> list[str]:
    sources = metadata.get("sources")
    if isinstance(sources, list) and sources:
        names = []
        for item in sources:
            if isinstance(item, dict):
                names.append(str(item.get("filename") or item.get("source_file") or "unknown source"))
        return names
    single = metadata.get("filename") or metadata.get("source_file")
    return [str(single)] if single else ["metadata.json"]


def pdf_sources(metadata: dict) -> list[dict]:
    sources = metadata.get("sources")
    if isinstance(sources, list) and sources:
        return [src for src in sources if isinstance(src, dict) and src.get("format") == "pdf"]
    if metadata.get("format") == "pdf":
        return [metadata]
    return []


def validate_docling_requirement(metadata: dict, allow_non_docling: bool = False) -> None:
    if allow_non_docling:
        return
    bad_sources = [
        src.get("filename") or src.get("source_file") or "unknown PDF"
        for src in pdf_sources(metadata)
        if src.get("extraction_method") != "docling"
    ]
    if bad_sources:
        joined = ", ".join(str(item) for item in bad_sources)
        raise RuntimeError(
            "Red Team/Pentest PDF generation requires Docling extraction. "
            f"Non-Docling PDF source(s): {joined}. "
            "Run extraction with `python3 scripts/extract.py <pdf> --mode technical` "
            "after installing docling, or use --allow-non-docling only for synthetic tests."
        )


def source_markers(text: str) -> list[str]:
    markers = []
    for line in text.splitlines():
        if line.startswith("SOURCE: "):
            markers.append(line.removeprefix("SOURCE: ").strip())
    return markers[:20]


def clean_line(line: str) -> str:
    return " ".join(line.strip().split())


def is_noise_heading(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 4 or len(stripped) > 140:
        return True
    if re.fullmatch(r"\d+(?:[-.]\d+)+", stripped):
        return True
    if re.fullmatch(r"\d+\s*-\s*\d+", stripped):
        return True
    if "..." in stripped or " . . " in stripped:
        return True
    if re.search(r"\[\d+\]|\d{4}-\d{2}-\d{2}|MB/s|saved \[", stripped):
        return True
    if re.match(r"^\d+(?:\.\d+)?\s+[A-Z]{2,}\b", stripped):
        return True
    return False


def extract_known_concepts(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for item in TAXONOMY:
        if any(alias.lower() in lowered for alias in item["aliases"]):
            found.append(item["name"])
    return found


def document_profile(full_text: str, metadata: dict) -> str:
    names = " ".join(metadata_sources(metadata)).lower()
    sample = full_text[:12000].lower()
    if (
        "ai-300" in names
        or "advanced ai red teaming" in names
        or "advanced ai red teaming" in sample
        or "ai-integrated environments" in sample
        or "attacking ai agents" in sample
    ):
        return "ai_redteam"
    if "pen200" in names or "oscp" in names or "pwk" in names or "penetration testing with kali" in sample:
        return "classic_pentest"
    if "800-115" in names or "nistspecialpublication800-115" in names or "technical guide to information security testing" in sample:
        return "nist_methodology"
    if "owasp" in names or "web security testing guide" in sample or "owasp testing guide" in sample:
        return "owasp_web"
    return "general_redteam"


def taxonomy_for_profile(profile: str) -> list[dict]:
    if profile == "ai_redteam":
        allowed_keys = {
            "rules-of-engagement",
            "logistics",
            "final-report",
            "cloud-container-pentest",
        }
        return [
            item
            for item in TAXONOMY
            if item["category"] == "ai_redteam" or item["key"] in allowed_keys
        ]
    if profile == "classic_pentest":
        allowed_keys = {
            "information-gathering",
            "input-validation-testing",
            "testing-for-weak-cryptography",
            "client-side-testing",
            "information-security-assessment-methodology",
            "rules-of-engagement",
            "technical-tools-resources-selection",
            "final-report",
        }
        return [
            item
            for item in TAXONOMY
            if item["category"] == "classic_pentest" or item["key"] in allowed_keys
        ]
    if profile == "nist_methodology":
        allowed = {"methodology", "safety", "tooling", "reporting"}
        return [item for item in TAXONOMY if item["category"] in allowed]
    if profile == "owasp_web":
        allowed = {"web_pentest", "safety", "reporting"}
        return [item for item in TAXONOMY if item["category"] in allowed]
    return TAXONOMY


def is_heading_line(line: str) -> bool:
    stripped = clean_line(line.strip(" #\t"))
    if not stripped or is_noise_heading(stripped):
        return False
    if line.lstrip().startswith(("# ", "## ", "### ", "#### ")):
        return True
    if re.match(r"^\d+\.?\s+[A-Z][A-Za-z0-9,/()&: -]{5,}$", stripped):
        return True
    if re.match(r"^\d+(?:\.\d+){1,3}\s+[A-Z][A-Za-z0-9,/() -]{5,}$", stripped):
        return True
    if re.match(r"^(chapter|section|module|lesson|appendix)\b", stripped, re.I):
        return True
    return False


def heading_level(line: str) -> int | None:
    stripped = line.lstrip()
    title = clean_line(line.strip(" #\t"))
    match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+[A-Z]", title)
    if match:
        return match.group(1).count(".") + 1
    if stripped.startswith("#"):
        return len(stripped) - len(stripped.lstrip("#"))
    if re.match(r"^(chapter|section|module|lesson|appendix)\b", title, re.I):
        return 1
    return None


def comparable_heading(text: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text.lower()).strip()


def find_section_end(lines: list[str], start: int, max_lines: int = 160) -> int:
    upper = min(len(lines), start + max_lines)
    start_level = heading_level(lines[start])
    start_title = clean_line(lines[start].strip(" #\t")).lower()
    broad_testing_heading = start_title.startswith("testing for ")
    for index in range(start + 1, upper):
        if not is_heading_line(lines[index]):
            continue
        if broad_testing_heading:
            continue
        current_level = heading_level(lines[index])
        if start_level is not None and current_level is not None and current_level <= start_level:
            return index
        if start_level is None:
            return index
    return upper


def meaningful_lines(lines: list[str], limit: int = 16) -> list[str]:
    results = []
    seen = set()
    for line in lines:
        stripped = clean_line(line)
        if len(stripped) < 25:
            continue
        if len(stripped) <= 140 and is_noise_heading(stripped):
            continue
        lowered = stripped.lower()
        if lowered in seen or looks_like_command(stripped):
            continue
        seen.add(lowered)
        results.append(shorten(stripped, width=180, placeholder="..."))
        if len(results) >= limit:
            break
    return results


def find_concept_candidates(lines: list[str], taxonomy_item: dict) -> list[int]:
    candidates = []
    for index, line in enumerate(lines):
        lowered = line.lower()
        if any(alias.lower() in lowered for alias in taxonomy_item["aliases"]):
            candidates.append(index)
    return candidates


def is_toc_or_table_context(lines: list[str], index: int) -> bool:
    window = "\n".join(lines[max(0, index - 8): index + 8]).lower()
    line = clean_line(lines[index])
    if "|" in line:
        return True
    if is_heading_line(lines[index]):
        return False
    if "table of contents" in window or "contents" in window:
        return True
    if re.search(r"\.{4,}\s*\d", window):
        return True
    return False


def section_substance_score(section_lines: list[str]) -> int:
    clean = meaningful_lines(section_lines, limit=20)
    score = len(clean) * 6
    joined = "\n".join(section_lines).lower()
    for keyword in (
        "how to test",
        "test objectives",
        "methodology",
        "process",
        "procedure",
        "review",
        "identify",
        "evidence",
        "report",
        "recommend",
        "expected result",
    ):
        if keyword in joined:
            score += 8
    return score


def score_concept_candidate(lines: list[str], taxonomy_item: dict, index: int) -> tuple[int, int, str]:
    end = find_section_end(lines, index)
    section_lines = lines[index:end]
    line = clean_line(lines[index])
    heading_text = clean_line(lines[index].strip(" #\t"))
    lowered = comparable_heading(heading_text)
    aliases = [alias.lower() for alias in taxonomy_item["aliases"]]
    score = section_substance_score(section_lines)
    confidence = "weak_mention"
    if is_heading_line(lines[index]):
        score += 30
        confidence = "body_match"
    if any(lowered == alias for alias in aliases):
        score += 35
        confidence = "primary_section"
    if any(lowered == f"testing for {alias}" for alias in aliases):
        score += 60
        confidence = "primary_section"
    if any(lowered.strip("# ").startswith(alias) for alias in aliases):
        score += 20
    if is_toc_or_table_context(lines, index):
        score -= 95
        confidence = "toc_only"
    if index < max(50, int(len(lines) * 0.08)) and not is_heading_line(lines[index]):
        score -= 25
    if len(meaningful_lines(section_lines, limit=4)) < 2:
        score -= 20
    return score, end, confidence


def find_best_concept_span(lines: list[str], taxonomy_item: dict) -> tuple[int, int, str] | None:
    candidates = find_concept_candidates(lines, taxonomy_item)
    if not candidates:
        return None
    scored = [(*score_concept_candidate(lines, taxonomy_item, index), index) for index in candidates]
    scored.sort(key=lambda item: (item[2] in PRIMARY_CONFIDENCES, item[0]), reverse=True)
    score, end, confidence, index = scored[0]
    if score < 5:
        return None
    return index, end, confidence


def build_chunks(full_text: str, taxonomy: list[dict] | None = None, include_weak: bool = False) -> list[dict]:
    lines = full_text.splitlines()
    chunks = []
    selected_taxonomy = taxonomy or TAXONOMY
    for item in selected_taxonomy:
        span = find_best_concept_span(lines, item)
        if span is None:
            continue
        start, end, confidence = span
        if not include_weak and confidence not in PRIMARY_CONFIDENCES:
            continue
        end = find_section_end(lines, start)
        chunk_lines = lines[start:end]
        citation_id = f"cite-{len(chunks) + 1:03d}"
        chunks.append(
            {
                "id": citation_id,
                "key": item["key"],
                "name": item["name"],
                "category": item["category"],
                "aliases": item["aliases"],
                "start_line": start + 1,
                "end_line": end,
                "heading": clean_line(lines[start]),
                "excerpt": meaningful_lines(chunk_lines, limit=18),
                "confidence": confidence,
            }
        )
    if chunks:
        return chunks

    for index, line in enumerate(lines):
        if not is_heading_line(line):
            continue
        heading = clean_line(line.strip(" #\t"))
        end = find_section_end(lines, index)
        citation_id = f"cite-{len(chunks) + 1:03d}"
        chunks.append(
            {
                "id": citation_id,
                "key": slugify(heading),
                "name": heading,
                "category": "procedural",
                "aliases": [heading],
                "start_line": index + 1,
                "end_line": end,
                "heading": heading,
                "excerpt": meaningful_lines(lines[index:end], limit=18),
                "confidence": "low",
            }
        )
        if len(chunks) >= 12:
            break
    return chunks


def build_weak_references(full_text: str, primary_chunks: list[dict], taxonomy: list[dict] | None = None) -> list[dict]:
    lines = full_text.splitlines()
    selected_taxonomy = taxonomy or TAXONOMY
    primary_keys = {chunk["key"] for chunk in primary_chunks}
    references = []
    for item in selected_taxonomy:
        if item["key"] in primary_keys:
            continue
        span = find_best_concept_span(lines, item)
        if span is None:
            continue
        start, end, confidence = span
        if confidence in PRIMARY_CONFIDENCES:
            continue
        references.append(
            {
                "key": item["key"],
                "name": item["name"],
                "category": item["category"],
                "source_lines": [start + 1, end],
                "matched_heading": clean_line(lines[start]),
                "confidence": confidence,
            }
        )
    return references


def extract_headings(text: str, limit: int = 24) -> list[str]:
    return [chunk["name"] for chunk in build_chunks(text)[:limit]]


def extract_commands(text: str, limit: int = 80) -> list[dict[str, str]]:
    candidates_found = []
    seen = set()
    lines = text.splitlines()
    in_fence = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        candidates = []
        if stripped.startswith(("$ ", "# ", "> ")):
            candidates.append(stripped[2:].strip())
        elif prompt_candidates := extract_prompt_commands(stripped):
            candidates.extend(prompt_candidates)
        elif in_fence and looks_like_command(stripped):
            candidates.append(stripped)
        else:
            candidate = extract_inline_command(stripped)
            if candidate:
                candidates.append(candidate)
        for candidate in candidates:
            candidate = expand_command_continuation(lines, index, candidate)
            candidate = sanitize_command(candidate)
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            caption = listing_caption_context(lines, index)
            before = nearest_context(lines, index, -1)
            after = nearest_context(lines, index, 1)
            candidates_found.append(
                {
                    "command": candidate,
                    "context": caption or before or after or "context incomplete",
                    "source": f"line {index + 1}",
                    "line": index + 1,
                    "score": command_score(candidate, index),
                }
            )
    candidates_found.sort(key=lambda item: (-int(item["score"]), int(item["line"])))
    selected = candidates_found[:limit]
    selected.sort(key=lambda item: int(item["line"]))
    for item in selected:
        item.pop("score", None)
    return selected


def expand_command_continuation(lines: list[str], index: int, command: str) -> str:
    if not needs_more_command_continuation(command):
        return command
    parts = [command.rstrip().rstrip("\\").strip()]
    cursor = index + 1
    while cursor < len(lines) and cursor <= index + 10:
        next_line = clean_line(lines[cursor].strip())
        if not next_line or next_line.startswith(("```", "~~~")):
            break
        if re.search(r"\b(?:Listing|Figure)\s+\d+\s*-", next_line):
            break
        prompt_commands = extract_prompt_commands(next_line)
        if prompt_commands:
            break
        line_continues = next_line.rstrip().endswith("\\")
        continuation = next_line.rstrip().rstrip("\\").strip()
        if continuation:
            parts.append(continuation)
        if not line_continues and not needs_more_command_continuation(" ".join(parts)):
            break
        cursor += 1
    return " ".join(parts)


def needs_more_command_continuation(command: str) -> bool:
    stripped = command.rstrip()
    if stripped.endswith(("\\", "|")):
        return True
    if stripped.count("'") % 2 == 1 or stripped.count('"') % 2 == 1:
        return True
    if stripped.count("{") > stripped.count("}") or stripped.count("[") > stripped.count("]"):
        return True
    return False


def extract_prompt_commands(line: str) -> list[str]:
    matches = list(SHELL_PROMPT_RE.finditer(line))
    if not matches:
        return []
    commands = []
    for current, next_match in zip(matches, matches[1:] + [None]):
        start = current.end()
        end = next_match.start() if next_match else len(line)
        segment = line[start:end].strip()
        if segment:
            commands.append(segment)
    return commands


def listing_caption_context(lines: list[str], index: int) -> str:
    start = max(0, index - 4)
    end = min(len(lines), index + 13)
    for line in [lines[index], *lines[index + 1:end], *lines[start:index]]:
        match = re.search(r"\b(?:Listing|Figure)\s+\d+\s*-\s*([^|]+)", clean_line(line))
        if match:
            caption = match.group(1).strip()
            if caption:
                return shorten(caption, width=140, placeholder="...")
    return ""


def extract_inline_command(line: str) -> str | None:
    match = re.match(
        r"^(?P<cmd>(?:nc|netcat|curl|nmap|openssl|socat|host|dig|whois|ffuf|gobuster|sqlmap|hydra|john|hashcat|ssh|python3?|crackmapexec|proxychains|msfvenom|msfconsole|searchsploit|ssh2john|wget)\b.+)$",
        line,
    )
    if not match:
        return None
    return match.group("cmd")


def sanitize_command(command: str) -> str | None:
    command = re.split(r"\s{6,}", command, maxsplit=1)[0].strip()
    command = re.split(r"\s+(?:Listing|Figure)\s+\d+\b", command, maxsplit=1)[0].strip()
    command = clean_line(command)
    command = command.replace("&lt;", "<").replace("&gt;", ">").replace("\\_", "_")
    command = command.replace("https:/ /", "https://").replace("http:/ /", "http://")
    command = re.sub(r"\.\s+(com|org|net|local|lan|ai)\b", r".\1", command)
    for marker in COMMAND_OUTPUT_SPLITS:
        if marker in command:
            command = command.split(marker, 1)[0].strip()
    for marker in (" is an alias", " name server ", " has address "):
        if marker in command:
            command = command.split(marker, 1)[0].strip()
    if " Host " in command:
        command = command.split(" Host ", 1)[0].strip()
    command = command.rstrip("|").strip()
    if " b'" in command or command.endswith("b'"):
        return None
    if "`" in command:
        return None
    parts = command.split()
    if len(parts) > 4 and parts[:3] == ["host", "-t", "ns"]:
        command = " ".join(parts[:4])
    elif len(parts) > 2 and parts[0] == "host" and parts[1] == parts[2]:
        command = " ".join(parts[:2])
    if not looks_like_command(command):
        return None
    broken_suffixes = {"-p", "--script", "-connect", "-H", "-d", "-u", "-x"}
    if command.split()[-1] in broken_suffixes:
        return None
    output_markers = ("HTTP/", "Content-Length:", "Server:", "Last-Modified:", "open ", "closed ")
    if any(marker.lower() in command.lower() for marker in output_markers):
        return None
    return command


def command_score(command: str, line_index: int) -> int:
    parts = command.split()
    if not parts:
        return 0
    first = parts[0].lower()
    if first == "sudo" and len(parts) > 1:
        first = parts[1].lower()
    score = 10
    if first.startswith("impacket-"):
        score += 80
    elif first in HIGH_VALUE_COMMANDS:
        score += 70
    elif first in MEDIUM_VALUE_COMMANDS:
        score += 35
    if any(term in command.lower() for term in ("192.168.", "172.16.", "megacorpone", "beyond.com", "rockyou", "meterpreter", "kerberos", "smb", "ssh", "http")):
        score += 12
    if first in {"cd", "cp", "mv", "mkdir", "cat"}:
        score -= 30
    if line_index < 3000 and first in {"chmod", "cat", "cd", "cp", "mkdir", "mv", "sudo"}:
        score -= 25
    return score


def looks_like_command(line: str) -> bool:
    if not line or line.startswith(("#", "//")) or len(line) > 180:
        return False
    first = line.split(maxsplit=1)[0]
    normalized = first.lower()
    if normalized.startswith("impacket-"):
        return True
    return normalized in COMMAND_STARTERS or first.startswith("./") or first.startswith(".\\")


def nearest_context(lines: list[str], index: int, step: int) -> str:
    cursor = index + step
    while 0 <= cursor < len(lines) and abs(cursor - index) <= 8:
        stripped = clean_line(lines[cursor].strip(" #\t"))
        if re.search(r"\b(?:Listing|Figure)\s+\d+\s*-", stripped):
            cursor += step
            continue
        if is_bad_command_context(stripped):
            cursor += step
            continue
        if stripped and not is_noise_heading(stripped) and not stripped.startswith(("```", "$ ", "# ", "> ")):
            return shorten(stripped, width=140, placeholder="...")
        cursor += step
    return ""


def is_bad_command_context(text: str) -> bool:
    if not text or text == "<!-- image -->":
        return True
    lowered = text.lower()
    if any(marker.lower() in lowered for marker in COMMAND_OUTPUT_SPLITS):
        return True
    if any(marker.lower() in lowered for marker in ("nmap done:", "nmap scan report", "port state service", "host is up", "not shown:", "wikipedia,", "microsoft documentation,")):
        return True
    if re.match(r"^\d+\s+\([^)]+,\s+\d{4}\),\s+https?://", text):
        return True
    if re.match(r"^(PORT|STATE|SERVICE)\b", text):
        return True
    return False


def commands_for_chunk(commands: list[dict], chunk: dict) -> list[dict]:
    return [
        command
        for command in commands
        if chunk["start_line"] <= int(command.get("line", 0)) <= chunk["end_line"]
    ][:8]


def extract_keyword_lines(text: str, keywords: tuple[str, ...], limit: int = 12) -> list[str]:
    results = []
    seen = set()
    for line in text.splitlines():
        stripped = clean_line(line)
        if len(stripped) < 20 or len(stripped) > 220:
            continue
        lowered = stripped.lower()
        if any(keyword in lowered for keyword in keywords) and stripped not in seen:
            results.append(stripped)
            seen.add(stripped)
        if len(results) >= limit:
            break
    return results


def bullets(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}\n"
    return "".join(f"- {item}\n" for item in items)


def link_list(items: list[dict]) -> str:
    if not items:
        return "- No source-supported concept chapters generated.\n"
    return "".join(f"- [{item['name']}](chapters/{item['key']}.md) - {item['category']}\n" for item in items)


def concept_table(chunks: list[dict]) -> str:
    if not chunks:
        return "- No named Red Team/Pentest concepts detected.\n"
    return "".join(
        f"- **{chunk['name']}** - {chunk['category']}; citation `{chunk['id']}`.\n"
        for chunk in chunks
    )


def render_skill(context: dict) -> str:
    schema_sections = "\n".join(f"- {title}" for title in context["required_section_titles"])
    commands = bullets(
        [f"`{cmd['command']}` - {cmd['context']} ({cmd['source']})" for cmd in context["commands"][:12]],
        "No source-supported commands detected; use commands.md as the command review surface.",
    )
    sources = bullets(context["sources"], "metadata.json")
    return f"""# {context['skill_name']}

## Skill Name
{context['skill_name']}

## Objective
Convert technical Red Team/Pentest source material into a source-grounded Skill for lab, education, defense, and explicitly authorized testing.

## Context
This Skill was generated from Docling-backed extraction metadata. It indexes source concepts into on-demand chapters and keeps operational material bounded by authorization, scope, and citations.

## Preconditions
- Written authorization and a defined scope are required before applying any procedure.
- Work must occur in a lab, training range, owned system, or client-approved environment.
- Operators must verify legal, organizational, and data-handling requirements before using commands or workflows.

## Procedure
1. Review `safety.md`.
2. Use the concept chapters for source-grounded details.
3. Use `checklist.md`, `workflows.md`, and `commands.md` only within authorized scope.
4. Use `reporting.md`, `coverage.json`, and `citations.json` to preserve traceability.

## Tools Commands
{commands}
## Expected Outputs
- Source-grounded Red Team/Pentest chapters.
- Checklist, workflow, command, troubleshooting, reporting, safety, and reference artifacts.
- Coverage and citation JSON files for auditability.

## Safety Constraints
- Authorized use only.
- Do not use generated commands as autonomous attack instructions.
- Stop when authorization, scope, or safety is unclear.

## References
{sources}
## Concept Chapters
{link_list(context['chunks'])}
## Supporting Artifacts
- [glossary.md](glossary.md)
- [patterns.md](patterns.md)
- [cheatsheet.md](cheatsheet.md)
- [checklist.md](checklist.md)
- [commands.md](commands.md)
- [workflows.md](workflows.md)
- [troubleshooting.md](troubleshooting.md)
- [reporting.md](reporting.md)
- [safety.md](safety.md)
- [references.md](references.md)
- [coverage.json](coverage.json)
- [citations.json](citations.json)

## Schema Coverage
{schema_sections}
"""


def render_chapter(chunk: dict, context: dict) -> str:
    chapter_commands = commands_for_chunk(context["commands"], chunk)
    command_lines = bullets(
        [f"`{item['command']}` - {item['context']} ({item['source']})" for item in chapter_commands],
        "No source-supported commands detected for this concept.",
    )
    excerpt = bullets(chunk["excerpt"], "No clean source excerpt available; inspect citation line range manually.")
    evidence_items = bullets(
        [
            f"Capture notes for source line range {chunk['start_line']}-{chunk['end_line']} and preserve citation `{chunk['id']}`.",
            f"Record observed behavior, affected asset, and defensive implication for {chunk['name']}.",
            "Store commands, outputs, screenshots, and error messages only when allowed by scope.",
        ],
        "No evidence guidance available.",
    )
    domain_steps = DOMAIN_PROCEDURE_STEPS.get(chunk["key"], [])
    procedure_items = bullets(
        [
            f"Read the source excerpt for {chunk['name']} and confirm it applies to the authorized target.",
            *domain_steps,
            "Execute only source-supported checks; mark missing context as `context incomplete`.",
            "Collect evidence and map it back to the citation before writing findings.",
        ],
        "No procedure guidance available.",
    )
    reporting_items = bullets(
        [
            f"Include `{chunk['id']}` in any finding or coverage note derived from this chapter.",
            "State scope, reproduction context, observed result, impact, and remediation.",
            "Separate verified findings from reference-only knowledge.",
        ],
        "No reporting guidance available.",
    )
    return f"""# {chunk['name']}

## Goal
Preserve source-grounded Red Team/Pentest knowledge for **{chunk['name']}**.

## Source Summary
{excerpt}
## Source-Derived Procedure
{procedure_items}
## Evidence To Collect
{evidence_items}
## Reporting Notes
{reporting_items}
## Decision Points
- If the source excerpt is only a table of contents or a weak mention, use this chapter as reference-only knowledge.
- If authorization, scope, inputs, or expected impact are unclear, stop and request human review.
- If commands are present without complete context, keep them in review status.

## Related Commands
{command_lines}
## Expected Outputs
- Concept-indexed notes and evidence requirements.
- Clear source references for follow-up analysis and reporting.

## Safety Constraints
- Authorized environments only.
- Do not execute commands outside approved scope.
- Escalate unclear source context to a human reviewer.

## Citation
- Citation ID: `{chunk['id']}`
- Source lines: {chunk['start_line']}-{chunk['end_line']}
- Matched heading: {chunk['heading']}
- Confidence: {chunk['confidence']}
"""


def render_glossary(context: dict) -> str:
    lines = [
        f"- **{chunk['name']}** ({chunk['category']}): source-supported concept, citation `{chunk['id']}`."
        for chunk in context["chunks"]
    ]
    if not lines:
        lines = ["- No source-supported glossary terms detected."]
    return "# Red Team/Pentest Glossary\n\n" + "\n".join(lines) + "\n"


def render_patterns(context: dict) -> str:
    categories = {}
    for chunk in context["chunks"]:
        categories.setdefault(chunk["category"], []).append(chunk)
    parts = ["# Red Team/Pentest Patterns\n"]
    if not categories:
        parts.append("- No source-supported patterns detected.\n")
    for category, chunks in sorted(categories.items()):
        parts.append(f"## {category.replace('_', ' ').title()}\n")
        for chunk in chunks:
            parts.append(
                f"- **{chunk['name']}**: review source lines {chunk['start_line']}-{chunk['end_line']} "
                f"before applying this pattern. Citation `{chunk['id']}`.\n"
            )
    return "\n".join(parts)


def render_cheatsheet(context: dict) -> str:
    rows = [
        "| Concept | Use When | Evidence | Safety Gate |",
        "|---|---|---|---|",
    ]
    for chunk in context["chunks"]:
        rows.append(
            f"| {chunk['name']} | Assessment scope includes {chunk['category']} work | "
            f"Notes tied to `{chunk['id']}` | Written authorization and bounded scope |"
        )
    if len(rows) == 2:
        rows.append("| No concept detected | Review source manually | Missing | Human review |")
    return "# Red Team/Pentest Cheatsheet\n\n" + "\n".join(rows) + "\n"


def render_checklist(context: dict) -> str:
    concepts = bullets([f"Review source guidance for {chunk['name']} (`{chunk['id']}`)." for chunk in context["chunks"]], "Review detected source sections before execution.")
    domain_checks = bullets(
        [
            f"[ ] {chunk['name']}: {DOMAIN_PROCEDURE_STEPS[chunk['key']][0]}"
            for chunk in context["chunks"]
            if chunk["key"] in DOMAIN_PROCEDURE_STEPS
        ],
        "[ ] No domain-specific checklist items detected.",
    )
    return f"""# Red Team/Pentest Checklist

## Scope and Authorization
- [ ] Written authorization is recorded.
- [ ] Targets, dates, techniques, and exclusions are defined.
- [ ] Stop conditions and escalation contacts are known.

## Source Coverage
{concepts}
## Domain-Specific Checks
{domain_checks}
## Command and Tool Readiness
- [ ] Every command in `commands.md` has context of use.
- [ ] Every command has a safety note.
- [ ] Commands with incomplete context are held for human review.

## Execution and Evidence
- [ ] Follow the relevant concept chapter or workflow.
- [ ] Capture expected outputs, observed errors, and source citations.
- [ ] Stop if observed behavior leaves approved scope.
"""


def render_commands(context: dict) -> str:
    if not context["commands"]:
        body = """## Command / Tool
- Command: Not found in source.
- Purpose: No source-supported command was detected.
- Context of use: context incomplete
- Preconditions: Written authorization and controlled environment.
- Required inputs: not found in source
- Important parameters: not found in source
- Expected output: not found in source
- Common errors: not found in source
- Safety note: Authorized-use only. Do not infer or invent commands from missing context.
- Source reference: full_text.txt
"""
    else:
        parts = []
        for item in context["commands"]:
            parts.append(f"""## Command / Tool
- Command: `{item['command']}`
- Purpose: Source-supported command or tool invocation.
- Context of use: {item['context']}
- Preconditions: Written authorization, controlled scope, and operator review.
- Required inputs: context incomplete unless explicit in source.
- Important parameters: Review source context before use.
- Expected output: context incomplete unless explicit in source.
- Common errors: See `troubleshooting.md` and source context.
- Safety note: Authorized-use only. Run only in lab, education, defense, owned, or explicitly approved assessment environments.
- Source reference: {item['source']}
""")
        body = "\n".join(parts)
    return "# Red Team/Pentest Commands\n\n" + body


def render_workflows(context: dict) -> str:
    concept_steps = bullets(
        [f"Map assessment tasks and evidence to **{chunk['name']}** (`{chunk['id']}`)." for chunk in context["chunks"]],
        "No named workflow concepts detected.",
    )
    domain_workflows = []
    for chunk in context["chunks"]:
        steps = DOMAIN_PROCEDURE_STEPS.get(chunk["key"])
        if not steps:
            continue
        domain_workflows.append(f"## {chunk['name']} Workflow\n")
        domain_workflows.append(f"- Goal: Apply source-grounded guidance for {chunk['name']} within approved scope.\n")
        domain_workflows.append("- Inputs: authorized targets, source citation, allowed tools, evidence repository, stop conditions.\n")
        domain_workflows.append("- Steps:\n")
        for step in steps:
            domain_workflows.append(f"  - {step}\n")
        domain_workflows.append("- Decision points: stop if authorization, target identity, or expected impact is unclear.\n")
        domain_workflows.append(f"- Source reference: `{chunk['id']}` lines {chunk['start_line']}-{chunk['end_line']}.\n\n")
    domain_workflow_text = "".join(domain_workflows) if domain_workflows else "## Domain Workflows\n- No domain-specific workflows detected.\n"
    return f"""# Red Team/Pentest Workflows

## Source-Grounded Review Workflow
- Goal: Convert source methodology into bounded Red Team/Pentest guidance.
- Scope assumptions: Authorized lab, education, defense, or approved testing only.
- Steps:
{concept_steps}- Decision points:
  - If a concept has no source-supported procedure, record it as reference knowledge.
  - If live testing is involved, verify written authorization and scope before use.
- Expected outputs: Concept-indexed notes, evidence needs, report sections, and citations.
- Safety controls: Human review, written authorization, and stop conditions for uncertainty.

{domain_workflow_text}
"""


def render_troubleshooting(context: dict) -> str:
    findings = context["troubleshooting_lines"] or [
        "If a command lacks context, do not run it until a human reviewer verifies scope, inputs, and expected output.",
        "If source and metadata disagree, preserve the discrepancy in references.md and review manually.",
    ]
    entries = []
    for index, item in enumerate(findings, start=1):
        entries.append(f"""## Issue {index}
- Symptom: {item}
- Likely cause: Source-specific context may be incomplete.
- Checks: Review nearby source text, command context, and assessment scope.
- Fix or workaround: Clarify source support before use.
- Safety or scope consideration: Do not bypass authorization, monitoring, or safety controls.
- Source reference: full_text.txt
""")
    return "# Red Team/Pentest Troubleshooting\n\n" + "\n".join(entries)


def render_reporting(context: dict) -> str:
    concept_lines = bullets(
        [f"Include coverage or finding notes for {chunk['name']} when in scope; cite `{chunk['id']}`." for chunk in context["chunks"]],
        "No named source concepts detected for reporting coverage.",
    )
    reporting_lines = bullets(
        context["reporting_lines"],
        "No source-specific reporting guidance detected; use the structure below.",
    )
    return f"""# Red Team/Pentest Reporting

## Evidence to Capture
{reporting_lines}
## Source Coverage in Report
{concept_lines}
## Finding Structure
- Title
- Scope and authorization context
- Affected asset or lab component
- Reproduction context from source-supported steps
- Observed result
- Risk or impact
- Defensive recommendation
- Evidence references
"""


def render_safety(_: dict) -> str:
    return """# Red Team/Pentest Safety

## Intended Use
This Skill is for education, research, defense, lab environments, and explicitly authorized security testing.

## Authorized Environments
- Personal labs and training ranges.
- Systems owned by the operator.
- Client or organizational environments with written authorization and defined scope.

## Prohibited Use
- No use against systems without explicit permission.
- No credential theft, persistence, exfiltration, disruption, or evasion outside approved scope.
- No autonomous attack execution.

## Scope Control
Keep activities within approved targets, dates, methods, and data-handling rules. Stop when scope, authorization, or safety is unclear.

## Commands and Tools
Commands must include context of use and a safety note before operation. Commands with incomplete context require human review.

## Human Oversight
A qualified human operator must review procedures, commands, impact, and authorization before use.
"""


def render_references(context: dict) -> str:
    markers = bullets(context["markers"], "No SOURCE markers found in full_text.txt.")
    sources = bullets(context["sources"], "metadata.json")
    concepts = concept_table(context["chunks"])
    weak_refs = bullets(
        [
            f"{item['name']} ({item['category']}) kept as weak reference; confidence `{item['confidence']}`, "
            f"source lines {item['source_lines'][0]}-{item['source_lines'][1]}."
            for item in context.get("weak_references", [])
        ],
        "No weak references retained.",
    )
    return f"""# Red Team/Pentest References

## Metadata Sources
{sources}
## Source Markers
{markers}
## Document Taxonomy Profile
- {context['document_profile']}

## Source Concepts Preserved
{concepts}
## Weak References Not Promoted To Chapters
{weak_refs}
## Citation Notes
- This prototype does not fabricate citations.
- `citations.json` contains line ranges for generated concept chapters.
- `coverage.json` records found and missing taxonomy concepts.
"""


def coverage_payload(context: dict) -> dict:
    found_keys = {chunk["key"] for chunk in context["chunks"]}
    weak_keys = {item["key"] for item in context.get("weak_references", [])}
    return {
        "skill_name": context["skill_name"],
        "docling_required": True,
        "docling_validated": context["docling_validated"],
        "document_profile": context["document_profile"],
        "taxonomy_total": len(context["taxonomy"]),
        "taxonomy": [
            {"key": item["key"], "name": item["name"], "category": item["category"], "aliases": item["aliases"]}
            for item in context["taxonomy"]
        ],
        "found_count": len(found_keys),
        "found_concepts": [
            {
                "key": chunk["key"],
                "name": chunk["name"],
                "category": chunk["category"],
                "citation_id": chunk["id"],
                "chapter": f"chapters/{chunk['key']}.md",
            }
            for chunk in context["chunks"]
        ],
        "weak_references": context.get("weak_references", []),
        "missing_concepts": [
            {"key": item["key"], "name": item["name"], "category": item["category"]}
            for item in context["taxonomy"]
            if item["key"] not in found_keys and item["key"] not in weak_keys
        ],
        "artifacts": REQUIRED_GENERATED_ARTIFACTS,
    }


def citations_payload(context: dict) -> dict:
    return {
        "sources": context["sources"],
        "citations": [
            {
                "id": chunk["id"],
                "concept_key": chunk["key"],
                "concept": chunk["name"],
                "category": chunk["category"],
                "source_lines": [chunk["start_line"], chunk["end_line"]],
                "matched_heading": chunk["heading"],
                "confidence": chunk["confidence"],
            }
            for chunk in context["chunks"]
        ],
    }


def build_context(full_text: str, metadata: dict, profile_dir: Path, out_dir: Path, schema: dict, allow_non_docling: bool = False) -> dict:
    validate_docling_requirement(metadata, allow_non_docling=allow_non_docling)
    required_fields = schema.get("skill", {}).get("required_fields", [])
    required_titles = [REQUIRED_SECTION_TITLES.get(field, field.replace("_", " ").title()) for field in required_fields]
    doc_profile = document_profile(full_text, metadata)
    taxonomy = taxonomy_for_profile(doc_profile)
    chunks = build_chunks(full_text, taxonomy=taxonomy)
    weak_references = build_weak_references(full_text, chunks, taxonomy=taxonomy)
    return {
        "skill_name": slug_to_title(source_name(metadata, out_dir)),
        "metadata_name": "metadata.json",
        "profile_dir": str(profile_dir),
        "document_profile": doc_profile,
        "taxonomy": taxonomy,
        "required_section_titles": required_titles,
        "sources": metadata_sources(metadata),
        "markers": source_markers(full_text),
        "chunks": chunks,
        "weak_references": weak_references,
        "concepts": [chunk["name"] for chunk in chunks],
        "headings": [chunk["name"] for chunk in chunks],
        "commands": extract_commands(full_text),
        "tool_lines": extract_keyword_lines(
            full_text,
            ("tool", "framework", "standard", "mitre", "owasp", "nmap", "burp", "metasploit", "kali"),
        ),
        "troubleshooting_lines": extract_keyword_lines(
            full_text,
            ("error", "fail", "failure", "troubleshoot", "debug", "warning", "denied", "timeout"),
        ),
        "reporting_lines": extract_keyword_lines(
            full_text,
            ("report", "finding", "evidence", "impact", "risk", "remediation", "mitigation"),
        ),
        "docling_validated": not allow_non_docling,
    }


RENDERERS = {
    "SKILL.md": render_skill,
    "glossary.md": render_glossary,
    "patterns.md": render_patterns,
    "cheatsheet.md": render_cheatsheet,
    "checklist.md": render_checklist,
    "commands.md": render_commands,
    "workflows.md": render_workflows,
    "troubleshooting.md": render_troubleshooting,
    "reporting.md": render_reporting,
    "safety.md": render_safety,
    "references.md": render_references,
}


def write_generated_artifacts(context: dict, out_dir: Path) -> list[Path]:
    written = []
    out_dir.mkdir(parents=True, exist_ok=True)

    chapters_dir = out_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    written.append(chapters_dir)
    expected_chapters = {f"{chunk['key']}.md" for chunk in context["chunks"]}
    for stale_chapter in chapters_dir.glob("*.md"):
        if stale_chapter.name not in expected_chapters:
            stale_chapter.unlink()
    for chunk in context["chunks"]:
        chapter_path = chapters_dir / f"{chunk['key']}.md"
        chapter_path.write_text(render_chapter(chunk, context).rstrip() + "\n", encoding="utf-8")
        written.append(chapter_path)

    for name, renderer in RENDERERS.items():
        target = out_dir / name
        target.write_text(renderer(context).rstrip() + "\n", encoding="utf-8")
        written.append(target)

    coverage_path = out_dir / "coverage.json"
    coverage_path.write_text(json.dumps(coverage_payload(context), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(coverage_path)

    citations_path = out_dir / "citations.json"
    citations_path.write_text(json.dumps(citations_payload(context), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(citations_path)
    return written


def generate(full_text_path: Path, metadata_path: Path, profile_dir: Path, out_dir: Path, allow_non_docling: bool = False) -> list[Path]:
    schema = load_profile_yaml(profile_dir / "schema.yaml")
    artifacts_config = load_profile_yaml(profile_dir / "artifacts.yaml")
    artifacts = artifacts_config.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"No artifacts configured in {profile_dir / 'artifacts.yaml'}")
    load_prompts(profile_dir, artifacts)

    full_text = read_text(full_text_path)
    metadata = json.loads(read_text(metadata_path))
    context = build_context(full_text, metadata, profile_dir, out_dir, schema, allow_non_docling=allow_non_docling)
    return write_generated_artifacts(context, out_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Red Team/Pentest Skill artifacts from extracted text.")
    parser.add_argument("full_text", type=Path, help="Path to full_text.txt")
    parser.add_argument("metadata", type=Path, help="Path to metadata.json")
    parser.add_argument("--profile", type=Path, default=Path("profiles/redteam"), help="Profile directory")
    parser.add_argument("--out", type=Path, required=True, help="Output skill directory")
    parser.add_argument("--allow-non-docling", action="store_true", help="Allow non-Docling metadata for synthetic tests only")
    args = parser.parse_args()

    written = generate(args.full_text, args.metadata, args.profile, args.out, allow_non_docling=args.allow_non_docling)
    print(f"Generated {len(written)} Red Team/Pentest artifact(s) in {args.out}")
    for path in written:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
