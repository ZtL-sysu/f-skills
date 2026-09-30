"""Mechanical regressions for the bounded academic-writing adapter.

These tests validate data boundaries and explicit invariants. They do not
certify scientific entailment, prose quality, figure correctness, or a model
executor's behavior.
"""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
RESEARCH = REPO / "skills/f-research-v1"
SCRIPTS = RESEARCH / "scripts"
sys.path.insert(0, str(SCRIPTS))

import manuscript_lint  # noqa: E402
import writing_adapter  # noqa: E402


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


pipeline_state = load_script("research_pipeline_state", SCRIPTS / "pipeline_state.py")
guidance_validator = load_script(
    "guidance_validator", REPO / "skills/f-guidance-builder-v1/scripts/validate_guidance.py"
)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_packet(root):
    root = Path(root).resolve()
    evidence = root / "results" / "metrics.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text('{"source":"fixture"}\n', encoding="utf-8")
    return {
        "schema_version": 1,
        "brief": {
            "question": "Does the method improve river-flow forecasting?",
            "answer": "The supplied comparison reports a bounded predictive improvement.",
            "audience": "Researchers in river forecasting",
            "domain_bridge": "river problem -> design requirement -> measured basin result",
            "section_jobs": {"Results": "Compare basin-level measurements"},
            "author_constraints": {"declaration_mode": "preserve"},
        },
        "facts": [
            {
                "id": "river-main-f1",
                "kind": "result",
                "statement": "Model-A reaches 0.8930 pooled F1 in Basin North.",
                "status": "observed_verified",
                "model": "Model-A",
                "condition": "Basin North",
                "metric": "F1",
                "value": 0.893,
                "unit": "score",
                "aggregation": "pooled",
                "uncertainty": "95% CI [-0.02, 0.04] on paired difference",
                "measurement_scope": "held-out Basin North",
                "evidence": [{"path": "results/metrics.json", "sha256": digest(evidence)}],
            },
            {
                "id": "theory-limit",
                "kind": "limitation",
                "statement": "The supplied theory has no application experiment.",
                "status": "author_reported",
                "evidence": [{"path": "results/metrics.json", "sha256": digest(evidence)}],
            },
        ],
        "internal": {"private_note": "INTERNAL_ONLY_LEAK_SENTINEL"},
    }


class FixtureCatalogTests(unittest.TestCase):
    def test_fixture_catalog_has_reviewable_contract_fields(self):
        cases = json.loads((REPO / "tests/fixtures/writing_regressions.json").read_text())
        self.assertGreaterEqual(len(cases), 20)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["input"])
                self.assertTrue(case["facts/invariants"])
                self.assertTrue(case["expected_actions"])
                self.assertTrue(case["forbidden_errors"])
        required_cases = {
            "whole-paper-limit-repetition", "methods-terms-and-seed",
            "introduction-conclusion-scope-drift", "results-number-inventory",
            "figure-label-production-marker", "good-passage-keep",
        }
        self.assertTrue(required_cases.issubset({case["id"] for case in cases}))
        domains = " ".join(case["id"] for case in cases).lower()
        self.assertIn("breaking", domains)
        self.assertIn("river", domains)
        self.assertIn("theory", domains)


