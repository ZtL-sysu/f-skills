# Research Guidance File

## Title / Topic

- Working title:
- Target field:
- Target journal tier:
- Candidate venues:
- Technique/method:
- Selected application scenario:

## Core Idea

Describe the proposed method, hypothesis, adaptation, or contribution in concrete terms.

### Mechanism-Level Rationale

- Domain bottleneck:
- Why the chosen technique fits:
- What must be changed or adapted:
- Why this is more than applying method X to dataset Y:

## Paper Story

- Opening problem:
- Why existing work is insufficient:
- Core insight:
- What evidence should convince the reader:
- Main claim:
- Boundary of the claim:
- Skeptical-reviewer hook:
- Strongest competing paper and why this is still distinct:

## Paper Outline

1. Introduction:
2. Related Work:
3. Method:
4. Experiments and Results:
5. Discussion:
6. Conclusion:

## Experiment Plan

### Datasets

| Dataset | Direct access URL | License/terms | Task role | Size | Labels/targets | Split strategy | Access decision |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | direct-public |

### Baselines

- Simple baseline:
- Matched internal baseline:
- Domain-standard baseline to rerun/adapt:
- Strong recent baseline to rerun/adapt:
- Strong recent baseline for literature context only:
- Technique-family baseline:
- Upper-bound or oracle-style comparison, if applicable:
- Strongest expected comparison:

### Proposed Method Variants

- Main method:
- Variant A:
- Variant B:
- Implementation notes:

### Metrics

- Primary metric:
- Secondary metrics:
- Efficiency metrics:
- Statistical test / confidence reporting:

### Required Ablations

- Ablation 1:
- Ablation 2:
- Ablation 3:
- Robustness or subgroup analysis:
- Error analysis:

### Runtime / Hardware Budget

- Local experiment machine and Conda environment:
- Optional remote fallback, only if authorized:
- GPU/CPU:
- RAM:
- Disk:
- Max runtime per run:
- Max total runs:
- Frozen train/validation/test identifiers and validation-only selection policy:
- Full search/trial ledger and held-out test isolation:
- CCFA packet path and feasibility-contract.json:
- Resource budget exhaustion and next-candidate decision rule:
- Scaling fallback:
- Stopping criteria:

## Expected Results

- Minimum acceptable result:
- Strong result:
- Failure signal:
- What to do if minimum is not reached:
- Claim adjustment rule if expectations fail:

## Figure/Table Decision Rules

Do not lock final figure/table contents before experiments are completed. Define evidence-driven decision rules instead.

- Required first figure type: GPT-generated framework/architecture figure after the method is finalized.
- Required experiment visualizations if supported by data:
- Required result tables if supported by data:
- Minimum total figures + tables expected in final paper:
- Maximum total figures + tables expected in final paper:
- Rules for excluding weak or misleading plots:
- Which claims must have a nearby figure/table:

## Traceability Checklist

| Requirement | Dataset | Baseline/method/ablation | Metric | Expected result | Planned figure/table | Must appear in paper? |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  | yes |

## Citation Scope

- Must-cite foundational papers:
- Must-cite recent papers:
- Dataset papers:
- Baseline papers:
- Search keywords:
- Target recency:
- Excluded areas:
- Minimum reference count: 36
- Recency expectation: majority from the last 3-5 years

## Novelty And Feasibility Summary

- Literature/baseline map verdict:
- Dataset access verdict:
- Task/evaluation verdict:
- Theoretical fit verdict:
- Novelty verdict:
- Hardware feasibility verdict:
- Baseline/ablation verdict:
- Effectiveness plausibility verdict:
- Q2+ story verdict:

## Theoretical Feasibility Audit

- Mechanism expected to help:
- Required assumptions:
- Supporting literature:
- Falsifying ablation:
- Critical failure mode:

## Story Strength Audit

- Why a top-journal reviewer should care:
- Strongest incrementality threat:
- Decisive distinguishing experiment:
- Strong-paper result threshold:
- Honest fallback story if only partially successful:

## Constraints and Preferences

- Things the workflow must do:
- Things the workflow must avoid:
- Preferred writing language:
- Preferred LaTeX/template/venue style:
