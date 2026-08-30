"""Focused D-123 ridgeline layout tests."""
import unittest

from ridgeline_layout_v15 import (
    is_detailed_ridgeline, layout_ridgeline, render_ridgeline,
    ridgeline_css, ridgeline_table, validate_ridgeline_svg,
)
from ridgeline_review43_fixture import ridgeline_fixture
from visual_adapters_v15 import adapt_visual


class RidgelineLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(ridgeline_fixture())

    def test_shared_domain_and_profile_contract(self):
        self.assertTrue(is_detailed_ridgeline(self.plan))
        layout = layout_ridgeline(self.plan)
        self.assertEqual(len(layout["rows"]), 12)
        self.assertEqual(layout["ticks"], (0, 20, 40, 60, 80, 100, 120))
        self.assertEqual(sum(row["focal"] for row in layout["rows"]), 1)
        self.assertTrue(all(len(row["points"]) == 20 for row in layout["rows"]))

    def test_svg_quantiles_and_exact_alternative(self):
        svg = f'<svg>{render_ridgeline(self.plan)}</svg>'
        metrics = validate_ridgeline_svg(svg)
        self.assertEqual(metrics["ridges"], 12)
        self.assertEqual(metrics["medians"], 12)
        self.assertEqual(metrics["bands"], 36)
        self.assertEqual(metrics["reference_lines"], 1)
        self.assertEqual(metrics["ticks"], 7)
        self.assertEqual(metrics["focal"], 1)
        self.assertGreater(metrics["profile_points"], 180)
        self.assertEqual(ridgeline_table(self.plan).count("<tr>"), 13)

    def test_only_declared_template_tokens_are_used(self):
        css = ridgeline_css({})
        for token in ("series-1", "series-3", "accent", "accent-text", "surface", "border", "grid", "text", "connector", "muted"):
            self.assertIn(f"var(--{token})", css)
        for forbidden in ("--purple", "--teal", "--lime", "--chart-green"):
            self.assertNotIn(f"var({forbidden})", css)


if __name__ == "__main__":
    unittest.main()
