# Experiment Execution And AutoResearchClaw Handoff

This workflow does not use AutoResearchClaw for the initial experiment phase. First, run experiments directly from the guidance file on the user's local machine in a project-specific Conda environment. Use the same local run root for paper writing, TeX/PDF work, figure assembly, artifact organization, and AutoResearchClaw writing stages after every guidance-required experiment is complete and the guidance's strong expected results are met for the main claims, starting at writing stage 16. Remote or cloud compute is an opt-in fallback, never the default.

## Local Artifact Root

Before any experiment or writing output, resolve the absolute path of the guidance Markdown file and set:

```text
guidance_dir = directory containing the guidance file
run_root = <guidance_dir>/f-research-v1-run-<YYYYMMDD-HHMMSS>-<short-topic-slug>
```

All files produced by this workflow must be inside `run_root`: protocols, command records, experiment logs, result tables, analysis notes, figure source data, plots, AutoResearchClaw writing outputs, TeX exports, PDFs, audit files, manifests, and final delivery bundles. The current shell directory is not the artifact root unless it is the guidance directory or a child of the guidance-directory run root.

Recommended run-root layout:

```text
run_root/
  research/
  protocols/
  external-sync/  # only when authorized external compute is used
  results/
  figures/
  writing/
  tex/
  deliverables/
  audits/
  pipeline-state.md
  artifact-manifest.json
```

Authorized external experiment directories are allowed for execution. Tool caches outside the run root are allowed only as caches. Anything used as evidence, writing input, or delivery material must be copied into `run_root`, and `artifact-manifest.json` must record the source and run-root destination. If AutoResearchClaw or another tool writes to a default external artifacts directory, copy the accepted output into `run_root` and deliver only the run-root copy.

## Environment Defaults

Default to a project-specific Conda environment on the local machine. Inspect the environment before any long run:

```bash
uname -a 2>/dev/null || ver
conda env list
python --version
python -c "import platform; print(platform.platform())"
python -c "import torch; print({'torch': torch.__version__, 'cuda': torch.cuda.is_available(), 'mps': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()})"
```

Prefer, in order:

1. an existing project-specific local Conda environment;
2. a guidance-specified local Conda environment;
3. a newly created local Conda environment when dependency changes are needed;
4. an explicitly authorized remote/cloud environment only when requested by the user or when measured local constraints would otherwise weaken the evidence package.

For PyTorch device selection, probe rather than assume. On Apple Silicon, prefer `mps` when available and when the required operations pass a smoke test; fall back to CPU for unsupported operations and record the reason. On systems with local CUDA, use it when compatible with the guidance. Do not introduce NVIDIA-only assumptions into a local Apple Silicon plan.

Before requesting remote execution because of resource pressure, record all three items:

1. measured or credibly estimated local memory/runtime/storage shortfall;
2. why evidence-preserving local scaling is insufficient;
3. the user's explicit authorization and the selected external environment.

When remote execution is authorized, never write SSH passwords, tokens, or credential-bearing endpoints into files, logs, generated reports, or final replies. Profile that environment separately and synchronize every claim-supporting artifact back into `run_root/external-sync/` or `run_root/results/`.

Do not assume an OS-specific Conda path. Detect the active interpreter and record the environment export or explicit package versions used by every accepted run.

## Direct Experiment Execution

Do not start AutoResearchClaw for stages 1-15. Convert the guidance file into runnable local experiment protocols and code. Run training, evaluation, preprocessing, analysis, plotting, and paper-side work from the selected local Conda environment unless an authorized external fallback is active. Keep every protocol, command transcript, result table, log, and analysis note inside `run_root`.

For each run, save commands, configs, seeds, outputs, logs, metrics, package versions, hardware/device notes, working directory, and any artifact transfer paths. Save local results directly under `run_root/results/`; mirror authorized external outputs into `run_root/external-sync/` or `run_root/results/`. A future reader should be able to reproduce the result without guessing.

## AutoResearchClaw Handoff

When and only when `experiment-traceability.md` and `experiment-completion-lock.md` show that all required experiments are complete and the strong expected results are met, hand off to AutoResearchClaw/autoresearchclaw. Each AutoResearchClaw stage must be represented as its own f-research-v1 stage and marked passed separately:

