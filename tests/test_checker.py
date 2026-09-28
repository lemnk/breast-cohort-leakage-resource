import unittest

from src.check_cohort_overlap import check, normalize_gse


class CheckerTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_gse("25055"), "GSE25055")
        with self.assertRaises(ValueError):
            normalize_gse("GPL96")

    def test_known_expression_overlap(self):
        row = check(["GSE20194", "GSE25055"])[0]
        self.assertEqual(row["status"], "high_confidence_overlap")
        self.assertIn("expression_confirmed=187", row["details"])

    def test_no_evidence_worded_cautiously(self):
        row = check(["GSE25055", "GSE25065"])[0]
        self.assertEqual(row["status"], "no_detected_evidence")
        self.assertIn("Not proof", row["details"])


if __name__ == "__main__":
    unittest.main()
