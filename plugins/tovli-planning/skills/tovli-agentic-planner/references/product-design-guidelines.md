# Product Design Guidelines for Agentic AI Systems

**Version 2.0 — Domain-Agnostic Product and Architecture Principles**

Source: the guidelines supplied by the user for this skill. This operational digest preserves the 35 numbered principles, autonomy scale, review questions, and governing rules. It is condensed for planning use rather than a verbatim copy. The guidelines concern the product being designed; they do not authorize the planner to execute that product.

**Governing principle:** Build the smallest, safest, most understandable system that can reliably complete the user's intended task. Complexity must earn its place through verified user outcomes.

## Contents

- 1-4: Product foundations and autonomy
- 5-8: ReAct, execution strategy, and verification
- 9-13: Architecture, contracts, and delegation
- 14-16: Context, memory, and state
- 17-19: Tools, permissions, and repeatable actions
- 20-23: User experience and control
- 24-27: Failure, security, and auditability
- 28-31: Evaluation and incremental complexity
- 32-34: Reuse, composition, and interaction models
- 35: Mandatory product design review

## Product foundations

### 1. Design for user outcomes, not agent capabilities

Establish who the user is, their intended outcome, today's difficulty, required information/decisions/actions, successful completion, credible harms, and why an AI agent improves on simpler software. Prefer deterministic software when more reliable, affordable, and predictable. Measure enabled outcomes rather than steps performed.

### 2. Organize the product around user intent

Expose goals and tasks rather than internal agent selection, models, tool wiring, or reasoning iterations. Show agent identity only when expertise, responsibility, permissions, or accountability make it useful. Users should not manually orchestrate agents unless that is their actual task.

### 3. Model every task as an outcome-oriented workflow

Use **Intent -> Context -> Plan -> Execution -> Verification -> Result**. Intent establishes the goal and constraints; context gathers needed information; planning selects the approach when necessary; execution performs authorized work; verification checks the actual outcome; the result reports completion, uncertainty, and next steps. Stages need not be visible, separate components, or all necessary for a simple task.

### 4. Apply risk-proportionate autonomy

Choose the lowest autonomy that delivers the needed value. Evaluate impact, reversibility, financial cost, privacy, and actual authorization per action.

| Level | Behavior | Example |
| --- | --- | --- |
| 0 — Inform | Provides information | Explain a policy |
| 1 — Recommend | Suggests an action | Recommend an itinerary |
| 2 — Prepare | Creates a proposed action | Draft an email or purchase order |
| 3 — Execute with approval | Acts after confirmation | Send an email or place an order |
| 4 — Bounded autonomy | Acts independently within explicit limits | Categorize incoming requests |
| 5 — Delegated autonomy | Manages a defined objective across steps | Maintain a recurring operational workflow |

An agent may use several levels across tasks. Ability does not imply permission.

## Agent execution and reasoning

### 5. Use ReAct as a foundational adaptive execution pattern

Use **Reason -> Act -> Observe -> Evaluate -> Repeat or Finish** when adapting to new observations creates value.

- **Reason:** Select the smallest meaningful next step using the objective, state, context, observations, available tools, permissions, and remaining budget.
- **Act:** Perform a concrete authorized operation with validated inputs: retrieval, analysis, artifact work, delegation, clarification, or approval.
- **Observe:** Read the actual result, including partial success, error, denial, conflict, or environmental change. An attempted call is not evidence of success.
- **Evaluate:** Decide whether the goal is achieved, verification or information is missing, the approach should change, human input is needed, or execution should stop.
- **Repeat or finish:** Continue only when another iteration is useful. Stop on verified completion, inability to progress, missing authority, or exhausted limits.

Every autonomous loop requires an objective, defined permissions, completion condition, maximum iterations or tool calls, time and cost budgets, failure/escalation conditions, repetition/no-progress detection, persistent state where needed, and verification of consequential results. Never design an unbounded autonomous loop. ReAct sits inside orchestration, permission enforcement, and verification; it does not replace them.

### 6. Select the right execution strategy

| Pattern | Suitable tasks | Trade-off |
| --- | --- | --- |
| Single-pass response | Simple questions, transformations, classification | Limited adaptation |
| Deterministic workflow | Predictable, repeatable processes | Less flexibility |
| ReAct loop | Discovery and adaptive tool use | Variability and cost |
| Plan-then-execute | Multi-step tasks with known dependencies | Plans can become stale |
| Plan-and-replan | Complex tasks under changing conditions | Coordination overhead |
| Parallel execution | Independent subtasks | Aggregation required |
| Multi-agent collaboration | Distinct expertise or capabilities | Communication and coordination costs |

Combine patterns where justified. Choose according to uncertainty, dependencies, risk, and measurable performance.

### 7. Separate planning, execution, and verification

Planning decides what to do; execution does it; verification establishes whether the goal was satisfied. One agent or deterministic components may serve several roles. Self-reported success is insufficient; higher-risk tasks need independent checks such as authoritative system state, calculation validation, artifact inspection, or external confirmation.

### 8. Use reflection selectively

