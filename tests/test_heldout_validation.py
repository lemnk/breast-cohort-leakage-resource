import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HeldoutValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (ROOT / "data" / "heldout" / "heldout_crossplatform_summary.json").read_text(
                encoding="utf-8"
            )
        )

    def test_pair_was_metadata_selected(self):
        self.assertIn("protocol-frozen before expression download", self.summary["selection_status"])
        self.assertEqual(self.summary["platform_pair"], "GPL96--GPL570")

    def test_mixed_result_is_preserved(self):
        self.assertEqual(
            self.summary["evidence_counts"],
            {"confirmed": 2, "supported": 0, "not_corroborated": 1},
        )

    def test_controls_do_not_trigger(self):
        self.assertEqual(self.summary["control_n"], 15)
        self.assertEqual(self.summary["control_rule_counts"]["confirmed"], 0)
        self.assertEqual(self.summary["control_rule_counts"]["supported"], 0)


if __name__ == "__main__":
    unittest.main()
