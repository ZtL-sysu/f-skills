# Paper Production Gates

Use these gates after the direct experiment phase is complete and before or during the individually gated writing/export stages. The paper-writing handoff is allowed only after every guidance-required experiment is complete and the strong expected results are met for the main claims.

## Gate -1: Guidance-Directory Artifact Boundary

Before any paper-production work, verify the P0 artifact boundary:

- `guidance_file` is an absolute path to the user-provided guidance Markdown file;
- `guidance_dir` is the directory containing that file;
- `run_root` is a child directory of `guidance_dir`;
- `pipeline-state.md`, `artifact-manifest.json`, `experiment-traceability.md`, `experiment-completion-lock.md`, paper drafts, TeX exports, figures, audit files, and final delivery bundles are created or copied under `run_root`.

This gate fails if final or process files are left only in a global AutoResearchClaw artifact directory, an `auto-paper` directory outside `guidance_dir`, a temp directory, downloads, desktop, or the shell's current working directory. External paths may appear in the manifest only as explicitly authorized execution sources or tool-cache sources, and the accepted artifact must have a run-root copy.

## Gate 0: Pre-Writing Experiment Lock

Before starting f-research-v1 P6 / AutoResearchClaw stage 16, create or update `experiment-completion-lock.md` from `assets/experiment-completion-lock-template.md`:

| Guidance experiment | Required evidence | Strong expected result | Actual result | Status | Blocking issue |
|---|---|---|---|---|---|

Allowed statuses: `strong-pass`, `needs-rerun`, `missing`, `blocked-needs-user-guidance-revision`.

This gate passes only when:

- every dataset, baseline, method variant, ablation, metric, statistical check, robustness/efficiency check, and required result artifact from the guidance file is complete;
- the strongest feasible baseline has been run, or a versioned guidance revision under `research-recovery.md` has accepted a documented substitute after renewed feasibility/review gates;
- the guidance's `expected_strong` target is met for the paper's main claims;
- raw logs, configs, seeds, metrics, environment records, and analysis notes exist for audit and replots.

If a required experiment is infeasible or the strong target cannot be reached, enter `research-recovery.md` correction before writing. Redesign within authorized scope, preserve negative evidence, and ask only for an out-of-scope change; do not lower the failed target to pass.

## Gate 1: Evidence-to-Claim

Before drafting, create a claim table and check it against the original guidance file:

| Claim | Evidence | Figure/Table | Citation support | Risk |
|---|---|---|---|---|

Claims that lack experiment or citation support must trigger an experiment repair, citation repair, or versioned guidance revision under `research-recovery.md`. Do not silently drop or weaken claims to bypass the strong-result lock.

Also create or update `paper-guidance-audit.md`:

| Guidance requirement | Paper location | Evidence/artifact | Status | Fix needed |
|---|---|---|---|---|

Allowed statuses: `covered`, `partially-covered-needs-repair`, `missing`, `blocked-needs-user-guidance-revision`.

## Gate 2: Manuscript Draft

Use AutoResearchClaw's writing stages as the main draft-and-review engine, but expose each called stage as a separate f-research-v1 pipeline stage. Earlier AutoResearchClaw stages are skipped because the guidance file and direct experiment phase already provide the topic, plan, evidence, and analysis. The writing/review/export/citation core must remain:

| f-research-v1 stage | AutoResearchClaw stage | Required output |
|---|---|---|
| P6 | 16 `PAPER_OUTLINE` | Canonical six-section outline with evidence map. |
| P7 | 17 `PAPER_DRAFT` | Full section-by-section draft with a relevant figure/table mapped to every subsection under `4 Experiments and Results`. |
| P9 | 18 `PEER_REVIEW` | At least two rigorous reviewer reports, including the every-subsection visual-coverage check. |
| P10 | 19 `PAPER_REVISION` | Revision plus response/resolution log. |
| P11 | 20 `QUALITY_GATE` | Quality-gate pass/fail report. |
| P13 | 22 `EXPORT_PUBLISH` | TeX source, bibliography, figures, and export artifacts. |
| P14 | 23 `CITATION_VERIFY` | Citation authenticity, relevance, placement, and duplicate-paper report. |

Use `ml-paper-writing` as a supporting paper-quality skill and final polish pass. Do not replace AutoResearchClaw's multi-round review loop with a one-pass draft.

Stage 16 `PAPER_OUTLINE` must produce exactly this numbered top-level manuscript structure:

