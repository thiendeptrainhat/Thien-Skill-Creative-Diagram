"""Focused D-103 tests for the uniformly inset exact-area Treemap."""
import copy
import re
import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from treemap_layout_v15 import (
    EXPECTED_LEAF_IDS, FOCAL_ID, SMALL_ID, INTER_TILE_GAP, TILE_INSET, is_detailed_treemap,
    layout_treemap, render_treemap, treemap_css, treemap_table, validate_treemap_svg,
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

    def test_every_tile_has_complete_outline_and_uniform_inset(self):
        layout = layout_treemap(self.plan)
        svg = render_treemap(self.plan)
        css = treemap_css({})
        self.assertNotIn('class="tm-gutter"', svg)
        self.assertEqual(svg.count('data-border-edges="top right bottom left"'), 6)
        self.assertIn('.tm-tile{stroke:var(--connector);stroke-width:2.4', css)
        self.assertIn('.tm-tile.tm-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:3.2}', css)
        for tile in layout["tiles"]:
            self.assertAlmostEqual(tile["draw_x"] - tile["x"], TILE_INSET)
            self.assertAlmostEqual(tile["draw_y"] - tile["y"], TILE_INSET)
            self.assertAlmostEqual(tile["x"] + tile["width"] - tile["draw_x"] - tile["draw_width"], TILE_INSET)
            self.assertAlmostEqual(tile["y"] + tile["height"] - tile["draw_y"] - tile["draw_height"], TILE_INSET)

    def test_shared_boundaries_have_real_uniform_gap(self):
        tiles = {tile["id"]: tile for tile in layout_treemap(self.plan)["tiles"]}
        horizontal_pairs = (
            ("continent-asia", "continent-africa"),
            ("continent-africa", "continent-europe"),
            ("continent-north-america", "continent-south-america"),
            ("continent-south-america", "continent-oceania"),
        )
        for left_id, right_id in horizontal_pairs:
            left, right = tiles[left_id], tiles[right_id]
            self.assertAlmostEqual(right["draw_x"] - left["draw_x"] - left["draw_width"], INTER_TILE_GAP)
        self.assertAlmostEqual(
            tiles["continent-north-america"]["draw_y"]
            - tiles["continent-africa"]["draw_y"]
            - tiles["continent-africa"]["draw_height"],
            INTER_TILE_GAP,
        )

    def test_serialized_geometry_validates(self):
        svg = "<svg>" + render_treemap(self.plan) + "</svg>"
        self.assertEqual(validate_treemap_svg(svg), {"tiles": 6, "exact_area_encoding": 6, "complete_borders": 6, "uniform_insets": 6, "direct_labels": 5, "compact_labels": 1, "focal_tiles": 1})

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
