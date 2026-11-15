# Argument and Section Guide

Use this guide to organize a paper's reasoning. The listed functions need coverage where relevant, but they are not compulsory headings or numbered sections.

## Contents

- [Plan the scientific argument](#1-plan-the-scientific-argument)
- [Adapt to the kind of paper](#2-adapt-to-the-kind-of-paper)
- [Title and abstract](#3-title-and-abstract)
- [Introduction](#4-introduction)
- [Related work](#5-related-work)
- [Definitions and problem formulation](#6-definitions-and-problem-formulation)
- [Method or analytical approach](#7-method-or-analytical-approach)
- [Evidence and results](#8-evidence-and-results)
- [Discussion and conclusion](#9-discussion-and-conclusion)
- [Figures and supplementary material](#10-figures-and-supplementary-material)

## 1. Plan the scientific argument

Before drafting a full paper, build a short argument map from actual materials:

| Element | Question to resolve |
|---|---|
| Problem and stakes | What does not work, remains unexplained, or cannot yet be achieved, and why does it matter? |
| Established knowledge | What do relevant prior studies already accomplish or explain? |
| Precise gap | What unresolved requirement, contradiction, assumption, or missing understanding remains? |
| Research question | What specific question does this study answer? |
| Insight | What observation or reasoning makes the approach plausible? |
| Contribution | What new capability, explanation, result, resource, or synthesis is provided? |
| Evidence | Which experiment, proof, analysis, source, or observation supports each claim? |
| Implication and scope | What follows, for which setting, and what has not been established? |

Do not manufacture a gap after selecting a favored method. A gap may concern explanation, conditions, evidence, or applicability rather than absence of any prior solution. “Little research exists” and “no one has studied this” require a justified literature basis, not a failed quick search.

A useful internal contribution statement is: **this study addresses [specific unresolved problem] through [central idea], establishing [supported advance] under [relevant conditions].** This is a planning aid, not a sentence that must be repeated throughout the paper.

Each section should answer a different reader question. Reuse the central concept for continuity, but do not repeat the same pipeline and result paragraph in the abstract, introduction, related work, and conclusion.

## 2. Adapt to the kind of paper

| Paper type | Typical contribution | Suitable evidence and organization |
|---|---|---|
| Empirical method or system | A capability, performance change, or practical mechanism | Setup and comparison, central results, mechanism tests and relevant operating conditions |
| Theoretical | A theorem, bound, characterization, or counterexample | Definitions, assumptions, statement, proof idea, proof, consequences and sharpness where relevant |
| Review or synthesis | A defensible organization of evidence, disagreement, or open questions | Scope, search/selection approach where applicable, analytical framework, synthesis, implications |
| Qualitative or observational | An interpretation, association, process account, or contextual understanding | Sampling/data provenance, analytical procedure, observations or themes, interpretation and scope |

Hybrid papers can combine these functions. Do not invent ablations for a review, a learning algorithm for a theory paper, or causal conclusions for observational evidence. A conceptual paper may organize around an argument rather than new measurements. Discipline-specific reporting standards can require a different order, structured abstract, ethics statement, or dedicated limitations section.

For method-oriented empirical work, a useful starting sequence is Introduction → Related Work → Problem/Setup → Method → Evaluation → Conclusion. It is a candidate organization, not a six-section rule. Merge small functions or separate substantial ones when this improves comprehension.

## 3. Title and abstract

### Title

Expose the problem or central contribution in language the intended reader can identify. Prefer technical specificity over grand adjectives. Avoid listing every component or claiming optimality and universal effectiveness unless these are demonstrated. A method acronym is optional, not a contribution in itself.

### Abstract

Use **gap → proposed approach or argument → enabled advantage → principal evidence → implication**. Combine functions naturally rather than enforcing a fixed sentence count.

Start near the actual unresolved issue, not a generic claim that a broad technology has become important. Identify the contribution early enough that the abstract is not mostly background. Explain why the core idea helps; naming modules does not explain value.

Summarize findings at the research-question level. For an empirical paper, “Experiments show that …” can move directly to the conclusion instead of listing all datasets before stating the finding. For theory, summarize the proved result; for a review, the synthesis; for qualitative work, the central finding. Do not force the word “experiments” into other genres.

Prefer a compact paragraph unless a structured abstract is required. Usually omit exhaustive task counts, hyperparameters, every metric, and production details. Include a key effect size or other number when it is essential to the contribution, required by the venue, or more informative than a vague success claim. Choosing representative evidence is different from presenting the best case as a universal outcome.

Close the opening gap by stating what the result enables or clarifies. Avoid two consecutive closing sentences that say the same thing. Do not mechanically add a defensive disclaimer after the contribution; state any condition necessary to keep the summary accurate.

## 4. Introduction

Build **documented real problem → tension or unresolved requirement → research question → prior capabilities and remaining gap → insight → contribution and evidence**.

Make the opening concrete. An application example should reveal a mechanism and consequence, not merely name an impressive industry. The motivating problem can also be theoretical or conceptual; a pure mathematics paper does not need an invented industrial story.

Narrow the scope progressively. Explain why the established setting, assumption, or method does not settle the question of this paper. Distinguish a study-specific constraint from an inherent limitation of an entire field.

When reviewing prior solutions, explain what they achieve before specifying what remains unresolved. Represent the closest work accurately, including relevant capabilities that weaken a simplistic novelty claim. Define the missing combination or understanding rather than claiming that all prior approaches fail.

Introduce the insight before announcing the method. The reader should see why the proposed direction follows from the problem, not encounter a sudden block of modules unrelated to the motivation.

Prefer a coherent closing paragraph: name or characterize the approach → central mechanism → enabled capability → concise evidence and implication. Add a contribution list only when it clarifies genuinely distinct advances or the venue favors it; avoid a numbered list that duplicates the paragraph. Do not repeat “Experiments show … These results show …” without a new inference.

Support nontrivial background and external empirical claims with relevant citations. Original contributions need accurate explanation and the paper's own evidence, not decorative references to unrelated studies. Cite borrowed components where their role is actually discussed.

## 5. Related work

Decide the intellectual route first: which research streams must the reader understand, and why does one lead to the next? Search for appropriate primary sources, then revise the planned narrative when the literature requires it. This is argument-guided research, not selective searching for supportive citations.

Group studies by problem, mechanism, assumptions, evidence, or explanatory framework rather than writing an author-by-author inventory. Within a group, explain the common approach, representative contributions, meaningful differences, and what question leads to the next group.

Keep the focus on others' work. The author's default preference is a brief closing positioning sentence for the current study, not repeated promotion after every cited paragraph. When a particular comparison is essential, make it locally and precisely rather than withholding it to satisfy a rigid final-sentence rule.

Do not describe every predecessor through its weakness. A fair synthesis can reveal a gap without a sequence of dismissals. Do not omit the closest work simply because it complicates the proposed contribution.

Retain foundational papers when they establish the relevant concept. Add current work for technical relevance, not merely recency. Correctly distinguish original ideas, later developments, and the present contribution; a citation does not transfer a predecessor's proof or guarantee to a new method.

Related-work length should follow the reasoning burden. Do not compress an approved version by removing the conceptual transitions that make the narrative readable. Citation-verification and publication-status bookkeeping belong outside the scientific prose unless source status is substantively relevant.

## 6. Definitions and problem formulation

Define the objects, data, assumptions, available information, and objective needed to understand the contribution. Move from familiar concepts to the study-specific setting. A separate mathematical section is useful only when this content needs it.

For each important equation, explain its purpose before it, define symbols where introduced, and state its consequence. Distinguish assumptions from observations, estimands from estimators, objectives from evaluation metrics, and available information from inaccessible quantities.

Do not import equations, constraints, or mathematical assumptions from a reference paper merely to imitate its appearance. Avoid introducing unused notation. State a restriction where it affects interpretation instead of collecting all restrictions in a distant paragraph.

Keep the boundary with the method clear: problem formulation specifies what must be solved and what information is allowed; the method specifies the proposed solution. In a nonmathematical paper, an explicit conceptual framework can serve the same function.

## 7. Method or analytical approach

Use **design need → proposed operation → output or result → connection to the next step**. Begin with an understandable overview, then explain the necessary details in dependency order. The reader should understand why each component exists, not just its name.

State what is novel and what is reused. Explain the mechanism that is expected to yield the claimed advantage. An architecture diagram does not replace this reasoning, and a long implementation inventory should not bury it.

Keep notation, pseudocode, diagrams, and execution order consistent. Distinguish a learned estimate from a measured quantity, an approximation from an exact result, and an implementation choice from a theoretical requirement. For theory, state assumptions and the theorem precisely and explain the proof's key idea; for qualitative analysis, explain how interpretations were obtained and checked.

Include enough detail for comprehension and the appropriate form of reproducibility. Put long derivations, full configurations, or expanded procedures in supplementary material when the main argument remains intelligible. Do not move a central assumption or indispensable algorithmic step out of sight.

## 8. Evidence and results

Organize the section around the questions that test the contribution. Describe the setup only to the extent needed to interpret those questions, then present the decisive evidence before secondary analyses.

For empirical comparisons, define the setting, data, comparators, outcomes, relevant controls, replication units, and uncertainty. Check that methods are compared under conditions that justify the sentence being written. A modified implementation is not automatically a faithful reproduction of a published result.

A useful result-paragraph pattern is **question → comparison or analysis → main finding → selected evidence → interpretation**. Use it flexibly, not as a five-sentence template. Lead with the achieved advance when supported; give numbers that explain its magnitude rather than transcribing every table cell.

Separate practical importance, effect size, and statistical significance. Report units, reference conditions, and aggregation faithfully. An average improvement is not improvement for every case; an association is not a causal effect; an illustrative case is not an independent replication.

Choose mechanism tests relevant to the contribution. In method papers, ablations should state what changes, what stays controlled, and what inference follows. They need not all produce large positive effects. In other genres, sensitivity analyses, counterexamples, triangulation, or evidence contrasts may be more appropriate than ablations.

Use qualitative examples to explain phenomena, not to substitute for broader evidence. Disclose selection or display choices when they affect interpretation. Do not silently select the best examples or relabel generated illustrations as observations.

Evaluate costs when central to the claim. A speed, efficiency, safety, or deployment claim may make operating constraints indispensable. Conversely, do not add an unrelated inventory of every measurable weakness merely to appear exhaustive. Relevance to the scientific question and transparency, not favorable appearance alone, determine what belongs.

## 9. Discussion and conclusion

### Discussion

Interpret the results: what mechanism they support, how they change understanding, where findings agree or disagree with prior work, and what conditions explain variation. Do not turn the discussion into a second result table.

A separate Discussion section is warranted when this interpretation is substantial or conventional for the field. Otherwise relevant interpretation can accompany results. Limitations should identify the scope of inference and unresolved explanations where needed; avoid both a ritual weakness list and concealment of a central caveat.

### Conclusion

Use **contribution → essential reason it works or matters → overall evidence → warranted implication → specific future questions**. Do not introduce new results or claims that the body has not established. The conclusion should answer the introduction's question at a higher level, not repeat the abstract word for word.

The author prefers a compact single paragraph when it covers the necessary functions. Use more than one when length, genre, or venue requires it. Derive future work from actual assumptions, unresolved findings, or a concrete extension of the contribution. Avoid copied future directions and generic promises to study “more complex scenarios.” Future plans are not completed capabilities.

## 10. Figures and supplementary material

Give each visual an argumentative role: explain the system, demonstrate a comparison, expose a mechanism, or summarize evidence. A framework diagram should emphasize the contribution and true dependencies instead of making every component equally prominent. A decorative icon or screenshot is not automatically useful evidence.

Choose plot types, units, scaling, aggregation, and captions to make the intended comparison accurate. Use a small consistent palette with readable contrast at final size, and ensure the figure remains understandable without color alone when necessary. Font and separator choices follow readability and venue constraints, not a universal font mandate.

Captions should identify what a reader needs to interpret the figure independently: panel roles, metrics, groups, and uncertainty where relevant. Do not explain every obvious graphical mark. Nonstandard encoding or a display choice affecting interpretation does need explanation.

Combine a figure and table when they cover the same question and the pairing improves comprehension. Do not force unrelated material together to imitate a reference layout. Introduce visuals naturally within the scientific discussion, not through isolated sentences that merely announce their existence.

Use the main text for the central argument and necessary evidence; use supplementary material for supported extensions such as full tables, derivations, protocols, instruments, or videos. Keep terminology, numbering, data, and scope consistent. Do not assume that supplementary material is mandatory or optional without checking the relevant venue when required.
