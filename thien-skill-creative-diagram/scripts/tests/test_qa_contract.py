from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from full_renderer import render_static
from output_pipeline import export_artifacts
from qa_contract import (
    QAFailure,
    audit_skill_tree,
    validate_carrier_equivalence,
    validate_contrast_contract,
    validate_determinism,
    validate_fidelity,
    validate_geometry_contract,
    validate_json_documents,
    validate_markdown_links,
    validate_motion_html,
    validate_package_inventory,
    validate_quantitative_ir,
    validate_state_redundancy,
    validate_svg_contract,
    validate_type_coverage,
)
from semantic_fixtures import fixtures, legacy_fixtures
from safe_import import ImportFailure, parse_drawio, parse_json_text, parse_mermaid_text, parse_pasted_table
from visual_system import Rect, Route, load_visual_system


SKILL_ROOT = SCRIPT_DIR.parent


def request(diagram_type: str, *, motion: str = "none", format: str = "svg") -> dict[str, object]:
    return {
        "instruction": "Tạo artifact QA.",
        "source": {"kind": "natural-language", "content": "Fixture độc lập."},
        "diagram_type": diagram_type,
        "size": "fit",
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": {"mode": "explicit", "tag": "vi"},
        "format": format,
        "motion": motion,
    }


def minimal_svg(label: str = "Nhãn tiếng Việt") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-labelledby="title desc"><title id="title">Sơ đồ</title><desc id="desc">Mô tả</desc><rect id="node" x="10" y="10" width="80" height="60"/><text x="20" y="45">{label}</text></svg>'''


def expect_code(test: unittest.TestCase, code: str, callback) -> None:
    with test.assertRaises(QAFailure) as raised:
        callback()
    test.assertEqual(raised.exception.code, code)


class RepositoryQATests(unittest.TestCase):
    def test_canonical_tree_passes_schema_link_type_hygiene_and_contrast_audit(self) -> None:
        report = audit_skill_tree(SKILL_ROOT)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["coverage"]["type_count"], 39)
        self.assertEqual(report["coverage"]["capability_count"], 111)
        self.assertEqual(report["contrast_pairs"], 27)

    def test_invalid_json_mutation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text("{", encoding="utf-8")
            expect_code(self, "schema-json-invalid", lambda: validate_json_documents([path]))

    def test_missing_and_escaping_link_mutations_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            missing = root / "missing.md"
            missing.write_text("[x](absent.md)", encoding="utf-8")
            expect_code(self, "reference-link-missing", lambda: validate_markdown_links([missing], root))
            escaping = root / "escape.md"
            escaping.write_text("[x](../outside.md)", encoding="utf-8")
            expect_code(self, "reference-link-escape", lambda: validate_markdown_links([escaping], root))

    def test_type_coverage_mutation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for diagram_type in fixtures():
                (root / f"type-{diagram_type}.md").write_text("# type\n", encoding="utf-8")
            (root / "type-line-chart.md").unlink()
            (root / "capability-map.json").write_text("{}", encoding="utf-8")
            expect_code(self, "type-coverage-mismatch", lambda: validate_type_coverage(root))

    def test_determinism_mutation_is_detected(self) -> None:
        self.assertEqual(validate_determinism("same", "same")["status"], "pass")
        expect_code(self, "build-drift", lambda: validate_determinism("first", "second"))


class GeometryMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = Rect(0, 0, 120, 100)
        self.nodes = {"a": Rect(10, 20, 20, 20), "b": Rect(90, 20, 20, 20)}
        self.route = Route("ab", "a", "b", ((30, 30), (90, 30)))

    def test_valid_geometry_passes(self) -> None:
        self.assertEqual(validate_geometry_contract(self.canvas, self.nodes, [self.route])["status"], "pass")

    def test_bounds_clipping_overlap_and_endpoint_mutations_are_detected(self) -> None:
        expect_code(self, "node-out-of-bounds", lambda: validate_geometry_contract(self.canvas, {**self.nodes, "b": Rect(110, 20, 20, 20)}, []))
        expect_code(self, "node-overlap", lambda: validate_geometry_contract(self.canvas, {**self.nodes, "b": Rect(25, 20, 20, 20)}, []))
        bad = Route("ab", "a", "b", ((20, 30), (100, 30)))
        expect_code(self, "route-endpoint-invalid", lambda: validate_geometry_contract(self.canvas, self.nodes, [bad]))
        missing = Route("ac", "a", "c", ((30, 30), (90, 30)))
        expect_code(self, "route-endpoint-missing", lambda: validate_geometry_contract(self.canvas, self.nodes, [missing]))

    def test_unrelated_node_crossing_mutation_is_detected(self) -> None:
        nodes = {**self.nodes, "middle": Rect(55, 20, 18, 20)}
        expect_code(self, "route-crosses-node", lambda: validate_geometry_contract(self.canvas, nodes, [self.route]))

    def test_connector_crossing_and_shared_attach_mutations_are_detected(self) -> None:
        nodes = {
            "left": Rect(0, 40, 10, 10), "right": Rect(110, 40, 10, 10),
            "top": Rect(55, 0, 10, 10), "bottom": Rect(55, 90, 10, 10),
        }
        routes = [
            Route("horizontal", "left", "right", ((10, 45), (110, 45))),
            Route("vertical", "top", "bottom", ((60, 10), (60, 90))),
        ]
        expect_code(self, "route-crossing-unmarked", lambda: validate_geometry_contract(self.canvas, nodes, routes))
        self.assertEqual(validate_geometry_contract(self.canvas, nodes, routes, intentional_crossings=[frozenset({"horizontal", "vertical"})])["status"], "pass")
        shared_nodes = {"a": Rect(10, 20, 20, 20), "b": Rect(90, 5, 20, 20), "c": Rect(90, 65, 20, 20)}
        shared = [
            Route("ab", "a", "b", ((30, 30), (60, 30), (60, 15), (90, 15))),
            Route("ac", "a", "c", ((30, 30), (60, 30), (60, 75), (90, 75))),
        ]
        expect_code(self, "shared-attach-point", lambda: validate_geometry_contract(self.canvas, shared_nodes, shared))


class SVGAccessibilityTypographyTests(unittest.TestCase):
    def test_valid_svg_and_all_27_generated_svgs_pass_static_contract(self) -> None:
        self.assertEqual(validate_svg_contract(minimal_svg())["status"], "pass")
        for diagram_type, ir in legacy_fixtures().items():
            with self.subTest(diagram_type=diagram_type):
                svg = render_static(ir).svg
                self.assertEqual(validate_svg_contract(svg, ir)["status"], "pass")

    def test_duplicate_id_name_external_and_bounds_mutations_are_detected(self) -> None:
        expect_code(self, "duplicate-svg-id", lambda: validate_svg_contract(minimal_svg().replace('id="node"', 'id="title"')))
        expect_code(self, "accessible-name-missing", lambda: validate_svg_contract(minimal_svg().replace('aria-labelledby="title desc"', 'aria-labelledby="absent desc"')))
        expect_code(self, "svg-executable-or-external", lambda: validate_svg_contract(minimal_svg().replace("<rect", '<rect onclick="x()"')))
        expect_code(self, "graphic-out-of-bounds", lambda: validate_svg_contract(minimal_svg().replace('x="10" y="10" width="80"', 'x="50" y="10" width="80"')))

    def test_clipping_compression_ellipsis_and_unicode_mutations_are_detected(self) -> None:
        clipped = minimal_svg().replace("</desc>", '</desc><defs><clipPath id="cut"><rect x="0" y="0" width="10" height="10"/></clipPath></defs>')
        expect_code(self, "material-clipping-risk", lambda: validate_svg_contract(clipped))
        compressed = minimal_svg().replace("<text", '<text textLength="10"')
        expect_code(self, "typography-compressed", lambda: validate_svg_contract(compressed))
        expect_code(self, "material-ellipsis", lambda: validate_svg_contract(minimal_svg("Nhãn…")))
        decomposed = unicodedata.normalize("NFD", "Tiếng Việt")
        expect_code(self, "unicode-not-nfc", lambda: validate_svg_contract(minimal_svg(decomposed)))

    def test_read_order_and_material_loss_mutations_are_detected(self) -> None:
        ir = copy.deepcopy(fixtures()["architecture"])
        svg = render_static(ir).svg
        ir["accessibility"]["reading_order"] = list(reversed(ir["accessibility"]["reading_order"]))
        expect_code(self, "reading-order-mismatch", lambda: validate_svg_contract(svg, ir))
        missing = copy.deepcopy(fixtures()["architecture"])
        missing["nodes"][0]["label"] = "Nhãn nguồn chưa render"
        expect_code(self, "material-label-missing", lambda: validate_svg_contract(svg, missing))

    def test_contrast_and_non_color_state_mutations_are_detected(self) -> None:
        system = load_visual_system()
        self.assertEqual(validate_contrast_contract(system)["status"], "pass")
        system["modes"]["neutral-light"]["text"] = system["modes"]["neutral-light"]["canvas"]
        expect_code(self, "contrast-failure", lambda: validate_contrast_contract(system))
        matrix = fixtures()["dp-security-matrix"]
        self.assertEqual(validate_state_redundancy(matrix, render_static(matrix).svg)["status"], "pass")
        ir = {"nodes": [{"id": "n", "label": "Mục", "state": "blocked"}]}
        expect_code(self, "color-only-state", lambda: validate_state_redundancy(ir, minimal_svg("Khác")))


class QuantitativeIntegrityTests(unittest.TestCase):
    def test_three_carriers_normalize_equivalently_including_zero_negative_and_missing(self) -> None:
        pasted = "Kỳ\tGiá trị\tGhi chú\nT1\t0\tnull\nT2\t-2.50\tổn định"
        csv_text = "Kỳ,Giá trị,Ghi chú\nT1,0,null\nT2,-2.50,ổn định"
        json_text = json.dumps([
            {"Kỳ": "T1", "Giá trị": 0, "Ghi chú": None},
            {"Kỳ": "T2", "Giá trị": -2.5, "Ghi chú": "ổn định"},
        ], ensure_ascii=False)
        self.assertEqual(validate_carrier_equivalence(pasted, csv_text, json_text)["status"], "pass")
        expect_code(self, "carrier-ir-mismatch", lambda: validate_carrier_equivalence(pasted, csv_text, json_text.replace("-2.5", "-3.5")))

    def test_core_chart_source_to_render_assertions_pass(self) -> None:
        for diagram_type in ("bar-chart", "line-chart", "scatter-plot", "radar"):
            ir = copy.deepcopy(fixtures()[diagram_type])
            for series in ir["series"]:
                series["unit"] = series.get("unit") or "điểm"
            svg = export_artifacts(ir, request(diagram_type), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
            with self.subTest(diagram_type=diagram_type):
                self.assertEqual(validate_quantitative_ir(ir, svg)["status"], "pass")

    def test_numeric_unit_missingness_and_source_render_mutations_are_detected(self) -> None:
        ir = copy.deepcopy(fixtures()["bar-chart"])
        ir["series"][0]["unit"] = None
        expect_code(self, "quantitative-unit-missing", lambda: validate_quantitative_ir(ir))
        ir = copy.deepcopy(fixtures()["bar-chart"])
        ir["series"][0]["data"][0].update({"value": None, "missing": False})
        expect_code(self, "missingness-implicit", lambda: validate_quantitative_ir(ir))
        ir = copy.deepcopy(fixtures()["bar-chart"])
        ir["axes"][1]["domain_min"] = 1
        expect_code(self, "bar-zero-baseline", lambda: validate_quantitative_ir(ir))
        ir["axes"][1]["domain_min"] = -5
        ir["series"][0]["data"][0]["value"] = -3
        self.assertEqual(validate_quantitative_ir(ir)["status"], "pass")
        good = copy.deepcopy(fixtures()["bar-chart"])
        svg = export_artifacts(good, request("bar-chart"), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
        mutated = svg.replace('"value":12', '"value":13', 1)
        expect_code(self, "source-render-value-mismatch", lambda: validate_quantitative_ir(good, mutated))

    def test_scatter_radar_quadrant_and_funnel_mutations_are_detected(self) -> None:
        scatter = copy.deepcopy(fixtures()["scatter-plot"])
        scatter["series"][0]["unit"] = "điểm"
        scatter["series"][0]["data"][0]["domain"] = 99
        expect_code(self, "scatter-coordinate-out-of-domain", lambda: validate_quantitative_ir(scatter))
        radar = copy.deepcopy(fixtures()["radar"])
        radar["axes"][1]["domain_max"] = 10
        expect_code(self, "radar-scale-incompatible", lambda: validate_quantitative_ir(radar))
        quadrant = copy.deepcopy(fixtures()["quadrant"])
        quadrant["series"][0]["unit"] = "điểm"
        quadrant["series"][0]["data"][0]["value"] = 99
        expect_code(self, "quadrant-coordinate-out-of-domain", lambda: validate_quantitative_ir(quadrant))
        funnel = copy.deepcopy(fixtures()["pyramid-funnel"])
        funnel["series"][0]["data"][1]["value"] = 135
        self.assertEqual(validate_quantitative_ir(funnel)["status"], "pass")
        svg = export_artifacts(funnel, request("pyramid-funnel"), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
        mutated = svg.replace('"domain":"Nhận biết"', '"domain":"Hành động"', 1)
        expect_code(self, "funnel-order-invalid", lambda: validate_quantitative_ir(funnel, mutated))

    def test_temporal_date_timezone_duration_order_and_render_mutations_are_detected(self) -> None:
        for diagram_type in ("gantt", "timeline"):
            ir = copy.deepcopy(fixtures()[diagram_type])
            svg = export_artifacts(ir, request(diagram_type), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
            self.assertEqual(validate_quantitative_ir(ir, svg)["status"], "pass")
        gantt = copy.deepcopy(fixtures()["gantt"])
        gantt["nodes"][0]["start"] = "2026-08-15T08:00:00"
        expect_code(self, "timezone-missing", lambda: validate_quantitative_ir(gantt))
        gantt = copy.deepcopy(fixtures()["gantt"])
        gantt["nodes"][0]["end"] = "2026-08-14T08:00:00+07:00"
        expect_code(self, "temporal-duration-invalid", lambda: validate_quantitative_ir(gantt))
        timeline = copy.deepcopy(fixtures()["timeline"])
        timeline["nodes"].reverse()
        expect_code(self, "temporal-order-invalid", lambda: validate_quantitative_ir(timeline))
        good = fixtures()["gantt"]
        svg = export_artifacts(good, request("gantt"), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
        expect_code(self, "source-render-time-mismatch", lambda: validate_quantitative_ir(good, svg.replace("2026-08-15T08:00:00+07:00", "changed", 1)))


class SecurityMotionPackageTests(unittest.TestCase):
    def test_import_security_codes_and_zero_network_side_effect(self) -> None:
        hostile = (
            ("mermaid-executable-feature", lambda: parse_mermaid_text("flowchart LR\nA-->B\nclick A https://example.invalid")),
            ("xml-external-feature", lambda: parse_drawio('<!DOCTYPE x [<!ENTITY y SYSTEM "file:///etc/passwd">]><mxfile/>')),
            ("json-depth-over-limit", lambda: parse_json_text("[" * 66 + "0" + "]" * 66)),
        )
        for code, callback in hostile:
            with self.subTest(code=code), self.assertRaises(ImportFailure) as raised:
                callback()
            self.assertEqual(raised.exception.code, code)
        with mock.patch("socket.socket", side_effect=AssertionError("network forbidden")) as network:
            bundle = parse_pasted_table("Tên\tGiá trị\nA\t1")
            self.assertEqual(bundle["record_count"], 4)
            network.assert_not_called()

    def test_fidelity_equation_and_invention_mutations_are_detected(self) -> None:
        ir = copy.deepcopy(fixtures()["architecture"])
        self.assertEqual(validate_fidelity(ir)["status"], "pass")
        ir["fidelity"]["kept"].pop()
        expect_code(self, "fidelity-equation-invalid", lambda: validate_fidelity(ir))
        ir = copy.deepcopy(fixtures()["architecture"])
        ir["fidelity"]["invented_count"] = 1
        expect_code(self, "invented-content", lambda: validate_fidelity(ir))

    def test_motion_static_reduced_print_focus_and_controls_mutations_are_detected(self) -> None:
        html = export_artifacts(fixtures()["flowchart"], request("flowchart", motion="step", format="html"), auto_detect_rasterizer=False).artifacts["html"].content.decode()
        self.assertEqual(validate_motion_html(html, "step")["status"], "pass")
        replacements = {
            "static-frame-incomplete": ('data-static-frame="complete"', ""),
            "reduced-motion-missing": ("prefers-reduced-motion", "prefers-motion"),
            "print-frame-missing": ("@media print", "@media screen"),
            "focus-style-missing": (":focus-visible", ":hover"),
            "motion-controls-missing": ("motion-replay", "motion-finished"),
        }
        for code, (old, new) in replacements.items():
            with self.subTest(code=code):
                expect_code(self, code, lambda old=old, new=new: validate_motion_html(html.replace(old, new), "step"))

    def test_package_hygiene_mutations_are_detected(self) -> None:
        self.assertEqual(validate_package_inventory(["SKILL.md", "scripts/run.py", "references/type-index.md"])["status"], "pass")
        cases = {
            "package-path-absolute": ["/Users/example/secret.txt"],
            "package-path-traversal": ["../escape.txt"],
            "package-development-file": ["scripts/__pycache__/x.pyc"],
            "package-secret-file": [".env"],
            "package-qa-only-file": ["evidence/p02/reference.png"],
            "package-duplicate-path": ["SKILL.md", "SKILL.md"],
        }
        for code, paths in cases.items():
            with self.subTest(code=code):
                expect_code(self, code, lambda paths=paths: validate_package_inventory(paths))


if __name__ == "__main__":
    unittest.main()
