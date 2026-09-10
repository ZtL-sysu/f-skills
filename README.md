# f-skills

Public collection of the currently installed `f-*` Codex skills plus the native subagent delegation skill used alongside them.

## Included skills

- `f-guidance-builder-v1`: build evidence-grounded research guidance from a method or technique idea.
- `f-research-v1`: execute a guidance contract through experiments, evidence audits, manuscript production, and delivery.
- `f-submit-v1`: perform scientific, integrity, comparator, revision, and submission-package checks for a finished manuscript.
- `f-teacher-guide`: create and audit step-by-step teaching guides and self-contained student experiment packages.
- `f-teacher-pptx`: create and audit image-rich, classroom-readable multi-lesson teaching decks.
- `f-holdle`: execute and audit the HOLDLE v9-robust A-share research and consultation rules.
- `f-holdle-v10`: execute the frozen HOLDLE v10 composite-champion configuration and rolling tests.
- `spark-task-delegator`: delegate substantial independent work to native Luna with medium reasoning when beneficial; keep complex judgment and final synthesis in the primary agent.

Each skill is stored under `skills/<skill-name>/` and retains its `SKILL.md`, scripts, references, assets, and UI metadata where present.

## GPT-6 Astra workflow update — 2026-09-10

The five research, submission, and teaching workflows now include canonical stage definitions, ordered JSON execution ledgers, evidence hashes, versioned contracts, recovery rules, and proportional revalidation. The research workflow retains its strong-result and CCFA review gates, including P1A, P1B, P3A, and P5A. Feasibility checks now include a structured evidence packet, finite experiment budgets, and held-out test isolation.

These are workflow improvements; installing a skill does not switch the host model or configure an external API executor. HOLDLE skills retain their existing portable public versions. The delegation skill reflects the latest local Luna-medium policy.

## Installation

Copy the desired skill directory into `${CODEX_HOME:-$HOME/.codex}/skills/`, or use Codex's GitHub skill installer with the repository path and the selected `skills/<skill-name>` subdirectory.

## Portability and private inputs

The public copies contain no user papers, credentials, database configuration, runtime caches, trading records, or private experiment outputs.

The HOLDLE skills use portable environment variables:

- `HOLDLE_ROOT`: project/source-data root; defaults to `$HOME/code/holdle`.
- `HOLDLE_OUTPUT_ROOT`: research and backtest outputs; defaults to `$HOLDLE_ROOT/04_训练记录`.
- `HOLDLE_LIVE_ROOT`: live-consultation outputs; defaults to `$HOLDLE_ROOT/05_上岗指令`.
- `HOLDLE_INPUT_DIR` and `HOLDLE_FIXTURE_DIR`: optional data/fixture overrides.
- `CODEX_HOME`: Codex configuration root; defaults to `$HOME/.codex`.

Course text, locally captured cases, private financial data, frozen result files, and credentials are intentionally not included. Users must supply legally obtained inputs and configure external dependencies such as `gjdata` separately.

## Safety

The investment-related skills are research and decision-support workflows, not guarantees of return or authorization to trade. They must not place orders without separate, explicit authorization.
