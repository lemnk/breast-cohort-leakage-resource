import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TitleAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (ROOT / "reports" / "validation" / "title_candidate_adjudication_summary.json").read_text(
                encoding="utf-8"
            )
        )
        with (ROOT / "reports" / "validation" / "title_candidate_adjudication.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_all_frozen_candidates_are_classified(self):
        self.assertEqual(len(self.rows), 100)
        self.assertTrue(all(row["adjudication_class"] for row in self.rows))
        self.assertTrue(all(row["adjudication_evidence"] for row in self.rows))
        self.assertTrue(all(row["evidence_sources"] for row in self.rows))

    def test_counts_and_unresolved_handling_are_frozen(self):
        self.assertEqual(
            self.summary["link_classification_counts"],
            {
                "confirmed same patient/sample/material": 40,
                "probable same patient/material": 2,
                "related study/model but identity not established": 34,
                "evidence against identity": 23,
                "indeterminate": 1,
            },
        )
        self.assertEqual(self.summary["positive_manual_support_links"], 42)
        self.assertEqual(self.summary["unresolved_links"], 35)

    def test_all_rows_have_author_signoff(self):
        self.assertEqual(self.summary["author_verifier"], "Naol Beyene")
        self.assertEqual(self.summary["author_verified_links"], 100)
        self.assertTrue(all(row["author_verification"] == "Naol Beyene" for row in self.rows))
        self.assertTrue(all(row["author_verification_status"] == "Verified" for row in self.rows))


if __name__ == "__main__":
    unittest.main()
