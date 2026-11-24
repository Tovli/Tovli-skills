---
name: tovli-plan
description: Facilitate decision-driven planning for any project, initiative, research, professional task, personal work, or ongoing project. Use when a user asks to plan, scope, revisit, organize, make decisions on, or track substantial work, or asks for a reusable project plan. Maintain a canonical `plan.json` in the project and generate a standalone interactive `plan.html` viewer with clickable answer choices, custom-answer and note fields, Copy answers and answers JSON export, Overview, Plan now, Decide, Steps, and History, plus SVG process, dependency, or architecture diagrams when useful. Also use to revise an existing plan while preserving decisions and history.
---

# Tovli Plan

Turn a planning conversation into **two synchronized files**, normally in `<project>/planning/`:

- **`plan.json`**: canonical, structured planning state. This is the only editable source of truth.
- **`plan.html`**: standalone, responsive visualization of canonical JSON with an **interactive draft-answer workspace** in Decide. It includes clickable choices, custom answers, notes, a Copy answers button, and draft-answer JSON export, plus an always-visible overview and four tabs: **Plan now**, **Decide**, **Steps**, **History**. It works without a server or CDN.

Use `scripts/plan_tool.py` to initialize, validate, and render both files. Never treat HTML draft responses as changes to the canonical plan. The HTML can collect responses but cannot silently write into the project JSON. Users must copy/export responses and have the planning skill reconcile them. See [the planning method](references/methodology.md) for field semantics and examples. See [the JSON Schema](references/plan.schema.json) for the contract.

## Operating workflow

1. **Find the context.** Determine the current project, objective, available docs, prior agreements, constraints, and desired outcome. If this is existing work, locate the current `plan.json` first and update it rather than starting another plan. Read relevant attached or connected material when available. If the user has not named a project directory, use a sensible workspace location and show it in the handoff; do not assert a remote repository was updated unless the write actually occurred.
2. **Facilitate, not just transcribe.** Distinguish observed facts, hypotheses, recommendations, decisions, scope exclusions, and actual commitments. Look for the most consequential unresolved choices. Challenge unsupported assumptions; make trade-offs visible. Ask at most a few high-value questions in conversation when answers materially block planning. Otherwise create a useful draft with unknowns explicitly open. Never invent an owner, deadline, decision, quote, evidence, or completed status.
3. **Fill the four views and overview.** Use the canonical fields in `assets/plan.template.json`:
   - **Overview:** identity, stage, problem, objective, plain-language approach, latest status, and one immediate actionable ask (or `unknown` / `none` honestly).
   - **Plan now:** concise **currently agreed** picture, visual examples, current user/operating journey, assumptions, success measures, exceptions, and supporting sources. Derive **Needs you**, **Settled**, and **Out this round** from canonical records; don't duplicate them in plan state.
   - **Decide:** major questions, factual baseline, why the choice matters, **My pick**, expected benefit, cost of skipping, alternatives with trade-offs, **actual recorded option**, note, owner/decision provenance. The HTML makes options clickable, accepts a separate custom answer and optional note, and exposes **Copy answers** / **Download answers JSON**. These edits remain drafts. Add low-stakes choices to `defaults` as **proposed** until accepted; use `direct_decisions` for settled facts/approvals that did not need a multi-option question. Store exclusions in `out_this_round`.
   - **Steps:** ordered outcomes, owners when known, dependency IDs, linked decision IDs, commitment vs execution status, acceptance criteria, validation, handoffs, delivery destination, risks, and source records. Separate the end-user journey from implementation order.
   - **History:** append-only dated records of actual user feedback, choices, reversals, and important changes. Preserve attributable wording as a quote only when supplied by the user/source. Maintain chronological `versions` and keep `metadata.version` equal to the last version.
4. **Add diagrams only if they clarify a real relationship.** For multi-step journeys, branching workflows, dependencies, or component boundaries, add a `diagrams[]` object with a clear title, `type` (`flow`, `dependency`, or `architecture`), 2–12 labeled nodes, and explicit directed edges. Do not add a decorative diagram to a simple checklist. Step dependencies also generate an automatic graph in the Steps tab. The viewer renders diagrams using local SVG and includes a text equivalent.
5. **Validate and render.** Use the commands below. Correct all errors and investigate warnings. Inspect the generated HTML and verify that the recorded option is distinguished from recommendations and drafts; click choices, enter a custom answer and a note, exercise Copy answers and Download answers JSON, and check that links and diagrams resolve and that the immediate ask is consistent with open blocking decisions.
6. **Handoff.** Provide both files, the outstanding choices, and the exact local or workspace paths. State what is provisional. Explain that the Decide tab can collect draft answers, saved in browser storage when allowed, and that **Copy answers** or **Download answers JSON** must be returned to the planning session to update the plan. On later sessions, edit `plan.json`, append meaningful changes to History, bump the version when materially revised, and regenerate `plan.html`.

## Commands

The script uses Python standard library for rendering; install `jsonschema` for complete schema and format validation (`python -m pip install jsonschema`).

