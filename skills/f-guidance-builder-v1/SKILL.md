---
name: f-guidance-builder-v1
description: Use when the user has a method or technique idea, optional application domain, and hardware constraints and wants a rigorously researched f-research-v1 guidance Markdown for a Q1/Q2-or-better journal research project.
---

# F Guidance Builder V1

## Theory-only requests

When the user explicitly requests a theoretical article without experiments, first load [references/theory-only-mode.md](references/theory-only-mode.md). Its authorized, separately recorded profile maps the existing stage IDs to proof-based gates and permits the actual native writing executor; empirical defaults below do not manufacture experiment obligations for this mode. Preserve empirical contracts unchanged.

## Execution contract

Read [references/execution-contract.md](references/execution-contract.md) at startup, resume, and correction. Initialize `pipeline-state.json` from `assets/pipeline-definition.json` using `scripts/pipeline_state.py --init` with the state path as its positional argument. Maintain the Markdown ledger as its readable view. Validate `--before <stage-id>` before starting a stage and `--complete` before delivery. The JSON definition is the canonical stage list; the workflow below defines the substantive gates. Record current user preferences and authorized scope once in a versioned run-local contract. This skill does not change the selected model or global settings.

## Overview

Use this skill before `f-research-v1`. Its job is to select or validate a publishable application scenario, then produce a guidance Markdown that satisfies `f-research-v1/references/guidance-file-spec.md` or the bundled copy at `references/f-research-guidance-file-spec.md`. Do not run experiments or write the paper here.

This skill is evidence-first, not story-first. Before generating the final guidance file, it must research recent literature, identify strong current baselines, reason through the method's theoretical feasibility, and stress-test whether the resulting story is strong enough for the requested journal tier. Only after those checks pass may it write the guidance file.

The `expected_strong` result required by `f-research-v1` remains binding. It is not a wish or a number selected for presentation value: it must be an evidence-grounded, pre-experiment target with a credible implementation path. This skill must reject attractive but mechanically unsupported stories before experiment execution begins.

## Inputs

Accept sparse inputs. The user only has to provide the target technique or method. If the user also provides hardware, datasets, target field, journal tier, or constraints, use them. If the application scenario is missing, search for one with public data, current research heat, a clear story, and realistic experiment cost.

Default to running experiments and paper-side work on the user's local machine in a project-specific Conda environment. Probe the actual local OS, CPU, RAM, disk, Python/Conda, and accelerator support before sizing the plan. For PyTorch on Apple Silicon, use MPS whenever the required operations are supported; otherwise record the CPU fallback. Use CUDA locally when available and appropriate. Treat remote or cloud execution as opt-in: use it only when the user explicitly requests it, the guidance already designates it, or local resources are demonstrably insufficient and the user authorizes the external execution. Never embed SSH endpoints, passwords, tokens, or other credentials in generated guidance, logs, templates, or skill files.

## Default Output Layout

Unless the user explicitly gives another output root, save every generated project under the current workspace's `auto-paper/` directory.

For each successful guidance build:

1. Create `auto-paper/` if it does not exist.
2. Create a run folder named by local generation time, using `yyyyMMdd-HHmmss` such as `20260602-143012`. If the timestamp already exists, append `-01`, `-02`, etc.
3. Inside the timestamp folder, create one folder named after the selected paper title. Sanitize only filesystem-illegal characters (`<>:"/\|?*`) and collapse repeated whitespace; keep the title human-readable.
4. Save all generated files inside that paper-title folder:
   - `guidance.md`
   - `novelty-feasibility-report.md`
   - `dataset-access-log.md`
   - `hardware-profile.md`
   - `scenario-decision-log.md`
   - `literature-baseline-matrix.md`
   - `theoretical-feasibility-audit.md`
   - `story-strength-audit.md`
5. Maintain `auto-paper/generated-research-directions.md`. If it does not exist, create it from `assets/generated-research-directions-template.md`. Append one row for every completed guidance build, including timestamp, paper title, technique, selected application scenario, gate verdict, guidance path, and brief notes.

Do not scatter generated files directly under `auto-paper/` or the workspace root.

## Sequential Execution Integrity

Create `guidance-pipeline-state.md` inside each selected paper-title folder before the CCFA startup deliberation. Its canonical order is `CCFA-startup -> G0 -> G1 -> G2 -> G3 -> G4 -> G5 -> G6 -> G7 -> G8 -> validation -> handoff`. Every stage must be recorded as `pending`, `running`, `passed`, `blocked`, or `superseded`; `skipped` is not a valid state.

Do not begin a stage until its immediate predecessor is recorded `passed`. A failed scenario may move to another scenario, but the replacement must restart from `CCFA-startup` and run every gate in order. A repair may revisit an earlier gate, but it must never mark a later gate passed using stale evidence. The final handoff is invalid unless the state ledger proves that every required stage passed in canonical order.

