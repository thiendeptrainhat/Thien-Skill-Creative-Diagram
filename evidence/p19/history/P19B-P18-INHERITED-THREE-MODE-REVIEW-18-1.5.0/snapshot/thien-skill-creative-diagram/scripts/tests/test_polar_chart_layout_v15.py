"""Focused D-098 tests for the eight-window radial-spoke polar chart."""
import copy
import math
import re
import unittest
import xml.etree.ElementTree as ET

from gallery_renderer_v15 import MODES, render_gallery_html
from diagram_core import CoreError
from polar_chart_layout_v15 import (
    EXPECTED_DOMAINS, EXPECTED_TICKS, layout_polar_chart, polar_chart_table,
    render_polar_chart, validate_polar_chart_svg,
)
from polar_chart_review18_fixture import polar_chart_fixture
from visual_adapters_v15 import adapt_visual


class DetailedPolarChartTests(unittest.TestCase):
    def setUp(self):
        self.fixture = polar_chart_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_series_windows_axes_ticks_and_peak(self):
        layout = layout_polar_chart(self.plan)
        self.assertEqual(tuple(point["domain"] for point in layout["points"]), EXPECTED_DOMAINS)
        self.assertEqual(layout["ticks"], EXPECTED_TICKS)
        self.assertEqual(set(layout["axes"]), {"axis-utc-window", "axis-normalized-demand"})
        self.assertEqual([point["id"] for point in layout["points"] if point["state"] == "peak"], ["request-12-15"])

    def test_serialized_spokes_endpoints_rings_and_arrow_free_geometry(self):
        svg = "<svg>" + render_polar_chart(self.plan) + "</svg>"
        self.assertEqual(validate_polar_chart_svg(svg), {"series": 1, "spokes": 8, "endpoints": 8, "rings": 5, "peak": 1, "axes": 2})
        self.assertNotIn("marker-end", svg)
        self.assertNotIn('class="polar', svg)

    def test_every_spoke_radius_is_proportional_to_exact_value(self):
        root = ET.fromstring("<svg>" + render_polar_chart(self.plan) + "</svg>")
        for spoke in root.findall(".//*[@data-spoke-id]"):
            dx = float(spoke.attrib["x2"]) - float(spoke.attrib["x1"])
            dy = float(spoke.attrib["y2"]) - float(spoke.attrib["y1"])
            expected = float(spoke.attrib["data-max-radius"]) * float(spoke.attrib["data-value"]) / 100
            self.assertAlmostEqual(math.hypot(dx, dy), expected, places=2)

    def test_peak_has_non_color_redundancy(self):
        svg = render_polar_chart(self.plan)
        self.assertEqual(svg.count('data-state="peak"'), 2)
        self.assertIn('100% · ĐỈNH', svg)
        self.assertIn('ĐỈNH · 12–15 · 100%', svg)

    def test_all_eight_values_appear_in_alternative_table(self):
        table = polar_chart_table(self.plan)
        self.assertEqual(table.count("<tr>"), 9)
        self.assertEqual(table.count("Đỉnh ngày"), 1)
        for domain in EXPECTED_DOMAINS:
            self.assertIn(f"<td>{domain}</td>", table)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-polar-chart")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 1020"', svg)
            validate_polar_chart_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_nonzero_radial_baseline_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["axes"][1]["domain_min"] = 10
        with self.assertRaises(ValueError):
            layout_polar_chart(adapt_visual(fixture))

    def test_missing_or_out_of_range_value_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][0]["data"][1]["value"] = None
        fixture["series"][0]["data"][1]["missing"] = True
        with self.assertRaises((ValueError, CoreError)):
            layout_polar_chart(adapt_visual(fixture))
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][0]["data"][1]["value"] = 101
        with self.assertRaises((ValueError, CoreError)):
            layout_polar_chart(adapt_visual(fixture))

    def test_window_order_duplicate_peak_and_annotation_target_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][0]["data"][0]["domain"] = "03–06"
        with self.assertRaises(ValueError):
            layout_polar_chart(adapt_visual(fixture))
        fixture = copy.deepcopy(self.fixture)
        fixture["series"][0]["data"][0]["value"] = 100
        with self.assertRaises(ValueError):
            layout_polar_chart(adapt_visual(fixture))
        fixture = copy.deepcopy(self.fixture)
        fixture["annotations"][0]["target_ids"] = ["request-09-12"]
        with self.assertRaises(ValueError):
            layout_polar_chart(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
