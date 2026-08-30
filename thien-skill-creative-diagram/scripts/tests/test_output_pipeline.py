from __future__ import annotations

import binascii
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from motion_catalog import MOTION_CAPABILITIES, select_motion_capabilities
from output_pipeline import (
    OUTPUT_CAPABILITIES,
    OutputFailure,
    RasterizerAdapter,
    detect_rasterizer,
    export_artifacts,
    registered_capabilities,
    write_bundle,
)
from p08_coverage import P08_COVERAGE
from semantic_fixtures import fixtures, legacy_fixtures


def request(diagram_type: str, *, format: str = "html", motion: str = "none", size: str = "fit") -> dict[str, object]:
    return {
        "instruction": "Tạo artifact đã xác thực.",
        "source": {"kind": "natural-language", "content": "Dữ liệu fixture."},
        "diagram_type": diagram_type,
        "size": size,
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": "neutral-light",
        "language": {"mode": "explicit", "tag": "vi"},
        "format": format,
        "motion": motion,
    }


def png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + b"\x00\x00\x00\x00" * width for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


class PortableOutputTests(unittest.TestCase):
    def test_all_27_types_export_html_svg_and_all_motion_modes(self) -> None:
        cases = legacy_fixtures()
        for diagram_type, ir in cases.items():
            with self.subTest(diagram_type=diagram_type, format="svg"):
                self.assertEqual(set(export_artifacts(ir, request(diagram_type, format="svg"), auto_detect_rasterizer=False).artifacts), {"svg"})
            for mode in ("none", "reveal", "step", "loop"):
                with self.subTest(diagram_type=diagram_type, mode=mode):
                    self.assertEqual(set(export_artifacts(ir, request(diagram_type, motion=mode), auto_detect_rasterizer=False).artifacts), {"html"})

    def test_html_none_is_self_contained_script_free_and_complete(self) -> None:
        ir = fixtures()["architecture"]
        bundle = export_artifacts(ir, request("architecture"), auto_detect_rasterizer=False)
        html = bundle.artifacts["html"].content.decode()
        self.assertIn("<svg", html)
        self.assertNotIn("<script>", html)
        self.assertNotIn("P-07 ·", html)
        for label in ("Người dùng", "Cổng dịch vụ", "Vùng tin cậy"):
            self.assertIn(label, html)
        self.assertTrue(bundle.ledger["static_fallback_complete"])
        self.assertEqual(bundle.ledger["validation"]["html"], "pass")

    def test_svg_is_diagram_only_accessible_and_contains_exact_chart_data(self) -> None:
        bundle = export_artifacts(fixtures()["bar-chart"], request("bar-chart", format="svg"), auto_detect_rasterizer=False)
        svg = bundle.artifacts["svg"].content.decode()
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn('role="img"', svg)
        self.assertIn("Dữ liệu chính xác:", svg)
        self.assertIn("Tháng 1", svg)
        self.assertIn("12", svg)
        self.assertNotIn("<script", svg)
        self.assertNotIn("P-07 ·", svg)

    def test_quantitative_html_has_exact_data_table(self) -> None:
        html = export_artifacts(fixtures()["radar"], request("radar"), auto_detect_rasterizer=False).artifacts["html"].content.decode()
        self.assertIn("<table>", html)
        self.assertIn("Tốc độ", html)
        self.assertIn("điểm", html)
        self.assertIn("Dữ liệu chính xác", html)

    def test_size_presets_and_print_page_rules_are_explicit(self) -> None:
        ir = fixtures()["architecture"]
        a4 = export_artifacts(ir, request("architecture", format="svg", size="print-a4-landscape"), auto_detect_rasterizer=False).artifacts["svg"].content.decode()
        self.assertIn('width="297mm"', a4)
        self.assertIn('height="210mm"', a4)
        letter_html = export_artifacts(ir, request("architecture", size="print-letter-landscape"), auto_detect_rasterizer=False).artifacts["html"].content.decode()
        self.assertIn("@page{size:Letter landscape", letter_html)

    def test_four_public_motion_modes_keep_complete_static_content(self) -> None:
        ir = fixtures()["flowchart"]
        for mode in ("none", "reveal", "step", "loop"):
            with self.subTest(mode=mode):
                bundle = export_artifacts(ir, request("flowchart", motion=mode), auto_detect_rasterizer=False)
                html = bundle.artifacts["html"].content.decode()
                for label in ("Bắt đầu", "Hợp lệ?", "Chấp nhận", "Từ chối"):
                    self.assertIn(label, html)
                self.assertIn("prefers-reduced-motion", html)
                self.assertIn("@media print", html)
                self.assertIn('data-static-frame="complete"', html)
                if mode == "none":
                    self.assertNotIn("<script>", html)
                else:
                    self.assertIn("<script>", html)
                    self.assertIn("motion-replay", html)
                if mode == "step":
                    for control in ("motion-prev", "motion-next", "motion-pause", "motion-replay"):
                        self.assertIn(control, html)
                    self.assertIn("ArrowRight", html)
                    self.assertIn("ArrowLeft", html)

    def test_motion_runtime_failure_degrades_to_static_html(self) -> None:
        bundle = export_artifacts(fixtures()["sequence"], request("sequence", motion="step"), auto_detect_rasterizer=False, motion_runtime=False)
        html = bundle.artifacts["html"].content.decode()
        self.assertNotIn("<script>", html)
        self.assertTrue(any("Motion runtime is unavailable" in warning for warning in bundle.ledger["warnings"]))
        self.assertEqual(bundle.ledger["motion_capabilities"], ["CAP-M01"])

    def test_output_is_deterministic(self) -> None:
        ir = fixtures()["swimlane"]
        first = export_artifacts(ir, request("swimlane", motion="step"), auto_detect_rasterizer=False)
        second = export_artifacts(ir, request("swimlane", motion="step"), auto_detect_rasterizer=False)
        self.assertEqual(first.artifacts["html"].content, second.artifacts["html"].content)
        self.assertEqual(first.ledger, second.ledger)

    def test_absent_png_renderer_returns_declared_fallback_without_install(self) -> None:
        bundle = export_artifacts(fixtures()["architecture"], request("architecture", format="png"), auto_detect_rasterizer=False)
        self.assertEqual(set(bundle.artifacts), {"svg"})
        self.assertIsNone(bundle.ledger["rasterizer"])
        self.assertTrue(any("no installation was attempted" in warning for warning in bundle.ledger["warnings"]))
        combo = export_artifacts(fixtures()["architecture"], request("architecture", format="html+png"), auto_detect_rasterizer=False)
        self.assertEqual(set(combo.artifacts), {"html"})

    def test_preinstalled_adapter_can_produce_validated_png_and_combo(self) -> None:
        adapter = RasterizerAdapter("test-preinstalled", lambda svg, width, height: png(width, height))
        only = export_artifacts(fixtures()["architecture"], request("architecture", format="png"), rasterizer=adapter, auto_detect_rasterizer=False)
        self.assertEqual(set(only.artifacts), {"png"})
        self.assertEqual(only.ledger["validation"]["png"], "pass")
        combo = export_artifacts(fixtures()["architecture"], request("architecture", format="html+png"), rasterizer=adapter, auto_detect_rasterizer=False)
        self.assertEqual(set(combo.artifacts), {"html", "png"})
        self.assertEqual(combo.ledger["base_static_svg_hash"], only.ledger["base_static_svg_hash"])

    def test_bad_png_adapter_falls_back_transparently(self) -> None:
        adapter = RasterizerAdapter("broken", lambda svg, width, height: b"not-png")
        bundle = export_artifacts(fixtures()["architecture"], request("architecture", format="png"), rasterizer=adapter, auto_detect_rasterizer=False)
        self.assertEqual(set(bundle.artifacts), {"svg"})
        self.assertTrue(any("broken failed" in warning for warning in bundle.ledger["warnings"]))

    def test_motion_request_on_svg_is_disclosed_static_fallback(self) -> None:
        bundle = export_artifacts(fixtures()["architecture"], request("architecture", format="svg", motion="reveal"), auto_detect_rasterizer=False)
        self.assertEqual(bundle.ledger["motion_capabilities"], ["CAP-M01"])
        self.assertTrue(any("unavailable for SVG" in warning for warning in bundle.ledger["warnings"]))
        self.assertNotIn("<script", bundle.artifacts["svg"].content.decode())

    def test_environment_detection_can_be_forced_to_empty_path(self) -> None:
        self.assertIsNone(detect_rasterizer(search_path="", allow_python_adapter=False))
        capabilities = registered_capabilities("architecture", auto_detect_rasterizer=False)
        self.assertIn("exporter:html", capabilities)
        self.assertIn("exporter:svg", capabilities)
        self.assertNotIn("exporter:png", capabilities)
        adapter = RasterizerAdapter("test-preinstalled", lambda svg, width, height: png(width, height))
        self.assertIn("exporter:png", registered_capabilities("architecture", rasterizer=adapter, auto_detect_rasterizer=False))

    def test_explicit_type_mismatch_fails(self) -> None:
        with self.assertRaisesRegex(OutputFailure, "does not match"):
            export_artifacts(fixtures()["architecture"], request("flowchart"), auto_detect_rasterizer=False)

    def test_font_substitution_is_disclosed_without_network_fetch(self) -> None:
        bundle = export_artifacts(fixtures()["architecture"], request("architecture"), auto_detect_rasterizer=False, font_substitution="system-ui")
        self.assertTrue(any("Preferred font is unavailable" in warning for warning in bundle.ledger["warnings"]))
        self.assertFalse(bundle.ledger["font_policy"]["network_fetch"])
        self.assertIn("Người dùng", bundle.artifacts["html"].content.decode())


