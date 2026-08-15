"""Regression checks for the QA-only P-12 benchmark evidence."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = REPO_ROOT / "evidence" / "p12" / "benchmark_runner.py"
REPORT_PATH = REPO_ROOT / "evidence" / "p12" / "benchmark-report.json"
CANDIDATE_INPUTS_PATH = REPO_ROOT / "evidence" / "p12" / "candidate-inputs.json"
GOLDEN_MANIFEST_PATH = REPO_ROOT / "evidence" / "p12" / "approved-p12-golden-manifest.json"

spec = importlib.util.spec_from_file_location("p12_benchmark_runner", RUNNER_PATH)
if spec is None or spec.loader is None:  # pragma: no cover - import bootstrap guard
    raise RuntimeError("P-12 benchmark runner is unavailable.")
p12 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p12)


class P12BenchmarkEvidenceTests(unittest.TestCase):
    def test_report_has_zero_hard_failure_and_exact_approved_family_counts(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(report["manifest_id"], "P02-E2-1")
        self.assertEqual(report["canonical"]["positive_cases"], 27)
        self.assertEqual(report["canonical"]["base_renders"], 81)
        self.assertEqual(report["boundary"]["detected"], 27)
        self.assertEqual(report["semantic_patterns"]["cases"], 7)
        self.assertEqual(report["quantitative"]["cases"], 6)
        self.assertEqual(report["pairwise"]["uncovered_pairs"], 0)
        self.assertEqual(report["hard_failures"], [])

    def test_approved_goldens_remain_immutable_and_qa_only(self) -> None:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        self.assertTrue(report["candidate_artifacts"])
        self.assertTrue(all(item["approval_state"] == "owner-approved" for item in report["candidate_artifacts"]))
        self.assertEqual(report["approval"]["g04"], "PASS")
        self.assertFalse(report["must_pass"]["reference_packaged"])

    def test_exact_candidate_inputs_are_hash_addressed_and_owner_approved(self) -> None:
        manifest = json.loads(CANDIDATE_INPUTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["rows"]), 27)
        self.assertEqual(manifest["approval_state"], "owner-approved")
        self.assertTrue(manifest["golden_eligible"])
        self.assertTrue(all(len(row["candidate_ir_sha256"]) == 64 for row in manifest["rows"]))
        self.assertTrue(all(row["approval_state"] == "owner-approved" for row in manifest["rows"]))
        self.assertTrue(all(row["golden_eligible"] for row in manifest["rows"]))

    def test_approved_golden_manifest_matches_all_18_artifacts(self) -> None:
        from golden_review import compare

        result = compare(GOLDEN_MANIFEST_PATH, GOLDEN_MANIFEST_PATH.parent)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["immutable"])
        self.assertEqual(result["compared"], 18)

    def test_pairwise_generator_covers_every_declared_pair(self) -> None:
        rows = p12._pairwise_rows()
        dimensions = {
            "size": ["doc-inline", "doc-wide", "slide-16x9", "slide-4x3", "social-og", "social-square", "print-a4-landscape", "print-letter-landscape", "fit"],
            "detail": ["faithful", "balanced", "simplified"],
            "audience": ["engineer", "mixed", "executive"],
            "format": ["html", "svg", "png", "html+png"],
            "language": ["vi", "en"],
        }
        names = list(dimensions)
        for index, first in enumerate(names):
            for second in names[index + 1:]:
                observed = {(row[first], row[second]) for row in rows}
                expected = {(left, right) for left in dimensions[first] for right in dimensions[second]}
                self.assertEqual(observed, expected, msg=f"missing pair: {first} × {second}")


if __name__ == "__main__":
    unittest.main()
