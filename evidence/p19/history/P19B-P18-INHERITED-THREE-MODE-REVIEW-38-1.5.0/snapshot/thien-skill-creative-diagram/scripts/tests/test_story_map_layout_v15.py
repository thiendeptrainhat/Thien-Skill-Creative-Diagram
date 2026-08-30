import re
import unittest

from gallery_renderer_v15 import MODES, render_gallery_html
from story_map_layout_v15 import (
    NODE_ORDER, RISK_ID, is_detailed_story_map, layout_story_map,
    validate_story_map_svg,
)
from story_map_review29_fixture import story_map_fixture
from visual_adapters_v15 import adapt_visual


class StoryMapLayoutTests(unittest.TestCase):
    def setUp(self):
        self.ir = story_map_fixture()
        self.plan = adapt_visual(self.ir)

    def test_detailed_contract_and_release_membership(self):
        self.assertTrue(is_detailed_story_map(self.plan))
        layout = layout_story_map(self.plan)
        self.assertEqual(set(layout["stories"]), set(NODE_ORDER))
        self.assertEqual({item["release"] for item in layout["stories"].values()}, {"MVP", "R2", "LATER"})
        self.assertTrue(layout["stories"][RISK_ID]["risk"])

    def test_three_modes_share_exact_geometry(self):
        geometries = []
        for mode in MODES:
            html = render_gallery_html(self.ir, mode, "type-story-map")
            svg = re.search(r"<svg\b.*?</svg>", html, re.S).group()
            self.assertEqual(validate_story_map_svg(svg), {
                "activities": 4, "steps": 6, "stories": 9,
                "release_slices": 3, "risk_stories": 1, "release_cut": 1,
            })
            geometries.append(re.findall(r'<(?:rect|line|text)\b[^>]*>', svg))
        self.assertEqual(geometries[0], geometries[1])
        self.assertEqual(geometries[1], geometries[2])

    def test_visual_contract_uses_thin_p18_strokes(self):
        html = render_gallery_html(self.ir, "neutral-light", "type-story-map")
        for token in (
            ".sm-header{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.2}",
            ".sm-story{fill:var(--surface);stroke:var(--connector);stroke-width:1.2}",
            ".sm-cut{stroke:var(--accent);stroke-width:1.6}",
            'data-story-map-contract="D-109-detailed-release-slices"',
            "ĐƯỜNG CẮT MVP",
        ):
            self.assertIn(token, html)


if __name__ == "__main__":
    unittest.main()
