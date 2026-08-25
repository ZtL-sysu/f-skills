# Final QA Evidence Schema v2

Read this file before writing the final QA report. The purpose is to make page review auditable without pretending that semantic relevance or visual collision can be proved by a geometry script alone.

## Top-level record

```json
{
  "schemaVersion": 2,
  "round": 3,
  "pptxSha256": "...",
  "reviewer": {"type": "primary-agent", "name": "Codex"},
  "reviewedAt": "2026-08-22T18:30:00+08:00",
  "viewMode": "native-resolution",
  "render": {
    "renderer": "LibreOffice/Poppler via render_slides.py",
    "rendererVersion": "...",
    "command": "...",
    "renderedAt": "2026-08-22T18:00:00+08:00",
    "requestedWidth": 1600,
    "requestedHeight": 900,
    "actualWidth": 1600,
    "actualHeight": 900
  },
  "renderedPages": 25,
  "reviewedPages": 25,
  "pages": [],
  "status": "pass"
}
```

`reviewedAt` and `renderedAt` use ISO 8601 with a timezone. `viewMode` must be `100-percent` or `native-resolution`. Record the exact render command and a useful renderer/version fingerprint so the PNG set can be recreated.

## Per-page record

```json
{
  "slide": 7,
  "evidence": "render/07/slide-7.png",
  "evidenceSha256": "...",
  "actualWidth": 1600,
  "actualHeight": 900,
  "content": true,
  "typography": true,
  "container": true,
  "visualRelevance": true,
  "legibility": true,
  "collisionFree": true,
  "teachingFlow": true,
  "reviewNote": "标题单行完整；三条正文均在蓝色说明框内并留有下边距；右侧放大截图的菜单文字在原始分辨率下可读，标注 1–3 与步骤逐项对应；未见图文或页脚碰撞。",
  "assets": [
    {
      "assetSha256": "...",
      "mapsTo": [1, 2, 3],
      "cropMode": "contain",
      "visibleAreaRatio": 0.31,
      "relevanceVerdict": "pass",
      "observation": "截图直接展示正文所述菜单路径，关键区域完整且未被裁切。"
    }
  ],
  "issues": [],
  "status": "pass"
}
```

The review note must describe observable page evidence, not repeat “all checks passed.” It should name the title/wrapping state, text-container state, visual/crop/legibility state, and collision result. `evidenceSha256` and dimensions must match the render manifest and actual PNG.

For each counted foreground image, record the frozen asset hash, body-point mapping, crop mode, approximate visible slide-area ratio, relevance verdict, and a concrete observation. Use `contain`, `cover`, `crop`, `full-bleed`, or `native` for `cropMode`. If an asset is hidden, illegible, badly cropped, or unrelated, the page fails even if its OOXML box is large.

## Issue lifecycle

An issue discovered in any round is never erased. Record its category, observation, affected object/region when identifiable, disposition, and before/after evidence:

```json
{
  "id": "S07-I01",
  "category": "container",
  "observation": "第三条正文越过卡片下边界。",
  "objects": ["正文-3", "说明框"],
  "status": "resolved",
  "resolution": "说明框增高 0.38 英寸并下移截图；字号保持 26 pt。",
  "beforeEvidence": "qa/round-01/slide-7.png",
  "afterEvidence": "render/07/slide-7.png"
}
```

The final report may retain resolved issues but may not contain an open issue. A shared builder/style change requires rerendering and rereviewing every affected page, not just updating the JSON.
