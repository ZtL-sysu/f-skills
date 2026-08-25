# Course Manifest Schema

Use one `course-manifest.json` to close the gap between syllabus/schedule, lesson plans, final decks, renders, and QA records. Paths may be absolute or relative to the manifest.

```json
{
  "courseName": "机器人技术基础（微专业）",
  "courseCode": "HW350102",
  "formalDirectory": "../正式课件",
  "syllabus": {"path": "sources/课程大纲.docx", "sha256": "..."},
  "schedule": {"path": "sources/教学进度表.xlsx", "sha256": "..."},
  "sourceInventory": {"path": "source-inventory.json", "sha256": "..."},
  "archiveInventories": [
    {"id": "robot-source", "path": "source-archive-inventory.json", "sha256": "..."}
  ],
  "sourceFiles": [],
  "lessons": [
    {
      "lessonNumber": 1,
      "lessonTitle": "认识机器人系统",
      "sourceMembers": ["robot-source::第一章/机器人概述.pptx"],
      "plan": {"path": "content-plans/lesson_01.json", "sha256": "..."},
      "planAudit": {
        "command": "conda run -n course-env python .../validate_lesson_plan.py .../lesson_01.json --json-out .../lesson_01-plan-audit.json",
        "exitCode": 0,
        "report": {"path": "qa/lesson_01-plan-audit.json", "sha256": "..."}
      },
      "buildManifest": {"path": "build/lesson_01-build.json", "sha256": "..."},
      "pptx": {"path": "staging/lesson_01.pptx", "sha256": "..."},
      "staticAudit": {
        "command": "conda run -n course-env python .../audit_teaching_pptx.py ... --strict-repeated-images --strict-text-capacity --strict-explicit-fonts --json-out .../lesson_01-static-audit.json",
        "exitCode": 0,
        "report": {"path": "qa/lesson_01-static-audit.json", "sha256": "..."}
      },
      "slidesTest": {
        "command": "conda run -n course-env env ... slides_test.py .../lesson_01.pptx > .../lesson_01-slides-test.txt",
        "exitCode": 0,
        "report": {"path": "qa/lesson_01-slides-test.txt", "sha256": "..."}
      },
      "formalPptx": {"path": "../正式课件/lesson_01.pptx", "sha256": "..."},
      "expectedSlides": 24,
      "renderDir": "render/01",
      "renderManifest": "render/01/render-manifest.json",
      "qaReport": "qa/lesson_01-final.json"
    }
  ],
  "excludedSourceMembers": [
    {"member": "robot-source::附录/宣传页.pptx", "reason": "不属于教学进度表中的课次"}
  ]
}
```

Qualify each archive member as `archive-id::member-path`. When source decks are direct files rather than archive members, list them under `sourceFiles` as `{id, path, sha256}` and use the `id` in `sourceMembers`. At least one archive member or direct source file is required. Every source unit must be mapped to at least one lesson or listed under `excludedSourceMembers` with a concrete reason. The staging and formal PPTX records must have identical SHA-256 values.

`planAudit`, `staticAudit`, and `slidesTest` are mandatory execution records, not prose claims. Each binds the exact command, zero exit code, and a hashed report. The final `planAudit` command may not use `--pre-freeze`; its JSON must identify the exact lesson-plan path and contain `status: "pass"`, zero errors, and zero warnings. The static report must pass with zero errors and its command must include all three strict flags. The overflow command must identify `slides_test.py`. `validate_course_manifest.py` rejects a missing, failed, unhashed, draft, or weakened gate.

Each render manifest records the exact PPTX hash and every page image:

```json
{
  "pptxSha256": "...",
  "pages": [
    {"slide": 1, "path": "slide-1.png", "sha256": "..."}
  ]
}
```

Each lesson also records a hashed `buildManifest` binding builder, plan, source inventory, frozen assets, runtime/export command, and the produced PPTX. Each final QA report follows [qa-evidence-schema.md](qa-evidence-schema.md): `renderedPages` and `reviewedPages` equal the expected slide count, renderer/reviewer evidence is present, and every page is bound to the exact rendered PNG hash and dimensions. Each page requires explicit booleans for `content`, `typography`, `container`, `visualRelevance`, `legibility`, `collisionFree`, and `teachingFlow`, a concrete `reviewNote`, an `issues` array, and `status: "pass"`. Final issues must be empty or explicitly resolved; an open issue cannot coexist with a passing final page. `validate_course_manifest.py` verifies hashes, identity/order, counts, render binding, and QA evidence structure; human review remains responsible for the truth of semantic and visual judgments.
