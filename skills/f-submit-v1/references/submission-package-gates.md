# Submission Package Gates

Use these gates in S2, S6-S10. They supplement comparator scoring: a manuscript is not submission-ready merely because its prose ranks well against comparator papers.

## Contents

- Requirement authority and canonical metadata
- Manuscript professionalism and selective humanization
- Declaration routing and authorized removal
- Publishing route and cost
- Package integrity and upload map
- Red flags and rationalization checks

## Gate A: Requirement Authority

Create `submission-constraints.md`:

| Field or file | Requirement | Hard/recommended | Authority and source | Final value/count | Status |
|---|---|---|---|---|---|

Record article type, special issue, classifications, template, anonymization, abstract limit, keyword maximum, highlight count and character limit, title-page rules, manuscript/source format, figure handling, supplementary files, declarations, data-availability prompt, checklist, and publishing options.

Treat a requirement as hard when the live portal blocks progress/validation or current instructions say `must`, `required`, or give an explicit maximum/minimum. Recommendations such as `encouraged` are optional. Resolve conflicts in this order:

1. live hard constraints for the selected article type or special issue;
2. current special-issue and journal hard requirements;
3. explicit user choices for optional content and route, within hard constraints;
4. older drafts, cached pages, generic publisher guidance, or defaults.

Use the stricter value between equally authoritative current hard limits. Record the source and exact wording. If ambiguity can materially change the manuscript, declaration, cost, or eligibility after checking the current instructions, obtain the user's decision rather than guessing.

Count the exact final plain text that will be pasted or uploaded. Recount after every revision.

## Gate B: Canonical Metadata

Create `manuscript-metadata.md`:

| Item | Canonical value | TeX/PDF | Title page | Cover letter | Source ZIP | Standalone file | Portal | Status |
|---|---|---|---|---|---|---|---|---|

Include title, author order, affiliations, corresponding-author order and emails, abstract, keywords, highlights, article type, special issue, funding, acknowledgments, data availability, code availability, competing interests, and every declaration's routing status. For generative-AI disclosure, use an explicit state such as `required-present`, `optional-author-chose-present`, `optional-author-chose-removed`, `not-applicable`, or `blocked-requirement-conflict`.

Any change invalidates all previously generated outputs until resynchronized. Do not assume an older PDF, DOCX, title page, cover letter, ZIP, or portal draft updated itself.

Verify user-provided email spelling and role/order across artifacts. Do not invent consent, an address, or an author role.

## Gate C: Manuscript Professionalism

The manuscript body may contain reproducible scientific methods, data sources, validation procedures, and result provenance that readers need. It must not narrate the clerical or engineering process of producing the manuscript.

Remove or externalize:

- JSON/CSV export and plotting mechanics;
- Crossref/BibTeX/reference-search workflow;
- file paths, packaging, delivery, or internal audit instructions;
- bug-fix chronology unless the bug itself is the subject of a scientific validation study;
- language asking readers to trust code, metrics, bibliography, or prose;
- journal/editor/reviewer-facing self-commentary;
- conversational verdicts and rhetorical questions;
- repeated defensive disclaimers that do not add a new applicability boundary.

Replace them with direct scientific statements: what was measured, under which protocol, what evidence supports the claim, and where applicability ends.

Maintain a limitation-placement ledger. Classify each caveat as `material limitation`, `necessary immediate factual qualification`, `methodological assumption`, `result uncertainty`, or `defensive rhetoric`. Move material limitations to Discussion/Limitations while narrowing the affected claim where needed. Rewrite defensive rhetoric as evidence-led prose. Keep an out-of-Limitations qualification only when removing it would make the adjacent claim false or unsafe, and record that reason.

## Gate D: Selective Humanization

Diagnose before editing. Flag concrete patterns such as templated transitions, rhetorical self-questioning, rule-of-three padding, slogan-like `not X but Y` contrasts, repeated `we therefore`, journal-facing meta-language, and conversational comparisons.

Scan title, abstract, introduction/background, methods, results, discussion, limitations, conclusion, captions, and declarations separately. Record `no concrete AI-like defect` or list exact locations and defect types. Apply `humanizer` only to flagged passages. Do not paraphrase the full paper merely to change wording. Preserve technical terms, equations, numbers, units, citations, figure/table references, and the strength of supported claims. Re-scan each edited passage for lost qualifiers, stronger/weaker claims, broken references, and casual-register drift. The output must remain formal academic English.

## Gate E: Declaration Routing

Declarations are conditional elements, not a fixed block that every manuscript must contain.

When the user asks to add, revise, or remove a declaration, create `declaration-change-record.md` from `assets/declaration-change-record-template.md`. Record the user's exact authorization, the current official requirement or portal prompt, whether it is hard/optional/not applicable, the selected action, and every affected submission surface.

