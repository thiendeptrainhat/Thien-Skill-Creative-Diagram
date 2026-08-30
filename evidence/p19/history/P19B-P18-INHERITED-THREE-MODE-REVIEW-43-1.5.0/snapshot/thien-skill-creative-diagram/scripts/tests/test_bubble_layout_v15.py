"""Focused D-120 Bubble layout tests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "evidence/p19/source"
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", SOURCE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from bubble_layout_v15 import bubble_table, layout_bubble, render_bubble, validate_bubble_svg
from bubble_review40_fixture import bubble_fixture
from visual_adapters_v15 import adapt_visual


class BubbleLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(bubble_fixture())

    def test_identity_semantics_remain_capability_bound(self):
        self.assertEqual(self.plan["adapter"]["capability_id"], "CAP-V20")
        self.assertEqual(self.plan["adapter"]["canonical_type"], "scatter-plot")

    def test_area_not_radius_is_linear(self):
        points = layout_bubble(self.plan)["points"]
        self.assertEqual(len(points), 7)
        self.assertEqual(len({round(point["radius"] ** 2 / point["area_value"], 10) for point in points}), 1)

    def test_exact_axes_focal_and_table(self):
        report = validate_bubble_svg("<svg>" + render_bubble(self.plan) + "</svg>")
        self.assertEqual(report, {"bubbles": 7, "focal": 1, "axes": 2, "x_ticks": 8, "y_ticks": 9, "area_scale_constant": 57.8})
        self.assertEqual(bubble_table(self.plan).count("<tr>"), 8)


if __name__ == "__main__":
    unittest.main()
