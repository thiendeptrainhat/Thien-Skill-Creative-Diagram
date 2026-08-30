"""Focused D-100 tests for the exact three-set Venn diagram."""
import copy
import re
import unittest

from gallery_renderer_v15 import MODES, render_gallery_html
from diagram_core import CoreError
from venn_layout_v15 import (
    CORE_MEMBER, EXPECTED_SET_IDS, layout_venn, render_venn,
    validate_venn_svg, venn_table,
)
from venn_review20_fixture import venn_fixture
from visual_adapters_v15 import adapt_visual


class DetailedVennTests(unittest.TestCase):
    def setUp(self):
        self.fixture = venn_fixture()
        self.plan = adapt_visual(self.fixture)

    def test_exact_sets_membership_and_balanced_geometry(self):
        layout = layout_venn(self.plan)
        self.assertEqual(tuple(item["id"] for item in layout["circles"]), EXPECTED_SET_IDS)
        self.assertTrue(all(CORE_MEMBER in item["member_ids"] for item in layout["circles"]))
        self.assertEqual(layout["circles"][1]["cy"], layout["circles"][2]["cy"])
        self.assertEqual(layout["circles"][1]["cx"] + layout["circles"][2]["cx"], 2 * layout["circles"][0]["cx"])

    def test_serialized_sets_use_exact_nested_clip_intersection(self):
        svg = "<svg>" + render_venn(self.plan) + "</svg>"
        self.assertEqual(validate_venn_svg(svg), {"sets": 3, "members": 4, "triple_intersections": 1, "clip_paths": 2, "direct_labels": 4})
        self.assertEqual(svg.count("clip-path="), 2)
        self.assertEqual(svg.count('data-region-id="triple-intersection"'), 1)

    def test_direct_labels_and_non_color_core_redundancy(self):
        svg = render_venn(self.plan)
        for label in ("Đáng mong muốn", "Khả thi", "Bền vững", "Sẵn sàng triển khai", "ĐIỂM CÂN BẰNG"):
            self.assertIn(label, svg)
        self.assertIn('data-member-id="member-ready"', svg)

    def test_alternative_table_is_exact(self):
        table = venn_table(self.plan)
        self.assertEqual(table.count("<tr>"), 5)
        self.assertEqual(table.count("Giao ba tập · điểm cân bằng"), 1)
        for set_label in ("Đáng mong muốn", "Khả thi", "Bền vững"):
            self.assertIn(set_label, table)

    def test_three_modes_share_exact_geometry(self):
        values = []
        for mode in MODES:
            page = render_gallery_html(self.fixture, mode, "type-venn")
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            self.assertIn('viewBox="0 0 2000 1040"', svg)
            validate_venn_svg(svg)
            values.append(svg.replace(mode, "MODE"))
        self.assertEqual(len(set(values)), 1)

    def test_missing_set_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["groups"].pop()
        with self.assertRaises((ValueError, CoreError)):
            layout_venn(adapt_visual(fixture))

    def test_missing_core_membership_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["groups"][1]["member_ids"].remove(CORE_MEMBER)
        with self.assertRaises(ValueError):
            layout_venn(adapt_visual(fixture))

    def test_duplicate_exclusive_membership_rejected(self):
        fixture = copy.deepcopy(self.fixture)
        fixture["groups"][1]["member_ids"][0] = "member-desirable"
        with self.assertRaises(ValueError):
            layout_venn(adapt_visual(fixture))


if __name__ == "__main__":
    unittest.main()