## CCFA Startup Deliberation

Run this deliberation before G0. The user has authorized this integrated CCFA handoff for this pipeline. Use the named CCFA skills for their owning responsibilities; do not replace their output with a generic internal summary or invoke unrelated CCFA skills.

1. Use `ccf-pipeline-orchestrator` to record the target venue/tier, constraints, stage gates, artifact owners, and the decision required at this start phase.
2. Use `ccf-idea-optimizer` in standard mode to turn the raw technique into one or more mechanism-level problem-method cards. Each card must state the bottleneck, causal or algorithmic mechanism, assumptions, falsification condition, contribution type, and known feasibility risks.
3. Use `ccf-literature-searcher` in standard mode to build a public-safe opportunity map: closest-work clusters, public datasets, current strong baselines, metrics, code/checkpoint availability, and differentiation routes. Its source-quality policy applies to the final packet.
4. Use `ccf-idea-reviewer` in standard mode for an independent red-team review after the literature map exists. Preserve its separate readiness score, development potential, confidence, fatal risks, and score-change conditions; do not convert an unsearched novelty claim into a positive score.
5. Use `ccf-experiment-designer` in `design` mode to build the claim-evidence matrix and the strong-result feasibility contract described below. It supplies placeholders and decision rules, never fabricated results.

Store the resulting `ccfa-startup-packet/` inside the selected paper-title folder. It must contain:

- `startup-stage-plan.md`
- `idea-cards.md`
- `prior-art-opportunity-map.md`
- `idea-red-team-review.md`
- `claim-evidence-matrix.md`
- `strong-result-feasibility-contract.md`
- `startup-decision.md`

`startup-decision.md` must be `proceed`, `revise`, `pivot-with-rescue-route`, or `needs-evidence`. Only `proceed` may enter G0. A low current-readiness score is not a rejection by itself, but an unaddressed fatal risk, missing mechanism, unavailable baseline, or infeasible evidence plan is a block.

### Strong-result feasibility contract

Also write `feasibility-contract.json` in the CCFA packet using [references/feasibility-schema.md](references/feasibility-schema.md). It is a machine-checkable index into the substantive Markdown evidence; the validator does not establish scientific validity. At validation, register the final guidance and packet as stage evidence rather than mutating the startup execution contract.


The contract makes the later P5 strong-result lock realistic without weakening it. For every main claim it must define:

- the claim, mechanism, prerequisite assumptions, and falsifying ablation;
- the exact dataset/split, primary metric and direction, simple baseline, strongest feasible domain baseline, and matched internal control;
- an evidence-based `minimum`, `expected_strong`, and `failure` condition. A target may use prior reported ranges, baseline variance, an effect-size or non-inferiority criterion, and planned seed confidence intervals, but may not assume an arbitrary headline gain;
- implementation readiness: code or adaptation source, missing components, prototype/sanity-check milestone, compute/memory/runtime budget, seed count, hyperparameter-search budget, and reproducibility artifacts;
- the reviewer question answered by each main experiment, ablation, robustness test, and efficiency measurement; and
- explicit stop-and-return conditions. If an assumption, baseline, prototype, or budget fails, return to scenario/method design before P2 rather than train toward an implausible target.

## Fail-Fast Pipeline

Run these gates in order. If a hard-blocking gate fails, stop that scenario immediately and try the next application scenario. Keep a `scenario-decision-log.md` with pass/fail reasons and source links.

