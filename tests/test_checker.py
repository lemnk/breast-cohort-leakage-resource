import unittest

from src.check_cohort_overlap import check, normalize_gse


class CheckerTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_gse("25055"), "GSE25055")
        with self.assertRaises(ValueError):
            normalize_gse("GPL96")

    def test_expression_only_pair_is_review_candidate(self):
        row = check(["GSE20194", "GSE25055"])[0]
        self.assertEqual(row["status"], "candidate_relationship_review_required")
        self.assertIn("expression_corroborated_candidate=187", row["details"])
        self.assertNotIn("expression_confirmed", row["details"])

    def test_exact_gsm_overlap_is_direct(self):
        row = check(["GSE81540", "GSE96058"])[0]
        self.assertEqual(row["status"], "direct_accession_overlap")
        self.assertIn("exact_GSM=3409", row["details"])

    def test_no_evidence_worded_cautiously(self):
        row = check(["GSE25055", "GSE25065"])[0]
        self.assertEqual(row["status"], "no_detected_evidence")
        self.assertIn("Not proof", row["details"])


if __name__ == "__main__":
    unittest.main()
