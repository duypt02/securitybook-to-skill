# Generate Red Team References

Generate a references document for the Skill.

The output must include these sections:
1. Source documents
2. Referenced tools and frameworks
3. Standards and external references
4. Citation notes

Quality requirements:
- `Source documents:` list every source file from `metadata.json` with its
  format and extraction method. Format:
  `[REF-N] <filename> — <format>, extracted via <method>`
  Example: `[REF-1] OWASP_Testing_Guide_v4.pdf — PDF, extracted via docling`
- `Referenced tools and frameworks:` list tools, frameworks, standards, and
  named methodologies that appear in the source text or concept chapters.
  For each tool, include: name, purpose as described in source, chapter reference.
  Do not list tools not mentioned in the source.
- `Standards and external references:` list any external standards (OWASP,
  NIST, ISO, CVE, CWE, ATT&CK, etc.) referenced in the source. If the source
  cites a specific test ID (e.g. OTG-AUTHN-002), preserve it exactly.
- `Citation notes:` note how artifacts in this skill trace back to source.
  Reference `coverage.json` (concept-level traceability) and `citations.json`
  (chapter-level line ranges). Explain how to read the citation IDs.
- Do not fabricate citations, DOIs, URLs, or publication dates not present in
  the source. If a URL appears in the source text, include it; otherwise omit.

Rules:
- Do not fabricate citations.
- Prefer filenames, source markers, and metadata fields over guesses.
- Keep references useful for tracing Skill artifacts back to source material.
