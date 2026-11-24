# Tovli Explain

This folder contains the `tovli-explain` Agent Skill for agents with repository access. In the ChatGPT desktop app, select `/tovli-explain` from the slash-command list after enabling or installing the skill. In Codex CLI or the IDE extension, invoke it with `$tovli-explain` or select it with `/skills`.

The skill compares a Git branch with its merge base. By default, it treats the current workspace as the AFTER state, including committed, staged, unstaged, and untracked non-ignored changes. It reconstructs observable behavior before and after the branch and assesses production deployment and rollback implications.

The final output is a standalone HTML scrollyteller.

Reports use a cinematic dark ink design with warm ivory typography, mint and cyan accents, layered hero decoration, and restrained scroll-driven parallax. Motion applies to decorative layers; diagrams and reading content stay stable. Native scrolling, keyboard navigation, offline use, and print output remain available. Mobile reduces motion, and the system's reduced-motion preference disables parallax and reveals while preserving all content.

The design is expressive; analysis stays neutral and evidence-backed. No visual treatment changes the confidence or meaning of a finding.

Reports have separate Business and Technical views. Business scenes explain domain outcomes and workflows with activity diagrams. Technical scenes focus on contract comparisons and component diagrams, with deployment and evidence details in the same technical view. Only one view is visible at a time.

Every material change includes a BEFORE baseline and matching AFTER state. Changed workflows and components use paired diagrams; contract tables compare both definitions. BEFORE comes from the merge base, and AFTER includes the current workspace by default.

Empty comparisons explicitly state that there are no changes. Each view also states when its category has no changes; insufficient evidence is reported as unknown instead.

## Install

Install or copy this entire folder into a skill location supported by your agent. For Codex, a user-level location is `~/.agents/skills/tovli-explain`; a repository-level location is `.agents/skills/tovli-explain`. Keep `SKILL.md`, `agents/`, `references/`, `scripts/`, and `examples/` together.

## Files

- `SKILL.md` — agent workflow and output contract
- `agents/openai.yaml` — Codex display name and starter prompt
- `references/ste-profile.md` — ASD-STE100 writing profile
- `references/analysis-checklist.md` — repository and deployment checklist
- `references/report-visuals.md` — scene categories and diagram data format
- `scripts/render_report.py` — zero-dependency HTML renderer
- `examples/report-data.example.json` — renderer input example

## Quick renderer test

```bash
python scripts/render_report.py examples/report-data.example.json example-report.html
```

Open `example-report.html` in a browser.

## Renderer checks

Run the regression checks from this skill directory:

```bash
python -B -m unittest discover -s tests -v
```

An optional browser check verifies parallax, reading progress, live reduced-motion changes, desktop and mobile view isolation, diagram switching, keyboard navigation, print layout, and offline loading. It requires Node 22 or later and a Chromium browser:

```bash
node tests/browser_check.mjs "<browser-executable>" examples/example-report.html
```
