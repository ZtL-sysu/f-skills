# Fail-Fast Gates

Use these gates before producing the final guidance file. Earlier gates are intentionally more important because they are harder to repair later.

## Gate Order

### G1 Public Dataset Access

Pass only if the dataset can be obtained directly through a public path such as an official download URL, Hugging Face, Kaggle, OpenML, UCI, Zenodo, Figshare, a public benchmark site, or a GitHub release.

Reject if access requires email, manual approval, account vetting, IRB, NDA, payment, institutional membership, private cloud bucket permission, or "available on request." A normal free account for Kaggle or Hugging Face is acceptable if the dataset files are directly accessible after login and license terms allow research use.

Record:

| Dataset | Direct URL | License/terms | Size | Labels/targets | Access friction | Decision |
|---|---|---|---|---|---|---|

### G2 Task And Evaluation Validity

Pass only if the dataset supports:

- Clear input and output.
- Labels, targets, rankings, events, or measurable outcomes.
- Standard or defensible splits.
- Primary metric and secondary metrics.
- A reproducible evaluation protocol.

Reject vague exploratory ideas that cannot become a testable task.

### G3 Theoretical Fit

Pass only if there is a mechanism-level fit between technique and application. Good reasons include structural inductive bias, temporal dynamics, topology, multimodality, robustness, sample efficiency, interpretability, calibration, computational efficiency, or domain constraints.

Reject ideas whose only claim is "method X has not been tried on dataset Y."

### G4 Novelty And Non-Duplication

Search for highly similar work using combinations of technique, task, dataset, domain, and claimed contribution. A direction fails if a paper already matches most of these:

- Same or near-identical method family.
- Same application task or dataset class.
- Same central claim.
- Similar experimental protocol and conclusion.

If related papers exist but do not duplicate the core contribution, write the difference as a precise positioning statement.

### G5 Hardware And Runtime Feasibility

Estimate whether the user can run main experiments, baselines, ablations, and repeats. Account for GPU memory, CPU, RAM, disk, data size, model size, training time, and number of seeds.

If too expensive, attempt scale repair:

- Smaller model or backbone.
- Subsampled dataset with full-test evaluation.
- Frozen encoders or parameter-efficient tuning.
- Fewer but stronger ablations.
- Classical or lightweight baselines.

Reject if scaling removes the ability to support the central claim.

### G6 Baseline And Ablation Feasibility

Pass only if at least three comparison classes can be included when appropriate:

- Simple baseline.
- Strong recent baseline.
- Domain-standard baseline.
- Main method.
- At least two ablations isolating the core mechanism.

Reject if the result would be a single-model demonstration without convincing controls.

### G7 Effectiveness Plausibility

Pass if prior theory, related empirical results, pilot evidence, or task structure makes improvement plausible. The expected result can be modest, but the reason must be explicit.

Write failure signals before experimentation so `f-research-v1` can avoid moving goalposts.

### G8 Q2+ Paper Story

Pass only if the project can produce a publishable arc:

- Important practical or scientific problem.
- Specific limitation in prior work.
- Method insight that follows from the limitation.
- Experiments that test the insight, not only leaderboard performance.
- Limitations and threat-to-validity discussion.
- Reproducible artifacts.

Reject if the direction is only a demo, a thin benchmark substitution, or a dataset-only report.

## Scenario Scoring

After hard gates pass, score remaining candidates from 1-5:

| Criterion | Weight |
|---|---:|
| Dataset accessibility and quality | 5 |
| Theoretical fit | 5 |
| Novelty margin | 5 |
| Experiment feasibility | 4 |
| Baseline/ablation strength | 4 |
| Current research heat | 3 |
| Story clarity | 5 |
| Q2+ journal fit | 4 |

Choose the highest total only if G1-G4 pass.
