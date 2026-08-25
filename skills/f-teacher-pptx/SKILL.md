---
name: f-teacher-pptx
description: "Create, rebuild, or rigorously audit multi-lesson teaching PPTX decks for university, vocational, or training courses when the slides must be classroom-readable, logically taught from background through principles and details, genuinely image-rich, traceable to source materials, and verified page by page. Do not use for ordinary business or pitch decks."
metadata:
  short-description: "严格创建、重构、审计并逐页验收图文并茂的高质量教学课件"
---

# F Teacher PPTX

Build teaching decks as reproducible instructional artifacts, not as decorated summaries. A deck is complete only when its content contract, visual contract, final PPTX package, and rendered pages all pass.

## Required companion skill

Read the installed `presentations:Presentations` `SKILL.md` completely before touching a PPTX. Follow its runtime, `@oai/artifact-tool`, notes, rendering, and delivery requirements. This skill adds teaching-specific rules; when two rules differ, use the stricter classroom-readability or verification rule.

Use `imagegen` when a custom illustration materially improves a concept and no suitable source image exists. Use browser or web tools only when permitted and record the actual source URL, access date, and usage context.

## Modes

- **Create/rebuild:** inventory sources, design the lesson mainline, prepare assets, write lesson-plan JSON, build, render, inspect, fix, and deliver.
- **Audit/fix:** inspect the current PPTX and its renders, reconstruct missing provenance or plans as needed, fix every failed page, rerender, and re-audit. A request to inspect does not authorize edits; a request to improve or fix does.

## Mandatory artifact contract

Keep intermediate artifacts in a task-local writable directory and final deliverables in the user-selected course folder.

```text
task-work/
├── course-manifest.json
├── source-inventory.json
├── source-notes.txt
├── content-plans/lesson_NN.json
├── assets/                         # downloaded, extracted, or generated
├── build/                          # .mjs builders and deterministic metadata
├── staging/                        # candidate PPTX files
├── render/NN/
│   ├── slide-N.png                 # every rendered page
│   └── render-manifest.json        # final PPTX hash + every PNG hash
├── render/NN-montage.png           # navigation aid only
├── inspect/NN.ndjson
└── qa/
    ├── static-audit.json
    ├── qa-round-01.json
    └── final-qa.json
```

Do not deliver scratch artifacts unless asked. Preserve the original source archive and source decks unchanged. Archive an existing formal output before replacement when the user asks for a rebuild.

## Required workflow and gates

