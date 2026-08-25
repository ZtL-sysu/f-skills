# Reproducible Workflow

Read this file when executing a complete create/rebuild/audit project.

## 1. Environment

Run project code inside the user's local Conda environment. Use the workspace dependency loader for the exact bundled Node, Python, module, and binary paths required by the Presentation skill. Do not install substitute runtimes or packages unless the user authorizes it.

Record in `qa/final-qa.json`:

- Conda environment name;
- runtime paths and bundle version;
- builder path and SHA-256;
- source inventory SHA-256;
- plan hashes;
- output PPTX hashes;
- render timestamp and page counts;
- validator command lines and exit codes.

## 2. Source preparation

1. Use `rg --files` and targeted `find` calls to inventory the course folder.
2. Hash source archives, decks, syllabus, schedule, and template.
3. Extract archives into task-local staging without modifying originals.
4. Render or inspect every source deck sufficiently to understand its teaching order and reusable assets.
5. Create `source-inventory.json` and `source-notes.txt` before drafting.

Create the archive inventory before extraction:

```bash
conda run -n <env> python \
  /absolute/path/f-teacher-pptx/scripts/inventory_archive.py \
  /absolute/path/source.rar \
  --json-out /absolute/path/task-work/source-archive-inventory.json
```

## 3. Content plan gate

Write one JSON plan per lesson. Validate all plans:

```bash
conda run -n <env> python \
  /absolute/path/f-teacher-pptx/scripts/validate_lesson_plan.py \
  /absolute/path/task-work/content-plans \
  --json-out /absolute/path/task-work/qa/plan-audit.json
```

During online image scouting only, `--pre-freeze` permits URL-only assets. After download/extraction/generation, add path, hash, dimensions, date, source, purpose, mapping, and alt text, then rerun without `--pre-freeze`. Do not build while errors remain. Warnings require explicit review; they are not automatically acceptable.

Save the final zero-error, zero-warning JSON report and its exact command/exit code as the lesson's `planAudit` record in `course-manifest.json`. The report must identify the exact lesson-plan path. A `--pre-freeze` report is draft evidence and cannot be used as the final `planAudit`.

## 4. Asset freeze

- Extract, download, or generate all planned assets.
- Rasterize unsupported formats with the Presentation skill helpers.
- Store source URL/prompt, access/generated date, local path, dimensions, and SHA-256.
- Verify all planned paths exist and no same foreground asset is reused without a reason.
- Freeze assets before the final build so later network changes cannot alter the deck.

## 5. Authoring

- Use a task-local `.mjs` builder and `@oai/artifact-tool`.
- Call the Presentation skill's artifact-operation marker exactly as instructed.
- Keep the builder deterministic: stable slide order, explicit sizes, fixed inputs, no network calls during export, and no current-time content in visible slides unless required.
- Name objects by semantic role (`标题`, `正文-1`, `截图-设置窗口`, `图注-1`) so inspection can distinguish typography roles.
- Calibrate the runtime's font-size unit with a one-slide export. If exported OOXML records roughly 0.75 pt per builder unit, multiply desired final point sizes by 1.333 in the builder; verify the final file rather than trusting source constants.
- Put connectors behind nodes, and keep connectors away from labels.
- Add speaker notes with knowledge and visual provenance on every slide.
- Write one `build/lesson_NN-build.json` with the builder record `{path, sha256}`, `sourceInventorySha256`, `planSha256`, sorted unique `assetSha256s`, runtime fields `{node, nodeModules, binDir, nodeVersion, artifactToolVersion}`, the exact `exportCommand`, optional deterministic `seed`, and `outputPptxSha256`. Paths may be absolute or relative to the build manifest. A build cannot be called reproducible when only its output is retained.

## 6. Static export audit

Run the skill audit and the Presentation skill overflow test on each deck:

```bash
conda run -n <env> python \
  /absolute/path/f-teacher-pptx/scripts/audit_teaching_pptx.py \
  /absolute/path/task-work/staging/lesson_01.pptx \
  --plan /absolute/path/task-work/content-plans/lesson_01.json \
  --strict-repeated-images \
  --strict-text-capacity \
  --strict-explicit-fonts \
  --json-out /absolute/path/task-work/qa/static-audit.json

conda run -n <env> env \
  RUNTIME_NODE=<loader-node> \
  RUNTIME_NODE_MODULES=<loader-node-modules> \
  RUNTIME_BIN_DIR=<loader-bin> \
  <loader-python> <presentation-skill>/container_tools/slides_test.py \
  /absolute/path/task-work/staging/lesson.pptx
```

