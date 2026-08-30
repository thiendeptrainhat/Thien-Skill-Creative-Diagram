"""Focused D-090 tests for the detailed ER data model."""
import copy
import re
import unittest

from diagram_core import CoreError
from er_data_model_layout_v15 import (
    EXPECTED_ENTITIES, EXPECTED_RELATIONSHIPS, er_data_model_table,
    layout_er_data_model, render_er_data_model, validate_er_data_model_svg,
)
from er_data_model_review10_fixture import er_data_model_fixture
from gallery_renderer_v15 import MODES, render_gallery_html
from visual_adapters_v15 import adapt_visual


class DetailedErDataModelTests(unittest.TestCase):
    def setUp(self):
        self.fixture = er_data_model_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_entities_members_relations(self):
        layout = layout_er_data_model(self.plan)
        self.assertEqual(set(layout["entities"]), set(EXPECTED_ENTITIES))
        self.assertEqual(set(layout["relationships"]), set(EXPECTED_RELATIONSHIPS))
        self.assertEqual(sum(len(item["members"]) for item in layout["entities"].values()), 19)

    def test_serialized_binding_and_cardinality(self):
        svg = "<svg>" + render_er_data_model(self.plan) + "</svg>"
        self.assertEqual(validate_er_data_model_svg(svg), {"entities": 4, "members": 19, "relationships": 3, "aggregate": 1, "join": 1})
        self.assertEqual(svg.count('data-source-multiplicity="1"'), 3)
        self.assertEqual(svg.count('data-target-multiplicity="N"'), 3)
        self.assertEqual(svg.count('data-label-placement="inline"'), 6)
        self.assertEqual(svg.count('data-er-cardinality-knockout='), 6)
        self.assertEqual(svg.count('data-fill-role="canvas"'), 6)

    def test_cardinalities_match_p18_inline_endpoint_contract(self):
        svg = "<svg>" + render_er_data_model(self.plan) + "</svg>"
        self.assertIn('data-er-cardinality="relation-author-writes-article:source"', svg)
        self.assertIn('data-axis-center="425.00"', svg)
        self.assertIn('data-er-cardinality="relation-tag-used-by:target"', svg)
        self.assertIn('data-axis="vertical"', svg)

    def test_alternative_table_covers_fields_and_relations(self):
        table = er_data_model_table(self.plan)
        self.assertEqual(table.count("<tr>"), 23)
        for token in ("ArticleTag", "author_id", "primary-key", "foreign-key", "relation-author-writes-article"):
            self.assertIn(token, table)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-er-data-model")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 940"', svg)
            validate_er_data_model_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_missing_field_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"][1]["members"].pop()
        with self.assertRaises((CoreError, ValueError)):
            layout_er_data_model(adapt_visual(fixture))

    def test_wrong_cardinality_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["edges"][0]["kind"] = "many-to-many"
        with self.assertRaises(ValueError):
            layout_er_data_model(adapt_visual(fixture))

    def test_join_role_rejected_when_lost(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["nodes"][3]["role"] = "entity"
        with self.assertRaises(ValueError):
            layout_er_data_model(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
