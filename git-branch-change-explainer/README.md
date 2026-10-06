# Git Branch Change Explainer

This folder is an installable-style Agent Skill for a coding agent with repository access.

The skill compares a Git branch with its merge base. It reconstructs observable behavior before and after the branch. It also assesses production deployment and rollback implications.

The final output is a standalone HTML scrollyteller.

## Files

- `SKILL.md` — agent workflow and output contract
- `references/ste-profile.md` — ASD-STE100 writing profile
- `references/analysis-checklist.md` — repository and deployment checklist
- `scripts/render_report.py` — zero-dependency HTML renderer
- `examples/report-data.example.json` — renderer input example

## Quick renderer test

```bash
python scripts/render_report.py examples/report-data.example.json example-report.html
```

Open `example-report.html` in a browser.
