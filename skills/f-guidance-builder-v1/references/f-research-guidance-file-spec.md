# Guidance File Specification

Use this file to decide whether the generated guidance Markdown is actionable for `f-research-v1`. The guidance file is the contract for the whole downstream run.

## Required Sections

The file must contain:

1. `Title / Topic`: working title, target field, target venue if known.
2. `Core Idea`: the proposed method or hypothesis in concrete terms.
3. `Paper Story`: what problem the paper opens with, why prior work is insufficient, what the new insight is, and what evidence should make the reader believe it.
4. `Paper Outline`: section-level outline with planned contribution per section, using exactly these numbered main sections: `1 Introduction`, `2 Related Work`, `3 Method`, `4 Experiments and Results`, `5 Discussion`, `6 Conclusion`.
5. `Experiment Plan`: datasets, baselines, proposed method variants, ablations, metrics, expected outcomes, statistical checks, hardware/runtime budget, and stopping criteria.
6. `Expected Results`: quantitative or qualitative targets from the user or builder. Include minimum acceptable result, strong result, and failure signal.
7. `Figure and Table Plan` or `Figure/Table Decision Rules`: retain the heading; the content records evidence-driven visual decisions, including deferring selection until results; no fixed count or per-subsection artifact requirement.
8. `Citation Scope`: keywords, must-cite papers, venue/domain boundaries, and citation recency expectations suited to the field and claim.

## Blocking Gaps

Stop and revise the guidance file when any of these are missing:

- No testable method or hypothesis.
- No directly public dataset or feasible substitute dataset strategy.
- No baseline or comparison class.
- No primary metric.
- No expected result or success criterion.
- No story/outline for the manuscript.

## Paper Outline Contract

The generated guidance outline must use exactly these top-level numbered sections:

1. `Introduction`
2. `Related Work`
3. `Method`
4. `Experiments and Results`
5. `Discussion`
6. `Conclusion`

Do not replace this with ad hoc top-level sections such as `Experimental Setup`, `Results`, `Ablations`, `Analysis`, `Limitations`, or `Future Work`. If those details are needed, keep them as subsections inside the six required sections.

If only minor details are missing, make a conservative assumption, record it in the run log, and proceed. The writing handoff fields (central question/reader, problem-to-design link, contribution type, planned-claim vs observed-finding status, and author writing protections/preferences with source) are optional for legacy guidance. If absent, f-research-v1 may derive them at P6 from authorized evidence; never infer observations from planned claims or mark an unrun stage complete.

## Contract Extraction

Before running downstream experiments, extract a compact contract:

```yaml
topic:
target_venue:
main_claim:
method:
datasets:
baselines:
primary_metric:
secondary_metrics:
expected_minimum:
expected_strong:
must_run_experiments:
must_have_ablations:
figure_table_decision_rules:
experiment_traceability:
citation_requirements:
central_question:
intended_reader:
domain_design_bridge:
planned_claim:
observed_finding: unresolved_until_evidence
writing_preferences_and_source:
protected_scope_and_source:
venue_length_requirements_and_source:
open_assumptions:
```

Save the contract in the project artifacts so later writing, figures, and citation checks can audit against it.

At writing handoff, transfer the question, section purposes and material conditions; research P6 resolves them against supported facts into the writing adapter's paragraph plan and qualification placement. Guidance expectations do not become drafting evidence, and search-access limitations do not become claims that prior work is scientifically inadequate.

## Traceability Requirements

Convert the experiment plan into checkable rows before running experiments:

| Guidance requirement | Required artifact | Success check | Planned figure/table | Must appear in paper? |
|---|---|---|---|---|

Include every dataset, baseline, method variant, ablation, metric, expected result, and planned figure/table. This table becomes the seed for `experiment-traceability.md`, `paper-guidance-audit.md`, and `figure-table-insertion-audit.md`.

## Integrity Rule

The expected results guide optimization, not reporting. If the method cannot reach the expected target after serious iteration, report the best honest result, explain the gap, and adjust claims. Never invent numbers, hide failed runs, or present simulated placeholders as experiments.
