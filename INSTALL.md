# Install Tovli Skills

Codex CLI and Claude Code support both a native marketplace route and a standalone installer. Install through a marketplace to get its group of skills. Use the standalone installer for one skill, a selection, or the full collection.

## Native marketplaces

Each marketplace has one plugin with the same name. The commands below install Planning. Substitute `tovli-explainer`, `tovli-writer`, or `tovli-career` for every occurrence of `tovli-planning` to choose another group.

| Marketplace name | Skills | Claude Code plugin commands |
| --- | --- | --- |
| `tovli-planning` | `tovli-plan`, `tovli-agentic-planner`, `tovli-adr` | `/tovli-planning:tovli-plan`, `/tovli-planning:tovli-agentic-planner`, `/tovli-planning:tovli-adr` |
| `tovli-explainer` | `tovli-explain` | `/tovli-explainer:tovli-explain` |
| `tovli-writer` | `tovli-post-writer` | `/tovli-writer:tovli-post-writer` |
| `tovli-career` | `tovli-interview-prep`, `tovli-cv-optimize` | `/tovli-career:tovli-interview-prep`, `/tovli-career:tovli-cv-optimize` |

### Codex CLI

```sh
codex plugin marketplace add Tovli/Tovli-skills --ref marketplace/tovli-planning
codex plugin add tovli-planning@tovli-planning
```

Start a fresh session and use the skill picker or mention the plugin's namespaced skill, for example `$tovli-planning:tovli-plan`. Check your installation with `codex plugin list`.

To update and reinstall the package at the catalog's newer version, run these commands.

```sh
codex plugin marketplace upgrade tovli-planning
codex plugin add tovli-planning@tovli-planning
```

To remove the plugin, use `codex plugin remove tovli-planning@tovli-planning`. To also remove its catalog, use `codex plugin marketplace remove tovli-planning`.

### Claude Code

```sh
claude plugin marketplace add 'Tovli/Tovli-skills#marketplace/tovli-planning'
claude plugin install tovli-planning@tovli-planning
```

Start a fresh session and invoke the namespaced command from the table. Check your installation with `claude plugin list`.

To update the plugin, run these commands.

```sh
claude plugin marketplace update tovli-planning
claude plugin update tovli-planning@tovli-planning
```

To remove the plugin, use `claude plugin uninstall tovli-planning@tovli-planning`. To also remove its catalog, use `claude plugin marketplace remove tovli-planning`.

The same-repository layout was verified with Codex CLI 0.171.0 and Claude Code 2.1.322. These versions are tested baselines. [Codex marketplace reference](https://developers.openai.com/plugins/build/plugins) · [Claude Code marketplace reference](https://code.claude.com/docs/en/plugins/host-marketplace)

## Standalone installer

Requires Git and Python 3.10 or later. Use `python3` wherever your system uses that name for Python. A checkout is needed to run the installer. Installed skills carry their own resources and can run after you remove the checkout.

1. Identify the target client and the named skills or collection. If your user did not specify scope, ask whether to install for the current project or for their user account, then wait for the answer.
2. Clone `https://github.com/Tovli/Tovli-skills` to a directory separate from the target project, or reuse a checkout you already have. Use an available release tag or commit with `--ref` to select a reproducible source. The default is the checkout's committed `HEAD`.
3. Run the installer from that checkout. For project scope, pass the actual project directory as `--project-dir`. For user scope, omit that argument.
4. Report the selected Git revision, paths and invocation. Start a fresh client session in the target project to discover the skills.

For example, install just the planning skill in a Codex project, or install the whole collection for the current Claude Code user.

```sh
python scripts/tovli_skills.py install --client codex --scope project --project-dir "/path/to/project" tovli-plan
python scripts/tovli_skills.py install --client claude --scope user --all
```

| Client | Project scope | User scope | Standalone invocation example |
| --- | --- | --- | --- |
| Codex CLI | `.agents/skills/` in the chosen project | `~/.agents/skills/` | `$tovli-plan` |
| Claude Code | `.claude/skills/` in the chosen project | `~/.claude/skills/` | `/tovli-plan` |

Run the same install command with a newer local ref to update an unmodified installer-managed copy, or with an earlier ref to restore named skills. For a full-collection rollback, check out the earlier release and run its own installer with --all so its catalog matches that release. An identical install succeeds without copying. The installer reports conflicts for divergent files and preserves them. A matching manually installed copy stays under manual ownership.

Use `uninstall` with the same client, scope, and skill selection to remove installer-managed copies. It preserves unmanaged copies and stops if a selected installed skill has local edits.

```sh
python scripts/tovli_skills.py uninstall --client codex --scope project --project-dir "/path/to/project" tovli-plan
```

The planning and branch-report skills require Python when you run their renderers. The planning skill can use `jsonschema` for full schema and format validation. See each skill's documentation for workflow requirements.

`tovli-adr` can create Markdown ADRs locally. Indexing and graph registration use a Ruflo or Claude Flow MCP connection or CLI configured for the target project. See the [Ruflo integration guide](tovli-adr/references/ruflo.md).

## Prepare a marketplace release

Build all catalog branches from one committed source. Run the tests and use a fresh output directory for each build. When updating published catalogs, `--base` fetches their existing parent commits so the new branches can fast-forward. Choose a version above the previous release when the generated contents change.

```sh
python -B -m unittest discover -s tests -v
python scripts/tovli_skills.py build-marketplaces --ref HEAD --version 0.1.0 --output .tovli-build/0.1.0 --git --base https://github.com/Tovli/Tovli-skills.git
```

Each output directory contains both catalog formats, a self-contained plugin, and `SOURCE.json` with the source commit and version. The optional `--git` flag also builds `marketplaces.git` with a branch for each marketplace. The build makes no remote changes.

In clean client profiles, add each local catalog directory first and verify installation, exact skill membership, and invocation. Then verify all refs using a Git fixture before publishing. Rebuild from the same commit and compare the catalog directories to check for generated file drift. To publish the prepared branches together after validation, push them from the generated repository.

```sh
git --git-dir=.tovli-build/0.1.0/marketplaces.git push --atomic https://github.com/Tovli/Tovli-skills.git marketplace/tovli-planning marketplace/tovli-explainer marketplace/tovli-writer marketplace/tovli-career
```

Publish the source commit or tag to the same repository for the standalone route. Verify fresh installs using the public commands. Keep the last known-good source release for standalone rollback. For a marketplace rollback, rebuild the prior source at a new version so clients pick up the restored package on refresh.
