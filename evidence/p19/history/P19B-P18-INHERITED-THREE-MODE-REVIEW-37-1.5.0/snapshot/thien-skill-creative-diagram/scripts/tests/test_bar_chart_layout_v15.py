"""Focused D-088 tests for the eight-sprint bar chart."""
import copy
import re
import unittest

from diagram_core import CoreError
from bar_chart_layout_v15 import (
    EXPECTED_POINTS, bar_chart_table, layout_bar_chart,
    render_bar_chart, validate_bar_chart_svg,
)
from bar_chart_review08_fixture import bar_chart_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual


class DetailedBarChartTests(unittest.TestCase):
    def setUp(self):
        self.fixture = bar_chart_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_material_scale_and_focal(self):
        layout = layout_bar_chart(self.plan)
        self.assertEqual(tuple(point["id"] for point in layout["points"]), EXPECTED_POINTS)
        self.assertEqual(layout["axes"]["axis-story-points"]["domain_min"], 0)
        self.assertEqual(layout["axes"]["axis-story-points"]["domain_max"], 120)
        self.assertEqual([point["id"] for point in layout["points"] if point["focal"]], ["sprint-05"])

    def test_serialized_bars_axes_ticks_and_arrow_free_baseline(self):
        svg = "<svg>" + render_bar_chart(self.plan) + "</svg>"
        self.assertEqual(validate_bar_chart_svg(svg), {"bars": 8, "focal": 1, "axes": 2, "ticks": 6})
        baseline = re.search(r'<line class="bar-chart-axis" data-axis-id="axis-sprint"[^>]+>', svg).group()
        self.assertNotIn("marker-end", baseline)

    def test_all_points_appear_in_alternative_table(self):
        table = bar_chart_table(self.plan)
        for point_id in EXPECTED_POINTS:
            self.assertIn(point_id, table)
        self.assertEqual(table.count("<tr>"), 9)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-bar-chart")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 1800 940"', svg)
            self.assertIn("Sprint 5 · kỷ lục 108 điểm", svg)
            validate_bar_chart_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_nonzero_baseline_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["axes"][1]["domain_min"] = 20
        with self.assertRaises((CoreError, ValueError)):
            layout_bar_chart(adapt_visual(fixture))

    def test_wrong_focal_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["annotations"][0]["target_ids"] = ["sprint-06"]
        with self.assertRaises(ValueError):
            layout_bar_chart(adapt_visual(fixture))

    def test_missing_value_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][0]["data"][2]["value"] = None
        fixture["series"][0]["data"][2]["missing"] = True
        with self.assertRaises(ValueError):
            layout_bar_chart(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
