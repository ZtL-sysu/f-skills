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

Use `imagegen` when a custom illustration or poster materially improves a concept. A source slide or source image does not remove this need when it preserves evidence but does not yet give students the required whole-view or mental model; in that case keep the source page and follow it with the generated explainer defined below. Use browser or web tools only when permitted and record the actual source URL, access date, and usage context.

## Mandatory imagegen poster-page policy

Treat a generated image as a teaching page, not as decoration. During lesson planning, review every major knowledge block and decide whether students need a single 16:9 poster-like image to form a mental model. Use `imagegen` for a full-slide or near-full-slide generated teaching poster when one of these jobs is present:

- **Whole-view poster:** introduce the overall appearance, system boundary, end-to-end loop, historical progression, family taxonomy, application landscape, or relationship among several parts before the lesson zooms into details.
- **Immediate follow-up explainer:** preserve a source-PPT page that carries accurate facts, terminology, tables, screenshots, or detailed bullets, then place a generated poster on the **immediately following slide** when the source page is correct but visually dense or abstract. The poster must retell the same knowledge through one memorable scene, comparison, process, cause-and-effect chain, before/after state, or annotated whole model. The source page supplies evidence and detail; the generated page supplies understanding and recall.
- **Local-concept poster:** after introducing a difficult local concept, add a generated page when students need to see a mechanism, state change, failure chain, feedback loop, spatial relationship, or “why this result follows” rather than another list of definitions.
- **Section synthesis poster:** use a poster after several detail pages to reconnect the parts, expose their dependencies, and bridge into the next section or question checkpoint.

### Imagegen-first teaching-benefit test

Do not treat image generation as a last resort and do not ask only whether native PowerPoint shapes *can* express the content. At outline and slide-pair planning time, compare two concrete candidates—native composition and a full-page generated teaching image—and choose the one that lets students understand the claim faster, remember it longer, and see the cause, scale, atmosphere, or relationship more directly. A coherent generated scene is preferred even when the same facts could technically be rebuilt from cards, icons, arrows, and text boxes.

Mark every knowledge block with `imagegen_candidate: yes/no` and record the reason. A `yes` is normally required when **any one** of these triggers is present:

- a history or evolution spans three or more stages, generations, time points, or visible forms;
- a scene needs three or more people, objects, devices, roles, or environmental elements to make the situation believable;
- an explanation contains three or more connected causes, state changes, actions, feedback links, or consequences;
- students must compare before/after, correct/failure, old/new, human/machine, local/whole, or several alternative outcomes at a glance;
- the knowledge point is best taught as a miniature story with a setting, motive, obstacle, action, result, and takeaway;
- scale, danger, emotion, spatial context, working environment, or historical atmosphere carries instructional meaning that isolated icons cannot convey;
- one coherent picture can replace several disconnected native cards while preserving a clear reading order;
- the supplied exemplar deck repeatedly uses a full-page image for the same teaching move;
- the existing/source slide is factually useful but abstract, dense, procedural, or emotionally flat, and an immediately following visual page would make the same point concrete.

The trigger is intentionally broad: `imagegen_candidate: yes` means the planner must either schedule the generated page or write a specific evidence-based exception. “能用形状做”“已经有一张配图”“页数会增加”“没有硬性配额” are not sufficient exceptions. Valid exceptions include exact software UI, inspectable source evidence, code, formulas, numerical tables, standards, exact device construction, editable data, or a case where generation would make the claim less verifiable. These exact materials remain native/source pages, but they may still be followed by a generated conceptual explainer.

Imagegen is a normal recurring teaching medium, not a rare special effect. Do not impose a blind numeric quota; however, if a lesson has several qualifying triggers but schedules only one or two generated teaching pages, the plan **fails by default** until the planner either adds the missing pages or documents each rejected candidate separately. A single decorative hero image does not satisfy this policy.

For a major background, origin, or development-history block, the plan must normally provide all four teaching moves, splitting them across pages when needed:

1. a whole-era overview poster that makes the complete path visible;
2. selected stage-detail pages that tell who acted, when and where it happened, what problem existed, and what changed;
3. a morphology-change visual showing how the object visibly evolved over time;
4. a causal bridge from that history to the system, practice, or device students use today.

If these moves are taught only as timelines, bullet lists, or portrait cards, the block fails the plan gate unless the source evidence itself is the lesson object. At least the overview, morphology change, or causal bridge should be evaluated for a full-page generated treatment, and every stage-detail page with a qualifying miniature story should be evaluated independently rather than hidden inside one summary poster.

### Exemplar-driven poster decisions