class AdapterBoundaryTests(unittest.TestCase):
    def test_stage_contexts_use_packet_only_and_keep_provenance_external(self):
        for stage in ("P6", "P7", "P10", "S7"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                packet = make_packet(root)
                (root / "old-stage-log.txt").write_text("RAW_RUN_CONTEXT_SENTINEL", encoding="utf-8")
                source = "Current draft text." if stage in {"P10", "S7"} else None
                edits = [{
                    "proposition": "Model-A outperforms comparator",
                    "evidence_status": "observed_verified",
                    "action": "NARROW",
                    "location": "Results paragraph 1",
                    "factual_check": "preserve model and basin pairing",
                    "reviewer_dialogue": "REVIEWER_DIALOGUE_SENTINEL",
                }]
                built = writing_adapter.build(
                    packet, root, stage, "Revise only the identified section", source=source,
                    edits=edits if stage in {"P10", "S7"} else None,
                )
                serialized = json.dumps(built["messages"], ensure_ascii=False)
                self.assertNotIn("INTERNAL_ONLY_LEAK_SENTINEL", serialized)
                self.assertNotIn("RAW_RUN_CONTEXT_SENTINEL", serialized)
                self.assertNotIn("REVIEWER_DIALOGUE_SENTINEL", serialized)
                self.assertIn("river-main-f1", serialized)
                self.assertIn("Model-A", serialized)
                self.assertIn("evidence_manifest", built["provenance"])
                self.assertNotIn("results/metrics.json", serialized)
                self.assertEqual(built["provenance"]["execution"], "input-built-only; no model invoked")
                if source:
                    self.assertIn("Current draft text.", serialized)

    def test_humanizer_messages_keep_academic_contract_above_installed_and_bundled_advice(self):
        contract = (RESEARCH / "references/scientific-writing-contract.md").read_text(encoding="utf-8")
        for origin in ("installed", "bundled"):
            with self.subTest(origin=origin), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                packet = make_packet(root)
                installed_root = root / "skills"
                if origin == "installed":
                    skill = installed_root / "humanizer/SKILL.md"
                    skill.parent.mkdir(parents=True)
                    skill.write_text("INSTALLED_HUMANIZER_ADVICE", encoding="utf-8")
                built = writing_adapter.build(
                    packet, root, "P19", "Polish the identified defect", subskill="humanizer",
                    installed_root=installed_root,
                )
                messages = built["messages"]
                self.assertEqual(messages[0]["role"], "system")
                self.assertEqual(messages[0]["content"], contract)
                self.assertIn("Evidence integrity, author protections", messages[0]["content"])
                self.assertTrue(messages[1]["content"].startswith("Subordinate advice; apply only within the higher-priority academic profile:"))
                expected = "INSTALLED_HUMANIZER_ADVICE" if origin == "installed" else "humanizer"
                self.assertIn(expected, messages[1]["content"])
                self.assertNotEqual(built["provenance"]["dependency"]["path"], None)

    def test_section_roles_keep_method_terms_and_direct_results_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            packet["facts"].append({
                "id": "reproducibility-method", "kind": "method",
                "statement": "Nested cross-validation used random seed 7 and a fixed validation split.",
                "status": "observed_verified",
                "evidence": [{"path": "results/metrics.json", "sha256": digest(root / "results/metrics.json")}],
            })
            methods = writing_adapter.build(packet, root, "P7", "Write Methods", section_role="methods")
            methods_task = json.loads(methods["messages"][-1]["content"])
            self.assertIn("random seed 7", json.dumps(methods_task))
            self.assertIn("cross-validation", json.dumps(methods_task))
            self.assertIn("including selection and measurement scope", methods_task["section_job"])
            results = writing_adapter.build(packet, root, "P7", "Write Results", section_role="results")
            results_task = json.loads(results["messages"][-1]["content"])
            self.assertIn("principal comparison", results_task["section_job"])
            self.assertIn("uncertainty", results_task["section_job"])
            self.assertIn("adverse findings", results_task["section_job"])
            discussion = writing_adapter.SECTION_JOBS["discussion"]
            conclusion = writing_adapter.SECTION_JOBS["conclusion"]
            self.assertIn("Do not replay the score inventory", discussion)
            self.assertIn("Avoid a closing list", conclusion)
            self.assertIn("not an obligatory closing sentence", writing_adapter.SECTION_JOBS["abstract"])

    def test_results_role_requires_observed_empirical_or_supported_theoretical_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            empirical = make_packet(root)
            empirical["facts"][0]["status"] = "planned"
            empirical["facts"][0].pop("evidence")
            with self.assertRaisesRegex(ValueError, "empirical Results needs reported/verified result facts"):
                writing_adapter.build(empirical, root, "P7", "write results", section_role="results")
            theoretical = make_packet(root)
            theoretical["brief"]["study_type"] = "theoretical"
            theoretical["facts"] = [{
                "id": "planned-theorem", "kind": "definition", "statement": "A planned proposition.",
                "status": "planned",
            }]
            with self.assertRaisesRegex(ValueError, "theoretical Results needs supported propositions"):
                writing_adapter.build(theoretical, root, "P7", "write results", section_role="results")
            theoretical["facts"][0].update({
                "id": "supported-theorem", "statement": "The theorem bounds regret by O(sqrt(T)).",
                "status": "author_reported", "evidence": [{"path": "results/metrics.json", "sha256": digest(root / "results/metrics.json")}],
            })
            accepted = writing_adapter.build(theoretical, root, "P7", "write results", section_role="results")
            task = json.loads(accepted["messages"][-1]["content"])
            self.assertIn("supported-theorem", json.dumps(task))

    def test_mixed_keep_rewrite_requires_unique_protected_text_and_forwards_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            source = "Methods: keep random seed 7. Old sentence to revise."
            edits = [
                {"proposition": "Preserve seed", "evidence_status": "observed_verified", "action": "KEEP", "location": "Methods", "factual_check": "retain exact method detail", "protected_text": "keep random seed 7"},
                {"proposition": "Clarify comparison", "evidence_status": "observed_verified", "action": "REWRITE", "location": "Results", "factual_check": "match evidence"},
            ]
            built = writing_adapter.build(packet, root, "P10", "revise local text", source=source, edits=edits)
            task = json.loads(built["messages"][-1]["content"])
            self.assertEqual(task["edits"][0]["protected_text"], "keep random seed 7")
            for bad_source, bad_edits in (
                (source, [{k: v for k, v in edits[0].items() if k != "protected_text"}, edits[1]]),
                (source + " keep random seed 7", edits),
                (None, edits),
            ):
                with self.subTest(source=bad_source), self.assertRaisesRegex(ValueError, "mixed KEEP requires unique protected_text"):
                    writing_adapter.build(packet, root, "P10", "revise local text", source=bad_source, edits=bad_edits)

    def test_response_parts_checks_mixed_keep_text_for_change_removal_or_duplication(self):
        source = "Methods keep random seed 7.\nResults old wording."
        protected = "keep random seed 7"
        self.assertEqual(
            writing_adapter.response_parts({"manuscript": "Methods keep random seed 7.\nResults revised wording.", "notes": "separate"}, source, keep_texts=[protected])[0],
            "Methods keep random seed 7.\nResults revised wording.",
        )
        for output in (
            "Methods keep random seed 8.\nResults revised wording.",
            "Methods removed detail.\nResults revised wording.",
            "Methods keep random seed 7. keep random seed 7\nResults revised wording.",
        ):
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "mixed KEEP changed or duplicated"):
                writing_adapter.response_parts({"manuscript": output, "notes": "separate"}, source, keep_texts=[protected])

    def test_introduction_and_conclusion_can_be_checked_against_same_task_and_population(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paper = root / "paper.md"
            policy = {"assertions": [
                {"id": "intro-task-population", "location_pattern": r"(?s)## Introduction.*?## Conclusion", "pattern": r"River forecasting.*adult operators"},
                {"id": "conclusion-task-population", "location_pattern": r"(?s)## Conclusion.*", "pattern": r"River forecasting.*adult operators", "forbidden": r"hospital triage|pediatric patients"},
            ]}
            paper.write_text(
                "## Introduction\nRiver forecasting for adult operators is the study question.\n"
                "## Conclusion\nRiver forecasting for adult operators is the supported scope.\n",
                encoding="utf-8",
            )
            self.assertEqual(manuscript_lint.check(paper, root, policy)["errors"], [])
            paper.write_text(
                "## Introduction\nRiver forecasting for adult operators is the study question.\n"
                "## Conclusion\nThe finding applies to hospital triage for pediatric patients.\n",
                encoding="utf-8",
            )
            errors = manuscript_lint.check(paper, root, policy)["errors"]
            self.assertTrue(any("conclusion-task-population" in e for e in errors))

    def test_figure_label_skill_and_prompt_markers_are_candidates_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paper = root / "paper.md"
            paper.write_text("## Results\nFigure 2 summarizes Basin North.\n", encoding="utf-8")
            labels = root / "visible-labels.json"
            labels.write_text(json.dumps(["f-research-v1 skill", "complete the evidence chain prompt"]), encoding="utf-8")
            report = manuscript_lint.check(paper, root, labels=labels)
            candidates = [item for item in report["findings"] if item["file"] == "visible-labels.json"]
            self.assertEqual(len(candidates), 2)
            self.assertTrue(all(item["status"] == "needs-visual-and-human-review" for item in candidates))
            self.assertEqual(report["status"], "semantic-review-required")

    def test_response_parts_preserve_keep_bytes_and_isolate_notes(self):
        source = "## Methods\r\nNested cross-validation; random seed 7.\r\n"
        response = {"manuscript": source, "notes": "PRIVATE_EDIT_NOTE"}
        manuscript, notes = writing_adapter.response_parts(response, source, keep=True)
        self.assertEqual(manuscript.encode(), source.encode())
        self.assertEqual(notes, "PRIVATE_EDIT_NOTE")
        self.assertNotIn(notes, manuscript)
        changed = {"manuscript": source.replace("seed 7", "seed 8"), "notes": "changed"}
        with self.assertRaisesRegex(ValueError, "KEEP changed manuscript text"):
            writing_adapter.response_parts(changed, source, keep=True)
        with self.assertRaisesRegex(ValueError, "separate manuscript and notes"):
            writing_adapter.response_parts({"manuscript": source, "notes": "notes", "reverse_outline": "leaked"})

    def test_cli_response_validation_accepts_exact_keep_and_rejects_changed_keep(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            packet_file = root / "packet.json"
            packet_file.write_text(json.dumps(packet), encoding="utf-8")
            source = "## Methods\r\nNested cross-validation used random seed 7.\r\n"
            manuscript = root / "manuscript.md"
            manuscript.write_bytes(source.encode())
            edits = root / "edits.json"
            edits.write_text(json.dumps([{
                "proposition": "Reproducibility details", "evidence_status": "observed_verified",
                "action": "KEEP", "location": "Methods", "factual_check": "same bytes",
            }]), encoding="utf-8")
            response = root / "response.json"
            response.write_text(json.dumps({"manuscript": source, "notes": "SEPARATE_NOTES_SENTINEL"}), encoding="utf-8")
            output = root / "request.json"
            command = [sys.executable, str(SCRIPTS / "writing_adapter.py"), "--packet", str(packet_file), "--run-root", str(root),
                       "--stage", "P10", "--section-task", "Keep this passage unchanged", "--section-role", "methods",
                       "--manuscript", str(manuscript), "--edits", str(edits), "--response", str(response), "--output", str(output)]
            proc = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "format-checked; semantic-review-required")
            self.assertEqual(result["manuscript"].encode(), source.encode())
            self.assertIn("SEPARATE_NOTES_SENTINEL", result["notes"])
            self.assertNotIn("SEPARATE_NOTES_SENTINEL", result["manuscript"])
            response.write_text(json.dumps({"manuscript": source.replace("seed 7", "seed 8"), "notes": "wrong"}), encoding="utf-8")
            bad_output = root / "bad-request.json"
            proc = subprocess.run([*command[:-1], str(bad_output)], cwd=root, capture_output=True, text=True, check=False)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("KEEP changed manuscript text", proc.stdout)
            self.assertFalse(bad_output.exists())

    def test_cli_automatically_binds_mixed_keep_text_to_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            packet_file = root / "packet.json"
            packet_file.write_text(json.dumps(packet), encoding="utf-8")
            source = "Methods keep random seed 7.\nResults old wording."
            manuscript = root / "manuscript.md"
            manuscript.write_text(source, encoding="utf-8")
            edits = root / "edits.json"
            edits.write_text(json.dumps([
                {"proposition": "Preserve seed", "evidence_status": "observed_verified", "action": "KEEP", "location": "Methods", "factual_check": "exact", "protected_text": "keep random seed 7"},
                {"proposition": "Improve result explanation", "evidence_status": "observed_verified", "action": "REWRITE", "location": "Results", "factual_check": "retain metric relationship"},
            ]), encoding="utf-8")
            response = root / "response.json"
            response.write_text(json.dumps({"manuscript": "Methods keep random seed 7.\nResults clarified wording.", "notes": "private notes"}), encoding="utf-8")
            common = [sys.executable, str(SCRIPTS / "writing_adapter.py"), "--packet", str(packet_file), "--run-root", str(root),
                      "--stage", "P10", "--section-task", "Revise local issues", "--manuscript", str(manuscript),
                      "--edits", str(edits), "--response", str(response)]
            output = root / "accepted.json"
            proc = subprocess.run([*common, "--output", str(output)], cwd=root, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("keep random seed 7", result["manuscript"])
            self.assertNotIn("private notes", result["manuscript"])
            response.write_text(json.dumps({"manuscript": "Methods changed seed 7.\nResults clarified wording.", "notes": "private notes"}), encoding="utf-8")
            rejected_output = root / "rejected.json"
            proc = subprocess.run([*common, "--output", str(rejected_output)], cwd=root, capture_output=True, text=True, check=False)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("mixed KEEP changed or duplicated protected text", proc.stdout)
            self.assertFalse(rejected_output.exists())

    def test_each_skill_copy_runs_its_cli_without_a_sibling_skill(self):
        for name in ("f-research-v1", "f-submit-v1"):
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                isolated = root / name
                shutil.copytree(REPO / "skills" / name, isolated, ignore=shutil.ignore_patterns("__pycache__"))
                self.assertEqual([p.name for p in root.iterdir()], [name])
                run_root = root / "run"
                run_root.mkdir()
                packet = make_packet(run_root)
                packet_file = run_root / "packet.json"
                packet_file.write_text(json.dumps(packet), encoding="utf-8")
                manuscript = run_root / "draft.md"
                manuscript.write_text("## Results\nThe river model retained uncertainty.\n", encoding="utf-8")
                adapter = isolated / "scripts/writing_adapter.py"
                lint = isolated / "scripts/manuscript_lint.py"
                build = subprocess.run(
                    [sys.executable, str(adapter), "--packet", str(packet_file), "--run-root", str(run_root),
                     "--stage", "P7", "--section-task", "Draft the river Results", "--section-role", "results",
                     "--output", str(run_root / "request.json")], cwd=root, capture_output=True, text=True, check=False,
                )
                self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
                self.assertEqual(json.loads((run_root / "request.json").read_text())["provenance"]["execution"], "input-built-only; no model invoked")
                lint_run = subprocess.run(
                    [sys.executable, str(lint), "--run-root", str(run_root), "--manuscript", str(manuscript),
                     "--report", str(run_root / "lint.json")], cwd=root, capture_output=True, text=True, check=False,
                )
                self.assertEqual(lint_run.returncode, 0, lint_run.stdout + lint_run.stderr)
                self.assertEqual(json.loads((run_root / "lint.json").read_text())["status"], "semantic-review-required")

    def test_installed_skill_precedes_bundled_and_fallback_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            skill_root = root / "isolated-skill"
            with patch.object(writing_adapter, "SKILL", skill_root):
                installed = root / "skills/paper-refine/SKILL.md"
                installed.parent.mkdir(parents=True)
                installed.write_text("INSTALLED_PROFILE", encoding="utf-8")
                bundled = skill_root / "bundled-skills/paper-refine/SKILL.md"
                bundled.parent.mkdir(parents=True)
                bundled.write_text("BUNDLED_PROFILE", encoding="utf-8")
                resolved = writing_adapter.dependency("paper-refine", root / "skills")
                self.assertEqual(Path(resolved["path"]), installed.resolve())
                installed.unlink()
                resolved = writing_adapter.dependency("paper-refine", root / "skills")
                self.assertEqual(Path(resolved["path"]), bundled.resolve())
                self.assertEqual(resolved["sha256"], digest(bundled))

    def test_adapter_rejects_stale_and_escaping_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            packet["facts"][0]["evidence"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "missing/stale evidence"):
                writing_adapter.build(packet, root, "P7", "Draft Results")
            packet = make_packet(root)
            packet["facts"][0]["evidence"][0]["path"] = "../outside.json"
            with self.assertRaisesRegex(ValueError, "outside run root"):
                writing_adapter.build(packet, root, "P7", "Draft Results")

    def test_revision_blocks_unresolved_evidence_and_rejects_admin_fact_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            packet = make_packet(root)
            with self.assertRaisesRegex(ValueError, "unresolved evidence blocker"):
                writing_adapter.build(packet, root, "P10", "revise", source="draft", edits=[{
                    "proposition": "Need a new experiment", "evidence_status": "unresolved",
                    "action": "BLOCK_EVIDENCE", "location": "Results", "factual_check": "missing",
                }])
            for stage in ("P10", "S7", "P19"):
                with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, "concern-to-edit decisions"):
                    writing_adapter.build(packet, root, stage, "revise", source="current source text")
            packet["facts"][0]["admin_note"] = "do not leak"
            with self.assertRaisesRegex(ValueError, "unknown fact field"):
                writing_adapter.build(packet, root, "P7", "draft")


class ManuscriptLintTests(unittest.TestCase):
    def test_multi_file_lint_skips_code_and_marks_declaration_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "sections").mkdir()
            main = root / "main.tex"
            section = root / "sections/results.tex"
            main.write_text(
                "\\section{Results}\n\\input{sections/results}\n"
                "\\section{AI Use Disclosure}\nThe P7 pipeline was used for language editing.\n"
                "\\begin{verbatim}\nP10 pipeline\n\\end{verbatim}\n"
                "\\begin{thebibliography}{1}\nP10 audit passed\n\\end{thebibliography}\n",
                encoding="utf-8",
            )
            section.write_text("The P7 pipeline was tested on held-out basins.\n", encoding="utf-8")
            findings, files, _ = manuscript_lint.scan(main, root)
            self.assertEqual(len(files), 2)
            self.assertTrue(any(f["file"] == "sections/results.tex" and f["rule_id"] == "W001" for f in findings))
            self.assertTrue(any(f["status"] == "declaration-review-do-not-auto-remove" for f in findings))
            self.assertFalse(any("P10 pipeline" in f["original"] and f["file"] == "main.tex" for f in findings))
            self.assertFalse(any("P10 audit passed" in f["original"] for f in findings))

    def test_relational_assertions_catch_model_swap_pooled_mean_and_cost_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paper = root / "paper.md"
            paper.write_text(
                "## Results\nModel-A reached 0.8930 F1 in Basin North; Model-B reached 0.8785 F1 in Basin South.\n"
                "Pooled F1 was 0.84; mean per-site F1 was 0.79.\n"
                "Training 20 candidates cost 8 GPU-hours; inference for one selected model was 14 ms per sample.\n",
                encoding="utf-8",
            )
            policy = {"assertions": [
                {"id": "model-condition-score", "location_pattern": r"(?s)## Results.*", "pattern": r"(?=.*Model-A[^;]*0\.8930[^;]*Basin North)(?=.*Model-B[^;]*0\.8785[^;]*Basin South)", "forbidden": r"Model-A[^;]*0\.8785"},
                {"id": "aggregation", "location_pattern": r"(?s)## Results.*", "pattern": r"(?=.*Pooled F1[^;]*0\.84)(?=.*mean per-site F1[^;]*0\.79)", "forbidden": r"Pooled F1[^;]*0\.79"},
                {"id": "cost-boundary", "location_pattern": r"(?s)## Results.*", "pattern": r"(?=.*Training 20 candidates[^;]*8 GPU-hours)(?=.*inference for one selected model[^;]*14 ms)", "forbidden": r"inference for one selected model[^;]*8 GPU-hours"},
            ]}
            accepted = manuscript_lint.check(paper, root, policy)
            self.assertEqual(accepted["errors"], [])
            self.assertEqual(accepted["status"], "semantic-review-required")
            paper.write_text(
                "## Results\nModel-A reached 0.8785 F1 in Basin North; Model-B reached 0.8930 F1 in Basin South.\n"
                "Pooled F1 was 0.79; mean per-site F1 was 0.84.\n"
                "Training 20 candidates cost 8 GPU-hours; inference for one selected model was 8 GPU-hours.\n",
                encoding="utf-8",
            )
            rejected = manuscript_lint.check(paper, root, policy)
            self.assertTrue(any("model-condition-score" in e for e in rejected["errors"]))
            self.assertTrue(any("aggregation" in e for e in rejected["errors"]))
            self.assertTrue(any("cost-boundary" in e for e in rejected["errors"]))

    def test_ci_crossing_zero_is_not_promoted_to_equivalence_or_significance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            paper = root / "paper.md"
            paper.write_text("## Results\nDifference 0.01, 95% CI [-0.02, 0.04].\n", encoding="utf-8")
            report = manuscript_lint.check(paper, root)
            self.assertEqual(report["status"], "semantic-review-required")
            self.assertEqual(report["errors"], [])
            self.assertFalse(any(f["rule_id"] == "W004" for f in report["findings"]))
            paper.write_text("## Results\nThe interval proves equivalence and statistical significance.\n", encoding="utf-8")
            policy = {"assertions": [{"id": "ci-interpretation", "location_pattern": r"(?s)## Results.*", "pattern": r"95% CI.*-0\.02.*0\.04", "forbidden": r"proves equivalence|statistical significance"}]}
            self.assertTrue(manuscript_lint.check(paper, root, policy)["errors"])

    def test_protected_ranges_artifacts_and_stale_export_invalidate_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            baseline = root / "source.md"
            current = root / "working.md"
            source_table = root / "source.csv"
            pdf = root / "paper.pdf"
            baseline.write_text("## Protected\nApproved author sentence.\n## End\n", encoding="utf-8")
            current.write_text("## Protected\nApproved author sentence.\n## End\n", encoding="utf-8")
            source_table.write_text("model,score\nA,0.81\n", encoding="utf-8")
            pdf.write_bytes(b"fixture-pdf")
            policy = {
                "protected_sections": [{"baseline": "source.md", "baseline_sha256": digest(baseline), "current": "working.md", "start": "## Protected", "end": "## End"}],
                "protected_artifacts": [{"path": "source.csv", "sha256": digest(source_table)}],
            }
            report = manuscript_lint.check(current, root, policy)
            self.assertEqual(report["errors"], [])
            current.write_text("## Protected\nChanged approved sentence.\n## End\n", encoding="utf-8")
            self.assertTrue(any("protected section changed" in e for e in manuscript_lint.check(current, root, policy)["errors"]))
            current.write_text("## Protected\nApproved author sentence.\n## End\n", encoding="utf-8")
            source_table.write_text("model,score\nA,0.80\n", encoding="utf-8")
            self.assertTrue(any("protected artifact changed" in e for e in manuscript_lint.check(current, root, policy)["errors"]))
            source_tex = root / "source.tex"
            source_tex.write_text("\\section{Results}\nModel-A reached 0.81.\n", encoding="utf-8")
            report = manuscript_lint.check(source_tex, root)
            report["dependencies"].append({"path": "paper.pdf", "sha256": digest(pdf)})
            accepted_pdf_hash = digest(pdf)
            source_tex.write_text("\\section{Results}\nModel-A reached 0.82.\n", encoding="utf-8")
            stale_source = manuscript_lint.current(report, root)
            self.assertTrue(any("source.tex" in e for e in stale_source))
            self.assertEqual(digest(pdf), accepted_pdf_hash)
            source_tex.write_text("\\section{Results}\nModel-A reached 0.81.\n", encoding="utf-8")
            pdf.write_bytes(b"changed-export")
            self.assertTrue(any("paper.pdf" in e for e in manuscript_lint.current(report, root)))

    def test_crlf_protected_range_change_is_detected_byte_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            baseline = root / "approved.tex"
            current = root / "revision.tex"
            baseline_bytes = b"\\section{Methods}\r\nKeep seed 7.\r\n\\section{Results}\r\n"
            baseline.write_bytes(baseline_bytes)
            current.write_bytes(baseline_bytes)
            policy = {"protected_sections": [{
                "baseline": "approved.tex", "baseline_sha256": digest(baseline), "current": "revision.tex",
                "start": r"\section{Methods}", "end": r"\section{Results}",
            }]}
            self.assertEqual(manuscript_lint.check(current, root, policy)["errors"], [])
            current.write_bytes(baseline_bytes.replace(b"seed 7", b"seed 8"))
            errors = manuscript_lint.check(current, root, policy)["errors"]
            self.assertTrue(any("protected section changed" in error for error in errors))

    def test_checker_versions_invalidate_report_after_script_contract_or_rubric_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            isolated_skill = root / "skill"
            for relative in ("scripts/manuscript_lint.py", "scripts/writing_adapter.py", "references/scientific-writing-contract.md"):
                path = isolated_skill / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("v1\n", encoding="utf-8")
            manuscript = root / "paper.md"
            manuscript.write_text("## Results\nA reported result.\n", encoding="utf-8")
            with patch.object(manuscript_lint, "SKILL", isolated_skill):
                report = manuscript_lint.check(manuscript, root)
                self.assertEqual(manuscript_lint.current(report, root), [])
                (isolated_skill / "references/scientific-writing-contract.md").write_text("v2\n", encoding="utf-8")
                self.assertTrue(any("checker, writing contract or rubric version" in e for e in manuscript_lint.current(report, root)))
                (isolated_skill / "references/scientific-writing-contract.md").write_text("v1\n", encoding="utf-8")
                rubric = isolated_skill / "references/module-quality-rubric.md"
                rubric.write_text("rubric v1\n", encoding="utf-8")
                self.assertTrue(any("checker, writing contract or rubric version" in e for e in manuscript_lint.current(report, root)))


