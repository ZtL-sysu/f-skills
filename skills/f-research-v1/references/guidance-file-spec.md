# Guidance File Specification

Use this file to decide whether the user's guidance Markdown is actionable. The guidance file is the contract for the whole run.

## Required Sections

The file must contain:  

1. `Title / Topic`: working title, target field, target venue if known.
2. `Core Idea`: the proposed method or hypothesis in concrete terms.
3. `Paper Story`: what problem the paper opens with, why prior work is insufficient, what the new insight is, and what evidence should make the reader believe it.
4. `Paper Outline`: section-level outline with planned contribution per section, using exactly these numbered main sections: `1 Introduction`, `2 Related Work`, `3 Method`, `4 Experiments and Results`, `5 Discussion`, `6 Conclusion`.
5. `Experiment Plan`: datasets, baselines, proposed method variants, ablations, metrics, expected outcomes, statistical checks, hardware/runtime budget, stopping criteria, and the complete list of experiments that must be run before writing.
6. `Expected Results`: quantitative or qualitative targets from the user. Include minimum acceptable result, strong result, and failure signal. The strong result is the default gate for entering paper writing.
7. `Figure/Table Decision Rules` or `Figure/Table Plan`: evidence-driven rules for selecting mature paper figures/tables. Every planned subsection under `4 Experiments and Results` must be mapped to at least one relevant nearby figure or table; a subsection without an artifact must be merged or removed. The guidance should not prematurely force a final figure list before experiments exist.
8. `Citation Scope`: keywords, must-cite papers, venue/domain boundaries, citation recency expectations, and any known preprint/published-version duplicate risks.
9. `Constraints and Preferences`: preferred writing language, preferred template or venue style, page policy, and any user-specific constraints. The local artifact root is always derived from the guidance file location even if this section omits it.

## Blocking Gaps

Stop and ask for a revised guidance file when any of these are missing:

- No testable method or hypothesis.
- No datasets or no feasible substitute dataset strategy.
- No baseline or comparison class.
- No primary metric.
- No expected result or success criterion.
- No strong expected result for the main claim.
- No story/outline for the manuscript.
- No strong baseline plan when recent authoritative baselines exist.
- No theory/feasibility reasoning for why the method should work.
- No figure/table mapping rule covering every planned subsection under `4 Experiments and Results`.

## Paper Outline Contract

The guidance outline and final AutoResearchClaw stage 16 outline must use exactly these top-level numbered sections:

1. `Introduction`
2. `Related Work`
3. `Method`
4. `Experiments and Results`
5. `Discussion`
6. `Conclusion`

Do not accept a guidance outline that replaces this structure with ad hoc top-level sections. If useful details such as problem formulation, experimental setup, ablations, limitations, or future work appear, keep them as subsections inside the six required sections.

If only minor details are missing, make a conservative assumption, record it in the run log, and proceed.

## Contract Extraction

Before running anything, extract a compact contract:

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
strong_result_entry_gate:
must_run_experiments:
must_have_ablations:
figure_table_decision_rules:
result_subsection_visual_requirements:
experiment_traceability:
citation_requirements:
citation_dedup_requirements:
local_artifact_policy:
page_length_policy:
single_final_pdf_template_policy:
open_assumptions:
```

Save the contract in the project artifacts so later writing, figures, and citation checks can audit against it.

Default extraction values:

- `local_artifact_policy`: all local process files and deliverables under a run root inside the directory containing the guidance file.
- `page_length_policy`: full-length manuscript more than 20 compiled PDF pages unless explicitly waived by the user.
- `single_final_pdf_template_policy`: produce exactly one final compiled PDF; use an unrestricted template when a limited venue template conflicts with the page-length policy, unless the user explicitly waives the page-length policy.

## Traceability Requirements

Convert the experiment plan into checkable rows before running experiments:

| Guidance requirement | Required artifact | Minimum success check | Strong success check | Planned figure/table | Must appear in paper? |
|---|---|---|---|---|---|

Include every dataset, baseline, method variant, ablation, metric, expected result, and figure/table decision rule. Also list every planned subsection under `4 Experiments and Results` and its required artifact. This table becomes the seed for `experiment-traceability.md`, `paper-guidance-audit.md`, and `figure-table-insertion-audit.md`.

## Integrity Rule

The expected results guide optimization, not reporting. If the method cannot reach the strong expected target after serious iteration, preserve the best honest result and the failure analysis, but do not enter paper writing until the user revises the guidance contract or authorizes a different target. Never invent numbers, hide failed runs, or present simulated placeholders as experiments.
