# Q2+ Guidance Standard

Use this reference to decide whether a generated guidance file is strong enough to hand off to `f-research-v1`.

## Minimum Bar

The project should be plausible for a Q2-or-better journal only if the guidance file contains:

- A specific research gap, not just a new combination of method and dataset.
- A mechanism-level contribution or adaptation.
- At least one directly public dataset and a reproducible evaluation protocol.
- Strong baselines, including recent and domain-standard methods.
- A recent-literature baseline matrix that separates direct rerun/adaptation baselines from literature-only context.
- A mechanism-level theoretical feasibility audit with explicit assumptions and falsifying ablations.
- A story-strength audit that explains why the project is not merely an incremental dataset application.
- Ablations tied to the proposed mechanism.
- Statistical checks or repeat runs where appropriate.
- Error analysis, robustness analysis, or subgroup analysis when relevant.
- Clear limitations and threat-to-validity plan.
- A figure/table plan that supports the argument.
- Citation scope with recent work and foundational references.

## Experiment Strength

Prefer plans with:

- More than one dataset, or one dataset plus cross-domain, temporal, subgroup, robustness, or external validation.
- At least one strong recent baseline.
- For Q1/top targets, at least one strong recent authoritative baseline must be attempted directly or adapted to the same protocol before method claims are finalized. If it cannot be run, the guidance must say what evidence will replace it and why the claim is downgraded.
- Clear primary metric and secondary metrics.
- Runtime budget realistic for the user's local machine and Conda environment, using MPS/CUDA when supported; remote compute is an explicitly authorized fallback rather than the default.
- Predefined stopping criteria and failure signals.

When only one dataset is feasible, strengthen the plan with repeated seeds, robust baselines, ablations, error analysis, and careful limitations.

## Story Strength

The story should answer:

1. What real bottleneck or scientific gap matters?
2. Why does prior work fail or remain incomplete?
3. Why should this technique address that gap?
4. What experiment would make a skeptical reviewer believe the claim?
5. What negative result would limit the claim?
6. Which existing recent paper is the strongest threat to novelty, and what experiment distinguishes this work?

If these cannot be answered concretely, do not produce a final guidance file.

## Journal Tier Fit

Use conservative language. "Q2+" means the plan should support a rigorous manuscript, not guarantee acceptance. Favor fields where incremental but well-validated methodological contributions are publishable: medical imaging, remote sensing, fault diagnosis, smart grid, time-series forecasting, bioinformatics, cybersecurity, recommender systems, education analytics, environmental monitoring, and industrial AI.

Avoid overstated novelty, unsupported clinical claims, private data dependencies, experiments that cannot be independently reproduced, and guidance files that prescribe final figures before evidence exists. The guidance may define figure/table decision rules, but `f-research-v1` chooses the final mature figure set after experiments are complete.
