# Scientific writing contract · v1

Authority: this file in f-research-v1 is the source; f-submit-v1 ships a byte-identical mirror for standalone installation. Repository `scripts/sync_writing_assets.py --check` checks the mirrors. Load at P6/P7/P10/P19 and S7, including every downstream rewrite/export that changes prose. Do not load the one-time migration task book.

The manuscript is organized around the scientific problem and the evidence, not around execution chronology, review checklists, or manuscript production. Write as the authors explaining the completed study to a knowledgeable reader. State supported findings directly, retain necessary qualifications, and give each paragraph a distinct argumentative purpose.

## Inputs and precedence

Evidence integrity, author protections and current journal requirements govern; next apply the manuscript brief and this contract; then subordinate subskill advice. Installed-first dependency resolution does not change this precedence. A passed research lock admits writing; it is not a scientific conclusion.

Build one compact scientific content packet from the existing claim/evidence and narrative maps: verified task/method definitions; study design; reported observations with model, split, metric, value, unit, aggregation, uncertainty type and measurement scope; material limitations; verified citations with supported propositions; figure/table scientific content. Tag facts `observed_verified`, `author_reported`, `planned`, or `unresolved`; the explicit theory-only profile additionally admits `derived_verified` propositions with checked assumptions and proofs. Preserve unfavorable and inconclusive results. Never upgrade author reports to independent verification, or plans to observations. Separate supported findings from explanatory hypotheses.

Keep evidence paths in the external manifest for targeted verification. Do not concatenate guidance expectations, stage ledgers, lock verdicts, logs, reviewer dialogue, debugging chronology or packaging notes into drafting inputs. Translate material test exposure, exclusions, post-hoc analyses and protocol changes into accurate scientific disclosures; they are not disposable process noise.

The brief states the central question, bounded answer, audience, main/supporting/diagnostic priorities, stable terminology, section purposes and author constraints. Trace only core claims through problem → design → evidence → interpretation → conclusion; supporting results may serve local purposes. For an application study connect a concrete domain problem → design requirement → actual choice → observed category/scenario result → supported use. For pure theory record why an application bridge is inapplicable; invent neither applications nor mechanisms.

## Writing and revision actions

Before outlining, reconcile expectations against supported facts and give every subsection a scientific purpose. For full drafts or structural repairs, turn the reverse outline into the adapter's `paragraph_plan`: point, supporting fact IDs, and what the passage adds. Assign repeated material conditions a `qualification_placement` home and a reason for any local repetition. Draft in reader order (working on Methods/Results first is allowed); no fixed sentence count or obligatory concluding transition. Keep mathematical assumptions in theorem statements when required for their truth, even if also defined in the setup.

After a section draft, produce an external reverse outline: paragraph location → new information/function. Merge overlapping roles, move misplaced protocol details, define terms fully once, and remove empty value announcements. Repair structure before paragraphs, then sentences. Keep good passages unchanged; KEEP means identical text, not a minimal clarity edit. Rewrite percentages are not quality measures.

Convert reviewer concerns in the existing revision log: concern → affected proposition → evidence status → action → location → factual check. Actions are KEEP, REWRITE, MOVE, MERGE, NARROW, REMOVE_NONSCIENTIFIC, BLOCK_EVIDENCE. Integrate replacements into the argument; do not append a defensive paragraph per comment. Conflicting/inapplicable requests may receive KEEP with an external rationale. Missing core evidence remains blocked.

For a local replacement, enumerate the scientific propositions that must survive in its factual check before rewriting. A measurement boundary or unresolved attribution cannot disappear merely because its original sentence was defensive. MOVE is valid only with an identified destination and verified retained text; otherwise retain the material condition in the replacement. Check those obligations against the actual output before insertion.

Use a run-configurable editing budget (default three rounds). Stop mechanical rewriting after two rounds without fewer named defects; diagnose evidence/input/argument problems. Budget exhaustion with unresolved defects is not a pass. Scientific repair needs its own existing authorization.

## Section jobs (load examples only when needed)