When the user supplies one or more self-made/reference decks, do not infer poster usage from generic presentation taste. Render and inspect the reference decks page by page before planning, identify every page whose main teaching surface is a single generated illustration or poster-like raster image, and inspect at least the immediately preceding and following pages. Record a `poster-use inventory` in the task evidence with the reference slide number, the surrounding knowledge point, whether the poster explains a whole system or a local concept, what the preceding page could not make vivid, and what teaching move the poster adds. The new deck's poster decisions must follow the recurring teaching patterns found in this inventory while still respecting factual accuracy and the current lesson's needs.

The inventory must distinguish at least these two user-intended uses:

- **整体图也会用:** a full-page generated poster gives students the first complete picture of an object, system, historical path, application world, or end-to-end loop. Use it at the entry to a major knowledge block or when returning from details to the whole.
- **局部概念也会用:** a full-page generated poster makes one difficult mechanism, relationship, state change, cause-and-effect chain, or failure consequence concrete. It normally follows the native/source knowledge page that introduced the concept.

When an existing PPT page already carries the correct knowledge point, preserve that page by default. If the reference-deck pattern or the concept's abstraction shows that an additional visual explanation is needed, insert the generated poster as the **very next slide**; do not replace the original page, move the poster to a remote section, or separate the pair with an unrelated example. The two-page teaching unit is `原页交代事实、术语或步骤 → 下一页用整页生图把同一知识讲活`. The poster must add an observable scene, analogy, relationship, process, consequence, or memory hook—not merely restyle the original text.

Before build, the plan gate must reject any proposed poster that lacks (1) a named preceding or surrounding knowledge page, (2) a declared whole-view or local-concept teaching job, (3) a statement of the understanding, recall, causal, contextual, or emotional benefit it contributes, or (4) a reason grounded in the imagegen-first test, the reference-deck inventory, or the concept's teaching difficulty. It must also reject a plan that has not listed every qualifying imagegen candidate, including candidates ultimately declined. After build, QA must inspect the source-page/poster pair consecutively at full size and confirm that the transition is immediate, the claim is continuous, and the poster genuinely deepens understanding.

Do not insert posters mechanically after every source slide. A poster is justified whenever it adds a whole-view, concrete scene, story continuity, visible cause and consequence, spatial or scale understanding, comparison, atmosphere, memory hook, or other clear teaching benefit—not only when it invents an entirely new mental model. It fails when it merely enlarges the previous bullets, repeats a keyword with decorative technology imagery, or interrupts a sequence that is already concrete. Exact numerical evidence, software UI states, code, formulas, standards, version tables, and operating steps remain on trustworthy source/native pages. A generated poster may explain them conceptually but must not replace or fabricate that evidence; mark schematic content as “示意” when students could mistake it for an exact interface, device, measurement, or implementation.

For every generated poster:

- Design for a 16:9 classroom slide and let the poster occupy the visual focus, normally at least 85% of the canvas. Keep the mandatory upper-right outline marker visible, either inside the verified poster or as a native overlay.
- Give `imagegen` the exact Simplified-Chinese wording and an explicit instruction for **very large classroom text**. At a 1600 × 900 final render, the main title should have at least about 50 px visible glyph height, ordinary explanatory text at least about 28 px, and necessary labels at least about 24 px. No required text may depend on zooming, tiny footnotes, or dense paragraph reading.
- Treat “字要大” as a rejection gate, not a prompt preference. Inspect the final rendered poster at normal full-slide view: every required Chinese label must be readable from the back of a classroom without zooming. If image generation produces small auxiliary copy, decorative microtext, garbled characters, or an accurate phrase at an unreadable size, regenerate or remove it; do not accept it merely because the main title is large.
- Prefer one dominant teaching claim, a clear reading order, and a small number of large visual groups. A taxonomy may contain more groups only when every label, image, and distinction remains legible at full-slide size; otherwise split it across multiple poster pages.
- Verify every Chinese character, technical term, number, arrow direction, object relationship, and implied cause. Regenerate when text is wrong, garbled, too small, or visually crowded. If image generation repeatedly cannot preserve exact text, generate the visual structure with minimal text and add large native PowerPoint text; never accept incorrect in-image wording.
- Give every generated-poster picture a meaningful OOXML accessibility title/description that names the poster and the knowledge point it explains. The metadata must let an audit distinguish a generated teaching poster from decoration and map it back to the planned slide; do not put prompt IDs, file paths, hashes, or provenance labels into the visible page or speaker notes.
- Record the generated asset, final prompt, prompt identifier, generation date, intended teaching claim, and mapping to the preceding or surrounding source slide in the lesson plan and sidecar evidence. Speaker notes remain talk-only and should tell the teacher how to read the poster, connect it to the preceding page, and state the takeaway.

