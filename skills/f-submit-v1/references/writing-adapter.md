# Bounded writing input and current-text verification

Load for P6/P7/P10/P19 (and later prose-changing exports), or S7–S9. `scientific-writing-contract.md` is authoritative. `writing-examples.md` is optional for matching defects. Keep the existing narrative map and revision log; do not produce parallel audit books.

## Build the actual input

1. In the accepted run root, populate `assets/scientific-content-packet-template.json` from the existing evidence/narrative maps. Required question/audience/section jobs can be recovered in P6 for old guidance; their absence in old guidance is not a failed prior stage. Expected claims stay planned until supported. Include negative findings and material validity disclosures. Evidence entries are relative snapshot paths and SHA-256s, not instructions to paste logs into the paper.
2. The packet schema rejects administrative fields inside facts/brief. Top-level `internal` may retain operation notes but is never sent. Before building, read every `statement`: a reference fact contains the source's supported scientific proposition and citation identity. Put inaccessible-full-text notes and search coverage in `internal`; they are neither scientific gaps nor evidence for novelty. Omit a citation with no needed verified proposition. Human extraction must check free-text meaning: a whitelist cannot discover every disguised process sentence. `observed_verified` is a reviewer assertion requiring real verification, never bestowed by hashing a file.
3. Build one task with the installed skill's script, inside local Conda:

```text
conda run -n <env> python <skill-dir>/scripts/writing_adapter.py --packet <run-root>/writing/packet.json --run-root <run-root> --stage P7 --section-task "Draft Results around the main comparison; keep negative findings and uncertainty" --subskill ml-paper-writing --output <run-root>/writing/request-v1.json
```

For P6 change stage/task to outlining. For P10/S7 also pass `--manuscript <current-copy>` and `--edits <decisions.json>`. Each decision has `proposition`, `evidence_status`, `action`, `location`, `factual_check`; the external revision log retains reviewer concern/rationale. BLOCK_EVIDENCE prevents a rewrite request. P19 uses `--subskill humanizer` with the named local defect. Do not use sentence refiners to bypass structural work.

Use `--section-role abstract|introduction|methods|results|discussion|conclusion|local-revision` for a concrete section job. After generation, repeat the input arguments with `--response <response.json>` and a new output path to check the manuscript/notes separation; an all-KEEP edit list must return the exact original text. This validates format and KEEP integrity, not scientific semantics. Insert only the returned `manuscript` after the required current-text review.

A current-manuscript P10/S7/P19 request requires edit decisions. In `factual_check`, enumerate source propositions that the replacement must preserve, particularly measurement exclusions and unresolved attribution; encode high-risk relationships as lint assertions when practical. A MOVE must name a verified destination. A successful input build does not discharge these output checks.

For mixed KEEP/REWRITE decisions, each KEEP also supplies `protected_text`, an exact unique source span. Response validation rejects changed or duplicated spans. Results tasks need reported/verified structured result facts; a theoretical paper may set `brief.study_type: theoretical` and supply supported propositions/proof evidence. A plan alone cannot satisfy either route. Lint freshness also binds its checker, adapter, contract and, for submit, local rubric versions; old reports lacking these versions require rechecking.

Only `request["messages"]` is writer context. `provenance` remains external: evidence links, resolved installed-first/bundled dependency path and hash, contract hash and execution identity. Send the system contract at its declared priority and the subordinate advice below it. Record the actual executor/model/tool version and settings from the executing tool response, or `unknown`; the builder itself invokes nothing and knows no model. Do not blindly serialize the whole request to a writer. Both skills contain the same builder/contract, so isolated installs work; an unavailable optional subskill is recorded as such, not simulated.

The writer returns separate `manuscript` and `notes` fields. Validate before inserting only `manuscript` into the working copy. Notes carry the reverse outline/changes and never enter TeX. This is a local exchange format, not a claim about an external vendor's API fields. If the tool has only plain-text input/output, preserve the separation in the caller and inspect its actual prompt/output.

## Paragraph inputs for structural repair

`attribution` names the scientific source or origin of a proposition. Per-fact `verification_note` records how it was checked, access depth, and retrieval details; the adapter moves this field into external provenance. Keep those details out of `attribution` and `statement`. Citation identity and the proposition actually supported remain in the scientific input.

A reported/verified reference also needs `citation` with `authors`, `title`, `year`, and `url` (DOI URL is sufficient; optional bibliographic fields may accompany them). Extract publication metadata rather than copying registry annotations: for example, a known arXiv version belongs in the citation, while “conference status not independently verified” belongs in `verification_note`, not `venue`. Recover missing metadata before drafting; do not give a writer an author/year fragment and ask it to invent a reference entry. This is a completeness check, not source verification. Preserve LaTeX backslashes when saving native responses: programming-language `\a`, `\r`, or `\t` escapes can corrupt `\alpha`, `\rho`, or `\tfrac`. The format checker rejects unexpected control characters, but a compile and current rendered-text inspection remain necessary to find stripped commands or broken inline math.

