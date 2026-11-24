# Tovli Skills

Tovli Skills is a public collection of skills for AI agents. Each skill lives in its own directory and contains its instructions in a `SKILL.md` file, with optional scripts, references, and examples.

Skills target agents that support the `SKILL.md` format. Check your agent's documentation for its skill installation and compatibility rules.

## Skills

| Skill | Description |
| --- | --- |
| [`tovli-explain` (`/tovli-explain`)](git-branch-change-explainer/) | Explains behavior and production impact across a Git branch, then creates a standalone HTML report. |
| [`tovli-post-writer`](tovli-post-writer/) | Drafts, reviews, and polishes credible LinkedIn posts while preserving the author's voice and factual accuracy. |
| [`tovli-agentic-planner`](tovli-agentic-planner/) | Turns an agent idea into a workflow and build plan with contracts, permissions, bounded execution, verification, and evaluation gates. |
| [`tovli-plan`](tovli-plan/) | Creates and maintains project plans with canonical JSON, an interactive HTML viewer, decisions, steps, diagrams, and history. |

This catalog grows as new skills are added. Each skill's directory may include its own README with specific usage instructions.

## Use a skill

1. Choose a skill directory and read its `SKILL.md` and any included README.
2. Install or copy that skill directory using the method supported by your agent.
3. Invoke the skill by its name or follow your agent's instructions for selecting skills.

There is no repository-wide installer. Skills may have different requirements; see their documentation before use.

## Contribute

Contributions that add or improve skills are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository conventions and pull request guidance. Read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## Security

For private vulnerability reports, follow [SECURITY.md](SECURITY.md). Do not post vulnerability details in a public issue.

## License

This repository is available under the [MIT License](LICENSE).
