import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from models.schema import validate_dataset

class DatasetTests(unittest.TestCase):
    def test_dataset_valid(self):
        items = json.loads((ROOT / "data/evaluation/synthetic_examples.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_dataset(items), {})
        self.assertGreaterEqual(len(items), 20)
