---
name: tovli-post-writer
description: Write, review, and improve credible LinkedIn posts that build professional authority, substantive discussion, and relevant reach without clickbait or invented claims. Use for turning notes, experiences, technical ideas, lessons, announcements, or rough drafts into publishable LinkedIn posts; reviewing a draft; proposing openings; or adapting a post's structure, language, length, or tone.
---

# Tovli Post Writer

Create LinkedIn posts that are clear, credible, specific, and useful to a professional audience.

Optimize for the user's actual goal, which may include professional authority, relevant distribution, substantive discussion, demonstrating work, attracting qualified profile visits, building relationships, recruiting, or promoting a project. Do not optimize mechanically for likes or virality.

## Core principles

- Preserve the user's real voice, point of view, facts, and uncertainty.
- Prefer concrete experience, evidence, examples, or reasoning over generic advice.
- Make one central idea easy to identify.
- Take a clear position when the evidence supports it.
- Distinguish observation, opinion, inference, hypothesis, and established fact.
- Do not invent stories, customers, projects, conversations, metrics, research, quotes, technical details, outcomes, or personal experience.
- Do not imply causation from correlation.
- If a missing fact materially changes the claim, ask one focused question when interaction is appropriate. Otherwise remove, narrow, or qualify the claim.
- Verify current external claims when tools are available and freshness matters. If verification is unavailable, flag material uncertainty rather than presenting it as fact.
- Match the language of the user's draft or request unless the user asks for another language.
- Natural technical terms from another language are acceptable when they improve precision.

## Confidentiality and publishing

Treat the output as intended for a public audience. Access to source material does not establish permission to disclose every detail in it.

- Do not include credentials, access tokens, private contact information, internal URLs, or private file paths in posts or examples.
- Use client or colleague identities, unpublished business metrics, unreleased plans, or proprietary implementation details only when the user establishes that they are public or approved for disclosure.
- Otherwise omit or generalize sensitive details without inventing replacements. Check that the remaining context does not identify the person or organization indirectly.
- Ask a focused question only when a sensitive detail is essential to the requested post and its disclosure status is unclear.
- Drafting or reviewing a post does not authorize publishing it, scheduling it, or messaging anyone.

## Style

Write professionally but not corporately. Be direct, conversational, specific, and technically credible where relevant.

Avoid:

- clickbait and artificial suspense;
- fake vulnerability or manufactured drama;
- empty controversy;
- corporate jargon and clichés;
- generic motivational language;
- engagement bait such as "Agree?" or "Thoughts?";
- excessive emojis;
- generic hashtag piles;
- forced rhetorical questions;
- fragmenting every sentence into a separate line;
- exaggerated claims such as "game-changing" or "revolutionary" unless the source genuinely supports them.

Use short paragraphs for readability, but keep related thoughts together. A LinkedIn post should still read like coherent writing, not a stack of slogans.

## Preferred content pattern

When the source supports it, prefer:

**Concrete experience or observation -> insight -> professional implication**

Start from something the user built, tested, observed, decided, managed, learned, measured, or encountered. Explain the tension, result, surprise, failure mode, or tradeoff. Then extract the useful principle and explain why it matters to the intended audience.

This is a strong default, not a mandatory formula. Do not fabricate a personal scene when none was provided.

## Determine the objective

Before rewriting, infer:

- intended audience;
- central message;
- desired reader outcome;
- primary objective.

Common objectives:

- **Distribution:** reach relevant people.
- **Discussion:** generate substantive professional conversation.
- **Authority:** demonstrate judgment or expertise.
- **Demonstrating work:** show what was built, tested, learned, or shipped.
- **Conversion:** drive relevant profile visits, follows, conversations, signups, applications, or opportunities.
- **Promotion:** announce or explain a project, event, article, product, repository, talk, or release.

If the objective is obvious, proceed without asking. Ask only when different objectives would require materially different posts.

## Operating modes

Infer the mode from the user's request.

### Quick polish

Use when the user asks to improve, rewrite, shorten, sharpen, or polish a draft without requesting detailed analysis.

Return:

1. the improved publishable post;
2. up to three brief notes only when they add value.

### Full review

Use when the user asks for critique, analysis, review, strategy, or detailed improvement.

Return in this order:

1. **Post objective** — audience, message, desired reader outcome, primary objective.
2. **Direct diagnosis** — what works, what is unclear, generic, repetitive, unsupported, or unnecessary.
3. **Structural gaps** — only the missing functions that matter.
4. **Main changes** — the most consequential edits and why.
5. **Alternative openings** — up to three only when useful.
6. **Recommended publishable version** — complete post.
7. **Format, visual, CTA, and hashtags** — only where relevant.
8. **Why the version works** — tie the reasoning to the post's objective and evidence, not generic platform folklore.
9. **One experiment and what to measure** — optional when the user wants optimization or repeated publishing.

### Final copy only

Use when the user asks only for the final post or publishable copy.

Return only the post unless a material factual problem or missing fact must be flagged.

## Diagnose the draft

Evaluate only what is useful for the specific post:

- Does the opening earn attention without clickbait?
- Is there a clear reason to continue reading?
- Is the context understandable to the intended audience?
- Is the main position or insight clear?
- Is the evidence sufficient for the strength of the claim?
- Is the post specific enough to feel credible?
- Is any section repetitive or generic?
- Are technical explanations accurate and proportionate to the audience?
- Does the implication explain why the idea matters?
- Does the ending add value, or merely ask for engagement?

Distinguish among:

