# Lesson Plan Schema

Read this file before writing `content-plans/lesson_NN.json` or using `validate_lesson_plan.py`.

Use [example-lesson-plan.json](example-lesson-plan.json) as a **pre-freeze planning example**. It intentionally uses placeholder URLs and therefore passes only with `--pre-freeze`; a final plan must replace every URL with a frozen local file and pass without that flag.

## Top-level object

```json
{
  "courseName": "计算机基础及应用",
  "courseCode": "H35B173D",
  "lessonNumber": 1,
  "lessonTitle": "课程导入：认识计算机",
  "sourceInventoryHash": "sha256:...",
  "fontPolicy": {
    "coverTitle": 60,
    "slideTitle": 40,
        "body": 26,
    "diagramLabel": 20,
    "caption": 16,
    "footer": 13
  },
  "visualPolicy": {
    "minImageSlideRatio": 0.8,
    "minMultiImageSlideRatio": 0.3,
    "maxConsecutiveDiagramOnly": 2
  },
  "slides": []
}
```

The course identity, lesson identity, policies, and slides are required. Use a stable source-inventory hash so the plan cannot silently drift from its source set.

## Slide object

```json
{
  "slide": 4,
  "type": "principle",
  "title": "存储程序让计算机自动执行指令",
  "teachingGoal": "解释指令和数据如何进入存储器并被处理器依次执行。",
  "body": [
    "程序和数据先以二进制形式存入存储器。",
    "处理器按地址取出一条指令，译码后完成规定操作。",
    "程序计数器指向下一条指令，使处理过程能够自动连续进行。"
  ],
  "sources": [
    {
      "kind": "source-deck",
      "path": "/absolute/path/chapter1.pptx",
      "slide": 18,
      "purpose": "存储程序原理与处理步骤"
    }
  ],
  "visual": {
    "kind": "source-image",
    "purpose": "把取指、译码、执行和更新地址四个阶段与正文逐项对应。",
    "assets": [
      {
        "path": "/absolute/path/assets/fetch-decode-execute.png",
        "sha256": "sha256:...",
        "width": 1920,
        "height": 1080,
        "date": "2026-08-22",
        "source": "source-deck:chapter1.pptx#slide=18",
        "purpose": "展示处理器工作循环",
        "engagementReason": "循环箭头与四个处理阶段一一对应，便于学生形成可复述的动作链",
        "mapsTo": [1, 2, 3],
        "alt": "处理器取指、译码、执行与更新地址的循环图"
      }
    ]
  },
  "layoutIntent": "image-left-explanation-right",
  "qaStatus": "planned"
}
```

## Required slide types

Default required types per lesson:

- exactly one `cover`;
- at least one `background`;
- at least one `roadmap` per 30 non-cover slides;
- at least one `principle` or `detail`;
- at least one `operation` or `case`;
- at least one `pitfall` per 30 non-cover slides;
- at least one `qa` per 30 non-cover slides;
- exactly one `summary`.

For a purely conceptual lesson, an applied worked example may use `case` instead of a software `operation`. For a purely practical lesson, principles may be short but cannot be absent.

## Visual kinds

Genuine image kinds counted by the validator:

`source-image`, `web-image`, `generated-image`, `photo`, `screenshot`, `document-example`, `chart-image`, `map`, `illustration`, `real-chart`

Non-image semantic visual kinds:

`diagram`, `native-diagram`, `equation`, `table`, `code`, `formula`

An image asset is an object, not a bare path. A final frozen asset requires `path`, `sha256`, pixel `width`, pixel `height`, acquisition/generation `date`, `source`, `purpose`, `engagementReason`, `mapsTo`, and `alt`. For a final web asset, `source` must be the landing-page URL and the asset must include `creatorOrSite`, `usageNote`, `cropOrAnnotation`, and a concrete `engagementReason`; preserve `directAssetUrl` when available. For a generated asset, include `promptId` and `engagementReason`. Use `url` only in a draft validated with `--pre-freeze`; the final gate forbids URL-only assets.

For a non-image semantic visual, declare executable content rather than saying only “draw a diagram”:

```json
"spec": {
  "steps": ["取指", "译码", "执行", "更新地址"],
  "mapsTo": [1, 2, 3]
}
```

`spec` must contain `mapsTo` and at least one of `elements`, `steps`, `equation`, `table`, `code`, or `relationships`.

Titles longer than 34 Chinese characters fail by default. An intentional title of 35–54 characters must declare `"titleLayout": "two-line"`, remain at least 40 pt in the exported PPTX, and pass full-size review.

## Exceptions

A slide without a genuine image asset must include:

```json
"visual": {
  "kind": "equation",
  "purpose": "逐步推导二进制按权展开。",
  "assets": [],
  "spec": {
    "equation": "1011₂ = 1×2³ + 0×2² + 1×2¹ + 1×2⁰",
    "mapsTo": [1, 2]
  },
  "exception": {
    "reason": "A decorative photo would not explain the derivation; the equation itself is the semantic visual."
  }
}
```

Exceptions do not remove the 80% lesson-level image gate unless the user explicitly approves a lower threshold for subject-matter reasons. The plan must set the lower value (never below 0.6), give a concrete `rationale`, and record the approval basis in `visualPolicy.userApproval`. Convenience, time pressure, or missing asset work are not valid reasons.

## Direct Q&A structure

The Q&A body must contain both prefixes:

```json
"body": [
  "问题：为什么复制文件后原位置仍然存在？",
  "答案：复制会创建一个内容相同的新文件，不改变原文件的位置。",
  "移动才会改变原文件所在位置。",
  "完成操作后应核对源路径和目标路径。"
]
```

No separate activity prompt, partner instruction, presentation request, or peer-assessment item may appear.

## QA lifecycle

`qaStatus` progresses through `planned → built → rendered → passed`. The final QA report, not the content plan alone, proves `passed`.
