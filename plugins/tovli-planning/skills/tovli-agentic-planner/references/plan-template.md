# Agentic workflow plan output contract

Use this structure as a starting point, adapting names, depth, and ordering to the user's requested format. Combine sections for simple tasks. Include a flow diagram when it clarifies branching or dependencies; do not force a diagram for a one-step response. The result must contain decisions and implementable behavior, not an unfilled questionnaire.

Distinguish user requirements, observed facts, proposed decisions, assumptions, and open questions. State unknowns explicitly. Proposed budgets and evaluation targets are starting points to validate, not measured capabilities or granted permissions.

## 1. Outcome and scope

- Primary user, trigger, current difficulty, and intended outcome.
- One concrete input-to-result journey, including what proves completion.
- In scope, out of scope, constraints, and why an agent adds value.
- Measurable acceptance criteria and worst credible consequences.
- Known environment/integrations, proposed additions, and material assumptions.

## 2. Architecture decision

| Candidate | Fit for this task | Trade-off / evidence required |
| --- | --- | --- |
| Simpler baseline | Describe the next simpler viable design | Explain any unmet need |
| Selected design | Components and execution strategy | Benefit and how to measure it |

Name the routing/orchestration owner, execution owner, and verification mechanism. These can share a component when justified. Explain deterministic versus adaptive steps and any use of parallel work, reflection, or multiple agents.

For a reusable product, distinguish shared infrastructure from domain-specific configuration. Do not design a general platform unless the request calls for one.

## 3. User journey and workflow

Describe the interface and what the user sees at meaningful transitions. Identify where the user can inspect, edit, approve, reject, correct, pause, cancel, resume, or recover as applicable. Explain the final result and partial-result experience.

Use a Mermaid diagram for nontrivial flows. Label approval, verification, failure, partial completion, and bounded retry/replan branches where applicable; diagrams must agree with the step table. Represent the actual product flow rather than a decorative generic agent loop.

| Step / owner | Input and preconditions | Operation / output | Success evidence | Next transition on success, failure, or missing authority |
| --- | --- | --- | --- | --- |

Include dependencies and resource ownership for parallel steps. Verification failure must lead to a bounded correction, partial result, or escalation rather than an unconditional success response.

### Adaptive loop specification, when used

Describe how Reason -> Act -> Observe -> Evaluate selects the smallest useful next step. Provide a state transition table or pseudocode if it makes implementation clearer. Include:

- Objective, permitted actions, and evidence-based completion condition.
- Finite iteration/tool-call count, elapsed time, token or monetary caps, retry and replan caps, and reflection limits if used.
- Scope of each limit (per call, step, workflow, or period), enforcement owner, and remaining-budget accounting across delegates.
- What constitutes progress; repeated-call/no-progress detection and thresholds.
- Events that trigger replanning, human input, escalation, partial completion, or failure.
- Checkpoints and restart/resume semantics where necessary.

For an impossible task, an exceeded cap, or insufficient authority, specify a truthful terminal or waiting state. Waiting for a user must not continue consuming autonomous execution budget indefinitely.

## 4. Agent and component contracts

For each actual agent, provide:

| Contract field | Required decision |
| --- | --- |
| Identity and responsibility | Bounded role, accepted tasks, refused or redirected tasks |
| Input | Required and optional fields, types, provenance, preconditions |
| Capabilities | Tool/data scopes, allowed operations, explicit delegation permissions |
| Output | Structured fields/types, artifact references, evidence, useful uncertainty indicators |
| Completion | Measurable criteria and downstream verifier |
| Limits | Time, cost/tokens, tool calls, retries, and escalation |
| Failure behavior | Refusal, incomplete output, invalid output, escalation, and recovery |

Define validation rules, not just a list of field names. Do not invent precise numerical confidence scores without calibration. Specify deterministic component interfaces separately.

For multiple agents, add the handoff payload and schema: objective, relevant context, constraints, expected output, allowed permissions, deadline/budget, completion criteria, and parent workflow identifier. Name who aggregates results, resolves disagreements, and owns the final result. Prevent concurrent edits to a shared resource unless a coordination mechanism is defined.

## 5. Tools, autonomy, and permissions

| Action / tool | Read / prepare / write | Autonomy 0-5 | Required scope / existing authority | Approval trigger and exact scope | Enforcement owner |
| --- | --- | --- | --- | --- | --- |

