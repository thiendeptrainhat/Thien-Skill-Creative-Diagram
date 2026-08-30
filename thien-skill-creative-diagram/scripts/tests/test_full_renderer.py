from __future__ import annotations

import copy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from full_renderer import RENDERER_VERSION, render_static
from semantic_catalog import PATTERNS, TYPE_GRAMMARS, VARIANT_MAPPINGS
from semantic_fixtures import axis, datum, finalize, fixtures, legacy_fixtures, series
from semantic_patterns import apply_pattern


MODES = ("neutral-light", "neutral-dark", "editorial")
MODE_VARIANTS = {"CAP-V01": "neutral-light", "CAP-V02": "neutral-dark", "CAP-V03": "editorial"}


class FullCoverageRendererTests(unittest.TestCase):
    def test_all_27_types_render_in_all_three_modes_deterministically(self) -> None:
        cases = legacy_fixtures()
        self.assertEqual(len(cases), 27)
        self.assertTrue(set(cases) < set(TYPE_GRAMMARS))
        hashes: set[str] = set()
        for diagram_type, ir in cases.items():
            for mode in MODES:
                with self.subTest(diagram_type=diagram_type, mode=mode):
                    first = render_static(ir, mode)
                    second = render_static(copy.deepcopy(ir), mode)
                    self.assertEqual(first.svg, second.svg)
                    self.assertEqual(first.sha256, second.sha256)
                    self.assertEqual(first.validation["renderer_version"], RENDERER_VERSION)
                    self.assertEqual(ET.fromstring(first.svg).tag.rsplit("}", 1)[-1], "svg")
                    hashes.add(first.sha256)
        self.assertEqual(len(hashes), 81)

    def test_all_16_variants_have_visual_smoke_or_declared_text_fallback(self) -> None:
        cases = legacy_fixtures()
        for capability_id, variant in list(VARIANT_MAPPINGS.items())[:16]:
            parent = "architecture" if "all" in variant["parents"] else variant["parents"][0]
            ir = copy.deepcopy(cases[parent])
            ir["diagram"]["variant_ids"] = [capability_id]
            with self.subTest(capability_id=capability_id, parent=parent):
                result = render_static(ir, MODE_VARIANTS.get(capability_id, "neutral-light"))
                self.assertEqual(result.validation["status"], "pass")
                if capability_id == "CAP-V15":
                    self.assertNotIn("<image", result.svg)
                if capability_id == "CAP-V12":
                    self.assertIn("hatch", result.svg)
                if capability_id == "CAP-V13":
                    self.assertIn("Terminal frame", result.svg)

    def test_untrusted_labels_are_escaped_as_text(self) -> None:
        ir = copy.deepcopy(fixtures()["architecture"])
        ir["nodes"][0]["label"] = '<script>alert("x")</script>'
        result = render_static(ir)
        self.assertNotIn("<script>", result.svg)
        self.assertIn("&lt;script&gt;", result.svg)

    def test_bar_zero_baseline_handles_positive_zero_negative_and_missing(self) -> None:
        ir = finalize("bar-chart", series=[series("series-values", "Giá trị", [datum("bar-positive", "Dương", 12), datum("bar-zero", "Không", 0), datum("bar-negative", "Âm", -3), datum("bar-missing", "Thiếu", None)], "sự cố")], axes=[axis("axis-category", "x", "categorical", "Loại"), axis("axis-value", "y", "linear", "Sự cố", domain_min=-5, domain_max=20, unit="sự cố")])
        result = render_static(ir)
        self.assertIn('data-zero-baseline="true"', result.svg)
        self.assertIn('id="p07-bar-chart-neutral-light-bar-negative"', result.svg)
        self.assertIn(">-3</text>", result.svg)

    def test_all_seven_semantic_patterns_render_under_existing_parent(self) -> None:
        facts = {
            "CAP-P01":{"producers":["A","B"],"queue":"Hàng đợi","sink":"Kho","capacity":"100","overflow":"Tràn"},
            "CAP-P02":{"stages":[{"activity":"Nhận","artifact":"Phiếu","owner":"Đơn vị A"},{"activity":"Duyệt","artifact":"Biên bản","owner":"Đơn vị B"}]},
            "CAP-P03":{"input":"Ghi chú","transform":"Chuẩn hóa","output":"Hồ sơ"},
            "CAP-P04":{"request":"Yêu cầu","policy":"Chính sách","allow_outcome":"Cho phép","deny_outcome":"Từ chối"},
            "CAP-P05":{"requester":"Nhóm","gateway":"Cổng","service":"Dịch vụ","denied_route":"Đường tắt","approved_label":"Được duyệt","denied_label":"Bị chặn","boundary":"Vùng tin cậy"},
            "CAP-P06":{"layers":[{"layer":"Biên","owner":"An toàn","control":"Tường lửa"},{"layer":"Dữ liệu","owner":"An toàn","control":"Mã hóa"}]},
            "CAP-P07":{"layers":["Biên","Dữ liệu"],"controls":["Tường lửa","Mã hóa"],"owner":"An toàn","residual_risk":"Rủi ro còn lại"},
        }
        for capability_id, pattern in PATTERNS.items():
            transformed = apply_pattern(capability_id, facts[capability_id])
            ir = finalize(pattern["parent"], **{key: transformed[key] for key in ("nodes","edges","groups","lanes","series","axes","annotations")})
            with self.subTest(capability_id=capability_id):
                self.assertEqual(render_static(ir).validation["status"], "pass")

    def test_static_coverage_does_not_implement_p08_motion_or_export(self) -> None:
        result = render_static(fixtures()["flowchart"])
        lowered = result.svg.lower()
        self.assertNotIn("<script", lowered)
        self.assertNotIn("animation", lowered)
        self.assertNotIn("data:image", lowered)


if __name__ == "__main__":
    unittest.main()