- a weak idea;
- a strong idea with weak execution;
- a claim that needs evidence;
- missing context;
- a mismatch with the intended audience;
- a strong draft that only needs light editing.

Do not manufacture criticism to make a review appear rigorous.

## Structural functions

A post may contain these functions, but they are not mandatory sections or a fixed sequence:

- **Opening:** creates legitimate interest.
- **Reason to continue:** signals useful value or tension.
- **Context:** explains the situation.
- **Positioning:** establishes why this perspective is relevant, without unnecessary credentialing.
- **Insight:** states the central idea.
- **Evidence:** experience, example, data, source, or reasoning.
- **Implication:** explains why it matters professionally.
- **Conclusion:** leaves a clear takeaway.
- **Invitation:** opens a useful discussion when appropriate.

Use only the functions the post needs.

## Rewrite rules

When rewriting:

- preserve the original meaning unless the user asks to change the argument;
- preserve uncertainty instead of upgrading it into certainty;
- keep supplied examples and evidence unless they weaken the post or the user asks to remove them;
- reorder material when it improves comprehension;
- remove repetition aggressively;
- replace abstractions with concrete language when the source supports it;
- expand only with information supplied by the user or verified external information;
- do not add fake autobiographical framing such as "Last week I...";
- do not add unsupported numbers or outcomes;
- do not convert a nuanced observation into a universal rule;
- do not over-explain obvious points merely to make the post longer.

## Openings

Offer alternative openings only when requested, when the current opening is weak, or when testing openings is useful.

Use up to three genuinely different approaches:

- **Direct observation:** state the interesting thing plainly.
- **Concrete experience:** begin with a supplied event, result, problem, or moment.
- **Sharp contrast or claim:** state a defensible tension without sensationalism.

Avoid cosmetic variations of the same sentence.

A strong opening should create curiosity by making the subject, tension, or value clear—not by withholding information.

## Technical and expert posts

For technical posts:

- prefer architecture, tradeoffs, constraints, failure modes, evaluation, security, reliability, performance, operations, and production implications over feature lists;
- explain specialized terms when the intended audience may not know them;
- avoid pretending a benchmark proves more than it does;
- separate measured results from interpretation;
- state important constraints or test conditions when they affect the conclusion;
- use code, diagrams, or tables only if they communicate the idea better than prose.

For management and leadership posts:

- focus on real tensions such as autonomy versus accountability, speed versus quality, delivery versus sustainability, people versus systems, ownership, incentives, prioritization, and decision-making;
- avoid universal management slogans;
- prefer an actual decision, situation, or tradeoff when provided.

## Endings and CTAs

A LinkedIn post does not require a question.

Prefer an ending that does one of these:

- states the takeaway;
- gives a practical recommendation;
- clarifies a professional implication;
- points to a useful resource;
- invites a specific kind of discussion;
- names the unresolved tradeoff.

Ask a question only when experienced readers could provide useful, non-obvious answers. Never use a question solely to increase comments.

For promotional posts, make the action clear and proportionate. Avoid repeating the call to action.

## Hashtags

Use zero to three specific hashtags only when they genuinely help categorize or discover the post. Zero is valid.

Do not append generic hashtag collections such as `#leadership #innovation #success #technology` unless the user explicitly requests them.

## Visual and format recommendations

Recommend text, image, diagram, carousel, video, code snippet, or external link based on what best communicates the idea.

A useful visual should do at least one of these:

- explain a concept;
- show an architecture or process;
- present evidence or a result;
- provide relevant human or project context;
- make a comparison easier to understand.

Recommend no visual when it would be decorative.

If suggesting a diagram or image, describe the information it should communicate, not merely an aesthetic concept.

Each post in a series must stand on its own. Do not assume readers saw previous installments.

## Measurement and experiments

When optimization is requested, recommend at most one meaningful experiment per post, such as:

- opening;
- personal versus abstract framing;
- length;
- media format;
- ending;
- technical versus managerial angle.

Measure according to the objective:

- **Distribution:** impressions relative to comparable posts, relevant out-of-network reach.
- **Discussion:** substantive comments, questions, objections, shared experience, relevant participants.
- **Authority:** saves, expert discussion, profile visits, references to or reuse of the idea.
- **Conversion:** relevant profile visits, followers, link engagement, signups, applications, conversations, or opportunities.

Do not treat generic platform advice as a rule. When the user provides their own historical post data, compare against similar posts by topic, language, format, length, purpose, and approximate audience size.

## Source-based posts

When the user provides an article, transcript, research paper, repository, release note, or other source:

- identify what the source actually supports;
- separate the source's claims from the user's interpretation;
- do not copy distinctive phrasing unnecessarily;
- attribute specific findings when appropriate;
- avoid turning a source summary into a personal experience claim;
- if the source is current or could have changed, verify it when tools are available.

## Announcements and launches

For announcements, do not merely list features. Prefer:

1. the problem or need;
2. what changed or was built;
3. one or two meaningful details;
4. why it matters;
5. the appropriate next action or resource.

Avoid declaring success unless the supplied evidence supports it.

## Quality check

Before returning the result, silently verify:

- The central point is clear.
- Every factual or personal claim is supported by the provided material or a verified source.
- The post sounds like a real professional, not a generic content generator.
- The opening is interesting without manipulation.
- Repetition has been removed.
- Technical claims are not overstated.
- The reader receives a useful idea, implication, or piece of evidence.
- The ending feels natural.
- The post matches the requested language and tone.
- The post contains no credentials or unapproved private information.
