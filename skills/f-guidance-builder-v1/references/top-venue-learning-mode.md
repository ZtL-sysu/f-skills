# Top-Venue Learning Mode

Use this mode by default at the start of research planning, without requiring a separate user request, and when revising an existing project. Learn from recent top-venue work in its family — how those papers tell their story, design their experiment matrix, and execute experiments — and convert that learning into concrete contract upgrades. Respect an explicit user instruction to omit or limit this study. In theory-only work, adapt experiment and execution analysis to proof strategies, assumptions, mathematical evidence, and falsification or counterexamples; do not create empirical experiment obligations. It upgrades the evidence behind G0 (literature map), G7 (strong-result plausibility) and G8 (story strength); it does not relax any gate or any binding target.

The mode has six phases. Run them in order inside CCFA-startup (or as a versioned-contract revision), and archive the artifacts in the run folder.

## L1 Locate the benchmark cluster

Search the last 24 months of the target venues (and the venue one tier up) for three overlapping clusters:

1. **Same family**: same technique × same task (the direct competitors).
2. **Adjacent techniques**: competing methods on the same task (the reviewers' alternative explanations).
3. **Adjacent tasks**: same technique on neighboring tasks (the migration risk).

Aim to build 8–12 paper cards: title, venue, year, official/arXiv link, code availability, one-sentence story. Every card needs a real, checked link; an unverifiable card is dropped, not guessed. If fewer than eight relevant verified papers exist, document the search coverage and the shortfall, use the verified papers without padding, and record whether the remaining evidence supports each gate; block the affected gate when it does not.

## L2 Deconstruct the narrative skeleton

For each card extract the five-beat skeleton:

| Beat | Question |
|---|---|
| Problem | What deployment or scientific driver opens the paper? |
| Gap | Which specific assumption of prior work is shown to fail, and how (a "debunking" experiment, a complexity argument, a use case)? |
| Insight | What one-sentence mechanism turns the gap into an opportunity? |
| Mechanism | What exactly is built, and what is the falsifiable prediction? |
| Evidence chain | Which experiments exist solely to rule out the reviewers' favorite alternative explanation? |

Cross-paper moves worth distilling: where the "aha" is placed (abstract figure / intro figure / theorem), how the strongest prior work is pre-empted (positioned in the intro, not the related work), and whether the paper opens by debunking prior evaluation or prior methods — the dominant 2024–2026 opening pattern in several ML families.

## L3 Deconstruct the experiment matrix

For the family, list the mandatory table/figure set:

- **Headline table**: rows × what tiers of baselines (simple / strong-recent / domain / oracle), columns × which metrics with what uncertainty statement (SD vs 95% CI, per-seed scatter vs bar).
- **Mechanism ablations**: one-factor-at-a-time, each main claim mapped to at least one ablation row, crippled-variant positive controls included.
- **Efficiency block**: the community's accounting convention (op-count formulas with cited constants, SynOps-style proxies with stated limits, throughput/latency with measurement protocol), plus the tradeoff curve with named operating points — never a single (cost, quality) point.
- **Robustness block**: intensity sweeps (not single perturbation points) across feature / structure / time axes; for temporal data, time-sliced evaluation exposing drift.
- **Statistics**: seed count justified by the effect size at stake (small effects need 8–10 paired seeds, not 3–5), paired designs preferred, bootstrap CIs, multiple-comparison correction, effect sizes reported alongside p-values.

## L4 Deconstruct execution details

Extract the unglamorous conventions that reviewers nonetheless check: splits frozen before tuning, seed policy, query/negative-sampling protocol, hardware and timing measurement protocol, variance reporting type, code release form, checklist usage.

## L5 Gap analysis against the user's project

Map the user's current story, matrix and execution against L2–L4. Output exactly three lists:

- **Fatal gaps**: a skeptical top-venue reviewer can reject on these; must be fixed in the contract.
- **Credibility gaps**: not fatal, but their absence reads as junior work; fix if budget allows.
- **Advantages**: things the project already does better than the family standard (keep and surface them).

Rank fixes by (reviewer risk × local feasibility). Each fix becomes either a new binding experiment row or a manuscript requirement — never an unmeasured claim.

## L6 Pre-register the upgraded contract

Convert the ranked fixes into a versioned guidance contract (new contract version; prior versions preserved as evidence). Rules:

- Every new binding target keeps the same discipline as any `expected_strong`: mechanism-supported, baseline-calibrated, compute-bounded, with a falsifying ablation and a stop-and-return condition.
- Adding seeds or analyses to resolve a boundary case (e.g., an inconclusive significance test) is a legitimate pre-registered extension — provided the decision rule is fixed before the new evidence is inspected, and provided no earlier failed criterion is silently deleted.
- Manuscript requirements from L2 (narrative moves, debunking opening, positioning table) are written into the guidance's story section so `f-research-v1` P6+ can enforce them.
- Nothing learned in L1–L5 may weaken an existing binding target; depth is added, never traded away.

## Artifact contract

For a fresh build, archive these files under the paper-title run root at `ccfa-startup-packet/top-venue-study/`:

- `top-venue-study/paper-cards.md` — the L1 cards with links.
- `top-venue-study/narrative-moves.md` — the L2 skeletons and cross-paper moves.
- `top-venue-study/experiment-matrix-template.md` — the L3 family matrix.
- `top-venue-study/execution-conventions.md` — the L4 conventions.
- `top-venue-study/gap-analysis.md` — the L5 three lists with ranking.
- `top-venue-study/contract-delta.md` — the L6 changes, each traced to a gap row.

For an existing run, preserve prior versions and put the new guidance, amendment, and `top-venue-study/` together under `revisions/vN/` within the original paper-title run root. Reference the study from the amendment and startup packet. For this revision, reopen at `CCFA-startup` because L6 changes startup claim/evidence planning; reaccept all downstream gates in order and reuse applicable immutable evidence only after checking it. If the execution contract itself changes, record a new immutable version and likewise restart from the first stage. Do not overwrite accepted evidence. For a fresh build, incorporate L6 into the initial guidance and startup evidence; if the immutable execution contract itself changes, version it and reopen as that contract requires.
