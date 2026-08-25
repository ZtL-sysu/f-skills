# Lesson Architecture

Read this file when planning or rewriting lesson content.

## Teaching contract

Each deck represents one class meeting, not one textbook chapter pasted onto slides. The lesson needs a single mainline that a teacher can narrate aloud and a student can reconstruct afterward.

Default sequence:

1. `cover` — lesson identity and a relevant visual hook.
2. `background` — the real problem, context, or need that makes the topic worth learning.
3. `roadmap` — three to five connected questions or stages, written as a logical route rather than an agenda list.
4. `principle` / `detail` — concepts, mechanism, terminology, relationships, and worked explanation.
5. `operation` / `case` — steps, evidence, examples, decisions, or an end-to-end application.
6. `pitfall` — common errors and the correct handling, paired one-to-one.
7. `qa` — a direct teacher question and direct answer.
8. `summary` — close the loop by answering the opening problem and naming the reusable mental model.

The exact count may vary, but no required teaching role may silently disappear. A practical/software lesson should devote substantial pages to actual operations and screenshots. A conceptual lesson should devote substantial pages to mechanisms, examples, and evidence.

## Full-length 25-slide architecture

Use this exact teaching-job sequence when the user asks for a full 25-slide lesson or an existing short lesson must be expanded to that length. It is an instructional completeness pattern, not permission to pad. Every added page must introduce a new prerequisite, causal stage, worked condition, operation state, inspection point, failure symptom, or decision.

1. Cover — lesson identity and a real visual hook.
2. Background — authentic task or problem.
3. Background — consequence or value of solving it.
4. Roadmap — three to four connected questions and final deliverable.
5. Prerequisite/vocabulary — only terms needed by the next pages.
6. Principle — core definition and boundary.
7. Mechanism A — first causal stage.
8. Mechanism B — intermediate state.
9. Mechanism C — output and why it follows.
10. Comparison — concepts, approaches, or states that students confuse.
11. Worked example A — input → rule → result.
12. Worked example B — changed condition → changed result.
13. Operation overview — full workflow and checkpoints.
14. Operation step 1 — action, evidence image, expected state.
15. Operation step 2 — action, evidence image, expected state.
16. Operation step 3 — action, evidence image, expected state.
17. Operation step 4 — action, evidence image, expected state.
18. Verification — compare the output with explicit acceptance criteria.
19. Failure example — observable symptom.
20. Diagnosis — symptom → likely cause → evidence to inspect.
21. Recovery/pitfall — correction and prevention.
22. Integrated case — realistic end-to-end decision chain.
23. Direct Q&A — question, answer, and two to three reasons/checks.
24. Summary — reusable mental model or checklist.
25. Closure — revisit the opening problem, show deliverable evidence, and bridge to the next lesson.

Do not split each old page mechanically. Treat a short source deck as a lesson map and mine source slides at region level: an overview crop, a magnified detail, and a result crop may support different claims only when each has a distinct purpose and provenance. If a proposed page cannot answer “what newly becomes understandable after this page?”, remove or redesign it.

## Three reusable lesson patterns

### Concept or principle lesson

`problem → historical/real context → definition → components → mechanism → comparison → worked example → boundary conditions → pitfall → Q&A → synthesis`

Do not replace the mechanism with isolated definitions. Show causal arrows, intermediate states, examples, and failure conditions.

### Software or tool lesson

`task need → software role → interface model → file/data model → operation chain → decision points → screenshots with annotations → verification → recovery/pitfall → Q&A → reusable workflow`

Explain what changes in the document/data after each action. Avoid instruction sequences that say only “click this, then click that.”

### Practice or integrated lesson

`deliverable definition → input constraints → acceptance criteria → decomposition → worked construction → intermediate checks → common failures → final validation → Q&A → checklist`

“Practice” does not authorize group activity. The slide teaches the method and shows a worked path. If student work is desired, write a concrete task and reference answer, not peer discussion or showcase language.

## Plain-language rules

- Introduce the familiar situation before the formal term.
- Define a term in one clear sentence, then explain why it matters and how it behaves.
- Use concrete nouns and active verbs. Replace “进行相关操作” with the actual operation and result.
- State assumptions, units, file paths, data ranges, formula references, and boundary values when they affect the result.
- Keep the reasoning chain visible: input → rule → intermediate state → output → check.
- Preserve useful examples from source decks, but rewrite fragmented textbook captions into teachable sentences.
- Do not mention missing figures (“as shown above”) unless the referenced figure is present on the same slide.
- Do not use vague internal scaffolding such as “本页可讲解……”, “建议配图……”, or production notes in visible content.

## Density and splitting

- A normal slide contains two to five complete teaching points.
- An operation/process slide may contain up to six short steps when each step has a clear state or visual anchor.
- A normal Chinese teaching point should usually be no longer than 42 characters. Split compound logic at a semantic boundary; do not mechanically truncate it.
- If a page needs more than five points, more than two distinct concepts, or more than one full worked example, split it.
- A title describes the conclusion or question of the page, not a generic noun such as “基本知识” or “相关内容.”

## Direct Q&A only

A Q&A slide contains:

```text
问题：为什么/什么时候/如何……？
答案：直接结论。
依据或解释：两到三条，说明原因、边界或检查方法。
```

Forbidden unless explicitly requested by the user: 同桌交流、小组讨论、分组任务、合作探究、投票、角色扮演、成果展示、作品展示、上台汇报、分享交流、同伴互评、课堂展示、展示你的成果。

Do not flag technical uses of words such as “数据分组”, “显示/展示数据”, or “讨论一种算法” by a bare keyword. Detect classroom-activity phrases, not ordinary subject vocabulary.

## Content review gate

For each slide, a reviewer must answer yes to all:

- Does the title state the page's teaching job?
- Can the body be understood without production notes or missing context?
- Does the page connect to the previous and next page?
- Are the principle, example, or operation accurate and sufficiently detailed?
- Does every visible visual support a named point?
- Would a teacher know what to explain and a student know what to remember?
