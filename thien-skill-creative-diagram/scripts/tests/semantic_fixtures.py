"""Original minimal semantic fixtures for P-05 tests."""

from __future__ import annotations

import copy
from typing import Any


COLLECTIONS = ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations")


def n(item_id: str, role: str, label: str, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "role": role, "label": label, **extra}


def e(item_id: str, source: str, target: str, kind: str, directed: bool = True, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "source": source, "target": target, "kind": kind, "directed": directed, **extra}


def g(item_id: str, label: str, members: list[str], **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "label": label, "member_ids": members, **extra}


def lane(item_id: str, label: str, members: list[str], order: int) -> dict[str, Any]:
    return {"id": item_id, "label": label, "owner": label, "member_ids": members, "order": order}


def axis(item_id: str, dimension: str, scale: str, label: str, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "dimension": dimension, "scale": scale, "label": label, **extra}


def datum(item_id: str, domain: str | int | float, value: float | int | None, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "domain": domain, "value": value, "missing": value is None, **extra}


def series(item_id: str, label: str, data: list[dict[str, Any]], unit: str | None = None) -> dict[str, Any]:
    return {"id": item_id, "label": label, "unit": unit, "data": data}


def annotation(item_id: str, text: str, targets: list[str]) -> dict[str, Any]:
    return {"id": item_id, "text": text, "target_ids": targets}


def _content_class(collection: str) -> str:
    return {
        "nodes": "entity", "edges": "relation", "groups": "group", "lanes": "lane",
        "series": "value", "axes": "label", "annotations": "annotation", "data": "value",
    }[collection]


def finalize(diagram_type: str, **collections: list[dict[str, Any]]) -> dict[str, Any]:
    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "request_id": f"request-{diagram_type}",
        "diagram": {"type": diagram_type, "variant_ids": [], "language": "vi", "title": f"Fixture {diagram_type}", "detail": "faithful", "audience": "mixed"},
        "selection": {"mode": "auto", "confidence": "high", "evidence": [f"request:fixture {diagram_type}"], "alternatives": [], "assumption": None},
        **{name: copy.deepcopy(collections.get(name, [])) for name in COLLECTIONS},
    }
    source_items: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    reading_order: list[str] = []
    for collection in COLLECTIONS:
        for item in ir[collection]:
            source_id = f"source-{item['id']}"
            item["source_refs"] = [source_id]
            reading_order.append(item["id"])
            source_items.append({"id": source_id, "source_kind": "natural-language", "locator": f"fixture:{item['id']}", "content_class": _content_class(collection)})
            kept.append({"source_ids": [source_id], "ir_ids": [item["id"]], "reason": "Supplied semantic item retained."})
            if collection == "series":
                for point in item["data"]:
                    point_source_id = f"source-{point['id']}"
                    point["source_refs"] = [point_source_id]
                    source_items.append({"id": point_source_id, "source_kind": "natural-language", "locator": f"fixture:{point['id']}", "content_class": "value"})
                    kept.append({"source_ids": [point_source_id], "ir_ids": [point["id"]], "reason": "Supplied quantitative datum retained."})
    ir["source_items"] = source_items
    ir["fidelity"] = {"kept": kept, "merged": [], "dropped": [], "source_rot": [], "invented_count": 0}
    ir["accessibility"] = {"name": f"Fixture {diagram_type}", "description": "Original minimal semantic fixture.", "reading_order": reading_order, "data_representation_required": bool(ir["series"] or diagram_type == "dp-security-matrix")}
    return ir


