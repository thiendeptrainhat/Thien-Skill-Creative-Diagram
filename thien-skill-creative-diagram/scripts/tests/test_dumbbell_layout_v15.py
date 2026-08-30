"""Focused D-122 dumbbell layout tests."""
import unittest

from dumbbell_layout_v15 import (
    dumbbell_css, dumbbell_table, is_detailed_dumbbell, layout_dumbbell,
    render_dumbbell, validate_dumbbell_svg,
)
from dumbbell_review42_fixture import dumbbell_fixture
from visual_adapters_v15 import adapt_visual


class DumbbellLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(dumbbell_fixture())

    def test_exact_shared_scale_pair_contract(self):
        self.assertTrue(is_detailed_dumbbell(self.plan))
        layout = layout_dumbbell(self.plan)
        self.assertEqual(len(layout["rows"]), 12)
        self.assertEqual(layout["ticks"], (0, 20, 40, 60, 80, 100))
        self.assertEqual(sum(item["focal"] for item in layout["rows"]), 1)
        self.assertTrue(all(item["x_after"] >= item["x_before"] for item in layout["rows"]))

    def test_svg_statistics_and_exact_alternative(self):
        svg = f'<svg>{render_dumbbell(self.plan)}</svg>'
        self.assertEqual(validate_dumbbell_svg(svg), {
            "pairs": 12, "endpoints": 24, "series": 2, "bands": 2,
            "mean_lines": 2, "axes": 1, "ticks": 6, "focal": 1, "delta_labels": 12,
        })
        self.assertEqual(dumbbell_table(self.plan).count("<tr>"), 13)

    def test_only_declared_template_tokens_are_used(self):
        css = dumbbell_css({})
        for token in ("series-1", "accent", "accent-soft", "accent-text", "surface", "border", "grid", "text", "connector", "muted"):
            self.assertIn(f"var(--{token})", css)
        for forbidden in ("--purple", "--teal", "--blue", "--green"):
            self.assertNotIn(f"var({forbidden})", css)


if __name__ == "__main__":
    unittest.main()
