from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from p11_coverage import P11_HARD_FAILURES
import test_golden_review
import test_qa_contract
import test_safe_import


class P11HardFailureCoverageTests(unittest.TestCase):
    def test_registry_covers_every_p11_workstream_and_has_unique_test_ids(self) -> None:
        categories = {item["category"] for item in P11_HARD_FAILURES.values()}
        self.assertEqual(categories, {
            "contract", "coverage", "determinism", "geometry", "accessibility",
            "vietnamese-typography", "quantitative", "import-fidelity",
            "import-security", "motion", "package-hygiene", "golden",
        })
        test_ids = [item["test_id"] for item in P11_HARD_FAILURES.values()]
        self.assertEqual(len(test_ids), len(set(test_ids)))
        self.assertGreaterEqual(len(P11_HARD_FAILURES), 55)
        self.assertTrue(all(item["status"] == "detected" for item in P11_HARD_FAILURES.values()))

    def test_every_registry_mutation_test_exists(self) -> None:
        modules = (test_qa_contract, test_golden_review, test_safe_import)
        classes = {name: value for module in modules for name, value in vars(module).items() if isinstance(value, type)}
        for failure, item in P11_HARD_FAILURES.items():
            class_name, method_name = item["mutation_test"].split(".", 1)
            with self.subTest(failure=failure):
                self.assertIn(class_name, classes)
                self.assertTrue(callable(getattr(classes[class_name], method_name, None)))


if __name__ == "__main__":
    unittest.main()