Run `slides_test.py` for every deck. Do not infer that all decks pass because one representative deck passes.

Capture the strict audit JSON and the complete `slides_test.py` stdout/stderr in files. Store their exact commands, exit codes, paths, and SHA-256 values as `staticAudit` and `slidesTest` in the lesson manifest. The strict audit command must retain `--strict-repeated-images`, `--strict-text-capacity`, and `--strict-explicit-fonts`.

## 7. Render and inspect

Render every final slide to PNG at no less than 1600 × 900 for a 16:9 deck. Use the Presentation skill's bundled renderer with the exact runtime returned by the workspace dependency loader:

```bash
conda run -n <env> env \
  RUNTIME_NODE=<loader-node> \
  RUNTIME_NODE_MODULES=<loader-node-modules> \
  RUNTIME_BIN_DIR=<loader-bin> \
  <loader-python> <presentation-skill>/container_tools/render_slides.py \
  /absolute/path/task-work/staging/lesson_01.pptx \
  --output_dir /absolute/path/task-work/render/01 \
  --width 1600 --height 900
```

Keep the renderer path/version, full command, render timestamp, requested dimensions, and actual dimensions of every PNG in the QA evidence. Build a montage only to navigate the deck. Review every page at 100% or full-resolution image view.

Create `qa/qa-round-NN.json` using [qa-evidence-schema.md](qa-evidence-schema.md). A minimal abbreviated record is shown below; the final v2 report must also include reviewer, renderer, page hash/dimensions, `reviewNote`, and asset observations:

```json
{
  "schemaVersion": 2,
  "round": 1,
  "pptxSha256": "...",
  "renderedPages": 24,
  "reviewedPages": 24,
  "pages": [
    {
      "slide": 1,
      "evidence": "render/04/slide-1.png",
      "content": true,
      "typography": true,
      "container": true,
      "visualRelevance": true,
      "legibility": true,
      "collisionFree": true,
      "teachingFlow": true,
      "reviewNote": "Describe the visible evidence for typography, containers, visuals, and collisions.",
      "status": "pass",
      "issues": []
    }
  ],
  "status": "fail"
}
```

The final round must list every page exactly once and identify the final PPTX SHA-256. Create `render-manifest.json` with that same PPTX hash and the SHA-256 of every PNG. A review record without all category booleans, evidence hash/dimensions, or a concrete observation is incomplete.

After fixes, export a new PPTX, rerun static checks, rerender, and produce the next QA round. Never modify the QA record to pretend an earlier render passed.

## 8. Independent review

For large or high-risk packages, assign a read-only reviewer a bounded page range. Give the reviewer full-resolution renders and the rubric, not the builder's intended result. Integrate concrete findings and rerender the affected pages. Independent review supplements, not replaces, the primary page-by-page review.

## 9. Deployment

1. Archive the pre-rebuild formal deck set.
2. Copy only the verified staging PPTX files to the formal folder and record each as `formalPptx`.
3. Compare per-file SHA-256 between staging and formal directories.
4. Recount final PPTX files and internal slides.
5. Confirm the course name/code and lesson identity in the formal files.
6. Validate the entire course contract:

```bash
conda run -n <env> python \
  /absolute/path/f-teacher-pptx/scripts/validate_course_manifest.py \
  /absolute/path/task-work/course-manifest.json \
  --json-out /absolute/path/task-work/qa/course-manifest-audit.json
```

7. Deliver only after hashes, counts, and QA reports all pass.

## 10. Final report

Report:

- final folder and files;
- deck and slide counts;
- lesson-plan validation result;
- genuine-image, diagram, screenshot/photo/generated-image counts;
- overflow-test result for every deck;
- number of rendered and reviewed pages;
- issues fixed in the final round;
- archive location and hash-match result.

Do not claim “visual QA completed” without a reviewed-page count equal to the rendered-page count.
