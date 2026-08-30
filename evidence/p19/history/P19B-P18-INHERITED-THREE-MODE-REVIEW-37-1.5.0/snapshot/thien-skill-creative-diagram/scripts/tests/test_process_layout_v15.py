import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT / "thien-skill-creative-diagram/scripts"),
    str(ROOT / "thien-skill-creative-diagram/scripts/tests"),
    str(ROOT / "evidence/p19/source"),
]

from process_layout_v15 import (
    EXPECTED_SHAPES,
    layout_process,
    process_css,
    process_table,
    render_process,
    validate_process_svg,
)
from process_review37_fixture import process_fixture
from visual_adapters_v15 import adapt_visual


class ProcessLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(process_fixture())

    def test_exact_shape_taxonomy(self):
        self.assertEqual(layout_process(self.plan)["shape_counts"], EXPECTED_SHAPES)

    def test_exact_node_and_edge_counts(self):
        layout = layout_process(self.plan)
        self.assertEqual((len(layout["nodes"]), len(layout["edges"])), (11, 11))

    def test_every_route_is_straight_and_directed(self):
        rendered = render_process(self.plan)
        self.assertEqual(rendered.count('data-route-kind="straight"'), 11)
        self.assertEqual(rendered.count('marker-end="url(#pr-arrow)"'), 12)  # eleven routes + legend sample
        self.assertNotIn("data-route-exception", rendered)

    def test_multiple_document_inlets_are_even(self):
        layout = layout_process(self.plan)
        target_x = sorted(item["end"][0] for item in layout["edges"] if item["target_anchor"].startswith("top-"))
        self.assertEqual(target_x, [920, 1080])
        self.assertEqual(sum(target_x) / len(target_x), 1000)

    def test_single_connectors_use_center_anchors(self):
        edges = layout_process(self.plan)["edges"]
        for item in edges:
            if item["target_anchor"].startswith("top-"):
                continue
            self.assertIn("center", item["source_anchor"])
            self.assertIn("center", item["target_anchor"])

    def test_document_shapes_have_real_waves_and_layers(self):
        rendered = render_process(self.plan)
        self.assertIn('data-shape-kind="document"', rendered)
        self.assertIn('data-shape-kind="multiple-document"', rendered)
        self.assertEqual(rendered.count('class="pr-layer focal"'), 2)
        self.assertGreaterEqual(rendered.count(" C"), 9)

    def test_strokes_are_thin_and_template_bound(self):
        css = process_css({})
        self.assertIn("stroke-width:1.45", css)
        self.assertIn("stroke-width:1.8", css)
        self.assertIn('data-template-contract="p18r6-review17-preserved"', render_process(self.plan))

    def test_serialized_contract(self):
        report = validate_process_svg(f"<svg>{render_process(self.plan)}</svg>")
        self.assertEqual(report["shape_counts"], EXPECTED_SHAPES)
        self.assertEqual(report["straight_routes"], 11)
        self.assertEqual(report["rounded_orthogonal_exceptions"], 0)

    def test_alternative_tables_are_exact(self):
        table = process_table(self.plan)
        self.assertEqual(table.count("<table>"), 1)
        self.assertEqual(table.count("<tr>"), 23)  # one header + eleven nodes + eleven routes

    def test_invalid_shape_inventory_fails_closed(self):
        broken = copy.deepcopy(self.plan)
        broken["semantic_projection"]["nodes"][3]["role"] = "activity"
        with self.assertRaisesRegex(ValueError, "shape taxonomy"):
            layout_process(broken)


if __name__ == "__main__":
    unittest.main()
