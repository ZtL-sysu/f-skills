# Machine-readable feasibility index

Write `ccfa-startup-packet/feasibility-contract.json` before the validation gate. This file indexes real evidence; strings alone cannot prove novelty, feasibility or public access. CCFA review remains mandatory.

Hash-bind all seven required startup Markdown artifacts in `evidence`, not only the summary decision. The validator rejects missing bindings or changed artifacts.

Root fields: `schema_version: 1`, `decision: proceed`, `claims` (nonempty list), and `evidence` (nonempty list of run/packet-local relative file paths with SHA-256 hashes). Evidence paths resolve relative to the packet and must stay inside it; snapshot upstream reports into the packet when needed.

Each claim must contain nonempty strings for `id`, `claim`, `mechanism`, `assumptions`, `falsifying_ablation`, `dataset_url`, `split_protocol`, `primary_metric`, `minimum`, `expected_strong`, `failure`, `simple_baseline`, `strong_baseline`, `matched_control`, `implementation_path`, `prototype_check`, `calibration_evidence`, `test_isolation`, and `stop_return_condition`. Use `metric_direction: higher|lower|target`. `dataset_url` must be HTTP(S) and actual direct access must be verified separately. No desired numeric gain without calibration evidence.

Each claim also requires positive numeric `runtime_hours`, `memory_gb`, positive integer `seeds` and `search_trials`. Record resource units and measured/estimated status in the linked hardware report. These fields are a finite execution budget, not permission to buy compute or use external services.

Example shape (replace every placeholder with verified project evidence):

```json
{"schema_version":1,"decision":"proceed","claims":[],"evidence":[{"path":"strong-result-feasibility-contract.md","sha256":"REPLACE_WITH_SHA256"}]}
```

The empty example deliberately fails validation. Run `scripts/validate_guidance.py <guidance.md> --strict --packet <packet-dir>`; validate the ordered pipeline ledger independently. Freeze test identities before tuning and record all trials; a test used to select the method must not later be described as unseen.
