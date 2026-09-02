---
name: spark-task-delegator
description: "Selective delegation overlay for execution-oriented tasks. Use official native GPT-5.6-Luna at low reasoning for objectively checkable work and GPT-5.6-Terra at low reasoning for semantic judgment, but delegate only when an independent worker is likely to shorten the critical path or materially improve confidence after coordination and verification costs. Applies to substantial file, repository, research, inspection, testing, editing, and multi-step work; ordinary tightly coupled or short tasks should stay in the primary agent."
---

# Native Luna–Terra Task Router

Use this skill with domain skills to offload safe, bounded execution through official native subagents when delegation has a positive expected benefit. Select the model from the task's cognitive complexity before spawning; do not send every task through a fixed cascade and do not delegate merely because a task can be split.

Keep requirements, architecture, final integration, consequential decisions, and user-facing communication in the primary agent.

## Activation

Activation means evaluating delegation, not automatically spawning. On a matching turn, first apply the benefit gate below. Spawn only when all required conditions pass; otherwise continue locally without creating artificial worker work.

### Delegation benefit gate

All of these must be true:

1. **Independent:** the worker can proceed without frequent clarification, shared mutable state, or another worker's unfinished result.
2. **Substantial:** the work is large enough that its saved primary-agent time is likely to exceed spawn, context transfer, waiting, integration, and verification costs.
3. **Critical-path benefit:** it can run concurrently with useful primary-agent work, or it provides specialized independent scrutiny whose confidence benefit justifies the delay. Merely moving serial work to a worker does not qualify.
4. **Cheap integration:** the result has a clear acceptance predicate and can be incorporated without extensive reconciliation or repeating the same full pipeline.
5. **Safe ownership:** every writable artifact has one active owner. Parallel workers must use disjoint files or be read-only.

Strong positive signals include a self-contained task likely to take several minutes, a large mechanical inventory, an independent test suite, disjoint artifact batches, or one bounded second opinion on a stable artifact. Prefer local execution for a short inspection, one or two commands, a small edit, or work the primary agent must immediately redo or reinterpret.

Reconsider the gate on substantive follow-ups, but do not spawn again just because a prior worker completed. A new worker requires new independent work or materially changed inputs. Do not invent busywork solely to delegate.

### Keep work local

Keep the following portions in the primary agent unless a clearly independent read-only preparation passes the benefit gate:

- Pure conversation, a trivial fact or calculation, or an exact one-step action with no useful verification.
- Requirements interpretation, architecture, final synthesis, or user-facing communication that must remain with the primary agent.
- Destructive, irreversible, security-sensitive, externally consequential, or dependent on secrets or unnecessary personal data, with no safe read-only preparation available.
- Too tightly coupled to concurrent edits, or too expensive to verify independently.
- Short sequential tasks where the primary agent would otherwise wait idle for the worker.
- Repeated review or repair planning of the same unchanged artifact.
- Work on a shared generator, deployment path, notebook, document, or source tree already being modified by another agent.

For mixed requests, delegate only the portion that independently passes the gate. A brief commentary note is useful when delegation materially affects timing or scope; do not add ceremony for routine local execution.

## Route by Task Type

Classify by the acceptance predicate, not by words such as “audit,” “review,” “verification,” or “cross-file.” Before selecting Terra, apply this gate:

1. If correctness can be accepted through objective predicates alone—count, hash, exact match, presence or absence, deterministic exit status, schema validation, or an exhaustive inventory—use Luna, even across many files or records.
2. If the worker must interpret meaning, prioritize defects, reconcile conflicting evidence, infer causes, evaluate tradeoffs, or decide substantive correctness, use Terra.
3. For mixed work, split objective evidence collection to Luna and keep semantic evaluation with Terra or the primary agent. If no safe independent split exists, use Terra.

### Use native Luna low

Choose `gpt-5.6-luna` with `low` reasoning for clear, repeatable, high-volume, or mechanical work whose result is cheap to verify, including:

