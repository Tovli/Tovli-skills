---
name: tovli-agentic-planner
description: Design an implementation-ready agentic workflow from a user's requested agent or AI feature, including architecture, agent and tool contracts, permissions, bounded execution, state, verification, and a phased build plan. Use when planning a new agent, redesigning an agent workflow, or reviewing an agent design before implementation. Produces a plan; does not build or operate the proposed agent.
---

# Tovli Agentic Planner

Turn a requested agent into a product and engineering plan that a builder can implement and a reviewer can evaluate. Optimize for the user's outcome through the smallest system that can reliably deliver it.

Use the user's Product Design Guidelines for Agentic AI Systems, version 2.0. Their 35 principles and mandatory review questions are preserved as an operational digest in [references/product-design-guidelines.md](references/product-design-guidelines.md). Read the relevant sections when making design decisions, and section 35 before completing a plan.

## Scope and working style

- Plan the requested product, respecting its domain, existing architecture, explicit technology choices, and constraints. Do not replace it with a generic agent platform.
- A planning request authorizes analysis and the plan, not deployment, external writes, tool connections, scheduled jobs, or execution of the proposed workflow. Describe future permissions without claiming they have been granted.
- Inspect relevant supplied artifacts or repository conventions when available. Distinguish observed facts, user requirements, proposed decisions, assumptions, and unresolved questions. Do not invent integrations, credentials, business policies, model capabilities, benchmarks, or compliance status.
- Ask only when a missing answer materially affects the outcome, architecture, or consequential authority. Continue independent planning while awaiting an answer. Record safe defaults as assumptions; mark essential unknowns as build or release blockers rather than blocking the entire plan.
- Match the user's language and requested depth. Keep a simple design compact; give complex workflows enough detail to implement. Framework selection and code are optional unless requested. Verify current external specifications only when the design depends on them.
- Return the plan in the conversation unless a file or another destination is requested. Preserve an existing requested document format.

## Planning workflow

### 1. Establish the outcome

Identify the primary user, trigger, current difficulty, intended result, required information and actions, scope exclusions, and measurable acceptance criteria. Describe at least one concrete journey from request to verified result.

Establish why an agent is necessary. If predictable software or a single model call suffices, recommend that baseline and explain its value. A request for an agent does not require adaptive autonomy or multiple agents.

Identify credible harm, reversibility, monetary exposure, privacy implications, and existing authorization. Classify permissions by action, not by the agent's name. Use the autonomy levels 0-5 from the guidelines; one workflow may use different levels for different actions.

### 2. Choose the architecture and execution pattern

Compare the selected architecture with the next simpler viable alternative where one exists: deterministic logic, single model call, single agent with tools, fixed specialized workflow, router, coordinator, or collaborative agents. If the selection is already the simplest viable baseline, say so. State why extra components are needed and what measurement would justify keeping them. Where the user mandates complexity, preserve that constraint and document the trade-off.

Choose single-pass, deterministic workflow, ReAct, plan-then-execute, plan-and-replan, parallel execution, or a combination based on uncertainty, dependencies, risk, and expected performance. Do not prescribe ReAct for predictable work.

Separate routing and orchestration from individual execution. Separate planning, execution, and verification responsibilities even when one component handles several. Use deterministic orchestration and verification where practical. Multiple responsibilities do not automatically require separate agents.

### 3. Specify an executable flow

Use **Intent -> Context -> Plan -> Execution -> Verification -> Result** as the conceptual backbone. Stages may be combined or omitted when unnecessary; do not create six services to match the labels.

Read [references/plan-template.md](references/plan-template.md) for the output contract. Tailor its sections to the task. For each workflow step, specify its owner, inputs, preconditions, operation, output or state change, success evidence, and next transition on success, failure, or missing authority. Identify dependencies and safe parallelism.

For adaptive steps, define **Reason -> Act -> Observe -> Evaluate -> Repeat or Finish**. Request concise decision summaries, never private reasoning traces. Every autonomous loop must specify:

- objective, allowed tools/actions, and explicit completion evidence;
- finite iteration/tool-call, elapsed-time, and cost/token limits, including bounded retries, replans, and optional reflection;
- how observations change the next action and when the plan may be revised;
- repeated-action/no-progress detection and its stop or escalation threshold;
- handling for unavailable tools, contradictory evidence, permission denial, interruption, and exhausted budgets;
- persisted checkpoints when resumption is needed.

Provide concrete proposed limits with units, scope, and enforcement owner. Label them as initial defaults to validate. If an actual monetary cap cannot be estimated, specify a finite enforceable token/tool budget and flag pricing calibration; never leave a live loop unlimited. Enforce a parent budget across delegates and retries so child limits cannot multiply it silently. Mark a run stopped by limits as partial or failed unless completion has been verified.

