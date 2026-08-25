# Module Quality Rubric

Use this rubric in S6/S8. Score the user's manuscript and each of the 10 comparator papers module by module.

## Contents

- Modules and scoring
- Top-40% gate and failure handling
- Module-specific checks
- Selling-point and closure checks
- Professionalism override
- Blocked cases

## Modules To Review

Review every module present in the submitted manuscript, normally:

1. Title
2. Abstract
3. Keywords
4. Introduction
5. Related Work or Background
6. Method or Materials and Methods
7. Experiments, Results, or Evaluation
8. Discussion or Analysis
9. Limitations, if present or expected by the field
10. Conclusion
11. Figure/table presentation, if relevant to the module
12. Citation and reference integration

If the paper uses a nonstandard structure, map its sections to the closest modules and record the mapping in `manuscript-module-map.md`.

## Scoring

Use a 100-point module score. Adjust criteria by module, but preserve these dimensions:

| Dimension | Points |
|---|---:|
| Purpose clarity and reader orientation | 15 |
| Field-standard structure and logical flow | 10 |
| Specificity and technical precision | 15 |
| Evidence, result, or citation support | 20 |
| Comparative positioning against prior work | 10 |
| Concision and information density | 10 |
| Journal-level tone and polish | 10 |
| Selling-point consistency and narrative closure | 10 |

For title and keywords, use an adapted 100-point version emphasizing specificity, discoverability, field fit, and non-hype wording.

## Top-40% Gate

For each module:

1. Score the same module in all 10 comparator papers.
2. Sort those 10 scores from high to low.
3. Set the threshold to the 4th-highest comparator score.
4. Score the user's module.
5. Pass only if `user_module_score >= fourth_highest_comparator_score`.

This implements "quality ranks in the top 40%" without pretending the user's paper is one of the comparator papers.

The top-40% score is necessary but not sufficient. A module also fails when the narrative map shows an orphan, contradiction, missing evidence callback, or conclusion claim that was not prepared and supported earlier.

## Failure Handling

If a module fails:

- identify which dimensions caused the gap;
- extract writing patterns from the top 4 comparator modules;
- revise the user's module to match the standard of organization, specificity, evidence use, and rhetorical pacing;
- preserve all factual content unless the user authorizes scientific changes;
- mark unsupported claims for author input instead of inventing evidence.

Do not copy comparator phrasing. Use patterns, not text.

## Module-Specific Checks

### Abstract

Must state problem, gap, method, key evidence, and implication. It should include concrete results when the paper has them and avoid generic claims.

When a target journal or live form is known, the exact final plain-text abstract must also pass the current hard word/character limit. A strong abstract that cannot be pasted into the active form fails submission readiness.

### Keywords

Keywords must be specific, searchable, nonredundant, and within the current journal/form maximum. Count phrases as the portal counts them; do not preserve extra keywords merely because an older template allowed more.

### Introduction

Must create a clear problem-to-gap-to-contribution chain, position against current literature, and preview evidence without overclaiming.

### Related Work / Background

Must group literature by theme, show what prior work cannot solve, and lead directly to the manuscript's contribution.

### Method

Must be reproducible enough for the target field: inputs, assumptions, model/design, algorithm/procedure, parameters, and implementation details.

### Experiments / Results

Must connect datasets, baselines, metrics, main results, ablations, uncertainty/statistics, and figure/table interpretation. Results should not be only descriptive if the field expects quantitative comparison.

### Discussion

Must interpret why results occur, compare with literature, discuss scope and limitations, and avoid simply repeating the results.

### Conclusion

Must summarize contribution and evidence with honest scope. It should not introduce new results or unsupported future claims.

## Selling-Point And Closure Checks

Build `narrative-consistency-map.md` with `assets/narrative-consistency-map-template.md`. For every primary selling point, verify:

1. the title and abstract frame the same contribution at compatible strength;
2. the Introduction states the gap and contribution without adding a second competing thesis;
3. the Method or study design operationalizes the promised mechanism or test;
4. the Results provide identifiable evidence for the claim rather than unrelated metric inventory;
5. the Discussion explains the evidence, compares it with prior work, and states its consequence;
6. the Conclusion recalls the same claim and evidence boundary without new results;
7. figures and tables support, rather than compete with, the narrative spine.

Flag contribution bullets with no result, result subsections unused in Discussion/Conclusion, conclusions absent from the Introduction, and shifts in task/method/population/causal strength. A single central selling point may have supporting subclaims, but they must remain subordinate and traceable.

## Professionalism Override

A module cannot pass on score alone while it contains any of the following:

- manuscript-production narration such as data-export, plotting, reference-retrieval, audit, or packaging workflow;
- non-scientific debugging chronology or statements about corrected bugs;
- language addressed to the journal, editor, reviewer, or the paper-building process;
- conversational comparisons, rhetorical self-questioning, slogan-like contrast, or repeated templated transitions;
- repeated defensive negation where one precise evidence boundary would suffice;
- a substantive caveat placed outside Discussion/Limitations without a logged claim-preserving necessity;
- an orphan selling point, unsupported narrative callback, or conclusion-only claim;
- unsupported claims about trust, reproducibility, novelty, superiority, efficiency, or deployment.

Inspect every module and record either `no concrete defect` or the exact flagged passage and defect class. Name the defect, revise only the affected passage, and re-score. After humanization, verify scientific facts, numbers, equations, citations, claim strength, and formal academic register.

## Blocked Cases

Mark `blocked-needs-author-input` when a module cannot be improved to threshold because:

- evidence is missing;
- experiments/results are absent or internally inconsistent;
- claims exceed the data;
- essential citations are unavailable;
- journal-specific requirements are unknown and materially affect structure.