- Put a statement in the manuscript only when the user or current journal instructions require or choose it there.
- Use a standalone declaration when the portal requests one.
- Use the journal's current official form or wording when supplied. For an allowed free-text generative-AI statement, state only verified facts: the named tool/service, the limited purpose or manuscript stages in which it was used, and the authors' review/responsibility where true. Do not invent prompts, versions, dates, or uses.
- A portal answer must describe the accepted manuscript/package, not an earlier version.
- Distinguish dataset availability from code availability.
- Name a public dataset and its access route only when verified.
- Do not claim code access without a real repository, DOI, or author-approved route.
- Remove stale declaration files and text that contradict the selected route.

For a user-authorized generative-AI declaration removal:

1. verify the current journal, article-type, special-issue, publisher, and live-portal requirement;
2. if disclosure is optional or not applicable, remove the declaration from the manuscript source, compiled PDF/DOCX, title page, cover letter, standalone files, source/final ZIP contents, metadata table, upload map, and portal-answer draft wherever present;
3. preserve immutable original inputs and internal historical audit records, but label them as non-upload artifacts so they cannot be mistaken for current deliverables;
4. rebuild every derived artifact and run exact phrase plus semantic searches for the removed heading, tool names, and distinctive wording;
5. if disclosure is mandatory, mark `blocked-requirement-conflict`, retain truthful required disclosure in the prepared package, and obtain author direction rather than hiding use or entering a false portal answer.

If the portal says `Yes - included in manuscript`, select it only after confirming that the accepted manuscript contains the corresponding statement. If the prompt is ambiguous and the answer changes the manuscript, record its exact wording and obtain the user's decision.

## Gate F: Publishing Route and Cost

When the user requires zero APC:

- verify that the target journal currently offers a subscription/traditional route with no mandatory APC;
- check other currently disclosed mandatory author charges, including submission, page/excess-length, print-color, and required processing fees; record unknowns instead of promising total zero cost;
- record the evidence and date in `submission-constraints.md`;
- label the prepared route `subscription` or `traditional`, not open access;
- do not treat optional open access, waivers, discounts, or institutional agreements as guaranteed zero cost;
- do not select or confirm the final external publishing option without explicit authorization.

## Gate G: Package Integrity

After every accepted prose, author, metadata, or declaration change:

1. rebuild the manuscript PDF and all derived Word/PDF files;
2. rebuild source and final-delivery ZIPs;
3. compare normalized source hashes across working files and archive copies;
4. compare PDF extracted text after whitespace normalization, page count, ordered figure/table labels, reference labels/count, and author/title metadata; do not require byte-identical PDFs when timestamps differ;
5. extract the final source ZIP into a clean temporary directory and compile there;
6. inspect the clean-build log for errors and undefined citations/references, then render/inspect the PDF for missing or cropped figures, text outside margins, unintended blank/duplicate pages, unreadable text, and broken cross-references;
7. verify semantic equivalence: normalized main-source files match the accepted source; normalized extracted PDF text matches; page count and ordered figure/table/reference inventories match; any intentional compiler-only metadata difference is documented;
8. search the final PDF, editable source, source ZIP contents, cover letter, title page, standalone files, metadata, upload map, and portal draft for removed process/meta phrases and stale author/declaration text; record per-artifact results in the declaration-change record;
9. re-run the narrative map, limitation-placement ledger, and humanizer post-edit checks after any late packaging or metadata revision that changes manuscript text.

Stale, contradictory, non-compiling, or semantically different copies fail the gate.

## Gate H: Upload Map

Create `upload-map.md` from current journal instructions. Map each required file to its portal designation and accepted final path. Typical candidates include main manuscript, title page, cover letter, highlights, source archive, figures, supplementary material, checklist, and declaration of interests; include only files the current journal/form requests.

An upload map is preparation, not authorization to upload or submit.

## Red Flags - Stop Finalization

- `The deadline is close, so only fix the form fields.`
- `The old ZIP is probably the same.`
- `The PDF looks right, so metadata files need no check.`
- `The dataset is public, so code availability is implied.`
- `The journal is hybrid, so open access must be free.`
- `Humanizer should rewrite everything to avoid AI detection.`
- `This process paragraph proves reproducibility, so leave it in the paper.`

## Rationalization Checks

| Excuse | Required response |
|---|---|
| `The comparator score passed.` | Comparator quality does not override journal limits, professionalism blockers, or package inconsistency. |
| `The user asked for speed.` | Speed does not authorize a stale or contradictory package; reduce optional work, not hard gates. |
| `It is only a recommended statement.` | Record it as optional and follow the user's choice; do not present a recommendation as mandatory. |
| `The source compiled before.` | Metadata and prose changes invalidate the old build and ZIP; rebuild and clean-test. |
| `A separate AI statement is enough.` | Only if the current portal requests it and it does not contradict manuscript/portal answers. |
| `Open access can probably be waived.` | A possible waiver is not a verified zero-APC subscription route. |
