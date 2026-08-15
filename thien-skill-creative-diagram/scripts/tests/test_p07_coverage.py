from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from p07_coverage import P07_COVERAGE, SPECIMEN_TOTAL
from semantic_catalog import expected_capability_ids


class P07CoverageTests(unittest.TestCase):
    def test_exact_capability_inventory_is_covered(self) -> None:
        self.assertEqual(set(P07_COVERAGE), expected_capability_ids())
        self.assertEqual(len(P07_COVERAGE), 95)
        for capability_id, entry in P07_COVERAGE.items():
            with self.subTest(capability_id=capability_id):
                self.assertTrue(entry["p07_disposition"])
                self.assertTrue(entry["visual_or_import_evidence"])
                self.assertTrue(entry["boundary"])

    def test_p08_boundary_is_explicit(self) -> None:
        for capability_id in [f"CAP-O{i:02d}" for i in range(1, 8)] + [f"CAP-M{i:02d}" for i in range(1, 13)]:
            self.assertIn("P-08", P07_COVERAGE[capability_id]["boundary"])
            self.assertNotIn("implemented", P07_COVERAGE[capability_id]["p07_disposition"])

    def test_all_p07_imports_have_implemented_disposition(self) -> None:
        for index in range(1, 12):
            self.assertEqual(P07_COVERAGE[f"CAP-I{index:02d}"]["p07_disposition"], "implemented-safe-import")

    def test_locked_specimen_total_is_preserved(self) -> None:
        self.assertEqual(SPECIMEN_TOTAL, 97)


if __name__ == "__main__":
    unittest.main()
