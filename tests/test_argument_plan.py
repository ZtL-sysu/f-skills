"""Validate scientific reference integrity at the paragraph input boundary."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/f-research-v1/scripts/writing_adapter.py"
spec = importlib.util.spec_from_file_location("argument_adapter", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class ArgumentPlanTests(unittest.TestCase):
    def packet(self):
        return {"schema_version": 1, "brief": {
            "question": "What explains the pattern?", "audience": "Researchers",
            "section_jobs": {"Discussion": "Interpret a possible explanation"},
            "paragraph_plan": [{"id": "d1", "section": "Discussion", "point": "A possible mechanism",
                                "fact_ids": ["h1"], "adds": "Explain the possible mechanism"}],
            "qualification_placement": [{"fact_id": "h1", "home": "Discussion d1",
                                         "repeat_when": "A later passage invokes this explanation"}]},
            "facts": [{"id": "h1", "kind": "hypothesis", "status": "unresolved",
                       "statement": "The mechanism is a hypothesis."}], "internal": {"reviewer": "private concern"}}

    def build(self, packet):
        with tempfile.TemporaryDirectory() as tmp:
            return adapter.build(packet, Path(tmp), "P7", "Draft Discussion")

    def test_plan_drives_actual_task_without_upgrading_support(self):
        result = self.build(self.packet())
        task = json.loads(result["messages"][-1]["content"])
        self.assertIn("composition_task", task)
        self.assertIn("qualification_task", task)
        self.assertEqual(task["scientific_content"][0]["status"], "unresolved")
        self.assertNotIn("private concern", json.dumps(result["messages"]))

    def test_missing_fact_reference_rejected(self):
        p = self.packet()
        p["brief"]["paragraph_plan"][0]["fact_ids"] = ["invented"]
        with self.assertRaisesRegex(ValueError, "missing scientific facts"):
            self.build(p)

    def test_verification_note_is_external_but_scientific_attribution_survives(self):
        p = self.packet()
        p['facts'][0]['attribution'] = 'Hypothesis proposed by the author'
        p['facts'][0]['verification_note'] = 'Access log: inspected abstract only at local/file.html'
        result = self.build(p)
        context = json.dumps(result['messages'])
        self.assertNotIn('Access log', context)
        self.assertNotIn('local/file.html', context)
        self.assertIn('Hypothesis proposed by the author', context)
        self.assertEqual(result['provenance']['verification_notes'][0]['fact_id'], 'h1')

    def test_duplicate_move_rejected(self):
        p = self.packet()
        p["brief"]["paragraph_plan"].append(copy.deepcopy(p["brief"]["paragraph_plan"][0]))
        with self.assertRaisesRegex(ValueError, "IDs unique"):
            self.build(p)

    def test_qualification_has_one_defined_home(self):
        for mutation in ("missing", "duplicate", "empty"):
            p = self.packet()
            placements = p["brief"]["qualification_placement"]
            if mutation == "missing":
                placements[0]["fact_id"] = "invented"
            elif mutation == "duplicate":
                placements.append(copy.deepcopy(placements[0]))
            else:
                placements[0]["repeat_when"] = ""
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.build(p)

    def test_legacy_packet_still_builds(self):
        p = self.packet()
        del p["brief"]["paragraph_plan"], p["brief"]["qualification_placement"]
        task = json.loads(self.build(p)["messages"][-1]["content"])
        self.assertNotIn("composition_task", task)

    def test_reference_metadata_is_required_before_drafting(self):
        p = self.packet()
        p['facts'][0].update(kind='reference', status='author_reported')
        with self.assertRaisesRegex(ValueError, 'citation authors/title/year/url'):
            self.build(p)

    def test_complete_citation_reaches_writer(self):
        import hashlib
        p = self.packet()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'reference.txt'
            source.write_text('Supplied citation evidence')
            p['facts'][0].update(kind='reference', status='author_reported', citation={
                'authors': ['Author'], 'title': 'Supplied title', 'year': 2020, 'url': 'https://example.org/source'},
                evidence=[{'path': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}])
            task = json.loads(adapter.build(p, root, 'P7', 'Write context')['messages'][-1]['content'])
            self.assertEqual(task['scientific_content'][0]['citation']['title'], 'Supplied title')

    def test_math_escape_corruption_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'control characters'):
            adapter.response_parts({'manuscript': 'Let \x07lpha be a mass.', 'notes': ''})
        result = adapter.response_parts({'manuscript': r'Let \(\alpha\) be a mass.', 'notes': ''})
        self.assertIn(r'\alpha', result[0])

    def test_composed_revision_keeps_audit_warning_out_and_scientific_scope_in(self):
        p = self.packet()
        edit = {'proposition': 'Reviewer warning: never claim a universal mechanism',
                'evidence_status': 'unresolved', 'action': 'REWRITE', 'location': 'Discussion',
                'factual_check': 'Audit warning: do not imply causality',
                'composition': {'point': 'Interpret a possible explanation', 'fact_ids': ['h1'],
                                'preserve': ['The proposed mechanism remains a hypothesis.']}}
        with tempfile.TemporaryDirectory() as tmp:
            result = adapter.build(p, Path(tmp), 'P10', 'Revise Discussion', source='Current text', edits=[edit])
        context = json.dumps(result['messages'])
        self.assertNotIn('Reviewer warning', context)
        self.assertNotIn('Audit warning', context)
        self.assertIn('mechanism remains a hypothesis', context)
        self.assertEqual(result['provenance']['revision_checks'][0]['factual_check'], edit['factual_check'])

    def test_composition_rejects_nonexistent_support(self):
        edit = {'proposition': 'Review concern', 'evidence_status': 'unresolved',
                'action': 'REWRITE', 'location': 'Discussion', 'factual_check': 'Check scientific scope',
                'composition': {'point': 'Interpret the result', 'fact_ids': ['fake'], 'preserve': []}}
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(ValueError, 'composition references'):
            adapter.build(self.packet(), Path(tmp), 'P10', 'Revise', source='Current text', edits=[edit])


if __name__ == "__main__":
    unittest.main()
