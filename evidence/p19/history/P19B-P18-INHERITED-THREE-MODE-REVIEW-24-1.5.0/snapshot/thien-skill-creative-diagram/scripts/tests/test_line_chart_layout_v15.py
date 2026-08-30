"""Focused D-096 tests for the three-series, eight-week line chart."""
import copy
import re
import unittest

from line_chart_layout_v15 import (
    EXPECTED_DOMAINS, EXPECTED_SERIES, layout_line_chart, line_chart_table,
    render_line_chart, validate_line_chart_svg,
)
from line_chart_review16_fixture import line_chart_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual


class DetailedLineChartTests(unittest.TestCase):
    def setUp(self):
        self.fixture = line_chart_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_three_series_eight_weeks_and_scale(self):
        layout = layout_line_chart(self.plan)
        self.assertEqual(tuple(item["id"] for item in layout["series"]), EXPECTED_SERIES)
        self.assertTrue(all(tuple(point["domain"] for point in item["points"]) == EXPECTED_DOMAINS for item in layout["series"]))
        self.assertEqual(sum(len(item["points"]) for item in layout["series"]), 24)
        self.assertEqual((layout["axes"]["axis-signups"]["domain_min"], layout["axes"]["axis-signups"]["domain_max"]), (0, 240))

    def test_serialized_series_points_ticks_area_and_arrow_free_axes(self):
        svg = "<svg>" + render_line_chart(self.plan) + "</svg>"
        self.assertEqual(validate_line_chart_svg(svg), {"series": 3, "points": 24, "axes": 2, "ticks": 6, "focus_areas": 1})
        for axis in re.findall(r'<line class="lc-axis"[^>]+>', svg):
            self.assertNotIn("marker-end", axis)

    def test_non_color_redundancy_is_explicit(self):
        svg = render_line_chart(self.plan)
        self.assertIn('data-line-style="solid"', svg)
        self.assertIn('data-line-style="long-dash"', svg)
        self.assertIn('data-line-style="dot-dash"', svg)
        self.assertIn('data-marker-shape="circle"', svg)
        self.assertIn('data-marker-shape="square"', svg)
        self.assertIn('data-marker-shape="diamond"', svg)

    def test_all_24_values_appear_in_alternative_table(self):
        table = line_chart_table(self.plan)
        self.assertEqual(table.count("<tr>"), 25)
        for series_id in EXPECTED_SERIES:
            self.assertEqual(table.count(f"<td>{series_id}</td>"), 8)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-line-chart")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 980"', svg)
            validate_line_chart_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_nonzero_baseline_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["axes"][1]["domain_min"] = 20
        with self.assertRaises(ValueError):
            layout_line_chart(adapt_visual(fixture))

    def test_missing_value_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][1]["data"][2]["value"] = None
        fixture["series"][1]["data"][2]["missing"] = True
        with self.assertRaises(ValueError):
            layout_line_chart(adapt_visual(fixture))

    def test_week_order_and_focal_target_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][2]["data"][0]["domain"] = "Tuần 2"
        with self.assertRaises(ValueError):
            layout_line_chart(adapt_visual(fixture))
        fixture = copy.deepcopy(self.fixture)
        fixture["annotations"][0]["target_ids"] = ["series-direct-growth"]
        with self.assertRaises(ValueError):
            layout_line_chart(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