A major conceptual section fails the plan gate when it contains a clear whole-view, story, history, comparison, context, abstract-mechanism, morphology-change, cause-and-effect, or synthesis trigger but neither a suitable source visual nor a planned generated poster performs that job. A lesson also fails when several recorded `imagegen_candidate: yes` items are silently omitted or dismissed with one generic justification. A source-page/poster pair fails QA when the two pages teach different claims, the poster adds no explanatory value, any embedded wording is inaccurate or too small, or the poster replaces evidence that students need to inspect directly.

### Generated-poster rejection patterns proven in production

Treat these as representative failure classes, not isolated cosmetic flaws:

- **Wrong arithmetic, scale, or mapping:** the rejected draft `05-overview` showed an incorrect hexadecimal positional relationship. Recompute every value, axis, proportion, unit, chart mapping, and formula independently; plausible-looking mathematics is not evidence. Any mismatch requires regeneration or a trustworthy native overlay.
- **Missing or malformed Chinese:** the rejected draft `07-overview` omitted the character “字” from “字符”. Compare every required phrase character by character against the approved copy. A missing character, substituted homophone, invented glyph, garbled label, or truncated technical term is a hard failure.
- **Unverifiable auxiliary microcopy:** the rejected draft `08-overview` added attractive but unreadable small text that could not be checked at slide scale. Reject decorative pseudo-text, unsupported annotations, and any label that cannot be verified at the final 1600 × 900 render. Remove it or regenerate with fewer, larger words.

The final visual review must open both the poster asset itself and the rendered three-slide sequence `preceding source page → generated poster → following page` at full size. Confirm exact wording and relationships on the asset, immediate adjacency and claim continuity in the sequence, and that the following page proceeds naturally rather than repeating or contradicting the poster. When an edit is intended to preserve all existing pages, hash- or pixel-compare every non-inserted rendered page against the accepted source render and record the count of exact matches.

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
2. **Write the lesson mainline.** Define the communication job and sequence before layout. Teach from whole to part: `引子/真实情境 → 先看对象的整体样貌 → 为什么需要它/发展背景 → 总体模型或工作闭环 → 分块拆解 → 原因与机制 → 细节、限制和失败 → 回到整体并解决开场问题`. Each knowledge block repeats the smaller cycle `它长什么样 → 为什么需要 → 怎样工作 → 哪些细节会改变结果`. At each whole-view, abstract-mechanism, and synthesis point, apply the mandatory imagegen poster-page decision above; when a source page needs visual clarification, keep it and place the poster immediately after it. Place the ideology page within slides 1–5. Distribute question checkpoints immediately after the knowledge sections they consolidate; never collect every question at the end. Read [lesson-architecture.md](references/lesson-architecture.md).
   - Group slides into a small, stable outline such as `课程导入 / 发展背景 / 概念边界 / 应用场景 / 任务闭环 / 软件协同 / 工程责任 / 复盘总结`. Every body slide must show its current outline category in a consistent upper-right marker. The marker is navigation, not a second title: keep its position, typography, and visual weight stable while the slide title remains page-specific.
   - For a non-practical lecture, plan at least 40 substantive slides unless the user sets a different length. Forty is a completeness floor, not a padding target.
   - A practice lesson may be shorter only when its deliverable, prerequisite, full worked path, intermediate checks, failure recovery, final acceptance criteria, distributed question checkpoints, and summary are all teachable from the deck.
   - Expand background encyclopedically: origins, historical stages, the problem each stage solved, competing approaches or families, mechanism, consequences, uses, limitations, and a bridge into the lesson's core operation. Give each causal or historical stage its own readable page when one page would be dense.
