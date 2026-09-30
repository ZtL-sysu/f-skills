# Research Guidance File

## Title / Topic

- Working title:
- Target field:
- Target venue:

## Core Idea

Describe the proposed method, hypothesis, or contribution in concrete terms.

## Paper Story

- Opening problem:
- Why existing work is insufficient:
- Core insight:
- What evidence should convince the reader:
- Main claim:

### Writing Handoff (optional for existing guidance)

- Central scientific question and target readers:
- Domain/theory problem -> design requirement -> proposed choice:
- Contribution type (method / empirical comparison / resource trade-off / theory / other):
- planned_claim (not an observed result):
- observed_finding: pending real evidence at P5A/P6
- Writing preferences/protected ranges/declaration mode and their author source:
- Explicit author or current journal length/citation constraints and sources:
- Update the narrative from accepted observations at P5A/P6; do not promote the plan to a finding.

## Paper Outline

1. Introduction:
2. Related Work:
3. Method:
4. Experiments and Results:
5. Discussion:
6. Conclusion:

## Experiment Plan

### Datasets

- Dataset:
- Source/access:
- Preprocessing:
- Splits:

### Baselines

- Baseline 1:
- Baseline 2:
- Strongest expected comparison:

### Proposed Method Variants

- Main method:
- Variant A:
- Variant B:

### Metrics

- Primary metric:
- Secondary metrics:
- Statistical test / confidence reporting:

## Expected Results

- Minimum acceptable result:
- Strong result:
- Failure signal:
- Strong-result entry gate for paper writing:

### Required Ablations

- Ablation 1:
- Ablation 2:
- Ablation 3:

### Runtime / Hardware Budget

- Experiment machine: local machine by default
- Conda environment:
- Accelerator: prefer Apple MPS or local CUDA when supported; record CPU fallback
- Optional remote fallback: disabled unless explicitly requested or authorized
- Credential handling: do not write SSH passwords, tokens, or endpoints with embedded credentials into project files
- GPU/CPU:
- Max runtime per run:
- Max total runs:
- Frozen train/validation/test protocol and split identifiers:
- Validation-only selection policy and final test isolation:
- Trial ledger and total search-budget limit:
- Claim-level feasibility contract and CCFA packet path:

## Figure and Table Plan

- Optional framework/architecture figure, if useful after method finalization; use the actual method and scientific labels:
- Data visualization Figure 2:
- Main result table:
- Ablation table:
- Robustness/error-analysis figure or table:
- Efficiency/resource figure or table:

### Evidence-Driven Figure/Table Decisions

Use visuals when they help readers evaluate a claim or inspect a result. No fixed count or per-subsection requirement applies; decide final artifacts after evidence stabilizes. Cite each selected artifact where its evidence is first discussed.

| Scientific question/claim | Candidate visual if useful | Evidence source | Decision after results |
|---|---|---|---|
|  |  |  |  |

## Traceability Checklist

List every required experiment and artifact so the workflow can verify coverage during experiments and after writing.

| Requirement | Dataset | Baseline/method/ablation | Metric | Minimum result | Strong result | Planned figure/table | Must appear in paper? |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Citation Scope

- Must-cite papers:
- Search keywords:
- Target recency:
- Excluded areas:
- Known arXiv/preprint vs published-version duplicate risks:
- Duplicate handling preference:

## Constraints and Preferences

- Things the workflow must do:
- Things the workflow must avoid:
- Preferred writing language:
- Preferred LaTeX/template/venue style:
- Local artifact policy: all process files and final deliverables must be stored under a run folder inside the directory containing this guidance file.
- Page policy: current target-journal limits and explicit author preference; if neither is specified, use a length proportionate to the evidence and scope, with no page-count target.
