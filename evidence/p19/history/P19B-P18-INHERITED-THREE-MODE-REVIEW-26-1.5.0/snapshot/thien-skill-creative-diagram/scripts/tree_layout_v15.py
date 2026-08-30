"""D-106 centered three-tier tree, inheriting P-18 org-chart geometry."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_NODE_IDS = (
    "capability-product", "branch-experience", "branch-operations", "branch-insight",
    "leaf-interface", "leaf-content", "leaf-data", "leaf-platform", "leaf-research",
)
EXPECTED_EDGE_IDS = (
    "parent-product-experience", "parent-product-operations", "parent-product-insight",
    "parent-experience-interface", "parent-experience-content",
    "parent-operations-data", "parent-operations-platform", "parent-insight-research",
)
BOXES = {
    "capability-product": (790.0, 90.0, 420.0, 120.0),
    "branch-experience": (190.0, 390.0, 340.0, 120.0),
    "branch-operations": (830.0, 390.0, 340.0, 120.0),
    "branch-insight": (1470.0, 390.0, 340.0, 120.0),
    "leaf-interface": (75.0, 680.0, 270.0, 110.0),
    "leaf-content": (375.0, 680.0, 270.0, 110.0),
    "leaf-data": (715.0, 680.0, 270.0, 110.0),
    "leaf-platform": (1015.0, 680.0, 270.0, 110.0),
    "leaf-research": (1505.0, 680.0, 270.0, 110.0),
}
DETAILS = {
    "capability-product": ("ROOT", "một định hướng chung"),
    "branch-experience": ("NHÓM", "giao diện · nội dung"),
    "branch-operations": ("NHÓM", "dữ liệu · nền tảng"),
    "branch-insight": ("NHÓM", "nghiên cứu · bằng chứng"),
    "leaf-interface": ("LEAF", "cấu trúc · tương tác"),
    "leaf-content": ("LEAF", "ngôn ngữ · nhịp điệu"),
    "leaf-data": ("LEAF", "mô hình · chất lượng"),
    "leaf-platform": ("LEAF", "vận hành · độ tin cậy"),
    "leaf-research": ("LEAF", "điều tra · tổng hợp"),
}
LEVELS = {
    "capability-product": 0,
    "branch-experience": 1, "branch-operations": 1, "branch-insight": 1,
    "leaf-interface": 2, "leaf-content": 2, "leaf-data": 2,
    "leaf-platform": 2, "leaf-research": 2,
}
CHILDREN = {
    "capability-product": ("branch-experience", "branch-operations", "branch-insight"),
    "branch-experience": ("leaf-interface", "leaf-content"),
    "branch-operations": ("leaf-data", "leaf-platform"),
    "branch-insight": ("leaf-research",),
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _center(box):
    return box[0] + box[2] / 2, box[1] + box[3] / 2


def is_detailed_tree(plan):
    projection = plan.get("semantic_projection", {})
    return (
        tuple(item.get("id") for item in projection.get("nodes", [])) == EXPECTED_NODE_IDS
        and tuple(item.get("id") for item in projection.get("edges", [])) == EXPECTED_EDGE_IDS
    )


def layout_tree(plan):
    projection = plan["semantic_projection"]
    nodes = projection["nodes"]
    edges = projection["edges"]
    _require(tuple(item["id"] for item in nodes) == EXPECTED_NODE_IDS, "D-106 exact tree node order mismatch")
    _require(tuple(item["id"] for item in edges) == EXPECTED_EDGE_IDS, "D-106 exact tree edge order mismatch")
    _require(all(item["kind"] == "parent" and item.get("directed") is False for item in edges), "D-106 requires undirected parent links")
    edge_pairs = {(item["source"], item["target"]) for item in edges}
    expected_pairs = {(parent, child) for parent, values in CHILDREN.items() for child in values}
    _require(edge_pairs == expected_pairs, "D-106 tree adjacency mismatch")

    cards = {}
    for item in nodes:
        x, y, width, height = BOXES[item["id"]]
        badge, detail = DETAILS[item["id"]]
        cards[item["id"]] = {
            **item, "x": x, "y": y, "width": width, "height": height,
            "center_x": x + width / 2, "center_y": y + height / 2,
            "level": LEVELS[item["id"]], "badge": badge, "detail": detail,
        }

    for parent, child_ids in CHILDREN.items():
        parent_x = cards[parent]["center_x"]
        child_centers = [cards[child]["center_x"] for child in child_ids]
        span_midpoint = (min(child_centers) + max(child_centers)) / 2
        _require(abs(parent_x - span_midpoint) < 1e-9, f"D-106 parent {parent} is not centered over child span")

    connectors = [
        ("root-trunk", 1000, 210, 1000, 300, "trunk", "capability-product", ""),
        ("root-bus", 360, 300, 1640, 300, "bus", "capability-product", ""),
        ("root-drop-experience", 360, 300, 360, 390, "drop", "capability-product", "branch-experience"),
        ("root-drop-operations", 1000, 300, 1000, 390, "drop", "capability-product", "branch-operations"),
        ("root-drop-insight", 1640, 300, 1640, 390, "drop", "capability-product", "branch-insight"),
        ("experience-trunk", 360, 510, 360, 610, "trunk", "branch-experience", ""),
        ("experience-bus", 210, 610, 510, 610, "bus", "branch-experience", ""),
        ("experience-drop-interface", 210, 610, 210, 680, "drop", "branch-experience", "leaf-interface"),
        ("experience-drop-content", 510, 610, 510, 680, "drop", "branch-experience", "leaf-content"),
        ("operations-trunk", 1000, 510, 1000, 610, "trunk", "branch-operations", ""),
        ("operations-bus", 850, 610, 1150, 610, "bus", "branch-operations", ""),
        ("operations-drop-data", 850, 610, 850, 680, "drop", "branch-operations", "leaf-data"),
        ("operations-drop-platform", 1150, 610, 1150, 680, "drop", "branch-operations", "leaf-platform"),
        ("insight-direct-research", 1640, 510, 1640, 680, "direct", "branch-insight", "leaf-research"),
    ]
    connector_items = [
        {"id": item_id, "x1": float(x1), "y1": float(y1), "x2": float(x2), "y2": float(y2),
         "role": role, "source": source, "target": target}
        for item_id, x1, y1, x2, y2, role, source, target in connectors
    ]
    _require(all(all(math.isfinite(item[key]) for key in ("x1", "y1", "x2", "y2")) for item in connector_items), "D-106 connector coordinates must be finite")
    return {"width": 2000, "height": 920, "cards": cards, "connectors": connector_items}


def tree_css(tokens):
    return """
    .tree-wire{fill:none;stroke:var(--connector);stroke-width:2.6;stroke-linecap:square;vector-effect:non-scaling-stroke}
    .tree-card-shape{fill:var(--surface);stroke:var(--connector);stroke-width:2.4;vector-effect:non-scaling-stroke}
    .tree-card.is-root .tree-card-shape{fill:var(--accent-soft);stroke:var(--accent);stroke-width:3}
    .tree-card.is-leaf .tree-card-shape{fill:var(--surface-alt)}
    .tree-badge-shape{fill:var(--canvas);stroke:var(--border);stroke-width:1.5}.tree-card.is-root .tree-badge-shape{fill:var(--accent-soft);stroke:var(--accent)}
    .tree-badge{font:700 12px Menlo,Monaco,monospace;letter-spacing:.08em;fill:var(--muted)}.tree-card.is-root .tree-badge{fill:var(--accent-text)}
    .tree-title{font:750 23px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .tree-detail{font:700 14px Menlo,Monaco,monospace;letter-spacing:.03em;fill:var(--muted)}
    .tree-tier{font:700 13px Menlo,Monaco,monospace;letter-spacing:.16em;fill:var(--muted)}
    .tree-rule{stroke:var(--grid);stroke-width:1.5}.tree-legend{font:700 13px Menlo,Monaco,monospace;fill:var(--muted);letter-spacing:.04em}
    .tree-swatch-root{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.4}.tree-swatch-branch{fill:var(--surface);stroke:var(--connector);stroke-width:2}.tree-swatch-leaf{fill:var(--surface-alt);stroke:var(--connector);stroke-width:2}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:g}" y="{y:g}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_tree(plan):
    layout = layout_tree(plan)
    parts = [
        '<g data-tree-contract="D-106-p18-org-chart-centered-spans" data-parent-centering="span-midpoint" '
        'data-entry-alignment="center" data-route-priority="straight-first" data-route-exception="branch-fanout-required">',
        _text(82, 155, "TẦNG 0 · ROOT", "tree-tier", "start"),
        _text(82, 455, "TẦNG 1", "tree-tier", "start"),
        _text(82, 745, "TẦNG 2", "tree-tier", "start"),
    ]
    for item in layout["connectors"]:
        relation = f' data-edge-target="{item["target"]}"' if item["target"] else ""
        parts.append(
            f'<line class="tree-wire" data-tree-connector-id="{item["id"]}" data-connector-role="{item["role"]}" '
            f'data-edge-source="{item["source"]}"{relation} x1="{item["x1"]:g}" y1="{item["y1"]:g}" x2="{item["x2"]:g}" y2="{item["y2"]:g}"/>'
        )
    for node_id in EXPECTED_NODE_IDS:
        item = layout["cards"][node_id]
        state = "is-root" if item["level"] == 0 else "is-leaf" if item["level"] == 2 else "is-branch"
        child_ids = CHILDREN.get(node_id, ())
        child_centers = [layout["cards"][child]["center_x"] for child in child_ids]
        span_midpoint = (min(child_centers) + max(child_centers)) / 2 if child_centers else item["center_x"]
        parts.append(
            f'<g class="tree-card {state}" data-tree-node-id="{node_id}" data-tree-level="{item["level"]}" '
            f'data-center-x="{item["center_x"]:g}" data-parent-span-center-x="{span_midpoint:g}">'
            f'<rect class="tree-card-shape" x="{item["x"]:g}" y="{item["y"]:g}" width="{item["width"]:g}" height="{item["height"]:g}" rx="16"/>'
            f'<rect class="tree-badge-shape" x="{item["x"]+18:g}" y="{item["y"]+16:g}" width="64" height="25" rx="5"/>'
            f'{_text(item["x"]+50, item["y"]+33, item["badge"], "tree-badge")}'
            f'{_text(item["center_x"], item["y"]+70, item["label"], "tree-title")}'
            f'{_text(item["center_x"], item["y"]+96, item["detail"], "tree-detail")}</g>'
        )
    parts.extend([
        '<line class="tree-rule" x1="80" y1="838" x2="1920" y2="838"/>',
        '<rect class="tree-swatch-root" x="80" y="870" width="30" height="22" rx="5"/>', _text(126, 887, "Root · tiêu điểm", "tree-legend", "start"),
        '<rect class="tree-swatch-branch" x="390" y="870" width="30" height="22" rx="5"/>', _text(436, 887, "Nhóm năng lực", "tree-legend", "start"),
        '<rect class="tree-swatch-leaf" x="740" y="870" width="30" height="22" rx="5"/>', _text(786, 887, "Leaf", "tree-legend", "start"),
        _text(1920, 887, "PARENT = TRUNG ĐIỂM SPAN CHILD · SINGLE CHILD = ĐƯỜNG THẲNG TÂM", "tree-legend", "end"),
        '</g>',
    ])
    return "".join(parts)