3. **Create a slide-level content plan.** Every slide declares its teaching goal, body, source, visual asset(s), visual purpose, and mapping from each visual to a specific claim or step. For each generated poster, state whether it is a whole-view, immediate follow-up, local-concept, or section-synthesis poster; identify the source slide or surrounding knowledge block it explains; and state the mental model it adds beyond the adjacent page. Use [plan-schema.md](references/plan-schema.md).
4. **Pass the plan gate.** Run `scripts/validate_lesson_plan.py` in the local Conda environment. Zero plan errors are required. Do not build first and promise to add sources or pictures later.
5. **Prepare genuine visuals.** Every non-cover slide needs a semantic visual. At least 80% of non-cover slides must contain a genuine embedded photo, screenshot, data chart, document example, web image, or generated illustration occupying meaningful area; pure formulas/tables may use declared exceptions. At least 30% should use two or more independently useful visuals. For each major topic, actively scout relevant web/source images and prefer an accurate, memorable, student-engaging example over a generic stock image; “interesting” never excuses weak factual mapping. Read [visual-standard.md](references/visual-standard.md).
6. **Build from content, not page number.** Choose layout from the teaching job and available evidence. Never select left/right/card layout by slide-number modulo. Do not truncate content to make it fit a fixed template. Use `@oai/artifact-tool` JavaScript modules; do not use `python-pptx`.
   Visible titles must sound like finished teaching or popular-science headings. State the page's question, claim, contrast, mechanism, or operation directly; never expose layout names, production terminology, generation rounds, review notes, source-processing remarks, or internal logs.
   Equivalent numbered steps, parallel options, or peer-level comparison panels must use the same fill, stroke, and typographic treatment. Do not highlight item 1 or any other peer with a different color unless the content explicitly establishes priority, status, correctness, risk, or selection and the slide explains that encoding.
7. **Use classroom typography.** Final exported cover title ≥60 pt; slide title ≥40 pt; ordinary instructional body ≥26 pt; diagram labels ≥20 pt; captions ≥16 pt. No slide may contain a page number, including `n / total`, isolated numeric folios, slide-number placeholders, or manually drawn page-number shapes. Body slides must not repeat the course name, course code, or a combined course-identity footer. These are acceptance floors, not aspirational source constants. Only a focused code, formula, or dense-table region may use the documented 18–20 pt exception. A long slide must be split or reflowed, not silently shrunk.
8. **Grow the container before shrinking text.** Size text boxes from content. Keep at least 15% vertical breathing room after estimated text height and 8% horizontal reserve. If text clips or overflows, enlarge the box, reduce padding only within the standard, reflow siblings, or split the slide. Do not use shrink-to-fit below the font floors.
9. **Write talk-only speaker notes.** Every slide has a non-empty oral script that the teacher can speak directly. Do not add headings such as `[讲授文案]` or `[Sources]`; do not place source labels, paths, URLs, hashes, prompt IDs, visual metadata, build notes, or QA tags in PowerPoint notes. Store provenance only in `source-notes.txt`, the lesson plan, asset records, build manifest, and QA evidence. The oral script should establish the situation, explain what triggered the problem, walk through the reasoning or operation, state the observable result, and close with the takeaway or transition. For a case or example, connect all five moves as a miniature story even when the visible slide is concise. Use natural transitions, concrete nouns, familiar comparisons, and rhetorical questions where helpful; do not merely read the bullets aloud or introduce unsupported facts.
10. **Audit the exported PPTX.** Run `scripts/audit_teaching_pptx.py --plan ... --strict-repeated-images --strict-text-capacity --strict-explicit-fonts` and the Presentation skill's `slides_test.py` on every final deck. The plan-aware check proves planned frozen images are embedded on their target pages, the ideology page is within slides 1–5, question pages are question-only and distributed, every page is free of page numbers, every page has talk-only notes, and body slides contain no course-identity footer; the strict capacity check rejects boxes whose estimated text height lacks the required breathing room; strict explicit-font mode rejects text whose final size cannot be proved. Zero corrupt files, missing or metadata-contaminated notes, page numbers, forbidden activity phrases, answer-labelled question pages, course-identity footers, estimated text-capacity errors, unverified fonts, overflow errors, or out-of-canvas objects are allowed. These checks are conservative gates, not proof of visual correctness.
11. **Render every slide.** Render the final PPTX, not an earlier staging version. Hash-match formal and rendered candidates. A montage is only a navigation map.
12. **Inspect every page at full size.** Check text readability, clipping, wrapping, box overflow, text-image collisions, screenshot legibility, crop quality, image relevance, image density, factual/visual match, repeated decoration, ideology relevance, question placement, answer leakage, and course-identity footer leakage. For generated posters, additionally verify exact Chinese wording, technical accuracy, reading order, classroom-scale text, source-page pairing, and the specific new mental model contributed by the poster. Record evidence and a concrete observation for each page; an unexplained row of all-true booleans is not a review. Read [qa-rubric.md](references/qa-rubric.md) and write the canonical v2 record in [qa-evidence-schema.md](references/qa-evidence-schema.md).
13. **Fix and rerender.** Any failed page reopens the gate. Rerender changed pages and rerun deck-level checks after global style changes. Completion requires all pages to pass, not merely absence of automated warnings.
14. **Deploy verified candidates.** Archive the previous formal outputs, then copy only verified staging files into the formal course folder and record each `formalPptx` path/hash.
15. **Validate the course evidence chain and prove identity.** Complete `course-manifest.json` and run `scripts/validate_course_manifest.py`. Read [course-manifest-schema.md](references/course-manifest-schema.md). Lesson order, source mapping, build inputs, staging/formal identity, plan/deck/render counts, hashes, renderer fingerprint, and one evidence-bearing QA record bound to each rendered page must all match. Report deck count, slide count, image/diagram mix, QA results, and archive location.

