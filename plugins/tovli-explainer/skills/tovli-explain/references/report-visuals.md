# Report categories and visuals

## Cinematic design and parallax

Use a dark ink canvas, warm ivory body text, and electric mint or cyan accents. Build visual depth with atmospheric gradients, a fine grid, orbital lines, and oversized decorative typography. Use local system fonts with generous headings and a clear reading hierarchy. Reserve saturated accents for navigation, active states, and comparison highlights. Avoid placing decoration over diagram labels or evidence.

Apply scroll-driven parallax only to decorative hero and background layers. Give layers different, bounded travel distances for depth. Update transforms through a single `requestAnimationFrame` loop and passive scroll listeners; avoid layout reads and writes per layer on every scroll event. Keep native scrolling and document reading order. Never pin or move reading text, diagrams, controls, or BEFORE and AFTER labels for visual effect. Existing sticky comparison panels can remain stationary while the narrative scrolls.

Decorative layers must use `aria-hidden="true"`, ignore pointer input, and stay behind readable content. Keep contrast at least 4.5:1 for normal text and 3:1 for large text and essential diagram elements. Provide visible keyboard focus. View navigation and every report action must work with a keyboard.

Reduce travel or disable parallax on small screens. Disable parallax, smooth scrolling, and reveal animations when `prefers-reduced-motion: reduce` matches, including if the preference changes while the report is open. Reset transforms and leave all content fully visible. Reveals are progressive enhancement: content must remain readable when JavaScript is unavailable. Do not add animation libraries, remote fonts, or other network dependencies.

For printing, remove decoration, animation, sticky positioning, and fixed-height scroll containers. Print the selected view's complete narrative and its visuals in document order. Do not mix Business and Technical content in the print layout.

Keep this treatment independent of scene data: do not add unsupported decorative fields to the report JSON. Use neutral STE prose and repository evidence for titles, findings, comparisons, and confidence. Visual drama must not imply unproved benefits, increased certainty, or invented metrics.

## Category boundaries

Every new scene must include `category: "business"` or `category: "technical"`. The renderer places each category in a separate view. Legacy scenes without a category go into Technical; do not omit categories in new reports.

Business narratives and diagram labels use domain terms, actions, decisions, and outcomes. Technical narratives and visuals describe contracts, components, compatibility, and operational requirements. Split a change with both kinds of impact into two scenes. Use evidence items on both; source details are collected in the Technical view, while Business scenes show confidence only.

Use `summary.purpose` for the business summary and `summary.technical_purpose` for the technical summary. Keep the report title neutral. Git scope, deployment risk, and source evidence appear only in Technical. Unknowns use objects such as `{"category": "business", "detail": "The supported invoice search scope is unknown."}`. Legacy unknown strings go into Technical.

## Change status and empty comparisons

New reports set three summary fields: `change_status` for the entire Git comparison, `business_change_status` for business impact, and `technical_change_status` for technical impact. Values are `changed`, `unchanged`, or `unknown`. These are analysis conclusions, not counts of scenes. A clean workspace does not exclude committed branch changes.

For a verified empty comparison, use:

```json
{
  "summary": {
    "change_status": "unchanged",
    "business_change_status": "unchanged",
    "technical_change_status": "unchanged"
  },
  "scenes": []
}
```

Keep the actual refs, comparison scope, and checked worktree status in `meta`. The renderer shows `No changes in the selected comparison.` prominently and states that both categories have no changes. An unchanged category must have no change scenes. For a category without changes in an otherwise changed comparison, set just that category to `unchanged`.

Use `unknown` when evidence is insufficient and explain the gap in categorized `unknowns`. Empty scenes without an explicit status mean that analysis was not recorded; they do not prove there were no changes. Do not include invented benefits or deployment requirements for an empty comparison.

## Activity and component diagrams

Use `meta.worktree_status` to state which committed and uncommitted changes are included in the target snapshot.

