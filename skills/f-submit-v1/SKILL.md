---
name: f-submit-v1
description: Use when a finished manuscript or source package needs journal-specific submission-readiness review, scientific/integrity audit, end-to-end selling-point and logic-closure revision, selective academic humanization, declaration routing or removal, and final package verification against recent comparable SCI literature.
---

# F Submit V1

## Overview

This is a strict pre-submission review and revision workflow for an already written paper. It does not run new experiments by default. It benchmarks the manuscript against 10 recent, similar, high-impact SCI-indexed papers, then reviews and improves each manuscript module until every module reaches the top-40% quality threshold among the comparator set.

The comparator workflow evaluates presentation quality; it must not hide scientific or evidence weaknesses. Before comparator selection, this pipeline performs an independent CCFA scientific review and integrity audit. These audits may identify missing evidence, but they do not fabricate experiments or silently turn an evidence blocker into a prose-only revision.

All local process files and final deliverables must live under the directory containing the submitted manuscript. At S0, resolve the absolute manuscript path, set `paper_dir = dirname(manuscript_file)`, and create one independent run root under it, such as `<paper_dir>/f-submit-v1-run-<YYYYMMDD-HHMMSS>-<slug>/`. Store every extraction, search record, comparator table, review matrix, revision, audit note, and final deliverable inside that run root.

The submitted manuscript and its original companion files are immutable inputs. Never edit, overwrite, rename, move, or delete the original manuscript, original PDF, original TeX project files, figures, tables, bibliography, or source package. If revision is needed, copy the minimum required source files into the run root and write revised files only there. The final revised manuscript/PDF must be delivered from the run root, not by replacing the submitted manuscript in place.

## Required Capabilities

| Phase | Required capability |
|---|---|
| Manuscript parsing | Read PDF, TeX, DOCX, or Markdown; preserve section/module boundaries and figure/table/citation references where possible |
| Web literature search | Use web search and primary/reliable sources to find current comparator papers and verify journal/index/impact evidence |
| SCI/index/impact verification | Prefer Web of Science Master Journal List, Clarivate JCR, journal official pages, publisher pages, Crossref, PubMed, Scopus, or other reliable bibliographic sources; record sources and access limitations |
| Paper quality review and revision | Use module-specific writing analysis, scientific peer-review judgment, and conservative academic editing |
| Independent scientific and evidence precheck | `ccf-paper-reviewer` in scientific mode and `ccf-integrity-auditor` in claim-audit or full mode; their reports identify scientific/evidence blockers before comparator-driven revision |
| Citation safety | Do not invent papers, impact factors, DOIs, or BibTeX; record uncertainty explicitly |
| Target-journal requirements | Inspect current official instructions, special-issue requirements, templates, and any live submission-form constraints supplied by the user |
| Narrative consistency | Build a claim spine from title through conclusion; verify that each selling point is embodied in the method, supported by results, interpreted in discussion, and recalled with honest scope |
| Professional prose audit | Use `humanizer` selectively after identifying concrete defects; preserve correct technical prose, numbers, equations, citations, and formal register |
| Declaration control | Route, retain, revise, or remove conditional declarations according to current hard requirements and explicit author choices; verify every submission surface |
| Package verification | Compile current sources, inspect the PDF, rebuild archives, and verify metadata, narrative, and declaration consistency across all deliverables |

Read `references/comparator-search-protocol.md` before searching, `references/module-quality-rubric.md` and `references/narrative-and-prose-gates.md` before scoring or revising, and `references/submission-package-gates.md` before journal adaptation or final delivery.

## Strict Pipeline

Execute this pipeline in order. Maintain `pipeline-state.md` from `assets/pipeline-state-template.md` inside the run root. Do not start a stage until the previous stage's gate is passed and recorded.

## Sequential Execution Integrity

`pipeline-state.md` is the execution authority. Its canonical order is `S0 -> S1 -> S1A -> S2 -> S3 -> S4 -> S5 -> S6 -> S7 -> S8 -> S9 -> S10`. Every stage must be recorded as `pending`, `running`, `passed`, `blocked`, or `superseded`; `skipped` is never valid.

