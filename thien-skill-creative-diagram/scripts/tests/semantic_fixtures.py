"""Original minimal semantic fixtures for 39-type semantic tests."""

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


def xy_datum(item_id: str, x: float, y: float, size: float, size_unit: str) -> dict[str, Any]:
    return {"id": item_id, "x_value": x, "y_value": y, "size_value": size, "size_unit": size_unit, "missing": False}


def distribution_datum(item_id: str, samples: list[float]) -> dict[str, Any]:
    return {"id": item_id, "distribution_samples": samples, "missing": False}


def member(item_id: str, kind: str, name: str, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "kind": kind, "name": name, **extra}


def series(item_id: str, label: str, data: list[dict[str, Any]], unit: str | None = None, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "label": label, "unit": unit, "data": data, **extra}


def annotation(item_id: str, text: str, targets: list[str]) -> dict[str, Any]:
    return {"id": item_id, "text": text, "target_ids": targets}


def _content_class(collection: str) -> str:
    return {
        "nodes": "entity", "edges": "relation", "groups": "group", "lanes": "lane",
        "series": "value", "axes": "label", "annotations": "annotation", "data": "value",
    }[collection]


def finalize(diagram_type: str, **collections: list[dict[str, Any]]) -> dict[str, Any]:
    ir: dict[str, Any] = {
        "schema_version": "1.5",
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
            if collection == "nodes":
                for nested_member in item.get("members", []):
                    member_source_id = f"source-{nested_member['id']}"
                    nested_member["source_refs"] = [member_source_id]
                    reading_order.append(nested_member["id"])
                    source_items.append({"id": member_source_id, "source_kind": "natural-language", "locator": f"fixture:{nested_member['id']}", "content_class": "entity"})
                    kept.append({"source_ids": [member_source_id], "ir_ids": [nested_member["id"]], "reason": "Supplied structured member retained."})
            if collection == "series":
                for point in item["data"]:
                    point_source_id = f"source-{point['id']}"
                    point["source_refs"] = [point_source_id]
                    source_items.append({"id": point_source_id, "source_kind": "natural-language", "locator": f"fixture:{point['id']}", "content_class": "value"})
                    kept.append({"source_ids": [point_source_id], "ir_ids": [point["id"]], "reason": "Supplied quantitative datum retained."})
    ir["source_items"] = source_items
    ir["fidelity"] = {"kept": kept, "merged": [], "dropped": [], "source_rot": [], "invented_count": 0}
    requires_data = bool(ir["series"] or diagram_type in {"dp-security-matrix", "treemap", "sankey"})
    ir["accessibility"] = {"name": f"Fixture {diagram_type}", "description": "Original minimal semantic fixture.", "reading_order": reading_order, "data_representation_required": requires_data}
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
        "polar-chart": finalize("polar-chart", series=[series("series-season", "Chu kỳ", [datum("polar-spring", "Xuân", 4), datum("polar-summer", "Hạ", 7), datum("polar-autumn", "Thu", 0), datum("polar-winter", "Đông", None)], "điểm")], axes=[axis("axis-angle", "angular", "categorical", "Mùa"), axis("axis-radius", "radial", "linear", "Mức độ", domain_min=0, domain_max=10, unit="điểm")]),
        "treemap": finalize("treemap", nodes=[n("leaf-a", "leaf", "Hạng mục A", value=60, unit="triệu đồng", parent_group_id="group-region"), n("leaf-b", "leaf", "Hạng mục B", value=40, unit="triệu đồng", parent_group_id="group-region")], groups=[g("group-root", "Tổng danh mục", ["group-region"], parent_group_id=None, declared_total=100, unit="triệu đồng"), g("group-region", "Khu vực", ["leaf-a", "leaf-b"], parent_group_id="group-root", declared_total=100, unit="triệu đồng")]),
        "sankey": finalize("sankey", nodes=[n("flow-source", "source", "Nguồn"), n("flow-stage", "stage", "Xử lý"), n("flow-sink", "sink", "Đích")], edges=[e("flow-in", "flow-source", "flow-stage", "flow", amount=25, unit="hồ sơ"), e("flow-out", "flow-stage", "flow-sink", "flow", amount=25, unit="hồ sơ")]),
        "fishbone": finalize("fishbone", nodes=[n("cause-process", "cause", "Quy trình thiếu bước kiểm tra"), n("cause-system", "cause", "Hệ thống cảnh báo chậm"), n("effect-delay", "effect", "Hồ sơ xử lý trễ")], edges=[e("cause-process-effect", "cause-process", "effect-delay", "cause"), e("cause-system-effect", "cause-system", "effect-delay", "cause")], groups=[g("category-method", "Phương pháp", ["cause-process"], cause_category="Phương pháp"), g("category-technology", "Công nghệ", ["cause-system"], cause_category="Công nghệ")]),
        "wardley-map": finalize("wardley-map", nodes=[n("wardley-need", "component", "Nhu cầu", strategy={"evolution": 0.2, "value_chain_position": 0.9}), n("wardley-service", "component", "Dịch vụ", strategy={"evolution": 0.65, "value_chain_position": 0.55})], edges=[e("wardley-dependency", "wardley-need", "wardley-service", "dependency")], axes=[axis("wardley-evolution", "x", "linear", "Tiến hóa", domain_min=0, domain_max=1), axis("wardley-value", "y", "linear", "Chuỗi giá trị", domain_min=0, domain_max=1)]),
        "kanban": finalize("kanban", nodes=[n("work-ready", "work-item", "Sẵn sàng", work={"column_order": 0, "item_order": 0, "wip_limit": 2, "blocked": False}), n("work-review", "work-item", "Đang rà soát", work={"column_order": 1, "item_order": 0, "wip_limit": 1, "blocked": True})], groups=[g("column-ready", "Chờ xử lý", ["work-ready"], wip_limit=2), g("column-review", "Đang xử lý", ["work-review"], wip_limit=1)]),
        "user-journey": finalize("user-journey", nodes=[n("journey-discover", "stage", "Khám phá", journey={"stage_order": 0, "action": "Tìm thông tin", "touchpoint": "Trang hướng dẫn", "sentiment": 0.2}), n("journey-submit", "stage", "Nộp hồ sơ", journey={"stage_order": 1, "action": "Gửi biểu mẫu", "touchpoint": "Cổng dịch vụ", "sentiment": -0.1})]),
        "deployment": finalize("deployment", nodes=[n("deploy-api", "artifact", "API", placement={"zone": "Vùng ứng dụng", "host": "node-a", "artifact": "api.jar", "replicas": 2, "ports": ["8443"]}), n("deploy-db", "artifact", "Cơ sở dữ liệu", placement={"zone": "Vùng dữ liệu", "host": "db-a", "artifact": "postgres", "replicas": 1, "ports": ["5432"]})], edges=[e("runtime-db", "deploy-api", "deploy-db", "runtime", relation_kind="runtime")]),
        "dependency-graph": finalize("dependency-graph", nodes=[n("dependency-a", "component", "A"), n("dependency-b", "component", "B"), n("dependency-c", "component", "C")], edges=[e("dependency-ab", "dependency-a", "dependency-b", "dependency"), e("dependency-bc", "dependency-b", "dependency-c", "dependency"), e("dependency-ca", "dependency-c", "dependency-a", "dependency")]),
        "uml-class": finalize("uml-class", nodes=[n("class-customer", "class", "Customer", members=[member("attribute-customer-id", "attribute", "id", data_type="UUID", visibility="private"), member("operation-submit", "operation", "submit", signature="submit(): void", visibility="public")]), n("class-order", "class", "Order", members=[member("attribute-order-id", "attribute", "id", data_type="UUID", visibility="private")])], edges=[e("uml-association", "class-customer", "class-order", "association", relation_kind="association", source_multiplicity="1", target_multiplicity="0..*")]),
        "story-map": finalize("story-map", nodes=[n("story-login", "story", "Đăng nhập", story={"backbone_order": 0, "story_order": 0, "release_slice": "R1", "cut_status": "above"}), n("story-export", "story", "Xuất dữ liệu", story={"backbone_order": 1, "story_order": 0, "release_slice": None, "cut_status": "unassigned"})], groups=[g("release-r1", "Release 1", ["story-login"], release_slice="R1")]),
        "database-schema": finalize("database-schema", nodes=[n("table-customer", "table", "customer", members=[member("column-customer-id", "column", "id", data_type="uuid", constraints=["primary-key", "not-null"]), member("index-customer-id", "index", "pk_customer", indexed_member_ids=["column-customer-id"], index_unique=True)]), n("table-order", "table", "sales_order", members=[member("column-order-id", "column", "id", data_type="uuid", constraints=["primary-key"]), member("column-order-customer", "column", "customer_id", data_type="uuid", constraints=["not-null"]), member("index-order-customer", "index", "ix_order_customer", indexed_member_ids=["column-order-customer", "column-order-id"], index_unique=False)])], edges=[e("foreign-key-order-customer", "table-order", "table-customer", "foreign-key", relation_kind="foreign-key", source_member="column-order-customer", target_member="column-customer-id")]),
    }


