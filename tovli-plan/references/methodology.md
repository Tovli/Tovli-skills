# Planning canvas method and content contract

This skill distills a concrete planning artifact whose full markup was inspected. The original artifact had an always-visible project overview, plus four tabs: **Plan now**, **Decide**, **Steps**, **History**. Its structural patterns were adapted to arbitrary work; the sample book-project content is intentionally not copied into new plans.

## Verified anatomy and reusable interpretation

| Location | Original content pattern | Generalized purpose |
|---|---|---|
| Overview | Title, version, stage, change since previous version, one-paragraph need and solution, "What I need from you" | An executive brief and next required response |
| Plan now | "How it looks right now", visual mockups, Needs you, Settled, Out this round, user journey, edge cases, references | A short current agreed operating picture with concrete examples and scope boundaries |
| Decide | Questions with Today / Why it matters / My pick / What we get / If we skip it / options / note | A decision register that retains alternatives and clear distinctions between recommendation and selection |
| Decide | "My defaults" (small proposed decisions) | Low-stakes preference choices, not automatically approved |
| Steps | Ordered delivery units, How we test it, Where it ships, How it is built, Records, technical detail | A feasible, testable plan and links to evidence |
| History | Chronological feedback and quotes, version list | A traceable record of why the plan changed |

### Interactive answering and acceptance boundary

The source artifact used clickable choices, notes, a Copy answers button, and database-backed response storage. Our standalone viewer must preserve the choice + note experience while adding a separate **Custom answer** textbox, because a novel decision must not be conflated with rationale for an existing option.

- Clicking a choice (for a major question or low-stakes default) records a **draft answer** in browser memory; entering text in **Custom answer** automatically selects a custom response and deselects the predefined options. An additional note can be entered with or without a selection.
- The default or recommended choice is not automatically selected merely because it is recommended. The viewer separately marks a recorded canonical selection, a recommendation, and a locally edited draft.
- **Copy answers** copies only edited responses, including full option descriptions, custom text and optional notes. Provide a visible manual-copy fallback if clipboard APIs fail.
- **Download answers JSON** creates a separate draft export, not a rewritten `plan.json`. Persist drafts with local browser storage only if available. Do not depend on it for durability. Allow users to clear an individual draft and restore the canonical display.
- On return to a planning session, reconcile draft answers with current `plan.json`. Explicitly decide what becomes accepted, preserve provenance and superseded choices in History, and render a new version. For a novel answer, add an option to the canonical list with a stable unique ID before selecting it.

### Core semantics

- **Question (`decide.questions[]`)**: A consequential unresolved or settled choice. Store `my_pick_option_id` (recommendation) separately from `selected_option_id` (accepted answer). `status`: `open`, `settled`, `deferred`, `superseded`. A note without a selection is legitimate input, not necessarily settlement.
- **Direct decision (`decide.direct_decisions[]`)**: An accepted constraint or approval without prior option selection. Store source/provenance; do not promote an unconfirmed assertion into one.
- **Default (`decide.defaults[]`)**: A proposed routine choice. `status` is `proposed`, `explicitly_accepted`, `implicitly_accepted` (only with a recorded consent rule), or `overridden`.
- **Scope exclusion (`decide.out_this_round[]`)**: Something deliberately not done now, with reason and reconsideration trigger. "Not considered yet" and "explicitly out of scope" are different states.
- **Step (`steps.phases[]`)**: A deliverable with observable completion conditions. `commitment_status`: `proposed` vs `committed` vs `cancelled`; `status`: `not_started`, `in_progress`, `blocked`, `done`, `cancelled`. Distinguish sequence display order from actual dependencies.
- **History (`history.events[]`)**: Record substantive user-supplied decisions, feedback and revisions with date, actor, original quote when available, affected IDs, and previous/new values for reversals. Never manufacture quotes.
- **Version (`history.versions[]`)**: Ordered snapshots; last element must match `metadata.version`. Bump version for meaningful changes, not every chat exchange.

### First-session facilitation prompts

Ask only what meaningfully changes the plan:

1. **Outcome**: What are you trying to achieve, for whom, and what would prove it worked?
2. **Current reality**: What exists now? What is actually known vs assumed?
3. **Boundaries**: What is explicitly excluded, constrained, blocked or still unknown?
4. **Decisions**: What 1–3 choices determine the plan? Present options and an argued recommendation instead of an endless questionnaire.
5. **Execution**: What can be committed to now, by whom, and what observable result completes each step?

