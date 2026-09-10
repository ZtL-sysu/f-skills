---
name: spark-task-delegator
description: "Selectively delegate substantial independent searches, tests, log analysis, extraction, and isolated edits to native Luna with medium reasoning. Use when parallel work and concise evidence can reduce main-thread work without costly coordination; keep short or tightly coupled tasks local."
---

# Selective Luna Delegation

Use official `spawn_agent` with `model: gpt-5.6-luna`, `reasoning_effort: medium`, and `fork_turns: none`. Use no other worker model; if Luna is unavailable or the task exceeds its capability, finish in the primary agent.

Delegate only a clear, bounded task with checkable results when useful primary-agent work can proceed alongside it and the expected benefit exceeds setup, waiting, and verification costs. Prefer read-heavy exploration, tests, extraction, and log analysis. Use direct tools for short or easily scripted work. Keep ambiguous diagnosis, consequential decisions, and final synthesis in the primary agent.

- Default to zero or one worker; add workers only for independent, substantial work. Never delegate merely to satisfy a quota or on every follow-up.
- Send only the objective, relevant paths, constraints, and acceptance criteria. Request a concise result with evidence locations, checks, and uncertainties, not raw logs or the full conversation.
- Give each artifact one writer. Read-only reviewers need a stable version; parallel writers need disjoint files and outputs. Workers must not delegate further.
- Continue useful local work while the worker runs; avoid duplicate execution and frequent polling. Reuse a suitable worker for related follow-ups; use unique names for new workers.
- Verify consequential claims and changed behavior proportionately, consolidate findings, then batch fixes. Re-review only changed or failed checks unless broader regression checks are warranted. Never drop required acceptance checks to save time.

Follow applicable project and execution constraints. Delegation aims to reduce main-thread load; it does not guarantee lower total tokens, account usage, latency, or unchanged quality.

Basis: [OpenAI subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents): prefer independent read-heavy work, return distilled results, and account for parallel-write coordination and additional token usage.