When a draft repeats boundaries or several paragraphs perform the same job, replace the affected part of the existing reverse outline with `brief.paragraph_plan`. Each move has `id`, `section`, `point` (the scientific proposition), `fact_ids` (packet evidence IDs), and `adds` (what this move adds to the argument). These are scientific tasks, not reviewer complaints. The adapter checks references and sends an explicit composition task; the writer maps actual paragraphs back to moves in separate notes. Combine moves naturally; this is not a prescribed paragraph count.

Use `brief.qualification_placement` for repeated material conditions: each row has `fact_id`, `home` (where it is defined fully), and `repeat_when` (when a local claim needs the condition). A fixed conditional-loss assumption belongs in Formal Setup and locally qualifies transfer to a population; it does not need three consecutive disclaimers in Discussion. A measurement exclusion may belong in Methods while a table caption needs a short scope label. Never remove a validity condition to satisfy a placement plan. Both fields are optional for legacy packets and simple edits; use them for new full-article drafts and diagnosed structural revisions.

At review, compare actual paragraph roles to the plan itself, not only the writer's notes. An added scope inventory can duplicate setup even when the notes say “no deviations.” Accept an extra move only when it adds a needed scientific point; otherwise merge it into its qualification home while retaining any locally necessary conditions. Record human structural corrections as corrections, not as an unchanged-model success.

For reviewer-triggered rewrites, add `composition` to each changing edit: `point` is the positive scientific proposition to develop, `fact_ids` identify its supporting packet facts, and `preserve` lists the scientific relations/conditions the output must retain. The adapter then sends these items instead of the concern wording and `factual_check`; the original concern and check remain in `provenance.revision_checks` for post-output verification. Thus “interpret effective weights after rescaling” reaches the writer, while “do not overclaim that every correction is impossible” remains an audit test. Include any material qualifier positively in `preserve`, such as “original weights are held fixed.” KEEP spans remain byte-exact. Legacy edit lists still build, but use this composed form for new concern-driven repairs; never copy a warning into `point` merely to satisfy the schema.

## AutoResearchClaw boundary

Do not assume a template override isolates inputs. Inspect the installed version, stage enum, context helpers, prompt manager and execution configuration before calling. Historical 0.5.0 source inspected during this migration uses `_execute_paper_outline` / `_execute_paper_draft` in `pipeline/stage_impls/_paper_writing.py` and revision in `_review_publish.py`; these add analysis/decision/history and raw experiment metrics beyond their declared file inputs. Stage 16/17/19 mappings remain P6/P7/P10, but that version has no verified clean-packet CLI option.

The builder is a usable prompt-input adapter for a writer that accepts explicit context, not an installed ARC patch. Before ARC can execute these stages compliantly, its actual call boundary must consume `messages` exclusively (plus the authorized current draft/scientific edit decisions), bypass historical context collectors, and pass a captured-context isolation test. Keep required ARC stages pending/blocked until verified; do not credit a direct writer or simulated call as ARC stage execution. The repository has no ARC executor source; do not edit unrelated historical project clones or invent flags. No automated training, paid probe or global model change is part of compatibility inspection.

## Check current text and author protections

Run `manuscript_lint.py --run-root <root> --manuscript <working-copy> --policy <policy.json> --labels <visible-labels.json> --bind <current.pdf> --bind <source-table> --report <new-report.json>`. Omit unavailable optional paths and mark those checks pending. `--check-current <report.json> --run-root <root>` rejects changed dependencies. Include that report and all accepted text/source/PDF/package dependencies in the existing pipeline-state evidence. Reopen the earliest affected writing stage after a change; never rerun valid experiments just for prose edits.

Policy uses the existing execution-contract protections, serialized compactly:

```json
{
  "protected_sections": [{"baseline":"sources/original.md","baseline_sha256":"<hash>","current":"writing/revised.md","start":"## Limitations","end":"## Conclusion"}],
  "protected_artifacts": [{"path":"sources/results.csv","sha256":"<hash>"}],
  "assertions": [{"id":"model-condition-association","location_pattern":"Fusion[^\\n]+","pattern":"Fusion.*0\\.8930.*pose.*0\\.8785","forbidden":"pooled F1|equivalent"}]
}
```

Use unique exact delimiters for protection or protect the whole file. Original manuscript/source package remains read-only outside the revision run. Snapshot author metadata/results and hash them before editing; verify the originals separately as well. Assertions must encode model/condition/direction/aggregation/uncertainty relationships supplied by the fact reviewer; matching all numbers is inadequate. Regex assertions are targeted guards, not a general factual entailment system. A whole-paper read must still verify evidence states, causal scope, core callbacks and paragraph roles.

Lint reports rule ID, file/line, original text, type and proposed action. Candidates require judgment; `not`, `pipeline`, `frozen`, tool names and formal disclosures are not automatically deleted. It follows literal TeX input/include within the run root, skips comments/code/bibliography and marks declaration candidates separately, but does not expand macros or OCR figures. Inspect rendered text, captions and pixels; label lists alone do not verify an image. Hash freshness alone cannot prove that a PDF was built from the bound source: compile and compare it before recording acceptance.

No candidate-free report is an automatic writing PASS. Combine the report with actual review decisions and reverse-outline findings. A stale source/figure/export invalidates the old review and downstream PDF/package acceptance, even if its old score was high.
