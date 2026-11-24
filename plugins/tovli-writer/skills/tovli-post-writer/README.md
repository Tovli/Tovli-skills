# Tovli Post Writer

A public, reusable skill for drafting, reviewing, and improving credible professional LinkedIn posts.

## What it does

- Turns rough notes, lessons, technical ideas, announcements, and experiences into publishable posts.
- Reviews drafts for clarity, credibility, structure, evidence, and professional value.
- Supports quick polish, detailed review, and final-copy-only workflows.
- Handles technical, leadership, product, career, and general professional topics.
- Avoids clickbait, engagement bait, invented stories, fake metrics, and unsupported certainty.
- Can recommend an appropriate visual, CTA, hashtags, and one measurable experiment when useful.

## Suggested prompts

Invoke as `$tovli-post-writer`, followed by your request and source material. For example:

- `Turn these notes into a LinkedIn post: ...`
- `Review this post and be critical: ...`
- `Polish this draft but keep my voice: ...`
- `Give me final copy only: ...`
- `Make this technical post understandable to engineering leaders without oversimplifying it: ...`
- `Create three substantially different openings for this draft: ...`
- `Shorten this by 30% without losing the argument or evidence: ...`

## Design goals

The skill optimizes for credibility, relevant reach, substantive discussion, professional authority, and qualified professional outcomes rather than generic virality.

It treats factual integrity as a hard constraint: it must not invent personal experience, customers, projects, results, metrics, research, or quotations.

## Files

- `SKILL.md` — the installable skill instructions.
- `README.md` — overview and example usage.
- `agents/openai.yaml` — Codex display metadata and a suggested starting prompt.

## Setup and privacy

Copy this directory into the skills location supported by your agent. Drafting from supplied material requires no scripts, credentials, LinkedIn account connection, or external services. Verifying current external claims may require browsing.

The bundled instructions and examples contain only generic writing guidance. Keep private source material and personal voice samples outside this public skill directory. The skill directs the agent to omit or generalize sensitive details unless their disclosure is established, and does not authorize publishing or scheduling posts.