For exact commands, environment recording, manifests, and QA-round structure, read [reproducible-workflow.md](references/reproducible-workflow.md).

## Non-negotiable teaching rules

- Explain in plain language, then introduce terminology. Every technical term answers “what it is, why it matters, how it works, and what can go wrong.”
- Preserve enough detail to teach from the slide. Split dense material across more slides instead of converting explanations into vague labels.
- Treat every example as a miniature story. The visible page must at least state the setting or problem and the observable outcome; the talk-only notes must connect background → trigger → handling process → result → teaching takeaway. A page that jumps straight to “how to do it” without explaining why the situation arose fails even when its image is relevant.
- Keep visible explanations complete but restrained: prefer plain causal sentences over compressed slogans, unexplained noun phrases, or keyword piles. Move additional context and storytelling into the oral notes rather than reducing the body font or crowding the page.
- The upper-right outline marker is mandatory on body slides and must remain visually subordinate to the unique slide title. Use the same category wording across a section; change it only when the lesson mainline advances to a new section.
- Peer-level `1 / 2 / 3` panels and equivalent dialogue boxes must be visually identical. A color difference is semantic evidence and therefore requires an explicit legend or explanation; accidental first-item emphasis fails review.
- Every deck contains exactly one lesson-related course-ideology page within slides 1–5. Tie it to the current lesson through concrete engineering conduct such as rigorous study, factual measurement, reproducibility, safety responsibility, collaboration, research integrity, national technological capability, or serving real public needs. It must encourage learning and 科技兴国 without becoming a generic slogan page; use relevant evidence or imagery and record provenance normally.
- No slide may display a page number. Body slides must not show a repeated course name, course code, or combined course-identity footer. Necessary source lines may appear only when they are audience-relevant and do not recreate the prohibited identity footer; full provenance remains in sidecar evidence, never in speaker notes.
- Student interaction is limited to teacher-led question checkpoints unless the user explicitly asks otherwise. A question page presents `问题：...` plus optional follow-up questions or an evidence requirement, but never `答案：...`, “参考答案”, “正确答案”, “直接问答”, or an answer paragraph. No peer talk, groups, voting, showcase, presentation, sharing, role-play, or mutual assessment.
- Place each question page directly after the knowledge section it consolidates. Use it to summarize, strengthen recall, prompt evidence-based reasoning, or bridge to the next section. For lessons with multiple question pages, spread them across the lesson; clustering all of them near the end fails.
- A colored rectangle, card, badge, arrow, divider, SmartArt block, or generic icon is not a picture and never satisfies the genuine-image requirement.
- Native diagrams are allowed only when they express a specific process, relationship, hierarchy, comparison, or derivation. Generic boxes that merely repeat the bullets fail.
- Do not fabricate operating-system or Office screenshots. Use real source screenshots, obtain a current relevant screenshot, or replace the screenshot with an honest explanatory diagram.
- Do not reuse the same foreground image within one lesson unless the repeated view is pedagogically necessary and documented.
- Do not use tiny whole-screen screenshots. Crop to the relevant region, annotate it, and ensure critical UI text is legible at 100% render size.
- Treat every crop edge as evidence. A crop fails if it contains the top/bottom of an adjacent row, half of a neighboring card, a clipped label, a lone punctuation mark, a black padding strip, or a fragment of the previous/next webpage region. Re-crop from the source and inspect the crop itself before rebuilding.
- A screenshot that teaches a directory, archive, before/after state, or multi-step operation must visibly match every claimed object and state. Showing a command button does not prove its result; showing an application installation folder does not prove the contents of a project archive. Use paired overview/result images or rewrite the claim to the state actually visible.
- Source deck logic may guide sequence and examples, but version-specific facts and obsolete UI must be corrected or labeled.

## Stop conditions

Do not claim completion when any required input is missing, the source archive cannot be read, a lesson lacks a mainline, the ideology page is absent or outside slides 1–5, question pages contain answers or are clustered at the end, a body slide repeats the course name/code footer, planned visual assets are absent, image-density gates fail without documented subject-matter exceptions, automated checks fail, any rendered page remains uninspected, or the formal files do not hash-match the verified candidates.
