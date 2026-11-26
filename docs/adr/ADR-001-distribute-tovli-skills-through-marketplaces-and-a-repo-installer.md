# ADR-001: Distribute Tovli Skills through marketplaces and a repo installer

- **Status** Accepted
- **Date** 2026-11-24

## Context

The repository publishes four skills and leaves directory placement and setup to each user. Users need two ways to get the skills in Codex CLI and Claude Code. They can browse and install native plugins, or give their agent the repository URL and ask it to install a named skill or the full collection. Both routes need to ship the same skill instructions and supporting files.

## Decision

Publish separately addable marketplaces for both clients. The catalog has since expanded to four groups.

| Marketplace | Skills |
| --- | --- |
| `tovli-planning` | `tovli-plan`, `tovli-agentic-planner`, `tovli-adr` |
| `tovli-explainer` | `tovli-explain` |
| `tovli-writer` | `tovli-post-writer` |
| `tovli-career` | `tovli-interview-prep`, `tovli-cv-optimize` |

Use the same mapping from public skill names to source directories for packaging and for a small cross-platform installer run from a checkout. The standalone installer supports named skills and the full collection. When the request omits scope, the agent asks the user to choose project or user installation before writing. A noninteractive installer run with no scope exits without writing.

Both routes are required at launch on Codex CLI and Claude Code. Document each desktop route after verifying it.

## Consequences

The marketplaces let users select a workflow and update its package independently. A single bundle would simplify registration and release checks, while one plugin per skill would give users finer control. The selected split requires maintaining and testing each catalog identity on both clients.

The installer makes scope, skill selection, and file placement repeatable across clients. A guide-only copy flow requires less code. A GitHub CLI-only flow adds a compatible GitHub CLI prerequisite. The dedicated installer adds a runtime and lifecycle behavior to maintain, including same-version retries and preservation of divergent local copies.

## Validation

Use one Git branch per marketplace in the source repository. In disposable Ubuntu profiles, Codex CLI 0.171.0 and Claude Code 2.1.322 registered all three branches from one Git source, discovered the expected skills, refreshed the catalogs, and removed a marketplace independently. Both Python renderers ran from the installed packages. The later career marketplace has automated distribution coverage and still requires clean-client verification before release. The GitHub release still requires a fresh verification from the public branch URLs.

## Links

- [PLAN-001, decisions D-001, D-002, D-003, and D-101](../../planning/PLAN-001-install-tovli-skills-in-codex-and-claude.json)
- [Installer and marketplace release guide](../../INSTALL.md)
- [Codex plugin packaging and marketplace registration](https://developers.openai.com/plugins/build/plugins)
- [Claude Code marketplace hosting](https://code.claude.com/docs/en/plugins/host-marketplace)
