---
name: f-teacher-guide
description: "Create, expand, or rigorously audit step-by-step Word teaching guides and self-contained student experiment packages, including real-machine execution, one-command-at-a-time instructions, success-state screenshots, relative-path consistency, parameter studies, accessibility, render review, and clean ZIP delivery. Use for 实验指导书、学生操作手册、实训手册、逐步截图教程、独立实验包; not for lecture-only slide decks."
---

# F Teacher Guide

## Execution contract

The numbered 10 build/workflow steps map one-to-one to `T1` through `T10` in the JSON definition. Internal repair loops reopen affected stages and invalidate the downstream suffix. For multiple packages, maintain a separate ledger per package; course-wide checks aggregate all required ledgers.


Read [references/execution-contract.md](references/execution-contract.md) at startup, resume, and correction. Initialize `pipeline-state.json` from `assets/pipeline-definition.json` using `scripts/pipeline_state.py --init` with the state path as its positional argument. Maintain the Markdown ledger as its readable view. Validate `--before <stage-id>` before starting a stage and `--complete` before delivery. The JSON definition is the canonical stage list; the workflow below defines the substantive gates. Record current user preferences and authorized scope once in a versioned run-local contract. This skill does not change the selected model or global settings.

Build a guide that an ordinary student can execute in order without reading source code, guessing omitted steps, or borrowing files from another package. Treat the guide, package files, screenshots, and acceptance checks as one artifact.

## Required companion workflow

- Read and follow the installed `documents:documents` skill before creating or editing DOCX files. Its one-time artifact marker, accessibility, render, and delivery rules remain mandatory.
- When the task also changes a teaching PPTX, use `f-teacher-pptx` for the deck; this skill governs the student guide and package contract.
- Run builders and audits in a local Conda environment. On Apple silicon, use MPS when a task genuinely runs PyTorch and supports it.

## Decide the teaching scope first

Before authoring, compare the scheduled class hours, prerequisite installation time, student baseline, hardware, and the real operational complexity. Separate in-class required work, pre-class environment setup, teacher preparation, and optional extension work.

For students with weak foundations, first secure one complete baseline, then add a bounded parameter sweep when the scheduled hours would otherwise be underfilled. A four-hour experiment should normally include at least four parameter levels including the baseline, a structured result table or trend plot, and evidence-based questions. Do not reveal the expected parameter-effect conclusion in the student guide; the student must infer it from measured data. State capability boundaries explicitly when a lightweight simulator is not equivalent to a full industrial stack.

## Guide contract

Read [references/guide-contract.md](references/guide-contract.md) before creating or substantially expanding a guide. Each required step must include the starting state, exact command or action, observable success criterion, one focused success-state image, and a recovery path. Do not use “自行探索”, “自主创新”, or another undefined task as a required completion condition unless the user explicitly requests it.

When packaging files, every archive must be self-contained and extract to one English-named root folder. A guide may refer to generated runtime outputs, but every input resource it names must exist inside that root. Never make experiment 2 depend on experiment 1's extracted folder unless the user explicitly chooses that dependency.

## Resume and evidence reuse

Keep a package-level command ledger keyed by archive/input hashes, exact commands, platform, Conda environment, parameters, working directory and success evidence. After interruption inspect existing processes and resume from the earliest unverified state. Reuse evidence only when these dependencies match; a documentation-only edit does not invalidate unchanged parameter results, but changed student commands or package inputs do. The final clean-ZIP full execution in step 9 remains mandatory. Record platform-sensitive gaps precisely and continue host-verifiable work without claiming target-platform acceptance. See `references/execution-contract.md` for ordered reacceptance and invalidation.

## Build and verify

1. Inventory the schedule, existing guide, source package, code, datasets, and related deck. Preserve originals.
2. Execute the student path from a cleanly extracted archive on a real machine in the intended Conda environment. A host-side unit test, source inspection, mocked output, or rewritten equivalent command does not replace this run. Record OS/hardware, environment, archive hash, command text, exit status, elapsed time, and generated evidence. When the target classroom platform differs from the authoring host, repeat all platform-sensitive steps on that target platform or disclose the unverified platform gap.
3. Run every displayed command exactly as written and in order. Use one command per code block or numbered command row. Do not combine student commands with `&&`, `;`, a multiline pasted block, or an explanatory comment inside the command block. A long launch invocation remains one physical line. After each command, give its starting state and immediate success criterion before presenting the next command. Preserve state explicitly when later commands depend on `cd`, environment activation, `source`, a running process, or another terminal.
4. For every required GUI, RViz, device, network, sensor, or hardware action, perform an actual interaction on the real target when available and capture the visible success state. Process liveness alone is not proof of correct GUI content. Clearly label synthetic terminal panels as expected-success references; never present them as real execution captures.
5. Author the DOCX with one stable visual system, readable screenshots, real headings/lists, image alt text, and explicit page geometry.
6. Run `scripts/audit_teacher_guide.py` on each package. Resolve every error before packaging.
7. Run the Documents skill accessibility audit. Zero high, medium, and low findings are required unless the user explicitly accepts a documented exception.
8. Render the final DOCX to page PNGs with the Documents skill renderer. Inspect every page at full size for clipping, overlap, missing glyphs, unreadable screenshots, false success evidence, awkward page breaks, and large accidental blank regions.
9. Create a clean ZIP that excludes generated build caches and local test residue. Extract it into a temporary directory and repeat the complete command ledger from the extracted copy, including every parameter level, summary/table or trend generation, report opening, and automatic acceptance. Do not substitute faster parameters or normalized commands for the student-facing text.
10. Record SHA-256 hashes, archive member lists, command-level test results, real-machine metadata, elapsed times, page counts, and QA results. Use [references/qa-schema.md](references/qa-schema.md) for the evidence record.

Do not claim completion when any input path is missing, an archive contains an absolute or non-English member path, a screenshot does not support its stated success criterion, automated acceptance fails, or any rendered page remains unchecked.
