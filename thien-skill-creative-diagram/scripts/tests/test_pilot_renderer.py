"""P-06 visual-system and pilot-renderer checks."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from pilot_cases import PILOT_BUILDERS, bar_pilot, swimlane_pilot  # noqa: E402
from pilot_renderer import MODE_IDS, VisualError, generate_pilots, render_pilot  # noqa: E402
from visual_system import contrast_report, load_visual_system, validate_contrast  # noqa: E402


class VisualSystemTests(unittest.TestCase):
    def test_exact_three_approved_modes_and_contrast_pairs(self):
        system = load_visual_system()
        self.assertEqual(set(system["modes"]), set(MODE_IDS))
        report = validate_contrast(system)
        self.assertTrue(report)
        self.assertTrue(all(item["status"] == "pass" for item in report))

    def test_slide_material_text_minimum_is_not_compressed(self):
        primitives = load_visual_system()["primitives"]
        self.assertGreaterEqual(primitives["font_label"], 20)
        self.assertGreaterEqual(primitives["font_annotation"], 20)

    def test_contrast_report_is_deterministic(self):
        system = load_visual_system()
        self.assertEqual(contrast_report(system), contrast_report(system))


class PilotRendererTests(unittest.TestCase):
    def test_only_three_authorized_pilot_families_exist(self):
        self.assertEqual(set(PILOT_BUILDERS), {"architecture", "bar-chart", "swimlane"})
        with self.assertRaises(VisualError):
            render_pilot("flowchart", "neutral-light")

    def test_all_nine_mode_case_combinations_render_deterministically(self):
        for case_name in PILOT_BUILDERS:
            for mode in MODE_IDS:
                with self.subTest(case=case_name, mode=mode):
                    first = render_pilot(case_name, mode)
                    second = render_pilot(case_name, mode)
                    self.assertEqual(first.svg, second.svg)
                    self.assertEqual(first.html, second.html)
                    self.assertEqual(first.validation["serialization"]["status"], "pass")
                    ET.fromstring(first.svg)

    def test_svg_has_unique_ids_and_no_executable_or_remote_content(self):
        for case_name in PILOT_BUILDERS:
            result = render_pilot(case_name, "neutral-light")
            root = ET.fromstring(result.svg)
            ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
            self.assertEqual(len(ids), len(set(ids)))
            lowered = result.svg.lower().replace('xmlns="http://www.w3.org/2000/svg"', "")
            for token in ("<script", "http://", "https://", "javascript:", "onload=", "onclick="):
                self.assertNotIn(token, lowered)

    def test_relationship_pilots_pass_geometry_checks(self):
        for case_name in ("architecture", "swimlane"):
            result = render_pilot(case_name, "editorial")
            self.assertEqual(result.validation["geometry"]["status"], "pass")
            self.assertGreater(len(result.node_bounds), 0)
            self.assertGreater(len(result.routes), 0)

    def test_grouped_bar_retains_exact_values_zero_baseline_and_table(self):
        ir = bar_pilot()
        expected = [[12, 18, 9, 16], [24, 20, 28, 22]]
        for mode in MODE_IDS:
            result = render_pilot("bar-chart", mode)
            self.assertEqual(result.validation["quantitative"]["values"], expected)
            self.assertTrue(result.validation["quantitative"]["zero_baseline"])
            self.assertIn("<table", result.html)
            for series in ir["series"]:
                for datum in series["data"]:
                    self.assertIn(str(datum["value"]), result.html)

    def test_swimlane_covers_approved_benchmark_semantics(self):
        ir = swimlane_pilot()
        result = render_pilot("swimlane", "neutral-dark")
        benchmark = result.validation["benchmark"]
        self.assertEqual(benchmark["lanes"], 6)
        self.assertEqual(benchmark["owner_groups"], 2)
        self.assertEqual(benchmark["handoffs"], ["(1)", "(2)", "(3)", "(4)", "(5)"])
        self.assertEqual(benchmark["roles"], ["document", "file", "listing", "money"])
        self.assertIn("Thủ quỹ", result.svg)
        self.assertIn("Kế toán trưởng", result.svg)
        for label in ("Khách hàng", "Phòng thư", "Thu tiền", "Phải thu", "Sổ cái", "Ngân hàng"):
            self.assertIn(label, result.svg)
        self.assertEqual(len(ir["edges"]), 10)

    def test_generation_writes_18_pilots_and_one_contact_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            manifest = generate_pilots(output)
            self.assertEqual(manifest["artifact_count"], 18)
            self.assertEqual(len(manifest["artifacts"]), 9)
            self.assertEqual(len(list(output.glob("pilot-*.svg"))), 9)
            self.assertEqual(len(list(output.glob("pilot-*.html"))), 9)
            contact = (output / "contact-sheet.html").read_text(encoding="utf-8")
            self.assertEqual(contact.count("<img "), 9)
            loaded = json.loads((output / "pilot-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded["approval"], "golden-candidate; owner review required")


if __name__ == "__main__":
    unittest.main()
