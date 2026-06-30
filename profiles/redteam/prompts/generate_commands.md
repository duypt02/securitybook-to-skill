# Generate Red Team Command Reference

You are generating a Red Team command reference from a technical document.

Use only the provided source content.

For each command or tool usage, produce:

## Command / Tool
- Command:
- Purpose:
- Context of use:
- Preconditions:
- Required inputs:
- Important parameters:
- Expected output:
- Common errors:
- Safety note:
- Source reference:

Rules:
- Do not include commands without context.
- Do not invent commands that are not present in the source.
- Do not present the output as instructions for unauthorized activity.
- Assume all usage is for lab, education, defense, or authorized testing.
- If the source lacks enough context for a command, mark it as "context incomplete".

Quality requirements:
- `Purpose:` must be one sentence describing *what the command accomplishes*
  in the context of a security assessment — not a restatement of the source
  caption or context field.
  Good: "Enumerate open TCP/UDP ports on a target host to identify running services."
  Good: "Perform a SYN scan to detect open ports without completing the TCP handshake."
  Good: "Brute-force hostnames against a target domain to discover hidden subdomains."
  Bad: "Performs DNS query: using host to find the A host record for www.example.com."
  Bad: "Uses nmap to perform a SYN scan." (echoes tool + caption, no added value)
  Bad: "Source-supported command or tool invocation."
  The Purpose must add meaning beyond the tool name and the Context of use field.
- `Context of use:` must explain *when, where, and why* the command is used
  in the assessment workflow. Write at least 25 words. Do not copy a raw
  sentence fragment from the source that describes output or response — describe
  the usage context instead.
- `Expected output:` describe the expected output if the source provides it;
  otherwise write `not documented in source`.
- Search for commands within *each concept's section* of the source. Do not
  aggregate commands from unrelated sections into a single concept's block.