import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "thien-skill-creative-diagram/scripts"
for path in (SCRIPT_DIR, SCRIPT_DIR / "tests", ROOT / "evidence/p19/source"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from gallery_renderer_v15 import MODES, render_gallery_html
from layer_stack_layout_v15 import (
    LAYER_ORDER, layer_stack_css, layer_stack_table, layout_layer_stack,
    render_layer_stack, validate_layer_stack_svg,
)
from layer_stack_review44_fixture import layer_stack_fixture
from visual_adapters_v15 import adapt_visual


class LayerStackLayoutV15Test(unittest.TestCase):
    def setUp(self):
        self.ir = layer_stack_fixture()
        self.plan = adapt_visual(self.ir)

    def test_detailed_inventory_and_ownership(self):
        layout = layout_layer_stack(self.plan)
        self.assertEqual(list(layout["rows"]), list(LAYER_ORDER))
        self.assertEqual(len(layout["module_owner"]), 23)
        self.assertEqual(len(layout["domain_boxes"]), 2)
        self.assertEqual(len(layout["connectors"]), 4)
        self.assertEqual(sum(row["focal"] for row in layout["rows"].values()), 1)

    def test_modules_and_domains_stay_inside_owner(self):
        layout = layout_layer_stack(self.plan)
        for layer_id, row in layout["rows"].items():
            x, y, width, height = row["box"]
            for module_id, (mx, my, mw, mh) in row["module_boxes"].items():
                self.assertGreaterEqual(mx, x + 16, module_id)
                self.assertGreaterEqual(my, y + 16, module_id)
                self.assertLessEqual(mx + mw, x + width - 16, module_id)
                self.assertLessEqual(my + mh, y + height - 16, module_id)

    def test_serialized_contract_and_thin_strokes(self):
        svg = "<svg>" + render_layer_stack(self.plan) + "</svg>"
        self.assertEqual(validate_layer_stack_svg(svg), {
            "layers": 5, "modules": 23, "domains": 2, "dependencies": 4,
            "focal_layers": 1, "abstraction_axes": 1,
        })
        css = layer_stack_css({})
        for weight in ("stroke-width:1", "stroke-width:1.2", "stroke-width:1.6"):
            self.assertIn(weight, css)
        self.assertEqual(layer_stack_table(self.plan).count("<tr>"), 24)

    def test_three_modes_share_geometry_and_template(self):
        geometries = []
        for mode in MODES:
            page = render_gallery_html(self.ir, mode, "type-layer-stack")
            self.assertIn('data-layer-stack-contract="D-124-five-layer-modular-split"', page)
            self.assertIn('data-template-contract="p18r6-review17-preserved"', page)
            self.assertIn('data-module-count="23"', page)
            svg = re.search(r"<svg\b.*?</svg>", page, re.S).group()
            geometries.append(re.findall(r'<(?:rect|line|path|circle|polygon|text)\b[^>]*>', svg))
        self.assertEqual(geometries[0], geometries[1])
        self.assertEqual(geometries[1], geometries[2])


if __name__ == "__main__":
    unittest.main()
