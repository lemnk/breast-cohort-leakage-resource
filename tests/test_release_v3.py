import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "release_v3" / "cohort_overlap_lookup.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.by_pair = {(row["series_a"], row["series_b"]): row for row in cls.rows}

    def test_expression_only_pairs_are_not_direct_overlap(self):
        row = self.by_pair[("GSE20194", "GSE25055")]
        self.assertEqual(row["exact_gsm_count"], "0")
        self.assertEqual(row["evidence_class"], "candidate_relationship_review_required")

    def test_exact_overlap_pair_is_direct(self):
        row = self.by_pair[("GSE81540", "GSE96058")]
        self.assertEqual(row["exact_gsm_count"], "3409")
        self.assertEqual(row["evidence_class"], "direct_accession_overlap")

    def test_control_summary_has_no_probability_bound(self):
        summary = json.loads(
            (ROOT / "data" / "overlap_v3" / "expression_candidate_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["control_rule_counts"]["strong_rule_exceeded"], 0)
        self.assertEqual(summary["control_rule_counts"]["weaker_rule_exceeded"], 4)
        self.assertFalse(any("bound" in key.lower() for key in summary))

    def test_bounded_evaluation_matches_direct_intersection(self):
        summary = json.loads(
            (ROOT / "reports" / "resource_evaluation" / "evaluation_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["screened_pairs"], 435)
        self.assertEqual(summary["checker_direct_count_mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
