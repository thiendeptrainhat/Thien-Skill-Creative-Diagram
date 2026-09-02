"""Focused D-104 tests for the detailed UML class renderer."""
import copy
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
SOURCE = ROOT / "evidence/p19/source"
for path in (SCRIPT_DIR, SCRIPT_DIR / "tests", SOURCE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from diagram_core import CoreError  # noqa: E402
from gallery_renderer_v15 import MODES, render_gallery_html  # noqa: E402
from uml_class_layout_v15 import (
    EXPECTED_CONTAINERS, EXPECTED_RELATIONSHIPS, INTERFACE_PORTS, LEGEND_KINDS,
    layout_uml_class, render_uml_class, uml_class_table,
    validate_uml_class_svg,
)  # noqa: E402
from uml_class_review24_fixture import uml_class_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


class DetailedUmlClassTests(unittest.TestCase):
    def setUp(self):
        self.fixture = uml_class_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_containers_members_relations(self):
        layout = layout_uml_class(self.plan)
        self.assertEqual(set(layout["containers"]), set(EXPECTED_CONTAINERS))
        self.assertEqual(set(layout["relationships"]), set(EXPECTED_RELATIONSHIPS))
        self.assertEqual(sum(len(item["members"]) for item in layout["containers"].values()), 17)

    def test_serialized_relationship_semantics(self):
        svg = "<svg>" + render_uml_class(self.plan) + "</svg>"
        self.assertEqual(validate_uml_class_svg(svg), {"containers": 7, "members": 17, "relationships": 5, "legend_kinds": 6, "cardinalities": 4})
        self.assertEqual(svg.count('data-relation-kind="realization"'), 2)
        self.assertIn('marker-start="url(#uml-filled-diamond)"', svg)
        self.assertIn('data-cardinality-value="1..*"', svg)

    def test_all_relationships_are_single_continuous_paths(self):
        svg = "<svg>" + render_uml_class(self.plan) + "</svg>"
        for relation_id in EXPECTED_RELATIONSHIPS:
            match = re.search(rf'data-uml-relation-id="{relation_id}"[^>]*\sd="([^"]+)"', svg)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(1).count("M"), 1)
        self.assertIn("Q305 1150 325 1150", svg)
        self.assertIn("Q1505 1150 1505 1130", svg)

    def test_ports_are_centered_even_and_straight_first(self):
        layout = layout_uml_class(self.plan)
        self.assertEqual(INTERFACE_PORTS, (1040, 1400))
        self.assertEqual(layout["relationships"]["relation-service-uses-option"]["path"], "M620 152.5 H680")
        self.assertEqual(layout["relationships"]["relation-wallet-realizes-option"]["path"], "M1040 425 V255")
        self.assertEqual(layout["relationships"]["relation-wire-realizes-option"]["path"], "M1400 425 V255")
        svg = render_uml_class(self.plan)
        self.assertEqual(svg.count('data-route-priority="straight"'), 4)
        self.assertEqual(svg.count('data-route-priority="orthogonal-required"'), 1)
        self.assertIn('data-route-exception="avoid-domain-cards"', svg)

    def test_legend_and_alternative_table_are_complete(self):
        svg = render_uml_class(self.plan)
        table = uml_class_table(self.plan)
        for kind in LEGEND_KINDS:
            self.assertIn(f'data-uml-legend-kind="{kind}"', svg)
        self.assertEqual(table.count("<tr>"), 23)
        for token in ("PaymentOption", "BillingService", "composition", "0..* → 1"):
            self.assertIn(token, table)

    def test_three_modes_share_exact_geometry(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-uml-class")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 1840 1320"', svg)
            validate_uml_class_svg(svg)
            geometry = re.findall(r'<(?:rect|path|line|text)\b[^>]*>', svg)
            geometry = [re.sub(r'class="[^"]*"', 'class="MODE"', item) for item in geometry]
            geometries.append(geometry)
        self.assertEqual(geometries[0], geometries[1])
        self.assertEqual(geometries[1], geometries[2])

    def test_wrong_relation_kind_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["edges"][3]["relation_kind"] = "aggregation"
        fixture["edges"][3]["kind"] = "aggregation"
        with self.assertRaises((CoreError, ValueError)):
            layout_uml_class(adapt_visual(fixture))

    def test_missing_member_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"][2]["members"].pop()
        with self.assertRaises((CoreError, ValueError)):
            layout_uml_class(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
