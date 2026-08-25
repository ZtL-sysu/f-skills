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

### Expected Results

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

## Figure and Table Plan

- Overall framework/architecture Figure 1, generated with GPT image generation (`image2`) from the user's reference-template style:
- Data visualization Figure 2:
- Main result table:
- Ablation table:
- Robustness/error-analysis figure or table:
- Efficiency/resource figure or table:

### Result Subsection Visual Rules

Every subsection under `4 Experiments and Results` must have at least one relevant nearby figure or table. Do not create a subsection without an assigned artifact; merge its material into a supported subsection or keep it in the parent-section introduction.

| Planned subsection | Scientific purpose | Required figure/table | Source experiment/artifact |
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
- Page policy: produce exactly one final compiled manuscript PDF of more than 20 pages unless explicitly waived. If the preferred venue template has a hard page limit that conflicts with this requirement, use an unrestricted manuscript template for the single final PDF unless the page requirement is explicitly waived.