If the user offers a vague goal but needs a plan quickly, create a draft with explicit unknowns and proposed next steps. Prefer one sharp question over a large intake form. If a new project is trivial, use only the essentials rather than generating artificial complexity.

### Execution feasibility

Use the checks that could change the plan's sequence, commitments, or next ask.

- **Inputs and handoffs.** For each meaningful step, identify the input needed to start, the observable output, and who or what uses it. Group related steps by deliverable. Split a step further when it exposes a handoff, decision, or blocker.
- **Dependencies and bottlenecks.** Use `depends_on` for required predecessor steps and `decision_ids` to link choices that affect execution. Surface external prerequisites such as approvals, access, and supplier lead times in the relevant step or handoff. Identify the critical path when credible durations support it. When timing is uncertain, flag the dependencies most likely to delay delivery.
- **Resources and parallel work.** Identify the people, expertise, tools, and capacity needed. Include agent roles or compute needs when delegation or compute affects feasibility. Propose parallel work only where prerequisites and shared capacity allow it.
- **Time estimates.** When timing affects a decision and there is a credible basis, give a provisional range with assumptions about effort, availability, and wait times. Use `target_date` for evidenced dates and mark uncertain timing as open.
- **Risks and checkpoints.** For each material risk, link the affected steps and record the mitigation, the trigger for a fallback, and the fallback action. At checkpoints that gate dependent work, specify the evidence needed to proceed.

### Maintenance session

1. Read the existing plan and relevant new facts.
2. Identify what changed since its current `as_of` date. Classify each incoming item as fact, assumption, recommendation, decision, commitment, task status, scope change, or feedback.
3. Update canonical records using stable IDs; never silently delete old history. If changing a choice, preserve the previous selection in a new History event.
4. Derive the Plan now summary from accepted records. Keep unresolved decisions explicit and update immediate asks.
5. Bump version once for the revision, append a Versions record, validate, rerender the HTML.

### When to draw

- **Flow**: 3+ meaningful actions or branches, especially when it helps readers visualize what happens to a request, user, document, or piece of work. Do not confuse user journey with implementation order.
- **Dependency**: 3+ tasks with nontrivial prerequisites. The viewer also builds a dependency graph automatically from steps; do not duplicate it unless a curated higher-level graph adds value.
- **Architecture**: Distinct actors, services, teams, components, data boundaries or important handoffs. Keep labels understandable to a non-technical reader.

Native diagram format:

```json
{
  "id": "G-001",
  "title": "Customer request flow",
  "type": "flow",
  "description": "How a request is handled",
  "nodes": [
    {"id":"request", "label":"Request arrives"},
    {"id":"review", "label":"Triage and review"},
    {"id":"result", "label":"Response delivered"}
  ],
  "edges": [
    {"from":"request", "to":"review"},
    {"from":"review", "to":"result"}
  ],
  "related_decision_ids": []
}
```

The viewer creates accessible SVGs without network libraries and lists each node/edge in text. Keep graphs small; very large graphs are better split into one high-level graph and detailed supporting documents. Avoid unsupported claims of dependency/sequence: draw only edges that are known or explicitly labeled proposed.

### Project domains

Examples where this same structure works:

- **Product feature**: Plan now describes the accepted user experience; Decide holds UX/architecture choices; Steps defines build, QA, release; History records feedback/revisions.
- **Customer discovery**: Plan now describes interview aims and evidence; Decide covers segment, method, and hypothesis choices; Steps holds outreach and validation; History preserves what participants actually said.
- **Work reorganization**: Plan now describes the agreed target operating model; Decide holds trade-offs and governance choices; Steps defines transition and success criteria; History records approvals.
- **Personal learning plan**: Plan now describes desired competency; Decide holds priorities and learning approach; Steps defines practice blocks and demonstrations; History tracks evidence and plan changes.

### Facts, inferences and sources

Only put verified statements in **Today**, decision provenance, or completed outcome fields. Put speculative statements in assumptions, options, or explicitly marked proposals. If relevant connected materials are available, extract the factual baseline and link them in supporting records. Do not infer that a plan has shipped solely from a green pull request or completed test; distinguish approved, built, merged, deployed, and observed outcomes.
