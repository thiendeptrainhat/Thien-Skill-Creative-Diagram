"""Focused D-095 tests for the Layers presentation variant."""

from __future__ import annotations

from html.parser import HTMLParser
import unittest

from gallery_renderer_v15 import MODES, render_gallery_html
from diagram_core import CoreError
from layers_layout_v15 import (
    FOCAL_NODE, LANE_ORDER, layers_table, layout_layers,
    render_layers, validate_layers_svg,
)
from layers_review15_fixture import layers_fixture
from visual_adapters_v15 import adapt_visual


class _HTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html = {}

    def handle_starttag(self, tag, attrs):
        if tag == "html":
            self.html = dict(attrs)


class LayersLayoutV15Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = layers_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_five_layer_material_and_order(self):
        layout = layout_layers(self.plan)
        self.assertEqual(list(layout["rows"]), list(LANE_ORDER))
        self.assertEqual([layout["rows"][key]["level"] for key in LANE_ORDER], ["L5", "L4", "L3", "L2", "L1"])
        self.assertEqual(sum(row["focal"] for row in layout["rows"].values()), 1)
        self.assertTrue(next(row for row in layout["rows"].values() if row["focal"])["node_id"] == FOCAL_NODE)

    def test_rows_form_one_contiguous_stack(self):
        layout = layout_layers(self.plan)
        boxes = [layout["rows"][key]["box"] for key in LANE_ORDER]
        self.assertTrue(all(boxes[index][1] + boxes[index][3] == boxes[index + 1][1] for index in range(4)))
        self.assertEqual({box[0] for box in boxes}, {245})
        self.assertEqual({box[2] for box in boxes}, {1710})

    def test_three_modes_preserve_geometry(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-layers")
            svg = page[page.index("<svg "):page.index("</svg>") + 6]
            self.assertEqual(validate_layers_svg(svg), {"layers": 5, "focal_layers": 1, "abstraction_axis": 1, "dependencies": 4})
            geometries.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometries)), 1)

    def test_focal_state_has_non_color_redundancy(self):
        svg = "<svg>" + render_layers(self.plan) + "</svg>"
        self.assertIn('data-focal="true"', svg)
        self.assertIn('data-focal-node="layer-orchestration"', svg)
        self.assertIn("TRỌNG TÂM", svg)
        self.assertIn('class="ly-row focal"', svg)

    def test_axis_and_original_vietnamese_content_are_visible(self):
        svg = render_layers(self.plan)
        for text in ("TRỪU TƯỢNG", "NỀN TẢNG", "Điều phối quy trình", "Nền tảng dữ liệu", "Hạ tầng vận hành"):
            self.assertIn(text, svg)

    def test_alternative_table_is_exact(self):
        table = layers_table(self.plan)
        self.assertEqual(table.count("<tr>"), 6)
        self.assertIn("layer-orchestration", table)
        self.assertIn("trọng tâm", table)

    def test_variant_metadata_keeps_frozen_parent(self):
        parser = _HTML()
        parser.feed(render_gallery_html(self.fixture, "neutral-light", "type-layers"))
        self.assertEqual(parser.html["data-diagram-type"], "layer-stack")
        self.assertEqual(parser.html["data-parent-type"], "layer-stack")
        self.assertEqual(parser.html["data-presentation-variant"], "layers")
        self.assertEqual(parser.html["data-silhouette"], "five-band-abstraction-stack")

    def test_mutations_fail_closed(self):
        wrong = layers_fixture()
        wrong["lanes"][0]["order"] = 2
        with self.assertRaises(CoreError):
            layout_layers(adapt_visual(wrong))
        wrong = layers_fixture()
        wrong["nodes"][1]["state"] = "default"
        with self.assertRaises(ValueError):
            layout_layers(adapt_visual(wrong))


if __name__ == "__main__":
    unittest.main()
