import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
SOURCE = ROOT / "evidence/p19/source"
for path in (SCRIPT_DIR, SCRIPT_DIR / "tests", SOURCE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nested_layout_v15 import (  # noqa: E402
    SCOPE_ORDER,
    layout_nested,
    nested_table,
    render_nested,
    validate_nested_svg,
)
from nested_review45_fixture import nested_fixture  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402


class NestedLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(nested_fixture())
        self.layout = layout_nested(self.plan)

    def test_exact_depth_and_artifact_inventory(self):
        self.assertEqual(tuple(self.layout["scopes"]), SCOPE_ORDER)
        self.assertEqual(len(self.layout["scopes"]), 5)
        self.assertEqual(len(self.layout["nodes"]), 5)
        self.assertEqual([item["order"] for item in self.layout["scopes"].values()], list(range(5)))

    def test_every_inner_scope_is_inset_evenly(self):
        boxes = [self.layout["scopes"][scope_id]["box"] for scope_id in SCOPE_ORDER]
        for parent, child in zip(boxes, boxes[1:]):
            self.assertEqual(child[0] - parent[0], 65)
            self.assertEqual(child[1] - parent[1], 75)
            self.assertEqual((parent[0] + parent[2]) - (child[0] + child[2]), 65)
            self.assertEqual((parent[1] + parent[3]) - (child[1] + child[3]), 75)

    def test_serialized_contract_is_exact(self):
        svg = f'<svg xmlns="http://www.w3.org/2000/svg">{render_nested(self.plan)}</svg>'
        self.assertEqual(
            validate_nested_svg(svg),
            {"scopes": 5, "artifacts": 5, "max_depth": 4, "focal_scopes": 1, "annotation_leaders": 1},
        )
        self.assertIn('data-nested-contract="D-125-five-depth-inheritance"', svg)
        self.assertIn('data-template-contract="p18r6-review17-preserved"', svg)

    def test_alternative_table_has_one_row_per_scope(self):
        self.assertEqual(nested_table(self.plan).count("<tr>"), 6)


if __name__ == "__main__":
    unittest.main()
