# ASD-STE100 writing profile for this skill

This profile is an implementation aid for branch-change reports. It is not a replacement for the ASD-STE100 standard.

Target: ASD-STE100 Simplified Technical English, Issue 9, dated 2025-01-15.

## Mandatory style controls

1. Use short, direct sentences.
2. Put one topic in each sentence.
3. Prefer active voice in descriptive text.
4. Use direct imperative sentences for deployment instructions.
5. Put one instruction in each procedural sentence, except when actions occur at the same time.
6. Use no more than 20 words in a procedural sentence.
7. Use no more than 25 words in a descriptive sentence.
8. Use no more than six sentences in one paragraph.
9. Put an important condition before the action when the reader must know the condition first.
10. Use the same term for the same technical concept.
11. Do not use a synonym only to make the text sound different.
12. Avoid ambiguous pronouns when a noun gives clearer meaning.
13. Avoid idioms, figurative language, marketing language, and rhetorical questions.
14. Avoid unnecessary `-ing` verb constructions.
15. Use American English spelling unless a technical identifier has a fixed spelling.

## Technical vocabulary

Source code creates many terms that are not general STE words.

Treat these items as technical nouns or technical verbs when necessary:

- class names
- method names
- API names
- endpoint paths
- event names
- queue names
- database objects
- configuration keys
- environment variable names
- product-specific actions

Keep the exact identifier in code formatting when precision is necessary.

Do not replace an identifier with a synonym.

## Preferred report language

Prefer concrete statements.

Use:

- `Before this change, the API returned HTTP 404 for an unknown invoice.`
- `After this change, the API returns an empty result.`
- `Deploy the database migration before the API.`
- `Rollback is unsafe after the backfill changes existing rows.`

Avoid:

- `The branch significantly enhances invoice handling.`
- `The new flow gracefully deals with missing invoices.`
- `This change should probably be safe.`
- `The implementation modernizes the architecture.`

## Evidence language

Use explicit confidence terms:

- `Evidence: direct.`
- `Evidence: corroborated.`
- `Evidence: inferred.`
- `Evidence: unknown.`

When a claim is inferred, identify the missing proof.

## STE verification status

When an official checker or controlled dictionary was used, use this statement:

`STE status: Writing rules and controlled vocabulary were verified with the supplied verification workflow.`

When no formal verification was available, use this statement:

`STE status: Writing rules applied. Controlled vocabulary not formally verified.`

Do not use the phrase `ASD-STE100 compliant` unless the user's authorized verification process supports that claim.
