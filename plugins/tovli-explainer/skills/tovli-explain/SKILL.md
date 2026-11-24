---
name: tovli-explain
description: Explain Git branch and workspace changes in separate business and technical views, with flow diagrams, contract comparisons, and component diagrams in a standalone HTML report. Use for branch reviews, PR handoffs, release notes, deployment briefs, production-readiness reviews, or /tovli-explain.
---

# Tovli Explain

## Invoke this skill

In the ChatGPT desktop app, select `/tovli-explain` from the slash-command list after you enable or install this skill. In Codex CLI or the IDE extension, type `$tovli-explain` or use `/skills` to select it.

Explain what a Git branch changes for a technical reader who must understand system behavior and production impact.

Do not make the report a file-by-file diff summary. Reconstruct the behavior of the system before the branch and after the branch.

The final deliverable is a standalone HTML scrollyteller. It must work without a server and without external JavaScript libraries.

## Visual direction and motion

Create a cinematic, premium report with a dark ink background, warm ivory text, and electric mint or cyan accents. Use generous typography, clear scene numbering, layered atmospheric gradients, a fine grid, and orbital or typographic hero decoration. Keep the strongest visual treatment in the hero and transitions. Preserve readable diagrams, tables, and evidence panels.

Use restrained scroll-driven parallax on decorative layers only. Keep body text, diagrams, controls, and comparison labels stable. Use native scrolling without scroll hijacking. Keep decoration behind content, hidden from assistive technology, and unable to intercept pointer input. Read `references/report-visuals.md` for motion and accessibility requirements.

The visual presentation can be dramatic. The report prose must remain neutral, specific, evidence-backed, and consistent with the STE writing rules. Do not invent benefits, metrics, or certainty to suit the design.

## Business and technical presentation

Present business changes and technical changes in separate views. Show only one view at a time, with explicit navigation between them. Separate headings in one scrolling screen are not sufficient.

Business changes describe user goals, domain rules, decisions, state transitions, and observable outcomes. Use domain language and activity diagrams for workflows. Keep API status codes, schemas, file paths, classes, infrastructure, and deployment procedures in the technical view. If no business behavior changes, state that without inventing a business benefit.

Technical changes focus on contracts and components:

- Contracts: changed API requests and responses, events, data schemas, validation, errors, configuration interfaces, consumers, and compatibility.
- Components: changed responsibilities, dependencies, boundaries, interactions, and data ownership. Use component diagrams to show changed relationships.
- Connect deployment, rollback, and verification requirements to affected contracts or components.

Classify a change with both effects as linked business and technical scenes. Each scene must contain only one category. Keep source evidence in the technical view; business scenes can display evidence confidence without source details.

For each material change, present an explicit BEFORE baseline and its matching AFTER state within the relevant view. A general BEFORE summary does not replace the baseline for each changed flow, contract, or component. Show the same trigger, conditions, and scope in both states so the reader can identify the change.

## Inputs

Use the current repository and branch unless the user gives other values.

Optional inputs:

- base branch or base commit
- target branch or target commit
- output path
- deployment environment
- audience
- official ASD-STE100 checker or controlled dictionary

Default output path: `artifacts/branch-change-explainer.html`.

## Required result

The report must answer these questions:

1. What did the system do before this branch?
2. What does the system do after this branch?
3. What code path or configuration causes the change?
4. Which users, services, data, APIs, or jobs can observe the change?
5. What must happen during production deployment?
6. What can fail during deployment or rollback?
7. What evidence supports each important statement?
8. Which conclusions are inferred or still unknown?

## Step 1: Read repository instructions

Before analysis, read repository guidance that can change the interpretation of the code.

Look for these files and directories when they exist:

- `AGENTS.md`
- `README*`
- `CONTRIBUTING*`
- architecture documents
- ADRs
- deployment documents
- `.github/workflows/`
- `Dockerfile*`
- Helm or Kubernetes manifests
- Terraform or other infrastructure code
- database migration directories
- service configuration
- feature flag configuration

Repository rules override generic assumptions.

## Step 2: Select the comparison range

Prefer the merge base between the current branch and the repository default branch.

By default, compare that merge base with the effective workspace state. The effective workspace state includes the current `HEAD`, staged changes, unstaged changes, and untracked non-ignored files. Treat these changes as part of the change in the branch.

If the user supplies a target commit or explicitly asks for committed history only, compare commits only and report the working tree separately.

Use this order to find a default base:

1. A base ref that the user supplied.
2. The remote default branch from `refs/remotes/origin/HEAD`.
3. `origin/main` if it exists.
4. `origin/master` if it exists.
5. `main` if it exists.
6. `master` if it exists.

Then calculate the merge base.

Typical commands:

