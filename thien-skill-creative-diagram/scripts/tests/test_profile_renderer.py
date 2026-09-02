from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.insert(0, str(TEST_DIR))

from diagram_core import canonical_json
from output_pipeline import OutputFailure, create_profiled_diagram, create_profiled_diagram_from_job
from profile_renderer import ENGINE_PRIMITIVES, ENGINE_RENDERERS, ProfileRenderError, _validate_edge_collision_graph, validate_rendered_geometry
from semantic_fixtures import axis, datum, e, finalize, fixtures, g, n, series, variant_fixtures, xy_datum
from structural_profiles import build_profiled_plan, load_profile_registry


SVG_NS = "http://www.w3.org/2000/svg"


def request(diagram_type: str, profile: str, *, mode: str = "neutral-light", variant_ids: list[str] | None = None, size: str = "fit") -> dict[str, object]:
    return {
        "instruction": "Create a source-faithful diagram.",
        "source": {"kind": "natural-language", "content": "Validated fixture data."},
        "diagram_type": diagram_type,
        "variant_ids": list(variant_ids or []),
        "structural_profile": profile,
        "structural_override": {"status": "none"},
        "size": size,
        "detail": "faithful",
        "audience": "mixed",
        "visual_mode": mode,
        "language": {"mode": "explicit", "tag": "vi"},
        "format": "svg",
        "motion": "none",
    }