1. `Introduction`
2. `Related Work`
3. `Method`
4. `Experiments and Results`
5. `Discussion`
6. `Conclusion`

Do not invent alternative top-level sections such as separate `Preliminaries`, `Problem Formulation`, `Experimental Setup`, `Results`, `Analysis`, `Limitations`, `Future Work`, or `Conclusion and Future Work` sections. If those topics are needed, place them as subsections under the six required sections. Title, abstract, references, and required venue declarations may exist outside the numbered main body. Appendices are not allowed by default for this workflow because they are too easy to use as padding; create appendices only when the user or the target journal explicitly requests them.

The draft must include the required content in the canonical structure:

- `Introduction`: clear problem, gap, contribution, and evidence preview.
- `Related Work`: prior work grouped by theme, ending with the exact gap this paper fills.
- `Method`: problem setup, notation, architecture, algorithm, objective, and implementation details.
- `Experiments and Results`: datasets, baselines, settings, metrics, main results, ablations, robustness/efficiency analysis, and all experiment-generated tables/figures.
- `Discussion`: interpretation, why the method works, failure cases, limitations, threats to validity, and practical implications.
- `Conclusion`: concise summary of contribution, evidence, and honest scope.

No scientific content may appear after `Conclusion` unless explicitly required by the target journal. Do not add post-conclusion sections such as `Reproducibility and Artifact Statement`, `Artifact Checklist`, `Claim-Boundary Audit`, `Submission Checklist`, or `Author Checklist` inside the paper. Put those in separate project files.

## Gate 3: Figures and Tables

Create and insert figures/tables while drafting the initial paper, not after the manuscript is otherwise complete. Use `nature-figure` for data visualization figures and result plots/tables. Select Python or R according to the user's data/codebase; if unclear, ask the backend question required by that skill.

Do not blindly follow a premature figure list from the guidance file. The guidance file may define figure/table decision rules, but the final figure set must be chosen after experiment evidence stabilizes.

For Figure 1, the overall framework/architecture figure:

1. Read the full draft first.
2. Extract the core mechanism and contribution.
3. Use the user's reference-template style, `references/framework-figure-style.md`, and `assets/framework-figure-prompt-template.md` to construct a GPT image-generation prompt.
4. Create the figure with GPT's own image-generation model (`image2` in the user's wording). This is not a Nature-skill dependency.
5. If the first image misses the method or deviates from the reference style, revise the prompt and regenerate until the architecture matches the paper.
6. Insert the figure into the paper and write a caption that explains the mechanism, not just the visual components.
7. Do not use `nature-figure` or any Nature skill to create this overall figure; Nature skills are for data visualizations and result artifacts.

For every subsection under `4 Experiments and Results`:

- Each subsection must contain or cite at least one nearby figure or table, regardless of whether it covers setup, datasets, metrics, main comparisons, ablations, robustness, efficiency, qualitative outcomes, or error analysis.
- Do not create a new subsection until a relevant supporting artifact has been assigned to it.
- If no meaningful figure/table exists, keep the material in the parent-section introduction or merge it into a related subsection that already has an appropriate artifact.
- Do not satisfy this gate with decorative or irrelevant visuals; the artifact must support the subsection's scientific purpose.
- The first substantive paragraph of the subsection should cite its corresponding figure/table.

Every figure/table must satisfy:

- cited in the text;
- explained near first citation;
- caption states the takeaway;
- source data is saved;
- no unsupported numbers;
- placement is close to the explanatory paragraph.

Default mature-paper figure/table count:

- total figures + tables: 6-10;
- Figure 1: GPT-generated architecture/framework image;
- at least one main result table;
- at least one ablation table or ablation figure;
- at least one robustness/error-analysis visualization if the guidance requires robustness;
- at least one efficiency/resource table or plot if the paper makes efficiency claims.

If fewer than 6 total artifacts are used, explain why in `figure-table-insertion-audit.md`. If more than 10 are used, justify that the paper still reads like a mature journal manuscript rather than a report dump.

Maintain `figure-table-insertion-audit.md`:

| Artifact | Source experiment/generation step | Manuscript label | First citation location | Caption quality | Discussed near citation? | Results subsection covered | Status |
|---|---|---|---|---|---|---|---|

Allowed statuses: `inserted`, `needs-caption`, `needs-text-citation`, `too-far-from-discussion`, `needs-result-subsection-artifact`, `unused-with-reason`.

