"""Focused D-101 tests for the exact-area continent Treemap."""
import copy
import re
import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from treemap_layout_v15 import (
    EXPECTED_LEAF_IDS, FOCAL_ID, SMALL_ID, is_detailed_treemap,
    layout_treemap, render_treemap, treemap_table, validate_treemap_svg,
)
from treemap_review21_fixture import treemap_fixture
from visual_adapters_v15 import adapt_visual


class DetailedTreemapTests(unittest.TestCase):
    def setUp(self):
        self.fixture = treemap_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_material_and_detection(self):
        self.assertTrue(is_detailed_treemap(self.plan))
        self.assertEqual(tuple(item["id"] for item in layout_treemap(self.plan)["tiles"]), EXPECTED_LEAF_IDS)

    def test_area_is_exactly_proportional_to_value(self):
        layout = layout_treemap(self.plan)
        canvas_area = layout["chart"]["width"] * layout["chart"]["height"]
        for tile in layout["tiles"]:
            self.assertAlmostEqual(tile["width"] * tile["height"] / canvas_area, tile["share"], places=9)

    def test_focal_and_small_tile_have_redundant_states(self):
        layout = layout_treemap(self.plan)
        self.assertEqual([item["id"] for item in layout["tiles"] if item["focal"]], [FOCAL_ID])
        self.assertEqual([item["id"] for item in layout["tiles"] if item["compact"]], [SMALL_ID])
        svg = render_treemap(self.plan)
        self.assertIn('data-small-tile-label="continent-oceania"', svg)
        self.assertIn("Châu Á · tỷ trọng tiêu điểm", svg)

    def test_serialized_geometry_validates(self):
        svg = "<svg>" + render_treemap(self.plan) + "</svg>"
        self.assertEqual(validate_treemap_svg(svg), {"tiles": 6, "exact_area_encoding": 6, "direct_labels": 5, "compact_labels": 1, "focal_tiles": 1})

    def test_accessible_table_is_exact(self):
        table = treemap_table(self.plan)
        self.assertEqual(table.count("<tr>"), 7)
        for label in ("Châu Á", "Châu Phi", "Châu Âu", "Bắc Mỹ", "Nam Mỹ", "Châu Đại Dương"):
            self.assertIn(label, table)

    def test_three_modes_share_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-treemap")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000.0 1040.0"', svg)
            validate_treemap_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_total_mismatch_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["groups"][1]["declared_total"] -= 1
        with self.assertRaises((ValueError, CoreError)):
            layout_treemap(adapt_visual(fixture))

    def test_missing_leaf_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"].pop()
        fixture["groups"][1]["member_ids"].pop()
        fixture["accessibility"]["reading_order"].remove("continent-oceania")
        fixture["groups"][0]["declared_total"] -= 50
        fixture["groups"][1]["declared_total"] -= 50
        with self.assertRaises((ValueError, CoreError)):
            layout_treemap(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
