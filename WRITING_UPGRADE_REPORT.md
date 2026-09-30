# Academic writing and theory-only workflow update — 2026-09-30

This release updates f-guidance-builder-v1, f-research-v1 and f-submit-v1. It changes the inputs actually consumed by writers, paragraph organization, concern-to-edit conversion and final verification. The one-time maintenance task is not part of future manuscript context.

## Changes

- Build writing requests from a scientific fact packet and manuscript brief. Keep execution logs, reviewer dialogue, retrieval notes and production history in external provenance; retain scientific disclosures that affect validity.
- Plan distinct paragraph contributions and condition placement. Revise structure before paragraphs and sentences; preserve sound passages and exact author-protected spans.
- Convert reviewer concerns into supported scientific composition tasks, rather than appending a defensive paragraph for every warning. Keep scientific scope, uncertainty, negative findings and attribution intact.
- Require complete reference identity before drafting; separate verification notes from scientific attribution. Reject unexpected control characters in mathematical text.
- Provide a conditional theory-only profile with definition/proof/counterexample evidence, explicit authorization and actual executor records. Empirical defaults remain unchanged; a theoretical exposition does not imply novelty or journal-tier readiness.
- Preserve independent research exports and immutable submission inputs. Later submission edits must not become mutable dependencies of earlier research gates.
- Keep controlled contract/adapter/profile mirrors and guarded installed-skill synchronization. Lint produces semantic-review candidates; hashes and ordered ledgers do not establish scientific or prose quality.

## Validation

Publication checks ran in local Conda on 2026-09-30:

- 46 unittest cases passed against the final release files, covering adapter inputs, citations, theoretical facts, paragraph plans, composition, exact KEEP spans, evidence freshness, installation and legacy empirical behavior.
- Controlled writing mirrors passed the synchronization check.
- The three release skill directories match their installed counterparts byte for byte.

Earlier native generation samples and two complete theoretical expositions exercised actual outline, drafting and revision calls. Initial outputs still contained redundant caveats, process remarks and mathematical defects; reviewed corrections and final whole-document checks resolved the identified issues in those articles. Their PDFs and source packages were compiled and inspected locally. These are development observations, not a blind quality study or a guarantee of clean first drafts. Manuscripts and machine-specific runtime records are not included in this public skill release.

External AutoResearchClaw end-to-end execution was not validated. The adapter does not configure a provider/model or launch ARC. Native theoretical writing execution is recorded separately. No research experiments, training, paid API calls or journal submission were performed for this maintenance verification.

## Reproduce interface checks

```sh
conda run -n <env> python scripts/sync_writing_assets.py --check
conda run -n <env> python -m unittest discover -s tests -v
```

See the skills' writing-adapter reference for the actual CLI and scientific-writing-contract reference for shared prose and integrity rules. Source, PDF and package checks must be renewed after the final manuscript edit; semantic review remains necessary.
