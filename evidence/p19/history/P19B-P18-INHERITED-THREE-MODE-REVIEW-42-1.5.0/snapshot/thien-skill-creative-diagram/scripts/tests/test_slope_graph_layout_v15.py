"""Focused D-121 slope-graph layout tests."""
import unittest

from slope_graph_layout_v15 import (
    is_detailed_slope_graph, layout_slope_graph, render_slope_graph,
    slope_graph_css, slope_graph_table, validate_slope_graph_svg,
)
from slope_graph_review41_fixture import slope_graph_fixture
from visual_adapters_v15 import adapt_visual


class SlopeGraphLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(slope_graph_fixture())

    def test_exact_two_state_rank_and_crossing_contract(self):
        self.assertTrue(is_detailed_slope_graph(self.plan))
        layout = layout_slope_graph(self.plan)
        self.assertEqual(len(layout["series"]), 7)
        self.assertGreater(layout["crossings"], 0)
        self.assertEqual({item["direction"] for item in layout["series"]}, {"up", "down"})
        self.assertEqual({item["rank_left"] for item in layout["series"]}, set(range(1, 8)))
        self.assertEqual({item["rank_right"] for item in layout["series"]}, set(range(1, 8)))

    def test_svg_and_exact_alternative(self):
        svg = f'<svg>{render_slope_graph(self.plan)}</svg>'
        measurement = validate_slope_graph_svg(svg)
        self.assertEqual(measurement["series"], 7)
        self.assertEqual(measurement["endpoints"], 14)
        self.assertEqual(measurement["axes"], 2)
        self.assertEqual(measurement["focal"], 1)
        self.assertEqual(slope_graph_table(self.plan).count("<tr>"), 8)

    def test_all_seven_lines_use_template_defined_color_tokens(self):
        css = slope_graph_css({})
        for undefined in ("--blue", "--green", "--amber", "--plum"):
            self.assertNotIn(f"var({undefined})", css)
        for defined in ("--accent", "--series-1", "--success", "--series-4", "--danger", "--connector", "--muted"):
            self.assertIn(f"var({defined})", css)


if __name__ == "__main__":
    unittest.main()
