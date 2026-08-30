import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
for path in (ROOT / "thien-skill-creative-diagram/scripts", ROOT / "thien-skill-creative-diagram/scripts/tests", ROOT / "evidence/p19/source"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from gallery_renderer_v15 import MODES, render_gallery_html
from state_machine_layout_v15 import layout_state_machine, validate_state_machine_svg
from state_machine_review30_fixture import state_machine_fixture
from visual_adapters_v15 import adapt_visual


class StateMachineLayoutTests(unittest.TestCase):
    def test_exact_geometry_and_routes(self):
        plan = adapt_visual(state_machine_fixture())
        layout = layout_state_machine(plan)
        self.assertEqual((layout["width"], layout["height"]), (2000, 980))
        self.assertEqual(layout["card_boxes"]["state-live"][0] + 170, 1330)
        self.assertEqual(layout["card_boxes"]["state-retired"][0] + 170, 1330)

    def test_three_modes_share_geometry_and_contract(self):
        fixture = state_machine_fixture()
        expected = {"states": 4, "initial_markers": 1, "terminal_markers": 1, "straight_transitions": 5, "return_transitions": 1, "centered_attachments": 12}
        for mode in MODES:
            html = render_gallery_html(fixture, mode, "type-state-machine")
            svg = html[html.index("<svg "):html.index("</svg>") + 6]
            self.assertEqual(validate_state_machine_svg(svg), expected)
            self.assertIn('data-route-exception="return-transition-avoids-forward-lane"', svg)
            self.assertIn('data-attachment-policy="D-105-centered-and-even"', svg)

    def test_accessible_exact_table(self):
        html = render_gallery_html(state_machine_fixture(), "neutral-light", "type-state-machine")
        self.assertIn("transition-revise", html)
        self.assertIn("TRẢ LẠI · CHỈNH SỬA", html)
        self.assertIn("Đang hiệu lực", html)


if __name__ == "__main__":
    unittest.main()