- Title/Abstract: identify task, design, a few main findings and their useful meaning; qualify a claim where its truth depends on scope. Do not end with a limitation inventory.
- Introduction: start from the specific scientific problem and what remains to be answered; link design to that question. Contribution counts and conference page templates are not journal rules.
- Related Work: group capabilities, assumptions, trade-offs and evaluation settings. Claim prior work cannot solve something only with supporting citations; do not compare incompatible published scores as direct experiments.
- Methods: reproducible scientific operations, assumptions, selection rules, splits, seeds, device and timing boundary. Report consequential protocol changes honestly; omit the mechanics of repairing code or producing the paper.
- Results: organize comparisons around questions and observed patterns, not run IDs/table cells. Keep main effects, conditions, units and uncertainty; cite figures near their evidence. Preserve negative/inconclusive findings. An interval crossing zero proves neither equivalence nor significance. Distinguish pooled F1 from the mean of per-unit F1 and training multiple candidates from inference with one.
- Keep an aggregation distinct from a subgroup: mean MAE does not mean MAE on mean-flow observations. Missing intervals leave precision/reliability uncertain, not the already reported point-estimate difference unknowable.
- Discussion: interpret what evidence establishes and relate it to prior knowledge and use. Distinguish observed patterns, analytically implied properties and untested mechanisms. A plausible mechanism remains a hypothesis; incomplete mechanism identification does not erase an observed predictive benefit. Do not repeat the Results inventory or write commands for future experiments.
- Limitations: concrete scope/unresolved issue and its consequence. Future work is optional and targeted. Keep method assumptions in Methods and uncertainty beside Results; material limits also constrain affected claims. Do not invent standard limitations or self-deprecation.
- Conclusion: answer the Introduction's question with supported evidence and meaning; add no result, mechanism or application promise.

Length follows scientific substance, article type and current journal limits. Twenty pages or fewer is not incomplete. Expand only an identified explanatory/evidence gap and shorten repetition. References cover the question, methods, data and relevant recent progress; 36 is not a universal minimum. Six–ten visuals is adjustable planning, not acceptance. Prose may adequately support settings; important measured comparisons need suitable evidence. Preserve explicit author contract requirements with their source; never pad to meet them.

## Academic profile for every subordinate writer

Apply to humanizer, paper-refine, paper-polish-workflow and ml-paper-writing after resolving their installed/bundled paths. No added opinions, feelings, jokes, asides, lived experience or deliberate messiness. Keep formal register, useful passive voice and scholarly first person. Preserve terms rather than varying them into inequivalent synonyms. Protect numbers, units, symbols, citations, model/condition associations, direction, uncertainty type and claim strength. Paper-refine handles local expression; use macro → paragraph → sentence → coherence order without automatic sentence-by-sentence permission requests.

Return manuscript text separately from short internal change notes. Humanizer diagnostics such as “What makes this obviously AI generated?” never enter manuscript text. `not`, `we`, `pipeline`, `control`, `checkpoint`, `frozen`, `validation` and agent/tool names are not banned words. Classify their scientific role before editing. Formal AI/data/ethics disclosures follow preserve/author-managed/journal-routed mode; never erase them with a style scan or invent tool usage.

Packet provenance (including test-fixture labels or “not supplied to the writer”) belongs in notes. If missing information changes scientific validity, state that scientific boundary or block externally; do not narrate the writer's access to the packet. Qualify the claim being made, not every possible future claim: a predictive conclusion does not require repeatedly disclaiming an unclaimed causal mechanism or deployment capability.

## Acceptance

Compare full paragraph and whole-paper meaning against the packet, not just numbers or word presence. Verify negative results, causal strength, task/population, protected ranges, author metadata and source tables. Review figure captions and visible label lists separately from generation prompts, then visually inspect rendered figures when possible. Mark unavailable visual checks pending.

After the last polish, translation, template conversion or export, recheck the current text and rebuild its PDF/package. Bind acceptance to current input, source, figure and output hashes. A changed dependency invalidates that acceptance. Lint supplies located candidates, not semantic proof; pipeline-state validation supplies ordered evidence, not writing quality.