def case_for_profile(profile: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    parent = str(profile["canonical_parent"])
    if profile["profile_class"] == "capability":
        capability = str(profile["capability_id"])
        ir = variant_fixtures()[capability]
        return ir, request(parent, str(profile["profile_id"]), variant_ids=[capability])
    return fixtures()[parent], request(parent, str(profile["profile_id"]))


def dense_topology_ir() -> dict[str, object]:
    return finalize(
        "architecture",
        nodes=[
            n("customer", "actor", "Khách hàng"),
            n("waf", "service", "WAF"),
            n("gateway", "service", "API Gateway"),
            n("identity", "service", "Identity"),
            n("order", "service", "Order"),
            n("payment", "service", "Payment"),
            n("transaction-db", "store", "Transaction DB"),
            n("log-store", "store", "Log Store"),
        ],
        groups=[
            g("public-edge", "Biên công khai", ["waf", "gateway"]),
            g("private-services", "Dịch vụ riêng", ["identity", "order", "payment"]),
            g("data-zone", "Dữ liệu", ["transaction-db", "log-store"]),
        ],
        edges=[
            e("customer-waf", "customer", "waf", "request"),
            e("waf-gateway", "waf", "gateway", "request"),
            e("gateway-identity", "gateway", "identity", "request"),
            e("gateway-order", "gateway", "order", "request"),
            e("gateway-payment", "gateway", "payment", "request"),
            e("order-db", "order", "transaction-db", "write"),
            e("payment-db", "payment", "transaction-db", "write"),
            e("identity-log", "identity", "log-store", "log"),
            e("order-log", "order", "log-store", "log"),
            e("payment-log", "payment", "log-store", "log"),
        ],
    )


def phase7_b3_frozen_case_shapes() -> list[tuple[str, dict[str, object], dict[str, object]]]:
    """Return the exact semantic shapes behind F-007 without persisting case artifacts."""

    swimlane = finalize(
        "swimlane",
        nodes=[n(item_id, "activity", label) for item_id, label in (
            ("submit", "Gửi yêu cầu"), ("validate", "Kiểm tra dữ liệu"),
            ("clarify", "Làm rõ thông tin"), ("approve", "Phê duyệt"),
            ("provision", "Cấp quyền"), ("notify", "Thông báo"), ("close", "Đóng yêu cầu"),
        )],
        lanes=[
            {"id": "requester", "label": "Người yêu cầu", "owner": "Người yêu cầu", "member_ids": ["submit", "clarify"], "order": 0},
            {"id": "control", "label": "Kiểm soát", "owner": "Kiểm soát", "member_ids": ["validate", "approve"], "order": 1},
            {"id": "operations", "label": "Vận hành", "owner": "Vận hành", "member_ids": ["provision", "notify", "close"], "order": 2},
        ],
        edges=[
            e(f"handoff-{order}", source, target, "handoff", order=order)
            for order, (source, target) in enumerate((
                ("submit", "validate"), ("validate", "clarify"), ("clarify", "approve"),
                ("approve", "provision"), ("provision", "notify"), ("notify", "close"),
            ), 1)
        ],
    )
    journey = finalize(
        "user-journey",
        nodes=[
            n(item_id, "stage", label, journey={"stage_order": order, "action": action, "touchpoint": touchpoint, "sentiment": sentiment})
            for item_id, label, order, action, touchpoint, sentiment in (
                ("discover", "Khám phá", 1, "Tìm giải pháp", "Search", 0.2),
                ("compare", "So sánh", 2, "Đối chiếu lựa chọn", "Website", -0.2),
                ("trial", "Dùng thử", 3, "Tạo diagram đầu tiên", "Product", 0.4),
                ("adopt", "Áp dụng", 4, "Đưa vào công việc", "Workspace", 0.7),
                ("renew", "Gia hạn", 5, "Đánh giá giá trị", "Account", 0.8),
            )
        ],
    )
    hierarchy = finalize(
        "org-chart",
        nodes=[n(item_id, "role", label) for item_id, label in (
            ("ceo", "CEO"), ("cto", "CTO"), ("coo", "COO"),
            ("engineering", "Engineering Lead"), ("data", "Data Lead"),
            ("operations", "Operations Lead"), ("support", "Support Lead"),
        )],
        edges=[
            e(f"reports-{employee}-{manager}", employee, manager, "reports-to")
            for employee, manager in (
                ("cto", "ceo"), ("coo", "ceo"), ("engineering", "cto"),
                ("data", "cto"), ("operations", "coo"), ("support", "coo"),
            )
        ],
    )
    funnel = finalize(
        "pyramid-funnel",
        series=[series("funnel", "Pipeline bán hàng", [
            datum("visitors", "Khách truy cập", 10000, label="Khách truy cập"),
            datum("signups", "Đăng ký", 4200, label="Đăng ký"),
            datum("trials", "Dùng thử", 1600, label="Dùng thử"),
            datum("paid", "Trả phí", 620, label="Trả phí"),
        ], "khách hàng")],
    )
    quadrant = finalize(
        "quadrant",
        series=[series("initiatives", "Sáng kiến", [
            datum("automate", 8, 9, label="Tự động hóa"), datum("training", 3, 8, label="Đào tạo"),
            datum("analytics", 7, 4, label="Phân tích"), datum("archive", 2, 2, label="Lưu trữ"),
        ])],
        axes=[axis("impact", "x", "linear", "Tác động", domain_min=0, domain_max=10), axis("urgency", "y", "linear", "Khẩn cấp", domain_min=0, domain_max=10)],
    )
    quantitative = finalize(
        "scatter-plot",
        series=[
            series("core", "Core", [datum("core-a", 1, 3, label="A"), datum("core-b", 4, 6, label="B"), datum("core-c", 8, 7, label="C")]),
            series("growth", "Growth", [datum("growth-a", 2, 8, label="D"), datum("growth-b", 6, 4, label="E"), datum("growth-c", 9, 9, label="F")]),
        ],
        axes=[axis("effort", "x", "linear", "Nỗ lực", domain_min=0, domain_max=10), axis("return", "y", "linear", "Lợi ích", domain_min=0, domain_max=10)],
    )
    dumbbell = finalize(
        "bar-chart",
        series=[
            series("before", "Trước", [datum("before-speed", "Tốc độ", 42), datum("before-quality", "Chất lượng", 68), datum("before-cost", "Chi phí", 74)]),
            series("after", "Sau", [datum("after-speed", "Tốc độ", 71), datum("after-quality", "Chất lượng", 86), datum("after-cost", "Chi phí", 55)]),
        ],
        axes=[axis("metric", "x", "categorical", "Chỉ tiêu"), axis("score", "y", "linear", "Điểm", domain_min=0, domain_max=100)],
    )
    dumbbell["diagram"]["variant_ids"] = ["CAP-V17"]  # type: ignore[index]
    slope = finalize(
        "line-chart",
        series=[
            series("north", "Miền Bắc", [datum("north-before", "Before", 54), datum("north-after", "After", 72)]),
            series("central", "Miền Trung", [datum("central-before", "Before", 61), datum("central-after", "After", 58)]),
            series("south", "Miền Nam", [datum("south-before", "Before", 47), datum("south-after", "After", 69)]),
        ],
        axes=[axis("period", "x", "ordinal", "Kỳ"), axis("score", "y", "linear", "Điểm", domain_min=0, domain_max=100)],
    )
    slope["diagram"]["variant_ids"] = ["CAP-V18"]  # type: ignore[index]
    bubble = finalize(
        "scatter-plot",
        series=[
            series("existing", "Hiện hữu", [
                {**xy_datum("alpha", 2, 7, 20, "triệu USD"), "label": "Alpha"},
                {**xy_datum("beta", 6, 5, 80, "triệu USD"), "label": "Beta"},
            ]),
            series("new", "Mới", [
                {**xy_datum("gamma", 4, 9, 45, "triệu USD"), "label": "Gamma"},
                {**xy_datum("delta", 8, 3, 125, "triệu USD"), "label": "Delta"},
            ]),
        ],
        axes=[
            axis("risk", "x", "linear", "Rủi ro", domain_min=0, domain_max=10),
            axis("return", "y", "linear", "Lợi ích", domain_min=0, domain_max=10),
            axis("investment", "size", "linear", "Đầu tư", domain_min=0, domain_max=125, unit="triệu USD"),
        ],
    )
    bubble["diagram"]["variant_ids"] = ["CAP-V20"]  # type: ignore[index]
    layers = finalize(
        "layer-stack",
        nodes=[n(item_id, "control", label) for item_id, label in (
            ("experience", "Experience Layer"), ("service", "Service Layer"),
            ("domain", "Domain Layer"), ("infrastructure", "Infrastructure Layer"),
        )],
        lanes=[
            {"id": f"layer-{item_id}", "label": label, "owner": label, "member_ids": [item_id], "order": order}
            for order, (item_id, label) in enumerate((
                ("experience", "Experience"), ("service", "Service"),
                ("domain", "Domain"), ("infrastructure", "Infrastructure"),
            ))
        ],
    )
    scatter = finalize(
        "scatter-plot",
        series=[series("vendors", "Nhà cung cấp", [
            datum("vendor-a", 2, 8, label="A"), datum("vendor-b", 4, 6, label="B"),
            datum("vendor-c", 5, 3, label="C"), datum("vendor-d", 7, 7, label="D"), datum("vendor-e", 9, 4, label="E"),
        ])],
        axes=[axis("cost", "x", "linear", "Chi phí", domain_min=0, domain_max=10), axis("quality", "y", "linear", "Chất lượng", domain_min=0, domain_max=10)],
    )
    return [
        ("R06", request("swimlane", "lane-interaction", mode="editorial"), swimlane),
        ("R08", request("user-journey", "work-experience", mode="neutral-dark"), journey),
        ("R09", request("org-chart", "hierarchy", mode="editorial"), hierarchy),
        ("R10", request("pyramid-funnel", "containment-stack"), funnel),
        ("R12", request("quadrant", "spatial-matrix", mode="editorial"), quadrant),
        ("R13", request("scatter-plot", "quantitative"), quantitative),
        ("R15", request("bar-chart", "dumbbell", mode="editorial", variant_ids=["CAP-V17"]), dumbbell),
        ("R16", request("line-chart", "slope-graph", variant_ids=["CAP-V18"]), slope),
        ("R18", request("scatter-plot", "bubble", mode="editorial", variant_ids=["CAP-V20"]), bubble),
        ("R19", request("layer-stack", "layers"), layers),
        ("R20", request("scatter-plot", "scatter-chart", mode="neutral-dark"), scatter),
    ]


def dense_topology_job() -> dict[str, object]:
    instruction = (
        "Tạo sơ đồ kiến trúc topology-and-zones với tám node. Khách hàng đi qua WAF rồi API Gateway; "
        "Gateway gọi Identity, Order và Payment; Order và Payment ghi Transaction DB; "
        "Identity, Order và Payment ghi Log Store."
    )
    return {
        "job_version": "2.1",
        "instruction": instruction,
        "title": "Luồng dịch vụ và dữ liệu",
        "diagram_type": "architecture",
        "structural_profile": "topology-and-zones",
        "size": "social-square",
        "visual_mode": "neutral-light",
        "language": "vi",
        "nodes": [
            {"id": "customer", "role": "actor", "label": "Khách hàng"},
            {"id": "waf", "role": "service", "label": "WAF"},
            {"id": "gateway", "role": "service", "label": "API Gateway"},
            {"id": "identity", "role": "service", "label": "Identity"},
            {"id": "order", "role": "service", "label": "Order"},
            {"id": "payment", "role": "service", "label": "Payment"},
            {"id": "transaction-db", "role": "data-store", "label": "Transaction DB"},
            {"id": "log-store", "role": "data-store", "label": "Log Store"},
        ],
        "source_assertions": {
            "node_ids": ["customer", "waf", "gateway", "identity", "order", "payment", "transaction-db", "log-store"],
            "edge_assertions": [
                {"source": "customer", "target": "waf", "kind": "request", "directed": True, "source_quote": "Khách hàng đi qua WAF rồi API Gateway"},
                {"source": "waf", "target": "gateway", "kind": "request", "directed": True, "source_quote": "Khách hàng đi qua WAF rồi API Gateway"},
                {"source": "gateway", "target": "identity", "kind": "request", "directed": True, "source_quote": "Gateway gọi Identity, Order và Payment"},
                {"source": "gateway", "target": "order", "kind": "request", "directed": True, "source_quote": "Gateway gọi Identity, Order và Payment"},
                {"source": "gateway", "target": "payment", "kind": "request", "directed": True, "source_quote": "Gateway gọi Identity, Order và Payment"},
                {"source": "order", "target": "transaction-db", "kind": "write", "directed": True, "source_quote": "Order và Payment ghi Transaction DB"},
                {"source": "payment", "target": "transaction-db", "kind": "write", "directed": True, "source_quote": "Order và Payment ghi Transaction DB"},
                {"source": "identity", "target": "log-store", "kind": "log", "directed": True, "source_quote": "Identity, Order và Payment ghi Log Store"},
                {"source": "order", "target": "log-store", "kind": "log", "directed": True, "source_quote": "Identity, Order và Payment ghi Log Store"},
                {"source": "payment", "target": "log-store", "kind": "log", "directed": True, "source_quote": "Identity, Order và Payment ghi Log Store"},
            ],
            "group_members": {
                "public-edge": ["waf", "gateway"],
                "private-services": ["identity", "order", "payment"],
                "data-zone": ["transaction-db", "log-store"],
            },
            "lane_members": {},
            "node_member_ids": {},
            "series_data_ids": {},
            "axis_ids": [],
            "annotation_ids": [],
        },
        "relation_groups": [
            {"id_prefix": "customer-waf", "sources": ["customer"], "targets": ["waf"], "kind": "request", "directed": True},
            {"id_prefix": "waf-gateway", "sources": ["waf"], "targets": ["gateway"], "kind": "request", "directed": True},
            {"id_prefix": "gateway-call", "sources": ["gateway"], "targets": ["identity", "order", "payment"], "kind": "request", "directed": True},
            {"id_prefix": "transaction-write", "sources": ["order", "payment"], "targets": ["transaction-db"], "kind": "write", "directed": True},
            {"id_prefix": "log-write", "sources": ["identity", "order", "payment"], "targets": ["log-store"], "kind": "log", "directed": True},
        ],
        "groups": [
            {"id": "public-edge", "label": "Biên công khai", "member_ids": ["waf", "gateway"]},
            {"id": "private-services", "label": "Dịch vụ riêng", "member_ids": ["identity", "order", "payment"]},
            {"id": "data-zone", "label": "Dữ liệu", "member_ids": ["transaction-db", "log-store"]},
        ],
        "expected_counts": {
            "nodes": 8,
            "edges": 10,
            "directed_edges": 10,
            "groups": 3,
            "lanes": 0,
            "series": 0,
            "axes": 0,
            "annotations": 0,
        },
    }


def ordered_sequence_job() -> dict[str, object]:
    instruction = "Ứng dụng gửi yêu cầu tới API; API trả phản hồi cho Ứng dụng."
    return {
        "job_version": "2.1",
        "instruction": instruction,
        "title": "Trao đổi API",
        "diagram_type": "sequence",
        "structural_profile": "type-sequence",
        "language": "vi",
        "nodes": [
            {"id": "app", "role": "participant", "label": "Ứng dụng"},
            {"id": "api", "role": "participant", "label": "API"},
        ],
        "source_assertions": {
            "node_ids": ["app", "api"],
            "edge_assertions": [
                {"source": "app", "target": "api", "kind": "request", "directed": True, "source_quote": "Ứng dụng gửi yêu cầu tới API"},
                {"source": "api", "target": "app", "kind": "response", "directed": True, "source_quote": "API trả phản hồi cho Ứng dụng"},
            ],
            "group_members": {},
            "lane_members": {},
            "node_member_ids": {},
            "series_data_ids": {},
            "axis_ids": [],
            "annotation_ids": [],
        },
        "relation_groups": [
            {"id_prefix": "request", "sources": ["app"], "targets": ["api"], "kind": "request", "directed": True, "order": 0},
            {"id_prefix": "response", "sources": ["api"], "targets": ["app"], "kind": "response", "directed": True, "order": 1},
        ],
        "expected_counts": {
            "nodes": 2,
            "edges": 2,
            "directed_edges": 2,
            "groups": 0,
            "lanes": 0,
            "series": 0,
            "axes": 0,
            "annotations": 0,
        },
    }


def bar_profile_job() -> dict[str, object]:
    return {
        "job_version": "2.1",
        "instruction": "Vẽ doanh số: Quý 1 là 12 tỷ đồng và Quý 2 là 18 tỷ đồng.",
        "title": "Doanh số theo quý",
        "diagram_type": "bar-chart",
        "structural_profile": "type-bar-chart",
        "size": "doc-wide",
        "visual_mode": "editorial",
        "language": "vi",
        "nodes": [],
        "edges": [],
        "groups": [],
        "lanes": [],
        "series": [
            {
                "id": "sales",
                "label": "Doanh số",
                "unit": "tỷ đồng",
                "data": [
                    {"id": "sales-q1", "domain": "Quý 1", "value": 12, "missing": False},
                    {"id": "sales-q2", "domain": "Quý 2", "value": 18, "missing": False},
                ],
            }
        ],
        "axes": [
            {"id": "quarter-axis", "dimension": "x", "scale": "categorical", "label": "Quý"},
            {"id": "sales-axis", "dimension": "y", "scale": "linear", "label": "Doanh số", "domain_min": 0, "domain_max": 20, "unit": "tỷ đồng"},
        ],
        "annotations": [],
        "source_assertions": {
            "node_ids": [],
            "edge_assertions": [],
            "group_members": {},
            "lane_members": {},
            "node_member_ids": {},
            "series_data_ids": {"sales": ["sales-q1", "sales-q2"]},
            "axis_ids": ["quarter-axis", "sales-axis"],
            "annotation_ids": [],
        },
        "relation_groups": [],
        "expected_counts": {
            "nodes": 0,
            "edges": 0,
            "directed_edges": 0,
            "groups": 0,
            "lanes": 0,
            "series": 1,
            "axes": 2,
            "annotations": 0,
        },
    }


def dense_request_and_receipt(ir: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    job = dense_topology_job()
    raw_request = request("architecture", "topology-and-zones", size="social-square")
    raw_request["instruction"] = job["instruction"]
    raw_request["source"] = {"kind": "natural-language", "content": raw_request["instruction"]}
    source_assertions = job["source_assertions"]
    receipt = {
        "schema_version": "1.2",
        "source_instruction_sha256": hashlib.sha256(raw_request["instruction"].encode("utf-8")).hexdigest(),
        "source_assertions_sha256": hashlib.sha256(canonical_json(source_assertions).encode("utf-8")).hexdigest(),
        "source_assertions": source_assertions,
        "node_ids": sorted(node["id"] for node in ir["nodes"]),
        "edges": sorted(
            (
                {
                    "id": edge["id"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "kind": edge["kind"],
                    "directed": edge["directed"],
                }
                for edge in ir["edges"]
            ),
            key=lambda edge: edge["id"],
        ),
        "group_members": {group["id"]: sorted(group["member_ids"]) for group in ir["groups"]},
    }
    return raw_request, receipt


class ProfileRendererCoverageTests(unittest.TestCase):
    def test_exact_14_engine_dispatch_has_no_generic_fallback(self) -> None:
        self.assertEqual(set(ENGINE_RENDERERS), set(ENGINE_PRIMITIVES))
        self.assertEqual(len(ENGINE_RENDERERS), 14)
        self.assertEqual(len(set(ENGINE_RENDERERS.values())), 14)
        self.assertEqual(len(set(ENGINE_PRIMITIVES.values())), 14)

    def test_all_45_profiles_render_their_bound_engine_and_exact_pair(self) -> None:
        registry = load_profile_registry()
        observed_profiles: set[str] = set()
        observed_engines: set[str] = set()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, profile in enumerate(registry["profiles"]):
                with self.subTest(profile=profile["profile_id"]):
                    ir, raw_request = case_for_profile(profile)
                    result = create_profiled_diagram(raw_request, ir, root / f"case-{index:02d}")
                    observed_profiles.add(result.selected_profile)
                    observed_engines.add(result.layout_engine)
                    output = Path(result.output_dir)
                    self.assertEqual({item.name for item in output.iterdir()}, {"diagram.svg", "diagram.ledger.json"})
                    svg = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
                    self.assertEqual(svg.get("data-selected-profile"), profile["profile_id"])
                    self.assertEqual(svg.get("data-layout-engine"), profile["layout_engine"])
                    self.assertTrue(any(element.get("data-primitive") == ENGINE_PRIMITIVES[str(profile["layout_engine"])] for element in svg.iter()))
                    ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
                    self.assertEqual(ledger["renderer_version"], "profile-renderer-2.1.0")
                    self.assertEqual(ledger["structural_conformance"], "pass")
                    self.assertEqual(ledger["geometry_validation"]["status"], "pass")
            self.assertEqual(len(observed_profiles), 45)
            self.assertEqual(observed_engines, set(ENGINE_RENDERERS))

    def test_three_equal_modes_keep_identical_layout_geometry(self) -> None:
        ir = fixtures()["architecture"]
        hashes = []
        contents = []
        with tempfile.TemporaryDirectory() as temporary:
            for mode in ("neutral-light", "neutral-dark", "editorial"):
                result = create_profiled_diagram(request("architecture", "topology-and-zones", mode=mode), ir, Path(temporary) / mode)
                root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
                hashes.append(root.get("data-layout-sha256"))
                contents.append(Path(result.svg_path).read_bytes())
        self.assertEqual(len(set(hashes)), 1)
        self.assertEqual(len(set(contents)), 3)

    def test_internal_profile_identity_is_not_printed_in_visible_svg_text(self) -> None:
        ir = fixtures()["architecture"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(request("architecture", "topology-and-zones"), ir, Path(temporary) / "diagram")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        visible_text = " ".join((element.text or "") for element in root.iter() if element.tag == f"{{{SVG_NS}}}text")
        self.assertNotIn("topology-and-zones", visible_text)
        self.assertNotIn("rendered by", visible_text)

    def test_canvas_reflow_preserves_profile_and_semantic_ids(self) -> None:
        ir = fixtures()["architecture"]
        with tempfile.TemporaryDirectory() as temporary:
            roots = []
            for size in ("social-square", "slide-16x9", "print-letter-landscape"):
                result = create_profiled_diagram(request("architecture", "topology-and-zones", size=size), ir, Path(temporary) / size)
                roots.append(ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8")))
        for root in roots:
            self.assertEqual(root.get("data-selected-profile"), "topology-and-zones")
            self.assertEqual({element.get("data-node-id") for element in root.iter() if element.get("data-node-id")}, {"actor-user", "service-api"})
        self.assertEqual(len({root.get("viewBox") for root in roots}), 3)

    def test_phase7_b3_frozen_shapes_use_one_square_fit_safe_area_without_right_overflow(self) -> None:
        expected_profiles = {
            "R06": "lane-interaction", "R08": "work-experience", "R09": "hierarchy",
            "R10": "containment-stack", "R12": "spatial-matrix", "R13": "quantitative",
            "R15": "dumbbell", "R16": "slope-graph", "R18": "bubble",
            "R19": "layers", "R20": "scatter-chart",
        }
        with tempfile.TemporaryDirectory() as temporary:
            for case_id, raw_request, ir in phase7_b3_frozen_case_shapes():
                with self.subTest(case_id=case_id):
                    result = create_profiled_diagram(raw_request, ir, Path(temporary) / case_id)
                    root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
                    ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
                    self.assertEqual(root.get("data-selected-profile"), expected_profiles[case_id])
                    self.assertEqual(root.get("viewBox"), "0 0 1600 1600")
                    self.assertEqual(root.get("preserveAspectRatio"), "xMidYMid meet")
                    self.assertEqual((root.get("width"), root.get("height")), ("1600", "1600"))
                    self.assertEqual(
                        ledger["geometry_validation"]["canvas"],
                        {
                            "width": 1600.0,
                            "height": 1600.0,
                            "preserve_aspect_ratio": "xMidYMid meet",
                            "bounded_receipts": ledger["geometry_validation"]["canvas"]["bounded_receipts"],
                            "overflow": 0,
                        },
                    )
                    self.assertGreater(ledger["geometry_validation"]["canvas"]["bounded_receipts"], 0)
                    for element in root.iter():
                        if all(field in element.attrib for field in ("data-x", "data-w")):
                            self.assertLessEqual(float(element.get("data-x", "0")) + float(element.get("data-w", "0")), 1600.0)
                        if element.tag == f"{{{SVG_NS}}}polyline" and element.get("points"):
                            self.assertTrue(all(float(pair.split(",", 1)[0]) <= 1600.0 for pair in element.get("points", "").split()))


class GeometryAndAtomicityTests(unittest.TestCase):
    def test_profile_job_cli_runs_from_unrelated_cwd_without_custom_driver(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            job_path = root / "job.json"
            output_path = root / "out"
            job_path.write_text(json.dumps(dense_topology_job(), ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "output_pipeline.py"), "--job", str(job_path), "--output-dir", str(output_path)],
                cwd=root,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual({item.name for item in output_path.iterdir()}, {"diagram.svg", "diagram.ledger.json"})
            ledger = json.loads((output_path / "diagram.ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["geometry_validation"]["edges"], 10)
            self.assertEqual(ledger["semantic_coverage"], "pass")
            self.assertEqual(ledger["semantic_coverage_scope"], "declared-source-assertions-to-validated-ir")
            self.assertEqual(ledger["source_interpretation_attestation"], "agent-authored-not-independently-proven")

    def test_profile_job_expands_coordinated_relations_to_exact_ten_edge_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram_from_job(dense_topology_job(), Path(temporary) / "dense-job")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        observed_edges = {
            (element.get("data-source"), element.get("data-target"))
            for element in root.iter()
            if element.get("data-edge-id")
        }
        self.assertEqual(
            observed_edges,
            {
                ("customer", "waf"),
                ("waf", "gateway"),
                ("gateway", "identity"),
                ("gateway", "order"),
                ("gateway", "payment"),
                ("order", "transaction-db"),
                ("payment", "transaction-db"),
                ("identity", "log-store"),
                ("order", "log-store"),
                ("payment", "log-store"),
            },
        )
        self.assertEqual(ledger["geometry_validation"]["edges"], 10)
        self.assertEqual(ledger["semantic_coverage"], "pass")
        self.assertRegex(ledger["semantic_receipt_sha256"], r"^[a-f0-9]{64}$")
        self.assertRegex(ledger["source_assertions_sha256"], r"^[a-f0-9]{64}$")

    def test_profiled_ledger_and_svg_embed_the_same_exact_semantic_snapshot(self) -> None:
        ir = fixtures()["database-schema"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("database-schema", "compartment-model"),
                ir,
                Path(temporary) / "snapshot",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        metadata = [
            element
            for element in root.iter()
            if element.tag == f"{{{SVG_NS}}}metadata" and element.get("data-kind") == "exact-semantics"
        ]
        self.assertEqual(len(metadata), 1)
        svg_snapshot = json.loads(metadata[0].text or "null")
        self.assertEqual(svg_snapshot, ledger["semantic_snapshot"])
        self.assertEqual(
            ledger["semantic_snapshot_sha256"],
            hashlib.sha256(canonical_json(svg_snapshot).encode("utf-8")).hexdigest(),
        )
        self.assertEqual(
            set(svg_snapshot),
            {"diagram", "nodes", "edges", "groups", "lanes", "series", "axes", "annotations"},
        )

        def contains_source_refs(value: object) -> bool:
            if isinstance(value, dict):
                return "source_refs" in value or any(contains_source_refs(item) for item in value.values())
            if isinstance(value, list):
                return any(contains_source_refs(item) for item in value)
            return False

        self.assertFalse(contains_source_refs(svg_snapshot))
        self.assertTrue(contains_source_refs(ir))

    def test_grouped_bar_renders_every_series_datum_once_on_the_declared_scale(self) -> None:
        job = bar_profile_job()
        job["series"].append(
            {
                "id": "cost",
                "label": "Chi phí",
                "unit": "tỷ đồng",
                "data": [
                    {"id": "cost-q1", "domain": "Quý 1", "value": 8, "missing": False},
                    {"id": "cost-q2", "domain": "Quý 2", "value": 20, "missing": False},
                ],
            }
        )
        job["source_assertions"]["series_data_ids"]["cost"] = ["cost-q1", "cost-q2"]
        job["expected_counts"]["series"] = 2
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram_from_job(job, Path(temporary) / "grouped-bar")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        bars = [element for element in root.iter() if element.get("data-mark") == "bar"]
        self.assertEqual(
            {element.get("data-semantic-id") for element in bars},
            {"sales-q1", "sales-q2", "cost-q1", "cost-q2"},
        )
        self.assertEqual(len(bars), 4)
        self.assertEqual({element.get("data-series-id") for element in bars}, {"sales", "cost"})
        scale = next(element for element in root.iter() if element.get("data-axis-id") == "sales-axis")
        self.assertEqual(
            {key: scale.get(key) for key in ("data-axis-dimension", "data-axis-scale", "data-axis-domain-min", "data-axis-domain-max", "data-axis-unit")},
            {
                "data-axis-dimension": "y",
                "data-axis-scale": "linear",
                "data-axis-domain-min": "0",
                "data-axis-domain-max": "20",
                "data-axis-unit": "tỷ đồng",
            },
        )
        height_per_unit = {
            round(float(element.get("height", "0")) / float(element.get("data-value", "1")), 8)
            for element in bars
        }
        self.assertEqual(len(height_per_unit), 1)
        self.assertEqual(ledger["geometry_validation"]["marks"], 4)

    def test_reports_to_ranks_manager_above_subordinate_without_reversing_edge_semantics(self) -> None:
        ir = fixtures()["org-chart"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("org-chart", "hierarchy"),
                ir,
                Path(temporary) / "hierarchy",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        nodes = {
            element.get("data-node-id"): element
            for element in root.iter()
            if element.get("data-node-id")
        }
        subordinate = nodes["role-manager"]
        manager = nodes["role-director"]
        subordinate_center = float(subordinate.get("data-y", "0")) + float(subordinate.get("data-h", "0")) / 2
        manager_center = float(manager.get("data-y", "0")) + float(manager.get("data-h", "0")) / 2
        self.assertLess(manager_center, subordinate_center)
        edge = next(element for element in root.iter() if element.get("data-edge-id") == "reporting-line")
        self.assertEqual(edge.get("data-source"), "role-manager")
        self.assertEqual(edge.get("data-target"), "role-director")
        self.assertEqual(edge.get("marker-end"), "url(#arrow)")

    def test_hierarchy_keeps_manager_families_together_without_shared_endpoint_stems(self) -> None:
        ir = finalize(
            "org-chart",
            nodes=[
                n("ceo", "role", "Tổng giám đốc"),
                n("ops-director", "role", "Giám đốc vận hành"),
                n("product-director", "role", "Giám đốc sản phẩm"),
                n("warehouse-lead", "role", "Trưởng kho"),
                n("design-lead", "role", "Trưởng thiết kế"),
                n("research-lead", "role", "Trưởng nghiên cứu"),
            ],
            edges=[
                e("ops-ceo", "ops-director", "ceo", "reports-to"),
                e("product-ceo", "product-director", "ceo", "reports-to"),
                e("warehouse-ops", "warehouse-lead", "ops-director", "reports-to"),
                e("design-product", "design-lead", "product-director", "reports-to"),
                e("research-product", "research-lead", "product-director", "reports-to"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("org-chart", "hierarchy"),
                ir,
                Path(temporary) / "hierarchy-families",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        nodes = {element.get("data-node-id"): element for element in root.iter() if element.get("data-node-id")}
        self.assertLess(float(nodes["warehouse-lead"].get("data-x", "0")), float(nodes["design-lead"].get("data-x", "0")))
        routes = [element.get("points", "").split() for element in root.iter() if element.get("data-edge-id")]
        self.assertTrue(all(all(left != right for left, right in zip(points, points[1:])) for points in routes))
        self.assertEqual(ledger["geometry_validation"]["collision_graph"]["shared_segments"], 0)
        self.assertEqual(ledger["geometry_validation"]["collision_graph"]["undeclared_junctions"], 0)

    def test_branching_tree_orders_interleaved_request_children_by_parent_family(self) -> None:
        ir = finalize(
            "tree",
            nodes=[
                n("root", "concept", "Root"),
                n("left", "concept", "Left"),
                n("right", "concept", "Right"),
                n("r1", "concept", "Right 1"),
                n("l1", "concept", "Left 1"),
                n("r2", "concept", "Right 2"),
                n("l2", "concept", "Left 2"),
            ],
            edges=[
                e("root-left", "root", "left", "parent"),
                e("root-right", "root", "right", "branch"),
                e("left-l1", "left", "l1", "branch"),
                e("left-l2", "left", "l2", "branch"),
                e("right-r1", "right", "r1", "branch"),
                e("right-r2", "right", "r2", "branch"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("tree", "type-tree"),
                ir,
                Path(temporary) / "branching-tree",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        nodes = {element.get("data-node-id"): element for element in root.iter() if element.get("data-node-id")}
        centers = {
            node_id: float(element.get("data-x", "0")) + float(element.get("data-w", "0")) / 2
            for node_id, element in nodes.items()
        }
        self.assertLess(max(centers["l1"], centers["l2"]), min(centers["r1"], centers["r2"]))
        rank_members = [
            element.get("data-member-ids", "").split()
            for element in root.iter()
            if element.get("data-primitive") == "hierarchy-rank"
        ]
        self.assertEqual(rank_members, [["root"], ["left", "right"], ["l1", "l2", "r1", "r2"]])
        collision = ledger["geometry_validation"]["collision_graph"]
        self.assertEqual((collision["proper_crossings"], collision["shared_segments"], collision["undeclared_junctions"]), (0, 0, 0))

    def test_hierarchy_secondary_peer_relation_does_not_change_ranks_or_enter_endpoint_interiors(self) -> None:
        ir = finalize(
            "org-chart",
            nodes=[
                n("ceo", "role", "Tổng giám đốc"),
                n("ops-director", "role", "Giám đốc vận hành"),
                n("product-director", "role", "Giám đốc sản phẩm"),
                n("warehouse-lead", "role", "Trưởng kho"),
                n("design-lead", "role", "Trưởng thiết kế"),
                n("research-lead", "role", "Trưởng nghiên cứu"),
            ],
            edges=[
                e("ops-ceo", "ops-director", "ceo", "reports-to"),
                e("product-ceo", "product-director", "ceo", "reports-to"),
                e("warehouse-ops", "warehouse-lead", "ops-director", "reports-to"),
                e("design-product", "design-lead", "product-director", "reports-to"),
                e("research-product", "research-lead", "product-director", "reports-to"),
                e("peer-escalation", "ops-director", "product-director", "escalates", label="Phối hợp"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("org-chart", "hierarchy"),
                ir,
                Path(temporary) / "hierarchy-secondary",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        nodes = {element.get("data-node-id"): element for element in root.iter() if element.get("data-node-id")}
        self.assertAlmostEqual(float(nodes["ops-director"].get("data-y", "0")), float(nodes["product-director"].get("data-y", "0")))
        peer = next(element for element in root.iter() if element.get("data-edge-id") == "peer-escalation")
        peer_points = peer.get("points", "").split()
        self.assertTrue(all(left != right for left, right in zip(peer_points, peer_points[1:])))
        collision = ledger["geometry_validation"]["collision_graph"]
        self.assertEqual((collision["shared_segments"], collision["undeclared_junctions"]), (0, 0))

    def test_ordered_swimlane_handoffs_avoid_peer_activities_and_use_horizontal_same_lane_ports(self) -> None:
        ir = finalize(
            "swimlane",
            nodes=[
                n("submit", "activity", "Gửi yêu cầu"),
                n("screen", "activity", "Kiểm tra nhu cầu"),
                n("quote", "activity", "Gửi báo giá"),
                n("pay", "activity", "Thanh toán"),
                n("receive", "activity", "Nhận hợp đồng"),
            ],
            edges=[
                e("submit-screen", "submit", "screen", "handoff", order=0),
                e("screen-quote", "screen", "quote", "handoff", order=1),
                e("quote-pay", "quote", "pay", "handoff", order=2),
                e("pay-receive", "pay", "receive", "handoff", order=3),
            ],
            lanes=[
                {"id": "buyer-lane", "label": "Người mua", "owner": "Người mua", "member_ids": ["submit", "receive"], "order": 0},
                {"id": "advisor-lane", "label": "Tư vấn", "owner": "Tư vấn", "member_ids": ["screen", "quote"], "order": 1},
                {"id": "finance-lane", "label": "Tài chính", "owner": "Tài chính", "member_ids": ["pay"], "order": 2},
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("swimlane", "lane-interaction"),
                ir,
                Path(temporary) / "same-lane",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        nodes = {
            element.get("data-node-id"): element
            for element in root.iter()
            if element.get("data-node-id")
        }
        self.assertEqual(
            {element.get("data-edge-id") for element in root.iter() if element.get("data-edge-id")},
            {"submit-screen", "screen-quote", "quote-pay", "pay-receive"},
        )
        edge = next(element for element in root.iter() if element.get("data-edge-id") == "screen-quote")
        points = [tuple(float(value) for value in pair.split(",")) for pair in edge.get("points", "").split()]
        screen_right = float(nodes["screen"].get("data-x", "0")) + float(nodes["screen"].get("data-w", "0"))
        quote_left = float(nodes["quote"].get("data-x", "0"))
        self.assertAlmostEqual(points[0][0], screen_right)
        self.assertAlmostEqual(points[-1][0], quote_left)
        self.assertAlmostEqual(points[0][1], points[-1][1])

    def test_slope_graph_prints_every_endpoint_value(self) -> None:
        ir = finalize(
            "line-chart",
            series=[
                series("alpha", "Alpha", [datum("alpha-before", "Before", 25), datum("alpha-after", "After", 70)], "points"),
                series("beta", "Beta", [datum("beta-before", "Before", 80), datum("beta-after", "After", 55)], "points"),
                series("gamma", "Gamma", [datum("gamma-before", "Before", 45), datum("gamma-after", "After", 45)], "points"),
            ],
            axes=[
                axis("state-axis", "x", "ordinal", "State"),
                axis("score-axis", "y", "linear", "Score", domain_min=0, domain_max=100, unit="points"),
            ],
        )
        ir["diagram"]["variant_ids"] = ["CAP-V18"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("line-chart", "slope-graph", variant_ids=["CAP-V18"]),
                ir,
                Path(temporary) / "slope-graph",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        visible_text = [element.text for element in root.iter() if element.tag == f"{{{SVG_NS}}}text"]
        for value in ("25", "70", "80", "55", "45", "+45", "-25", "0"):
            self.assertIn(value, visible_text)
        delta_by_series = {
            element.get("data-series-id"): element.text
            for element in root.iter()
            if element.get("data-mark") == "slope-delta"
        }
        self.assertEqual(delta_by_series, {"alpha": "+45", "beta": "-25", "gamma": "0"})
        gamma = next(element for element in root.iter() if element.get("data-mark") == "slope" and element.get("y1") == element.get("y2"))
        self.assertIsNotNone(gamma)
        self.assertTrue(all(element.get("marker-end") is None for element in root.iter() if element.get("data-mark") == "slope"))

    def test_phase7_b5_frozen_shapes_show_units_and_non_color_series_identity(self) -> None:
        cases = {
            case_id: (case_request, ir)
            for case_id, case_request, ir in phase7_b3_frozen_case_shapes()
            if case_id in {"R10", "R13", "R16"}
        }
        rendered: dict[str, ET.Element] = {}
        with tempfile.TemporaryDirectory() as temporary:
            for case_id, (case_request, ir) in cases.items():
                result = create_profiled_diagram(case_request, ir, Path(temporary) / case_id)
                rendered[case_id] = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        funnel_labels = {
            element.text
            for element in rendered["R10"].iter()
            if element.tag == f"{{{SVG_NS}}}text"
        }
        self.assertTrue({
            "Khách truy cập · 10000 khách hàng",
            "Đăng ký · 4200 khách hàng",
            "Dùng thử · 1600 khách hàng",
            "Trả phí · 620 khách hàng",
        }.issubset(funnel_labels))
        self.assertEqual(
            {element.get("data-visible-unit") for element in rendered["R10"].iter() if element.get("data-mark") == "funnel-tier"},
            {"khách hàng"},
        )

        for case_id, expected_labels in (
            ("R13", {"core": "Core", "growth": "Growth"}),
            ("R16", {"north": "Miền Bắc", "central": "Miền Trung", "south": "Miền Nam"}),
        ):
            root = rendered[case_id]
            legend_entries = {
                element.get("data-series-legend-id"): element
                for element in root.iter()
                if element.get("data-series-legend-id")
            }
            self.assertEqual(set(legend_entries), set(expected_labels))
            patterns = {series_id: entry.get("data-series-pattern") for series_id, entry in legend_entries.items()}
            self.assertEqual(len(set(patterns.values())), len(expected_labels))
            for series_id, expected_label in expected_labels.items():
                labels = [
                    element.text
                    for element in legend_entries[series_id].iter()
                    if element.get("data-series-label-for") == series_id
                ]
                self.assertEqual(labels, [expected_label])
                series_marks = [
                    element for element in root.iter()
                    if element.get("data-series-id") == series_id
                    and element.get("data-mark") in {"observation", "endpoint"}
                ]
                self.assertTrue(series_marks)
                self.assertTrue(all(element.get("data-series-pattern") == patterns[series_id] for element in series_marks))

        slope_lines = [element for element in rendered["R16"].iter() if element.get("data-mark") == "slope"]
        self.assertEqual({element.get("data-series-id") for element in slope_lines}, {"north", "central", "south"})
        self.assertEqual(len({element.get("data-series-pattern") for element in slope_lines}), 3)
        self.assertTrue(all(element.get("marker-end") is None for element in slope_lines))

    def test_deployment_preserves_first_seen_edge_app_data_zone_order(self) -> None:
        ir = finalize(
            "deployment",
            nodes=[
                n("public-api", "artifact", "Public API", placement={"zone": "Edge", "host": "edge-1", "artifact": "api", "replicas": 2, "ports": ["443"]}),
                n("queue-worker", "artifact", "Queue Worker", placement={"zone": "App", "host": "app-1", "artifact": "worker", "replicas": 3, "ports": ["9000"]}),
                n("ledger-db", "artifact", "Ledger DB", placement={"zone": "Data", "host": "data-1", "artifact": "postgres", "replicas": 1, "ports": ["5432"]}),
            ],
            edges=[
                e("api-worker", "public-api", "queue-worker", "authenticate", label="authenticate"),
                e("worker-db", "queue-worker", "ledger-db", "transaction", label="write transaction"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("deployment", "runtime-deployment", size="slide-16x9"),
                ir,
                Path(temporary) / "deployment-order",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        zones = sorted(
            (element for element in root.iter() if element.get("data-primitive") == "deployment-zone"),
            key=lambda element: float(element.get("data-x", "0")),
        )
        self.assertEqual([element.get("data-member-ids") for element in zones], ["public-api", "queue-worker", "ledger-db"])

    def test_incident_source_and_target_ports_share_one_allocator_without_overlap(self) -> None:
        ir = finalize(
            "architecture",
            nodes=[
                n("left-a", "service", "A"),
                n("left-c", "service", "C"),
                n("right-b", "service", "B"),
            ],
            groups=[g("right-zone", "Right", ["right-b"])],
            edges=[
                e("a-b", "left-a", "right-b", "request"),
                e("b-c", "right-b", "left-c", "request"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("architecture", "topology-and-zones"),
                ir,
                Path(temporary) / "cross-kind-terminal",
            )
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        self.assertEqual(
            ledger["geometry_validation"]["collision_graph"],
            {
                "segment_count": 6,
                "proper_crossings": 0,
                "declared_junctions": 0,
                "terminal_fan_groups": 1,
                "shared_segments": 0,
                "undeclared_junctions": 0,
            },
        )

    def test_domain_specific_receipts_preserve_placement_journey_layers_database_and_fishbone(self) -> None:
        cases = {
            "deployment": ("runtime-deployment", fixtures()["deployment"]),
            "user-journey": ("work-experience", fixtures()["user-journey"]),
            "layer-stack": ("layers", fixtures()["layer-stack"]),
            "database-schema": ("compartment-model", fixtures()["database-schema"]),
            "fishbone": ("type-fishbone", fixtures()["fishbone"]),
        }
        with tempfile.TemporaryDirectory() as temporary:
            roots = {}
            for diagram_type, (profile, ir) in cases.items():
                result = create_profiled_diagram(
                    request(diagram_type, profile),
                    ir,
                    Path(temporary) / diagram_type,
                )
                roots[diagram_type] = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        deployment_nodes = {
            element.get("data-node-id"): element
            for element in roots["deployment"].iter()
            if element.get("data-node-id")
        }
        self.assertEqual(
            {
                key: deployment_nodes["deploy-api"].get(key)
                for key in (
                    "data-placement-zone",
                    "data-placement-host",
                    "data-placement-artifact",
                    "data-placement-replicas",
                    "data-placement-ports",
                )
            },
            {
                "data-placement-zone": "Vùng ứng dụng",
                "data-placement-host": "node-a",
                "data-placement-artifact": "api.jar",
                "data-placement-replicas": "2",
                "data-placement-ports": "8443",
            },
        )
        deployment_text = " ".join(element.text or "" for element in roots["deployment"].iter() if element.tag == f"{{{SVG_NS}}}text")
        self.assertIn("api.jar · ×2 · port 8443", deployment_text)

        journey_nodes = {
            element.get("data-node-id"): element
            for element in roots["user-journey"].iter()
            if element.get("data-node-id")
        }
        self.assertEqual(journey_nodes["journey-submit"].get("data-journey-stage-order"), "1")
        self.assertEqual(journey_nodes["journey-submit"].get("data-journey-action"), "Gửi biểu mẫu")
        self.assertEqual(journey_nodes["journey-submit"].get("data-journey-touchpoint"), "Cổng dịch vụ")
        self.assertEqual(journey_nodes["journey-submit"].get("data-journey-sentiment"), "-0.1")
        journey_text = " ".join(element.text or "" for element in roots["user-journey"].iter() if element.tag == f"{{{SVG_NS}}}text")
        self.assertIn("sentiment -0.1", journey_text)

        layers = [element for element in roots["layer-stack"].iter() if element.get("data-lane-id")]
        self.assertEqual([element.get("data-lane-id") for element in layers], ["layer-edge", "layer-data"])
        self.assertEqual([element.get("data-lane-order") for element in layers], ["0", "1"])
        self.assertEqual([element.get("data-lane-owner") for element in layers], ["Biên", "Dữ liệu"])
        self.assertEqual({element.get("data-x") for element in layers}, {"100"})
        self.assertEqual({element.get("data-w") for element in layers}, {"1400"})

        database_root = roots["database-schema"]
        member_rows = {
            element.get("data-member-id"): element.get("data-owner-node")
            for element in database_root.iter()
            if element.get("data-member-id")
        }
        self.assertEqual(
            member_rows,
            {
                "column-customer-id": "table-customer",
                "index-customer-id": "table-customer",
                "column-order-id": "table-order",
                "column-order-customer": "table-order",
                "index-order-customer": "table-order",
            },
        )
        foreign_key = next(element for element in database_root.iter() if element.get("data-edge-id") == "foreign-key-order-customer")
        self.assertEqual(foreign_key.get("data-source-member"), "column-order-customer")
        self.assertEqual(foreign_key.get("data-target-member"), "column-customer-id")
        database_text = " ".join(element.text or "" for element in database_root.iter() if element.tag == f"{{{SVG_NS}}}text")
        self.assertIn("id: uuid  [PK NN]", database_text)
        self.assertIn("customer_id: uuid  [NN]", database_text)

        fishbone_root = roots["fishbone"]
        fishbone_groups = {
            element.get("data-semantic-group-id"): set(element.get("data-member-ids", "").split())
            for element in fishbone_root.iter()
            if element.get("data-semantic-group-id")
        }
        self.assertEqual(
            fishbone_groups,
            {
                "category-method": {"cause-process"},
                "category-technology": {"cause-system"},
            },
        )
        self.assertEqual(
            {element.get("data-category-id") for element in fishbone_root.iter() if element.get("data-mark") == "category-bone"},
            {"category-method", "category-technology"},
        )

    def test_layers_exposes_top_to_bottom_reading_and_visible_abstraction_axis(self) -> None:
        ir = finalize(
            "layer-stack",
            nodes=[
                n("customer-channel", "channel", "Customer Channel"),
                n("order-orchestrator", "service", "Order Orchestrator"),
                n("transaction-store", "store", "Transaction Store"),
            ],
            lanes=[
                {"id": "experience-layer", "label": "Experience", "owner": "Kinh doanh", "member_ids": ["customer-channel"], "order": 0},
                {"id": "service-layer", "label": "Service", "owner": "Nền tảng", "member_ids": ["order-orchestrator"], "order": 1},
                {"id": "data-layer", "label": "Data", "owner": "Dữ liệu", "member_ids": ["transaction-store"], "order": 2},
            ],
            edges=[
                e("customer-request", "customer-channel", "order-orchestrator", "request"),
                e("orchestrator-write", "order-orchestrator", "transaction-store", "write"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("layer-stack", "layers", size="slide-16x9"),
                ir,
                Path(temporary) / "layers",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        self.assertEqual(root.get("data-presentation-variant-id"), "layers")
        self.assertEqual(root.get("data-reading-direction"), "top-to-bottom")
        abstraction = next(element for element in root.iter() if element.get("data-abstraction-axis") == "true")
        self.assertEqual(
            (
                abstraction.get("data-abstraction-axis-label"),
                abstraction.get("data-abstraction-axis-top"),
                abstraction.get("data-abstraction-axis-bottom"),
            ),
            ("Mức trừu tượng", "Cao", "Thấp"),
        )
        visible_text = {element.text for element in root.iter() if element.tag == f"{{{SVG_NS}}}text"}
        self.assertTrue({"Mức trừu tượng", "Cao", "Thấp"} <= visible_text)
        bands = sorted(
            (element for element in root.iter() if element.get("data-lane-id")),
            key=lambda element: float(element.get("data-y", "0")),
        )
        self.assertEqual([element.get("data-lane-id") for element in bands], ["experience-layer", "service-layer", "data-layer"])
        self.assertEqual(len({element.get("data-x") for element in bands}), 1)
        self.assertEqual(len({element.get("data-w") for element in bands}), 1)
        self.assertFalse(any(element.get("data-primitive") == "module-grid" for element in root.iter()))

    def test_dense_fishbone_declares_every_edge_crossing_and_preserves_categories(self) -> None:
        ir = finalize(
            "fishbone",
            nodes=[
                n("late-review", "cause", "Review muộn"),
                n("unstable-env", "cause", "Môi trường thiếu ổn định"),
                n("scope-churn", "cause", "Thay đổi phạm vi"),
                n("staff-gap", "cause", "Thiếu nhân sự"),
                n("late-release", "effect", "Phát hành trễ"),
            ],
            edges=[
                e("late-review-effect", "late-review", "late-release", "cause"),
                e("unstable-env-effect", "unstable-env", "late-release", "cause"),
                e("scope-churn-effect", "scope-churn", "late-release", "cause"),
                e("staff-gap-effect", "staff-gap", "late-release", "cause"),
            ],
            groups=[
                g("category-process", "Quy trình", ["late-review", "unstable-env"], cause_category="Quy trình"),
                g("category-planning", "Kế hoạch", ["scope-churn"], cause_category="Kế hoạch"),
                g("category-people", "Con người", ["staff-gap"], cause_category="Con người"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("fishbone", "type-fishbone", size="slide-16x9"),
                ir,
                Path(temporary) / "dense-fishbone",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        self.assertEqual(
            {element.get("data-semantic-group-id") for element in root.iter() if element.get("data-semantic-group-id")},
            {"category-process", "category-planning", "category-people"},
        )
        self.assertGreaterEqual(ledger["geometry_validation"]["collision_graph"]["proper_crossings"], 1)
        self.assertEqual(ledger["geometry_validation"]["collision_graph"]["shared_segments"], 0)
        self.assertEqual(ledger["geometry_validation"]["collision_graph"]["undeclared_junctions"], 0)

    def test_dumbbell_transposes_semantic_axes_and_keeps_one_declared_linear_scale(self) -> None:
        ir = finalize(
            "bar-chart",
            series=[
                series("before", "Before", [
                    datum("before-north", "Chi nhánh Bắc", 42),
                    datum("before-central", "Chi nhánh Trung", 55),
                    datum("before-south", "Chi nhánh Nam", 48),
                ], "điểm"),
                series("after", "After", [
                    datum("after-north", "Chi nhánh Bắc", 63),
                    datum("after-central", "Chi nhánh Trung", 60),
                    datum("after-south", "Chi nhánh Nam", 72),
                ], "điểm"),
            ],
            axes=[
                axis("branch-axis", "x", "categorical", "Chi nhánh"),
                axis("score-axis", "y", "linear", "Điểm", domain_min=0, domain_max=80, unit="điểm"),
            ],
        )
        ir["diagram"]["variant_ids"] = ["CAP-V17"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("bar-chart", "dumbbell", variant_ids=["CAP-V17"]),
                ir,
                Path(temporary) / "dumbbell",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        self.assertEqual(
            root.get("data-axis-presentation-mapping"),
            "semantic-y-to-horizontal semantic-x-to-vertical",
        )
        axes = {
            element.get("data-axis-id"): element
            for element in root.iter()
            if element.get("data-axis-id")
        }
        self.assertEqual(axes["score-axis"].get("data-axis-presentation"), "horizontal")
        self.assertEqual(axes["score-axis"].get("data-axis-domain-min"), "0")
        self.assertEqual(axes["score-axis"].get("data-axis-domain-max"), "80")
        self.assertEqual(axes["branch-axis"].get("data-axis-presentation"), "vertical")
        endpoints = {
            element.get("data-semantic-id"): (float(element.get("cx", "0")), float(element.get("data-value", "0")))
            for element in root.iter()
            if element.get("data-mark") == "endpoint"
        }
        self.assertEqual(set(endpoints), {"before-north", "after-north", "before-central", "after-central", "before-south", "after-south"})
        slopes = [
            (endpoints[right][0] - endpoints[left][0]) / (endpoints[right][1] - endpoints[left][1])
            for left, right in (("before-north", "after-north"), ("before-central", "after-central"), ("before-south", "after-south"))
        ]
        self.assertLess(max(slopes) - min(slopes), 0.01)
        self.assertTrue(all(value > 0 for value in slopes))
        deltas = {
            element.get("data-domain"): element.text
            for element in root.iter()
            if element.get("data-mark") == "comparison-delta"
        }
        self.assertEqual(deltas, {"Chi nhánh Bắc": "+21", "Chi nhánh Trung": "+5", "Chi nhánh Nam": "+24"})
        self.assertTrue(all(element.get("marker-end") is None for element in root.iter() if element.get("data-mark") == "comparison-segment"))

    def test_ridgeline_receipts_bind_declared_bins_and_global_normalization(self) -> None:
        distribution = {
            "method": "histogram",
            "domain_min": 0,
            "domain_max": 12,
            "bin_count": 6,
            "bin_edges": [0, 2, 4, 6, 8, 10, 12],
            "bandwidth": 2,
            "amplitude_normalization": "global-max",
            "shared_domain": True,
            "shared_bins": True,
        }
        ir = finalize(
            "line-chart",
            series=[
                series(
                    "weekday",
                    "Ngày thường",
                    [{"id": "weekday-distribution", "distribution_samples": [2, 3, 3, 4, 5, 5, 5, 6, 7, 8], "missing": False}],
                    distribution=copy.deepcopy(distribution),
                ),
                series(
                    "weekend",
                    "Cuối tuần",
                    [{"id": "weekend-distribution", "distribution_samples": [4, 5, 6, 6, 7, 8, 8, 9, 10, 11], "missing": False}],
                    distribution=copy.deepcopy(distribution),
                ),
            ],
            axes=[
                axis("duration", "x", "linear", "Thời lượng", domain_min=0, domain_max=12),
                axis("density", "y", "linear", "Biên độ chuẩn hóa", domain_min=0, domain_max=1),
            ],
        )
        ir["diagram"]["variant_ids"] = ["CAP-V19"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("line-chart", "ridgeline", variant_ids=["CAP-V19"]),
                ir,
                Path(temporary) / "ridgeline",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        ridges = [element for element in root.iter() if element.get("data-mark") == "ridge"]
        self.assertEqual({element.get("data-semantic-id") for element in ridges}, {"weekday-distribution", "weekend-distribution"})
        self.assertEqual({element.get("data-bin-count") for element in ridges}, {"6"})
        self.assertEqual({element.get("data-normalization") for element in ridges}, {"global-max"})
        self.assertEqual({element.get("data-distribution-bandwidth") for element in ridges}, {"2"})
        self.assertTrue(all(len(element.get("points", "").split()) == 8 for element in ridges))
        axes = {
            element.get("data-axis-id"): element
            for element in root.iter()
            if element.get("data-axis-id")
        }
        self.assertEqual(axes["duration"].get("data-axis-domain-min"), "0")
        self.assertEqual(axes["duration"].get("data-axis-domain-max"), "12")
        self.assertEqual(axes["density"].get("data-axis-domain-min"), "0")
        self.assertEqual(axes["density"].get("data-axis-domain-max"), "1")
        self.assertEqual(
            root.get("data-axis-presentation-mapping"),
            "semantic-y-to-local-ridge-amplitude semantic-x-to-horizontal",
        )
        self.assertEqual(axes["duration"].get("data-axis-presentation"), "horizontal")
        self.assertEqual(axes["density"].get("data-axis-presentation"), "local-ridge-amplitude")
        local_receipts = {
            element.get("data-local-amplitude-series"): (
                element.get("data-local-amplitude-axis-id"),
                element.get("data-local-amplitude-min"),
                element.get("data-local-amplitude-max"),
                element.get("data-local-amplitude-normalization"),
            )
            for element in root.iter()
            if element.get("data-local-amplitude-series")
        }
        self.assertEqual(local_receipts, {
            "weekday": ("density", "0", "1", "global-max"),
            "weekend": ("density", "0", "1", "global-max"),
        })
        header_roles = {
            element.get("data-ridgeline-header-role"): element
            for element in root.iter()
            if element.get("data-ridgeline-header-role")
        }
        self.assertEqual(set(header_roles), {
            "shared-scale-heading",
            "amplitude-axis-title",
            "distribution-metadata",
        })
        self.assertEqual(
            {role: element.get("data-layout-band") for role, element in header_roles.items()},
            {
                "shared-scale-heading": "ridgeline-heading",
                "amplitude-axis-title": "ridgeline-axis-title",
                "distribution-metadata": "ridgeline-distribution-metadata",
            },
        )
        header_y = [float(header_roles[role].get("y", "nan")) for role in (
            "shared-scale-heading",
            "amplitude-axis-title",
            "distribution-metadata",
        )]
        self.assertTrue(all(right - left >= 24 for left, right in zip(header_y, header_y[1:])))
        self.assertLess(header_y[-1], min(float(element.get("data-ridge-baseline", "nan")) for element in ridges))

    def test_ridgeline_renders_canonical_unequal_bin_density_and_kde_method(self) -> None:
        distribution = {
            "method": "histogram",
            "domain_min": 0,
            "domain_max": 3,
            "bin_count": 2,
            "bin_edges": [0, 1, 3],
            "bandwidth": None,
            "amplitude_normalization": "global-max",
            "shared_domain": True,
            "shared_bins": True,
        }
        ir = finalize(
            "line-chart",
            series=[series(
                "unequal",
                "Unequal bins",
                [{"id": "unequal-samples", "distribution_samples": [0.5, 2.0], "missing": False}],
                "points",
                distribution=distribution,
            )],
            axes=[
                axis("domain", "x", "linear", "Value", domain_min=0, domain_max=3, unit="points"),
                axis("amplitude", "y", "linear", "Normalized density", domain_min=0, domain_max=1, unit=None),
            ],
        )
        ir["diagram"]["variant_ids"] = ["CAP-V19"]
        kde = copy.deepcopy(ir)
        kde["series"][0]["distribution"].update({"method": "kde-gaussian", "bandwidth": 0.5})
        with tempfile.TemporaryDirectory() as temporary:
            histogram_result = create_profiled_diagram(
                request("line-chart", "ridgeline", variant_ids=["CAP-V19"]),
                ir,
                Path(temporary) / "histogram",
            )
            kde_result = create_profiled_diagram(
                request("line-chart", "ridgeline", variant_ids=["CAP-V19"]),
                kde,
                Path(temporary) / "kde",
            )
            histogram_root = ET.fromstring(Path(histogram_result.svg_path).read_text(encoding="utf-8"))
            kde_root = ET.fromstring(Path(kde_result.svg_path).read_text(encoding="utf-8"))

        histogram_ridge = next(element for element in histogram_root.iter() if element.get("data-mark") == "ridge")
        baseline = float(histogram_ridge.get("data-ridge-baseline", "nan"))
        amplitude = float(histogram_ridge.get("data-ridge-amplitude-pixels", "nan"))
        histogram_points = [tuple(float(value) for value in pair.split(",")) for pair in histogram_ridge.get("points", "").split()]
        observed = [(baseline - point[1]) / amplitude for point in histogram_points[1:-1]]
        self.assertAlmostEqual(observed[0], 1.0, places=3)
        self.assertAlmostEqual(observed[1], 0.5, places=3)
        kde_ridge = next(element for element in kde_root.iter() if element.get("data-mark") == "ridge")
        self.assertEqual(kde_ridge.get("data-distribution-method"), "kde-gaussian")
        self.assertEqual(kde_ridge.get("data-distribution-bandwidth"), "0.5")
        kde_text = {element.text for element in kde_root.iter() if element.tag == f"{{{SVG_NS}}}text"}
        self.assertIn("kde-gaussian · 2 bins · bandwidth 0.5 · global-max", kde_text)

    def test_bubble_uses_area_proportional_size_with_labels_and_exact_size_axis(self) -> None:
        ir = finalize(
            "scatter-plot",
            series=[
                series("portfolio-core", "Portfolio Core", [
                    {**xy_datum("apollo", 2, 8, 20.0, "million USD"), "label": "Apollo"},
                    {**xy_datum("borealis", 7, 5, 45, "million USD"), "label": "Borealis"},
                ], "percent"),
                series("portfolio-growth", "Portfolio Growth", [
                    {**xy_datum("cygnus", 4, 3, 10, "million USD"), "label": "Cygnus"},
                    {**xy_datum("draco", 9, 9, 70, "million USD"), "label": "Draco"},
                ], "percent"),
            ],
            axes=[
                axis("risk", "x", "linear", "Risk", domain_min=0, domain_max=10, unit="points"),
                axis("return", "y", "linear", "Return", domain_min=0, domain_max=10, unit="percent"),
                axis("capital", "size", "linear", "Capital", domain_min=0, domain_max=80, unit="million USD"),
            ],
        )
        ir["diagram"]["variant_ids"] = ["CAP-V20"]
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("scatter-plot", "bubble", variant_ids=["CAP-V20"]),
                ir,
                Path(temporary) / "bubble",
            )
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))

        bubbles = {
            element.get("data-semantic-id"): element
            for element in root.iter()
            if element.get("data-mark") == "bubble"
        }
        radius_a = float(bubbles["apollo"].get("r", "0"))
        radius_b = float(bubbles["borealis"].get("r", "0"))
        self.assertAlmostEqual(radius_a * radius_a / (radius_b * radius_b), 20 / 45, places=3)
        self.assertEqual({element.get("data-size-unit") for element in bubbles.values()}, {"million USD"})
        self.assertEqual(
            {item_id: element.get("data-series-id") for item_id, element in bubbles.items()},
            {"apollo": "portfolio-core", "borealis": "portfolio-core", "cygnus": "portfolio-growth", "draco": "portfolio-growth"},
        )
        visible_text = {element.text for element in root.iter() if element.tag == f"{{{SVG_NS}}}text"}
        self.assertTrue({"Apollo", "Borealis", "Cygnus", "Draco"} <= visible_text)
        self.assertIn("Capital · million USD · 0..80 · area", visible_text)
        size_axis = next(element for element in root.iter() if element.get("data-axis-id") == "capital")
        self.assertEqual(size_axis.get("data-axis-presentation"), "size-area")
        self.assertEqual(size_axis.get("data-axis-domain-min"), "0")
        self.assertEqual(size_axis.get("data-axis-domain-max"), "80")
        self.assertEqual(size_axis.get("data-axis-unit"), "million USD")
        self.assertEqual(size_axis.get("data-size-legend-label"), "Capital")
        self.assertEqual(size_axis.get("data-size-legend-unit"), "million USD")
        legend_entries = {
            element.get("data-series-legend-id"): element
            for element in root.iter()
            if element.get("data-series-legend-id")
        }
        self.assertEqual(set(legend_entries), {"portfolio-core", "portfolio-growth"})
        self.assertEqual(
            {
                series_id: [
                    element.text
                    for element in entry.iter()
                    if element.get("data-series-label-for") == series_id
                ]
                for series_id, entry in legend_entries.items()
            },
            {"portfolio-core": ["Portfolio Core"], "portfolio-growth": ["Portfolio Growth"]},
        )
        patterns = {series_id: entry.get("data-series-pattern") for series_id, entry in legend_entries.items()}
        self.assertEqual(len(set(patterns.values())), 2)
        self.assertEqual(
            {
                series_id: [
                    element.get("data-series-pattern")
                    for element in entry.iter()
                    if element.get("data-series-legend-mark") == series_id
                ]
                for series_id, entry in legend_entries.items()
            },
            {series_id: [pattern] for series_id, pattern in patterns.items()},
        )
        self.assertEqual(
            {item_id: element.get("data-series-pattern") for item_id, element in bubbles.items()},
            {
                "apollo": patterns["portfolio-core"],
                "borealis": patterns["portfolio-core"],
                "cygnus": patterns["portfolio-growth"],
                "draco": patterns["portfolio-growth"],
            },
        )
        self.assertEqual(bubbles["apollo"].get("stroke-dasharray"), None)
        self.assertEqual(bubbles["cygnus"].get("stroke-dasharray"), "10 6")

    def test_relation_groups_preserve_required_sequence_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram_from_job(ordered_sequence_job(), Path(temporary) / "sequence")
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        self.assertEqual(result.selected_profile, "type-sequence")
        self.assertEqual(result.layout_engine, "lane-interaction")
        self.assertEqual(ledger["geometry_validation"]["edges"], 2)

    def test_profile_job_expected_count_mismatch_fails_before_output(self) -> None:
        job = dense_topology_job()
        job["expected_counts"]["edges"] = 8
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "must-not-exist"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram_from_job(job, target)
            self.assertEqual(caught.exception.code, "semantic-coverage-mismatch")
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_source_assertions_reject_assertion_to_materialization_drift(self) -> None:
        job = dense_topology_job()
        job["relation_groups"] = job["relation_groups"][:-1]
        job["expected_counts"]["edges"] = 7
        job["expected_counts"]["directed_edges"] = 7
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "must-not-exist"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram_from_job(job, target)
            self.assertEqual(caught.exception.code, "semantic-coverage-mismatch")
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_agent_authored_assertions_disclose_that_raw_prompt_completeness_is_not_proven(self) -> None:
        job = dense_topology_job()
        job["relation_groups"] = job["relation_groups"][2:]
        job["source_assertions"]["edge_assertions"] = job["source_assertions"]["edge_assertions"][2:]
        job["expected_counts"]["edges"] = 8
        job["expected_counts"]["directed_edges"] = 8
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram_from_job(job, Path(temporary) / "underread")
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        self.assertEqual(ledger["semantic_coverage"], "pass")
        self.assertEqual(ledger["semantic_coverage_scope"], "declared-source-assertions-to-validated-ir")
        self.assertEqual(ledger["source_interpretation_attestation"], "agent-authored-not-independently-proven")

    def test_profile_job_series_data_ids_are_not_misclassified_as_reading_order_items(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram_from_job(bar_profile_job(), Path(temporary) / "bar")
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        self.assertEqual(result.selected_profile, "type-bar-chart")
        self.assertEqual(ledger["geometry_validation"]["marks"], 2)
        self.assertEqual(ledger["semantic_coverage"], "pass")

    def test_relation_group_cartesian_expansion_is_bounded_before_materialization(self) -> None:
        job = dense_topology_job()
        job["relation_groups"] = [
            {
                "id_prefix": "amplified",
                "sources": [f"source-{index}" for index in range(45)],
                "targets": [f"target-{index}" for index in range(45)],
                "kind": "request",
                "directed": True,
            }
        ]
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "must-not-exist"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram_from_job(job, target)
            self.assertEqual(caught.exception.code, "profile-job-complexity-limit")
            self.assertFalse(target.exists())

    def test_semantic_receipt_rejects_valid_but_incomplete_ir_before_output(self) -> None:
        ir = dense_topology_ir()
        raw_request, receipt = dense_request_and_receipt(ir)
        incomplete = finalize(
            "architecture",
            nodes=[{key: copy.deepcopy(value) for key, value in node.items() if key != "source_refs"} for node in ir["nodes"]],
            groups=[{key: copy.deepcopy(value) for key, value in group.items() if key != "source_refs"} for group in ir["groups"]],
            edges=[{key: copy.deepcopy(value) for key, value in edge.items() if key != "source_refs"} for edge in ir["edges"][:-2]],
        )
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "must-not-exist"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram(raw_request, incomplete, target, semantic_receipt=receipt)
            self.assertEqual(caught.exception.code, "semantic-coverage-mismatch")
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(temporary).iterdir()), [])

    def test_semantic_receipt_rejects_edge_kind_drift_and_assertion_hash_drift(self) -> None:
        ir = dense_topology_ir()
        raw_request, receipt = dense_request_and_receipt(ir)
        kind_drift = copy.deepcopy(ir)
        kind_drift["edges"][0]["kind"] = "fabricated-kind"
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "kind-drift"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram(raw_request, kind_drift, target, semantic_receipt=receipt)
            self.assertEqual(caught.exception.code, "semantic-coverage-mismatch")
            self.assertFalse(target.exists())
        hash_drift = copy.deepcopy(receipt)
        hash_drift["source_assertions_sha256"] = "a" * 64
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "hash-drift"
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram(raw_request, ir, target, semantic_receipt=hash_drift)
            self.assertEqual(caught.exception.code, "semantic-coverage-mismatch")
            self.assertFalse(target.exists())

    def test_dense_topology_separates_terminal_fan_in_and_reports_collision_graph(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "dense")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        collision_graph = ledger["geometry_validation"]["collision_graph"]
        self.assertEqual(collision_graph["shared_segments"], 0)
        self.assertEqual(collision_graph["undeclared_junctions"], 0)
        self.assertGreaterEqual(collision_graph["terminal_fan_groups"], 3)
        for target, expected_count in (("transaction-db", 2), ("log-store", 3)):
            terminals = {
                element.get("points", "").split()[-1]
                for element in root.iter()
                if element.get("data-target") == target
            }
            self.assertEqual(len(terminals), expected_count)

    def test_phase7_b1_topology_routes_internal_vertex_crossings_without_junctions(self) -> None:
        ir = finalize(
            "architecture",
            nodes=[
                n("customer", "actor", "Khách hàng"),
                n("gateway", "service", "API Gateway"),
                n("identity", "service", "Identity Service"),
                n("orders", "service", "Order Service"),
                n("inventory", "service", "Inventory Service"),
                n("order-db", "store", "Order Database"),
                n("event-bus", "broker", "Event Bus"),
            ],
            groups=[
                g("edge-zone", "Edge", ["customer", "gateway"]),
                g("app-zone", "App", ["identity", "orders", "inventory"]),
                g("data-zone", "Data", ["order-db", "event-bus"]),
            ],
            edges=[
                e("customer-gateway", "customer", "gateway", "request"),
                e("gateway-identity", "gateway", "identity", "authenticate"),
                e("identity-orders", "identity", "orders", "authorize"),
                e("gateway-orders", "gateway", "orders", "route"),
                e("orders-inventory", "orders", "inventory", "check-stock"),
                e("orders-db", "orders", "order-db", "persist"),
                e("orders-bus", "orders", "event-bus", "publish"),
                e("bus-inventory", "event-bus", "inventory", "update-stock"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("architecture", "topology-and-zones", mode="neutral-light"),
                ir,
                Path(temporary) / "b1-topology",
            )
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        collision = ledger["geometry_validation"]["collision_graph"]
        self.assertEqual(collision["shared_segments"], 0)
        self.assertEqual(collision["undeclared_junctions"], 0)

    def test_phase7_b1_pipeline_and_flow_routes_avoid_unrelated_nodes(self) -> None:
        cases = [
            (
                "data-flow",
                "integration-pipeline",
                "neutral-dark",
                finalize(
                    "data-flow",
                    nodes=[
                        n("crm", "source", "CRM"),
                        n("billing", "source", "Billing"),
                        n("ingest", "transform", "Ingestion"),
                        n("normalize", "transform", "Normalization"),
                        n("warehouse", "store", "Data Warehouse"),
                        n("dashboard", "sink", "Executive Dashboard"),
                        n("forecast", "sink", "Forecast Service"),
                    ],
                    groups=[
                        g("source-zone", "Source", ["crm", "billing"]),
                        g("platform-zone", "Platform", ["ingest", "normalize", "warehouse"]),
                        g("consumer-zone", "Consumer", ["dashboard", "forecast"]),
                    ],
                    edges=[
                        e("crm-ingest", "crm", "ingest", "customer-data"),
                        e("billing-ingest", "billing", "ingest", "invoice-data"),
                        e("ingest-normalize", "ingest", "normalize", "raw-batch"),
                        e("normalize-warehouse", "normalize", "warehouse", "curated-data"),
                        e("warehouse-dashboard", "warehouse", "dashboard", "KPI-data"),
                        e("warehouse-forecast", "warehouse", "forecast", "feature-data"),
                    ],
                ),
            ),
            (
                "flowchart",
                "directed-flow-state",
                "neutral-dark",
                finalize(
                    "flowchart",
                    nodes=[
                        n("start", "start", "Bắt đầu"),
                        n("receive", "process", "Tiếp nhận hồ sơ"),
                        n("valid", "decision", "Hồ sơ hợp lệ?"),
                        n("request-info", "process", "Yêu cầu bổ sung"),
                        n("approve", "process", "Phê duyệt sơ bộ"),
                        n("risk", "decision", "Rủi ro cao?"),
                        n("complete", "terminal", "Hoàn tất"),
                        n("reject", "terminal", "Từ chối"),
                    ],
                    edges=[
                        e("start-receive", "start", "receive", "flow"),
                        e("receive-valid", "receive", "valid", "flow"),
                        e("valid-approve", "valid", "approve", "flow", guard="Có"),
                        e("valid-request", "valid", "request-info", "flow", guard="Không"),
                        e("request-receive", "request-info", "receive", "flow", guard="Đã bổ sung"),
                        e("approve-risk", "approve", "risk", "flow"),
                        e("risk-complete", "risk", "complete", "flow", guard="Không"),
                        e("risk-reject", "risk", "reject", "flow", guard="Có"),
                    ],
                ),
            ),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            for diagram_type, profile, mode, ir in cases:
                with self.subTest(profile=profile):
                    result = create_profiled_diagram(
                        request(diagram_type, profile, mode=mode),
                        ir,
                        Path(temporary) / profile,
                    )
                    ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
                    self.assertEqual(ledger["geometry_validation"]["collision_graph"]["shared_segments"], 0)
                    self.assertEqual(ledger["geometry_validation"]["collision_graph"]["undeclared_junctions"], 0)

    def test_phase7_b1_dependency_dag_routes_converging_paths_without_overlap(self) -> None:
        ir = finalize(
            "dependency-graph",
            nodes=[n(node_id, "component", label) for node_id, label in (
                ("config", "Config"),
                ("logging", "Logging"),
                ("storage", "Storage"),
                ("identity", "Identity"),
                ("catalog", "Catalog"),
                ("checkout", "Checkout"),
                ("storefront", "Storefront"),
            )],
            edges=[
                e("config-logging", "config", "logging", "dependency"),
                e("config-storage", "config", "storage", "dependency"),
                e("logging-identity", "logging", "identity", "dependency"),
                e("storage-catalog", "storage", "catalog", "dependency"),
                e("identity-checkout", "identity", "checkout", "dependency"),
                e("catalog-checkout", "catalog", "checkout", "dependency"),
                e("checkout-storefront", "checkout", "storefront", "dependency"),
                e("catalog-storefront", "catalog", "storefront", "dependency"),
            ],
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(
                request("dependency-graph", "dependency-dag", mode="neutral-light"),
                ir,
                Path(temporary) / "b1-dag",
            )
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))

        collision = ledger["geometry_validation"]["collision_graph"]
        self.assertEqual(collision["shared_segments"], 0)
        self.assertEqual(collision["undeclared_junctions"], 0)

    def test_topology_external_shell_is_presentation_only_and_group_ids_are_exact(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "dense")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
            ledger = json.loads(Path(result.ledger_path).read_text(encoding="utf-8"))
        semantic_groups = {
            element.get("data-semantic-group-id"): set(element.get("data-member-ids", "").split())
            for element in root.iter()
            if element.get("data-semantic-group-id")
        }
        self.assertEqual(
            semantic_groups,
            {
                "public-edge": {"waf", "gateway"},
                "private-services": {"identity", "order", "payment"},
                "data-zone": {"transaction-db", "log-store"},
            },
        )
        shells = [element for element in root.iter() if element.get("data-presentation-shell") == "external"]
        self.assertEqual(len(shells), 1)
        self.assertNotIn("data-semantic-id", shells[0].attrib)
        self.assertNotIn("data-semantic-group-id", shells[0].attrib)
        self.assertNotIn("data-member-ids", shells[0].attrib)
        self.assertEqual(ledger["geometry_validation"]["semantic_groups"], 3)
        self.assertEqual(ledger["geometry_validation"]["presentation_shells"], 1)

    def test_geometry_validator_rejects_external_shell_semantic_leakage(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        shell = next(element for element in root.iter() if element.get("data-presentation-shell") == "external")
        shell.set("data-semantic-id", "outside")
        shell.set("data-member-ids", "customer")
        with self.assertRaisesRegex(ProfileRenderError, "Presentation shell"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_geometry_validator_rejects_group_id_or_member_drift(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        group = next(element for element in root.iter() if element.get("data-semantic-group-id") == "data-zone")
        group.set("data-semantic-group-id", "data")
        with self.assertRaisesRegex(ProfileRenderError, "exactly cover semantic groups"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])
        group.set("data-semantic-group-id", "data-zone")
        group.set("data-member-ids", "transaction-db")
        with self.assertRaisesRegex(ProfileRenderError, "changed its exact member set"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_geometry_validator_rejects_shared_edge_segment(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        first = next(element for element in root.iter() if element.get("data-edge-id") == "identity-log")
        second = next(element for element in root.iter() if element.get("data-edge-id") == "payment-db")
        first_points = first.get("points", "").split()
        second_points = second.get("points", "").split()
        first_trunk_x = first_points[1].split(",", 1)[0]
        second_points[1] = f"{first_trunk_x},{second_points[1].split(',', 1)[1]}"
        second_points[2] = f"{first_trunk_x},{second_points[2].split(',', 1)[1]}"
        second.set("points", " ".join(second_points))
        with self.assertRaisesRegex(ProfileRenderError, "shared segment"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_geometry_validator_rejects_terminal_fan_in_port_reuse(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        first = next(element for element in root.iter() if element.get("data-edge-id") == "identity-log")
        second = next(element for element in root.iter() if element.get("data-edge-id") == "order-log")
        first_points = first.get("points", "").split()
        second_points = second.get("points", "").split()
        second_points[-1] = first_points[-1]
        second_points[-2] = f"{second_points[-2].split(',', 1)[0]},{first_points[-1].split(',', 1)[1]}"
        second.set("points", " ".join(second_points))
        with self.assertRaisesRegex(ProfileRenderError, "reuses one terminal port"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_geometry_validator_rejects_undeclared_crossing(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        declared = next((element for element in root.iter() if element.get("data-crossing-points")), None)
        self.assertIsNotNone(declared)
        assert declared is not None
        declared.attrib.pop("data-crossing-points")
        with self.assertRaisesRegex(ProfileRenderError, "without one explicit overpass declaration"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_collision_graph_rejects_crossing_receipt_copied_to_unrelated_edge(self) -> None:
        root = ET.Element(f"{{{SVG_NS}}}svg")
        edge_elements = {
            "e1": ET.SubElement(root, f"{{{SVG_NS}}}polyline", {"points": "0,5 10,5", "data-crossing-points": "5,5"}),
            "e2": ET.SubElement(root, f"{{{SVG_NS}}}polyline", {"points": "5,0 5,10"}),
            "e3": ET.SubElement(root, f"{{{SVG_NS}}}polyline", {"points": "20,0 20,10", "data-crossing-points": "5,5"}),
        }
        expected_edges = {
            "e1": {"source": "n1", "target": "n2"},
            "e2": {"source": "n3", "target": "n4"},
            "e3": {"source": "n5", "target": "n6"},
        }
        with self.assertRaises(ProfileRenderError) as caught:
            _validate_edge_collision_graph(root, edge_elements, expected_edges)
        self.assertEqual(caught.exception.code, "renderer-crossing-declaration-orphan")

    def test_geometry_validator_rejects_missing_visible_crossing_bridge(self) -> None:
        ir = dense_topology_ir()
        raw_request = request("architecture", "topology-and-zones", size="social-square")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        bridge = next((element for element in root if element.get("data-crossing-bridge")), None)
        self.assertIsNotNone(bridge)
        assert bridge is not None
        root.remove(bridge)
        with self.assertRaises(ProfileRenderError) as caught:
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])
        self.assertEqual(caught.exception.code, "renderer-crossing-bridge-mismatch")

    def test_geometry_validator_rejects_detached_port(self) -> None:
        ir = fixtures()["architecture"]
        raw_request = request("architecture", "topology-and-zones")
        plan = build_profiled_plan(ir, raw_request)
        with tempfile.TemporaryDirectory() as temporary:
            result = create_profiled_diagram(raw_request, ir, Path(temporary) / "valid")
            root = ET.fromstring(Path(result.svg_path).read_text(encoding="utf-8"))
        edge = next(element for element in root.iter() if element.get("data-edge-id") == "edge-access")
        points = edge.get("points", "").split()
        points[0] = f"0,{points[1].split(',', 1)[1]}"
        edge.set("points", " ".join(points))
        with self.assertRaisesRegex(ProfileRenderError, "detached"):
            validate_rendered_geometry(ET.tostring(root, encoding="unicode"), ir, plan["profile_binding"])

    def test_atomic_api_rejects_existing_directory_without_writing(self) -> None:
        ir = fixtures()["architecture"]
        raw_request = request("architecture", "topology-and-zones")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing"
            target.mkdir()
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram(raw_request, ir, target)
            self.assertEqual(caught.exception.code, "output-exists")
            self.assertEqual(list(target.iterdir()), [])

    def test_atomic_api_rejects_requested_symlink_parent(self) -> None:
        ir = fixtures()["architecture"]
        raw_request = request("architecture", "topology-and-zones")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_parent = root / "real"
            real_parent.mkdir()
            linked_parent = root / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(OutputFailure) as caught:
                create_profiled_diagram(raw_request, ir, linked_parent / "out")
            self.assertEqual(caught.exception.code, "output-parent-invalid")
            self.assertFalse((real_parent / "out").exists())

    def test_custom_structure_cannot_borrow_catalog_renderer(self) -> None:
        ir = fixtures()["architecture"]
        raw_request = request("architecture", "topology-and-zones")
        raw_request["structural_override"] = {"status": "custom-structure", "reason": "Use a radial topology."}
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ProfileRenderError) as caught:
                create_profiled_diagram(raw_request, ir, Path(temporary) / "custom")
        self.assertEqual(caught.exception.code, "renderer-custom-structure-unsupported")

    def test_failure_leaves_no_final_or_staging_directory(self) -> None:
        ir = copy.deepcopy(fixtures()["architecture"])
        ir["edges"][0]["target"] = "missing-node"
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "invalid"
            with self.assertRaises(Exception):
                create_profiled_diagram(request("architecture", "topology-and-zones"), ir, target)
            self.assertFalse(target.exists())
            self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
