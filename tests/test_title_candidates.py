import unittest

from src.build_title_alias_candidates import has_specific_identifier, normalize_title


class TitleCandidateTests(unittest.TestCase):
    def test_namespaced_identifiers_retained(self):
        self.assertTrue(has_specific_identifier("HCSC-0003"))
        self.assertTrue(has_specific_identifier("Breast tumor [P101T]"))
        self.assertTrue(has_specific_identifier("CTR_d14_1"))

    def test_generic_numbering_rejected(self):
        self.assertFalse(has_specific_identifier("Patient 10"))
        self.assertFalse(has_specific_identifier("sample_001"))
        self.assertFalse(has_specific_identifier("Breast Tumor 100"))

    def test_cell_lines_rejected(self):
        self.assertFalse(has_specific_identifier("MDA-MB-231"))
        self.assertFalse(has_specific_identifier("BT549 cell, DMSO"))

    def test_terminal_polarity_preserved(self):
        self.assertNotEqual(normalize_title("TNBC011 ROI-013 PanCK+"), normalize_title("TNBC011 ROI-013 PanCK-"))


if __name__ == "__main__":
    unittest.main()
