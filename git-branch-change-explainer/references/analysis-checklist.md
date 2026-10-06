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
- [ ] Record uncommitted work separately.

## Behavior

- [ ] Trace changed entry points.
- [ ] Trace important callers.
- [ ] Trace important consumers.
- [ ] Read the previous implementation.
- [ ] Read the new implementation.
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
