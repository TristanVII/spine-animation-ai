# Codex working notes

This fork uses Codex as its agent host. The character animation skill is at
`.agents/skills/spine-animation/SKILL.md`.

- Read `SKILL.template.md` before changing the skill. Read the relevant tool and
  reference before changing animation behavior.
- Edit canonical tools in `scripts/` and references in `references/`. Run
  `python3 build_skill.py` after edits. Do not edit generated bundle files.
- Run `python3 build_skill.py --check` and `python3 -m unittest discover -s tests`.
- Preserve input artwork, existing user edits, and earlier exports. Write new
  animation outputs to a separate directory.
- Keep image provider credentials outside Git. Local animation tools require
  no agent model API key; optional Gemini generation remains a separate service.
- For Reskin Studio UI work, follow `reskin-app/AGENTS.md` and its design system.
- Keep the upstream license and attribution. Do not claim runtime or visual
  validation from a successful JSON build alone.
