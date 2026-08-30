"""D-095 detailed Layers presentation variant in the approved P-18 grammar."""

from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH = 2000
HEIGHT = 920
LANE_ORDER = ("level-5", "level-4", "level-3", "level-2", "level-1")
NODE_ORDER = (
    "layer-experience",
    "layer-orchestration",
    "layer-services",
    "layer-data-platform",
    "layer-infrastructure",
)
FOCAL_NODE = "layer-orchestration"
STACK_BOX = (245, 105, 1710, 650)
ROW_HEIGHT = 130


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_layers(plan):
    contract = plan.get("semantic_projection", {}).get("containment_contract", {})
    lanes = contract.get("ordered_layers", [])
    return {item.get("id") for item in lanes} == set(LANE_ORDER)


def layout_layers(plan):
    projection = plan["semantic_projection"]
    contract = projection["containment_contract"]
    lanes = {item["id"]: item for item in contract["ordered_layers"]}
    nodes = {item["id"]: item for item in projection["nodes"]}
    edges = {item["id"]: item for item in projection["edges"]}
    _require(set(lanes) == set(LANE_ORDER), "D-095 layer inventory mismatch")
    _require(set(nodes) == set(NODE_ORDER), "D-095 layer member mismatch")
    _require(len(edges) == 4, "D-095 dependency count mismatch")
    _require(sum(item.get("state") == "focal" for item in nodes.values()) == 1, "D-095 requires one focal layer")

    x, y, width, _ = STACK_BOX
    rows = {}
    owned = []
    for index, lane_id in enumerate(LANE_ORDER):
        lane = lanes[lane_id]
        _require(lane["order"] == index, f"D-095 layer order mismatch: {lane_id}")
        _require(len(lane["member_ids"]) == 1, f"D-095 layer ownership mismatch: {lane_id}")
        node_id = lane["member_ids"][0]
        _require(node_id == NODE_ORDER[index], f"D-095 layer member order mismatch: {lane_id}")
        owned.append(node_id)
        title, detail = [part.strip() for part in nodes[node_id]["label"].split(" | ", 1)]
        rows[lane_id] = {
            "lane_id": lane_id,
            "level": lane["label"],
            "node_id": node_id,
            "title": title,
            "detail": detail,
            "focal": node_id == FOCAL_NODE,
            "box": (x, y + index * ROW_HEIGHT, width, ROW_HEIGHT),
        }
    _require(owned == list(NODE_ORDER), "D-095 ownership must be exact")
    result = {"width": WIDTH, "height": HEIGHT, "stack_box": STACK_BOX, "rows": rows, "edges": edges}
    validate_layers_layout(result)
    return result


def validate_layers_layout(layout):
    sx, sy, sw, sh = layout["stack_box"]
    boxes = [layout["rows"][lane_id]["box"] for lane_id in LANE_ORDER]
    _require(boxes[0][1] == sy and boxes[-1][1] + boxes[-1][3] == sy + sh, "D-095 stack bounds mismatch")
    _require(all(x == sx and width == sw and height == ROW_HEIGHT for x, _, width, height in boxes), "D-095 row geometry mismatch")
    _require(all(boxes[index][1] + ROW_HEIGHT == boxes[index + 1][1] for index in range(4)), "D-095 layer continuity mismatch")
    _require(sum(layout["rows"][lane_id]["focal"] for lane_id in LANE_ORDER) == 1, "D-095 focal count mismatch")


def layers_css(tokens):
    return '''
.ly-axis{fill:none;stroke:var(--connector);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.ly-axis-label{font:700 12px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}
.ly-row{fill:var(--surface);stroke:var(--border);stroke-width:1.4}.ly-row.alt{fill:color-mix(in srgb,var(--surface-alt) 64%,var(--surface))}.ly-row.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.6}
.ly-level{font:700 13px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--muted)}.ly-level.focal{fill:var(--accent-text)}.ly-title{font:650 26px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}
.ly-detail{font:600 15px Menlo,Monaco,monospace;letter-spacing:.5px;fill:var(--muted)}.ly-detail.focal{fill:var(--accent-text)}.ly-focus-tag{fill:var(--accent);stroke:none}.ly-focus-tag-text{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--on-accent)}
.ly-note-rule{stroke:var(--grid);stroke-width:1.3}.ly-note-kicker{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}.ly-note{font:italic 15px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.ly-details{overflow-x:auto}.ly-details table{min-width:840px}
'''


