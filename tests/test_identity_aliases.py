import unittest

from src.build_identity_edges import compact, source_identifier, title_core, aliases_for_sample


class AliasTests(unittest.TestCase):
    def test_title_cleanup(self):
        self.assertEqual(title_core("BR_FNA_M485"), "m485")
        self.assertEqual(title_core("breast cancer SPAIN57"), "spain57")
        self.assertEqual(title_core("Br Ca Pt sample #S1178752-1"), "s11787521")

    def test_source_requires_explicit_cue(self):
        self.assertEqual(source_identifier("breast cancer, sample ISPY-1002"), "ispy1002")
        self.assertEqual(source_identifier("Sample ID -- 157, fine-needle aspiration"), "157")
        self.assertIsNone(source_identifier("pre-treatment breast cancer tumor biopsy"))

    def test_numeric_title_is_study_aware(self):
        base = {"series_accession": "GSE20271", "sample_title": "breast cancer 485", "source_name_ch1": "biopsy"}
        self.assertIn(("m485", "study_aware_title"), aliases_for_sample(base, []))
        outside = dict(base, series_accession="GSE99999")
        self.assertEqual(aliases_for_sample(outside, []), [])

    def test_numeric_title_uses_explicit_namespace(self):
        row = {"series_accession": "GSE25055", "sample_title": "1002", "source_name_ch1": "breast cancer, sample ISPY-1002"}
        self.assertIn(("ispy1002", "source_namespaced_title"), aliases_for_sample(row, []))

    def test_short_alias_rejected(self):
        row = {"series_accession": "GSE99999", "sample_title": "S2", "source_name_ch1": "breast cancer"}
        self.assertEqual(aliases_for_sample(row, []), [])


if __name__ == "__main__":
    unittest.main()
