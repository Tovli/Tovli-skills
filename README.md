# Tovli Skills

Tovli Skills is a public collection of skills for AI agents. Each skill lives in its own directory and contains its instructions in a `SKILL.md` file, with optional scripts, references, and examples.

Install skills in Codex CLI or Claude Code through a native marketplace or by asking your agent to install from this repository.

## Skills

| Skill | Description |
| --- | --- |
| [`tovli-explain` (`/tovli-explain`)](git-branch-change-explainer/) | Explains behavior and production impact across a Git branch, then creates a standalone HTML report. |
| [`tovli-post-writer`](tovli-post-writer/) | Drafts, reviews, and polishes credible LinkedIn posts while preserving the author's voice and factual accuracy. |
| [`tovli-agentic-planner`](tovli-agentic-planner/) | Turns an agent idea into a workflow and build plan with contracts, permissions, bounded execution, verification, and evaluation gates. |
| [`tovli-plan`](tovli-plan/) | Creates and maintains project plans with canonical JSON, an interactive HTML viewer, decisions, steps, diagrams, and history. |

This catalog grows as new skills are added. Each skill's directory may include its own README with specific usage instructions.

## Install from a marketplace

| Marketplace | Skills |
| --- | --- |
| `tovli-planning` | `tovli-plan`, `tovli-agentic-planner` |
| `tovli-explainer` | `tovli-explain` |
| `tovli-writer` | `tovli-post-writer` |

See the [marketplace commands](INSTALL.md#native-marketplaces) for both clients and how to update or remove a plugin. Each command uses its own published Git branch.

## Ask your agent to install

> Install Tovli Skills from https://github.com/Tovli/Tovli-skills for this project. Follow INSTALL.md and tell me how to invoke the installed skills.

To install a single skill, name it in the request. If you leave out the scope, the agent asks whether to install for the project or for your user account. [Read the installer guide](INSTALL.md#standalone-installer) to run it from your terminal.

## Contribute

Contributions that add or improve skills are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions and pull request guidance. Read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## Security

For private vulnerability reports, follow [SECURITY.md](SECURITY.md). Do not post vulnerability details in a public issue.

## License

This repository is available under the [MIT License](LICENSE).