def render_layers(plan):
    layout = layout_layers(plan)
    parts = ['<g data-layers-contract="D-095-five-layer-abstraction" data-focal-node="layer-orchestration">']
    parts.append(
        '<path class="ly-axis" d="M160 755 L160 132 M150 146 L160 132 L170 146"/>'
        '<text class="ly-axis-label" x="120" y="112">TRỪU TƯỢNG</text>'
        '<text class="ly-axis-label" x="120" y="785">NỀN TẢNG</text>'
    )
    for index, lane_id in enumerate(LANE_ORDER):
        row = layout["rows"][lane_id]
        x, y, width, height = row["box"]
        row_class = "ly-row focal" if row["focal"] else "ly-row alt" if index >= 3 else "ly-row"
        level_class = "ly-level focal" if row["focal"] else "ly-level"
        detail_class = "ly-detail focal" if row["focal"] else "ly-detail"
        parts.append(
            f'<g data-layer-id="{lane_id}" data-node-id="{row["node_id"]}" data-order="{index}" data-focal="{str(row["focal"]).lower()}">'
            f'<rect class="{row_class}" x="{x}" y="{y}" width="{width}" height="{height}"/>'
            f'<text class="{level_class}" x="{x+42}" y="{y+72}">{escape(row["level"])}</text>'
            f'<text class="ly-title" x="{x+285}" y="{y+76}">{escape(row["title"])}</text>'
            f'<text class="{detail_class}" x="{x+width-42}" y="{y+72}" text-anchor="end">{escape(row["detail"])}</text>'
        )
        if row["focal"]:
            parts.append(
                f'<rect class="ly-focus-tag" x="{x+42}" y="{y+20}" width="116" height="24" rx="4"/>'
                f'<text class="ly-focus-tag-text" x="{x+100}" y="{y+37}" text-anchor="middle">TRỌNG TÂM</text>'
            )
        parts.append('</g>')
    parts.append(
        '<line class="ly-note-rule" x1="245" y1="820" x2="1955" y2="820"/>'
        '<text class="ly-note-kicker" x="245" y="860">LỚP TRỌNG TÂM</text>'
        '<text class="ly-note" x="500" y="860">Điều phối quy trình kết nối quy tắc, phê duyệt và bằng chứng vận hành xuyên suốt nền tảng.</text>'
        '</g>'
    )
    return "".join(parts)


def validate_layers_svg(svg):
    root = ET.fromstring(svg)
    rows = {item.attrib["data-layer-id"]: item for item in root.findall(".//*[@data-layer-id]")}
    _require(set(rows) == set(LANE_ORDER), "D-095 serialized layer mismatch")
    _require([rows[lane_id].attrib["data-order"] for lane_id in LANE_ORDER] == [str(i) for i in range(5)], "D-095 serialized order mismatch")
    focal = [item.attrib["data-node-id"] for item in rows.values() if item.attrib["data-focal"] == "true"]
    _require(focal == [FOCAL_NODE], "D-095 serialized focal mismatch")
    return {"layers": 5, "focal_layers": 1, "abstraction_axis": 1, "dependencies": 4}


def layers_table(plan):
    layout = layout_layers(plan)
    rows = []
    for lane_id in LANE_ORDER:
        row = layout["rows"][lane_id]
        rows.append((row["level"], row["node_id"], row["title"], row["detail"], "trọng tâm" if row["focal"] else "mặc định"))
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows)
    return '<details class="ly-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Cấp</th><th>Semantic ID</th><th>Lớp</th><th>Phạm vi</th><th>Trạng thái</th></tr></thead><tbody>' + body + '</tbody></table></details>'
