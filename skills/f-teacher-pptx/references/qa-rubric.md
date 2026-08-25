# QA Rubric and Completion Gates

Read this file before the first render review and again before delivery.

## Machine gates

All are required:

- PPTX is a valid ZIP/OOXML package.
- Expected file and slide counts match.
- Course/lesson identity is correct.
- Every slide has speaker notes with `[Sources]`, `visual.kind`, and `visual.purpose`.
- No forbidden classroom-activity phrases.
- Plan and final deck satisfy image-density thresholds or documented exceptions.
- No repeated foreground images without approval.
- Typography meets role-specific floors.
- Strict text-capacity estimation passes for every deck; this supplements rather than replaces rendered inspection.
- No instructional text shape relies on shrink-to-fit; boxes grow, reflow, or split instead.
- `slides_test.py` reports no overflow for every deck.
- Object inspection reports no unintended out-of-canvas elements.
- Formal files hash-match the verified staging files.
- Frozen plan asset hashes are found in the corresponding slide media.
- Render manifest identifies the final PPTX and hashes every rendered PNG.
- QA evidence records the renderer command/version, render time, requested resolution, and actual PNG dimensions.
- Final QA contains one fully populated record for every rendered page.
- Final QA uses schema v2, records reviewer/time/view mode and the renderer fingerprint, and binds each page to the exact PNG hash and dimensions.

Machine gates cannot judge whether a picture is relevant, whether a crop is useful, or whether a page teaches clearly. They never replace visual review.

## Full-size page review

Review each rendered PNG individually. Record pass/fail for every category:

### Content

- Title and body describe the same concept.
- The page has one clear teaching job.
- Explanation is plain, complete, and logically connected.
- Terms, numbers, formulas, dates, units, and references are correct.
- A screenshot, chart, or example matches the described operation/result.
- No production notes, unresolved placeholders, or raw source captions leak into visible content.

### Typography and containers

- Slide title is large, single-line when intended, and not clipped.
- Body text is readable from a classroom projection distance.
- No text crosses a card or box boundary.
- No glyph, line, bullet, formula, or caption is clipped.
- Text has sufficient padding and line spacing.
- A container has grown with its content; there is visible breathing room rather than edge-hugging text.
- No small-font workaround was used to save a crowded layout.

### Images and charts

- Every visual is relevant to a named body point.
- Genuine image coverage meets the lesson policy.
- Critical screenshot text is legible at 100%.
- Crop, aspect ratio, and resolution are clean.
- A photo is not decorative filler.
- Externally scouted/generated visuals have a concrete engagement hook and provenance; “technology atmosphere” does not count.
- A diagram adds relationships or mechanism rather than duplicating bullets.
- Charts use the correct type, labels, units, ranges, and data.
- No same foreground image repeats without a new purpose.

### Spatial layout

- No text-text, text-image, image-image, or connector-label collision.
- No object unintentionally leaves the canvas.
- Alignment, margins, and footer placement are consistent.
- The page does not look like a dense dashboard of tiny cards.
- Visual weight is balanced; the image is not a token thumbnail.
- Adjacent slides do not repeat an identical layout without a content reason.

### Teaching flow

- The page follows naturally from the previous page.
- The next page is prepared by the current conclusion or question.
- Operations include checks or observable results.
- Pitfalls pair each error with its correct handling.
- Q&A states both the question and answer directly.
- Summary closes the opening problem rather than starting new content.

## Severity

- **Fail:** clipping, overflow, collision, unreadable body/screenshot, wrong formula/chart/image, missing source, fake visual, forbidden activity, or broken teaching logic. Must fix.
- **Major:** weak relevance, insufficient image density, vague explanation, repeated decorative layout, or misleading crop. Must fix before delivery.
- **Minor:** small spacing inconsistency or polish issue that does not harm teaching. Fix when it occurs in a repeated component or is conspicuous.

## Review protocol

1. Check the montage for sequence and density only.
2. Open every page at full size and complete the rubric.
3. Open suspicious pages at native resolution; do not judge fine text from a montage.
4. Fix the underlying content or layout, not only the symptom.
5. Rerender every changed page. If a shared style or builder function changed, rerender all decks affected by it.
6. Recount rendered and reviewed pages. The two numbers must match.
7. Run machine gates again after the final export.
8. Write an observable `reviewNote` for every page and asset-level crop/relevance observations for every counted foreground image. A repeated generic sentence or unexplained all-true checklist fails the evidence gate.

## Completion statement

A valid completion statement includes exact evidence, for example:

```text
16 decks / 417 slides exported; 417/417 pages rendered and reviewed;
16/16 overflow tests passed; plan and package audits passed;
formal/staging SHA-256 matched for 16/16 files.
```

Avoid unsupported language such as “looks fine,” “spot-checked,” or “should be okay.”
