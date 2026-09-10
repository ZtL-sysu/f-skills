# Pipeline State

Update this file after every stage. This file must live under the run root created inside the guidance-file directory. Do not begin the next stage until the current stage is marked `passed`.

## Run Boundary

- Guidance file:
- Guidance directory:
- Run root under guidance directory:
- Artifact manifest:
- Single final PDF page policy: current journal limits / `>20 pages when no journal limit exists` / user-selected policy
- Final template policy: current target-journal template when specified; otherwise contract-selected template
- Path-containment status: `pending` / `passed` / `blocked`

All process files and deliverables must be under the run root. External paths may be listed only as explicitly authorized execution sources or tool-cache sources after the accepted artifact has been copied into the run root.

| Stage | Name | Status | Evidence / artifact path | Gate result | Notes |
|---|---|---|---|---|---|
| P0 | Load guidance file and create guidance-directory run root | pending |  |  |  |
| P1 | Validate guidance file | pending |  |  |  |
| P1A | Strong-result feasibility lock | pending |  |  |  |
| P1B | CCFA pre-experiment review and integrity audit | pending |  |  |  |
| P2 | Local Conda experiment protocols and setup checks | pending |  |  |  |
| P3 | Baseline-first execution gate | pending |  |  |  |
| P3A | Baseline-evidence stop-loss review | pending |  |  |  |
| P4 | Full guidance experiment execution | pending |  |  |  |
| P5 | Strong-result lock and experiment evidence audit | pending |  |  |  |
| P5A | CCFA pre-draft scientific review and integrity audit | pending |  |  |  |
| P6 | AutoResearchClaw 16 PAPER_OUTLINE | pending |  |  |  |
| P7 | AutoResearchClaw 17 PAPER_DRAFT | pending |  |  |  |
| P8 | Figure/table generation and every-subsection insertion | pending |  |  |  |
| P9 | AutoResearchClaw 18 PEER_REVIEW | pending |  |  |  |
| P10 | AutoResearchClaw 19 PAPER_REVISION | pending |  |  |  |
| P11 | AutoResearchClaw 20 QUALITY_GATE | pending |  |  |  |
| P12 | Reference build, verification, and duplicate-paper audit | pending |  |  |  |
| P13 | AutoResearchClaw 22 EXPORT_PUBLISH into run root | pending |  |  |  |
| P14 | AutoResearchClaw 23 CITATION_VERIFY | pending |  |  |  |
| P15 | TeX export verification and PDF compilation in run root | pending |  |  |  |
| P16 | Single final PDF page count, expansion, and template policy | pending |  |  |  |
| P17 | Guidance-file paper audit | pending |  |  |  |
| P18 | Figure/table and every-subsection visual audit | pending |  |  |  |
| P19 | Humanizer and final ML-paper polish | pending |  |  |  |
| P20 | Final PDF recompile and sanity checks | pending |  |  |  |
| P21 | Final delivery from guidance-directory run root | pending |  |  |  |

Allowed statuses: `pending`, `running`, `passed`, `blocked`, `superseded`. Put experiment failure details in Notes. The canonical definition is `assets/pipeline-definition.json`; validate the matching JSON ledger before advancing.

## Path-Containment Audit

| Artifact class | Expected location under run root | Current status | External source recorded? | Notes |
|---|---|---|---|---|
| Protocols and commands | `protocols/` or `research/` | pending |  |  |
| Experiment logs and raw metrics | `results/` or `external-sync/` when authorized | pending |  |  |
| Process audits and traceability | `audits/` or `research/` | pending |  |  |
| Figures and source data | `figures/` | pending |  |  |
| Drafts and AutoResearchClaw outputs | `writing/` | pending |  |  |
| TeX build inputs and logs | `tex/` | pending |  |  |
| Final delivery bundle | `deliverables/` | pending |  |  |

## Page-Policy Audit

| Artifact | Template/style | Page count | Requirement | Status | Notes |
|---|---|---:|---|---|---|
| `paper.pdf` | current target template or contract-selected template |  | current journal limits, otherwise >20 pages unless user changes the default | pending |  |
