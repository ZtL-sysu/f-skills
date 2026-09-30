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
7. `Figure and Table Plan` or `Figure/Table Decision Rules`: retain the heading with evidence-driven guidance for selecting useful figures/tables. Do not require an artifact for every subsection or a fixed count; choose visuals after evidence stabilizes.
8. `Citation Scope`: keywords, must-cite papers, venue/domain boundaries, citation recency expectations, and any known preprint/published-version duplicate risks.
9. `Constraints and Preferences`: preferred writing language, preferred template or venue style, page policy, and any user-specific constraints. The local artifact root is always derived from the guidance file location even if this section omits it.

## Blocking Gaps

Complete missing elements from available evidence within authorized scope before execution; request only material missing choices. The required elements are:

- No testable method or hypothesis.
- No datasets or no feasible substitute dataset strategy.
- No baseline or comparison class.
- No primary metric.
- No expected result or success criterion.
- No strong expected result for the main claim.
- No story/outline for the manuscript.
- No strong baseline plan when recent authoritative baselines exist.
- No theory/feasibility reasoning for why the method should work.


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
result_subsection_visual_requirements: optional_legacy_author_requirement
experiment_traceability:
citation_requirements:
citation_dedup_requirements:
local_artifact_policy:
page_length_policy:
single_final_pdf_template_policy:
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

Default extraction values:

- `local_artifact_policy`: all local process files and deliverables under a run root inside the directory containing the guidance file.
- `page_length_policy`: current target-journal limits and explicit author requirements; otherwise proportionate to the research question and evidence, with no default page threshold.
- `single_final_pdf_template_policy`: produce exactly one final compiled PDF using the current target-journal template where specified; journal limits govern; no default page target applies.

## Traceability Requirements

Convert the experiment plan into checkable rows before running experiments:

| Guidance requirement | Required artifact | Minimum success check | Strong success check | Planned figure/table | Must appear in paper? |
|---|---|---|---|---|---|

Include every required experiment and material figure/table decision rule. Subsection-to-artifact mappings are optional and evidence-driven. This table seeds experiment traceability and the paper-guidance audit; figure insertion is audited only for selected artifacts.

## Integrity Rule

The expected results guide optimization, not reporting. If the method cannot reach the strong expected target after serious iteration, preserve the best honest result and the failure analysis, but do not enter writing until correction under `research-recovery.md` yields a versioned contract and evidence passing all required gates; obtain new authorization only for a material scope expansion. Never invent numbers, hide failed runs, or present simulated placeholders as experiments.

## Optional writing handoff and legacy guidance

The central question, reader, domain/theory bridge, contribution type, planned claim, observed finding, author protections and sourced writing preferences are light handoff fields. If absent in legacy guidance, recover them at P6 from real accepted inputs; never mark stages passed or upgrade expectations to observations. Preserve explicitly accepted author quantity constraints and their provenance.
