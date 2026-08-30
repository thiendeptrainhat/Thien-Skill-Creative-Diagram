"""D-093 detailed current-state landscape with P-18 route grammar."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET

from high_level_layout_v15 import orthogonal_path


WIDTH, HEIGHT = 2000, 1040
NODE_ORDER = (
    "source-pos", "source-commerce", "source-supplier",
    "processing-shared-drive", "processing-spreadsheet", "processing-rdbms",
    "delivery-portal", "delivery-email", "delivery-regional",
)
EDGE_ORDER = (
    "handoff-pos-drive", "handoff-commerce-drive", "handoff-supplier-drive",
    "handoff-drive-spreadsheet", "integration-spreadsheet-rdbms",
    "handoff-spreadsheet-portal", "handoff-portal-email", "handoff-email-regional",
)
GROUP_ORDER = ("group-collection", "group-processing", "group-dissemination")
BOXES = {
    "source-pos": (70, 170, 450, 120),
    "source-commerce": (70, 350, 450, 120),
    "source-supplier": (70, 550, 450, 120),
    "processing-shared-drive": (700, 170, 560, 140),
    "processing-spreadsheet": (700, 420, 560, 150),
    "processing-rdbms": (700, 670, 560, 120),
    "delivery-portal": (1490, 170, 440, 130),
    "delivery-email": (1490, 430, 440, 130),
    "delivery-regional": (1490, 680, 440, 120),
}
BOUNDARIES = {
    "group-collection": (30, 110, 530, 740),
    "group-processing": (600, 110, 780, 740),
    "group-dissemination": (1420, 110, 550, 740),
}
ROUTE_POINTS = {
    "handoff-pos-drive": [(520, 230), (700, 230)],
    "handoff-commerce-drive": [(520, 410), (650, 410), (650, 260), (700, 260)],
    "handoff-supplier-drive": [(520, 610), (650, 610), (650, 290), (700, 290)],
    "handoff-drive-spreadsheet": [(980, 310), (980, 420)],
    "integration-spreadsheet-rdbms": [(980, 570), (980, 670)],
    "handoff-spreadsheet-portal": [(1260, 495), (1400, 495), (1400, 235), (1490, 235)],
    "handoff-portal-email": [(1710, 300), (1710, 430)],
    "handoff-email-regional": [(1710, 560), (1710, 680)],
}
PAIRS = {
    "handoff-pos-drive": ("source-pos", "processing-shared-drive"),
    "handoff-commerce-drive": ("source-commerce", "processing-shared-drive"),
    "handoff-supplier-drive": ("source-supplier", "processing-shared-drive"),
    "handoff-drive-spreadsheet": ("processing-shared-drive", "processing-spreadsheet"),
    "integration-spreadsheet-rdbms": ("processing-spreadsheet", "processing-rdbms"),
    "handoff-spreadsheet-portal": ("processing-spreadsheet", "delivery-portal"),
    "handoff-portal-email": ("delivery-portal", "delivery-email"),
    "handoff-email-regional": ("delivery-email", "delivery-regional"),
}
LABEL_POSITIONS = {
    "handoff-pos-drive": (600, 210),
    "handoff-commerce-drive": (600, 390),
    "handoff-supplier-drive": (600, 590),
    "handoff-drive-spreadsheet": (1035, 370),
    "integration-spreadsheet-rdbms": (1035, 625),
    "handoff-spreadsheet-portal": (1330, 475),
    "handoff-portal-email": (1765, 365),
    "handoff-email-regional": (1775, 625),
}
PAIN_EDGES = {"handoff-drive-spreadsheet", "handoff-spreadsheet-portal"}
EXTERNAL_EDGES = {"handoff-supplier-drive", "handoff-email-regional"}


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_it_current_state(plan):
    p = plan.get("semantic_projection", {})
    return {item.get("id") for item in p.get("nodes", [])} == set(NODE_ORDER)


def layout_it_current_state(plan, corner_style="rounded"):
    p = plan["semantic_projection"]
    nodes = {item["id"]: item for item in p["nodes"]}
    edges = {item["id"]: item for item in p["edges"]}
    groups = {item["id"]: item for item in p["groups"]}
    _require(set(nodes) == set(NODE_ORDER), "D-093 current-state node mismatch")
    _require(set(edges) == set(EDGE_ORDER), "D-093 current-state handoff mismatch")
    _require(set(groups) == set(GROUP_ORDER), "D-093 current-state group mismatch")
    for edge_id, pair in PAIRS.items():
        edge = edges[edge_id]
        _require((edge["source"], edge["target"]) == pair and edge["directed"], f"D-093 endpoint mismatch: {edge_id}")
        _require(edge["kind"] in {"handoff", "integration"} and edge.get("label"), f"D-093 handoff label mismatch: {edge_id}")
    expected_groups = {
        "group-collection": set(NODE_ORDER[:3]),
        "group-processing": set(NODE_ORDER[3:6]),
        "group-dissemination": set(NODE_ORDER[6:]),
    }
    for group_id, members in expected_groups.items():
        _require(set(groups[group_id]["member_ids"]) == members, f"D-093 group ownership mismatch: {group_id}")
    _require(all(node.get("state") for node in nodes.values()), "D-093 every current-state node needs state")
    result = {
        "width": WIDTH,
        "height": HEIGHT,
        "corner_style": corner_style,
        "nodes": {node_id: {**nodes[node_id], "box": BOXES[node_id]} for node_id in NODE_ORDER},
        "edges": {
            edge_id: {
                **edges[edge_id],
                "points": ROUTE_POINTS[edge_id],
                "path": orthogonal_path(ROUTE_POINTS[edge_id], corner_style, radius=22),
                "label_position": LABEL_POSITIONS[edge_id],
            }
            for edge_id in EDGE_ORDER
        },
        "groups": {group_id: {**groups[group_id], "box": BOUNDARIES[group_id]} for group_id in GROUP_ORDER},
    }
    validate_it_current_state_layout(result)
    return result


def validate_it_current_state_layout(layout):
    _require(layout["corner_style"] in {"rounded", "straight"}, "D-093 corner policy mismatch")
    for group_id, group in layout["groups"].items():
        bx, by, bw, bh = group["box"]
        for node_id in group["member_ids"]:
            x, y, w, h = layout["nodes"][node_id]["box"]
            _require(bx < x and by < y and x + w < bx + bw and y + h < by + bh, f"D-093 containment mismatch: {node_id}")
    for edge_id, edge in layout["edges"].items():
        _require(edge["path"].startswith("M") and edge["path"].count("M") == 1, f"D-093 discontinuous route: {edge_id}")


def it_current_state_css(tokens):
    return '''
.ics-zone{fill:color-mix(in srgb,var(--surface-alt) 46%,transparent);stroke:var(--border);stroke-width:1.6}.ics-zone-label-bg,.ics-edge-label-bg{fill:var(--canvas)}
.ics-zone-label,.ics-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.7px;fill:var(--muted)}
.ics-card{fill:var(--surface);stroke:var(--connector);stroke-width:2}.ics-card.bottleneck{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.6}.ics-card.external{stroke-dasharray:9 7}.ics-card.healthy{fill:color-mix(in srgb,var(--success) 10%,var(--surface));stroke:var(--success)}
.ics-title{font:650 17px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.ics-detail{font:500 12px Menlo,Monaco,monospace;fill:var(--muted)}.ics-detail.pain{fill:var(--accent-text)}.ics-detail.healthy{fill:var(--success)}
.ics-state{font:700 10px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--muted)}.ics-icon{fill:none;stroke:var(--connector);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}.ics-card.bottleneck+.ics-icon{stroke:var(--accent)}
.ics-route{fill:none;stroke:var(--series-1);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}.ics-route.pain{stroke:var(--accent);stroke-width:2.8}.ics-route.external{stroke-dasharray:8 7}
.ics-edge-label{font:700 11px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--series-1)}.ics-edge-label.pain{fill:var(--accent-text)}
.ics-legend-rule{stroke:var(--grid);stroke-width:1.3}.ics-legend{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.ics-details{overflow-x:auto}.ics-details table{min-width:980px}
'''


def _icon(node_id, x, y):
    if "rdbms" in node_id:
        return f'<ellipse class="ics-icon" cx="{x+39}" cy="{y+41}" rx="14" ry="6"/><path class="ics-icon" d="M{x+25} {y+41}v24q14 11 28 0V{y+41}m-28 12q14 11 28 0"/>'
    if node_id == "delivery-regional":
        return f'<circle class="ics-icon" cx="{x+38}" cy="{y+42}" r="10"/><path class="ics-icon" d="M{x+22} {y+71}q2-18 16-18t16 18m2-28q10 1 10 13m-4 15q0-10-7-14"/>'
    if node_id in {"processing-spreadsheet", "delivery-portal"}:
        return f'<rect class="ics-icon" x="{x+23}" y="{y+30}" width="31" height="23" rx="2"/><path class="ics-icon" d="M{x+28} {y+61}h21m-10-8v8"/>'
    return f'<path class="ics-icon" d="M{x+26} {y+29}h20l10 10v31H{x+26}Z M{x+46} {y+29}v11h10"/>'


def _card(node_id, node):
    x, y, w, h = node["box"]
    state = node["state"]
    css = "ics-card bottleneck" if state == "bottleneck" else "ics-card external" if state.startswith("external") else "ics-card healthy" if state == "active" else "ics-card"
    detail_css = "ics-detail pain" if state == "bottleneck" else "ics-detail healthy" if state == "active" else "ics-detail"
    values = [part.strip() for part in node["label"].split(" | ", 1)]
    title = values[0]
    detail = values[1] if len(values) == 2 else state
    return (
        f'<g data-ics-node-id="{node_id}" data-state="{escape(state)}">'
        f'<rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>{_icon(node_id, x, y)}'
        f'<text class="ics-state" x="{x+78}" y="{y+28}">{escape(state.upper().replace("-", " "))}</text>'
        f'<text class="ics-title" x="{x+78}" y="{y+58}">{escape(title)}</text>'
        f'<text class="{detail_css}" x="{x+78}" y="{y+86}">{escape(detail)}</text></g>'
    )


def render_it_current_state(plan, corner_style="rounded"):
    layout = layout_it_current_state(plan, corner_style)
    parts = ['<g data-ics-contract="D-093-detailed-current-state" data-corner-style="' + corner_style + '"><defs><marker id="ics-arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker></defs>']
    for group_id in GROUP_ORDER:
        group = layout["groups"][group_id]
        x, y, w, h = group["box"]
        label_width = max(180, len(group["label"]) * 13)
        label_x = x + 40 + label_width / 2
        parts.append(
            f'<g data-ics-group-id="{group_id}"><rect class="ics-zone" x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/>'
            f'<rect class="ics-zone-label-bg" x="{x+40}" y="{y-10}" width="{label_width}" height="24"/>'
            f'<text class="ics-zone-label" x="{label_x}" y="{y+7}" text-anchor="middle">{escape(group["label"])}</text></g>'
        )
    for edge_id in EDGE_ORDER:
        edge = layout["edges"][edge_id]
        pain = edge_id in PAIN_EDGES
        external = edge_id in EXTERNAL_EDGES
        css = "ics-route pain" if pain else "ics-route external" if external else "ics-route"
        marker = "url(#ics-arrow-accent)" if pain else "url(#arrow)"
        parts.append(
            f'<path class="{css}" data-ics-edge-id="{edge_id}" data-corner-style="{corner_style}" data-source="{edge["source"]}" data-target="{edge["target"]}" d="{edge["path"]}" marker-end="{marker}"/>'
        )
        lx, ly = edge["label_position"]
        label = edge["label"]
        width = max(64, len(label) * 10 + 26)
        label_css = "ics-edge-label pain" if pain else "ics-edge-label"
        parts.append(
            f'<g data-ics-edge-label="{edge_id}"><rect class="ics-edge-label-bg" x="{lx-width/2:g}" y="{ly-16}" width="{width}" height="24" rx="3"/>'
            f'<text class="{label_css}" x="{lx}" y="{ly}" text-anchor="middle">{escape(label)}</text></g>'
        )
    for node_id in NODE_ORDER:
        parts.append(_card(node_id, layout["nodes"][node_id]))
    parts.append(
        '<line class="ics-legend-rule" x1="35" y1="925" x2="1965" y2="925"/>'
        '<text class="ics-legend-title" x="35" y="957">CHÚ GIẢI</text>'
        '<line class="ics-route" x1="175" y1="952" x2="225" y2="952"/><text class="ics-legend" x="240" y="958">Luồng dữ liệu</text>'
        '<line class="ics-route pain" x1="435" y1="952" x2="485" y2="952"/><text class="ics-legend" x="500" y="958">Điểm đau</text>'
        '<rect class="ics-card external" x="690" y="941" width="28" height="22" rx="4"/><text class="ics-legend" x="732" y="958">Bên ngoài</text>'
        '<rect class="ics-card bottleneck" x="930" y="941" width="28" height="22" rx="4"/><text class="ics-legend" x="972" y="958">Nút nghẽn</text>'
        '<text class="ics-legend" x="1965" y="958" text-anchor="end">Hiện trạng · không phải kiến trúc đích</text></g>'
    )
    return "".join(parts)


def validate_it_current_state_svg(svg):
    root = ET.fromstring(svg)
    nodes = {item.attrib["data-ics-node-id"]: item for item in root.findall(".//*[@data-ics-node-id]")}
    edges = {item.attrib["data-ics-edge-id"]: item for item in root.findall(".//*[@data-ics-edge-id]")}
    groups = {item.attrib["data-ics-group-id"]: item for item in root.findall(".//*[@data-ics-group-id]")}
    labels = {item.attrib["data-ics-edge-label"]: item for item in root.findall(".//*[@data-ics-edge-label]")}
    _require(set(nodes) == set(NODE_ORDER) and set(edges) == set(EDGE_ORDER), "D-093 serialized material mismatch")
    _require(set(groups) == set(GROUP_ORDER) and set(labels) == set(EDGE_ORDER), "D-093 serialized group/label mismatch")
    styles = {item.attrib.get("data-corner-style") for item in edges.values()}
    _require(len(styles) == 1 and styles <= {"rounded", "straight"}, "D-093 serialized corner mismatch")
    style = next(iter(styles))
    for edge_id, item in edges.items():
        expected = orthogonal_path(ROUTE_POINTS[edge_id], style, radius=22)
        _require(item.tag == "path" and item.attrib.get("d") == expected and expected.count("M") == 1, f"D-093 serialized route mismatch: {edge_id}")
    return {"nodes": 9, "edges": 8, "groups": 3, "edge_labels": 8, "continuous_routes": 8, "corner_style": style}


def it_current_state_table(plan):
    layout = layout_it_current_state(plan)
    rows = []
    for node_id in NODE_ORDER:
        node = layout["nodes"][node_id]
        rows.append(("node", node_id, node["role"], node["label"], node["state"], "—"))
    for edge_id in EDGE_ORDER:
        edge = layout["edges"][edge_id]
        rows.append(("edge", edge_id, edge["kind"], f'{edge["source"]} → {edge["target"]}', edge["label"], "rounded default"))
    for group_id in GROUP_ORDER:
        group = layout["groups"][group_id]
        rows.append(("group", group_id, "boundary", group["label"], "—", ", ".join(group["member_ids"])))
    return '<details class="ics-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Collection</th><th>Semantic ID</th><th>Role/kind</th><th>Nhãn/quan hệ</th><th>State/format</th><th>Chi tiết</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></details>'
