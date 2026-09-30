# Narrative And Prose Gates

Use these gates in S1 and S6-S9. They make whole-paper coherence, limitation placement, and selective humanization auditable rather than impressionistic.

## Gate N1: Canonical Selling-Point Spine

Write the paper's central scientific question and one evidence-bounded core claim. Separate core claims from supporting, diagnostic, and negative findings; only core claims need a cross-paper spine. Decompose each core claim into:

`problem/gap -> insight -> method or study-design embodiment -> evidence -> interpretation -> bounded conclusion`

Record the chain and claim role in `narrative-consistency-map.md`. Supporting findings may answer a local question or qualify interpretation; do not promote them into competing theses or force them into every section. Flag actual contradictions, terminology drift, population/task drift, changed causal strength, or novelty wording that varies across modules.

## Gate N2: Forward And Backward Closure

Trace each core claim in both directions:

- Forward: title/abstract promise -> Introduction gap/contribution -> Method/test -> Result.
- Backward: Conclusion implication -> Discussion interpretation -> Result -> Method/test -> stated gap.

Fail the gate when a core contribution lacks evidence, a conclusion claim first appears at the end, or a figure/table carries a different message from the prose. Give major supporting or diagnostic results the interpretation needed for their local purpose; they need not be repeated in abstract, introduction, discussion, and conclusion. Preserve honest scope: closure means consistent support, not repetition of the same sentence.

## Gate N3: Section Roles

- Title: name the same task, method/insight, and scope used later.
- Abstract: compress the complete chain with concrete evidence and no extra thesis.
- Introduction: establish one problem-to-gap-to-contribution path and preview how it will be tested.
- Method: operationalize every promised mechanism, comparison, or design boundary.
- Results: answer the declared scientific questions with informative comparisons, direction, uncertainty, and relevant conditions; keep full cell-by-cell values in tables where appropriate rather than transcribing inventories.
- Discussion: explain what the evidence establishes, relate it to relevant literature and practical meaning, and distinguish observed patterns from plausible explanations and untested mechanisms. Do not require a causal mechanism where the study did not test one.
- Conclusion: recall the central contribution and evidence boundary; add no new result or claim.

## Gate P1: Limitation Placement

Classify every caveat:

Maintain a limitation-placement ledger with the passage location, class, claim affected, final action/location, and any exception rationale.

| Class | Default action |
|---|---|
| Material limitation | State in Discussion/Limitations and narrow the affected claim where it appears |
| Necessary immediate factual qualification | Keep beside the affected claim and log why removal would make it false or unsafe |
| Methodological assumption | State neutrally in Methods; do not phrase as a defense |
| Result uncertainty | State with the result/statistic; do not turn it into a general disclaimer |
| Defensive rhetoric | Remove or rewrite as direct evidence-led prose |

For material limitations, state the evidence boundary and its practical consequence where relevant. Name future work only when a concrete next study is useful and follows from that boundary; it is not a required sentence element. Keep each result's qualification with the result when needed, without forcing every result into the whole-paper claim spine. Do not hide validity threats by moving them away from the affected claim.

Record author scope alongside the existing limitation ledger: `edit_scope`, `protected_sections`, `protected_artifacts`, `declaration_mode` (`preserve` / `author-managed` / `journal-routed`), and whether new experiments are authorized. Respect exact protected ranges. If a protected passage contains a material factual concern, report it outside the manuscript and leave it unchanged. Route required declarations according to current journal instructions; an author-managed item remains pending and cannot be labeled complete. Keyword scans must not remove required disclosure or protected text.

## Gate P2: Selective Humanization

Inspect every scientific module and record either `no concrete AI-like defect` or an exact location with one of these named defects:

- templated transition or repeated contribution announcement;
- rule-of-three padding or inflated abstract noun;
- slogan-like negative parallelism (`not X but Y`);
- rhetorical self-questioning, conversational verdict, or journal-facing meta-language;
- clause-stacked endpoint inventory or mechanical sentence rhythm;
- promotional, vague, or unsupported novelty/deployment wording.

Use the documented CLI in `references/writing-adapter.md` to construct an explicit-context request that loads the shared contract, academic profile, and manuscript-facing packet. The builder does not invoke a model or perform edits. For a flagged humanizer passage, set `--subskill humanizer` and state the named local defect in the request; then verify the returned manuscript text separately. Installed subskills have lower priority than the shared contract, evidence, author protections, and journal rules. Preserve terminology, equations, numbers, units, citations, cross-references, and claim strength. If the adapter/contract is unavailable, record the integration as blocked/unverified; do not claim successful academic-profile application. A stylistic change that alters evidence scope fails this gate.

## Acceptance Record

S8/S9 pass only when:

- every core claim has a complete trace and callback, and no unsupported contribution, result, figure/table message, or conclusion claim remains;
- supporting and diagnostic findings are interpreted where relevant without forced cross-section repetition;
- every caveat is classified and correctly placed;
- protected sections/artifacts and declaration handling match the run contract;
- every module has a humanizer scan result;
- every humanized passage passes technical-anchor, claim-strength, citation, and register checks.
