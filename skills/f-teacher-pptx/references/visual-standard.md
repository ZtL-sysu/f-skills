# Visual and Layout Standard

Read this file before choosing layouts or placing text and images.

## Canvas and safe area

- Default to 16:9 widescreen.
- Keep audience-facing content inside a consistent safe area. On a 13.333 × 7.5 inch slide, use about 0.65–0.8 inch left/right margins and 0.3–0.45 inch top/bottom margins unless a full-bleed image is intentional.
- Reserve the footer band before sizing the content area. Do not let diagrams, captions, or screenshots drift into it.
- Use a small set of content-led layouts: image-led explanation, annotated screenshot, full-width process, comparison, worked example, evidence/chart, direct Q&A, and summary. Vary adjacent silhouettes when the content supports it.

## Classroom typography

Hard floors are acceptance gates, not design targets.

| Role | Preferred | Hard floor |
|---|---:|---:|
| Cover title | 64–72 pt | 60 pt |
| Slide title | 42–48 pt | 40 pt |
| Section/card heading | 30–34 pt | 28 pt |
| Main instructional body | 28–32 pt | 26 pt |
| Diagram/process label | 22–24 pt | 20 pt |
| Screenshot annotation | 20–24 pt | 18 pt |
| Caption/source line | 16–18 pt | 16 pt |
| Footer/page number | 12–14 pt | 12 pt |

These are **final PowerPoint point sizes after export**. Do not assume the builder's numeric `fontSize` is already a PowerPoint point value. Some Artifact Tool/runtime paths serialize a CSS-pixel-like value at roughly 0.75 PowerPoint points; calibrate a sample, inspect the exported OOXML/render, and use about `target_pt / 0.75` (for example, about 37.3 builder units for a 28 pt final body) when that runtime exhibits the conversion. The final PPTX and render, not the source constant, determine compliance.

Use the preferred range for new or rebuilt slides. The hard floor is only the rejection boundary; do not set every body paragraph to 26 pt merely because it passes. Give every visible text object a semantic name that identifies its role (`封面标题`, `标题`, `卡片标题-*`, `正文-*`, `流程文字-*`, `代码-*`, `公式-*`, `表格-*`, `标注-*`, `图注-*`, `页脚`) and an explicit font size so the exported deck can be audited without guessing inherited typography.

Code, formulas, and dense data tables may use 18–20 pt only when the page contains a focused magnified region and no more than one such exception. Never shrink an entire page to preserve a fixed layout.

Titles intended for one line must not wrap. Shorten the title or change the title region. Do not reduce a slide title below 40 pt.

## Text-box growth rule

The container follows the content; content does not get crushed into a template.

1. Choose the font size from the table before choosing box height.
2. Set deliberate internal padding: at least 0.12 inch vertically and 0.16 inch horizontally for normal cards; larger for prominent callouts.
3. Estimate line count using the actual font and available width. Use `estimated text height = line_count × font_size × 1.25` and add top/bottom padding.
4. Make the container at least 15% taller than the estimate and keep roughly 8% horizontal reserve.
5. Render and inspect. Heuristics never replace the rendered result.

When text does not fit, use this order:

1. Enlarge the text box or card.
2. Reflow siblings or switch from columns to a wider single column.
3. Shorten redundant wording without removing logic.
4. Split the slide at a semantic boundary.
5. Use a documented exception only for code/formulas/tables, never below the applicable hard floor.

Forbidden fixes: shrink-to-fit below the floor, clipping, hiding overflow, placing text outside its box, reducing line spacing until glyphs collide, or truncating text with an ellipsis.

After layout, check the text itself, not just the box geometry. A box may remain inside the slide while its text still escapes or overlaps adjacent content.

## Genuine-image requirement

A “genuine visual” is a photo, software screenshot, document example, data chart, map, real object, relevant web illustration, generated illustration, or content-specific diagram that materially explains the page.

A **genuine image asset** is an embedded raster/vector picture or rendered chart/document asset, not a PowerPoint rectangle or text shape.

Default lesson gates, excluding the cover:

- 100% of slides have a semantic visual.
- At least 80% contain one or more genuine image assets occupying meaningful area.
- At least 30% contain two or more independently useful visuals, such as before/after, overview/detail, input/output, or example/result.
- No more than two consecutive slides may be diagram-only.
- Every major topic section contains at least one real screenshot, photo, document example, data chart, or generated illustration.

Pure formula, pure derivation, or dense table pages may declare a subject-matter exception. Each exception must state why an image would reduce clarity and still use a content-specific equation, table, or diagram. Exception pages may not exceed 20% of non-cover slides by default.

A rectangle, rounded card, badge, pill, divider, generic icon, arrow, SmartArt block, timeline made only of shapes, or enlarged title is not a genuine image. It cannot satisfy the 80% image-asset gate.

## Relevance and visual mapping

Every visual asset must map to a specific claim, step, example, or comparison in the body. Record the mapping in the lesson plan.

Reject an image when:

- it merely matches a broad keyword but not the page's actual claim;
- it is decorative technology imagery behind unrelated text;
- it repeats another slide without a new pedagogical purpose;
- it shows a different software version or command without labeling the difference;
- the important region is too small to read;
- the crop removes necessary context;
- it contradicts the title, formula, data, or operation being taught.

## Engagement value and web-image scouting

For every major topic, search the supplied sources first and scout the web when permitted. The goal is not decoration: choose visuals that make students look twice and understand faster. Prefer, in order, a real device or real-world scene, a revealing before/after or failure example, an annotated interface/detail, a surprising but accurate comparison, or a restrained humorous/curious image whose connection can be stated in one sentence.

Record an `engagementReason` for each externally scouted or generated image. It must name the concrete hook, such as “shows the robot's lidar blind zone in a real corridor” or “contrasts a tidy and tangled cable layout so the wiring rule is memorable.” Reject vague claims such as “more interesting,” “adds atmosphere,” or “technology feel.”

An engaging image still fails when it is only keyword-related, visually loud but instructionally empty, culturally insensitive, misleading, low-resolution, watermarked beyond acceptable educational use, or impossible to trace. Freeze the exact downloaded asset and record its landing-page URL, direct asset URL when available, access date, creator/site, license or usage note when known, crop/annotation performed, and claim mapping. Never hotlink during the final build.

## Screenshot and chart legibility

- Crop to the relevant region and preserve enough context to identify the interface.
- Use numbered annotations, callout lines, or a paired overview/detail view.
- If key UI text is not legible at 100% rendered slide size, the screenshot fails even if its source resolution is high.
- Do not stretch images. Use contain/crop behavior deliberately.
- Prefer one large readable screenshot over four tiny screenshots.
- For charts, state the question, units, time range, categories, and conclusion. Remove 3D effects, heavy shadows, and unnecessary gridlines.

## Layout anti-patterns

- A dashboard of many same-size cards when the audience needs one coherent explanation.
- Repeating the body a second time inside a diagram.
- Choosing layout by odd/even slide number or slide-number modulo.
- A tiny image in a corner used only to satisfy an image count.
- Full-screen screenshots shrunk until interface text is unreadable.
- Text floating over a busy image without contrast or safe positioning.
- Connectors crossing labels or nodes.
- A title/body mismatch, wrong chart type, wrong screenshot, or unrelated decorative visual.