def validate_tree_svg(svg):
    root = ET.fromstring(svg)
    group = root.find(".//*[@data-tree-contract]")
    _require(group is not None, "Serialized D-106 tree contract missing")
    nodes = root.findall(".//*[@data-tree-node-id]")
    lines = root.findall(".//*[@data-tree-connector-id]")
    _require(tuple(item.attrib["data-tree-node-id"] for item in nodes) == EXPECTED_NODE_IDS, "Serialized D-106 node order mismatch")
    _require(len(lines) == 14, "Serialized D-106 connector primitive count mismatch")
    _require(all("marker-end" not in item.attrib and item.tag == "line" for item in lines), "D-106 hierarchy connectors must be straight line primitives without arrows")
    for item in nodes:
        if item.attrib["data-tree-node-id"] in CHILDREN:
            _require(abs(float(item.attrib["data-center-x"]) - float(item.attrib["data-parent-span-center-x"])) < 1e-9, "Serialized D-106 parent centering mismatch")
    direct = [item for item in lines if item.attrib.get("data-connector-role") == "direct"]
    _require(len(direct) == 1 and direct[0].attrib["x1"] == direct[0].attrib["x2"], "D-106 single-child link must be centered and straight")
    return {"nodes": len(nodes), "edges": 8, "tiers": 3, "connector_primitives": len(lines), "centered_parents": len(CHILDREN), "single_child_straight": len(direct)}


def tree_table(plan):
    layout = layout_tree(plan)
    rows = []
    for node_id in EXPECTED_NODE_IDS:
        item = layout["cards"][node_id]
        rows.append(f'<tr><th scope="row">Node</th><td>{escape(item["label"])}</td><td>{escape(node_id)}</td><td>Tầng {item["level"]}</td></tr>')
    edge_by_pair = {(item["source"], item["target"]): item for item in plan["semantic_projection"]["edges"]}
    for parent, child_ids in CHILDREN.items():
        for child in child_ids:
            edge = edge_by_pair[(parent, child)]
            rows.append(f'<tr><th scope="row">Parent</th><td>{escape(parent)} → {escape(child)}</td><td>{escape(edge["id"])}</td><td>centered</td></tr>')
    return '<details class="tree-details"><summary>Cấu trúc cây có thể kiểm chứng</summary><table><thead><tr><th scope="col">Loại</th><th scope="col">Nội dung</th><th scope="col">Semantic ID</th><th scope="col">Bố trí</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></details>'
