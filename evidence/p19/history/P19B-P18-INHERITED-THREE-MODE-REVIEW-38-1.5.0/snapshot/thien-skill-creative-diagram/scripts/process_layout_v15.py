"""D-118 detailed process renderer with continuous document connectors."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


EXPECTED_NODE_ORDER = (
    "process-start", "process-check", "decision-complete", "document-supplement",
    "process-return", "decision-sensitive", "process-standard", "process-control",
    "document-approval-pack", "process-log", "process-complete",
)
EXPECTED_EDGE_ORDER = (
    "flow-start-check", "flow-check-complete", "flow-incomplete-document",
    "flow-document-return", "flow-complete-sensitive", "flow-standard-review",
    "flow-sensitive-control", "flow-standard-pack", "flow-control-pack",
    "flow-pack-log", "flow-log-complete",
)
EXPECTED_SHAPES = {
    "terminator": 3,
    "process": 4,
    "decision": 2,
    "document": 1,
    "multiple-document": 1,
}

NODE_BOXES = {
    "process-start": (820, 60, 360, 104),
    "process-check": (820, 208, 360, 108),
    "decision-complete": (800, 365, 400, 170),
    "document-supplement": (30, 382, 360, 136),
    "process-return": (30, 785, 360, 104),
    "decision-sensitive": (800, 590, 400, 170),
    "process-standard": (300, 615, 340, 110),
    "process-control": (1360, 615, 340, 110),
    "document-approval-pack": (820, 825, 360, 138),
    "process-log": (820, 1010, 360, 108),
    "process-complete": (820, 1160, 360, 104),
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_process(plan):
    nodes = plan.get("semantic_projection", {}).get("nodes", [])
    return tuple(item.get("id") for item in nodes) == EXPECTED_NODE_ORDER


def _shape_kind(item):
    if item["id"] == "document-approval-pack":
        return "multiple-document"
    return {
        "start": "terminator",
        "terminal": "terminator",
        "activity": "process",
        "decision": "decision",
        "artifact": "document",
    }[item["role"]]


def layout_process(plan):
    projection = plan["semantic_projection"]
    nodes = projection["nodes"]
    edges = projection["edges"]
    _require(tuple(item["id"] for item in nodes) == EXPECTED_NODE_ORDER, "D-118 process node inventory mismatch")
    _require(tuple(item["id"] for item in edges) == EXPECTED_EDGE_ORDER, "D-118 process edge inventory mismatch")
    counts = {kind: 0 for kind in EXPECTED_SHAPES}
    laid_out_nodes = []
    for item in nodes:
        shape_kind = _shape_kind(item)
        _require(shape_kind in counts, f"D-118 unsupported shape: {shape_kind}")
        counts[shape_kind] += 1
        laid_out_nodes.append({**item, "shape_kind": shape_kind, "box": NODE_BOXES[item["id"]]})
    _require(counts == EXPECTED_SHAPES, "D-118 process shape taxonomy mismatch")
    routes = {
        "flow-start-check": ((1000, 164), (1000, 208), "center-bottom", "center-top"),
        "flow-check-complete": ((1000, 316), (1000, 365), "center-bottom", "center-top"),
        "flow-incomplete-document": ((800, 450), (390, 450), "center-left", "center-right"),
        "flow-document-return": ((210, 518), (210, 785), "center-bottom", "center-top"),
        "flow-complete-sensitive": ((1000, 535), (1000, 590), "center-bottom", "center-top"),
        "flow-standard-review": ((800, 675), (640, 675), "center-left", "center-right"),
        "flow-sensitive-control": ((1200, 675), (1360, 675), "center-right", "center-left"),
        "flow-standard-pack": ((470, 725), (920, 825), "center-bottom", "top-left-inlet"),
        "flow-control-pack": ((1530, 725), (1080, 825), "center-bottom", "top-right-inlet"),
        "flow-pack-log": ((1000, 963), (1000, 1010), "center-bottom", "center-top"),
        "flow-log-complete": ((1000, 1118), (1000, 1160), "center-bottom", "center-top"),
    }
    laid_out_edges = []
    for item in edges:
        start, end, source_anchor, target_anchor = routes[item["id"]]
        routed = {
            **item,
            "start": start,
            "end": end,
            "source_anchor": source_anchor,
            "target_anchor": target_anchor,
            "route_kind": "straight",
            "boundary_contact": item["source"].startswith("document-") or item["target"].startswith("document-"),
        }
        if item["id"] == "flow-standard-pack":
            routed.update({
                "route_kind": "rounded-orthogonal",
                "path": "M470 725 V773 Q470 785 482 785 H908 Q920 785 920 797 V825",
                "exception_reason": "owner-requested-document-merge-clarity",
            })
        elif item["id"] == "flow-control-pack":
            routed.update({
                "route_kind": "rounded-orthogonal",
                "path": "M1530 725 V773 Q1530 785 1518 785 H1092 Q1080 785 1080 797 V825",
                "exception_reason": "owner-requested-document-merge-clarity",
            })
        laid_out_edges.append(routed)
    return {
        "width": 2000,
        "height": 1340,
        "nodes": laid_out_nodes,
        "edges": laid_out_edges,
        "shape_counts": counts,
    }


def process_css(tokens):
    return """
    .pr-node{fill:var(--surface);stroke:var(--connector);stroke-width:1.45;vector-effect:non-scaling-stroke}
    .pr-node.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.8}
    .pr-node.muted{fill:var(--surface-alt);stroke:var(--border)}
    .pr-layer{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.15}
    .pr-layer.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.25}
    .pr-route{fill:none;stroke:var(--connector);stroke-width:1.45;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
    .pr-route.merge{stroke-width:1.8}
    .pr-title{font:700 22px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .pr-subtitle{font:700 14px Menlo,Monaco,monospace;fill:var(--muted)}
    .pr-badge{fill:var(--surface-alt);stroke:var(--border);stroke-width:1}
    .pr-badge.focal{fill:var(--accent-soft);stroke:var(--accent)}
    .pr-badge-text{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--muted)}
    .pr-badge-text.focal,.pr-guard.focal{fill:var(--accent-text)}
    .pr-guard-bg{fill:var(--canvas)}
    .pr-guard{font:700 13px Menlo,Monaco,monospace;letter-spacing:1.3px;fill:var(--connector)}
    .pr-rule{stroke:var(--grid);stroke-width:1}
    .pr-legend-title,.pr-legend-text{font:700 13px Menlo,Monaco,monospace;fill:var(--muted)}
    .pr-legend-title{letter-spacing:2px}.pr-legend-text{fill:var(--connector)}
    .pr-details{overflow-x:auto}.pr-details table{min-width:980px}
    """


def _text(x, y, value, css="pr-title", anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _badge(x, y, label, focal=False):
    width = max(88, len(label) * 8 + 24)
    css = " focal" if focal else ""
    return (
        f'<rect class="pr-badge{css}" x="{x:.3f}" y="{y:.3f}" width="{width}" height="25" rx="5"/>'
        + _text(x + width / 2, y + 17, label, f"pr-badge-text{css}")
    )


def _node_shape(item):
    x, y, w, h = item["box"]
    kind = item["shape_kind"]
    focal = item.get("state") == "focal"
    css = "pr-node focal" if focal else "pr-node muted" if item["id"] == "process-return" else "pr-node"
    if kind == "terminator":
        return f'<rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.3f}"/>'
    if kind == "process":
        return f'<rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
    if kind == "decision":
        return f'<polygon class="{css}" points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"/>'
    wave_y = y + h - 22
    center_y = y + h
    front = f'M{x} {y} H{x+w} V{wave_y} C{x+w*0.80} {wave_y-18} {x+w*0.64} {center_y} {x+w*0.50} {center_y} C{x+w*0.34} {center_y} {x+w*0.20} {wave_y-18} {x} {wave_y} Z'
    if kind == "document":
        return f'<path class="{css}" d="{front}"/>'
    back_one = f'M{x+18} {y-18} H{x+w+18} V{wave_y-18} C{x+w*0.80+18} {wave_y-36} {x+w*0.64+18} {center_y-18} {x+w*0.50+18} {center_y-18} C{x+w*0.34+18} {center_y-18} {x+w*0.20+18} {wave_y-36} {x+18} {wave_y-18} Z'
    back_two = f'M{x+9} {y-9} H{x+w+9} V{wave_y-9} C{x+w*0.80+9} {wave_y-27} {x+w*0.64+9} {center_y-9} {x+w*0.50+9} {center_y-9} C{x+w*0.34+9} {center_y-9} {x+w*0.20+9} {wave_y-27} {x+9} {wave_y-9} Z'
    layer_css = "pr-layer focal" if focal else "pr-layer"
    return f'<path class="{layer_css}" d="{back_one}"/><path class="{layer_css}" d="{back_two}"/><path class="{css}" d="{front}"/>'


def _node(item):
    x, y, w, h = item["box"]
    kind = item["shape_kind"]
    focal = item.get("state") == "focal"
    label_y = y + h / 2 + (0 if kind == "decision" else -2)
    if kind == "terminator":
        label_y = y + 58
    if kind in {"document", "multiple-document"}:
        label_y = y + 58
    subtitle_y = label_y + 28
    badge_y = y + 13
    badge_label = {
        "terminator": "ĐIỂM MỐC",
        "process": "XỬ LÝ",
        "decision": "QUYẾT ĐỊNH",
        "document": "TÀI LIỆU",
        "multiple-document": "BỘ HỒ SƠ",
    }[kind]
    badge = "" if kind == "decision" else _badge(x + 16, badge_y, badge_label, focal)
    return (
        f'<g data-process-node="{escape(item["id"], quote=True)}" data-shape-kind="{kind}" data-focal="{str(focal).lower()}">'
        + _node_shape(item) + badge
        + _text(x + w / 2, label_y, item["label"])
        + ("" if not item.get("secondary_label") else _text(x + w / 2, subtitle_y, item["secondary_label"], "pr-subtitle"))
        + "</g>"
    )


def render_process(plan):
    layout = layout_process(plan)
    parts = [
        '<g data-process-contract="D-118-continuous-document-connectors" '
        'data-template-contract="p18r6-review17-preserved" '
        'data-attachment-policy="D-105-centered-and-even" '
        'data-route-priority="straight-first-rounded-orthogonal-exception">',
        '<defs><marker id="pr-arrow" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--connector)"/></marker><marker id="pr-arrow-merge" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L15 8 L1 15 Z" fill="var(--connector)"/></marker></defs>',
    ]
    # Nodes are painted first so document layers cannot hide connector tips.
    for item in layout["nodes"]:
        parts.append(_node(item))
    for edge in layout["edges"]:
        (x1, y1), (x2, y2) = edge["start"], edge["end"]
        common = (
            f'data-process-edge="{escape(edge["id"], quote=True)}" '
            f'data-route-kind="{edge["route_kind"]}" data-source-anchor="{edge["source_anchor"]}" '
            f'data-target-anchor="{edge["target_anchor"]}" data-start-x="{x1}" data-start-y="{y1}" '
            f'data-end-x="{x2}" data-end-y="{y2}" data-boundary-contact="{str(edge["boundary_contact"]).lower()}"'
        )
        if edge["route_kind"] == "rounded-orthogonal":
            parts.append(
                f'<path class="pr-route merge" {common} data-route-exception="{edge["exception_reason"]}" '
                f'd="{edge["path"]}" marker-end="url(#pr-arrow-merge)"/>'
            )
        else:
            parts.append(
                f'<line class="pr-route" {common} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#pr-arrow)"/>'
            )
    guard_positions = {
        "flow-incomplete-document": (595, 436, "CHƯA ĐỦ"),
        "flow-complete-sensitive": (1045, 562, "ĐẦY ĐỦ"),
        "flow-standard-review": (715, 660, "KHÔNG"),
        "flow-sensitive-control": (1285, 660, "CÓ"),
    }
    for edge_id, (x, y, label) in guard_positions.items():
        width = len(label) * 9 + 24
        parts.append(f'<rect class="pr-guard-bg" x="{x-width/2}" y="{y-17}" width="{width}" height="24" rx="4"/>')
        parts.append(_text(x, y, label, "pr-guard focal" if edge_id == "flow-sensitive-control" else "pr-guard"))
    parts.extend([
        '<line class="pr-rule" x1="56" y1="1282" x2="1944" y2="1282"/>',
        _text(56, 1315, "CHÚ GIẢI", "pr-legend-title", "start"),
        '<rect class="pr-node" x="220" y="1296" width="52" height="26" rx="13"/>',
        _text(288, 1316, "Điểm bắt đầu / kết thúc", "pr-legend-text", "start"),
        '<polygon class="pr-node" points="628,1296 650,1309 628,1322 606,1309"/>',
        _text(668, 1316, "Quyết định", "pr-legend-text", "start"),
        '<path class="pr-node" d="M880 1296 H930 V1314 C918 1305 908 1322 896 1314 C888 1308 884 1316 880 1314 Z"/>',
        _text(946, 1316, "Tài liệu / bộ hồ sơ", "pr-legend-text", "start"),
        '<line class="pr-route" x1="1290" y1="1309" x2="1340" y2="1309" marker-end="url(#pr-arrow)"/>',
        _text(1358, 1316, "Luồng thẳng / vuông góc bo tròn", "pr-legend-text", "start"),
        "</g>",
    ])
    return "".join(parts)


def validate_process_svg(svg):
    root = ET.fromstring(svg)
    nodes = root.findall(".//*[@data-process-node]")
    edges = root.findall(".//*[@data-process-edge]")
    _require(tuple(item.attrib["data-process-node"] for item in nodes) == EXPECTED_NODE_ORDER, "Serialized D-118 node order mismatch")
    _require(tuple(item.attrib["data-process-edge"] for item in edges) == EXPECTED_EDGE_ORDER, "Serialized D-118 edge order mismatch")
    counts = {kind: 0 for kind in EXPECTED_SHAPES}
    for item in nodes:
        counts[item.attrib["data-shape-kind"]] += 1
    _require(counts == EXPECTED_SHAPES, "Serialized D-118 shape count mismatch")
    straight = [item for item in edges if item.attrib["data-route-kind"] == "straight"]
    orthogonal = [item for item in edges if item.attrib["data-route-kind"] == "rounded-orthogonal"]
    _require(len(straight) == 9 and all(item.tag == "line" for item in straight), "D-118 straight route count mismatch")
    _require(len(orthogonal) == 2 and all(item.tag == "path" for item in orthogonal), "D-118 merge route count mismatch")
    _require(all(item.attrib.get("marker-end") == "url(#pr-arrow-merge)" for item in orthogonal), "D-118 merge arrowhead mismatch")
    _require(all("Q" in item.attrib.get("d", "") for item in orthogonal), "D-118 merge routes must have rounded 90-degree corners")
    pack_targets = [item for item in edges if item.attrib["data-target-anchor"].startswith("top-")]
    _require(len(pack_targets) == 2, "D-117 multiple-document inlet count mismatch")
    pack_x = sorted(float(item.attrib["data-end-x"]) for item in pack_targets)
    _require(pack_x == [920.0, 1080.0] and abs((pack_x[0] + pack_x[1]) / 2 - 1000) < .01, "D-118 multiple inlet spacing mismatch")
    _require(all(item.attrib.get("data-boundary-contact") == "true" for item in edges if item.attrib["data-process-edge"] in {"flow-incomplete-document", "flow-document-return", "flow-standard-pack", "flow-control-pack", "flow-pack-log"}), "D-118 document boundary contact mismatch")
    return {
        "nodes": 11,
        "edges": 11,
        "shape_counts": counts,
        "straight_routes": 9,
        "rounded_orthogonal_exceptions": 2,
        "multiple_document_inlets": 2,
        "document_boundary_contacts": 5,
    }


def process_table(plan):
    layout = layout_process(plan)
    rows = []
    for index, item in enumerate(layout["nodes"], 1):
        rows.append(
            f'<tr><td>Ô {index}</td><td>{escape(item["label"])}</td><td>—</td>'
            f'<td>{escape(item["shape_kind"])}</td><td>{"Trọng tâm" if item.get("state") == "focal" else "Chuẩn"}</td></tr>'
        )
    for index, item in enumerate(layout["edges"], 1):
        rows.append(
            f'<tr><td>Luồng {index}</td><td>{escape(item["source"])}</td><td>{escape(item["target"])}</td>'
            f'<td>{escape(item.get("guard", "—"))}</td><td>{escape(item["route_kind"])}</td></tr>'
        )
    return (
        '<details class="pr-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Năm loại shape được biểu diễn trực tiếp; chín luồng thẳng và hai luồng hợp nhất vuông góc bo tròn đều chạm liền mạch vào biên tài liệu.</p>'
        '<table><thead><tr><th scope="col">Bản ghi</th><th scope="col">Nhãn / nguồn</th><th scope="col">Đích</th><th scope="col">Shape / nhánh</th><th scope="col">Vai trò / route</th></tr></thead><tbody>'
        + "".join(rows) + '</tbody></table></details>'
    )