```bash
# First planning session: generate starter JSON and HTML in the project
python <skill-root>/scripts/plan_tool.py init <project>/planning/plan.json \
  --title "Project or work name" --id PLAN-001

# Edit plan.json to reflect the conversation, then validate and regenerate
python <skill-root>/scripts/plan_tool.py validate <project>/planning/plan.json
python <skill-root>/scripts/plan_tool.py render <project>/planning/plan.json

# Optional: direct a standalone HTML viewer to another filename
python <skill-root>/scripts/plan_tool.py render <project>/planning/plan.json --out <project>/plan.html
```

Do not re-run `init` over an existing plan; it refuses overwrites unless forced. When the user gives a different naming convention or file location, honor it.

## Incorporating answers from HTML

The viewer's **Copy answers** button produces a plain-text summary of the user's *draft* responses. **Download answers JSON** exports a machine-readable payload containing `plan_id`, `plan_version`, `status: draft_not_applied`, question/default IDs, `choice_id`, `custom_answer`, `note`, and timestamps. Both contain **only actively edited answers**, not every already-recorded plan decision. Save the response in the project or paste it into the conversation, then:

1. Open the **current** canonical `plan.json`. Confirm that the exported plan ID/version matches. If versions diverged, reconcile changes by stable IDs and ask about conflicts; never blindly overwrite newer decisions.
2. For `choice_id` matching an option, resolve the option text and record that option only if the response was intentionally submitted as a decision. For `choice_id: "__custom__"`, add a new uniquely identified option containing the custom text, then select it; never shoehorn the custom answer into an unrelated option. A note without a choice is feedback, not automatic acceptance.
3. For changed settled decisions, preserve the previous choice, rationale, and who/when in a History event before updating. Apply the same provenance standard to accepted defaults. Recompute dependent Plan now text, immediate asks, step dependencies, and status; avoid invented facts.
4. Update the version and history only after a substantive confirmed change, validate and regenerate HTML. The viewer's browser storage is a convenience, not a reliable project backup; recommend copying or downloading answers before replacing the HTML.

Do not claim the page can edit `plan.json` in place. Browsers commonly disallow silently writing local files. See [methodology](references/methodology.md) for acceptance rules.

## Decision and data invariants

- **Selection is not recommendation.** Never copy `my_pick_option_id` into `selected_option_id` without a decision. A settled question needs an actual selection or an explicit recorded answer in its note, with provenance.
- **No silent defaults.** `default_option_id` is a suggestion, not acceptance. Use `status: proposed` unless the user approves it. `implicitly_accepted` requires an explicit previously agreed consent rule in History.
- **Do not promote proposals into commitments.** A step can be `not_started` and `proposed`. Use `commitment_status: committed` only after a real commitment. `owner`, `target_date` and `done_when` are not to be invented.
- **No fake certainty in Plan now.** If a major choice is open, state its effect on the current plan. Preserve genuine ambiguity and distinguish proposed vs agreed parts in prose.
- **History is not a rewritten summary.** Append events rather than overwriting old feedback. When decisions change, record old and new values, cause, and affected IDs. Update `as_of`, `version`, and current views accordingly.
- **Stale asks are defects.** Never show "nothing needed" while a blocking decision is open. Update immediate asks when a step is completed or cancelled.
- **Portable outputs.** JSON and rendered HTML must remain self-contained and contain no credentials. Embedded JSON is visible in HTML; never embed secrets, private tokens, or raw sensitive documents. Link restricted material instead, respecting its access controls. The HTML shows a canonical snapshot plus locally collected draft responses; rerun render after canonical JSON edits. Local storage can be unavailable on some `file://` and privacy-restricted browsers, so Copy answers and Download answers JSON must always work offline.
- **Generalize to the actual domain.** In non-software work, "Where it ships" means where the output is delivered/used, and "How we test it" means how outcomes will be validated. Do not force software terminology, PRs, or release pipelines into unrelated work.

## File map

- `assets/plan.template.json` — starter canonical document; leave unknowns blank, not invented.
- `assets/plan-viewer.html` — HTML/CSS/JS layout and native SVG graph renderer, interactive draft responses, Copy answers, Download answers JSON, optional local browser draft persistence; `__PLAN_DATA__` injection point for the tool.
- `references/plan.schema.json` — structural contract; `scripts/plan_tool.py` runs it when `jsonschema` is installed and always performs ID, relationship, dependency, and state checks.
- `references/methodology.md` — verified anatomy of the motivating artifact, prompts, decision-state meanings, and diagram guidance.
- `examples/sample-plan.json` — fictional cross-domain example demonstrating recommendations vs actual selections and diagrams.
- `scripts/plan_tool.py` — `init`, `validate`, `render`.

## Quality check before delivery

Confirm that (1) all four tabs render, (2) the overview's action is current, (3) option clicks, custom text, note-only answers, copying, and JSON answer export work without turning drafts into accepted decisions, (4) no open decision has been silently accepted, (5) step owners/dates/commitment state are evidenced or blank, (6) all references and diagram edges validate, (7) history/version are consistent, (8) `plan.html` represents the latest `plan.json`, and (9) links/files are verified. For a new work plan, give the user a compact summary of objective, open questions, next steps and major risks alongside the files.
