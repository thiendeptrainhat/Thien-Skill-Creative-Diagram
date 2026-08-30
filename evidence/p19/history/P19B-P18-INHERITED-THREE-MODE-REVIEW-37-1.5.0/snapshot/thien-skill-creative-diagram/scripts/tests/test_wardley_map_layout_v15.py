"""Focused D-099 tests for the detailed Wardley map."""
import copy
import re
import unittest
import xml.etree.ElementTree as ET

from gallery_renderer_v15 import MODES, render_gallery_html
from diagram_core import CoreError
from wardley_map_layout_v15 import (
    EXPECTED_COMPONENT_IDS,
    EXPECTED_DEPENDENCY_IDS,
    FOCAL_COMPONENT,
    layout_wardley_map,
    render_wardley_map,
    validate_wardley_map_svg,
    wardley_map_table,
)
from wardley_map_review19_fixture import wardley_map_fixture
from visual_adapters_v15 import adapt_visual


class DetailedWardleyMapTests(unittest.TestCase):
    def setUp(self):
        self.fixture = wardley_map_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_components_dependencies_axes_and_evolving_target(self):
        layout = layout_wardley_map(self.plan)
        self.assertEqual(tuple(item["id"] for item in layout["components"]), EXPECTED_COMPONENT_IDS)
        self.assertEqual(tuple(item["id"] for item in layout["dependencies"]), EXPECTED_DEPENDENCY_IDS)
        self.assertEqual(set(layout["axes"]), {"wardley-evolution", "wardley-value"})
        self.assertEqual([item["id"] for item in layout["components"] if item["state"] == "evolving"], [FOCAL_COMPONENT])

    def test_serialized_map_has_expected_geometry_and_arrow_policy(self):
        svg = "<svg>" + render_wardley_map(self.plan) + "</svg>"
        self.assertEqual(validate_wardley_map_svg(svg), {"components": 8, "dependencies": 9, "axes": 2, "boundaries": 3, "evolving": 1})
        root = ET.fromstring(svg)
        self.assertTrue(all("marker-end" not in item.attrib for item in root.findall(".//*[@data-dependency-id]")))
        self.assertTrue(all("marker-end" not in item.attrib for item in root.findall(".//*[@data-axis-id]")))

    def test_positions_are_derived_from_normalized_coordinates(self):
        layout = layout_wardley_map(self.plan)
        plot = layout["plot"]
        for item in layout["components"]:
            expected_x = plot["left"] + item["evolution"] * (plot["right"] - plot["left"])
            expected_y = plot["bottom"] - item["value_chain_position"] * (plot["bottom"] - plot["top"])
            self.assertAlmostEqual(item["x"], expected_x, places=6)
            self.assertAlmostEqual(item["y"], expected_y, places=6)

    def test_evolving_signal_has_non_color_redundancy(self):
        svg = render_wardley_map(self.plan)
        self.assertEqual(svg.count('data-state="evolving"'), 1)
        self.assertEqual(svg.count('data-evolution-signal="true"'), 1)
        self.assertIn("ĐANG TIẾN HÓA", svg)
        self.assertIn('stroke-dasharray:11 9', __import__("wardley_map_layout_v15").wardley_map_css({}))

    def test_alternative_tables_are_exact(self):
        table = wardley_map_table(self.plan)
        self.assertEqual(table.count("<tr>"), 18)
        self.assertEqual(table.count("<table>"), 1)
        for item_id in EXPECTED_COMPONENT_IDS + EXPECTED_DEPENDENCY_IDS:
            self.assertIn(item_id, table)

    def test_three_modes_share_exact_geometry(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-wardley-map")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 980"', svg)
            validate_wardley_map_svg(svg)
            geometries.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometries)), 1)

    def test_out_of_range_component_position_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"][0]["strategy"]["evolution"] = 1.1
        with self.assertRaises((ValueError, CoreError)):
            layout_wardley_map(adapt_visual(fixture))

    def test_missing_dependency_or_wrong_kind_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["edges"].pop()
        with self.assertRaises((ValueError, CoreError)):
            layout_wardley_map(adapt_visual(fixture))
        fixture = copy.deepcopy(self.fixture)
        fixture["edges"][0]["kind"] = "flow"
        with self.assertRaises((ValueError, CoreError)):
            layout_wardley_map(adapt_visual(fixture))

    def test_annotation_target_rejected_when_not_focal_component(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["annotations"][0]["target_ids"] = ["component-chat"]
        with self.assertRaises(ValueError):
            layout_wardley_map(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