class MotionInventoryTests(unittest.TestCase):
    def test_exact_output_and_motion_inventory(self) -> None:
        self.assertEqual(set(OUTPUT_CAPABILITIES), {f"CAP-O{i:02d}" for i in range(1, 8)})
        self.assertEqual(set(MOTION_CAPABILITIES), {f"CAP-M{i:02d}" for i in range(1, 13)})
        for capability in MOTION_CAPABILITIES.values():
            self.assertTrue(capability["test_id"])
        expected_p08 = {f"CAP-O{i:02d}" for i in range(1, 8)} | {f"CAP-M{i:02d}" for i in range(1, 13)} | {f"CAP-F{i:02d}" for i in range(7, 13)}
        self.assertEqual(set(P08_COVERAGE), expected_p08)
        self.assertEqual(len(P08_COVERAGE), 25)

    def test_all_motion_specializations_are_selected_on_original_fixtures(self) -> None:
        cases = legacy_fixtures()
        selected = set()
        for diagram_type, mode in (("architecture", "reveal"), ("architecture", "loop"), ("data-flow", "step"), ("flowchart", "step"), ("timeline", "step")):
            selected.update(select_motion_capabilities(cases[diagram_type], mode))
        self.assertEqual(selected, set(MOTION_CAPABILITIES))


class OutputWritingTests(unittest.TestCase):
    def test_write_requires_exact_relative_targets_and_no_implicit_overwrite(self) -> None:
        bundle = export_artifacts(fixtures()["architecture"], request("architecture", format="svg"), auto_detect_rasterizer=False)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OutputFailure):
                write_bundle(bundle, {}, directory)
            with self.assertRaises(Exception):
                write_bundle(bundle, {"svg": "../escape.svg"}, directory)
            written = write_bundle(bundle, {"svg": "artifacts/diagram.svg"}, directory)
            self.assertTrue(Path(written["svg"]).is_file())
            with self.assertRaisesRegex(OutputFailure, "overwrite permission"):
                write_bundle(bundle, {"svg": "artifacts/diagram.svg"}, directory)


if __name__ == "__main__":
    unittest.main()
