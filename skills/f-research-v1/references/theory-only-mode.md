# Theory-only article mode · v1

Load only when the user explicitly requests a theoretical/conceptual article without experiments, and record that authorization. This conditional profile overrides empirical-only requirements below the entrypoint; it does not reclassify an incomplete empirical project. Existing empirical contracts and strong-result locks retain their original meaning.

## Contract and execution

Record `execution_profile: theory-only`, `evidence_basis: definitions-proofs-counterexamples`, `allow_new_experiments: false`, `article_goal` (original research or theoretical exposition), and the actual executor in the versioned run contract. No benchmark, pilot or training is required or implied. An exposition may synthesize established facts but must identify its sources and cannot claim novelty or journal-tier readiness without evidence. A request to write an article does not implicitly require a journal submission.

Keep canonical stage IDs and ordered JSON evidence. For this profile the state includes a hash-bound `profile` snapshot and `authorization` snapshot, and each passed row identifies `gate_basis: theory-only` and `actual_executor`. Use the gate meanings below. A passed proof gate is never a passed experiment. Do not migrate an old empirical failure into this mode to obtain a pass; create a new authorized contract.

Native Codex writing/review through `writing_adapter.py` is an allowed actual executor for this mode; record requested model/effort and exposed versions. It is not AutoResearchClaw. Preserve every request/response and dependency hash. External ARC remains separately unverified until its actual context boundary is integrated. Named CCFA capabilities can support substantive review; record which were actually used, and distinguish agent review from role self-review. Do not fabricate CCFA or ARC completion from a file name.

## Guidance: same stages, theoretical questions

| Stage | Required substantive work/evidence |
|---|---|
| CCFA-startup | Candidate questions, ownership/scope, evidence plan and critical feasibility review; record actual review tools, no invented mandatory skill runs |
| G0 | Verify relevant mathematical/disciplinary sources and what they establish |
| G1 | Establish accessible definitions, source/proof materials; dataset access is inapplicable because the authorized object is a theorem/concept |
| G2 | Define objects, quantifiers, domains, assumptions and the exact question |
| G3 | Derive the proposed claims or a credible proof route; identify potential counterexamples |
| G4 | Position against known results; label synthesis/exposition honestly when novelty is unproven |
| G5 | Confirm local writing, proof-checking and document-production tools; no training hardware gate |
| G6 | Compare against known propositions and construct discriminating analytic examples/counterexamples |
| G7 | Freeze proof obligations and failure criteria; a desired conclusion is not a proved result |
| G8 | Establish the reader benefit and coherent article argument; apply an explicitly requested tier only if evidence supports it |
| validation/handoff | Validate the theoretical guidance and transfer supported definitions, proof obligations, sources and brief |

Retain recognizable guidance headings, using `Evidence Plan` instead of `Experiment Plan`. Outline: Introduction, Related Work, Formal Setup, Theoretical Results, Discussion, Conclusion (venue/author variants may be mapped explicitly). Use the existing validator's explicit `--study-mode theory-only`; empirical default stays unchanged. No empirical feasibility packet is fabricated for this profile. Bind the actual proof plan and reviewed guidance as evidence instead.

## Research: prove, then write

| Stage | Required substantive work/evidence |
|---|---|
| P0/P1 | Authorized contract, run boundary and theoretical guidance validation |
| P1A/P1B | Proof feasibility and adversarial assumptions/novelty review; unresolved critical flaws block |
| P2 | Local document tools and notation/proof plan; no training setup |
| P3/P3A | Reconstruct relevant known results and check what is inherited versus added |
| P4 | Complete each promised derivation and analytic counterexample; a numerical illustration is exact arithmetic, not an experiment |
| P5 | Lock only proved claims, explicit assumptions and counterexamples; unresolved claims remain hypotheses or block the core argument |
| P5A | Independent proof/claim review and correction before prose drafting |
| P6/P7 | Actual adapter-built outline and full article; theoretical facts cite checked proof sources; use reader-order paragraph tasks |
| P8 | Mathematical display/table/diagram decisions; an analytic article does not require an invented architecture or generated Figure 1 |
| P9/P10 | Actual scientific and prose reviews, concern-to-edit decisions, integrated revision; no generic response paragraphs |
| P11/P12 | Whole-paper logic, proof/claim correspondence and verified citation coverage |
| P13/P14 | Export current standalone source and verify citations in context |
| P15/P16 | Compile/check the document and its information density; no page floor |
| P17/P18 | Compare against guidance; inspect included equations/tables/figures and their labels |
| P19–P21 | Selective final editing, renewed fact/proof/paragraph checks, source/PDF consistency and final delivery |

Use `status: derived_verified` for a theorem only after its assumptions and proof were actually checked; it is not empirical observation. A proof-plan fact stays `planned`. A result fact may use `kind: theorem` with a statement, assumptions and hash-bound proof evidence; do not force numeric metric fields onto mathematical results. Record analytic examples as such rather than measured data.

## Submission skill: actual article review, no invented submission readiness

Use S0–S10 in order. Research exports derive from the accepted research manuscript and remain independent of later submission edits. S0 snapshots the completed research deliverables as immutable input; submission edits and exports stay inside their own run. Never bind an earlier research gate to a mutable submission output. S1/S1A map and audit the argument, proof dependencies and author protections. S2 records the real article goal and target requirements (unknown if none supplied). S3/S4 retrieve and verify relevant theoretical comparators; for a user-requested exposition with no journal target, use a justified accessible set and qualitative argument comparison, without fabricated SCI metrics, ten-paper scores or percentile claims. The original ten-comparator/fourth-score rule still governs the default journal-submission mode.

S5/S6 identify useful organizing patterns and located defects in the actual manuscript. S7 changes only identified defects through the adapter; S8 checks the whole article and exact protected content. S9 compiles and inspects current output plus source/package consistency. S10 delivers an **article-development revision**, not a journal submission-ready package unless all real target requirements were verified. No upload is implied.

## Narrative validation on the actual article

Maintain one reverse outline and one revision log. For each paragraph, record its new proposition/function and the facts/assumptions it needs. Diagnose repeated caveats by meaning, not `not` counts. Locate measurement/assumption definitions once and repeat only when local truth requires it. A Discussion paragraph should interpret a proved boundary or decision consequence; do not replace it with a list of unclaimed things the article does not establish.

Review the current full article after revision for factual/proof defects, process narration, unnecessary defensive paragraphs and duplicate paragraph roles. Preserve drafts and actual requests, and report unresolved defects instead of equating a clean lint report with semantic acceptance. Skill-maintenance experiments and transfer tests belong in the maintenance task's artifacts, not in each ordinary article's writing obligations.