class PipelineAndGuidanceRegressionTests(unittest.TestCase):
    def make_valid_state(self, root):
        spec = pipeline_state.definition()
        contract = root / "contract.md"
        evidence = root / "evidence.md"
        contract.write_text("Versioned research contract.\n", encoding="utf-8")
        evidence.write_text("Stage P0 evidence.\n", encoding="utf-8")
        rows = [{"id": stage, "status": "pending", "contract_version": "v1", "inputs": [], "evidence": [], "gate_verdict": "pending"} for stage in spec["stages"]]
        rows[0].update({"status": "passed", "gate_verdict": "pass", "inputs": [{"path": "contract.md", "sha256": digest(contract)}], "evidence": [{"path": "evidence.md", "sha256": digest(evidence)}]})
        return {"schema_version": 1, "pipeline": spec["pipeline"], "contract_version": "v1", "contract": [{"path": "contract.md", "sha256": digest(contract)}], "stages": rows, "history": [{"stage": spec["stages"][0], "action": "pass"}]}

    def test_pipeline_state_valid_ordered_then_rejects_unordered_and_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = self.make_valid_state(root)
            self.assertEqual(pipeline_state.validate(state, root, before="P1"), [])
            state["stages"][0]["status"] = "pending"
            state["stages"][0]["gate_verdict"] = "pending"
            state["stages"][0]["inputs"] = []
            state["stages"][0]["evidence"] = []
            state["stages"][1].update({"status": "passed", "contract_version": "v1", "gate_verdict": "pass", "inputs": [{"path": "contract.md", "sha256": digest(root / "contract.md")}], "evidence": [{"path": "evidence.md", "sha256": digest(root / "evidence.md")}]})
            state["history"] = [{"stage": "P1", "action": "pass"}]
            errors = pipeline_state.validate(state, root)
            self.assertTrue(any("predecessor has not passed" in e for e in errors))
            self.assertTrue(any("out-of-order pass" in e for e in errors))
            state = self.make_valid_state(root)
            (root / "evidence.md").write_text("changed evidence\n", encoding="utf-8")
            self.assertTrue(any("stale hash evidence.md" in e for e in pipeline_state.validate(state, root)))

    def test_legacy_guidance_without_new_packet_fields_still_validates_structurally(self):
        legacy = """# Legacy research guidance
## Title / Topic
River forecasting study.
## Core Idea
Compare a model with a baseline.
## Paper Story
Dataset access URL: https://example.org/data. Baseline and primary metric: F1. Secondary metrics: MAE. Failure signal: lower than baseline. Runtime / Hardware Budget: 2 hours.
## Paper Outline
1. Introduction: question.
2. Related Work: prior findings.
3. Method: evaluation.
4. Experiments and Results: comparisons.
5. Discussion: interpretation.
6. Conclusion: bounded answer.
## Experiment Plan
Baseline, metrics, and split.
## Expected Results
Expected strong direction.
## Traceability Checklist
Must appear in paper? Yes.
## Figure and Table Plan
Framework overview and main result table.
## Citation Scope
References should match study scope and include relevant recent work.
"""
        self.assertEqual(guidance_validator.validate(legacy), [])
        self.assertNotRegex(legacy, r"\b36\b|3-5")
        self.assertNotIn("scientific_content_packet", legacy)
        self.assertNotIn("domain_bridge", legacy)

    def test_research_and_submission_mirrors_are_byte_identical(self):
        proc = subprocess.run(
            [sys.executable, str(REPO / "scripts/sync_writing_assets.py"), "--check"],
            cwd=REPO, capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
