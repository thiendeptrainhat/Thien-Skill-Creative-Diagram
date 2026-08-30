"""Exact original P-18 pilot fixtures locked by the approved P-16 contract.

This evidence-only module owns no runtime/package behavior. It converts the
owner-approved abstract case contract into independently authored semantic IR.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "thien-skill-creative-diagram" / "scripts"
TEST_DIR = SCRIPT_DIR / "tests"
for _path in (SCRIPT_DIR, TEST_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from diagram_core import semantic_hash  # noqa: E402
from semantic_fixtures import (  # noqa: E402
    axis,
    datum,
    distribution_datum,
    e,
    finalize,
    g,
    lane,
    n,
    series,
    xy_datum,
)
from semantic_grammars import validate_semantics  # noqa: E402


MODES = ("neutral-light", "neutral-dark", "editorial")

CASE_META: dict[str, dict[str, str]] = {
    "P18-C01-ARCH": {"slug": "architecture", "type": "architecture", "capability": "CAP-T01", "title": "Phê duyệt hồ sơ số", "reading": "Theo dõi tuyến phê duyệt qua bốn vùng tin cậy."},
    "P18-C02-SWIM": {"slug": "swimlane", "type": "swimlane", "capability": "CAP-T08", "title": "Luồng chứng từ thu tiền", "reading": "Đọc từ trái sang phải theo handoff (1) đến (5)."},
    "P18-C03-SANKEY": {"slug": "sankey", "type": "sankey", "capability": "CAP-T30", "title": "Dòng nước đô thị", "reading": "Độ rộng dải biểu diễn chính xác lưu lượng ML/ngày."},
    "P18-C04-TREEMAP": {"slug": "treemap", "type": "treemap", "capability": "CAP-T29", "title": "Phân bổ quỹ cộng đồng", "reading": "Diện tích lá biểu diễn tỷ trọng trong tổng 100 đơn vị."},
    "P18-C05-WARDLEY": {"slug": "wardley-map", "type": "wardley-map", "capability": "CAP-T32", "title": "Bản đồ dịch vụ cấp phép", "reading": "Vị trí thể hiện chuỗi giá trị và mức tiến hóa đã khai báo."},
    "P18-C06-DEPLOY": {"slug": "deployment", "type": "deployment", "capability": "CAP-T35", "title": "Triển khai dịch vụ phê duyệt", "reading": "Đọc theo vùng, host, artifact và quan hệ runtime."},
    "P18-C07-JOURNEY": {"slug": "user-journey", "type": "user-journey", "capability": "CAP-T34", "title": "Hành trình đăng ký thư viện", "reading": "Theo dõi hành động, điểm chạm và cảm xúc qua năm giai đoạn."},
    "P18-C08-FISH": {"slug": "fishbone", "type": "fishbone", "capability": "CAP-T31", "title": "Giả thuyết nguyên nhân báo cáo trễ", "reading": "Các nhánh là giả thuyết phân tích, không phải quan hệ nhân quả đã chứng minh."},
    "P18-V17-DUMBBELL": {"slug": "dumbbell", "type": "bar-chart", "capability": "CAP-V17", "title": "Thời gian phản hồi trung vị", "reading": "So sánh Trước và Sau trên cùng thang phút bắt đầu từ 0."},
    "P18-V18-SLOPE": {"slug": "slopegraph", "type": "line-chart", "capability": "CAP-V18", "title": "Số ngày xử lý trung vị", "reading": "So sánh hướng và thứ hạng giữa Q1 và Q2."},
    "P18-V19-RIDGE": {"slug": "ridgeline", "type": "line-chart", "capability": "CAP-V19", "title": "Phân bố thời lượng cuộc gọi", "reading": "Ba histogram dùng chung miền, bins và chuẩn hóa biên độ global-max."},
    "P18-V20-BUBBLE": {"slug": "bubble", "type": "scatter-plot", "capability": "CAP-V20", "title": "Danh mục dự án", "reading": "Vị trí biểu diễn tác động/nỗ lực; diện tích biểu diễn ngân sách."},
}


def _title(ir: dict[str, Any], case_id: str) -> dict[str, Any]:
    meta = CASE_META[case_id]
    ir["request_id"] = f"request-{case_id.lower()}"
    ir["diagram"]["title"] = meta["title"]
    ir["accessibility"]["name"] = meta["title"]
    ir["accessibility"]["description"] = meta["reading"]
    return validate_semantics(ir)


def architecture_case() -> dict[str, Any]:
    ir = finalize(
        "architecture",
        nodes=[
            n("arch-applicant", "actor", "Người nộp"),
            n("arch-api", "gateway", "Cổng API"),
            n("arch-identity", "service", "Dịch vụ định danh"),
            n("arch-approval", "service", "Dịch vụ phê duyệt"),
            n("arch-records", "data-store", "Kho hồ sơ"),
            n("arch-audit", "data-store", "Nhật ký bất biến"),
            n("arch-notify", "service", "Dịch vụ thông báo"),
        ],
        groups=[
            g("zone-public", "Công khai", ["arch-applicant"]),
            g("zone-app", "Ứng dụng", ["arch-api", "arch-identity", "arch-approval", "arch-notify"]),
            g("zone-data", "Dữ liệu", ["arch-records"]),
            g("zone-audit", "Kiểm toán", ["arch-audit"]),
        ],
        edges=[
            e("arch-submit", "arch-applicant", "arch-api", "request"),
            e("arch-route", "arch-api", "arch-approval", "request"),
            e("arch-verify", "arch-approval", "arch-identity", "request"),
            e("arch-verified", "arch-identity", "arch-approval", "response"),
            e("arch-store", "arch-approval", "arch-records", "transfer"),
            e("arch-log", "arch-approval", "arch-audit", "transfer"),
            e("arch-notification", "arch-approval", "arch-notify", "event"),
        ],
    )
    return _title(ir, "P18-C01-ARCH")


def swimlane_case() -> dict[str, Any]:
    ir = finalize(
        "swimlane",
        nodes=[
            n("sw-check-customer", "money", "Séc"), n("sw-check-mail", "money", "Séc"),
            n("sw-check-cash", "money", "Séc"), n("sw-check-bank", "money", "Séc"),
            n("sw-notice-customer", "document", "Giấy báo chuyển tiền"), n("sw-notice-mail", "document", "Giấy báo chuyển tiền"),
            n("sw-notice-ar", "document", "Giấy báo chuyển tiền"), n("sw-listing-mail", "listing", "Bảng kê chuyển tiền"),
            n("sw-listing-cash", "listing", "Bảng kê chuyển tiền"), n("sw-listing-ledger", "listing", "Bảng kê chuyển tiền"),
            n("sw-file-ar", "file", "Tệp phải thu"), n("sw-file-ledger", "file", "Tệp sổ cái"),
        ],
        edges=[
            e("sw-e01", "sw-check-customer", "sw-check-mail", "handoff", order=0, label="(1)"),
            e("sw-e02", "sw-check-mail", "sw-check-cash", "handoff", order=1, label="(2)"),
            e("sw-e03", "sw-check-cash", "sw-check-bank", "handoff", order=2, label="(3)"),
            e("sw-e04", "sw-notice-customer", "sw-notice-mail", "handoff", order=3, label="(1)"),
            e("sw-e05", "sw-notice-mail", "sw-notice-ar", "handoff", order=4, label="(4)"),
            e("sw-e06", "sw-notice-ar", "sw-file-ar", "handoff", order=5, label="(4)"),
            e("sw-e07", "sw-listing-mail", "sw-listing-cash", "handoff", order=6, label="(2)"),
            e("sw-e08", "sw-listing-cash", "sw-listing-ledger", "handoff", order=7, label="(5)"),
            e("sw-e09", "sw-listing-ledger", "sw-file-ledger", "handoff", order=8, label="(5)"),
            e("sw-e10", "sw-file-ar", "sw-file-ledger", "handoff", order=9, label="(5)"),
        ],
        lanes=[
            lane("sw-lane-customer", "Khách hàng", ["sw-check-customer", "sw-notice-customer"], 0),
            lane("sw-lane-mail", "Phòng thư", ["sw-check-mail", "sw-notice-mail", "sw-listing-mail"], 1),
            lane("sw-lane-cash", "Thu tiền", ["sw-check-cash", "sw-listing-cash"], 2),
            lane("sw-lane-ar", "Phải thu", ["sw-notice-ar", "sw-file-ar"], 3),
            lane("sw-lane-ledger", "Sổ cái", ["sw-listing-ledger", "sw-file-ledger"], 4),
            lane("sw-lane-bank", "Ngân hàng", ["sw-check-bank"], 5),
        ],
    )
    return _title(ir, "P18-C02-SWIM")


def sankey_case() -> dict[str, Any]:
    ir = finalize(
        "sankey",
        nodes=[
            n("water-intake", "source", "Intake"), n("water-pretreat", "stage", "Pretreatment"),
            n("water-reject", "sink", "Reject"), n("water-filter", "stage", "Filtration"),
            n("water-wash", "sink", "Washwater"), n("water-distribution", "sink", "Distribution"),
            n("water-sludge", "sink", "Sludge"),
        ],
        edges=[
            e("water-e01", "water-intake", "water-pretreat", "flow", amount=92, unit="ML/day"),
            e("water-e02", "water-intake", "water-reject", "flow", amount=8, unit="ML/day"),
            e("water-e03", "water-pretreat", "water-filter", "flow", amount=88, unit="ML/day"),
            e("water-e04", "water-pretreat", "water-wash", "flow", amount=4, unit="ML/day"),
            e("water-e05", "water-filter", "water-distribution", "flow", amount=84, unit="ML/day"),
            e("water-e06", "water-filter", "water-sludge", "flow", amount=4, unit="ML/day"),
        ],
    )
    return _title(ir, "P18-C03-SANKEY")


def treemap_case() -> dict[str, Any]:
    leaves = [
        n("grant-literacy", "leaf", "Literacy", value=15, unit="units", parent_group_id="grant-community"),
        n("grant-digital", "leaf", "Digital access", value=10, unit="units", parent_group_id="grant-community"),
        n("grant-outreach", "leaf", "Outreach", value=15, unit="units", parent_group_id="grant-community"),
        n("grant-wetlands", "leaf", "Wetlands", value=20, unit="units", parent_group_id="grant-environment"),
        n("grant-trees", "leaf", "Urban trees", value=15, unit="units", parent_group_id="grant-environment"),
        n("grant-paths", "leaf", "Walking paths", value=10, unit="units", parent_group_id="grant-mobility"),
        n("grant-stops", "leaf", "Accessible stops", value=15, unit="units", parent_group_id="grant-mobility"),
    ]
    groups = [
        g("grant-root", "Annual community grant", ["grant-community", "grant-environment", "grant-mobility"], parent_group_id=None, declared_total=100, unit="units"),
        g("grant-community", "Community", ["grant-literacy", "grant-digital", "grant-outreach"], parent_group_id="grant-root", declared_total=40, unit="units"),
        g("grant-environment", "Environment", ["grant-wetlands", "grant-trees"], parent_group_id="grant-root", declared_total=35, unit="units"),
        g("grant-mobility", "Mobility", ["grant-paths", "grant-stops"], parent_group_id="grant-root", declared_total=25, unit="units"),
    ]
    return _title(finalize("treemap", nodes=leaves, groups=groups), "P18-C04-TREEMAP")


def wardley_case() -> dict[str, Any]:
    coords = [
        ("wardley-portal", "Resident portal", 0.35, 0.95),
        ("wardley-processing", "Application processing", 0.45, 0.75),
        ("wardley-workflow", "Case workflow", 0.55, 0.55),
        ("wardley-identity", "Identity", 0.70, 0.40),
        ("wardley-hosting", "Hosting", 0.82, 0.20),
    ]
    nodes = [n(item_id, "component", label, strategy={"evolution": x, "value_chain_position": y}) for item_id, label, x, y in coords]
    edges = [
        e("wardley-e01", "wardley-portal", "wardley-processing", "dependency"),
        e("wardley-e02", "wardley-processing", "wardley-workflow", "dependency"),
        e("wardley-e03", "wardley-workflow", "wardley-identity", "dependency"),
        e("wardley-e04", "wardley-workflow", "wardley-hosting", "dependency"),
    ]
    axes = [axis("wardley-x", "x", "linear", "Evolution", domain_min=0, domain_max=1), axis("wardley-y", "y", "linear", "Value chain", domain_min=0, domain_max=1)]
    return _title(finalize("wardley-map", nodes=nodes, edges=edges, axes=axes), "P18-C05-WARDLEY")


def deployment_case() -> dict[str, Any]:
    placements = [
        ("deploy-gateway", "Gateway", "Edge", "gateway-a", "api-gateway", 2, ["443"]),
        ("deploy-approval", "Approval", "App", "app-a", "approval-service", 3, ["8443"]),
        ("deploy-worker", "Worker", "App", "worker-a", "document-worker", 2, []),
        ("deploy-postgres", "Postgres", "Data", "db-a", "postgres", 1, ["5432"]),
        ("deploy-store", "Object store", "Data", "store-a", "object-store", 2, ["9000"]),
    ]
    nodes = [n(item_id, "artifact", label, placement={"zone": zone, "host": host, "artifact": artifact, "replicas": replicas, "ports": ports}) for item_id, label, zone, host, artifact, replicas, ports in placements]
    edges = [
        e("deploy-e01", "deploy-gateway", "deploy-approval", "runtime", relation_kind="runtime"),
        e("deploy-e02", "deploy-approval", "deploy-postgres", "runtime", relation_kind="runtime"),
        e("deploy-e03", "deploy-approval", "deploy-store", "runtime", relation_kind="runtime"),
        e("deploy-e04", "deploy-approval", "deploy-worker", "runtime", relation_kind="runtime"),
        e("deploy-e05", "deploy-worker", "deploy-store", "runtime", relation_kind="runtime"),
    ]
    return _title(finalize("deployment", nodes=nodes, edges=edges), "P18-C06-DEPLOY")


def journey_case() -> dict[str, Any]:
    stages = [
        ("journey-discover", "Discover", 0, "Read eligibility", "Website", -0.1),
        ("journey-prepare", "Prepare", 1, "Gather ID", "Checklist", 0.2),
        ("journey-apply", "Apply", 2, "Submit form", "Portal", -0.4),
        ("journey-verify", "Verify", 3, "Respond to question", "Email", 0.3),
        ("journey-activate", "Activate", 4, "Receive card", "App", 0.8),
    ]
    nodes = [n(item_id, "stage", label, journey={"stage_order": order, "action": action, "touchpoint": touchpoint, "sentiment": sentiment}) for item_id, label, order, action, touchpoint, sentiment in stages]
    axes = [axis("journey-sentiment", "y", "linear", "Sentiment", domain_min=-1, domain_max=1, unit="score")]
    return _title(finalize("user-journey", nodes=nodes, axes=axes), "P18-C07-JOURNEY")


def fishbone_case() -> dict[str, Any]:
    cause_groups = {
        "People": ["Thiếu người ca tối", "Bàn giao không rõ"],
        "Process": ["Ưu tiên mẫu chưa thống nhất", "Duyệt hai lần"],
        "Equipment": ["Máy quét tem gián đoạn", "Máy ly tâm chờ bảo trì"],
        "Data": ["Mã mẫu trùng", "Thời gian nhận thiếu"],
        "Environment": ["Quãng đường chuyển mẫu dài", "Nhiệt độ kho không ổn định"],
    }
    nodes = [n("fish-effect", "effect", "Báo cáo mẫu xét nghiệm trễ")]
    groups: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for group_index, (group_name, labels) in enumerate(cause_groups.items()):
        member_ids: list[str] = []
        for cause_index, label in enumerate(labels):
            cause_id = f"fish-cause-{group_index + 1}-{cause_index + 1}"
            member_ids.append(cause_id)
            nodes.append(n(cause_id, "cause", label))
            edges.append(e(f"fish-edge-{group_index + 1}-{cause_index + 1}", cause_id, "fish-effect", "cause"))
        groups.append(g(f"fish-group-{group_index + 1}", group_name, member_ids, cause_category=group_name))
    return _title(finalize("fishbone", nodes=nodes, edges=edges, groups=groups), "P18-C08-FISH")


def dumbbell_case() -> dict[str, Any]:
    categories = [("North", 18, 12), ("Central", 25, 17), ("South", 20, 15), ("Remote", 30, 22)]
    ir = finalize(
        "bar-chart",
        series=[
            series("dumbbell-before", "Before", [datum(f"db-before-{name.lower()}", name, before) for name, before, _ in categories], "minutes"),
            series("dumbbell-after", "After", [datum(f"db-after-{name.lower()}", name, after) for name, _, after in categories], "minutes"),
        ],
        axes=[axis("dumbbell-category", "x", "categorical", "Region"), axis("dumbbell-value", "y", "linear", "Median response time", domain_min=0, domain_max=30, unit="minutes")],
    )
    ir["diagram"]["variant_ids"] = ["CAP-V17"]
    return _title(ir, "P18-V17-DUMBBELL")


def slopegraph_case() -> dict[str, Any]:
    values = [("Permits", 9.2, 7.4), ("Records", 5.8, 6.1), ("Grants", 12.5, 9.8)]
    ir = finalize(
        "line-chart",
        series=[series(f"slope-{name.lower()}", name, [datum(f"slope-{name.lower()}-q1", "Q1", q1), datum(f"slope-{name.lower()}-q2", "Q2", q2)], "days") for name, q1, q2 in values],
        axes=[axis("slope-state", "x", "ordinal", "Quarter"), axis("slope-value", "y", "linear", "Median processing days", domain_min=0, domain_max=14, unit="days")],
    )
    ir["diagram"]["variant_ids"] = ["CAP-V18"]
    return _title(ir, "P18-V18-SLOPE")


def ridgeline_case() -> dict[str, Any]:
    distribution = {
        "method": "histogram", "domain_min": 0, "domain_max": 12,
        "bin_count": 6, "bin_edges": [0, 2, 4, 6, 8, 10, 12],
        "bandwidth": None, "amplitude_normalization": "global-max",
        "shared_domain": True, "shared_bins": True,
    }
    samples = {"Team A": [3, 4, 4, 5, 6, 7], "Team B": [4, 5, 6, 6, 7, 8], "Team C": [2, 3, 5, 7, 9, 11]}
    ir = finalize(
        "line-chart",
        series=[series(f"ridge-{label.lower().replace(' ', '-')}", label, [distribution_datum(f"ridge-data-{label[-1].lower()}", values)], "minutes", distribution=copy.deepcopy(distribution)) for label, values in samples.items()],
        axes=[axis("ridge-domain", "x", "linear", "Call handling duration", domain_min=0, domain_max=12, unit="minutes"), axis("ridge-amplitude", "y", "linear", "Normalized density", domain_min=0, domain_max=1)],
    )
    ir["diagram"]["variant_ids"] = ["CAP-V19"]
    return _title(ir, "P18-V19-RIDGE")


def bubble_case() -> dict[str, Any]:
    observations = [("Accessibility", 9, 4, 2.4), ("Search", 7, 5, 1.6), ("Migration", 8, 9, 5.2), ("Notifications", 5, 3, 0.9)]
    ir = finalize(
        "scatter-plot",
        series=[series("bubble-projects", "Project portfolio", [dict(xy_datum(f"bubble-{label.lower()}", x, y, size, "budget_M"), label=label) for label, x, y, size in observations], "score")],
        axes=[
            axis("bubble-impact", "x", "linear", "Impact", domain_min=0, domain_max=10, unit="score"),
            axis("bubble-effort", "y", "linear", "Effort", domain_min=0, domain_max=10, unit="score"),
            axis("bubble-budget", "size", "linear", "Budget", domain_min=0, domain_max=5.2, unit="budget_M"),
        ],
    )
    ir["diagram"]["variant_ids"] = ["CAP-V20"]
    return _title(ir, "P18-V20-BUBBLE")


CASE_BUILDERS = {
    "P18-C01-ARCH": architecture_case,
    "P18-C02-SWIM": swimlane_case,
    "P18-C03-SANKEY": sankey_case,
    "P18-C04-TREEMAP": treemap_case,
    "P18-C05-WARDLEY": wardley_case,
    "P18-C06-DEPLOY": deployment_case,
    "P18-C07-JOURNEY": journey_case,
    "P18-C08-FISH": fishbone_case,
    "P18-V17-DUMBBELL": dumbbell_case,
    "P18-V18-SLOPE": slopegraph_case,
    "P18-V19-RIDGE": ridgeline_case,
    "P18-V20-BUBBLE": bubble_case,
}


def build_case(case_id: str) -> dict[str, Any]:
    try:
        return CASE_BUILDERS[case_id]()
    except KeyError as error:
        raise ValueError(f"Unknown P-18 case: {case_id}") from error


def all_cases() -> dict[str, dict[str, Any]]:
    return {case_id: builder() for case_id, builder in CASE_BUILDERS.items()}


def source_hash(case_id: str) -> str:
    return semantic_hash(build_case(case_id))


__all__ = ["CASE_BUILDERS", "CASE_META", "MODES", "all_cases", "build_case", "source_hash"]
