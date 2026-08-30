"""Focused P-19B tests for three-mode standalone gallery rendering."""

from __future__ import annotations

from html.parser import HTMLParser
import re
import unittest

from gallery_renderer_v15 import GalleryRenderError, MODES, P19B_CANDIDATE_ID, render_gallery_html, renderer_inventory
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
        self.assertIn("@media(max-width:720px)", value)
        self.assertIn("content-fit-no-global-transform", value)

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
