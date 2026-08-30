import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "thien-skill-creative-diagram/scripts"), str(ROOT / "thien-skill-creative-diagram/scripts/tests"), str(ROOT / "evidence/p19/source")]

from scatter_chart_review33_fixture import scatter_chart_fixture
from scatter_chart_layout_v15 import layout_scatter_chart, render_scatter_chart, validate_scatter_chart_svg
from visual_adapters_v15 import adapt_visual


class ScatterChartLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(scatter_chart_fixture())

    def test_exact_domains_and_ticks(self):
        layout = layout_scatter_chart(self.plan)
        self.assertEqual((layout["axes"]["axis-deploys"]["domain_min"], layout["axes"]["axis-deploys"]["domain_max"]), (0, 20))
        self.assertEqual((layout["axes"]["axis-lead-time"]["domain_min"], layout["axes"]["axis-lead-time"]["domain_max"]), (0, 24))
        self.assertEqual(layout["x_ticks"], (0, 4, 8, 12, 16, 20))
        self.assertEqual(layout["y_ticks"], (0, 6, 12, 18, 24))

    def test_exact_twelve_points_and_one_focal(self):
        points = layout_scatter_chart(self.plan)["points"]
        self.assertEqual(len(points), 12)
        self.assertEqual([p["id"] for p in points if p["focal"]], ["team-platform"])

    def test_mapping_is_truthful(self):
        point = next(p for p in layout_scatter_chart(self.plan)["points"] if p["id"] == "team-platform")
        self.assertEqual((point["domain"], point["value"]), (18, 3))
        self.assertAlmostEqual(point["x"], 1762)
        self.assertAlmostEqual(point["y"], 736.25)

    def test_regression_is_exact_and_descending(self):
        layout = layout_scatter_chart(self.plan)
        self.assertAlmostEqual(layout["trend_slope"], -0.9891304347826086)
        self.assertAlmostEqual(layout["trend_intercept"], 20.141304347826086)
        self.assertLess(layout["trend_slope"], 0)

    def test_serialized_contract(self):
        report = validate_scatter_chart_svg(f"<svg>{render_scatter_chart(self.plan)}</svg>")
        self.assertEqual(report, {"points": 12, "focal": 1, "axes": 2, "x_ticks": 6, "y_ticks": 5, "trends": 1})

    def test_axis_lines_have_no_arrowheads(self):
        svg = render_scatter_chart(self.plan)
        self.assertNotIn('class="sc-axis" marker-end=', svg)

    def test_invalid_focal_is_rejected(self):
        broken = adapt_visual(scatter_chart_fixture())
        broken["semantic_projection"]["annotations"][0]["target_ids"] = ["team-01"]
        with self.assertRaisesRegex(ValueError, "focal target"):
            layout_scatter_chart(broken)


if __name__ == "__main__":
    unittest.main()