def legacy_fixtures() -> dict[str, dict[str, Any]]:
    """Return the historical 27-type visual fixtures without implying v1.5 render coverage."""

    return dict(list(fixtures().items())[:27])


def variant_fixtures() -> dict[str, dict[str, Any]]:
    dumbbell = finalize(
        "bar-chart",
        series=[
            series("series-before", "Trước", [datum("before-a", "A", -2), datum("before-b", "B", 0)], "điểm"),
            series("series-after", "Sau", [datum("after-a", "A", 4), datum("after-b", "B", 6)], "điểm"),
        ],
        axes=[axis("axis-dumbbell-category", "x", "categorical", "Nhóm"), axis("axis-dumbbell-value", "y", "linear", "Điểm", domain_min=-5, domain_max=10, unit="điểm")],
    )
    dumbbell["diagram"]["variant_ids"] = ["CAP-V17"]

    slopegraph = finalize(
        "line-chart",
        series=[
            series("series-alpha", "Alpha", [datum("alpha-before", "Trước", 2), datum("alpha-after", "Sau", 8)], "điểm"),
            series("series-beta", "Beta", [datum("beta-before", "Trước", 7), datum("beta-after", "Sau", 4)], "điểm"),
        ],
        axes=[axis("axis-slope-state", "x", "ordinal", "Trạng thái"), axis("axis-slope-value", "y", "linear", "Điểm", domain_min=0, domain_max=10, unit="điểm")],
    )
    slopegraph["diagram"]["variant_ids"] = ["CAP-V18"]

    distribution = {
        "method": "histogram",
        "domain_min": -2,
        "domain_max": 2,
        "bin_count": 4,
        "bin_edges": [-2, -1, 0, 1, 2],
        "bandwidth": None,
        "amplitude_normalization": "global-max",
        "shared_domain": True,
        "shared_bins": True,
    }
    ridgeline = finalize(
        "line-chart",
        series=[
            series("series-north", "Miền Bắc", [distribution_datum("samples-north", [-1.5, -0.5, 0.2, 1.2, 2.0])], "điểm", distribution=copy.deepcopy(distribution)),
            series("series-south", "Miền Nam", [distribution_datum("samples-south", [-1.2, -0.2, 0.4, 0.8, 1.6])], "điểm", distribution=copy.deepcopy(distribution)),
        ],
        axes=[axis("axis-ridge-domain", "x", "linear", "Giá trị", domain_min=-2, domain_max=2, unit="điểm"), axis("axis-ridge-amplitude", "y", "linear", "Mật độ chuẩn hóa", domain_min=0, domain_max=1, unit=None)],
    )
    ridgeline["diagram"]["variant_ids"] = ["CAP-V19"]

    bubble = finalize(
        "scatter-plot",
        series=[series("series-bubble", "Danh mục", [xy_datum("bubble-a", -2, 3, 0, "triệu đồng"), xy_datum("bubble-b", 6, -1, 25, "triệu đồng")], "điểm")],
        axes=[
            axis("axis-bubble-x", "x", "linear", "Trục X", domain_min=-5, domain_max=10, unit="điểm x"),
            axis("axis-bubble-y", "y", "linear", "Trục Y", domain_min=-5, domain_max=10, unit="điểm"),
            axis("axis-bubble-size", "size", "linear", "Quy mô", domain_min=0, domain_max=30, unit="triệu đồng"),
        ],
    )
    bubble["diagram"]["variant_ids"] = ["CAP-V20"]
    return {"CAP-V17": dumbbell, "CAP-V18": slopegraph, "CAP-V19": ridgeline, "CAP-V20": bubble}


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
    elif diagram_type == "polar-chart": ir["series"][0]["data"][0]["value"] = -1
    elif diagram_type == "treemap": ir["groups"][1]["declared_total"] = 99
    elif diagram_type == "sankey": ir["edges"][1]["amount"] = 24
    elif diagram_type == "fishbone": ir["edges"][1]["target"] = "cause-process"
    elif diagram_type == "wardley-map": ir["nodes"][0]["strategy"]["evolution"] = 1.1
    elif diagram_type == "kanban": ir["nodes"][1]["work"]["column_order"] = 0
    elif diagram_type == "user-journey": ir["nodes"].reverse()
    elif diagram_type == "deployment": ir["nodes"][0].pop("placement")
    elif diagram_type == "dependency-graph": ir["edges"][0]["kind"] = "association"
    elif diagram_type == "uml-class": ir["edges"][0].pop("relation_kind")
    elif diagram_type == "story-map": ir["nodes"][1]["story"]["release_slice"] = "R2"
    elif diagram_type == "database-schema": ir["nodes"][0]["members"][1]["indexed_member_ids"] = ["column-order-id"]
    return ir
