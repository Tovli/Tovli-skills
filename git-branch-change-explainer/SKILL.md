---
name: git-branch-change-explainer
description: Explain the functional and operational changes in a Git branch. Reconstruct behavior before and after the change, assess production deployment implications, and generate a standalone HTML scrollyteller in ASD-STE100-style English. Use for branch reviews, PR handoffs, release notes, deployment briefs, and production-readiness explanations.
---

# Git Branch Change Explainer

Explain what a Git branch changes for a technical reader who must understand system behavior and production impact.

Do not make the report a file-by-file diff summary. Reconstruct the behavior of the system before the branch and after the branch.

The final deliverable is a standalone HTML scrollyteller. It must work without a server and without external JavaScript libraries.

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
```

Do not include uncommitted work in the branch comparison unless the user asks for it. Report uncommitted work separately when it can affect the analysis.

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

Describe the same flow at the branch head.

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

Use these story sections when they apply:

1. Change summary
2. Before the change
3. The change path
4. After the change
5. Production deployment
6. Rollback
7. Production verification
8. Evidence and unknowns

A section must have one central idea.

Use a `before-after` visual for behavior changes.

Use a `deployment` visual for rollout and rollback implications.

Use an `evidence` visual when the reader needs proof for a conclusion.

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
- Scrolling changes the sticky visual panel.
- BEFORE and AFTER statements describe observable behavior.
- Deployment requirements are explicit.
- Rollback safety is explicit.
- Important claims include evidence.
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
