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
- `spark-task-delegator`: selectively route objectively verifiable work to Luna and semantic judgment work to Terra after a delegation net-benefit check.

Each skill is stored under `skills/<skill-name>/` and retains its `SKILL.md`, scripts, references, assets, and UI metadata where present.

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