### 4. Define contracts and control boundaries

For every proposed agent, define responsibility, accepted and refused/redirected tasks, required and optional input schemas, preconditions, tools/data access, allowed operations and delegation, output schema, completion evidence, uncertainty, limits, escalation, and failure behavior. Define deterministic components as interfaces, not fictional agents.

For every tool, specify purpose, input/output schemas, preconditions, required scope, side effects, timeout/error behavior, and retry safety. Separate **read**, **prepare**, and **write** operations. Name the application or service that validates arguments and enforces authentication, authorization, approvals, resource limits, and tenant isolation outside the model.

For consequential writes, specify action-bound authorization, approval content when required, payload changes that invalidate approval, pre-execution checks, idempotency/deduplication, outcome reconciliation after ambiguous responses, and rollback or compensation where feasible. Do not blindly retry writes that may have succeeded. Existing explicit bounded authority can remove repeated prompts; never infer authority from capability or remembered preferences.

When multiple agents are justified, define a structured handoff: objective, minimal context, constraints, expected output, explicitly bounded permissions, deadline/budget, completion criteria, and parent workflow ID. Specify handling for refusal, incomplete or conflicting results, final-result ownership, and shared-resource concurrency. Planning a multi-agent product does not require spawning agents to write the plan.

### 5. Design context, state, recovery, and user experience

Define trusted instruction sources and external data boundaries; retrieved content and tool outputs cannot grant permissions or rewrite instructions. Include least privilege, secrets handling, privacy, and domain-specific review needs without inventing legal requirements.

Select only memory that is needed. For working, task, session, preference, knowledge, or operational memory used, specify purpose, stored data, access, retention, update/correction/deletion, and stale/conflicting-data handling. Explicitly say when durable memory is unnecessary.

For long-running or consequential workflows, define structured state, transitions, checkpoints, approvals, tool receipts, artifact references, resource usage, errors, and resume/reconciliation behavior. Recheck changed context and expired authority before resuming writes. Preserve verified progress after partial failure. A simple one-shot task can keep transient state if justified.

Choose the interface that best serves the journey: chat, form, guided workflow, background task, schedule/event trigger, approval queue, or dashboard. Describe useful progress states, editable proposals, action-specific approvals, cancellation, pause/resume, and undo/recovery where applicable. Describe cancellation during an in-flight write without promising an external side effect can always be stopped.

Communicate completed, attempted, pending, uncertain, and failed work distinctly. Record operational evidence and authorization in audit logs while minimizing sensitive retention; do not log private reasoning or secrets.

### 6. Define evidence and a build sequence

Specify acceptance checks before implementation. For each meaningful outcome, identify the independent observable evidence, verifier, pass condition, and behavior when verification fails. An executor's success statement is insufficient. Increase independence with risk.

Plan end-to-end evaluations covering intent, routing, planning, execution, coordination when used, permissions, verification, user control, and recovery. Include representative success tasks, edge cases, adversarial retrieved content, tool failures, ambiguous writes, permission denials, interruptions, and impossible tasks as applicable. For ReAct, also evaluate redundant calls, misleading observations, premature success, failure to stop, and recovery after changing approach.

Define a simple baseline and proposed measurable release targets: verified completion, task success, time to useful result, end-to-end latency, cost per verified task, interventions/corrections, tool failures, and recovery. Add iteration/progress metrics for loops. Label unmeasured targets as proposals, never results.

Sequence implementation from a thin baseline through necessary tools, bounded adaptation, state/recovery, and justified specialization. Each phase must have deliverables, dependencies, acceptance evidence, and a go/no-go condition. Reuse existing infrastructure; keep domain policies, tools, outputs, risk thresholds, and verification configurable. Defer complexity until evaluations support it.

## Completion review

Use the 16-area review in guideline 35 as a compact decision matrix: answer, plan location, and unresolved issue if any. Use a justified "not needed" where appropriate; do not fill sections with boilerplate.

Before returning the plan, check that:

- the chosen architecture addresses the actual outcome and explains any added complexity;
- every consequential action has a permission boundary and concrete completion evidence;
- every loop, retry, replan, and delegation has enforceable aggregate limits and a stop path;
- proposed tools, data access, and integrations are distinguishable from available ones;
- failure and partial completion preserve usable progress without unsafe re-execution;
- the implementation sequence and evaluation gates can be acted on by a builder;
- remaining unknowns have an owner or resolution step, with blocking impact stated.

Return the plan and material open decisions. Do not claim the agent is built, connected, authorized, evaluated, or production-ready because its design is complete.