| Gate | Decision | Pass condition |
|---|---|---|
| G0 Recent literature and baseline map | Hard block | Web/literature search identifies the current strongest baselines, including recent authoritative papers from the last 3-5 years, their official code/checkpoint status when available, datasets, metrics, and whether they are direct experimental baselines or literature-only context. |
| G1 Public dataset access | Hard block | At least one suitable dataset is directly public: downloadable by URL, official repository, Hugging Face, Kaggle, OpenML, UCI, Zenodo, Figshare, GitHub release, or similar. Exclude datasets requiring email approval, institutional approval, NDA, IRB, payment, manual review, or waiting for access. |
| G2 Task and evaluation validity | Hard block | Dataset supports a clear input-output task, labels or measurable targets, reproducible splits or split strategy, primary metric, and evaluation protocol. |
| G3 Theoretical fit and feasibility proof | Hard block | The technique has a concrete mechanism-level reason to help in this application, not just "apply method X to domain Y"; the guidance includes a short theory/algorithm feasibility audit explaining why the method is learnable, what assumptions it needs, and what would falsify the mechanism. |
| G4 Novelty and non-duplication | Hard block | Literature search finds no highly similar paper with the same method family, application task, dataset class, and core contribution. Related work is allowed only if the proposed angle remains distinct. |
| G5 Hardware and runtime feasibility | Repairable block | The project can run on the user's local machine and Conda environment under its hardware/runtime budget, using MPS/CUDA when supported, or the plan can be credibly scaled down while preserving evidence strength. Any remote execution is an explicit opt-in exception. |
| G6 Strong baseline and ablation feasibility | Repairable block | The plan includes simple baselines, matched internal baselines, strong recent domain baselines, and technique-family baselines. For Q1/top targets, at least one strong recent authoritative baseline must be planned as a direct rerun/adaptation attempt before method iteration; literature-only baselines are clearly separated and cannot carry the main comparison. |
| G7 Effectiveness and strong-result plausibility | Repairable block | The CCFA strong-result feasibility contract shows a mechanism-supported, baseline-calibrated path to the binding `expected_strong` result, including a runnable prototype milestone, adequate compute/seed/search budget, falsifying ablations, and stop-and-return conditions. Theory, prior results, pilot evidence, or task structure must support the target; arbitrary desired gains do not pass. |
| G8 Story strength for target tier | Final value gate | The result can support the requested journal tier with a skeptical-reviewer story: clear bottleneck, distinct mechanism, strong baselines, decisive ablations, honest risks, and a reason the contribution is more than an incremental benchmark table. |

Read `references/fail-fast-gates.md` for detailed gate criteria.

## Search And Verification

Use web/literature search for datasets, recent papers, and citation candidates because these facts are time-sensitive. Prefer official dataset pages, papers, venue pages, publisher pages, arXiv, Papers With Code, Hugging Face dataset cards, and repository releases. Record exact source links, access dates, license notes, and why each source is relevant.

Never present "public on request", "available after approval", "contact authors", or "request access" as directly public. If all useful datasets have access friction, reject the scenario.

For novelty, check at least:

- Same technique + same application domain.
- Same task + competing techniques.
- Same dataset + similar claims.
- Last 3-5 years of top venues and Q1/Q2 journals.

For baseline selection, create `literature-baseline-matrix.md` before the guidance file. It must include:

- paper/method name, year, venue/publisher, and official URL;
- task/dataset/metric used by the paper;
- whether code and checkpoints are available;
- direct-rerun feasibility on the user's local machine and selected Conda environment;
- expected role: `must-rerun`, `adaptation-attempt`, `internal-matched`, `oracle/upper-bound`, or `literature-context`;
- why it is strong, recent, and authoritative enough to include or why it is rejected.

Do not let the final guidance compare only against weak ANN toy baselines when recent domain baselines exist. Matched ANN baselines are useful controls, but they are not enough for a top-journal guidance file.

Use `references/source-verification.md` when deciding whether evidence is strong enough.

## Scenario Selection

When the user does not provide an application scenario, generate 3-6 candidate scenarios. Evaluate each in canonical order from CCFA-startup through G0-G8; rejected candidates retain their failed gate and do not advance. Reuse unchanged sourced evidence only after checking applicability to each candidate. Prefer scenarios with:

- Directly public datasets and mature metrics.
- Current research heat from recent papers, benchmarks, regulations, or deployment needs.
- A method-domain fit that can be explained mechanistically.
- A story that can produce more than an incremental benchmark table.
- Experiments feasible on the user's local machine, including local writing and final artifact preparation; remote compute is optional and never assumed.

Select the highest-scoring scenario only after the earlier hard gates pass. If two scenarios are close, pick the one with stronger data access and cleaner story.

## Theory And Story Verification

Before writing the final `guidance.md`, create `theoretical-feasibility-audit.md` and `story-strength-audit.md`.

The theoretical audit must answer:

- What is the causal or algorithmic mechanism by which the technique should improve the task?
- What assumptions about data, labels, temporal structure, optimization, or compute are required?
- What existing papers support those assumptions?
- What ablation would falsify the claimed mechanism?
- What failure mode would make the project unsuitable for the requested journal tier?

The story audit must answer:

- Why would a skeptical top-journal reviewer care?
- What is the strongest existing paper that could make this work look incremental?
- What exact experiment would distinguish the proposed contribution from that paper?
- What result threshold is needed for a strong paper, not merely a runnable demo?
- If the result is only partially positive, what honest lower-tier or diagnostic story remains?

The story audit must agree with `ccfa-startup-packet/strong-result-feasibility-contract.md`. It may not promise an experiment whose mechanism, strong baseline, code path, seed budget, or compute budget is absent from the contract.

If either audit is weak, revise the scenario or method before generating `guidance.md`.

## Guidance File Output