Choose autonomy per action, based on impact, reversibility, cost, privacy, and authorization. Define approval validity, expiration or revocation where relevant, and what changed payloads require new approval. A proposed approval gate does not mean approval already exists.

For each tool, define purpose, input/output schema and validation, preconditions, side effects, timeout, error classifications, and retry safety. Describe restricted wrappers around broad APIs if needed. Name the application/service enforcing access and budgets outside the model.

For consequential actions, specify idempotency keys, precondition checks, receipts, status reconciliation after uncertain responses, safe retry conditions, and rollback/compensation or human recovery. If the external system cannot deduplicate or reconcile, define a safe stop and escalation path.

## 6. Context, memory, state, and security

Identify trusted instructions, external/untrusted data, retrieval provenance, freshness rules, minimum sufficient context, tenant isolation, and secret handling. External instructions cannot change tool permissions or approval policy.

| Memory type used | Purpose / stored fields | Access | Retention | Update, correction, deletion | Stale/conflicting information |
| --- | --- | --- | --- | --- | --- |

Explicitly omit memory types with no demonstrated purpose. Describe any required domain policy review without presenting assumptions as legal conclusions.

For durable workflows, specify a state schema with objective, status, completed/pending steps, observations, artifact references, approval scope, tool operation IDs/receipts, budget usage, errors, and checkpoints. Include a transition table and recovery owner.

Select applicable statuses: created, queued, running, waiting for tool/user/approval, paused, completed, partially completed, failed, cancelled. Explain transition guards, resumption after process/session loss, and reconciliation of in-flight operations. Revalidate stale inputs and expired/revoked authority before resuming consequential work. Do not restart completed writes blindly.

Define audit events for request, routing, authorized actions, tool outcomes, approvals, external effects, verification evidence, errors, and interventions. State access and retention limits; exclude secrets and private reasoning.

## 7. Failure and recovery

| Failure / observation | Detection | Bounded response / retry safety | Preserved progress | User message / escalation |
| --- | --- | --- | --- | --- |

Cover applicable cases: invalid/missing inputs, timeout, outage/rate limit, denied permission, contradictory findings, malformed agent output, repetitive execution, ambiguous write success, failed verification, interruption, cancellation during an in-flight operation, and exhausted budgets. Mark genuinely irrelevant cases briefly rather than inventing unnecessary infrastructure.

## 8. Verification and evaluation

| User acceptance criterion | Observable evidence / authoritative source | Verifier | Proposed pass threshold | Failure response |
| --- | --- | --- | --- | --- |

Prefer external state, schema checks, calculations, artifact inspection, tests, or appropriate human review. A confident executor response alone cannot verify completion. Name any remaining reliance on human judgment and its consequences.

Define a stable representative task set and simpler baseline. Include normal, edge, adversarial, and fault-injection cases proportionate to risk. Test permissions and approval bypass, untrusted instructions, partial completion, resumption, and duplicate-action prevention when applicable.

Measure complete tasks: success rate, verified completion, time to useful result, end-to-end latency, cost per verified outcome, tool failures, intervention/correction, recovery, and user satisfaction as useful. Define denominators and measurement sources for release-critical metrics.

For adaptive loops, measure average/maximum iterations, productive iterations, redundant/incorrect tool calls, premature completion, failure to stop, response to misleading/conflicting observations, unavailable tools, revised approaches, and impossible requests.

Label targets as proposed until measured. State release gates, regression comparison against the baseline, and what evidence would remove an unnecessary loop, agent, or memory layer.

## 9. Phased implementation

| Phase | Deliverable / owner role | Dependencies | Acceptance evidence | Go/no-go decision |
| --- | --- | --- | --- | --- |

Start with a thin end-to-end baseline. Add only necessary tools, adaptive execution, state/recovery, or specialization. Describe concrete interfaces, schemas, modules, and integration work at the detail supported by the environment; do not fabricate repository paths or team assignments.

Include evaluation and enforcement before enabling consequential autonomous writes. Separate MVP from deferred work and identify each deferred feature's evidence trigger. Record build blockers versus release blockers.

## 10. Mandatory design review and open decisions

Complete the 16-area matrix from guideline 35 with a concise answer and a pointer to the relevant plan section. A justified "not needed" is a decision; an unanswered heading is not.

For material open questions, give the assumption used, consequence if wrong, owner role/resolution step, and whether the question blocks design, implementation, or release. End with the next concrete build step, without implying permission to execute the proposed agent.
