"""Focused D-108 tests for the centered three-tier tree."""
import re
import unittest

from gallery_renderer_v15 import MODES, render_gallery_html
from tree_layout_v15 import CHILDREN, EXPECTED_EDGE_IDS, EXPECTED_NODE_IDS, layout_tree, render_tree, tree_table, validate_tree_svg
from tree_review26_fixture import tree_fixture
from visual_adapters_v15 import adapt_visual


class DetailedTreeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tree_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_nodes_edges_and_tiers(self):
        layout = layout_tree(self.plan)
        self.assertEqual(tuple(layout["cards"]), EXPECTED_NODE_IDS)
        self.assertEqual(tuple(item["id"] for item in self.plan["semantic_projection"]["edges"]), EXPECTED_EDGE_IDS)
        self.assertEqual({item["level"] for item in layout["cards"].values()}, {0, 1, 2})

    def test_every_parent_is_centered_over_child_span(self):
        layout = layout_tree(self.plan)
        for parent, child_ids in CHILDREN.items():
            centers = [layout["cards"][child]["center_x"] for child in child_ids]
            self.assertEqual(layout["cards"][parent]["center_x"], (min(centers) + max(centers)) / 2)

    def test_connectors_follow_org_chart_grammar(self):
        svg = "<svg>" + render_tree(self.plan) + "</svg>"
        self.assertEqual(validate_tree_svg(svg), {"nodes": 9, "edges": 8, "tiers": 3, "connector_primitives": 14, "centered_parents": 4, "single_child_straight": 1})
        self.assertNotIn("marker-end", svg)
        self.assertIn('data-tree-connector-id="insight-direct-research"', svg)

    def test_thin_stroke_hierarchy_is_locked(self):
        page = render_gallery_html(self.fixture, "neutral-light", "type-tree")
        self.assertIn(".tree-wire{fill:none;stroke:var(--connector);stroke-width:1;", page)
        self.assertIn(".tree-card-shape{fill:var(--surface);stroke:var(--connector);stroke-width:1.2", page)
        self.assertIn(".tree-card.is-root .tree-card-shape{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6", page)
        self.assertIn(".tree-badge-shape{fill:var(--canvas);stroke:var(--border);stroke-width:.9}", page)
        self.assertIn(".tree-rule{stroke:var(--grid);stroke-width:1}", page)

    def test_three_modes_share_exact_geometry(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-tree")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 920"', svg)
            validate_tree_svg(svg)
            geometry = re.findall(r'<(?:rect|line|text)\b[^>]*>', svg)
            geometries.append([re.sub(r'class="[^"]*"', 'class="MODE"', item) for item in geometry])
        self.assertEqual(geometries[0], geometries[1])
        self.assertEqual(geometries[1], geometries[2])

    def test_accessible_table_is_complete(self):
        table = tree_table(self.plan)
        self.assertEqual(table.count("<tr>"), 18)
        for token in ("Năng lực sản phẩm", "parent-product-insight", "leaf-research"):
            self.assertIn(token, table)


if __name__ == "__main__":
    unittest.main()