```bash
BRANCH="$(git branch --show-current)"
DEFAULT_REMOTE="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
BASE_REF="${BASE_REF:-$DEFAULT_REMOTE}"
MERGE_BASE="$(git merge-base HEAD "$BASE_REF")"
git status --short --branch
git log --oneline --decorate "$MERGE_BASE"..HEAD
git diff --find-renames --name-status "$MERGE_BASE"..HEAD
git diff --stat "$MERGE_BASE"..HEAD
git diff --find-renames "$MERGE_BASE"..HEAD --
git diff --find-renames --name-status "$MERGE_BASE"
git diff --stat "$MERGE_BASE"
git diff --find-renames "$MERGE_BASE" --
git ls-files --others --exclude-standard
```

Use `git diff <merge-base>` for tracked files because it includes staged and unstaged changes relative to the merge base. Read each untracked non-ignored file that can affect behavior, deployment, documentation, or evidence. Do not include ignored files unless the user asks for them.

For the BEFORE state, inspect the merge-base tree with `git show <merge-base>:<path>`. For the AFTER state, inspect the current filesystem. The current filesystem represents the combined committed and uncommitted state.

Record the working-tree status in the report. Identify which claims come from committed branch changes, staged changes, unstaged changes, and untracked files.

If the comparison is empty, say `No changes in the selected comparison.` explicitly. Check the effective tracked diff and non-ignored untracked files before making that statement; a clean working tree alone does not establish an unchanged branch. Include the comparison refs and working-tree scope in Technical. Do not fabricate change scenes, benefits, deployment actions, or comparison diagrams.

Determine business and technical impact separately. Say `No business changes identified.` when the changes do not affect business behavior. Say `No technical changes identified.` when contracts, components, and operational behavior are unchanged. If evidence is insufficient, say that the impact is unknown rather than claiming there are no changes.

## Step 3: Build an evidence map

For each material change, identify:

- changed entry points
- callers and consumers
- changed interfaces or contracts
- previous implementation
- new implementation
- tests that prove behavior
- configuration that enables behavior
- migrations that alter stored data
- deployment resources that alter runtime behavior

Use `git show <base>:<path>` when you must inspect the previous version of a file.

Do not infer previous behavior only from deleted lines. Inspect the previous call path when the behavior depends on surrounding code.

For each important claim, record at least one evidence item. Use a file path, symbol, test, configuration key, migration, or commit.

Classify evidence as one of these values:

- `direct`: the code or test directly proves the claim
- `corroborated`: two or more independent artifacts support the claim
- `inferred`: the claim follows from code structure but is not directly tested
- `unknown`: the available repository data is not sufficient

## Step 4: Reconstruct BEFORE behavior

Describe the observable behavior at the merge base.

Reconstruct the complete relevant previous path, including the components and contract definitions that produced the outcome. Record this baseline for presentation, not only for internal analysis. For an added capability, state that it did not exist before; for a removed capability, show its previous behavior. If the baseline cannot be established, label BEFORE as unknown and identify the missing evidence. Do not invent a previous flow.

Focus on behavior, not implementation details.

Include applicable items:

- request or event trigger
- validation
- state transition
- persistence
- external calls
- emitted events or messages
- API response
- retries and failure behavior
- authorization
- scheduling
- caching
- concurrency behavior
- operational signals

Use concrete conditions. Example: `When the queue message has no customer ID, the function rejects the message.`

## Step 5: Reconstruct AFTER behavior

Describe the same flow at the effective workspace state.

Include uncommitted changes in AFTER behavior when they alter the current files or configuration. State that the behavior is uncommitted when the change is not present in `HEAD`.

Make the delta explicit. Do not repeat unchanged behavior unless it is necessary to understand the change.

For each changed behavior, state:

- trigger
- previous result
- new result
- affected component
- externally visible effect
- evidence confidence

## Step 6: Assess production deployment impact

Always inspect production implications, even when the diff looks small.

Check these areas:

### Compatibility

- API request and response compatibility
- message or event schema compatibility
- database schema compatibility
- serialized data compatibility
- cache key or value compatibility
- cross-version service compatibility
- client compatibility

### Deployment requirements

- database migrations
- data backfills
- environment variables
- secrets
- configuration values
- feature flags
- infrastructure changes
- permissions or identities
- new dependencies
- build or runtime requirements
- deployment order across services

### Runtime risk

- startup failure
- partial rollout behavior
- retry storms
- duplicate work
- lost work
- timeout changes
- concurrency changes
- memory or CPU changes
- rate limits
- external dependency load
- unavailable rollback path

### Operations

- logs
- metrics
- traces
- health checks
- dashboards
- alerts
- release validation
- rollback validation

### Rollback

State whether rollback is:

- safe
- conditionally safe
- unsafe after a data change
- unknown

Explain the condition that controls rollback safety.

## Step 7: Write with ASD-STE100 rules

Use ASD-STE100 Simplified Technical English, Issue 9, as the writing target.

Read `references/ste-profile.md` before you write the report.

Important limits:

- Use one topic in each sentence.
- Prefer active voice.
- Use imperative voice for deployment procedures.
- Put one instruction in each procedural sentence, except simultaneous actions.
- Limit procedural sentences to 20 words.
- Limit descriptive sentences to 25 words.
- Limit a paragraph to six sentences.
- Avoid unnecessary synonyms.
- Use one term for one concept throughout the report.
- Treat code identifiers, API names, configuration keys, and product terms as technical nouns.
- Avoid idioms, metaphors, rhetorical language, and vague qualifiers.