def fixtures() -> dict[str, dict[str, Any]]:
    return {
        "architecture": finalize("architecture", nodes=[n("actor-user", "actor", "Người dùng"), n("service-api", "service", "Cổng dịch vụ")], edges=[e("edge-access", "actor-user", "service-api", "dependency")], groups=[g("boundary-trust", "Vùng tin cậy", ["service-api"])]),
        "it-current-state": finalize("it-current-state", nodes=[n("system-legacy", "system", "Hệ thống cũ", state="legacy"), n("system-core", "system", "Nền tảng lõi", state="active")], edges=[e("edge-integration", "system-legacy", "system-core", "integration")], groups=[g("group-finance", "Khối tài chính", ["system-legacy", "system-core"])]),
        "flowchart": finalize("flowchart", nodes=[n("start-request", "start", "Bắt đầu"), n("decision-valid", "decision", "Hợp lệ?"), n("terminal-ok", "terminal", "Chấp nhận"), n("terminal-no", "terminal", "Từ chối")], edges=[e("edge-review", "start-request", "decision-valid", "flow"), e("edge-yes", "decision-valid", "terminal-ok", "flow", guard="Có"), e("edge-no", "decision-valid", "terminal-no", "flow", guard="Không")]),
        "sequence": finalize("sequence", nodes=[n("participant-client", "participant", "Ứng dụng"), n("participant-api", "participant", "API")], edges=[e("message-request", "participant-client", "participant-api", "request", order=0), e("message-response", "participant-api", "participant-client", "response", order=1)]),
        "state-machine": finalize("state-machine", nodes=[n("state-new", "initial", "Mới"), n("state-review", "state", "Đang duyệt"), n("state-done", "terminal", "Hoàn tất")], edges=[e("transition-review", "state-new", "state-review", "transition"), e("transition-done", "state-review", "state-done", "transition")]),
        "er-data-model": finalize("er-data-model", nodes=[n("entity-customer", "entity", "Khách hàng"), n("entity-order", "entity", "Đơn hàng")], edges=[e("relation-orders", "entity-customer", "entity-order", "one-to-many")]),
        "timeline": finalize("timeline", nodes=[n("event-open", "event", "Mở", start="2026-08-15T08:00:00+07:00"), n("event-close", "milestone", "Đóng", start="2026-08-15T17:00:00+07:00")]),
        "swimlane": finalize("swimlane", nodes=[n("activity-send", "activity", "Gửi hồ sơ"), n("activity-review", "activity", "Duyệt hồ sơ")], edges=[e("handoff-review", "activity-send", "activity-review", "handoff", order=0)], lanes=[lane("lane-requester", "Người đề nghị", ["activity-send"], 0), lane("lane-reviewer", "Người duyệt", ["activity-review"], 1)]),
        "quadrant": finalize("quadrant", series=[series("series-items", "Tình huống", [datum("point-a", 2, 8), datum("point-b", 7, 3)])], axes=[axis("axis-x", "x", "linear", "Tác động", domain_min=0, domain_max=10, unit="điểm"), axis("axis-y", "y", "linear", "Khả năng", domain_min=0, domain_max=10, unit="điểm")]),
        "radar": finalize("radar", series=[series("series-team", "Đội A", [datum("radar-one", "Tốc độ", 4), datum("radar-two", "Chất lượng", 3), datum("radar-three", "Ổn định", 5)], "điểm")], axes=[axis("axis-speed", "radial", "linear", "Tốc độ", domain_min=0, domain_max=5, unit="điểm"), axis("axis-quality", "radial", "linear", "Chất lượng", domain_min=0, domain_max=5, unit="điểm"), axis("axis-stability", "radial", "linear", "Ổn định", domain_min=0, domain_max=5, unit="điểm")]),
        "loop-flywheel": finalize("loop-flywheel", nodes=[n("station-learn", "station", "Học"), n("station-build", "station", "Xây"), n("station-measure", "station", "Đo")], edges=[e("cycle-build", "station-learn", "station-build", "cycle"), e("cycle-measure", "station-build", "station-measure", "cycle"), e("cycle-learn", "station-measure", "station-learn", "cycle")]),
        "nested": finalize("nested", nodes=[n("item-service", "item", "Dịch vụ")], groups=[g("group-platform", "Nền tảng", ["group-domain"]), g("group-domain", "Miền", ["item-service"], parent_group_id="group-platform")]),
        "tree": finalize("tree", nodes=[n("root-company", "root", "Công ty"), n("branch-unit", "branch", "Đơn vị"), n("leaf-team", "leaf", "Nhóm")], edges=[e("branch-unit-edge", "root-company", "branch-unit", "parent"), e("branch-team-edge", "branch-unit", "leaf-team", "parent")]),
        "org-chart": finalize("org-chart", nodes=[n("role-director", "role", "Giám đốc"), n("role-manager", "role", "Quản lý")], edges=[e("reporting-line", "role-manager", "role-director", "reports-to")]),
        "layer-stack": finalize("layer-stack", nodes=[n("control-edge", "control", "Kiểm soát biên"), n("control-data", "control", "Kiểm soát dữ liệu")], edges=[e("edge-enforce", "control-edge", "control-data", "enforcement")], lanes=[lane("layer-edge", "Biên", ["control-edge"], 0), lane("layer-data", "Dữ liệu", ["control-data"], 1)]),
        "venn": finalize("venn", nodes=[n("member-shared", "member", "Dùng chung"), n("member-outside", "outside-member", "Ngoài phạm vi")], groups=[g("set-a", "Tập A", ["member-shared"]), g("set-b", "Tập B", ["member-shared"])]),
        "pyramid-funnel": finalize("pyramid-funnel", series=[series("series-stages", "Chuyển đổi", [datum("stage-awareness", "Nhận biết", 100), datum("stage-action", "Hành động", 35)], "hồ sơ")]),
        "bar-chart": finalize("bar-chart", series=[series("series-volume", "Khối lượng", [datum("bar-january", "Tháng 1", 12), datum("bar-february", "Tháng 2", 18)], "hồ sơ")], axes=[axis("axis-category", "x", "categorical", "Tháng"), axis("axis-value", "y", "linear", "Hồ sơ", domain_min=0, domain_max=20, unit="hồ sơ")]),
        "line-chart": finalize("line-chart", series=[series("series-trend", "Xu hướng", [datum("line-one", 1, 10), datum("line-two", 2, 14)], "điểm")], axes=[axis("axis-time", "x", "ordinal", "Kỳ"), axis("axis-measure", "y", "linear", "Điểm", domain_min=0, domain_max=20, unit="điểm")]),
        "gantt": finalize("gantt", nodes=[n("task-discovery", "task", "Khảo sát", start="2026-08-15T08:00:00+07:00", end="2026-08-16T17:00:00+07:00"), n("task-build", "task", "Xây dựng", start="2026-08-17T08:00:00+07:00", end="2026-08-20T17:00:00+07:00")], edges=[e("dependency-build", "task-discovery", "task-build", "dependency")]),
        "scatter-plot": finalize("scatter-plot", series=[series("series-observations", "Quan sát", [datum("scatter-a", 2, 5), datum("scatter-b", 8, 7)])], axes=[axis("axis-cost", "x", "linear", "Chi phí", domain_min=0, domain_max=10, unit="điểm"), axis("axis-benefit", "y", "linear", "Lợi ích", domain_min=0, domain_max=10, unit="điểm")]),
        "high-level": finalize("high-level", nodes=[n("stage-ingest", "stage", "Thu nhận"), n("stage-serve", "stage", "Phục vụ")], edges=[e("progression-serve", "stage-ingest", "stage-serve", "progression")], groups=[g("group-input", "Đầu vào", ["stage-ingest"]), g("group-output", "Đầu ra", ["stage-serve"])], annotations=[annotation("annotation-governance", "Quản trị xuyên suốt", ["stage-ingest", "stage-serve"])]),
        "process": finalize("process", nodes=[n("activity-check", "activity", "Kiểm tra"), n("artifact-record", "artifact", "Biên bản")], edges=[e("flow-record", "activity-check", "artifact-record", "flow", order=0)]),
        "medallion": finalize("medallion", nodes=[n("dataset-raw", "dataset", "Dữ liệu thô"), n("dataset-curated", "dataset", "Dữ liệu chuẩn")], edges=[e("promotion-curated", "dataset-raw", "dataset-curated", "promotion")], lanes=[lane("tier-raw", "Tầng thô", ["dataset-raw"], 0), lane("tier-curated", "Tầng chuẩn", ["dataset-curated"], 1)]),
        "data-flow": finalize("data-flow", nodes=[n("source-events", "source", "Sự kiện"), n("transform-clean", "transform", "Làm sạch"), n("sink-warehouse", "sink", "Kho dữ liệu")], edges=[e("transfer-clean", "source-events", "transform-clean", "transfer"), e("transfer-store", "transform-clean", "sink-warehouse", "transfer")]),
        "dp-integration": finalize("dp-integration", nodes=[n("source-erp", "source", "ERP"), n("platform-api", "platform-service", "API nền tảng"), n("consumer-report", "consumer", "Báo cáo")], edges=[e("integration-platform", "source-erp", "platform-api", "integration"), e("integration-consumer", "platform-api", "consumer-report", "integration")], groups=[g("boundary-platform", "Nền tảng dữ liệu", ["platform-api"])]),
        "dp-security-matrix": finalize("dp-security-matrix", nodes=[n("cell-reader-store", "permission-cell", "Đọc / Kho", secondary_label="reader|store", state="allow"), n("cell-reader-api", "permission-cell", "Đọc / API", secondary_label="reader|api", state="conditional"), n("cell-admin-store", "permission-cell", "Quản trị / Kho", secondary_label="admin|store", state="allow"), n("cell-admin-api", "permission-cell", "Quản trị / API", secondary_label="admin|api", state="deny")]),
    }