Only a recorded `passed` predecessor authorizes the next stage. S7/S8 may iterate, but every revision and re-score must be logged. If the scientific/integrity precheck at S1A exposes a blocker, later comparator or prose work cannot bypass it; return to the earliest affected stage and re-run all dependent gates. S10 is invalid unless the state ledger proves the accepted revision passed every required stage in canonical order.

| Stage | Action | Gate to advance |
|---|---|---|
| S0 | Load the finished manuscript. Resolve `paper_dir`, create an independent run root under `paper_dir`, initialize `pipeline-state.md`, and copy or reference the original manuscript without modifying it. | Manuscript exists; run root exists under `paper_dir`; original manuscript is preserved unchanged; no output file is placed outside the run root except read-only references to original inputs. |
| S1 | Extract manuscript structure into modules: title, abstract, keywords if present, introduction, related work/background, method, experiments/results, discussion, conclusion, limitations if present, figures/tables, and references. Initialize `narrative-consistency-map.md` from `assets/narrative-consistency-map-template.md` by recording candidate selling points and their current locations without yet repairing them. | `manuscript-module-map.md` exists and every major section is mapped; the narrative map identifies candidate primary claims and any immediately visible orphan or contradictory formulation. |
| S1A | Run `ccf-paper-reviewer` in scientific mode and `ccf-integrity-auditor` in claim-audit or full mode against the module map and supplied evidence. Record `ccfa-scientific-review.md`, `ccfa-integrity-audit.md`, and `ccfa-concern-to-action.md` inside the run root. Distinguish scientific/evidence blockers from comparator-style or prose defects. | Every major claim has a support status and every review concern has severity, evidence basis, repair owner, and unblock condition. Missing experiments, unsupported claims, unverified citations, or inconsistent numbers are `blocked-needs-author-input` unless safely resolved from existing supplied artifacts; they cannot advance as prose-only fixes. |
| S2 | Infer the paper's field, topic, method family, and audience. If a target journal/special issue or live submission form is known, verify the current official requirements and create `submission-constraints.md` plus `manuscript-metadata.md` using `references/submission-package-gates.md`. Record article type, special issue, hard field/file limits, template, anonymization, declarations, data/code prompts, publishing route, and canonical author/correspondence metadata. When the user requests adding, revising, or removing a declaration, initialize `declaration-change-record.md` from `assets/declaration-change-record-template.md`. | `submission-profile.md` exists; every current requirement and canonical metadata item has a source/status. A requested declaration change has user authorization, an official requirement classification, and an artifact inventory; an unresolved mandatory-versus-remove conflict is blocked rather than guessed. |
| S3 | Search the web for candidate similar papers published close to the current date. Prefer the last 3 years; allow up to 5 years when the field has sparse recent SCI literature. | At least 20 candidate papers are recorded with URLs, years, journals, and relevance notes. |
| S4 | Verify and select exactly 10 comparator papers that are similar, recent, SCI-indexed, and from high-impact journals for the field. Use `assets/comparator-literature-table-template.md`. | `comparator-literature-table.md` contains 10 accepted papers, source links, SCI/index evidence, impact evidence, and relevance rationale; no paper-identity, relevance, or index-status gap remains. Bounded impact-metric access limitations are labeled and do not become invented certainty. |
| S5 | Build a section-pattern digest for the 10 comparators. For each module, summarize how strong papers structure claims, evidence, transitions, figures/tables, limitations, and conclusions. | `comparator-section-patterns.md` covers every manuscript module to be reviewed. |
| S6 | Score the user's manuscript module by module against the 10 comparators using `references/module-quality-rubric.md`. Run the narrative-spine, limitation-placement, and section-by-section prose scans in `references/narrative-and-prose-gates.md`. Treat orphan selling points, broken gap-to-evidence links, conclusion-only claims, unexplained results, project-process narration, templated AI-like prose, and repeated defensive disclaimers as blockers even if numeric scores pass. | `module-quality-review.md` and `narrative-consistency-map.md` record every module score, selling-point link, callback status, professionalism finding, limitation classification, and humanizer decision (`no defect` or a named passage-level defect). |
| S7 | Revise every failed or blocked module using comparator patterns without copying their text. Preserve actual science, claims, numbers, citations, and author intent. Close each selling-point chain across title/abstract/introduction/method/results/discussion/conclusion. Consolidate legitimate limitations in Discussion/Limitations as `evidence boundary -> practical consequence -> testable future work`; rewrite defensive rhetoric elsewhere as direct evidence-led prose unless a logged immediate factual qualification prevents a false claim. Apply `humanizer` only to named passages and record preserved technical anchors plus post-edit checks. Write all revised artifacts inside the run root only. | The revised draft, narrative map, limitation-placement ledger, humanizer audit, and `revision-log.md` exist; every edit has a named defect or closure gap and a factual-integrity check. |
| S8 | Re-score the revised modules and re-run the narrative, limitation, and humanizer gates. Iterate S7/S8 until every module passes or a genuine evidence item is blocked for author input. | Every module passes; each primary selling point has a complete and non-contradictory chain; no orphan contribution/result/conclusion claim remains; every out-of-Limitations caveat has a logged necessity; post-humanizer claim strength and technical anchors are unchanged. |
| S9 | Run the journal-specific final audit in `references/submission-package-gates.md`: exact limits, claim support, narrative closure, professional tone, limitation placement, selective-humanization traceability, figure/table/citation integrity, metadata, declaration routing or authorized removal, publishing route, and source-PDF-package consistency. Recompile after every accepted change; rebuild and clean-test the source archive. | `final-submission-audit.md` has no unresolved major issue; narrative and declaration records pass; constrained fields pass exact counts; TeX/PDF/title page/cover letter/standalone files/source ZIP/portal draft agree; clean extraction compiles to a semantically equivalent manuscript. |
| S10 | Deliver final artifacts and a file-to-upload map from the run root. | Delivery includes the revised manuscript/PDF, current source archive, required journal files, constraints and metadata, upload and module maps, comparator artifacts, `narrative-consistency-map.md`, module review, revision log, final audit, declaration-change record when applicable, and verification evidence. Report the preserved original separately. No upload or submission occurs without explicit instruction. |