1. **Inventory before authoring.** Locate the syllabus, schedule, source archives/decks, templates, and current outputs. Hash inputs. Inventory every archive member, extract read-only, and explicitly map or exclude every teaching source member. Map source chapters/slides and reusable assets to each lesson. Read [source-assets.md](references/source-assets.md).
2. **Write the lesson mainline.** Define the communication job and sequence before layout. Each lesson normally contains `cover → background → roadmap → principle/detail → operation/case → pitfall → qa → summary`. Read [lesson-architecture.md](references/lesson-architecture.md).
3. **Create a slide-level content plan.** Every slide declares its teaching goal, body, source, visual asset(s), visual purpose, and mapping from each visual to a specific claim or step. Use [plan-schema.md](references/plan-schema.md).
4. **Pass the plan gate.** Run `scripts/validate_lesson_plan.py` in the local Conda environment. Zero plan errors are required. Do not build first and promise to add sources or pictures later.
5. **Prepare genuine visuals.** Every non-cover slide needs a semantic visual. At least 80% of non-cover slides must contain a genuine embedded photo, screenshot, data chart, document example, web image, or generated illustration occupying meaningful area; pure formulas/tables may use declared exceptions. At least 30% should use two or more independently useful visuals. For each major topic, actively scout relevant web/source images and prefer an accurate, memorable, student-engaging example over a generic stock image; “interesting” never excuses weak factual mapping. Read [visual-standard.md](references/visual-standard.md).
6. **Build from content, not page number.** Choose layout from the teaching job and available evidence. Never select left/right/card layout by slide-number modulo. Do not truncate content to make it fit a fixed template. Use `@oai/artifact-tool` JavaScript modules; do not use `python-pptx`.
7. **Use classroom typography.** Final exported cover title ≥60 pt; slide title ≥40 pt; ordinary instructional body ≥26 pt; diagram labels ≥20 pt; captions ≥16 pt. Footer/source text may be 12–14 pt. These are acceptance floors, not aspirational source constants. Only a focused code, formula, or dense-table region may use the documented 18–20 pt exception. A long slide must be split or reflowed, not silently shrunk.
8. **Grow the container before shrinking text.** Size text boxes from content. Keep at least 15% vertical breathing room after estimated text height and 8% horizontal reserve. If text clips or overflows, enlarge the box, reduce padding only within the standard, reflow siblings, or split the slide. Do not use shrink-to-fit below the font floors.
9. **Attach provenance.** Every slide has speaker notes using explicit non-empty fields: `[Sources]`, `knowledge.source: ...`, `visual.kind: ...`, `visual.purpose: ...`, and one `visual.asset: ...` line per visual with its source/path/URL or ImageGen prompt identifier. Notes must distinguish knowledge evidence from visual provenance. The plan-aware audit must match these identifiers back to the frozen plan; empty labels do not pass.
10. **Audit the exported PPTX.** Run `scripts/audit_teaching_pptx.py --plan ... --strict-text-capacity --strict-explicit-fonts` and the Presentation skill's `slides_test.py` on every final deck. The plan-aware check proves planned frozen images are embedded on their target pages; the strict capacity check rejects boxes whose estimated text height lacks the required breathing room; strict explicit-font mode rejects text whose final size cannot be proved. Zero corrupt files, missing notes, forbidden activity phrases, estimated text-capacity errors, unverified fonts, overflow errors, or out-of-canvas objects are allowed. These checks are conservative gates, not proof of visual correctness.
11. **Render every slide.** Render the final PPTX, not an earlier staging version. Hash-match formal and rendered candidates. A montage is only a navigation map.
12. **Inspect every page at full size.** Check text readability, clipping, wrapping, box overflow, text-image collisions, screenshot legibility, crop quality, image relevance, image density, factual/visual match, and repeated decoration. Record evidence and a concrete observation for each page; an unexplained row of all-true booleans is not a review. Read [qa-rubric.md](references/qa-rubric.md) and write the canonical v2 record in [qa-evidence-schema.md](references/qa-evidence-schema.md).
13. **Fix and rerender.** Any failed page reopens the gate. Rerender changed pages and rerun deck-level checks after global style changes. Completion requires all pages to pass, not merely absence of automated warnings.
14. **Deploy verified candidates.** Archive the previous formal outputs, then copy only verified staging files into the formal course folder and record each `formalPptx` path/hash.
15. **Validate the course evidence chain and prove identity.** Complete `course-manifest.json` and run `scripts/validate_course_manifest.py`. Read [course-manifest-schema.md](references/course-manifest-schema.md). Lesson order, source mapping, build inputs, staging/formal identity, plan/deck/render counts, hashes, renderer fingerprint, and one evidence-bearing QA record bound to each rendered page must all match. Report deck count, slide count, image/diagram mix, QA results, and archive location.

For exact commands, environment recording, manifests, and QA-round structure, read [reproducible-workflow.md](references/reproducible-workflow.md).

## Non-negotiable teaching rules

- Explain in plain language, then introduce terminology. Every technical term answers “what it is, why it matters, how it works, and what can go wrong.”
- Preserve enough detail to teach from the slide. Split dense material across more slides instead of converting explanations into vague labels.
- Student interaction is limited to direct Q&A unless the user explicitly asks otherwise. A Q&A page writes `问题：...` and `答案：...` directly. No peer talk, groups, voting, showcase, presentation, sharing, role-play, or mutual assessment.
- A colored rectangle, card, badge, arrow, divider, SmartArt block, or generic icon is not a picture and never satisfies the genuine-image requirement.
- Native diagrams are allowed only when they express a specific process, relationship, hierarchy, comparison, or derivation. Generic boxes that merely repeat the bullets fail.
- Do not fabricate operating-system or Office screenshots. Use real source screenshots, obtain a current relevant screenshot, or replace the screenshot with an honest explanatory diagram.
- Do not reuse the same foreground image within one lesson unless the repeated view is pedagogically necessary and documented.
- Do not use tiny whole-screen screenshots. Crop to the relevant region, annotate it, and ensure critical UI text is legible at 100% render size.
- Source deck logic may guide sequence and examples, but version-specific facts and obsolete UI must be corrected or labeled.

## Stop conditions

Do not claim completion when any required input is missing, the source archive cannot be read, a lesson lacks a mainline, planned visual assets are absent, image-density gates fail without documented subject-matter exceptions, automated checks fail, any rendered page remains uninspected, or the formal files do not hash-match the verified candidates.
