import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExplicitGeoReuseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (ROOT / "reports" / "validation" / "explicit_geo_reuse_summary.json").read_text(
                encoding="utf-8"
            )
        )
        with (ROOT / "reports" / "validation" / "explicit_geo_reuse_relationships.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_explicit_cross_series_relationships_are_recovered(self):
        self.assertEqual(self.summary["third_party_reanalysis_series"], 27)
        self.assertEqual(self.summary["cross_series_referenced_gsms_mapped_inside_query_universe"], 35)
        self.assertEqual(
            self.summary["pair_counts"],
            {"GSE22664--GSE3156": 2, "GSE65314--GSE32124": 33},
        )

    def test_relationships_are_kept_separate_from_identity_evidence(self):
        self.assertEqual(len(self.rows), 35)
        self.assertTrue(all(row["relationship_type"] == "explicit normalization data reuse" for row in self.rows))
        self.assertIn("do not by themselves establish shared patients", self.summary["interpretation"])


if __name__ == "__main__":
    unittest.main()
