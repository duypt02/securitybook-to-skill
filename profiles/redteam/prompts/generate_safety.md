# Generate Red Team Safety Constraints

Generate a safety and authorized-use document for the Skill.

The output must include these sections:
1. Intended use
2. Authorized environments
3. Prohibited use
4. Scope control
5. Handling of commands and tools
6. Reporting and evidence handling
7. Human oversight requirements

Quality requirements:
- The evaluator checks `safety.md` for the presence of these specific terms.
  All of the following must appear in the output:
  - `authorized` or `authorization` (in the context of permitted use)
  - `prohibited` (for explicitly forbidden activities)
  - `scope` (defining what is in and out of bounds)
  - `human oversight` or `human operator` (requiring a human decision point)
  - `lab` or `training` or `owned` or `defense` or `research` (valid environments)
- `Intended use:` state clearly that the skill is for authorized lab, education,
  defense, owned systems, or explicitly approved assessment environments only.
  Name the source document so the authorized use is contextually grounded.
- `Authorized environments:` list the specific environment types where these
  techniques may be applied. Be concrete, not generic.
- `Prohibited use:` explicitly state what is not permitted. Must include:
  unauthorized systems, credential exfiltration, data destruction, bypassing
  monitoring. If the source names additional prohibited activities, include them.
- `Scope control:` describe how testers must verify they stay within authorized
  scope before and during the assessment.
- `Handling of commands and tools:` note that commands are reference material,
  not instructions for autonomous execution. Preconditions must be verified before
  running any command.
- `Human oversight requirements:` state that a qualified human operator must
  review findings, approve scope changes, and authorize any deviation from the
  planned test. Stop conditions must be defined.
- Do not weaken safety constraints even if the source document has minimal safety
  guidance. Safety requirements are baseline, not derived from source depth.

Rules:
- Emphasize education, research, defense, lab environments, and authorized testing.
- Do not frame the Skill as an autonomous attack tool.
- Make clear that all activities require explicit authorization.