Also maintain a compact result-subsection coverage table in the same file:

| Experiments and Results subsection | Scientific purpose | Required artifact | Artifact label | Nearby citation? | Status |
|---|---|---|---|---|---|

Allowed statuses: `covered`, `needs-artifact`, `merge-or-remove-subsection`.

## Gate 4: Citations

Use `ml-paper-writing`, `nature-citation`, and `citation-audit`.

Requirements:

- at least 36 references;
- most references from the last 3-5 years relative to the current date;
- all references real and relevant;
- BibTeX fetched from reliable sources when possible;
- no memory-invented BibTeX;
- placeholders clearly marked if verification fails;
- no duplicate-paper entries in the final bibliography.

Maintain `reference-dedup-audit.md` from `assets/reference-dedup-audit-template.md`:

| Candidate key | DOI | arXiv id | Normalized title | Authors/year | Possible duplicate of | Decision | Evidence/source |
|---|---|---|---|---|---|---|---|

Duplicate checks must include:

- exact DOI match;
- exact arXiv id match;
- normalized title match after lowercasing and removing punctuation/subtitles where appropriate;
- same first author/year with near-identical title;
- preprint and conference/journal versions of the same paper.

When a preprint and a published venue version refer to the same work, keep the authoritative published version by default. Keep both only if the manuscript explicitly discusses version differences, and document the reason in `reference-dedup-audit.md`.

## Gate 5: TeX, PDF, Single-Final Template Policy, And Expansion

The final deliverable must include TeX source and a compiled PDF. Use `paper-compile` where available. Required outputs:

- `paper.tex` or an equivalent main `.tex` file;
- bibliography file such as `.bib`;
- figure files referenced by the TeX;
- compiled `paper.pdf`.

All required outputs must be under `run_root`. If LaTeX compilation fails, fix the TeX, bibliography, figure paths, packages, or labels until a PDF is produced. Do not deliver only Markdown or only an uncompiled TeX draft.

The length policy is single-final-PDF:

1. Produce exactly one final compiled manuscript PDF, normally `paper.pdf`.
2. If the current target journal or template defines a word, page, figure, or file-size limit, comply with it and record the source in `submission-constraints.md`.
3. If no target length limit is known, the default mature-draft target is more than 20 pages unless the user explicitly waives it.
4. Do not create conflicting parallel manuscripts merely to satisfy both the default draft target and a real venue limit. The current target-journal version governs.

After compiling, count pages and, when applicable, words and file size. If no target limit exists and the PDF is 20 pages or fewer without a waiver:

1. Identify short sections and thin paragraphs.
2. Use `paper-refine`, `paper-polish-workflow`, or the relevant paper skill to expand paragraph by paragraph.
3. Expand with substance inside the six required sections: mechanisms, experimental detail, failure cases, limitations, related-work distinctions, and ablation interpretation.
4. Do not pad with repetition.
5. Do not add appendices, artifact checklists, workflow descriptions, or post-conclusion notes to satisfy the page policy.
6. Recompile and repeat until `paper.pdf` is more than 20 pages.

Record the final PDF path, template/style, page/word/file-size constraints, actual values, waiver status, and pass/fail decision in `page-count-audit.md`. Do not produce or audit a second manuscript variant unless the user explicitly requests it.

## Gate 5.5: Submission Constraints, Metadata, and Declaration Routing

Apply this gate whenever a target journal, special issue, official template, author guide, or live submission form is known. Create two external working records:

### `submission-constraints.md`

| Field or file | Current requirement | Authority/source | Count or status | Pass/fix |
|---|---|---|---|---|

Record at least article type, special issue, abstract word limit, keyword maximum, highlight count/character limit, manuscript format, anonymization, declarations, data-availability prompt, source-file requirements, figure requirements, supplementary files, checklist, and publishing route when supplied. Resolve requirements as follows:

1. hard technical and eligibility constraints in the live form for the current article type or special issue;
2. hard requirements in current special-issue instructions, journal author guide, and template;
3. explicit current user choices for optional content, wording, declarations, and publishing route, provided they remain within the hard constraints;
4. older drafts, cached instructions, or generic publisher guidance.

Use the stricter requirement when equally authoritative current sources differ. A user preference cannot relax a hard portal or journal limit. Record unresolved conflicts instead of silently choosing the easier value.

