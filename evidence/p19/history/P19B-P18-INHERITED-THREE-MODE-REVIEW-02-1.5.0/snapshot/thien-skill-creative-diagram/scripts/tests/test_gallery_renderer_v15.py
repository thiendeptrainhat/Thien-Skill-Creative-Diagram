"""Focused P-19B tests for three-mode standalone gallery rendering."""

from __future__ import annotations

from html.parser import HTMLParser
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from gallery_renderer_v15 import (
    GalleryRenderError,
    MODES,
    P18_PARENT_CANDIDATE_ID,
    P18_PARENT_MANIFEST_SHA256,
    P18_VISUAL_MODES,
    P19B_CANDIDATE_ID,
    render_gallery_html,
    renderer_inventory,
    _centered_enclosure,
    _orthogonal_path,
    validate_target_geometry,
)
from semantic_fixtures import fixtures, variant_fixtures
from visual_adapters_v15 import P19A_CAPABILITIES


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.html_attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_attrs = values
        if "id" in values:
            self.ids.append(values["id"])


def all_sources() -> list[tuple[str, dict]]:
    values = [(f"type-{key}", value) for key, value in fixtures().items()]
    values.extend((f"cap-{key.lower()}", value) for key, value in variant_fixtures().items())
    return values


class GalleryRendererV15Tests(unittest.TestCase):
    def target_svg(self, kind, mode="neutral-light", **options):
        value = render_gallery_html(fixtures()[kind], mode, f"type-{kind}", **options)
        return value[value.index("<svg "):value.index("</svg>") + 6]

    def test_dp_integration_contained_and_centered_in_all_modes(self):
        for mode in MODES:
            svg = self.target_svg("dp-integration", mode)
            result = validate_target_geometry(svg, "dp-integration")
            self.assertEqual(result["padding_ltrb"], [24, 85, 24, 85])
            self.assertEqual(result["center_error_xy"], [0, 0])
            root = ET.fromstring(svg)
            parent = root.find(".//*[@id='integration-api-zone']")
            self.assertEqual([float(parent.get(k)) for k in ("x", "y", "width", "height")], [466, 190, 308, 290])
            nodes = [e for e in root.iter("rect") if "node" in e.get("class", "").split()]
            self.assertEqual([float(e.get("x")) for e in nodes], [120, 490, 860])
            self.assertIn("API nền tảng", svg)

    def test_enclosure_uses_arbitrary_child_union_not_fixture_offsets(self):
        for children in ([(12, 36, 420, 83)], [(10, 20, 40, 60), (130, 100, 75, 30)]):
            x, y, w, h = _centered_enclosure(children, padding=32, min_height=300)
            left, top = min(c[0] for c in children), min(c[1] for c in children)
            right, bottom = max(c[0]+c[2] for c in children), max(c[1]+c[3] for c in children)
            self.assertEqual(x+w/2, (left+right)/2)
            self.assertEqual(y+h/2, (top+bottom)/2)
            self.assertGreaterEqual(min(left-x, top-y, x+w-right, y+h-bottom), 32)

    def test_enclosure_invalid_geometry_fails_closed(self):
        for boxes in ([], [(0, 0, -1, 4)], [(0, 0, float("nan"), 4)]):
            with self.assertRaises(GalleryRenderError):
                _centered_enclosure(boxes)

    def test_enclosure_mutation_detects_overflow_and_off_center(self):
        svg = self.target_svg("dp-integration")
        for replacement in ('x="470" y="190" width="260"', 'x="465" y="190" width="312"', 'x="466" y="191" width="308"'):
            mutated = svg.replace('x="466" y="190" width="308"', replacement)
            with self.assertRaises(GalleryRenderError):
                validate_target_geometry(mutated, "dp-integration")

    def test_swimlane_continuity_rounded_and_straight_in_all_modes(self):
        for mode in MODES:
            for style in ("rounded", "straight"):
                svg = self.target_svg("swimlane", mode, connector_corner_style=style)
                result = validate_target_geometry(svg, "swimlane")
                path = ET.fromstring(svg).find(".//*[@data-connector-id='swimlane-handoff']")
                route = path.get("d")
                expected = ("M460 265 L620 265 Q650 265 650 295 L650 415 Q650 445 680 445 L740 445"
                            if style == "rounded" else "M460 265 L650 265 L650 445 L740 445")
                self.assertEqual(route, expected)
                self.assertEqual(result["continuous_subpaths"], 1)
                self.assertEqual(result["erase_overlays"], 0)
                self.assertNotIn('class="bridge"', svg)

    def test_swimlane_default_retains_rounded_policy(self):
        self.assertEqual(self.target_svg("swimlane"), self.target_svg("swimlane", connector_corner_style="rounded"))

    def test_orthogonal_path_handles_all_turn_directions_and_short_segments(self):
        for xsign in (-1, 1):
            for ysign in (-1, 1):
                route = _orthogonal_path([(0, 0), (10*xsign, 0), (10*xsign, 10*ysign)])
                self.assertEqual(route.count("M"), 1)
                self.assertIn(f"Q{10*xsign} 0 {10*xsign} {5*ysign}", route)
                self.assertTrue(route.endswith(f"L{10*xsign} {10*ysign}"))
        self.assertEqual(_orthogonal_path([(0,0), (0,20), (10,20)], corner_style="straight"), "M0 0 L0 20 L10 20")

    def test_invalid_route_and_corner_override_fail_closed(self):
        for points in ([(0,0)], [(0,0), (0,0)], [(0,0), (1,1)], [(0,0), (1,0), (0,0)]):
            with self.assertRaises(GalleryRenderError):
                _orthogonal_path(points)
        for kind, style in (("swimlane", "smooth"), ("architecture", "straight")):
            with self.assertRaises(GalleryRenderError):
                self.target_svg(kind, connector_corner_style=style)

    def test_continuity_mutation_detects_erase_overlay_or_second_subpath(self):
        svg = self.target_svg("swimlane")
        mutations = [svg.replace("L620 265", "M620 265"),
                     svg.replace("</svg>", '<path class="bridge" d="M620 265 A30 30 0 0 1 650 295"/></svg>'),
                     svg.replace('class="connector" data-connector-id', 'class="connector" stroke="none" data-connector-id')]
        for mutated in mutations:
            with self.assertRaises(GalleryRenderError):
                validate_target_geometry(mutated, "swimlane")

    def test_renderer_rejects_geometry_regression_before_emitting_html(self):
        with patch("gallery_renderer_v15._centered_enclosure", return_value=(470,190,260,290)):
            with self.assertRaises(GalleryRenderError):
                self.target_svg("dp-integration")

    def test_exact_adapter_and_mode_inventory(self) -> None:
        inventory = renderer_inventory()
        self.assertEqual(inventory["adapter_count"], 43)
        self.assertEqual(inventory["engine_renderer_count"], 14)
        self.assertEqual(inventory["modes"], list(MODES))
        self.assertEqual(len(inventory["bindings"]) * len(MODES), 129)

    def test_all_bindings_are_explicit_and_silhouettes_unique(self) -> None:
        bindings = renderer_inventory()["bindings"]
        self.assertEqual(len({item["adapter_id"] for item in bindings}), 43)
        self.assertEqual(len({item["silhouette"] for item in bindings}), 43)
        self.assertFalse(any("generic" in item["silhouette"] or "unknown" in item["silhouette"] for item in bindings))
        self.assertTrue(all(item["renderer"].startswith("_") for item in bindings))

    def test_exact_129_documents_render(self) -> None:
        documents = [render_gallery_html(ir, mode, fixture_id) for fixture_id, ir in all_sources() for mode in MODES]
        self.assertEqual(len(documents), 129)
        self.assertTrue(all(value.startswith("<!doctype html>") for value in documents))

    def test_every_document_has_required_metadata(self) -> None:
        for fixture_id, ir in all_sources():
            for mode in MODES:
                parser = Collector()
                parser.feed(render_gallery_html(ir, mode, fixture_id))
                self.assertEqual(parser.html_attrs["data-candidate-id"], P19B_CANDIDATE_ID)
                self.assertEqual(parser.html_attrs["data-fixture-id"], fixture_id)
                self.assertEqual(parser.html_attrs["data-mode"], mode)
                self.assertEqual(parser.html_attrs["data-visual-parent-candidate"], P18_PARENT_CANDIDATE_ID)
                self.assertEqual(parser.html_attrs["data-visual-parent-manifest-sha256"], P18_PARENT_MANIFEST_SHA256)
                self.assertIn(parser.html_attrs["data-check-disposition"], {"p19b-static-and-browser-planned"})
                self.assertNotIn("", (parser.html_attrs["data-layout-engine"], parser.html_attrs["data-silhouette"]))

    def test_every_document_is_scriptless_and_network_independent(self) -> None:
        forbidden = re.compile(r"(?:https?:|//fonts\.|<script\b|onload\s*=|onclick\s*=|javascript:)", re.IGNORECASE)
        for fixture_id, ir in all_sources():
            for mode in MODES:
                self.assertIsNone(forbidden.search(render_gallery_html(ir, mode, fixture_id)))

    def test_every_document_has_unique_svg_accessibility_ids(self) -> None:
        for fixture_id, ir in all_sources():
            for mode in MODES:
                parser = Collector()
                parser.feed(render_gallery_html(ir, mode, fixture_id))
                self.assertEqual(len(parser.ids), len(set(parser.ids)))
                self.assertEqual(parser.tags.count("svg"), 1)
                self.assertEqual(parser.tags.count("title"), 2)  # HTML title plus SVG title.
                self.assertEqual(parser.tags.count("desc"), 1)

    def test_every_document_exposes_alternative_table(self) -> None:
        for fixture_id, ir in all_sources():
            value = render_gallery_html(ir, "neutral-light", fixture_id)
            self.assertIn("Dữ liệu thay thế có thể kiểm chứng", value)
            self.assertIn("<table>", value)
            self.assertIn("<th scope=\"col\">Semantic IDs</th>", value)

    def test_mode_derivation_preserves_svg_geometry(self) -> None:
        for fixture_id, ir in all_sources():
            normalized = []
            for mode in MODES:
                value = render_gallery_html(ir, mode, fixture_id)
                svg = value[value.index("<svg "):value.index("</svg>") + 6]
                normalized.append(svg.replace(mode, "MODE"))
            self.assertEqual(normalized[0], normalized[1])
            self.assertEqual(normalized[1], normalized[2])

    def test_reduced_motion_print_and_responsive_contracts_are_present(self) -> None:
        value = render_gallery_html(fixtures()["architecture"], "neutral-light", "type-architecture")
        self.assertIn("prefers-reduced-motion:reduce", value)
        self.assertIn("@media print", value)
        self.assertIn("@media(max-width:820px)", value)
        self.assertIn("content-fit-no-global-transform", value)

    def test_neutral_light_preserves_exact_p18_review17_roles(self) -> None:
        self.assertEqual(P18_VISUAL_MODES["neutral-light"], {
            "paper": "#eeece7", "canvas": "#f7f6f2", "surface": "#ffffff",
            "surface_alt": "#eeece7", "text": "#252b3c", "muted": "#687286",
            "border": "#c7ccd2", "connector": "#4f5e76", "grid": "#d9d7d2",
            "accent": "#f26a32", "accent_soft": "#f8e7dd", "accent_text": "#df5522",
            "blue": "#2f65af", "green": "#7c9167", "amber": "#b9894b",
            "plum": "#756b7f", "danger": "#b9473f", "on_accent": "#ffffff",
        })

    def test_p18_typography_shape_and_legend_grammar_are_emitted(self) -> None:
        value = render_gallery_html(fixtures()["architecture"], "neutral-light", "type-architecture")
        for receipt in ("Georgia · display", "Avenir Next · material", "Menlo · technical"):
            self.assertIn(receipt, value)
        self.assertIn("border-radius:18px", value)
        self.assertIn("stroke-linecap:round", value)
        self.assertIn("P18 REVIEW‑17 VISUAL LINEAGE", value)
        self.assertIn('data-visual-grammar="p18r6-review17"', value)

    def test_legacy_blue_accent_direction_is_absent(self) -> None:
        for fixture_id, ir in all_sources():
            for mode in MODES:
                value = render_gallery_html(ir, mode, fixture_id).lower()
                self.assertNotIn("#246bce", value)
                self.assertNotIn("#f5f7fa", value)

    def test_invalid_mode_fails_closed(self) -> None:
        with self.assertRaises(GalleryRenderError) as context:
            render_gallery_html(fixtures()["architecture"], "sepia", "type-architecture")
        self.assertEqual(context.exception.code, "mode-invalid")

    def test_exact_four_capability_parents_render(self) -> None:
        parents = {}
        for capability, ir in variant_fixtures().items():
            parser = Collector()
            parser.feed(render_gallery_html(ir, "neutral-light", f"cap-{capability.lower()}"))
            parents[capability] = parser.html_attrs["data-parent-type"]
        self.assertEqual(set(parents), set(P19A_CAPABILITIES))
        self.assertEqual(parents, {"CAP-V17": "bar-chart", "CAP-V18": "line-chart", "CAP-V19": "line-chart", "CAP-V20": "scatter-plot"})


if __name__ == "__main__":
    unittest.main()