## Non-Negotiable Rules

- Preserve the original submission exactly. Treat the input manuscript and its source package as read-only. Do not edit in place, overwrite compiled PDFs in the original folder, clean build artifacts from the original package, or copy revised content back over the submitted files.
- Put all revised outputs in an independent run folder under `paper_dir`. If path length or filesystem limits make the preferred long run-root name unsafe, create a shorter uniquely named run root under the same `paper_dir` and record the deviation in `pipeline-state.md`; do not fall back to editing the original location.
- Before S7 revisions, copy the files needed to compile or package the revision into the run root and edit only those copies. Keep an original snapshot or reference in `run_root/sources/`.
- Use current web search during S3/S4. Do not rely on memory for journal status, impact factor, publication year, or indexing status.
- Select exactly 10 comparator papers unless fewer than 10 can be verified after serious search; if fewer than 10 are possible, stop and ask the user whether to broaden topic, year range, or journal scope.
- Comparator papers must be close to the submitted manuscript's topic, method family, or application domain. High impact alone is not enough.
- SCI-indexed status and impact evidence must be sourced. If direct JCR/SCI confirmation is inaccessible, record the best available evidence and uncertainty; if that evidence is insufficient to verify index status, reject the comparator or stop rather than counting it among the 10.
- "High impact" is field-relative. Prefer journals in the top quartile or clearly high impact for the manuscript's domain; record the impact metric source and year.
- "Recent" defaults to publication years within 3 years of the current date. Use 5 years only when justified by field sparsity or very close topical match.
- Review from abstract through conclusion. Do not skip weak modules because the overall paper seems good.
- Define the paper's primary selling point in one precise sentence and maintain a traceable chain: `problem/gap -> insight -> method/design embodiment -> evidence -> interpretation -> bounded conclusion`. Repair or remove every orphan, contradiction, and late-added conclusion claim.
- The top-40% threshold is module-specific: compare abstract to abstracts, introduction to introductions, method to methods, and so on.
- If a module fails, revise it using comparator writing patterns, not copied text. Do not plagiarize, paraphrase too closely, or transplant unsupported claims.
- Preserve factual integrity. Do not invent experiments, results, datasets, citations, limitations, or journal metrics.
- Treat S1A evidence blockers as higher priority than comparator-style findings. Do not revise an unsupported scientific claim into more persuasive prose; remove, narrow, or block it until the author supplies real evidence.
- Keep defensive rhetoric out of the full manuscript. Consolidate legitimate scope limits in Discussion/Limitations, preferably as `evidence boundary -> practical consequence -> testable future work`. Outside that module, retain only immediate factual qualifications needed to keep a nearby claim true, and log the reason.
- Do not use limitation placement or future-work framing to conceal a material weakness. Any limitation that changes the validity, interpretation, generalizability, reproducibility, or safety of a main claim must be explicit, evidence-grounded, and reflected in the affected claim as well as in Discussion/Limitations.
- A professional manuscript reports scientific methods and evidence, not the mechanics of producing the paper. Remove JSON/CSV plotting workflow, reference-retrieval/BibTeX/Crossref workflow, packaging instructions, internal audit narration, and non-scientific bug-fix chronology from the manuscript body; keep them in external records when useful.
- Do not address the journal, editor, reviewer, or manuscript-building process inside the scientific narrative. Replace journal-facing self-commentary, rhetorical questions, conversational verdicts, slogan-like contrasts, and repeated defensive limitations with direct evidence-led statements and consolidated applicability boundaries.
- Inspect every scientific module for concrete AI-like prose defects before using `humanizer`. Record `no defect` when none exists. Every rewrite needs a named passage-level defect and a post-edit check for terminology, equations, numbers, units, citations, figure/table references, claim strength, and academic register.
- Current hard portal/journal limits govern submission fields and files. A user preference cannot relax a hard maximum or eligibility rule; user choices govern optional wording, declarations, and publishing route within those limits.
- Maintain one canonical metadata record and synchronize title, author order, affiliations, corresponding-author order and emails, abstract, keywords, highlights, funding, acknowledgments, data/code availability, and declaration status across every manuscript and submission artifact.
- Treat data availability, code availability, competing-interest, funding, and generative-AI statements as routed journal elements, not boilerplate. If the user explicitly requests removal of a generative-AI declaration and current authoritative instructions make it optional or inapplicable, remove it from every submission-facing manuscript, PDF, source archive, cover letter, standalone statement, metadata record, upload map, and portal-answer draft, then verify absence. If current rules make disclosure mandatory, do not conceal the use or fabricate a negative answer; record the conflict and request author direction. Never imply that code is public merely because the dataset is public.
- If the user requires zero APC, prepare and label only a subscription/traditional route where the current journal actually offers one; do not select open access or imply that optional OA is free. Do not make the final external publishing choice without authorization.
- Rebuild every stale PDF, title page, cover letter, source ZIP, and nested delivery package after a prose or metadata change. Clean-extract and compile the source ZIP before declaring the package ready.
- Do not submit, upload, email, or publish the paper. This skill produces a submission-ready revision package only.
- Never skip, reorder, or silently infer a submission stage. Record every S7/S8 iteration and any back-edge in `pipeline-state.md` before proceeding.

## Detailed References

- `references/comparator-search-protocol.md`: how to search, verify, rank, and select the 10 SCI high-impact comparators.
- `references/module-quality-rubric.md`: scoring rubric, top-40% threshold, pass/fail logic, and revision rules.
- `references/submission-package-gates.md`: target-journal constraints, professionalism, metadata, declarations, publishing route, and package-integrity gates.
- `references/narrative-and-prose-gates.md`: selling-point spine, callback closure, limitation-placement ledger, and selective-humanization audit.
- `assets/pipeline-state-template.md`: stage-by-stage state file.
- `assets/comparator-literature-table-template.md`: table for accepted/rejected comparator evidence.
- `assets/module-quality-review-template.md`: module scoring and pass/fail matrix.
- `assets/revision-log-template.md`: traceable revision log.
- `assets/narrative-consistency-map-template.md`: end-to-end selling-point and callback ledger.
- `assets/declaration-change-record-template.md`: authorization, requirement, artifact, and absence/presence verification for declaration changes.