Do not claim certified ASD-STE100 compliance unless an authorized workflow verifies the full controlled vocabulary and rules.

If no official checker or dictionary is available, show this status in the report:

`STE status: Writing rules applied. Controlled vocabulary not formally verified.`

## Step 8: Create the scrollyteller content model

Create a JSON file that follows the example in `examples/report-data.example.json`.

Read `references/report-visuals.md` for scene categories and diagram fields before authoring the JSON.

Use `category: business` for business outcomes and workflows. Use `category: technical` for contracts, components, deployment, rollback, verification, and source evidence. Categorize unknowns too. Write `summary.purpose` in business language and `summary.technical_purpose` in contract or component language.

Set `summary.change_status`, `summary.business_change_status`, and `summary.technical_change_status` to `changed`, `unchanged`, or `unknown`, based on the comparison and evidence. Leave scenes empty for an unchanged category. When the entire comparison is unchanged, set all three statuses to `unchanged`; the report must show a prominent no-change statement and explicit statements in both views. Keep comparison details in Technical.

The Business view must explain observable BEFORE and AFTER behavior for each material business change. The Technical view must compare previous and current contract definitions and component responsibilities, then explain applicable operational implications. Use the evidence map to support both states in both views.

A section must have one central idea. Keep its narrative and visual in the same category.

Use an `activity` diagram when there is a flow to explain. Show triggers, actions, decisions, labeled branches, and outcomes. For a changed flow, supply matched `visual.before` and `visual.after` graphs, even when only an outcome changes. For changed component responsibilities or dependencies, supply both previous and current `components` graphs. Keep matching node labels and layout stable where practical. Use a `contracts` table with populated BEFORE and AFTER cells for changed interfaces and compatibility. Use `before-after` for simple outcome comparisons, `deployment` for rollout and rollback, and `evidence` for proof. Single-state diagrams are suitable only for unchanged context; they cannot be the sole visual for a changed flow or component.

Prefer diagrams for flows rather than representing them only as bullets. Every arrow and branch must follow repository evidence. Make inferred or unknown paths explicit. Keep diagrams readable; divide large flows into multiple scenes instead of compressing them into one diagram.

## Step 9: Render the HTML

Run:

```bash
python scripts/render_report.py report-data.json artifacts/branch-change-explainer.html
```

If the repository does not contain the skill directory, run the renderer from this skill directory.

The generated HTML must be standalone. Do not require a CDN, network access, fonts, or a build step.

## Step 10: Validate the report

Before delivery, verify these conditions:

- The HTML opens as a local file.
- The report has a layered cinematic hero, generous typography, and readable high-contrast content.
- Decorative layers move at restrained, distinct rates during native desktop scrolling; text, diagrams, and controls remain stable.
- Mobile uses restrained or disabled parallax without horizontal page overflow.
- `prefers-reduced-motion` disables parallax and reveals while keeping all content visible.
- Keyboard navigation, visible focus, and readable text and diagram contrast work in both views.
- Printing removes decorative layers and sticky positioning and preserves the selected view's full narrative and visuals.
- No fonts, scripts, images, or other report assets require a network connection.
- Empty comparisons explicitly state that there are no changes, with the checked scope recorded in Technical.
- Each unchanged category states that no changes were identified; unknown impact is distinguished from unchanged impact.
- Scrolling changes the sticky visual panel.
- Business and Technical views never show their content simultaneously, including on mobile.
- Business scenes use domain language and contain no contract or component implementation details.
- Technical scenes focus on changed contracts and component relationships.
- Flows have readable activity diagrams with labeled decisions and outcomes.
- Each material change has an explicit BEFORE baseline and matching AFTER state within its own category.
- Changed flows and component relationships have both BEFORE and AFTER diagrams; contract comparisons contain both definitions.
- Diagram relationships agree with the evidence, with persistent BEFORE and AFTER labels.
- BEFORE and AFTER statements describe observable behavior under matching conditions; absent capabilities and unknown baselines are explicit.
- Deployment requirements are explicit.
- Rollback safety is explicit.
- Important claims include evidence.
- The report identifies whether the effective AFTER state includes uncommitted changes.
- Inferences are labeled.
- Unknowns are visible.
- No sentence exceeds the applicable STE word limit, except code or identifiers that make this impractical.
- No paragraph has more than six sentences.
- The report does not claim formal STE certification without verification.

## Report quality rules

Do not use commit messages as the primary explanation. Use them only as supporting evidence.

Do not report a changed test as a production behavior change unless production code or configuration supports that conclusion.

Do not assume that a new configuration key is active in production. Inspect defaults and deployment configuration.

Do not assume that a migration is reversible. Inspect down migrations, data loss, and old-code compatibility.

Do not treat successful unit tests as proof of deployment safety.

When evidence is incomplete, say what is unknown and what must be checked before deployment.