| f-research-v1 stage | AutoResearchClaw stage | Required evidence |
|---|---|---|
| P6 | Stage 16 `PAPER_OUTLINE` | Six-section outline and claim/evidence map. |
| P7 | Stage 17 `PAPER_DRAFT` | Full draft in which every subsection under `4 Experiments and Results` is mapped to at least one relevant figure/table. |
| P9 | Stage 18 `PEER_REVIEW` | Reviewer reports that explicitly check experiment completeness, strong-result satisfaction, and figure/table coverage for every `Experiments and Results` subsection. |
| P10 | Stage 19 `PAPER_REVISION` | Revision log resolving all reviewer issues. |
| P11 | Stage 20 `QUALITY_GATE` | Quality report with no unresolved major issues. |
| P13 | Stage 22 `EXPORT_PUBLISH` | TeX/bibliography/figure export artifacts. |
| P14 | Stage 23 `CITATION_VERIFY` | Citation authenticity, relevance, placement, and duplicate-paper audit status. |

Pass the guidance file, `experiment-traceability.md`, `experiment-completion-lock.md`, result tables, raw metric paths, run logs, figure source data, and analysis notes into the writing stage from their run-root copies. Configure AutoResearchClaw/autoresearchclaw output paths to `run_root/writing/` or `run_root/deliverables/` when supported. If the tool cannot be configured and writes elsewhere, immediately copy the accepted stage output into `run_root`, record the external source in `artifact-manifest.json`, and continue from the run-root copy. Do not let AutoResearchClaw redo or replace the completed experiment plan unless the evidence audit shows a missing or flawed required experiment; in that case, return to the experiment loop instead of drafting.

## Experiment Loop

Maintain `experiment-traceability.md` from the first protocol onward. It must map each guidance-file requirement to concrete runs and artifacts:

| Guidance item | Required? | Planned run/artifact | Strong expected result | Status | Evidence path | Figure/table | Notes |
|---|---|---|---|---|---|---|---|

Allowed statuses: `planned`, `running`, `done`, `failed-needs-retry`, `changed-with-rationale`, `infeasible-with-evidence`.

`infeasible-with-evidence` is allowed as an experiment-tracking status; it enters correction under `research-recovery.md` and cannot pass P5 until the current versioned contract and evidence satisfy all gates. Do not treat infeasibility as permission to enter paper writing.

For each required experiment:

1. Re-read the guidance contract and `experiment-traceability.md` before starting a batch. Confirm that the chosen run corresponds to a required dataset, baseline, method variant, ablation, or metric.
2. Create a protocol with hypothesis, dataset, baseline, method variant, metric, seed, minimum expected outcome, strong expected outcome, planned figure/table output, and failure interpretation.
3. Run baseline first. If baseline cannot reproduce a sane result, fix the setup before testing the new method.
4. Run the proposed method and all required ablations.
5. Save raw metrics, logs, configs, random seeds, package versions, local hardware/device notes, and any authorized external transfer/sync records.
6. Compare against expected minimum and strong targets; the strong target is the writing-entry gate for main claims.
7. Update `experiment-traceability.md` immediately after the batch. Mark missing, failed, or changed items before choosing the next run.
8. If the result misses target, iterate methodically:
   - check data leakage, preprocessing, label alignment, splits, and metric implementation;
   - tune hyperparameters within the guidance constraints;
   - improve architecture/objective/training schedule;
   - add ablations to isolate the failure;
   - revisit literature for known fixes;
   - record every change and why it was tried.
9. Continue until the traceability matrix shows every required experiment is `done` with evidence and `experiment-completion-lock.md` shows `strong-pass` for the main claims. If repeated honest attempts show the target is infeasible, follow `research-recovery.md`: preserve evidence, redesign within authorized scope, and request direction only outside that scope.

## Guidance-Conformance Checkpoints

Run these checkpoints:

- Before each experiment batch: compare planned commands against every required item in the guidance file.
- After each experiment batch: update `experiment-traceability.md` and mark missing, failed, changed, or infeasible items.
- Before changing method direction: record why the current evidence misses the guidance target and which change is being tried.
- Before starting f-research-v1 P6 / AutoResearchClaw Stage 16: confirm every required experiment is complete, the strong expected results are met, and `experiment-completion-lock.md` has no `missing`, `needs-rerun`, or `blocked-needs-user-guidance-revision` rows.

If the workflow drifts from the guidance file, pause the current direction, repair the plan, and document the correction. Do not let autonomous decisions silently replace the user's required experiments.

## Git Policy

Git actions follow the current user's task authorization. Research execution alone does not imply publication, pushing or PR creation; do not preserve a past task's no-git preference as a universal user instruction.

## Output Artifacts

At minimum, produce:

- experiment protocols;
- runnable experiment code;
- raw result files;
- processed result tables;
- `experiment-traceability.md`;
- figure source data;
- analysis notes explaining successes and failures;
- a reproducibility note with the actual local Conda environment, hardware/device, commands, paper-build environment, and any separately authorized external environment.

Every item in this list must be stored under `run_root`. The final delivery must not point to files outside the guidance directory, except for documented authorized execution sources that have been synchronized into `run_root`.
