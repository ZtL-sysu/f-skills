import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/f-guidance-builder-v1/scripts/validate_guidance.py'
spec = importlib.util.spec_from_file_location('top_venue_validator', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class TopVenueArtifactsTest(unittest.TestCase):
    def test_missing_complete_and_empty(self):
        names = ('paper-cards.md', 'narrative-moves.md', 'experiment-matrix-template.md',
                 'execution-conventions.md', 'gap-analysis.md', 'contract-delta.md')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(len(validator.validate_top_venue_study(root)), 6)
            for name in names:
                (root / name).write_text('evidence', encoding='utf-8')
            self.assertEqual(validator.validate_top_venue_study(root), [])
            (root / names[0]).write_text('  ', encoding='utf-8')
            self.assertEqual(len(validator.validate_top_venue_study(root)), 1)


if __name__ == '__main__':
    unittest.main()
