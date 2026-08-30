"""Focused executable contract for the P-18 owner-review gallery."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path


P18_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = P18_DIR.parents[1]
SOURCE_DIR = P18_DIR / "source"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from generate_p18_gallery import build_outputs, source_bundle_hash  # noqa: E402
from p18_cases import CASE_META, MODES, all_cases  # noqa: E402
from p18_qa import P18QAFailure, validate_rendered  # noqa: E402
from p18_renderer import render_specimen  # noqa: E402


class P18GalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_hash = source_bundle_hash()
        cls.rendered = [render_specimen(case_id, mode, source_bundle_hash=cls.bundle_hash) for case_id in CASE_META for mode in MODES]
        cls.manifest = json.loads((P18_DIR / "PILOT-MANIFEST.json").read_text(encoding="utf-8"))

    def test_exact_12_by_3_matrix_and_non_counted_index(self) -> None:
        self.assertEqual(len(CASE_META), 12)
        self.assertEqual(len(MODES), 3)
        self.assertEqual(len(self.rendered), 36)
        self.assertEqual(self.manifest["specimen_count"], 36)
        self.assertFalse(self.manifest["index"]["counted_as_specimen"])
        self.assertEqual({item.mode for item in self.rendered}, set(MODES))

    def test_all_exact_case_fixtures_validate_semantically(self) -> None:
        cases = all_cases()
        self.assertEqual(set(cases), set(CASE_META))
        self.assertEqual({value["schema_version"] for value in cases.values()}, {"1.5"})
        self.assertTrue(all(value["fidelity"]["invented_count"] == 0 for value in cases.values()))

    def test_every_specimen_passes_all_technical_checks(self) -> None:
        for specimen in self.rendered:
            report = validate_rendered(specimen)
            self.assertEqual(report["technical_status"], "PASS", (specimen.case_id, specimen.mode))
            self.assertEqual(report["visual_review"]["status"], "OWNER-REVIEW-PENDING")

    def test_generated_outputs_are_byte_deterministic(self) -> None:
        outputs = build_outputs()
        for path, expected in outputs.items():
            self.assertTrue(path.exists(), path)
            self.assertEqual(path.read_bytes(), expected, path)

    def test_manifest_hashes_bind_every_standalone_file(self) -> None:
        artifacts = self.manifest["artifacts"]
        self.assertEqual(len(artifacts), 36)
        self.assertEqual(len({item["path"] for item in artifacts}), 36)
        for item in artifacts:
            path = REPO_ROOT / item["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])
            self.assertEqual(item["source_bundle_sha256"], self.bundle_hash)
            self.assertEqual(item["checks"]["technical_status"], "PASS")

    def test_provenance_receipt_is_one_to_one_with_manifest(self) -> None:
        receipts = json.loads((P18_DIR / "PROVENANCE-RECEIPTS.json").read_text(encoding="utf-8"))["receipts"]
        self.assertEqual(len(receipts), 36)
        manifest_keys = {(item["case_id"], item["mode"], item["sha256"]) for item in self.manifest["artifacts"]}
        receipt_keys = {(item["case_id"], item["mode"], item["artifact_sha256"]) for item in receipts}
        self.assertEqual(receipt_keys, manifest_keys)
        self.assertTrue(all(item["upstream_gallery_code_css_template_asset_used"] is False for item in receipts))
        self.assertTrue(all(item["benchmark_expression_reused"] is False for item in receipts))

    def test_gallery_is_script_free_and_has_no_machine_path(self) -> None:
        forbidden = ("<script", "javascript:", "/Users/", "file://", "@import", "<link")
        for path in sorted((P18_DIR / "gallery").glob("*.html")) + [P18_DIR / "index.html"]:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, (path, token))

    def test_geometry_check_rejects_out_of_canvas_y_coordinate(self) -> None:
        specimen = self.rendered[0]
        mutated_svg = specimen.svg.replace('d="M258 446 H366"', 'd="M258 946 H366"', 1)
        self.assertNotEqual(mutated_svg, specimen.svg)
        with self.assertRaises(P18QAFailure):
            validate_rendered(replace(specimen, svg=mutated_svg))

    def test_owner_gate_and_p19_remain_closed(self) -> None:
        self.assertEqual(self.manifest["owner_visual_approval"], "PENDING")
        self.assertEqual(self.manifest["gate"], "G-03@1.5.0 NOT-EVALUATED")
        self.assertIn("no P-19", self.manifest["scope_boundary"])

    def test_dist_release_aggregate_is_unchanged(self) -> None:
        dist = REPO_ROOT / "dist"
        lines = []
        for path in sorted(value for value in dist.rglob("*") if value.is_file() and value.name != ".DS_Store"):
            lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(REPO_ROOT).as_posix()}\n")
        aggregate = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
        self.assertEqual(aggregate, "188526fdf60b53183723bb231a6940896a42cf90db5df71094eebc66ac45c065")


if __name__ == "__main__":
    unittest.main()
