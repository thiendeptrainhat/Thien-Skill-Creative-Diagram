"""Focused D-089 tests for the five-by-five permission matrix."""
import copy
import re
import unittest

from dp_security_matrix_layout_v15 import (
    COMPONENT_KEYS, FOCAL_CELL_ID, ROLE_KEYS, dp_security_matrix_table,
    layout_dp_security_matrix, render_dp_security_matrix,
    validate_dp_security_matrix_svg,
)
from dp_security_matrix_review09_fixture import dp_security_matrix_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual


class DetailedSecurityMatrixTests(unittest.TestCase):
    def setUp(self):
        self.fixture = dp_security_matrix_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_rectangular_material_and_focal(self):
        layout = layout_dp_security_matrix(self.plan)
        self.assertEqual(layout["roles"], ROLE_KEYS)
        self.assertEqual(layout["components"], COMPONENT_KEYS)
        self.assertEqual(len(layout["cells"]), 25)
        self.assertEqual([item["id"] for item in layout["cells"] if item["focal"]], [FOCAL_CELL_ID])

    def test_serialized_cells_headers_permissions_and_boundary(self):
        svg = "<svg>" + render_dp_security_matrix(self.plan) + "</svg>"
        self.assertEqual(validate_dp_security_matrix_svg(svg), {"cells": 25, "roles": 5, "components": 5, "focal": 1})
        self.assertIn("Dashboard được chia sẻ", svg)

    def test_alternative_table_has_every_cell(self):
        table = dp_security_matrix_table(self.plan)
        self.assertEqual(table.count("<tr>"), 26)
        for role in ROLE_KEYS:
            self.assertIn(role.rsplit(" · ", 1)[1], table)
        for component in COMPONENT_KEYS:
            self.assertIn(component.rsplit(" · ", 1)[1], table)
        self.assertIn("GRP-PARTNER", table)
        self.assertIn("Dashboard được chia sẻ", table)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-dp-security-matrix")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 820"', svg)
            validate_dp_security_matrix_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_missing_cell_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"].pop()
        with self.assertRaises(Exception):
            layout_dp_security_matrix(adapt_visual(fixture))

    def test_wrong_state_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"][0]["state"] = "deny"
        with self.assertRaises(ValueError):
            layout_dp_security_matrix(adapt_visual(fixture))

    def test_unscoped_partner_boundary_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        cell = next(item for item in fixture["nodes"] if item["id"] == FOCAL_CELL_ID)
        cell["label"] = "Read"
        with self.assertRaises(ValueError):
            layout_dp_security_matrix(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