Use `visual.type: "activity"` for flows, and `visual.type: "components"` for component relationships. Both accept `title`, `nodes`, and `edges`:

```json
{
  "type": "activity",
  "title": "AFTER: invoice search",
  "nodes": [
    {"id": "start", "kind": "start", "label": "Search requested", "row": 0, "column": 0},
    {"id": "found", "kind": "decision", "label": "Invoice found?", "row": 1, "column": 0},
    {"id": "show", "kind": "action", "label": "Show invoice", "row": 2, "column": 0},
    {"id": "empty", "kind": "action", "label": "Show no matches", "row": 2, "column": 1},
    {"id": "end", "kind": "end", "label": "Search complete", "row": 3, "column": 0}
  ],
  "edges": [
    {"from": "start", "to": "found"},
    {"from": "found", "to": "show", "label": "Yes"},
    {"from": "found", "to": "empty", "label": "No"},
    {"from": "show", "to": "end"},
    {"from": "empty", "to": "end"}
  ]
}
```

Node IDs must be unique. Rows and columns are nonnegative integers and identify positions on a grid; avoid placing two nodes in the same cell. If omitted, each node occupies its own row in one column. Edges must reference existing nodes. Keep edge labels short and label each decision branch. Supported kinds are `start`, `end`, `decision`, `action`, `component`, `store`, and `external`. Mark changed components with `changed: true`.

For a changed flow or component relationship, put two graph objects under `visual.before` and `visual.after` instead of top-level nodes and edges. Both are required for a change comparison. Give both a descriptive `title`; the renderer adds persistent BEFORE and AFTER labels. Keep matching node IDs, labels, and grid positions stable where practical so changed outcomes, dependencies, and ownership stand out. Keep both states within the scene's category. Rows and columns are layout only; connections must be specified in edges.

The single graph above illustrates the graph shape only. A complete change scene wraps its previous and current graphs like this:

```json
{
  "type": "activity",
  "before": {"title": "Previous invoice search", "nodes": [], "edges": []},
  "after": {"title": "Current invoice search", "nodes": [], "edges": []}
}
```

Replace the placeholder arrays with evidence-backed graphs; see the complete example report. Show the previous error path as well as the new successful or empty-result path. For components, show removed dependencies and previous ownership in BEFORE, and added dependencies and new ownership in AFTER. Single-state graphs are suitable for unchanged context only.

BEFORE represents the merge-base tree; AFTER represents the effective target snapshot, including local edits by default. Match triggers and conditions across states. For additions or removals, explicitly show which capability is absent. If the baseline is unknown, explain the missing evidence in a `before-after` comparison instead of fabricating a graph.

The renderer draws SVG without external libraries or network access. Inspect the resulting diagrams for overlapping edges, readable labels, valid decision paths, and evidence coverage. Divide a large graph across scenes when needed.

## Contract comparisons

Use `visual.type: "contracts"` only in Technical. Supply `rows`, each with `name`, `before`, `after`, and `compatibility`:

```json
{
  "type": "contracts",
  "rows": [
    {
      "name": "GET /invoices/{id}: missing invoice",
      "before": "HTTP 404",
      "after": "HTTP 200 with an empty result",
      "compatibility": "Consumers must handle the empty result."
    }
  ]
}
```

Populate both `before` and `after` for every changed contract. State affected producers and consumers in the narrative. Identify changed fields, validation, error semantics, or version compatibility where applicable. State the previous behavior in the narrative too; do not describe only the new contract.

## Other visuals

- `before-after`: `before_title`, `before`, `after_title`, and `after` for short outcome lists.
- `deployment`: `risk`, `requires`, `rollback`, `verify`, and `compatibility` in Technical only.
- `evidence`: displays the scene's evidence items in Technical only.

Each evidence item has `label` (`direct`, `corroborated`, `inferred`, or `unknown`) and `detail`. The Technical source register associates every item with its scene ID. Business confidence badges never expose the source details.
