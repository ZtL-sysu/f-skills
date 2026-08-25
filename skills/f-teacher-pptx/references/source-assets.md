# Source and Asset Workflow

Read this file when the task includes source archives, inherited decks, web images, or generated images.

## Source inventory

Before writing content:

1. Locate the syllabus, teaching schedule, course identity, source archive, source PPTX files, templates, and formal output directory.
2. Record absolute path, size, SHA-256, modification time, and role in `source-inventory.json`.
3. Preserve source files. Run `scripts/inventory_archive.py` for every ZIP/RAR/7z file before extraction. The inventory records the original member listing hash, tool version, member paths, sizes, and content hashes; duplicate, dangerous, symlink, or listing/extraction-mismatch paths fail. Extract into a task-local read-only staging area; never overwrite the archive. If no supported RAR tool exists, stop and report the exact missing dependency instead of silently skipping the archive.
4. Inventory each source deck by chapter, slide count, titles, text volume, pictures, charts, tables, and notes.
5. Render source decks or make contact sheets so the sequence and useful pages can be reviewed visually.
6. Build a mapping from course lesson → source chapter/slides → reusable facts/examples/assets.
7. Map every relevant archive member to a lesson or record it in `excludedSourceMembers` with a concrete reason. “Not used” is not a reason.

Source decks are teaching evidence, not design authority unless the user explicitly names them as a template. Reuse their logic, facts, screenshots, examples, and real images selectively.

## Source quality decisions

- Preserve the source lesson order when it is pedagogically sound; reorganize only with a documented reason.
- Correct obvious errors, corrupt formulas, mismatched charts, and obsolete interface assumptions.
- Label version-dependent screenshots. Do not imply that an old Windows/Office interface is current.
- Do not remove necessary conditions, variables, units, or data just because a source page is dense.
- When a screenshot is unreadable, extract the original image, find a higher-quality equivalent, take an authorized current screenshot, or replace it with an honest diagram.

## Asset priority

Use this order:

1. Relevant high-quality asset already present in the source teaching material.
2. Official or primary-source screenshots, diagrams, photos, or datasets.
3. Reputable educational, museum, institutional, or documentation images.
4. A purpose-built ImageGen illustration when a concept is abstract or no suitable real asset exists.
5. A native diagram only when relationships are clearer as shapes than as a sourced image.

Never fabricate a software screenshot. Do not use stock “person at laptop” imagery where an actual workflow, object, document, or result can be shown.

## Web-image record

For each major topic whose supplied sources do not already contain a strong visual, create a small scouting log before download. Record the search query, two to five plausible landing pages, the selected candidate, and concrete rejection reasons for the others (for example: wrong software version, subject too small, unclear license, watermark, low resolution, or only keyword-related). This makes “find more interesting images” a repeatable selection process instead of an undocumented taste judgment.

For every downloaded or linked image record:

- page URL and direct asset URL when available;
- title/creator or organization;
- access date;
- license or usage note if visible;
- local filename and SHA-256;
- target lesson/slide;
- the exact claim or step it explains.
- the scouting-log entry and why this candidate is more memorable or revealing than the rejected alternatives.

Prefer images whose provenance and usage terms are clear. If licensing is uncertain, keep the image out of the deliverable or ask the user.

## ImageGen record

Use ImageGen for a new illustration only after specifying the target frame and teaching job. Save:

- the complete prompt;
- generated date;
- output path and hash;
- target slide and crop intent;
- a note that the image is illustrative rather than documentary evidence.

Prompts should name the subject, composition, viewpoint, aspect ratio, negative space for text, and elements that must or must not appear. Do not ask ImageGen to create legible software UI, formulas, dense labels, or factual charts.

## Asset acceptance

An asset passes only if:

- it is technically readable and not visibly compressed;
- its content matches the page's title and body;
- the selected crop keeps the teaching subject intact;
- it adds information, emotion, comparison, evidence, or orientation;
- it is not repeated within the lesson without a documented new purpose;
- it has speaker-note provenance and alt text.

For a normal 16:9 slide, a single explanatory image should usually occupy at least 25% of the slide. An image smaller than 8% of slide area cannot count toward the image-density gate unless it is one of several meaningful detail images.
