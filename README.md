# f-skills

Public collection of the currently installed `f-*` Codex skills plus the native subagent delegation skill used alongside them.

## Included skills

- `f-guidance-builder-v1`: build evidence-grounded research guidance from a method or technique idea.
- `f-research-v1`: execute a guidance contract through experiments, evidence audits, manuscript production, and delivery.
- `f-submit-v1`: perform scientific, integrity, comparator, revision, and submission-package checks for a finished manuscript.
- `f-teacher-guide`: create and audit step-by-step teaching guides and self-contained student experiment packages.
- `f-teacher-pptx`: create and audit image-rich, classroom-readable multi-lesson teaching decks.
- [scientific-paper-writing](skills/scientific-paper-writing/SKILL.md): portable, contribution-led scholarly writing and revision guidance with English and Chinese references.
- `f-holdle`: execute and audit the HOLDLE v9-robust A-share research and consultation rules.
- `f-holdle-v10`: execute the frozen HOLDLE v10 composite-champion configuration and rolling tests.
- `spark-task-delegator`: delegate substantial independent work to native Luna with medium reasoning when beneficial; keep complex judgment and final synthesis in the primary agent.
- [`research-github-sync`](skills/research-github-sync/SKILL.md): lightweight multi-agent collaboration and research memory — one shared `AGENTS.md` entry plus three collaboration documents, with ordinary Git sync.

Each skill is stored under `skills/<skill-name>/` and retains its `SKILL.md` and any scripts, references, assets, and UI metadata it needs.

### Shared research and handoffs

Use `$research-github-sync` when a new agent with no prior conversation context must understand a project and continue work, or when several agents (Codex, WorkBuddy, others) work in sequence or in parallel. A root `AGENTS.md` is the common entry point: what the project is, how to run it, and where the collaboration docs live. New agents read `AGENTS.md` → `collaboration/STATE.md` → `TASKS.md` → relevant `agents/<id>.md` first, form a short project summary, then verify only the source, config and result files they actually need. STATE separates Verified / Hypothesis / Pending / Superseded conclusions and records Key Decisions with reasons and rejected alternatives; agent records end with an executable Resume Entry.

[Templates](skills/research-github-sync/assets/) are a starting point, not a required layout: existing README / AGENTS.md / experiment records are referenced, never moved or overwritten. Older `collaboration/PROJECT.md`, `PROTOCOL.md` and `tasks/` trees are read and left in place.

Git uses ordinary commits and pushes. Shared working directories serialize Git writes; genuinely parallel work uses separate branches or worktrees with explicit file ownership. Sensitive files and large artifacts stay out of uploads; never force-push or overwrite another agent's work. Optional independent review is encouraged for high-impact results, but PRs, branches and reviews are not mandatory. The skill itself has no runtime scripts; `tests/test_research_github_sync.py` verifies the protocol, templates and a zero-context handoff path in temporary Git repos via `python -m unittest discover -s tests -v`.

Example instruction: `使用 $research-github-sync，进入这个项目，了解当前进展，并继续尚未完成的工作。`

## GPT-6 Astra workflow update — 2026-09-10

The five research, submission, and teaching workflows now include canonical stage definitions, ordered JSON execution ledgers, evidence hashes, versioned contracts, recovery rules, and proportional revalidation. The research workflow retains its strong-result and CCFA review gates, including P1A, P1B, P3A, and P5A. Feasibility checks now include a structured evidence packet, finite experiment budgets, and held-out test isolation.

These are workflow improvements; installing a skill does not switch the host model or configure an external API executor. HOLDLE skills retain their existing portable public versions. The delegation skill reflects the latest local Luna-medium policy.

## Installation

Copy the desired skill directory into `${CODEX_HOME:-$HOME/.codex}/skills/`, or use Codex's GitHub skill installer with the repository path and the selected `skills/<skill-name>` subdirectory.

### Academic writing update — 2026-09-30

Research and submission now construct explicit writing inputs from a scientific packet and manuscript brief, then apply a shared academic profile above installed or bundled writing subskills. Their standalone distributions contain byte-identical controlled copies of the contract and adapter. Generic humanizer files are unchanged. See [change and validation report](WRITING_UPGRADE_REPORT.md) and the [actual adapter interface](skills/f-research-v1/references/writing-adapter.md).

Run checks in a local Conda environment (standard library only):

```sh
conda run -n <env> python scripts/sync_writing_assets.py --check
conda run -n <env> python -m unittest discover -s tests -v
```

After editing authoritative writing assets in `f-research-v1`, run the mirror script without `--check`, then retest. To update an existing local installation, preview with:

```sh
conda run -n <env> python scripts/sync_installed_writing.py --installed-root <skills-directory>
```

Apply by adding `--apply --backup-root <new-backup-directory>`; the script refuses divergent installed edits, snapshots previous bytes, and changes only the three targeted skills. Copying either research or submit alone also works for the shared contract/adapter; external engines and optional subskills still need their own installation. Input building never configures a model or launches AutoResearchClaw. Historical ARC context collectors require separate verified integration; repository/interface tests and native-subagent samples do not establish ARC runtime compatibility.

### Theory-only writing and revision

All three research skills include an explicitly authorized, on-demand theory-only profile. It replaces experiment gates with checked definitions, proofs and counterexamples while retaining canonical stage records and evidence integrity. Research and submit adapters support paragraph plans, qualification placement and positive scientific composition tasks; reviewer warnings and retrieval notes remain external. Research exports are independent of later submission revisions.

The final release passes 46 interface/regression tests. Native writing examples were reviewed separately; neither these tests nor those examples establish external ARC runtime compatibility or guarantee a clean first draft. Final whole-paper review and source/PDF/package checks remain required.

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
