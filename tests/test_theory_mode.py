"""Regression tests for the explicit theory-only study profile."""
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "skills/f-research-v1"
GUIDANCE_SCRIPT = REPO / "skills/f-guidance-builder-v1/scripts/validate_guidance.py"


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(RESEARCH / "scripts"))
import writing_adapter  # noqa: E402

pipeline_state = load_script("theory_test_pipeline_state", RESEARCH / "scripts/pipeline_state.py")
guidance_validator = load_script("theory_test_guidance", GUIDANCE_SCRIPT)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


THEORY_GUIDANCE = """## Title / Topic
A theoretical study.
## Core Idea
A theorem-backed analysis.
## Paper Story
We establish a bounded guarantee.
## Paper Outline
1. Introduction: problem
2. Related Work: context
3. Formal Setup: assumptions and model
4. Theoretical Results: theorem and proof
5. Discussion: implications
6. Conclusion: summary
## Evidence Plan
Assumptions and proof obligations are checked against a counterexample analysis. Failure signal: a violated assumption invalidates the guarantee.
## Expected Results
A formal guarantee under stated assumptions.
## Traceability Checklist
Must appear in paper? State theorem and proof.
## Citation Scope
Relevant theory literature.
## Figure and Table Plan
No empirical plots; summarize assumptions.
"""

EMPIRICAL_GUIDANCE = """## Title / Topic
An empirical study.
## Core Idea
A measured comparison.
## Paper Story
We evaluate on a dataset.
## Paper Outline
1. Introduction: question
2. Related Work: context
3. Method: approach
4. Experiments and Results: comparison
5. Discussion: implications
6. Conclusion: summary
## Experiment Plan
Dataset access: Source/access. Baseline: baseline model. Primary metric: accuracy. Secondary metrics: latency. Failure signal: no improvement. Runtime / Hardware Budget: fixed.
## Expected Results
Evidence from experiments.
## Traceability Checklist
Must appear in paper? Link claims to measurements.
## Citation Scope
Relevant empirical literature.
## Figure and Table Plan
Plot measured outcomes.
"""


class GuidanceModeTests(unittest.TestCase):
    def test_theory_guidance_is_valid_without_empirical_dataset_terms(self):
        self.assertEqual(guidance_validator.validate(THEORY_GUIDANCE, study_mode="theory-only"), [])

    def test_theory_guidance_requires_evidence_plan_and_proof_fields(self):
        cases = [
            (THEORY_GUIDANCE.replace("## Evidence Plan", "## Experiment Plan"), "Evidence Plan"),
            (re.sub("assumptions", "premises", THEORY_GUIDANCE, flags=re.IGNORECASE), "/Assumptions/"),
            (re.sub("proof obligations", "derivation steps", THEORY_GUIDANCE, flags=re.IGNORECASE), "/Proof obligations/"),
            (re.sub("counterexample", "illustration", THEORY_GUIDANCE, flags=re.IGNORECASE), "/Counterexample/"),
        ]
        for text, expected in cases:
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in error for error in guidance_validator.validate(text, study_mode="theory-only")))

    def test_empirical_default_still_requires_empirical_contract(self):
        errors = guidance_validator.validate(THEORY_GUIDANCE)
        self.assertTrue(any("Experiment Plan" in error for error in errors))
        self.assertTrue(any("dataset access" in error for error in errors))
        self.assertEqual(guidance_validator.validate(EMPIRICAL_GUIDANCE), [])


