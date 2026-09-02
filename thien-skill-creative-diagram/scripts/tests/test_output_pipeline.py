from __future__ import annotations

import binascii
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
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
    _prepare_svg,
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
    def test_profiled_fit_preserves_renderer_intrinsic_canvas_while_generic_fit_keeps_public_default(self) -> None:
        ir = fixtures()["architecture"]
        profiled = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1600" viewBox="0 0 1600 1600" '
            'role="img" aria-labelledby="diagram-title diagram-description" data-renderer-version="profile-renderer-2.1.0">'
            '<title id="diagram-title">Profiled</title><desc id="diagram-description">Profiled fit.</desc>'
            '<text>Người dùng</text><text>Cổng dịch vụ</text><text>Vùng tin cậy</text></svg>'
        )
        generic = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" '
            'role="img" aria-labelledby="diagram-title diagram-description">'
            '<title id="diagram-title">Generic</title><desc id="diagram-description">Generic fit.</desc>'
            '<text>Người dùng</text><text>Cổng dịch vụ</text><text>Vùng tin cậy</text></svg>'
        )
        profiled_root = ET.fromstring(_prepare_svg(profiled, ir, "neutral-light", "fit", annotate_motion=False)[0])
        generic_root = ET.fromstring(_prepare_svg(generic, ir, "neutral-light", "fit", annotate_motion=False)[0])
        self.assertEqual((profiled_root.get("width"), profiled_root.get("height")), ("1600", "1600"))
        self.assertEqual((generic_root.get("width"), generic_root.get("height")), ("1600", "900"))

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
    def test_profile_job_cli_help_and_contract_are_discoverable_from_unrelated_cwd(self) -> None:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            help_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--help"],
                cwd=temporary,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            contract_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--print-job-contract"],
                cwd=temporary,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--job", help_result.stdout)
        self.assertIn("--output-dir", help_result.stdout)
        self.assertEqual(contract_result.returncode, 0, contract_result.stderr)
        contract = json.loads(contract_result.stdout)
        self.assertEqual(contract["job_version"], "2.1")
        self.assertEqual(contract["fixed_output"]["files"], ["diagram.svg", "diagram.ledger.json"])
        self.assertEqual(
            contract["expected_counts"]["required"],
            ["nodes", "edges", "groups", "lanes", "series", "axes", "annotations", "directed_edges"],
        )
        self.assertFalse(contract["expected_counts"]["additional_keys"])
        self.assertIn("exactly all eight", contract["expected_counts"]["semantics"])
        self.assertIn("source_assertions", contract["required"])
        self.assertEqual(
            set(contract["source_assertions"]["exact_shapes"]),
            {"node_ids", "edge_assertions", "group_members", "lane_members", "node_member_ids", "series_data_ids", "axis_ids", "annotation_ids"},
        )
        self.assertIn("explicitly contain a members field", contract["source_assertions"]["exact_shapes"]["node_member_ids"])
        self.assertIn("order", contract["relation_group"]["optional_edge_fields"])
        self.assertEqual(set(contract["collection_schema"]["properties"]), {"nodes", "edges", "groups", "lanes", "series", "axes", "annotations"})
        self.assertNotIn("source_refs", contract["collection_schema"]["$defs"]["node"]["properties"])
        self.assertNotIn("source_refs", contract["collection_schema"]["$defs"]["node"]["required"])
        self.assertEqual(len(contract["supported_profiles"]), 45)
        self.assertEqual(len({item["layout_engine"] for item in contract["supported_profiles"]}), 14)
        self.assertIn("social-square", contract["dial_values"]["size"])
        self.assertEqual(contract["optional_defaults"]["detail"], "balanced")
        special = {item["profile_id"]: item for item in contract["supported_profiles"]}
        self.assertEqual(special["dumbbell"]["variant_ids"], ["CAP-V17"])
        self.assertEqual(special["layers"]["canonical_parent"], "layer-stack")

    def test_minimal_contract_skeleton_drives_real_cli_from_unrelated_cwd(self) -> None:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            contract_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--print-job-contract"],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(contract_result.returncode, 0, contract_result.stderr)
            contract = json.loads(contract_result.stdout)
            skeleton = contract["minimal_valid_job"]
            self.assertEqual(set(skeleton["expected_counts"]), set(contract["expected_counts"]["required"]))

            job_path = root / "job-from-contract.json"
            output_path = root / "output-from-contract"
            job_path.write_text(json.dumps(skeleton, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(job_path), "--output-dir", str(output_path)],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual({item.name for item in output_path.iterdir()}, {"diagram.svg", "diagram.ledger.json"})

            svg_path = output_path / "diagram.svg"
            ledger_path = output_path / "diagram.ledger.json"
            svg_root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual(svg_root.tag.rsplit("}", 1)[-1], "svg")
            self.assertEqual(svg_root.get("data-selected-profile"), "topology-and-zones")
            self.assertEqual(ledger["semantic_coverage"], "pass")
            self.assertEqual(ledger["geometry_validation"]["status"], "pass")
            self.assertEqual(ledger["semantic_snapshot"]["diagram"]["type"], "architecture")
            self.assertEqual(report["files"]["diagram.svg"]["sha256"], hashlib.sha256(svg_path.read_bytes()).hexdigest())
            self.assertEqual(report["files"]["diagram.ledger.json"]["sha256"], hashlib.sha256(ledger_path.read_bytes()).hexdigest())

    def test_r07_timeline_preserves_and_visibly_maps_all_five_dates_without_overlap(self) -> None:
        prompt = (
            'Dùng Thien-Skill-Creative-Diagram để tạo một SVG tĩnh bằng public one-call workflow. '
            'Chọn structural profile "time-planning", visual mode "neutral-light" và structural_override "none". '
            'Giữ nguyên toàn bộ ID, nhãn, thứ tự, nhóm, giá trị và quan hệ được nêu. Không thêm hoặc suy diễn quan hệ khác.\n'
            'Có 5 node theo thời gian: kickoff "Khởi động" role milestone bắt đầu "2026-09-01"; '
            'discovery "Khảo sát" role event bắt đầu "2026-09-03"; design "Chốt thiết kế" role milestone '
            'bắt đầu "2026-09-10"; pilot "Pilot" role event bắt đầu "2026-09-17"; launch "Go-live" '
            'role milestone bắt đầu "2026-09-30". Không có edge.'
        )
        milestones = (
            ("kickoff", "Khởi động", "milestone", "2026-09-01"),
            ("discovery", "Khảo sát", "event", "2026-09-03"),
            ("design", "Chốt thiết kế", "milestone", "2026-09-10"),
            ("pilot", "Pilot", "event", "2026-09-17"),
            ("launch", "Go-live", "milestone", "2026-09-30"),
        )
        job = {
            "job_version": "2.1",
            "instruction": prompt,
            "title": "Khởi động · Khảo sát · Chốt thiết kế · Pilot · Go-live",
            "diagram_type": "timeline",
            "structural_profile": "time-planning",
            "visual_mode": "neutral-light",
            "nodes": [
                {"id": node_id, "label": label, "role": role, "start": f"{start}T00:00:00+07:00"}
                for node_id, label, role, start in milestones
            ],
            "groups": [],
            "lanes": [],
            "series": [],
            "axes": [],
            "annotations": [],
            "relation_groups": [],
            "source_assertions": {
                "node_ids": [item[0] for item in milestones],
                "edge_assertions": [],
                "group_members": {},
                "lane_members": {},
                "node_member_ids": {},
                "series_data_ids": {},
                "axis_ids": [],
                "annotation_ids": [],
            },
            "expected_counts": {
                "nodes": 5,
                "edges": 0,
                "groups": 0,
                "lanes": 0,
                "series": 0,
                "axes": 0,
                "annotations": 0,
                "directed_edges": 0,
            },
        }
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            job_path = root / "r07.json"
            output_path = root / "r07-output"
            job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(job_path), "--output-dir", str(output_path)],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            ledger = json.loads((output_path / "diagram.ledger.json").read_text(encoding="utf-8"))
            svg = ET.fromstring((output_path / "diagram.svg").read_text(encoding="utf-8"))

        self.assertEqual(
            [(node["id"], node["label"], node["role"], node["start"]) for node in ledger["semantic_snapshot"]["nodes"]],
            [
                (node_id, label, role, f"{start}T00:00:00+07:00")
                for node_id, label, role, start in milestones
            ],
        )
        rendered_nodes = {
            element.get("data-node-id"): element
            for element in svg.iter()
            if element.get("data-node-id")
        }
        self.assertEqual(list(rendered_nodes), [item[0] for item in milestones])
        boxes: list[tuple[float, float, float, float]] = []
        for node_id, label, _role, start in milestones:
            group = rendered_nodes[node_id]
            visible_text = [
                element.text or ""
                for element in group.iter()
                if element.tag.rsplit("}", 1)[-1] == "text"
            ]
            self.assertIn(label, visible_text)
            self.assertIn(start, visible_text)
            box = tuple(float(group.get(field, "nan")) for field in ("data-x", "data-y", "data-w", "data-h"))
            x, y, width, height = box
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x + width, 1600)
            self.assertLessEqual(y + height, 1600)
            date_text = next(element for element in group.iter() if (element.text or "") == start)
            self.assertGreaterEqual(float(date_text.get("x", "nan")), x)
            self.assertLessEqual(float(date_text.get("x", "nan")), x + width)
            self.assertGreaterEqual(float(date_text.get("y", "nan")), y)
            self.assertLessEqual(float(date_text.get("y", "nan")), y + height)
            boxes.append(box)
        for index, (x1, y1, width1, height1) in enumerate(boxes):
            for x2, y2, width2, height2 in boxes[index + 1:]:
                overlaps = not (
                    x1 + width1 <= x2 or x2 + width2 <= x1
                    or y1 + height1 <= y2 or y2 + height2 <= y1
                )
                self.assertFalse(overlaps)

    def test_r08_categorical_journey_sentiments_are_contract_required_and_preserved(self) -> None:
        prompt = (
            'Dùng Thien-Skill-Creative-Diagram để tạo một SVG tĩnh bằng public one-call workflow. '
            'Chọn structural profile "work-experience", visual mode "neutral-dark" và structural_override "none". '
            'Giữ nguyên toàn bộ ID, nhãn, thứ tự, nhóm, giá trị và quan hệ được nêu. Không thêm hoặc suy diễn quan hệ khác.\n'
            'Có 5 journey stage node: discover "Khám phá" với stage_order=1, action="Tìm giải pháp", '
            'touchpoint="Search", sentiment="curious"; compare "So sánh" với stage_order=2, '
            'action="Đối chiếu lựa chọn", touchpoint="Website", sentiment="uncertain"; trial "Dùng thử" '
            'với stage_order=3, action="Tạo diagram đầu tiên", touchpoint="Product", sentiment="hopeful"; '
            'adopt "Áp dụng" với stage_order=4, action="Đưa vào công việc", touchpoint="Workspace", '
            'sentiment="confident"; renew "Gia hạn" với stage_order=5, action="Đánh giá giá trị", '
            'touchpoint="Account", sentiment="satisfied". Không có edge.'
        )
        stages = (
            ("discover", "Khám phá", 1, "Tìm giải pháp", "Search", "curious"),
            ("compare", "So sánh", 2, "Đối chiếu lựa chọn", "Website", "uncertain"),
            ("trial", "Dùng thử", 3, "Tạo diagram đầu tiên", "Product", "hopeful"),
            ("adopt", "Áp dụng", 4, "Đưa vào công việc", "Workspace", "confident"),
            ("renew", "Gia hạn", 5, "Đánh giá giá trị", "Account", "satisfied"),
        )
        nodes = [
            {
                "id": node_id,
                "role": "stage",
                "label": label,
                "journey": {
                    "stage_order": order,
                    "action": action,
                    "touchpoint": touchpoint,
                    "sentiment": sentiment,
                },
            }
            for node_id, label, order, action, touchpoint, sentiment in stages
        ]
        job = {
            "job_version": "2.1",
            "instruction": prompt,
            "title": "Khám phá · So sánh · Dùng thử · Áp dụng · Gia hạn",
            "diagram_type": "user-journey",
            "structural_profile": "work-experience",
            "visual_mode": "neutral-dark",
            "nodes": nodes,
            "groups": [],
            "lanes": [],
            "series": [],
            "axes": [],
            "annotations": [],
            "relation_groups": [],
            "source_assertions": {
                "node_ids": [item[0] for item in stages],
                "edge_assertions": [],
                "group_members": {},
                "lane_members": {},
                "node_member_ids": {},
                "series_data_ids": {},
                "axis_ids": [],
                "annotation_ids": [],
            },
            "expected_counts": {
                "nodes": 5,
                "edges": 0,
                "groups": 0,
                "lanes": 0,
                "series": 0,
                "axes": 0,
                "annotations": 0,
                "directed_edges": 0,
            },
        }
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            contract_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--print-job-contract"],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(contract_result.returncode, 0, contract_result.stderr)
            sentiment_contract = json.loads(contract_result.stdout)["collection_schema"]["$defs"]["journey"]["properties"]["sentiment"]
            self.assertEqual(set(sentiment_contract["type"]), {"number", "string", "null"})

            job_path = root / "r08.json"
            output_path = root / "r08-output"
            job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(job_path), "--output-dir", str(output_path)],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            ledger = json.loads((output_path / "diagram.ledger.json").read_text(encoding="utf-8"))
            svg = ET.fromstring((output_path / "diagram.svg").read_text(encoding="utf-8"))

        expected = {
            node_id: (order, action, touchpoint, sentiment)
            for node_id, _label, order, action, touchpoint, sentiment in stages
        }
        observed = {
            node["id"]: (
                node["journey"]["stage_order"],
                node["journey"]["action"],
                node["journey"]["touchpoint"],
                node["journey"]["sentiment"],
            )
            for node in ledger["semantic_snapshot"]["nodes"]
        }
        self.assertEqual(observed, expected)
        self.assertTrue(all("state" not in node for node in ledger["semantic_snapshot"]["nodes"]))
        rendered_nodes = {
            element.get("data-node-id"): element
            for element in svg.iter()
            if element.get("data-node-id")
        }
        for node_id, (_order, _action, _touchpoint, sentiment) in expected.items():
            self.assertEqual(rendered_nodes[node_id].get("data-journey-sentiment"), sentiment)
        visible_text = " ".join(element.text or "" for element in svg.iter() if element.tag.rsplit("}", 1)[-1] == "text")
        for sentiment in ("curious", "uncertain", "hopeful", "confident", "satisfied"):
            self.assertIn(f"sentiment {sentiment}", visible_text)

    def test_r11_database_column_types_are_contract_required_and_preserved(self) -> None:
        prompt = (
            'Dùng Thien-Skill-Creative-Diagram để tạo một SVG tĩnh bằng public one-call workflow. '
            'Chọn structural profile "compartment-model", visual mode "neutral-dark" và structural_override "none". '
            'Giữ nguyên toàn bộ ID, nhãn, thứ tự, nhóm, giá trị và quan hệ được nêu. Không thêm hoặc suy diễn quan hệ khác.\n'
            'Có 3 table node. customer "Customer" có member customer-id "customer_id UUID PK NOT NULL" và '
            'customer-email "email TEXT UNIQUE NOT NULL". sales-order "Sales Order" có member order-id '
            '"order_id UUID PK NOT NULL", order-customer-id "customer_id UUID FK NOT NULL" và order-total '
            '"total DECIMAL NOT NULL". payment "Payment" có member payment-id "payment_id UUID PK NOT NULL", '
            'payment-order-id "order_id UUID FK NOT NULL" và payment-amount "amount DECIMAL NOT NULL". '
            'Tạo foreign-key edge từ sales-order member order-customer-id đến customer member customer-id. '
            'Tạo foreign-key edge từ payment member payment-order-id đến sales-order member order-id.'
        )
        members_by_node = {
            "customer": [
                ("customer-id", "customer_id UUID PK NOT NULL", "UUID"),
                ("customer-email", "email TEXT UNIQUE NOT NULL", "TEXT"),
            ],
            "sales-order": [
                ("order-id", "order_id UUID PK NOT NULL", "UUID"),
                ("order-customer-id", "customer_id UUID FK NOT NULL", "UUID"),
                ("order-total", "total DECIMAL NOT NULL", "DECIMAL"),
            ],
            "payment": [
                ("payment-id", "payment_id UUID PK NOT NULL", "UUID"),
                ("payment-order-id", "order_id UUID FK NOT NULL", "UUID"),
                ("payment-amount", "amount DECIMAL NOT NULL", "DECIMAL"),
            ],
        }
        node_labels = {"customer": "Customer", "sales-order": "Sales Order", "payment": "Payment"}
        nodes = [
            {
                "id": node_id,
                "role": "table",
                "label": node_labels[node_id],
                "members": [
                    {"id": member_id, "kind": "column", "name": label, "data_type": data_type}
                    for member_id, label, data_type in members
                ],
            }
            for node_id, members in members_by_node.items()
        ]
        job = {
            "job_version": "2.1",
            "instruction": prompt,
            "title": "Customer · Sales Order · Payment",
            "diagram_type": "database-schema",
            "structural_profile": "compartment-model",
            "visual_mode": "neutral-dark",
            "nodes": nodes,
            "groups": [],
            "lanes": [],
            "series": [],
            "axes": [],
            "annotations": [],
            "relation_groups": [
                {
                    "id_prefix": "sales-order-customer-fk",
                    "sources": ["sales-order"],
                    "targets": ["customer"],
                    "kind": "foreign-key",
                    "directed": True,
                    "relation_kind": "foreign-key",
                    "source_member": "order-customer-id",
                    "target_member": "customer-id",
                },
                {
                    "id_prefix": "payment-sales-order-fk",
                    "sources": ["payment"],
                    "targets": ["sales-order"],
                    "kind": "foreign-key",
                    "directed": True,
                    "relation_kind": "foreign-key",
                    "source_member": "payment-order-id",
                    "target_member": "order-id",
                },
            ],
            "source_assertions": {
                "node_ids": list(members_by_node),
                "edge_assertions": [
                    {
                        "source": "sales-order",
                        "target": "customer",
                        "kind": "foreign-key",
                        "directed": True,
                        "source_quote": "Tạo foreign-key edge từ sales-order member order-customer-id đến customer member customer-id.",
                    },
                    {
                        "source": "payment",
                        "target": "sales-order",
                        "kind": "foreign-key",
                        "directed": True,
                        "source_quote": "Tạo foreign-key edge từ payment member payment-order-id đến sales-order member order-id.",
                    },
                ],
                "group_members": {},
                "lane_members": {},
                "node_member_ids": {
                    node_id: [member_id for member_id, _label, _data_type in members]
                    for node_id, members in members_by_node.items()
                },
                "series_data_ids": {},
                "axis_ids": [],
                "annotation_ids": [],
            },
            "expected_counts": {
                "nodes": 3,
                "edges": 2,
                "groups": 0,
                "lanes": 0,
                "series": 0,
                "axes": 0,
                "annotations": 0,
                "directed_edges": 2,
            },
        }
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            contract_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--print-job-contract"],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(contract_result.returncode, 0, contract_result.stderr)
            member_contract = json.loads(contract_result.stdout)["collection_schema"]["$defs"]["member"]
            column_contract = next(
                rule for rule in member_contract["allOf"]
                if rule.get("if", {}).get("properties", {}).get("kind", {}).get("const") == "column"
            )
            self.assertEqual(column_contract["then"]["required"], ["data_type"])
            self.assertEqual(column_contract["then"]["properties"]["data_type"]["type"], "string")

            job_path = root / "r11.json"
            output_path = root / "r11-output"
            job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(job_path), "--output-dir", str(output_path)],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            ledger = json.loads((output_path / "diagram.ledger.json").read_text(encoding="utf-8"))
            svg = ET.fromstring((output_path / "diagram.svg").read_text(encoding="utf-8"))

        expected = {
            member_id: (label, data_type)
            for members in members_by_node.values()
            for member_id, label, data_type in members
        }
        observed = {
            member["id"]: (member["name"], member["data_type"])
            for node in ledger["semantic_snapshot"]["nodes"]
            for member in node["members"]
        }
        self.assertEqual(observed, expected)
        visible_text = {element.text for element in svg.iter() if element.tag.rsplit("}", 1)[-1] == "text"}
        self.assertTrue({label for label, _data_type in expected.values()} <= visible_text)

    def test_profile_job_cli_rejects_oversized_input_before_reading_payload(self) -> None:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            oversized = root / "oversized.json"
            with oversized.open("wb") as stream:
                stream.seek(2 * 1024 * 1024)
                stream.write(b"x")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(oversized), "--output-dir", str(root / "out")],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(completed.returncode, 2)
        report = json.loads(completed.stderr)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["issue"]["code"], "profile-job-input-invalid")

    def test_profile_job_cli_rejects_non_utf8_and_fifo_inputs_without_blocking(self) -> None:
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            utf16 = root / "utf16.json"
            utf16.write_bytes("{}".encode("utf-16"))
            utf16_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(utf16), "--output-dir", str(root / "utf16-out")],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=2,
            )
            fifo = root / "job.fifo"
            os.mkfifo(fifo)
            fifo_result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(fifo), "--output-dir", str(root / "fifo-out")],
                cwd=root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=2,
            )
        self.assertEqual(json.loads(utf16_result.stderr)["issue"]["code"], "profile-job-json-invalid")
        self.assertEqual(json.loads(fifo_result.stderr)["issue"]["code"], "profile-job-input-invalid")

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