Treat a requirement as hard when the portal blocks progression or validation, or the current instructions use mandatory language such as `must`, `required`, or an explicit maximum/minimum. Recommendations such as `encouraged` remain optional unless the user chooses them. If a declaration prompt or its effect is still ambiguous after checking the current instructions, do not guess: record the exact wording and obtain the user's decision before changing the accepted manuscript or portal answer.

### `manuscript-metadata.md`

| Metadata item | Canonical value | TeX/PDF | Title page | Cover letter | Source archive | Portal/standalone file | Status |
|---|---|---|---|---|---|---|---|

Include title, author order, affiliations, corresponding-author order and emails, abstract, keywords, highlights, funding, acknowledgments, data availability, code availability, competing interests, and generative-AI declaration status. A change to any canonical value invalidates every previously built PDF, title page, cover letter, archive, and portal draft until resynchronized.

Declarations are routed, not blindly accumulated:

- put a statement in the manuscript only when the user or current journal instructions require or encourage it there;
- keep a declaration external when the system requests a standalone form;
- distinguish public datasets from public code;
- do not claim code availability unless a real access route exists;
- remove stale statements and files that contradict the selected route;
- answer portal questions from the accepted manuscript and canonical metadata, not from memory.

This gate checks preparation only. Do not click final submission, choose a paid publishing route, or make an external commitment without explicit user instruction.

## Gate 6: Professionalism, Selective Humanization, and Final Polish

Before humanization, run the final guidance and artifact audit:

1. Re-read the original guidance file.
2. Check `experiment-completion-lock.md`; do not proceed if any strong-result lock item is unresolved.
3. Check `paper-guidance-audit.md`; fix every `missing` or unjustified `partially-covered-needs-repair` item.
4. Check `experiment-traceability.md`; verify every required run is represented in the paper.
5. Check `figure-table-insertion-audit.md`; insert or explain every experiment-generated figure/table and verify that every subsection under `4 Experiments and Results` has at least one relevant visual artifact.
6. Check `reference-dedup-audit.md`; fix duplicate-paper entries before final polish.
7. Recompile TeX to PDF after fixes.

Before `humanizer`, scan the manuscript for concrete professionalism defects:

- project-process narration: JSON/CSV export, plotting pipeline, BibTeX/Crossref retrieval, audit mechanics, file packaging, or how the paper was assembled;
- debugging chronology or bug-fix history that is not itself a scientifically relevant method or validation result;
- editor-, reviewer-, venue-, or paper-facing narration instead of a direct scientific claim;
- conversational verdicts, rhetorical self-questioning, slogan-like contrasts, rule-of-three padding, and repeated templated transitions;
- repeated negative disclaimers that restate the same limitation rather than defining the measured scope once;
- unsupported trust, reproducibility, superiority, novelty, or deployment language.

Run `humanizer` only on passages with identified defects. Do not blanket-paraphrase the full draft. Preserve already-natural academic text, technical terms, equations, numerical values, citations, figure/table references, and the intended strength of supported claims. Humanization must retain a formal journal register; it is not permission to make the prose casual.

Keep process material in external artifacts such as `experiment-traceability.md`, `reference-dedup-audit.md`, `figure-table-insertion-audit.md`, logs, manifests, and source archives. The manuscript should report reproducible scientific methods and evidence, not narrate the mechanics of producing the manuscript.

Then run `ml-paper-writing` as the final ML-paper polish pass:

- tighten claims;
- improve section flow;
- align terminology;
- verify citation placement;
- check venue tone;
- remove unsupported hype.

After final polish, recompile again. The final PDF must reflect the final TeX source.

If Gate 5.5 applies, recount the exact final abstract, keywords, and highlights; resynchronize all author/correspondence metadata and declarations; rebuild source archives; then compare the accepted TeX, PDF text, title page, cover letter, standalone statements, and package copies. Extract the final source archive into a clean temporary directory and compile it independently. Compare normalized source hashes and the PDFs' extracted text, page count, figure inventory, references, and metadata; do not require byte-identical PDFs when timestamps or engine metadata differ. Stale, contradictory, semantically different, or non-compiling package copies fail this gate.

## Final Audit Note

Deliver a concise audit note with:

- guidance file used;
- main achieved results;
- experiments completed and failed;
- figures/tables included;
- guidance-file coverage status;
- figure/table insertion audit status;
- citation count, recency ratio, and duplicate-paper audit status;
- TeX path, single final PDF path, template/style, and page count;
- single-final-PDF page-policy status;
- run-root path and artifact-containment status;
- unresolved risks or claims needing human review.
