# Branch analysis checklist

Use this checklist to prevent a diff-only explanation.

## Repository context

- [ ] Read repository instructions.
- [ ] Identify service boundaries.
- [ ] Identify deployment topology.
- [ ] Identify persistent data stores.
- [ ] Identify queues, streams, topics, and scheduled jobs.
- [ ] Identify public and internal APIs.

## Git range

- [ ] Identify the target branch.
- [ ] Identify the base ref.
- [ ] Calculate the merge base.
- [ ] Record commits in the range.
- [ ] Record renamed, added, modified, and deleted files.
- [ ] Include staged and unstaged tracked changes in the effective AFTER state.
- [ ] Include untracked non-ignored files in the effective AFTER state.
- [ ] Record ignored files separately when they could affect interpretation.
- [ ] Identify committed, staged, unstaged, and untracked evidence.

## Behavior

- [ ] Trace changed entry points.
- [ ] Trace important callers.
- [ ] Trace important consumers.
- [ ] Read the previous implementation.
- [ ] Read the current filesystem implementation, including uncommitted files.
- [ ] Compare validation behavior.
- [ ] Compare error behavior.
- [ ] Compare state changes.
- [ ] Compare external side effects.
- [ ] Compare observability.

## Contracts

- [ ] API schemas.
- [ ] Message schemas.
- [ ] Database schemas.
- [ ] Serialized models.
- [ ] Configuration contracts.
- [ ] Authentication and authorization.

## Presentation

- [ ] State explicitly when the selected comparison has no changes, after checking committed and included local changes.
- [ ] Record overall, business, and technical change status; distinguish unchanged from unknown impact.
- [ ] Show an explicit no-change statement for each unchanged view without fabricating change scenes.
- [ ] Classify business outcomes separately from technical contracts and components.
- [ ] Present business and technical content in mutually exclusive views.
- [ ] Describe business rules and outcomes in domain language.
- [ ] Draw activity diagrams for changed flows, decisions, and outcomes.
- [ ] Show matched BEFORE and AFTER diagrams for each changed flow and component relationship.
- [ ] Explain the previous outcome and current outcome under the same conditions for every material change.
- [ ] Label absent capabilities and unknown baselines explicitly instead of inventing previous behavior.
- [ ] Compare contract definitions and compatibility before and after the change.
- [ ] Diagram changed component responsibilities, dependencies, and boundaries.
- [ ] Keep source paths and implementation evidence in the technical view.
- [ ] Give each unknown a business or technical category.

## Deployment

- [ ] Migration order.
- [ ] Multi-service rollout order.
- [ ] Mixed-version compatibility.
- [ ] Environment variables.
- [ ] Secrets.
- [ ] Feature flags.
- [ ] Infrastructure resources.
- [ ] Permissions.
- [ ] Resource usage.
- [ ] External dependency load.
- [ ] Health checks.
- [ ] Metrics and alerts.

## Rollback

- [ ] Old code can read new data.
- [ ] Old code can read new messages.
- [ ] New schema supports old binaries.
- [ ] Data migrations are reversible or non-destructive.
- [ ] Feature flags can isolate the change.
- [ ] Rollback sequence is documented.

## Evidence

- [ ] Each major conclusion has evidence.
- [ ] Tests are linked to the behavior that they prove.
- [ ] Inferences are labeled.
- [ ] Unknowns are visible.
