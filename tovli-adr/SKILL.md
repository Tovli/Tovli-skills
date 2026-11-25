---
name: tovli-adr
description: Create an Architecture Decision Record (ADR) for a significant technical decision, link relevant project ADRs, and register it through Ruflo or Claude Flow MCP or CLI.
---

# Tovli ADR

Create one Markdown record for a consequential architectural choice, such as an API contract, storage model, infrastructure change, or technology adoption. Treat the repository's ADR as the source of truth and Ruflo as its searchable index and relationship graph.

1. **Find the ADR location and next ID.** Read project guidance, the ADR template and index if present, and neighboring records. Follow the established directory, numbering, and naming convention. Otherwise use `docs/adr/ADR-NNN-<slug>.md`, where `NNN` is one above the highest existing numeric ID, starting at `001`. Build a lowercase, hyphenated slug from the title. Recheck the ID before writing and preserve existing records. If another ADR claims the same ID during creation, renumber the new record before registration.
2. **Check for Ruflo.** Before searching or registering ADRs, choose a backend using the [availability check](references/ruflo.md#check-availability-and-choose-a-backend). Reuse the CLI preflight result from this conversation when it still applies. If neither an MCP connection nor an installed CLI is found, show this user-visible warning once and continue with the local ADR workflow.

   > **Ruflo warning.** Ruflo and Claude Flow are unavailable through MCP and CLI. I’ll create the Markdown ADR locally. Indexing and graph registration are pending.

3. **Gather the decision and related records.** Use the user's request, relevant project materials, and existing ADRs. When a backend is available, search the project's `adr-patterns` namespace by title and context before adding the new entry. Verify matching IDs against the repository and read the actual ADRs before linking them. Search the local ADRs when integration is unavailable.
4. **Write the Markdown.** Use the project template when it exists, or the form below. Default to `proposed` and record `accepted` only when the user or project materials establish acceptance. Describe the problem and constraints, the decision or proposal, the meaningful alternatives, and the consequences. Leave unknown metadata blank. Add relative Markdown links with specific relationship labels. Maintain an existing ADR index if the repository uses one.
5. **Register the saved ADR when a backend is available.** Follow the Ruflo integration for hierarchical storage, edge creation, and semantic indexing. Create a `depends-on` edge when the new decision actually relies on the linked decision. A topical match belongs in Markdown as a related link. If a backend operation fails, keep the ADR and report which operations remain pending. Reuse the saved ADR and ID when completing a pending registration.
6. **Report the outcome.** Give the ADR ID, file path, status, relevant links, and the observed integration outcome.

## Default Markdown

```markdown
# ADR-NNN: <Title>

- **Status**: proposed
- **Date**: <today's date YYYY-MM-DD>
- **Deciders**:
- **Tags**:

## Context

<!-- What is the issue that motivates this decision? -->

## Decision

<!-- What is the change that we are proposing? -->

## Consequences

### Positive
-

### Negative
-

### Neutral
-

## Links
```

Fill in the current local date unless the decision date is supplied. Leave Deciders and Tags blank when unknown. Add verified relationships under Links using bold labels such as `**Depends on**:` and `**Related**:` so the Ruflo ADR importer can read them. Group links of the same type under one label.
