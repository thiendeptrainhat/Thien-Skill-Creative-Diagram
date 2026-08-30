import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "thien-skill-creative-diagram/scripts"), str(ROOT / "thien-skill-creative-diagram/scripts/tests"), str(ROOT / "evidence/p19/source")]

from radar_review34_fixture import radar_fixture
from radar_layout_v15 import layout_radar, radar_table, render_radar, validate_radar_svg
from visual_adapters_v15 import adapt_visual


class RadarLayoutTests(unittest.TestCase):
    def setUp(self):
        self.plan = adapt_visual(radar_fixture())

    def test_exact_shared_domain(self):
        axes = layout_radar(self.plan)["axes"]
        self.assertEqual(len(axes), 5)
        self.assertTrue(all((item["domain_min"], item["domain_max"]) == (0, 10) for item in axes))

    def test_exact_four_profiles_and_twenty_values(self):
        profiles = layout_radar(self.plan)["profiles"]
        self.assertEqual(len(profiles), 4)
        self.assertEqual(sum(len(item["points"]) for item in profiles), 20)

    def test_one_focal_profile(self):
        focal = [item for item in layout_radar(self.plan)["profiles"] if item["focal"]]
        self.assertEqual([item["id"] for item in focal], ["series-internal-platform"])

    def test_non_color_redundancy(self):
        profiles = layout_radar(self.plan)["profiles"]
        self.assertEqual({item["marker"] for item in profiles}, {"circle", "square", "triangle", "diamond"})
        self.assertEqual(len({item["css"] for item in profiles}), 4)

    def test_truthful_radial_mapping(self):
        layout = layout_radar(self.plan)
        first = layout["profiles"][0]["points"][0]
        self.assertEqual(first["value"], 9)
        self.assertAlmostEqual(first["x"], layout["cx"])
        self.assertAlmostEqual(first["y"], layout["cy"] - layout["radius"] * .9)

    def test_serialized_contract(self):
        report = validate_radar_svg(f"<svg>{render_radar(self.plan)}</svg>")
        self.assertEqual(report, {"profiles": 4, "values": 20, "axes": 5, "rings": 5, "markers": 20, "focal": 1})

    def test_table_has_twenty_rows(self):
        self.assertEqual(radar_table(self.plan).count("<tr>"), 21)

    def test_invalid_focal_is_rejected(self):
        broken = adapt_visual(radar_fixture())
        broken["semantic_projection"]["annotations"][0]["target_ids"] = ["series-managed-service"]
        with self.assertRaisesRegex(ValueError, "focal target"):
            layout_radar(broken)


if __name__ == "__main__":
    unittest.main()
