"""Focused D-097 tests for the detailed medallion lifecycle."""

from __future__ import annotations

import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from medallion_layout_v15 import (
    ANNOTATION_ORDER, ARCHIVE_NODE, EDGE_ORDER, FOCAL_NODE, LANE_ORDER,
    NODE_ORDER, layout_medallion, medallion_table, render_medallion,
    validate_medallion_svg,
)
from medallion_review17_fixture import medallion_fixture
from visual_adapters_v15 import adapt_visual


class MedallionLayoutV15Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = medallion_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_five_stage_lifecycle_and_order(self):
        layout = layout_medallion(self.plan)
        self.assertEqual(list(layout["stages"]), list(NODE_ORDER))
        self.assertEqual([layout["stages"][node]["lane_id"] for node in NODE_ORDER], list(LANE_ORDER))
        self.assertEqual([item["id"] for item in layout["promotions"]], list(EDGE_ORDER))
        self.assertEqual(list(layout["paths"]), list(ANNOTATION_ORDER))

    def test_stage_cards_are_equal_non_overlapping_and_inside_viewbox(self):
        layout = layout_medallion(self.plan)
        boxes = [layout["stages"][node]["box"] for node in NODE_ORDER]
        self.assertEqual({box[1] for box in boxes}, {170})
        self.assertEqual({box[2:] for box in boxes}, {(350, 650)})
        self.assertTrue(all(boxes[index][0] + boxes[index][2] < boxes[index + 1][0] for index in range(4)))
        self.assertLessEqual(boxes[-1][0] + boxes[-1][2], layout["width"])

    def test_three_modes_preserve_exact_geometry(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-medallion")
            svg = page[page.index("<svg "):page.index("</svg>") + 6]
            self.assertEqual(validate_medallion_svg(svg), {
                "stages": 5, "promotions": 4, "focal_stages": 1,
                "archive_stages": 1, "processing_paths": 2,
            })
            geometries.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometries)), 1)

    def test_focal_and_archive_states_have_non_color_redundancy(self):
        svg = "<svg>" + render_medallion(self.plan) + "</svg>"
        self.assertIn(f'data-stage-id="{FOCAL_NODE}"', svg)
        self.assertIn(f'data-stage-id="{ARCHIVE_NODE}"', svg)
        self.assertIn("TRỌNG TÂM", svg)
        self.assertIn("LƯU TRỮ", svg)
        self.assertIn('class="md-card archive"', svg)

    def test_promotions_are_single_continuous_directed_paths(self):
        svg = "<svg>" + render_medallion(self.plan) + "</svg>"
        self.assertEqual(svg.count('data-transition-id="'), 4)
        self.assertEqual(svg.count('<path class="md-transition'), 4)
        self.assertEqual(svg.count('marker-end="url(#md-arrow'), 4)
        for label in ("ẨN ĐỊNH DANH", "LÀM SẠCH + LIÊN KẾT", "TỔNG HỢP", "LƯU TRỮ VÒNG ĐỜI"):
            self.assertIn(label, svg)

    def test_original_detailed_material_is_visible(self):
        svg = render_medallion(self.plan)
        for text in ("landing-commerce", "privacy-commerce", "staging-commerce", "mart-commerce", "archive-commerce", "Công cụ", "Định dạng", "Chủ trì", "VÍ DỤ THƯƠNG MẠI"):
            self.assertIn(text, svg)

    def test_alternative_table_has_exact_stage_inventory(self):
        table = medallion_table(self.plan)
        self.assertEqual(table.count("<tr>"), 6)
        self.assertIn(FOCAL_NODE, table)
        self.assertIn(ARCHIVE_NODE, table)
        self.assertIn("doanh thu theo kênh", table)

    def test_mutations_fail_closed(self):
        wrong = medallion_fixture()
        wrong["lanes"][0]["order"] = 2
        with self.assertRaises(CoreError):
            layout_medallion(adapt_visual(wrong))
        wrong = medallion_fixture()
        wrong["nodes"][0]["state"] = "focal"
        with self.assertRaises(ValueError):
            layout_medallion(adapt_visual(wrong))


if __name__ == "__main__":
    unittest.main()
