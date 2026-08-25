# Pipeline State

Update this file after every stage. Do not begin the next stage until the current stage is marked `passed`.

| Stage | Name | Status | Evidence / artifact path | Gate result | Notes |
|---|---|---|---|---|---|
| S0 | Load manuscript, preserve original, and create independent run root | pending |  |  | Original manuscript/source package must remain unchanged; all outputs must stay inside run root. |
| S1 | Extract manuscript module map | pending |  |  |  |
| S1A | Scientific review and integrity audit | pending |  |  |  |
| S2 | Build submission profile | pending |  |  |  |
| S3 | Search recent similar literature candidates | pending |  |  |  |
| S4 | Verify and select 10 SCI high-impact comparators | pending |  |  |  |
| S5 | Build comparator section-pattern digest | pending |  |  |  |
| S6 | Score modules; audit narrative closure, limitation placement, and prose | pending |  |  |  |
| S7 | Revise failed modules and update all ledgers inside run root only | pending |  |  | Revised drafts/PDFs must be written only to copied files in the run root. |
| S8 | Re-score and re-run narrative/prose gates | pending |  |  |  |
| S9 | Final submission-readiness, declaration, and package audit | pending |  |  |  |
| S10 | Deliver independent revision package | pending |  |  | Report revised artifacts from run root and original preserved input path separately. |

Allowed stage statuses: `pending`, `running`, `passed`, `blocked`, `superseded`. Put details such as `blocked-needs-author-input` or `failed-needs-retry` in Gate result or Notes, not in the Status column.
