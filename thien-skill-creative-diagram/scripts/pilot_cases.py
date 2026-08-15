"""Original, source-traceable P-06 pilot fixtures.

These fixtures contain only project-authored synthetic data or the owner-approved
semantic inventory of the QA-only cash-receipts benchmark. They contain no
reference coordinates, styles, templates, assets, or executable content.
"""

from __future__ import annotations

import copy
from typing import Any

from semantic_grammars import validate_semantics


COLLECTIONS = ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations")


def _node(item_id: str, role: str, label: str, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "role": role, "label": label, **extra}


def _edge(item_id: str, source: str, target: str, kind: str, *, order: int | None = None, label: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"id": item_id, "source": source, "target": target, "kind": kind, "directed": True}
    if order is not None:
        value["order"] = order
    if label is not None:
        value["label"] = label
    return value


def _group(item_id: str, label: str, members: list[str]) -> dict[str, Any]:
    return {"id": item_id, "label": label, "member_ids": members}


def _lane(item_id: str, label: str, members: list[str], order: int) -> dict[str, Any]:
    return {"id": item_id, "label": label, "owner": label, "member_ids": members, "order": order}


def _axis(item_id: str, dimension: str, scale: str, label: str, **extra: Any) -> dict[str, Any]:
    return {"id": item_id, "dimension": dimension, "scale": scale, "label": label, **extra}


def _series(item_id: str, label: str, values: list[tuple[str, int]], unit: str) -> dict[str, Any]:
    return {"id": item_id, "label": label, "unit": unit, "data": [{"id": f"datum-{item_id.removeprefix('series-')}-{index + 1}", "domain": domain, "value": value, "missing": False, "label": domain} for index, (domain, value) in enumerate(values)]}


def _annotation(item_id: str, text: str, targets: list[str]) -> dict[str, Any]:
    return {"id": item_id, "text": text, "target_ids": targets}


def _content_class(collection: str) -> str:
    return {"nodes": "entity", "edges": "relation", "groups": "group", "lanes": "lane", "series": "value", "axes": "label", "annotations": "annotation", "data": "value"}[collection]


def _finalize(case_id: str, diagram_type: str, title: str, language: str, *, variant_ids: list[str] | None = None, **collections: list[dict[str, Any]]) -> dict[str, Any]:
    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "request_id": f"request-{case_id}",
        "diagram": {"type": diagram_type, "variant_ids": variant_ids or [], "language": language, "title": title, "detail": "faithful", "audience": "mixed"},
        "selection": {"mode": "manual", "confidence": "high", "evidence": [f"request:approved P-06 pilot {case_id}"], "alternatives": [], "assumption": None},
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
            source_items.append({"id": source_id, "source_kind": "natural-language", "locator": f"pilot:{case_id}:{item['id']}", "content_class": _content_class(collection)})
            kept.append({"source_ids": [source_id], "ir_ids": [item["id"]], "reason": "Approved pilot semantic item retained exactly."})
            if collection == "series":
                for datum in item["data"]:
                    datum_source = f"source-{datum['id']}"
                    datum["source_refs"] = [datum_source]
                    source_items.append({"id": datum_source, "source_kind": "natural-language", "locator": f"pilot:{case_id}:{datum['id']}", "content_class": "value"})
                    kept.append({"source_ids": [datum_source], "ir_ids": [datum["id"]], "reason": "Disclosed synthetic quantitative datum retained exactly."})
    ir["source_items"] = source_items
    ir["fidelity"] = {"kept": kept, "merged": [], "dropped": [], "source_rot": [], "invented_count": 0}
    ir["accessibility"] = {"name": title, "description": f"Original P-06 {diagram_type} pilot.", "reading_order": reading_order, "data_representation_required": diagram_type == "bar-chart"}
    return validate_semantics(ir)


def architecture_pilot() -> dict[str, Any]:
    nodes = [
        _node("actor-team", "actor", "Nhóm phát hành"),
        _node("service-build", "service", "Dịch vụ xây dựng"),
        _node("service-policy", "service", "Cổng chính sách"),
        _node("data-registry", "data-store", "Kho gói đã ký"),
        _node("service-deploy", "service", "Bộ điều phối triển khai"),
        _node("service-runtime", "service", "Dịch vụ vận hành"),
        _node("data-audit", "data-store", "Nhật ký kiểm toán"),
        _node("service-bypass", "service", "Đường tắt trực tiếp", state="denied"),
    ]
    edges = [
        _edge("edge-submit", "actor-team", "service-build", "dependency", label="gửi bản dựng"),
        _edge("edge-evaluate", "service-build", "service-policy", "dependency", label="đánh giá"),
        _edge("edge-sign", "service-policy", "data-registry", "transfer", label="ký và lưu"),
        _edge("edge-release", "data-registry", "service-deploy", "transfer", label="phát hành"),
        _edge("edge-deploy", "service-deploy", "service-runtime", "dependency", label="triển khai"),
        _edge("edge-audit-policy", "service-policy", "data-audit", "transfer", label="ghi quyết định"),
        _edge("edge-audit-runtime", "service-runtime", "data-audit", "transfer", label="ghi trạng thái"),
        _edge("edge-deny-bypass", "actor-team", "service-bypass", "dependency", label="bị từ chối"),
    ]
    groups = [
        _group("boundary-build", "Vùng xây dựng", ["service-build", "service-policy"]),
        _group("boundary-control", "Vùng kiểm soát", ["data-registry", "data-audit"]),
        _group("boundary-production", "Vùng vận hành", ["service-deploy", "service-runtime", "service-bypass"]),
    ]
    annotations = [_annotation("annotation-approved", "pattern:CAP-P05 tuyến chuẩn được kiểm soát", ["service-build", "service-policy", "data-registry", "service-deploy", "service-runtime"])]
    return _finalize("pilot-architecture", "architecture", "Tuyến triển khai được kiểm soát", "vi", nodes=nodes, edges=edges, groups=groups, annotations=annotations)