Use deliberate review to find a specific gap or corrective action when the improvement justifies the cost. Prefer objective tests, external evidence, and independent validation. Repeated self-critique can reinforce errors and consume time; it must not become endless reconsideration.

## Multi-agent architecture

### 9. Start with the simplest viable architecture

Consider, in increasing complexity: deterministic logic, single model call, single agent with tools, fixed specialized workflow, router with specialists, coordinator with multiple agents, collaborative multi-agent system. Add agents for distinct permissions, expertise, independent parallel work, quality/safety boundaries, different execution needs, or reusable capabilities when benefits are measurable. Multiple user needs alone do not justify multiple agents.

### 10. Define explicit agent contracts

Specify responsibility; accepted, refused, or redirected tasks; required/optional input context, format, and preconditions; tools, data, operations, and delegation permissions; output structure, completion criteria, evidence, and meaningful uncertainty; time/cost/retry limits, escalation, and failure behavior. Avoid overlapping responsibilities without conflict resolution. Agents should be independently understandable, testable, and replaceable.

### 11. Treat orchestration as a separate architectural layer

Orchestration chooses which capability runs, order, context, and authority; individual execution determines how a task is performed. Routing, dependencies, parallel scheduling, state, budgets, aggregation, failures, approvals, and completion belong to orchestration. Predictable orchestration can be deterministic rather than another AI agent.

### 12. Use explicit delegation and handoff protocols

Handoffs carry objective, relevant context, constraints, expected output, explicitly available permissions, deadline/budget, completion criteria, and parent workflow ID. Receivers should not reconstruct a full conversation. Delegation cannot expand authority. Define refusal, failure, incomplete-result, and contradiction handling.

### 13. Minimize coordination overhead

Parallelize sufficiently independent work. Prefer structured messages and artifacts to long internal discussions. Name the final-result owner and coordinate shared-resource writes. Added agents should improve specialization or throughput enough to justify communication, latency, synchronization, and failure costs.

## Context, memory, and state

### 14. Treat context as a managed resource

Provide the minimum sufficient request, history, preferences, documents, retrieved knowledge, observations, state, decisions, and permissions. Avoid indiscriminate full-history or memory transfer. Separate trusted instructions from external documents, websites, messages, and tool results: external content is evidence to evaluate, not authority to obey.

### 15. Design memory by purpose

| Type | Purpose |
| --- | --- |
| Working | Current execution information |
| Task | Ongoing progress, decisions, artifacts |
| Session | Conversation continuity |
| Preference | Durable user preferences |
| Knowledge | Retrieved or curated domain knowledge |
| Operational history | Actions, approvals, outcomes |

For each type used, define stored data, purpose, access, lifetime, updates, correction/deletion, and stale/conflicting-information handling. Memory should support continuity without hidden assumptions; remembered information is not permanently true.

### 16. Maintain durable workflow state

Complex and long-running work must survive the end of a model call, process, or session. Use structured status and checkpoints rather than conversation alone. Statuses may include created, queued, running, waiting for tool/user/approval, paused, completed, partially completed, failed, and cancelled. Track objective, completed/pending steps, tool outcomes, artifacts, approvals, resource usage, errors, and recovery checkpoints to support interruption, resumption, auditing, and recovery.

## Tools, actions, and permissions

### 17. Treat tools as explicit capabilities

Each tool needs purpose, input/output schemas, preconditions, required permissions, side effects, error/timeout behavior, and retry safety. Favor narrowly scoped capabilities. Validate arguments outside the model and avoid granting powerful operations when restricted ones suffice.

### 18. Separate reading, preparing, and acting

Read retrieves without external changes; prepare creates drafts or previews; write modifies data, communicates externally, spends money, or triggers consequential actions. Apply distinct permissions and confirmations. Read or draft authority does not grant send authority. Approval is specific to the action and consequences, not the agent's identity.

### 19. Design for safe and repeatable actions

After timeout or ambiguous outcome, determine whether the action already succeeded before retrying. Use idempotency, transaction IDs, receipts, deduplication, precondition checks, compensation, rollback, or escalation as appropriate. Never blindly retry a potentially duplicate payment, message, booking, order, or record creation.

## Human experience and control

### 20. Make agent behavior understandable

Show meaningful states: understanding, gathering information, preparing, waiting for approval, executing, checking, completed, or unable to proceed. Scale detail to task complexity. Explain actions, evidence, decisions, and limits concisely; do not expose noisy agent messages or private reasoning traces.

### 21. Preserve user control

Support appropriate review, editing, approval/rejection, pause, cancel, resume, corrections, changed constraints, and feasible undo/recovery. Confirmations must make consequences and authorization clear, especially for irreversible actions.

### 22. Ask questions only when they matter

Infer, retrieve, or use a safe stated default when possible. Clarify materially different interpretations, essential missing information, unclear authority, significant consequences of a wrong assumption, or preferences that cannot safely be inferred. Obtain explicit confirmation for high-impact decisions instead of assuming consent.

### 23. Communicate uncertainty and partial completion

