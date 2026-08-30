"""Focused D-094 tests for the detailed Kanban board."""
from __future__ import annotations

import copy
import re
import unittest

from diagram_core import CoreError
from gallery_renderer_v15 import MODES, render_gallery_html
from kanban_layout_v15 import (
    COLUMN_ORDER, NODE_ORDER, kanban_table, layout_kanban,
    render_kanban, validate_kanban_svg,
)
from kanban_review14_fixture import kanban_fixture
from visual_adapters_v15 import adapt_visual


class DetailedKanbanTests(unittest.TestCase):
    def setUp(self):
        self.fixture = kanban_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_board_material(self):
        layout = layout_kanban(self.plan)
        self.assertEqual(list(layout["columns"]), list(COLUMN_ORDER))
        self.assertEqual(list(layout["items"]), list(NODE_ORDER))
        self.assertEqual([column["count"] for column in layout["columns"].values()], [3, 4, 2, 2])

    def test_wip_and_state_semantics(self):
        layout = layout_kanban(self.plan)
        self.assertEqual(sum(column["over_limit"] for column in layout["columns"].values()), 1)
        self.assertEqual(layout["columns"]["column-progress"]["counter"], "4/3")
        states = [item["state"] for item in layout["items"].values()]
        self.assertEqual(states.count("blocked"), 1)
        self.assertEqual(states.count("waiting-external"), 1)
        self.assertEqual(states.count("done"), 2)

    def test_containment_and_unique_ownership(self):
        layout = layout_kanban(self.plan)
        member_ids = [item_id for column in layout["columns"].values() for item_id in column["member_ids"]]
        self.assertEqual(member_ids, list(NODE_ORDER))
        self.assertEqual(len(member_ids), len(set(member_ids)))

    def test_serialized_binding_and_three_mode_geometry(self):
        geometry = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-kanban")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 900"', svg)
            self.assertEqual(validate_kanban_svg(svg), {
                "columns": 4, "items": 11, "wip_breaches": 1,
                "blocked": 1, "waiting_external": 1, "done": 2,
            })
            geometry.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(geometry)), 1)

    def test_render_has_redundant_non_color_state_encoding(self):
        svg = "<svg>" + render_kanban(self.plan) + "</svg>"
        self.assertEqual(validate_kanban_svg(svg)["items"], 11)
        self.assertIn('class="kb-card blocked"', svg)
        self.assertIn('class="kb-card waiting"', svg)
        self.assertIn('class="kb-card done"', svg)
        self.assertIn('class="kb-counter over"', svg)
        self.assertIn("Bị chặn", svg)
        self.assertIn("Chờ bên ngoài", svg)

    def test_alternative_table_covers_columns_and_items(self):
        table = kanban_table(self.plan)
        self.assertEqual(table.count("<tr>"), 16)
        for token in ("column-progress", "work-data-cluster", "waiting-external", "4/3"):
            self.assertIn(token, table)

    def test_wrong_column_or_blocked_binding_fails_closed(self):
        wrong = copy.deepcopy(self.fixture)
        wrong["nodes"][0]["work"]["column_order"] = 2
        with self.assertRaises((CoreError, ValueError)):
            layout_kanban(adapt_visual(wrong))
        wrong = copy.deepcopy(self.fixture)
        wrong["nodes"][3]["work"]["blocked"] = False
        with self.assertRaises((CoreError, ValueError)):
            layout_kanban(adapt_visual(wrong))

    def test_duplicate_membership_fails_closed(self):
        wrong = copy.deepcopy(self.fixture)
        wrong["groups"][1]["member_ids"][0] = "work-api-limit"
        with self.assertRaises((CoreError, ValueError)):
            layout_kanban(adapt_visual(wrong))


if __name__ == "__main__":
    unittest.main()