def bar_pilot() -> dict[str, Any]:
    domains = ["Quý 1", "Quý 2", "Quý 3", "Quý 4"]
    series = [
        _series("series-priority", "Ưu tiên cao", list(zip(domains, [12, 18, 9, 16])), "sự cố"),
        _series("series-standard", "Tiêu chuẩn", list(zip(domains, [24, 20, 28, 22])), "sự cố"),
    ]
    axes = [_axis("axis-quarter", "x", "categorical", "Quý"), _axis("axis-incidents", "y", "linear", "Số sự cố", unit="sự cố", domain_min=0, domain_max=30)]
    annotations = [_annotation("annotation-synthetic", "Dữ liệu tổng hợp nguyên bản chỉ dùng cho pilot; không đại diện số liệu thực tế.", ["series-priority", "series-standard"])]
    return _finalize("pilot-bar", "bar-chart", "Sự cố theo quý và mức xử lý", "vi", variant_ids=["CAP-V05"], series=series, axes=axes, annotations=annotations)


def swimlane_pilot() -> dict[str, Any]:
    nodes = [
        _node("check-customer", "money", "Séc"), _node("check-mail", "money", "Séc"), _node("check-cash", "money", "Séc"), _node("check-bank", "money", "Séc"),
        _node("notice-customer", "document", "Giấy báo chuyển tiền"), _node("notice-mail", "document", "Giấy báo chuyển tiền"), _node("notice-ar", "document", "Giấy báo chuyển tiền"),
        _node("listing-mail", "listing", "Bảng kê chuyển tiền"), _node("listing-cash", "listing", "Bảng kê chuyển tiền"), _node("listing-ledger", "listing", "Bảng kê chuyển tiền"),
        _node("file-ar", "file", "Tệp phải thu"), _node("file-ledger", "file", "Tệp sổ cái"),
    ]
    edges = [
        _edge("handoff-check-mail", "check-customer", "check-mail", "handoff", order=0, label="(1)"),
        _edge("handoff-check-cash", "check-mail", "check-cash", "handoff", order=1, label="(2)"),
        _edge("handoff-check-bank", "check-cash", "check-bank", "handoff", order=2, label="(3)"),
        _edge("handoff-notice-mail", "notice-customer", "notice-mail", "handoff", order=3, label="(1)"),
        _edge("handoff-notice-ar", "notice-mail", "notice-ar", "handoff", order=4, label="(4)"),
        _edge("handoff-notice-file", "notice-ar", "file-ar", "handoff", order=5, label="(4)"),
        _edge("handoff-listing-cash", "listing-mail", "listing-cash", "handoff", order=6, label="(2)"),
        _edge("handoff-listing-ledger", "listing-cash", "listing-ledger", "handoff", order=7, label="(5)"),
        _edge("handoff-listing-file", "listing-ledger", "file-ledger", "handoff", order=8, label="(5)"),
        _edge("handoff-file-ledger", "file-ar", "file-ledger", "handoff", order=9, label="(5)"),
    ]
    lanes = [
        _lane("lane-customer", "Khách hàng", ["check-customer", "notice-customer"], 0),
        _lane("lane-mail", "Phòng thư", ["check-mail", "notice-mail", "listing-mail"], 1),
        _lane("lane-cash", "Thu tiền", ["check-cash", "listing-cash"], 2),
        _lane("lane-ar", "Phải thu", ["notice-ar", "file-ar"], 3),
        _lane("lane-ledger", "Sổ cái", ["listing-ledger", "file-ledger"], 4),
        _lane("lane-bank", "Ngân hàng", ["check-bank"], 5),
    ]
    annotations = [
        _annotation("owner-treasury", "owner-group:Thủ quỹ", ["lane-mail", "lane-cash"]),
        _annotation("owner-accounting", "owner-group:Kế toán trưởng", ["lane-ar", "lane-ledger"]),
        _annotation("legend-roles", "legend:money=Séc;document=Chứng từ đối chiếu;file=Tệp lưu;listing=Bảng kê", ["check-customer", "notice-customer", "file-ar", "listing-mail"]),
    ]
    return _finalize("pilot-swimlane", "swimlane", "Luồng chứng từ thu tiền", "vi", nodes=nodes, edges=edges, lanes=lanes, annotations=annotations)


PILOT_BUILDERS = {"architecture": architecture_pilot, "bar-chart": bar_pilot, "swimlane": swimlane_pilot}


def build_pilot(case_name: str) -> dict[str, Any]:
    builder = PILOT_BUILDERS.get(case_name)
    if builder is None:
        raise ValueError(f"Unsupported P-06 pilot: {case_name}")
    return builder()


__all__ = ["PILOT_BUILDERS", "architecture_pilot", "bar_pilot", "build_pilot", "swimlane_pilot"]
