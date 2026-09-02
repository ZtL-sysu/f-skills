# Lesson Architecture

Read this file when planning or rewriting lesson content.

## Teaching contract

Each deck represents one class meeting, not one textbook chapter pasted onto slides. The lesson needs a single mainline that a teacher can narrate aloud and a student can reconstruct afterward.

Default sequence:

1. `cover` — lesson identity and a relevant visual hook.
2. `background` — the real problem, context, or need that makes the topic worth learning.
3. `ideology` — one lesson-specific course-ideology page within slides 1–5, connecting the topic to rigorous learning, engineering responsibility, research integrity, public need, or national technological capability.
4. `roadmap` — three to five connected questions or stages, written as a logical route rather than an agenda list.
5. `principle` / `detail` — concepts, mechanism, terminology, relationships, and worked explanation.
6. `qa` — a question-only checkpoint immediately after a coherent knowledge section; use more than one across a long lesson.
7. `operation` / `case` — steps, evidence, examples, decisions, or an end-to-end application.
8. `pitfall` — common errors and the correct handling, paired one-to-one.
9. `summary` — close the loop by answering the opening problem and naming the reusable mental model.

The exact count may vary, but no required teaching role may silently disappear. A practical/software lesson should devote substantial pages to actual operations and screenshots. A conceptual lesson should devote substantial pages to mechanisms, examples, and evidence.

## Full-length 40-plus-slide architecture

For a non-practical lecture, use at least 40 substantive slides unless the user specifies another length. It is an instructional completeness pattern, not permission to pad. Every added page must introduce a new historical stage, prerequisite, causal mechanism, competing family, worked condition, operation state, inspection point, failure symptom, application, boundary, or decision. Practice/integrated lessons may be shorter only when the full deliverable and validation path remain teachable.

1. Cover — lesson identity and a real visual hook.
2. Background — authentic task or problem.
3. Course ideology — connect this lesson to rigorous study, engineering responsibility, trustworthy evidence, public need, or national technological capability.
4. Background — consequence or value of solving it.
5. Historical stage A — first workable approach and its limitation.
6. Historical stage B — the improvement and new capability.
7. Historical stage C — the modern form and what persisted.
8. Family landscape — major systems, approaches, or product families.
9. Family comparison — strengths, weaknesses, and typical uses.
10. Roadmap — three to five connected questions and final deliverable.
11. Prerequisite/vocabulary A — a familiar example before the formal term.
12. Prerequisite/vocabulary B — boundary, unit, symbol, or file/data model.
13. Principle — core definition and why it matters.
14. Mechanism A — first causal stage.
15. Mechanism B — intermediate state.
16. Mechanism C — output and why it follows.
17. Mechanism overview — connect the stages into one mental model.
18. Comparison — concepts, approaches, or states students confuse.
19. Question checkpoint — question, follow-up, and evidence requirement for the principle section; no answer text.
20. Worked example A — input → rule → result.
21. Worked example A detail — magnify the decisive step or evidence.
22. Worked example B — changed condition → changed result.
23. Worked comparison — explain why A and B diverge.
24. Real-world application A — authentic object, document, system, or outcome.
25. Real-world application B — another domain, scale, or user need.
26. Operation overview — full workflow and checkpoints.
27. Operation step 1 — action, evidence image, expected state.
28. Operation step 2 — action, evidence image, expected state.
29. Operation step 3 — action, evidence image, expected state.
30. Operation step 4 — action, evidence image, expected state.
31. Intermediate verification — inspect an observable state before proceeding.
32. Final verification — compare the output with explicit acceptance criteria.
33. Question checkpoint — question, follow-up, and evidence requirement for the operation section; no answer text.
34. Failure example A — observable symptom and why it matters.
35. Diagnosis A — symptom → likely cause → evidence to inspect.
36. Failure example B — a different cause or misleading look-alike.
37. Recovery/prevention — correction and how to avoid recurrence.
38. Integrated case — realistic end-to-end decision chain.
39. Question checkpoint — transfer question that consolidates the case and bridges to closure; no answer text.
40. Summary/closure — reusable model, opening-problem closure, deliverable evidence, and bridge to the next lesson.

If the topic needs more than 40 pages, add pages at real semantic boundaries: separate historical eras, competing families, mechanism stages, overview/detail pairs, input/result pairs, or distinct failure modes. Never split one sentence across pages merely to increase the count.

Do not split each old page mechanically. Treat a short source deck as a lesson map and mine source slides at region level: an overview crop, a magnified detail, and a result crop may support different claims only when each has a distinct purpose and provenance. If a proposed page cannot answer “what newly becomes understandable after this page?”, remove or redesign it.

## Three reusable lesson patterns

## Whole-to-part teaching spine

Before selecting individual slide types, write the lesson as one causal journey:

`引子/真实情境 → 先看对象、界面或成果的整体样貌 → 为什么需要它/问题从哪里来 → 总体模型或闭环 → 分块拆解 → 原因与机制 → 关键细节、限制与失败 → 回到整体并解决开场问题`

This is not a decorative agenda. Each transition must answer the question naturally raised by the previous section. A student should know both “我们现在讲到哪里” and “为什么下一步要讲这个”. Use a stable upper-right outline marker on body slides so sections remain visible while each page keeps a unique teaching title.

Within every major knowledge block, repeat the smaller sequence:

`它长什么样/结果是什么样 → 为什么需要 → 怎样工作或怎样做 → 哪些细节会改变结果 → 如何检查`

Do not start a block with isolated terminology or button steps when students have not yet seen the object, task, or result those terms describe.

### Concept or principle lesson

`problem → course ideology → historical/real context → definition → components → mechanism → question checkpoint → comparison → worked example → boundary conditions → pitfall → question checkpoint → synthesis`

Do not replace the mechanism with isolated definitions. Show causal arrows, intermediate states, examples, and failure conditions.

### Software or tool lesson

`task need → course ideology → software role → interface model → file/data model → operation chain → question checkpoint → decision points → screenshots with annotations → verification → recovery/pitfall → question checkpoint → reusable workflow`

Explain what changes in the document/data after each action. Avoid instruction sequences that say only “click this, then click that.”

### Practice or integrated lesson

`deliverable definition → course ideology → input constraints → acceptance criteria → decomposition → worked construction → question checkpoint → intermediate checks → common failures → final validation → question checkpoint → checklist`

“Practice” does not authorize group activity. The slide teaches the method and shows a worked path. If student work is desired, write a concrete task and reference answer, not peer discussion or showcase language.

## Plain-language rules

- Introduce the familiar situation before the formal term.
- Define a term in one clear sentence, then explain why it matters and how it behaves.
- Use concrete nouns and active verbs. Replace “进行相关操作” with the actual operation and result.
- State assumptions, units, file paths, data ranges, formula references, and boundary values when they affect the result.
- Keep the reasoning chain visible: input → rule → intermediate state → output → check.
- Preserve useful examples from source decks, but rewrite fragmented textbook captions into teachable sentences.
- Treat every example as a miniature story. The visible page identifies the setting/problem and observable outcome; the speaker notes connect background, trigger, reasoning or action, result, takeaway, and the transition onward.
- Speaker notes are talk-only prose. Use natural phrases such as “先看这里”“为什么会这样”“这就像……”“结果会发生什么”，but do not copy visible bullets word for word or include production metadata.
- Do not mention missing figures (“as shown above”) unless the referenced figure is present on the same slide.
- Do not use vague internal scaffolding such as “本页可讲解……”, “建议配图……”, or production notes in visible content.
- Do not expose `two-image`, `image-right`, `process`, “第N轮”, “优化版”, “素材处理”, “页面审查”, or any other layout/build/review vocabulary in audience-facing titles or body text.

## Density and splitting

- A normal slide contains two to five complete teaching points.
- An operation/process slide may contain up to six short steps when each step has a clear state or visual anchor.
- A normal Chinese teaching point should usually be no longer than 42 characters. Split compound logic at a semantic boundary; do not mechanically truncate it.
- If a page needs more than five points, more than two distinct concepts, or more than one full worked example, split it.
- A title describes the conclusion or question of the page, not a generic noun such as “基本知识” or “相关内容.”

## Question-only checkpoints

A question checkpoint contains:

```text
问题：为什么/什么时候/如何……？
追问：改变一个条件后，判断是否仍然成立。
证据要求：指出需要观察、测量或核对的依据。
```

Do not include an answer label or answer paragraph. The teacher may discuss the answer orally, but the visible slide must preserve the thinking task. Place the checkpoint immediately after the section it consolidates. When a lesson contains multiple checkpoints, distribute them across the lesson rather than placing them together near the end.

Forbidden unless explicitly requested by the user: 同桌交流、小组讨论、分组任务、合作探究、投票、角色扮演、成果展示、作品展示、上台汇报、分享交流、同伴互评、课堂展示、展示你的成果。

Do not flag technical uses of words such as “数据分组”, “显示/展示数据”, or “讨论一种算法” by a bare keyword. Detect classroom-activity phrases, not ordinary subject vocabulary.

## Content review gate

For each slide, a reviewer must answer yes to all:

- Does the title state the page's teaching job?
- Can the body be understood without production notes or missing context?
- Does the page connect to the previous and next page?
- Are the principle, example, or operation accurate and sufficiently detailed?
- Does every visible visual support a named point?
- Is the ideology page within slides 1–5, specific to this lesson, and free of generic slogan-only language?
- Does every question checkpoint follow the section it consolidates, remain answer-free, and help summarize, reinforce, or bridge?
- Are course-name/course-code footers absent from body slides?
- Would a teacher know what to explain and a student know what to remember?