def remove_material(ir: dict[str, Any], collection: str, item_id: str) -> None:
    item = next(item for item in ir[collection] if item["id"] == item_id)
    source_ids = set(item["source_refs"])
    if collection == "series":
        source_ids.update(ref for point in item["data"] for ref in point["source_refs"])
    ir[collection] = [value for value in ir[collection] if value["id"] != item_id]
    ir["source_items"] = [source for source in ir["source_items"] if source["id"] not in source_ids]
    ir["fidelity"]["kept"] = [entry for entry in ir["fidelity"]["kept"] if not set(entry["source_ids"]) & source_ids]
    ir["accessibility"]["reading_order"] = [value for value in ir["accessibility"]["reading_order"] if value != item_id]


def negative_fixture(diagram_type: str, source: dict[str, Any]) -> dict[str, Any]:
    ir = copy.deepcopy(source)
    if diagram_type == "architecture": remove_material(ir, "groups", "boundary-trust")
    elif diagram_type == "it-current-state": ir["nodes"][0].pop("state")
    elif diagram_type == "flowchart": ir["edges"][1].pop("guard")
    elif diagram_type == "sequence": ir["edges"][1]["order"] = 0
    elif diagram_type == "state-machine": ir["nodes"][2]["role"] = "state"
    elif diagram_type == "er-data-model": ir["edges"][0]["kind"] = "relationship"
    elif diagram_type == "timeline": ir["nodes"].reverse()
    elif diagram_type == "swimlane": ir["edges"][0]["kind"] = "flow"
    elif diagram_type == "quadrant": ir["series"][0]["data"][0]["domain"] = 20
    elif diagram_type == "radar": ir["axes"][1]["domain_max"] = 10
    elif diagram_type == "loop-flywheel": ir["edges"][2]["source"] = "station-learn"; ir["edges"][2]["target"] = "station-measure"
    elif diagram_type == "nested": ir["groups"][1].pop("parent_group_id")
    elif diagram_type == "tree": ir["edges"][0]["target"] = "leaf-team"
    elif diagram_type == "org-chart": ir["edges"][0]["kind"] = "escalates"; ir["edges"][0]["label"] = "escalation"
    elif diagram_type == "layer-stack": ir["lanes"][1]["order"] = 0
    elif diagram_type == "venn": remove_material(ir, "groups", "set-b")
    elif diagram_type == "pyramid-funnel": remove_material(ir, "series", "series-stages")
    elif diagram_type == "bar-chart": ir["axes"][1]["domain_min"] = 1
    elif diagram_type == "line-chart": ir["series"][0]["data"].reverse()
    elif diagram_type == "gantt": ir["nodes"][0]["end"] = "2026-08-14T17:00:00+07:00"
    elif diagram_type == "scatter-plot": ir["series"][0]["data"][0]["value"] = None
    elif diagram_type == "high-level": ir["annotations"][0]["target_ids"] = ["stage-ingest"]
    elif diagram_type == "process": ir["nodes"][1]["role"] = "activity"
    elif diagram_type == "medallion": ir["edges"][0]["kind"] = "flow"
    elif diagram_type == "data-flow": ir["nodes"][2]["role"] = "store"
    elif diagram_type == "dp-integration": ir["nodes"][2]["role"] = "store"
    elif diagram_type == "dp-security-matrix": remove_material(ir, "nodes", "cell-admin-api")
    return ir

