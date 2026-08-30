"""Focused D-092 tests for the detailed high-level data-platform overview."""
from __future__ import annotations

import copy
import re
import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from high_level_layout_v15 import (
    EDGE_ORDER, NODE_ORDER, ROUTE_POINTS, high_level_table,
    layout_high_level, orthogonal_path, render_high_level,
    validate_high_level_svg,
)
from high_level_review12_fixture import high_level_fixture
from visual_adapters_v15 import adapt_visual


class DetailedHighLevelTests(unittest.TestCase):
    def setUp(self):
        self.fixture = high_level_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_material_and_default_corner_policy(self):
        layout = layout_high_level(self.plan)
        self.assertEqual(list(layout["nodes"]), list(NODE_ORDER))
        self.assertEqual(list(layout["edges"]), list(EDGE_ORDER))
        self.assertEqual(len(layout["groups"]), 2)
        self.assertEqual(layout["corner_style"], "rounded")

    def test_every_connector_is_one_continuous_path(self):
        for style in ("rounded", "straight"):
            layout = layout_high_level(self.plan, style)
            for edge in layout["edges"].values():
                self.assertTrue(edge["path"].startswith("M"))
                self.assertEqual(edge["path"].count("M"), 1)

    def test_rounded_is_default_and_applies_to_every_bend(self):
        default = layout_high_level(self.plan)
        explicit = layout_high_level(self.plan, "rounded")
        self.assertEqual(default, explicit)
        for edge_id, points in ROUTE_POINTS.items():
            expected_turns = max(0, len(points) - 2)
            self.assertEqual(default["edges"][edge_id]["path"].count("Q"), expected_turns)

    def test_straight_policy_is_explicit_and_still_continuous(self):
        for edge_id, points in ROUTE_POINTS.items():
            path = layout_high_level(self.plan, "straight")["edges"][edge_id]["path"]
            self.assertEqual(path, orthogonal_path(points, "straight"))
            self.assertNotIn("Q", path)
            self.assertEqual(path.count("M"), 1)

    def test_serialized_binding_and_three_mode_geometry(self):
        geometry = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-high-level")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 1040"', svg)
            self.assertEqual(validate_high_level_svg(svg), {
                "nodes": 11, "edges": 13, "groups": 2,
                "continuous_routes": 13, "corner_style": "rounded",
            })
            geometry.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometry)), 1)

    def test_renderer_exposes_both_approved_corner_styles(self):
        for style in ("rounded", "straight"):
            page = render_gallery_html(
                self.fixture, "neutral-light", "type-high-level",
                connector_corner_style=style,
            )
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertEqual(validate_high_level_svg(svg)["corner_style"], style)

    def test_accessible_table_covers_nodes_edges_and_groups(self):
        table = high_level_table(self.plan)
        self.assertEqual(table.count("<tr>"), 27)
        for token in ("source-portal", "flow-store-model", "boundary-platform", "rounded default"):
            self.assertIn(token, table)

    def test_wrong_endpoint_or_missing_group_fails_closed(self):
        wrong_endpoint = copy.deepcopy(self.fixture)
        wrong_endpoint["edges"][0]["target"] = "stage-query"
        with self.assertRaises(ValueError):
            layout_high_level(adapt_visual(wrong_endpoint))

        missing_group = copy.deepcopy(self.fixture)
        missing_group["groups"].pop()
        with self.assertRaises((CoreError, ValueError)):
            layout_high_level(adapt_visual(missing_group))

    def test_direct_render_validates_as_one_continuous_topology(self):
        svg = "<svg>" + render_high_level(self.plan) + "</svg>"
        result = validate_high_level_svg(svg)
        self.assertEqual(result["continuous_routes"], 13)
        self.assertEqual(svg.count('data-hl-edge-id='), 13)


if __name__ == "__main__":
    unittest.main()
