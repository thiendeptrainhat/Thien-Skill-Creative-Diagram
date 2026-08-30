"""Focused D-093 tests for the detailed IT current-state landscape."""
from __future__ import annotations

import copy
import re
import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from it_current_state_layout_v15 import (
    EDGE_ORDER, NODE_ORDER, ROUTE_POINTS, it_current_state_table,
    layout_it_current_state, render_it_current_state,
    validate_it_current_state_svg,
)
from it_current_state_review13_fixture import it_current_state_fixture
from visual_adapters_v15 import adapt_visual


class DetailedItCurrentStateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = it_current_state_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_current_state_material(self):
        layout = layout_it_current_state(self.plan)
        self.assertEqual(list(layout["nodes"]), list(NODE_ORDER))
        self.assertEqual(list(layout["edges"]), list(EDGE_ORDER))
        self.assertEqual(len(layout["groups"]), 3)
        self.assertEqual(sum(node["state"] == "bottleneck" for node in layout["nodes"].values()), 2)

    def test_every_node_has_state_and_group_ownership(self):
        layout = layout_it_current_state(self.plan)
        self.assertTrue(all(node["state"] for node in layout["nodes"].values()))
        member_ids = [node_id for group in layout["groups"].values() for node_id in group["member_ids"]]
        self.assertEqual(set(member_ids), set(NODE_ORDER))
        self.assertEqual(len(member_ids), len(set(member_ids)))

    def test_all_routes_are_continuous_and_rounded_by_default(self):
        layout = layout_it_current_state(self.plan)
        for edge_id, edge in layout["edges"].items():
            self.assertEqual(edge["path"].count("M"), 1)
            self.assertEqual(edge["path"].count("Q"), max(0, len(ROUTE_POINTS[edge_id]) - 2))

    def test_straight_override_preserves_vertices_and_endpoints(self):
        layout = layout_it_current_state(self.plan, "straight")
        for edge_id, edge in layout["edges"].items():
            self.assertNotIn("Q", edge["path"])
            self.assertEqual(edge["path"].count("M"), 1)
            self.assertTrue(edge["path"].startswith(f"M{ROUTE_POINTS[edge_id][0][0]} {ROUTE_POINTS[edge_id][0][1]}"))
            self.assertTrue(edge["path"].endswith(f"L{ROUTE_POINTS[edge_id][-1][0]} {ROUTE_POINTS[edge_id][-1][1]}"))

    def test_serialized_binding_and_three_mode_geometry(self):
        geometry = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-it-current-state")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 1040"', svg)
            self.assertEqual(validate_it_current_state_svg(svg), {
                "nodes": 9, "edges": 8, "groups": 3, "edge_labels": 8,
                "continuous_routes": 8, "corner_style": "rounded",
            })
            geometry.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometry)), 1)

    def test_renderer_exposes_rounded_and_straight_contracts(self):
        default_page = render_gallery_html(self.fixture, "neutral-light", "type-it-current-state")
        rounded_page = render_gallery_html(self.fixture, "neutral-light", "type-it-current-state", connector_corner_style="rounded")
        self.assertEqual(default_page, rounded_page)
        straight_page = render_gallery_html(self.fixture, "neutral-light", "type-it-current-state", connector_corner_style="straight")
        straight_svg = re.search(r"<svg\b.*?</svg>", straight_page, re.S).group()
        self.assertEqual(validate_it_current_state_svg(straight_svg)["corner_style"], "straight")

    def test_alternative_table_covers_nodes_edges_and_groups(self):
        table = it_current_state_table(self.plan)
        self.assertEqual(table.count("<tr>"), 21)
        for token in ("processing-shared-drive", "handoff-spreadsheet-portal", "group-dissemination", "bottleneck"):
            self.assertIn(token, table)

    def test_wrong_endpoint_or_missing_state_fails_closed(self):
        wrong = copy.deepcopy(self.fixture)
        wrong["edges"][0]["target"] = "processing-rdbms"
        with self.assertRaises(ValueError):
            layout_it_current_state(adapt_visual(wrong))
        missing = copy.deepcopy(self.fixture)
        missing["nodes"][0].pop("state")
        with self.assertRaises((CoreError, ValueError)):
            layout_it_current_state(adapt_visual(missing))

    def test_direct_render_has_pain_and_external_redundancy(self):
        svg = "<svg>" + render_it_current_state(self.plan) + "</svg>"
        self.assertEqual(validate_it_current_state_svg(svg)["continuous_routes"], 8)
        self.assertEqual(svg.count('class="ics-route pain"'), 3)  # two routes plus legend
        self.assertEqual(svg.count('class="ics-card bottleneck"'), 3)  # two cards plus legend
        self.assertEqual(svg.count('class="ics-card external"'), 3)  # two cards plus legend


if __name__ == "__main__":
    unittest.main()
