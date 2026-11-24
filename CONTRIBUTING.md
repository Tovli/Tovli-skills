# Contributing

Thank you for helping improve Tovli Skills. Contributions can add a skill, improve an existing skill, or fix its supporting scripts, references, examples, and documentation.

## Add a skill

- Put each skill in a clearly named directory at the repository root.
- Include a `SKILL.md` with valid front matter containing a unique public skill name and a concise description of when to use it. The skill name is its invocation identifier and may differ from the directory name.
- Keep skill-specific scripts, references, and examples inside that skill's directory unless they are intentionally shared.
- Add a short README when setup or use needs explanation beyond `SKILL.md`.
- Document required software, network access, credentials, and other external services. Avoid requiring secrets in examples.
- Update the root README catalog when you add or rename a skill.

## Prepare a change

1. Keep each pull request focused on a skill or a closely related set of changes.
2. Explain the user need, affected skill directory, and expected behavior.
3. Update instructions and examples when behavior or requirements change.
4. Review examples and generated output for private data, credentials, and unsupported claims.
5. Follow any validation steps documented by the affected skill. This repository does not currently define a repository-wide automated check suite.

## Pull requests

Use the pull request template. Include enough context for a reviewer to understand how to invoke the skill and what a successful result looks like. Call out new dependencies or behavior that may vary by agent platform.

## Issues

Use the issue templates for bug reports and skill ideas. For suspected security vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
