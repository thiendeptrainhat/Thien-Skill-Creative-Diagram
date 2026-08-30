"""Focused D-087 tests for the detailed DP integration topology."""
import copy
import re
import unittest
import xml.etree.ElementTree as ET

from diagram_core import CoreError
from dp_integration_layout_v15 import (
    BOUNDARY, EXPECTED_EDGES, EXPECTED_NODES, dp_integration_table,
    layout_dp_integration, render_dp_integration, validate_dp_integration_svg,
)
from dp_integration_review07_fixture import dp_integration_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual


class DetailedDPIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = dp_integration_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_material_and_roles(self):
        layout = layout_dp_integration(self.plan)
        self.assertEqual(set(layout["nodes"]), EXPECTED_NODES)
        self.assertEqual(set(layout["edges"]), EXPECTED_EDGES)
        self.assertEqual(len(layout["nodes"]), 11)
        self.assertEqual(len(layout["edges"]), 11)
        self.assertEqual(layout["group"]["id"], "boundary-data-platform")

    def test_platform_members_inside_and_external_nodes_outside(self):
        layout = layout_dp_integration(self.plan)
        bx, by, bw, bh = BOUNDARY
        members = set(layout["group"]["member_ids"])
        for node_id, node in layout["nodes"].items():
            x, y, w, h = node["box"]
            contained = bx <= x and by <= y and x + w <= bx + bw and y + h <= by + bh
            self.assertEqual(contained, node_id in members)

    def test_serialized_semantic_bindings_and_continuous_paths(self):
        svg = '<svg>' + render_dp_integration(self.plan) + '</svg>'
        result = validate_dp_integration_svg(svg)
        self.assertEqual(result, {"nodes": 11, "edges": 11, "groups": 1, "continuous_routes": 11})
        root = ET.fromstring(svg)
        self.assertEqual(len(root.findall(".//*[@data-dp-node-id]")), 11)
        self.assertEqual(len(root.findall(".//*[@data-dp-edge-id]")), 11)
        self.assertNotIn('class="bridge"', svg)

    def test_all_material_ids_appear_in_alternative_table(self):
        table = dp_integration_table(self.plan)
        for item in self.fixture["nodes"] + self.fixture["edges"] + self.fixture["groups"]:
            self.assertIn(item["id"], table)
        self.assertEqual(table.count("<tr>"), 24)

    def test_three_modes_share_exact_svg_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-dp-integration")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 1800 1040"', svg)
            self.assertIn("NỀN TẢNG DỮ LIỆU", svg)
            self.assertIn("Quan sát tập trung", svg)
            validate_dp_integration_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_endpoint_mutation_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["edges"][0]["target"] = "platform-query"
        with self.assertRaises((CoreError, ValueError)):
            layout_dp_integration(adapt_visual(fixture))

    def test_group_membership_mutation_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["groups"][0]["member_ids"].append("source-crm")
        with self.assertRaises((CoreError, ValueError)):
            layout_dp_integration(adapt_visual(fixture))

    def test_route_mutation_rejected(self):
        svg = '<svg>' + render_dp_integration(self.plan) + '</svg>'
        mutated = svg.replace('M330 185 H360 V275 H560 V345 H610', 'M330 185 M560 345 H610')
        with self.assertRaises(ValueError):
            validate_dp_integration_svg(mutated)


if __name__ == "__main__":
    unittest.main()