class PipelineProfileTests(unittest.TestCase):
    def _make_state(self, root, profile="empirical"):
        definition = pipeline_state.definition()
        contract_path = root / "contract.json"
        contract_path.write_text('{"contract":"v1"}\n', encoding="utf-8")
        state = {
            "schema_version": 1,
            "pipeline": definition["pipeline"],
            "contract_version": "v1",
            "contract": [{"path": "contract.json", "sha256": sha(contract_path)}],
            "history": [],
            "stages": [],
        }
        if profile:
            state["execution_profile"] = profile
        for key, content, path_name in (("profile", "theory profile\n", "profile.md"),
                                        ("authorization", "authorized theory-only\n", "authorization.md")):
            path = root / path_name
            path.write_text(content, encoding="utf-8")
            state[key] = [{"path": path_name, "sha256": sha(path)}]
        for stage in definition["stages"]:
            for artifact in (stage + "-input.txt", stage + "-evidence.txt"):
                (root / artifact).write_text(stage + "\n", encoding="utf-8")
            row = {
                "id": stage, "status": "passed", "contract_version": "v1", "gate_verdict": "pass",
                "inputs": [{"path": stage + "-input.txt", "sha256": sha(root / (stage + "-input.txt"))}],
                "evidence": [{"path": stage + "-evidence.txt", "sha256": sha(root / (stage + "-evidence.txt"))}],
            }
            if profile == "theory-only":
                row.update(gate_basis="theory-only", actual_executor="analyst")
            state["stages"].append(row)
            state["history"].append({"stage": stage, "action": "pass"})
        return state

    def test_legacy_empirical_pipeline_state_still_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = self._make_state(root, profile=None)
            self.assertEqual(pipeline_state.validate(state, root, complete=True), [])

    def test_theory_only_requires_hash_bound_profile_and_authorization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = self._make_state(root, profile="theory-only")
            self.assertEqual(pipeline_state.validate(state, root, complete=True), [])
            for key in ("profile", "authorization"):
                incomplete = dict(state)
                incomplete.pop(key)
                errors = pipeline_state.validate(incomplete, root, complete=True)
                self.assertTrue(any("nonempty file/hash list required" in error for error in errors), key)

    def test_theory_passed_row_requires_explicit_gate_basis_and_executor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = self._make_state(root, profile="theory-only")
            state["stages"][0].pop("actual_executor")
            errors = pipeline_state.validate(state, root, complete=True)
            self.assertTrue(any("actual executor required" in error for error in errors))


class TheoreticalFactTests(unittest.TestCase):
    def _packet(self, root, fact):
        evidence = root / "proof.md"
        evidence.write_text("Proof and derivation evidence.\n", encoding="utf-8")
        return {
            "schema_version": 1,
            "brief": {"question": "What guarantee holds?", "audience": "Theory researchers",
                      "section_jobs": {"Results": "Present the guarantee"}, "study_type": "theoretical"},
            "facts": [{**fact, "evidence": [{"path": "proof.md", "sha256": sha(evidence)}]}],
        }

    def test_theorem_with_assumptions_proof_and_evidence_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = self._packet(root, {"id": "thm-1", "kind": "theorem", "status": "derived_verified",
                                         "statement": "The method has regret bounded by O(sqrt(T)).",
                                         "assumptions": ["bounded rewards"], "proof": "By the stated potential argument."})
            output = writing_adapter.build(packet, root, "P7", "Write theoretical results", section_role="results")
            self.assertIn("thm-1", output["messages"][-1]["content"])

    def test_theorem_requires_assumptions_and_proof(self):
        for missing in ("assumptions", "proof"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                fact = {"id": "thm-1", "kind": "theorem", "status": "derived_verified",
                        "statement": "A formal guarantee."}
                fact["assumptions"] = ["bounded rewards"]
                fact["proof"] = "Potential argument."
                fact.pop(missing)
                with self.assertRaisesRegex(ValueError, "theorem requires explicit assumptions and proof"):
                    writing_adapter.build(self._packet(root, fact), root, "P7", "Write theoretical results")

    def test_numerical_experiment_cannot_be_derived_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            fact = {"id": "metric-1", "kind": "result", "status": "derived_verified",
                    "statement": "Accuracy is 0.9.", "model": "M", "condition": "test split",
                    "metric": "accuracy", "value": 0.9, "unit": "fraction", "aggregation": "mean",
                    "uncertainty": "none", "measurement_scope": "held-out test"}
            with self.assertRaisesRegex(ValueError, "derived_verified belongs to theoretical propositions"):
                writing_adapter.build(self._packet(root, fact), root, "P7", "Write results")


class ProfileMirrorTests(unittest.TestCase):
    def test_three_theory_profile_copies_are_byte_identical(self):
        paths = [REPO / f"skills/{name}/references/theory-only-mode.md" for name in
                 ("f-guidance-builder-v1", "f-research-v1", "f-submit-v1")]
        contents = [path.read_bytes() for path in paths]
        self.assertTrue(all(content == contents[0] for content in contents[1:]),
                        "theory-only-mode.md copies must be byte-identical")


if __name__ == "__main__":
    unittest.main()