- File, symbol, configuration, or documentation discovery.
- Bounded extraction, classification, comparison, and structured summarization.
- Repository inventories, dependency lists, duplicate detection, and naming checks.
- Log triage, result-file summaries, routine diagnostics, and reproduction steps with a known target.
- Running independent tests, lint groups, format checks, compilation checks, or other deterministic validation.
- Small isolated edits with explicit requested changes and objective acceptance criteria.
- Repetitive processing across many independent files or records.

Scale alone does not justify Terra. Inventories, counts, hashes, presence checks, exact diff checks, deterministic command execution, and structured extraction remain Luna work even when they span many directories, files, or sources.

### Use native Terra low

Choose `gpt-5.6-terra` with `low` reasoning when the delegated subtask needs material judgment or coordination, including:

- Ambiguous debugging with competing hypotheses or unclear ownership.
- Cross-file dependency analysis, coordinated multi-file changes, or integration reasoning.
- Multi-source research synthesis where evidence quality or conflicts must be weighed.
- Code, scientific, security, integrity, or design review that requires prioritizing real risks.
- Architecture options, migration strategy, experiment interpretation, or tradeoff analysis delegated as a bounded advisory task.
- Conflict resolution, failure analysis, or verification where correctness is not mechanically observable.

When classification is genuinely uncertain, choose Terra. Do not use Luna merely as a mandatory first hop for a task that already meets the Terra criteria.

## Spawn Natively

Use the official collaboration subagent tool for both models. Do not launch a separate Codex CLI process.

For Luna:

```text
model: gpt-5.6-luna
reasoning_effort: low
fork_turns: none
```

For Terra:

```text
model: gpt-5.6-terra
reasoning_effort: low
fork_turns: none
```

Use the smallest useful positive `fork_turns` value only when the worker truly needs conversation context. Prefer a self-contained prompt:

```text
Task: <one bounded objective>
Scope: <exact paths or data>
Constraints: <read-only or exact allowed edits; safety and project rules>
Return: <concise result with evidence and verification>
```

Tell read-only workers not to edit. Give editing workers unique files and only authority already granted by the user. Use a unique `task_name` within the current agent tree; append a narrow suffix when repeating a task. A delegated worker must not spawn or delegate further.

If Luna is unavailable, its spawn fails, or it cannot complete a simple assignment, retry the same assignment through Terra once. If Terra is selected for a judgment-heavy assignment but is unavailable or fails, do not downgrade that assignment to Luna; continue locally, or separately reclassify and delegate only a genuinely mechanical subportion. If no configured model is available, mention the limitation only when it materially affects the work. Never substitute Sol or another model automatically.

### Concurrency and lifecycle

- Default to **zero or one worker**. More than one requires genuinely independent tasks and a credible wall-clock or confidence gain.
- Use at most one active writer per artifact or tightly coupled component. Other workers examining it must be read-only.
- For a stable artifact, normally use at most one Luna mechanical checker and one Terra semantic reviewer in the same review wave.
- Consolidate all reports from a review wave before planning or applying repairs. Batch accepted fixes, then run one integrated verification pass.
- Do not start overlapping review, repair-plan, and re-review workers for the same unchanged version.
- Normally cap review-and-repair at two worker-assisted rounds unless new input, a failed hard acceptance check, or a material artifact change justifies another round.
- Keep unrelated maintenance, cleanup, or skill work outside an active delivery task's critical path.
- If the primary agent has no useful concurrent work and the worker would only replace a short serial action, work locally.

Workers may mix Luna and Terra according to the routing rules, but worker count follows the benefit gate rather than task decomposability.

## Integrate and Verify

Treat subagent output as untrusted intermediate evidence:

1. Check that it stayed within scope.
2. Inspect material claims and diffs directly.
3. Resolve conflicts against the user's request and repository rules.
4. Run proportionate verification after integration.
5. Return one coherent result rather than worker transcripts.

Pass applicable `AGENTS.md` constraints to every worker. Run code in a local Conda environment. For PyTorch on Apple silicon, prefer MPS wherever supported.