Distinguish facts, inferences, recommendations, unverified claims, attempted actions, completed actions, and pending work. Report partial success and evidence gaps honestly. Offer an alternative when unable to act; never simulate success.

## Reliability, safety, and governance

### 24. Engineer for failure and recovery

Account for timeout, invalid output, missing information, rate limits, outages, conflicting findings, denials, interruptions, partial execution, and unexpected effects. Use bounded retries and clear recovery. Reuse safe completed work rather than restarting everything; preserve useful progress when recovery is impossible.

### 25. Verify outcomes independently where possible

Define acceptance criteria before execution. Check authoritative data, external system changes, automated tests, schemas, calculations, constraints, artifacts, or human review. Verification rigor and independence increase with impact. Generated text is not proof of completion.

### 26. Enforce security outside the model

Use technical authentication, authorization, least privilege, data isolation, secret handling, restricted tools, approval enforcement, audit logs, and rate/spending caps. Treat retrieved content and tool results as untrusted. They cannot change trusted instructions or permissions. Identify applicable domain privacy, retention, and regulatory needs without substituting prompt text for enforcement.

### 27. Make actions auditable

Record the request, workflow/agent, tools, authorization, external changes, completion evidence, errors, and interventions needed for accountability. Minimize sensitive retention. An audit trail does not require internal model thoughts.

## Quality, performance, and evaluation

### 28. Optimize quality, latency, and cost together

Measure task success, verified completion, time to useful result, end-to-end latency, cost per successful task, tool failures, interventions, user corrections, unnecessary iterations, recovery, and satisfaction. Include model, tool, retrieval, and coordination costs. Cheap calls with retries may cost more overall; fast incorrect external actions may be unacceptable.

### 29. Evaluate the entire workflow

Evaluate intent understanding, routing, planning, execution, coordination, safety, verification, user experience/control, and recovery. Use representative tasks, edge cases, adversarial inputs, and failure simulations. Maintain a stable baseline and track regressions over time; prompt-only tests are insufficient.

### 30. Evaluate ReAct loops specifically

Measure average/max iterations, productive iterations, redundant calls, incorrect tool choice, premature completion, failure to stop, recovery from unexpected observations, revision of wrong approaches, and cost/latency per verified outcome. Test misleading observations, unavailable tools, conflicting evidence, and impossible tasks. Recognizing when to stop is part of success.

### 31. Introduce complexity through evidence

Define outcome and acceptance criteria, build a simple baseline, add necessary tools, add bounded adaptation if needed, add state/recovery, then justified specialization. Advanced planning, memory, and collaboration must show measured improvement against the baseline. Remove complexity without sufficient benefit.

## Reusable product architecture

### 32. Separate reusable infrastructure from domain behavior

Reuse identity, permissions, registry/routing, orchestration, tool execution, context/memory, state, approvals, observability, cost controls, evaluation, and audit infrastructure where needed. Configure domain instructions, knowledge, tools, policies, approvals, outputs, success criteria, verification, and risk thresholds. Do not duplicate foundations per agent or force every domain into one reasoning process.

### 33. Keep agent capabilities composable

Use clear interfaces, bounded responsibilities, and predictable outputs so research, document generation, and other capabilities can serve several workflows. Prefer reusable capabilities to tightly coupled personalities.

### 34. Support multiple interaction models

Choose among conversation, forms, guided flows, background execution, scheduled/event-triggered tasks, approval queues, dashboards, and collaborative workspaces according to clarity and user control. Chat is not the default answer for every task.

## 35. Mandatory product design review

These answers must affect architecture, permissions, user experience, and tests. In a plan, add the concrete decision, relevant plan section, and unresolved issue where applicable.

| Area | Required question |
| --- | --- |
| User value | What specific user outcome does this feature improve? |
| Necessity | Why is an agent needed instead of simpler software? |
| Autonomy | What may the system do without asking? |
| Execution | Should it use deterministic logic, ReAct, planning, or a combination? |
| Architecture | Is one agent sufficient, or is specialization justified? |
| Routing | How is the appropriate capability selected? |
| Tools | Which tools are required, and what permissions apply? |
| Context | What information is necessary and trustworthy? |
| Memory | What must persist, and for how long? |
| State | Can the task be paused, resumed, or recovered? |
| Verification | How will successful completion be established? |
| Failure | What happens when execution cannot continue? |
| User control | When can the user inspect, correct, approve, or cancel? |
| Safety | What are the worst credible consequences? |
| Evaluation | Which measurable results justify the design? |
| Performance | What are the acceptable time, cost, and iteration limits? |

## Decision rules and final principle

The numbered principles above operationalize the guidelines' final rules: start with the outcome; prefer simplicity; use bounded ReAct for adaptation and deterministic workflows for predictability; separate orchestration, execution, and verification; define contracts; manage context/memory; enforce authority technically; make consequential actions deliberate; preserve progress through failure; provide proportionate control; verify outcomes; measure whole tasks; configure domain logic; and make every added agent, loop, tool, and memory layer justify its cost.

An excellent agentic product makes complex work feel simple while remaining reliable, transparent, and under the user's control.
