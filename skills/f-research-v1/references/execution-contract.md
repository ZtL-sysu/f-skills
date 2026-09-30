# Execution and evidence contract

Use this reference at run startup, resume, correction, and final delivery. The ordered stages in `assets/pipeline-definition.json` are the machine-readable authority; the numbered workflow supplies each stage's substantive gate. Keep a human-readable Markdown ledger alongside `pipeline-state.json`. JSON controls structural readiness; neither a hash nor a successful validator proves scientific, factual, or visual correctness.

## Startup and authority

Record an immutable run-local `execution-contract-v1.md`: user goal, authorized operations, inputs, scope, resource/runtime envelope, output root, quality requirements, and relevant user preferences. Preserve the user's current instructions over skill defaults, subject to host/system constraints. Routine work and explicitly integrated CCFA transitions inside that scope need no renewed confirmation. Do not change global CCFA handoff settings. Questions are for material missing choices or scope expansion, not repeated approval of already authorized steps. Cite the exact instruction and completed preparation when a genuine blocker requires user direction.

For writing, add optional `edit_scope`, `protected_sections` (exact unique text/label ranges), `protected_artifacts`, `declaration_mode` (`preserve`, `author-managed`, `journal-routed`), and `allow_new_experiments` from current authorization, never inferred from a prose task. Hash protected originals and compare exact protected ranges before/after edits; report factual concerns externally when an author forbids changes. Author-managed required declarations remain pending until the author resolves them. Record an editing-round budget (default three) and stop after two rounds without fewer concrete defects; exhaustion never grants acceptance. Older contracts without these fields remain usable: establish their current scope before editing without inventing prior stage completion.

Record installed dependency names, versions or hashes, available tools, actual model/effort if exposed, Conda environment and device. Do not infer the running model from this file. Preserve the selected model and effort; request stronger reasoning only when needed and supported. Astra API tool-calling adaptations belong in the actual API executor, not skill prose. If one is used, verify its current official compatibility before execution; do not assume an external CLI inherits this chat's model.

Initialize once, inside the run root:
```text
conda run -n <environment> python <skill-dir>/scripts/pipeline_state.py <run-root>/pipeline-state.json --init
```
Populate `contract` with immutable contract/input-manifest snapshots. Each file entry is `{"path":"relative/path","sha256":"64-character SHA-256"}`. All listed files must be nonempty, present under the run root, and hash-correct. Imported originals may be referenced externally in prose, but copy evidence snapshots into the run root for validation.

## Ordered progress and back-edges

Before starting a stage run the validator with `--before <stage-id>`. After completing its real gate, write its `inputs`, `evidence` (including a substantive gate report), current `contract_version`, `gate_verdict: pass`, and `status: passed`; append `{"action":"pass","stage":"<id>"}` to `history`. Validate immediately. Record failed checks as `blocked` with failure details, not passed. Only the first unfinished stage may be running or blocked. Statuses are pending/running/passed/blocked/superseded.

Before revising an accepted input, preserve the previous acceptance report, append a `reopen` event with the earliest affected stage and a concrete `reason`, and reset that stage and its entire downstream suffix to pending. Preserve prior evidence in versioned files/history. Then process the suffix in order. Corrections inside a not-yet-passed stage remain inside that stage.

A change to the execution contract creates a new immutable contract version and reopens the entire sequence from its first stage; every gate must be accepted against the new version. This does not require redoing unchanged experiments: reuse immutable prior evidence only after explicitly confirming all relevant data/splits/code/config/seeds/environment and gate criteria still match. Never transfer a passed flag without rechecking its applicability.

The ledger validator is a consistency guard, not a tamper-proof scheduler. It detects missing/reordered stages, unfinished predecessors, stale or missing evidence, mismatched contract versions, and inconsistent pass/reopen history. Never hand-edit a fake history to claim unexecuted work. At delivery require:
```text
conda run -n <environment> python <skill-dir>/scripts/pipeline_state.py <run-root>/pipeline-state.json --complete
```

## Existing-run migration

For a run that has only an older Markdown ledger, initialize a pending JSON ledger without overwriting any existing JSON state. Reconstruct accepted stages in canonical order from real versioned evidence and current input hashes; record that this is migration/reacceptance in the Markdown report. A missing old stage cannot be inferred passed from a later draft or report. Reuse verifiable artifacts, execute missing gates, and preserve the old ledger as run history. This concerns research/teaching run continuity, not backups of installed skills.

## Resume and change control

After interruption read the latest contract, JSON ledger, correction record, and artifact index; check existing process/job identifiers before restarting work. Rehash accepted evidence and resume the first unfinished stage. Do not spawn duplicate training, builds, or image jobs. A mid-task user update preserves completed work unless its dependencies changed; log changed constraints and invalidate affected evidence.

Use stable, versioned outputs for accepted stages. Do not hash a mutable shared ledger as stage evidence. Record an input manifest listing actual dependencies and their hashes for large jobs, and verify those dependencies before reuse. A matching manifest file alone does not prove its listed dependencies remain unchanged.

## Proportionate checking and delegation

Keep required final acceptance. Recheck changed outputs and their dependents; broaden checks when shared code, data, renderer, template, environment, or acceptance rules change. Unchanged valid experiment results do not need retraining after prose edits. A global visual-style change requires global visual review. A final distributed archive still needs its required clean-extraction test.

During a substantial stage, use the installed `spark-task-delegator` only if independent read-heavy work can run alongside useful primary work. Respect its current model/effort policy and one-writer rule; this workflow does not override it. Do not parallelize canonical stages. Give a reviewer frozen inputs and record `review_execution: same-agent-role-pass | independent-agent`; skill switching or multiple simulated personas alone is not independent-agent review. The primary agent owns scientific judgment and final acceptance.

## Official basis

Checked 2026-09-10: [Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra), [Build skills](https://developers.openai.com/codex/skills), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Apply their guidance on conflicting instructions, autonomy, context, delegation and proportionate verification. The workflow's scientific and teaching thresholds remain domain requirements, not claims about model capabilities.