Keep the existing first-level headings and six-section outline. Add only lightweight optional writing handoff fields: the central scientific question and intended reader; how the domain/theory problem motivates a design choice; expected contribution type; author writing preferences/protected scope/venue requirements with their source; and a statement that `planned_claim` is distinct from `observed_finding`, which is updated from evidence at P5A/P6. Missing fields in an existing guidance file are not blocking: f-research-v1 may fill them from authorized facts at P6, preserving unknown/unresolved states. Do not turn predicted findings into results, or rebuild research-planning content here.

Produce a `guidance.md` inside `auto-paper/<generation-time>/<paper-title>/` that follows `f-research-v1/references/guidance-file-spec.md` when available, otherwise use `references/f-research-guidance-file-spec.md`. Use the template in `assets/guidance-output-template.md`. Do not modify either spec unless the user explicitly asks.

The guidance file must be strong enough for a Q2-or-better journal submission plan:

- Concrete title, target field, target journal tier, and contribution claim.
- Paper story with problem, gap, insight, and evidence chain.
- Section-level outline.
- Detailed experiments: datasets, baselines, variants, ablations, metrics, statistical checks, runtime budget, stopping criteria.
- Expected results with minimum acceptable result, strong result, and failure signal.
- A reference to the CCFA startup packet and a claim-level strong-result feasibility contract; every binding strong target must be traceable to a baseline-calibrated evidence plan, not a desired outcome.
- Optional figure/table decision rules that describe what evidence may benefit from visualization, without imposing a count or assigning an artifact to every subsection. The final set is chosen by `f-research-v1` after evidence stabilizes.
- Citation scope with relevant topic clusters, must-cite works, and venue/field recency considerations; the appropriate bibliography size depends on scope and venue.

Also output:

- `novelty-feasibility-report.md` using `assets/novelty-report-template.md`.
- `dataset-access-log.md` with direct access links and rejected datasets.
- `hardware-profile.md` using `assets/hardware-profile-template.md`.
- `scenario-decision-log.md` for all scenarios considered.
- `literature-baseline-matrix.md` with recent authoritative baselines and direct-rerun feasibility.
- `theoretical-feasibility-audit.md` with mechanism-level reasoning and falsification tests.
- `story-strength-audit.md` with skeptical-reviewer and target-tier checks.
- `ccfa-startup-packet/` with the deliberation, red-team review, and strong-result feasibility contract.
- an appended entry in `auto-paper/generated-research-directions.md` recording the generated research direction.

Run `scripts/validate_guidance.py <guidance.md> --strict --packet <ccfa-startup-packet-directory>` before handing off to `f-research-v1`. Fix missing sections before finalizing.

## Blocking Rules

- If no directly public dataset exists, do not generate a final guidance file for that scenario.
- If the core idea is substantially duplicated by an existing paper, switch scenarios or redefine the contribution.
- If the method has no theoretical fit, switch scenarios.
- If the theory audit cannot identify a falsifying ablation, do not generate the final guidance file.
- If the strong-result feasibility contract lacks a mechanism-supported runnable path, a feasible strong baseline, or an adequate compute/seed/search budget, do not generate the final guidance file. Redesign the scenario, claim, or method; do not lower a binding target merely to pass the gate.
- If recent strong baselines exist but the plan has no credible way to rerun, adapt, or honestly separate them, do not claim a Q1/top-journal target.
- If the local machine cannot support persuasive experiments after evidence-preserving scaling, either switch scenarios or request explicit authorization for suitable remote compute.
- If the story cannot reach Q2+ rigor, label it unsuitable instead of lowering the standard.
- Do not invent datasets, citations, benchmark results, or access status.
- Never skip, reorder, or infer completion of a CCFA-startup or G0-G8 gate. Record every revisit and scenario replacement in `guidance-pipeline-state.md`.

## References

- `references/fail-fast-gates.md`: detailed gate checks and scoring.
- `references/f-research-guidance-file-spec.md`: bundled copy of the target guidance file contract.
- `references/source-verification.md`: dataset, literature, and novelty source standards.
- `references/q2-guidance-standard.md`: minimum quality bar for generated guidance files.
- `assets/idea-intake-template.md`: optional intake form when the user gives very little context.
- `assets/guidance-output-template.md`: final guidance Markdown template.
- `assets/generated-research-directions-template.md`: `auto-paper` index template for generated research directions.
- `scripts/hardware_probe.py`: preferred cross-platform, privacy-safe local hardware/Conda/PyTorch accelerator probe; run it inside the intended Conda environment.
- `scripts/hardware_probe.ps1`: optional supplemental Windows local-hardware snapshot helper. Profile remote hardware only when remote execution has been explicitly selected.
- `scripts/validate_guidance.py`: structural validator for generated guidance files.
