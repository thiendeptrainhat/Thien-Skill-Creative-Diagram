"""Detailed D-087 data-platform integration layout derived from semantic IDs."""
from html import escape
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 1800, 1040
EXPECTED_NODES = {
    "source-crm", "source-pos", "source-events",
    "platform-orchestrator", "platform-object-store", "platform-query",
    "consumer-bi", "consumer-notebook", "consumer-partner",
    "service-identity", "service-observability",
}
EXPECTED_EDGES = {
    "flow-crm-store", "flow-pos-store", "flow-events-store",
    "control-orchestrator-store", "control-orchestrator-query", "flow-store-query",
    "flow-query-bi", "flow-query-notebook", "flow-query-partner",
    "service-identity-store", "service-identity-query",
}
BOXES = {
    "source-crm": (60, 130, 270, 110),
    "source-pos": (60, 300, 270, 110),
    "source-events": (60, 470, 270, 110),
    "platform-orchestrator": (430, 160, 940, 90),
    "platform-object-store": (610, 315, 280, 125),
    "platform-query": (1010, 315, 280, 125),
    "consumer-bi": (1470, 130, 270, 110),
    "consumer-notebook": (1470, 300, 270, 110),
    "consumer-partner": (1470, 470, 270, 110),
    "service-identity": (60, 720, 1680, 90),
    "service-observability": (60, 840, 1680, 90),
}
BOUNDARY = (390, 90, 1020, 570)
ROUTES = {
    "flow-crm-store": "M330 185 H360 V275 H560 V345 H610",
    "flow-pos-store": "M330 355 H610",
    "flow-events-store": "M330 525 H560 V410 H610",
    "control-orchestrator-store": "M700 250 V315",
    "control-orchestrator-query": "M1150 250 V315",
    "flow-store-query": "M890 375 H1010",
    "flow-query-bi": "M1290 345 H1425 V185 H1470",
    "flow-query-notebook": "M1290 375 H1470",
    "flow-query-partner": "M1290 405 H1425 V525 H1470",
    "service-identity-store": "M760 720 V440",
    "service-identity-query": "M1160 720 V440",
}
ROUTE_CLASS = {
    **{key: "dp-route dp-primary" for key in EXPECTED_EDGES},
    "control-orchestrator-store": "dp-route dp-control",
    "control-orchestrator-query": "dp-route dp-control",
    "service-identity-store": "dp-route dp-service",
    "service-identity-query": "dp-route dp-service",
}
LABELS = {
    "flow-crm-store": (405, 168), "flow-pos-store": (405, 338),
    "flow-events-store": (405, 508), "control-orchestrator-store": (700, 283),
    "control-orchestrator-query": (1150, 283), "flow-store-query": (950, 358),
    "flow-query-bi": (1375, 328), "flow-query-notebook": (1375, 358),
    "flow-query-partner": (1375, 438), "service-identity-store": (730, 690),
    "service-identity-query": (1190, 690),
}


def _split(label):
    values = [part.strip() for part in label.split(" | ", 1)]
    return values[0], values[1] if len(values) == 2 else ""


def _projection(plan):
    return plan["semantic_projection"]


def is_detailed_dp_integration(plan):
    p = _projection(plan)
    return ({item["id"] for item in p["nodes"]} == EXPECTED_NODES
            and {item["id"] for item in p["edges"]} == EXPECTED_EDGES)


def layout_dp_integration(plan):
    p = _projection(plan)
    nodes = {item["id"]: item for item in p["nodes"]}
    edges = {item["id"]: item for item in p["edges"]}
    groups = {item["id"]: item for item in p["groups"]}
    if set(nodes) != EXPECTED_NODES or set(edges) != EXPECTED_EDGES or set(groups) != {"boundary-data-platform"}:
        raise ValueError("D-087 detailed DP integration material mismatch")
    group = groups["boundary-data-platform"]
    if set(group["member_ids"]) != {"platform-orchestrator", "platform-object-store", "platform-query"}:
        raise ValueError("D-087 platform ownership mismatch")
    if any(not edge["directed"] or edge["kind"] != "integration" for edge in edges.values()):
        raise ValueError("D-087 requires directed integration relations")
    expected_pairs = {
        "flow-crm-store": ("source-crm", "platform-object-store"),
        "flow-pos-store": ("source-pos", "platform-object-store"),
        "flow-events-store": ("source-events", "platform-object-store"),
        "control-orchestrator-store": ("platform-orchestrator", "platform-object-store"),
        "control-orchestrator-query": ("platform-orchestrator", "platform-query"),
        "flow-store-query": ("platform-object-store", "platform-query"),
        "flow-query-bi": ("platform-query", "consumer-bi"),
        "flow-query-notebook": ("platform-query", "consumer-notebook"),
        "flow-query-partner": ("platform-query", "consumer-partner"),
        "service-identity-store": ("service-identity", "platform-object-store"),
        "service-identity-query": ("service-identity", "platform-query"),
    }
    for edge_id, pair in expected_pairs.items():
        if (edges[edge_id]["source"], edges[edge_id]["target"]) != pair:
            raise ValueError(f"D-087 endpoint mismatch: {edge_id}")
    result = {
        "width": WIDTH, "height": HEIGHT, "boundary": BOUNDARY,
        "nodes": {key: {**nodes[key], "box": BOXES[key]} for key in EXPECTED_NODES},
        "edges": {key: {**edges[key], "path": ROUTES[key], "css": ROUTE_CLASS[key], "label_position": LABELS[key]} for key in EXPECTED_EDGES},
        "group": {**group, "box": BOUNDARY},
    }
    validate_dp_integration_layout(result)
    return result


def validate_dp_integration_layout(layout):
    bx, by, bw, bh = layout["boundary"]
    inside = {"platform-orchestrator", "platform-object-store", "platform-query"}
    outside = EXPECTED_NODES - inside
    for node_id, node in layout["nodes"].items():
        x, y, w, h = node["box"]
        if x < 30 or y < 30 or x + w > WIDTH - 30 or y + h > HEIGHT - 30:
            raise ValueError(f"Node outside canvas: {node_id}")
        contained = bx <= x and by <= y and x + w <= bx + bw and y + h <= by + bh
        if (node_id in inside) != contained:
            raise ValueError(f"Platform containment mismatch: {node_id}")
    if not all(edge["path"].startswith("M") and edge["path"].count("M") == 1 for edge in layout["edges"].values()):
        raise ValueError("Every integration route must be one continuous subpath")
    if set(layout["group"]["member_ids"]) != inside or not outside:
        raise ValueError("Platform ownership mismatch")


def validate_dp_integration_svg(svg):
    root = ET.fromstring(svg)
    nodes = {item.attrib["data-dp-node-id"]: item for item in root.findall(".//*[@data-dp-node-id]")}
    edges = {item.attrib["data-dp-edge-id"]: item for item in root.findall(".//*[@data-dp-edge-id]")}
    group = root.find(".//*[@data-dp-group-id='boundary-data-platform']")
    if set(nodes) != EXPECTED_NODES or set(edges) != EXPECTED_EDGES or group is None:
        raise ValueError("Serialized D-087 semantic binding mismatch")
    for edge_id, path in edges.items():
        if (path.tag != "path" or path.attrib.get("d") != ROUTES[edge_id]
                or path.attrib.get("marker-end") != "url(#arrow)"
                or path.attrib.get("class") != ROUTE_CLASS[edge_id]
                or path.attrib["d"].count("M") != 1):
            raise ValueError(f"Serialized D-087 route mismatch: {edge_id}")
    bx, by, bw, bh = BOUNDARY
    inside = {"platform-orchestrator", "platform-object-store", "platform-query"}
    for node_id, group_node in nodes.items():
        rect = group_node.find("rect")
        if rect is None:
            raise ValueError(f"Missing D-087 card: {node_id}")
        x, y, w, h = (float(rect.attrib[key]) for key in ("x", "y", "width", "height"))
        contained = bx <= x and by <= y and x + w <= bx + bw and y + h <= by + bh
        if (node_id in inside) != contained:
            raise ValueError(f"Serialized D-087 containment mismatch: {node_id}")
    return {"nodes": len(nodes), "edges": len(edges), "groups": 1, "continuous_routes": len(edges)}


def _card(node_id, node):
    x, y, w, h = node["box"]
    title, detail = _split(node["label"])
    if node_id in {"platform-object-store", "platform-query"}:
        css = "dp-card dp-focal"
    elif node_id == "platform-orchestrator":
        css = "dp-card dp-orchestrator"
    elif node_id == "service-identity":
        css = "dp-band dp-identity"
    elif node_id == "service-observability":
        css = "dp-band dp-observability"
    else:
        css = "dp-card dp-external"
    icon = ""
    if node_id.startswith("source-"):
        icon = f'<circle class="dp-icon" cx="{x+34}" cy="{y+42}" r="10"/><path class="dp-icon" d="M{x+24} {y+42}v18q10 8 20 0V{y+42}"/>'
    elif node_id.startswith("consumer-"):
        icon = f'<path class="dp-icon" d="M{x+24} {y+63}h24M{x+28} {y+59}V{y+46}m8 13V{y+36}m8 23V{y+42}"/>'
    elif node_id == "service-identity":
        icon = f'<circle class="dp-icon" cx="{x+42}" cy="{y+45}" r="9"/><path class="dp-icon" d="M{x+51} {y+45}h20m-7 0v7m-7-7v5"/>'
    elif node_id == "service-observability":
        icon = f'<path class="dp-icon" d="M{x+24} {y+60}h32m-27-6 8-12 7 5 9-17 8 5"/>'
    return (f'<g data-dp-node-id="{escape(node_id, quote=True)}"><rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>{icon}'
            f'<text class="dp-title" x="{x+74 if icon else x+w/2}" y="{y+46}" text-anchor="{ "start" if icon else "middle"}">{escape(title)}</text>'
            f'<text class="dp-detail" x="{x+74 if icon else x+w/2}" y="{y+74}" text-anchor="{ "start" if icon else "middle"}">{escape(detail)}</text></g>')


def render_dp_integration(plan):
    layout = layout_dp_integration(plan)
    bx, by, bw, bh = layout["boundary"]
    parts = [
        f'<g data-dp-group-id="boundary-data-platform"><rect class="dp-boundary" x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18"/>'
        f'<rect class="dp-boundary-label-bg" x="760" y="76" width="280" height="30"/><text class="dp-boundary-label" x="900" y="98" text-anchor="middle">NỀN TẢNG DỮ LIỆU</text></g>'
    ]
    for edge_id in sorted(layout["edges"], key=lambda key: layout["edges"][key].get("order", 999)):
        edge = layout["edges"][edge_id]
        lx, ly = edge["label_position"]
        parts.append(f'<path class="{edge["css"]}" data-dp-edge-id="{escape(edge_id, quote=True)}" d="{edge["path"]}" marker-end="url(#arrow)"/><rect class="dp-route-label-bg" x="{lx-42}" y="{ly-16}" width="84" height="24" rx="3"/><text class="dp-route-label" x="{lx}" y="{ly}" text-anchor="middle">{escape(edge.get("label", ""))}</text>')
    for node_id in ("source-crm", "source-pos", "source-events", "platform-orchestrator", "platform-object-store", "platform-query", "consumer-bi", "consumer-notebook", "consumer-partner", "service-identity", "service-observability"):
        parts.append(_card(node_id, layout["nodes"][node_id]))
    parts.append('<g aria-label="Chú giải DP integration"><line class="dp-legend-rule" x1="60" y1="975" x2="1740" y2="975"/><text class="micro" x="60" y="1008">TYPE KEY</text><rect class="dp-card dp-external" x="190" y="990" width="28" height="22" rx="3"/><text class="dp-legend-text" x="232" y="1007">Nguồn / consumer</text><rect class="dp-card dp-focal" x="470" y="990" width="28" height="22" rx="3"/><text class="dp-legend-text" x="512" y="1007">Lõi nền tảng</text><rect class="dp-card dp-orchestrator" x="745" y="990" width="28" height="22" rx="3"/><text class="dp-legend-text" x="787" y="1007">Điều phối</text><line class="dp-route dp-primary" x1="1010" y1="1001" x2="1060" y2="1001" marker-end="url(#arrow)"/><text class="dp-legend-text" x="1077" y="1007">Luồng dữ liệu</text><line class="dp-route dp-service" x1="1335" y1="1001" x2="1385" y2="1001" marker-end="url(#arrow)"/><text class="dp-legend-text" x="1402" y="1007">Dịch vụ dùng chung</text></g>')
    return "".join(parts)


def dp_integration_css(tokens):
    return '''
    .dp-boundary{fill:color-mix(in srgb,var(--surface-alt) 54%,transparent);stroke:var(--border);stroke-width:1.8}
    .dp-boundary-label-bg,.dp-route-label-bg{fill:var(--canvas)}
    .dp-boundary-label{font:700 13px Menlo,Monaco,monospace;letter-spacing:.17em;fill:var(--muted)}
    .dp-card,.dp-band{fill:var(--surface);stroke:var(--connector);stroke-width:1.9}
    .dp-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.3}.dp-orchestrator{fill:var(--surface-alt);stroke:var(--border)}
    .dp-identity{fill:color-mix(in srgb,var(--accent-soft) 42%,var(--surface));stroke:color-mix(in srgb,var(--accent) 34%,var(--border))}
    .dp-observability{fill:color-mix(in srgb,var(--surface-alt) 70%,var(--surface));stroke:var(--border)}
    .dp-title{font:650 17px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.dp-detail{font:500 12px Menlo,Monaco,monospace;fill:var(--muted)}
    .dp-icon{fill:none;stroke:var(--connector);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
    .dp-route{fill:none;stroke-linecap:round;stroke-linejoin:round}.dp-primary{stroke:var(--accent);stroke-width:2.6}.dp-control{stroke:var(--connector);stroke-width:1.8}.dp-service{stroke:var(--accent);stroke-width:2;stroke-dasharray:8 7}
    .dp-route-label{font:700 11px Menlo,Monaco,monospace;letter-spacing:.06em;fill:var(--accent-text)}
    .dp-legend-rule{stroke:var(--grid);stroke-width:1.4}.dp-legend-text{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}
    .dp-details{overflow-x:auto}.dp-details table{min-width:980px}.dp-details th,.dp-details td:last-child{width:auto}
    '''


def dp_integration_table(plan):
    layout = layout_dp_integration(plan)
    node_rows = []
    for node_id in sorted(layout["nodes"]):
        node = layout["nodes"][node_id]
        title, detail = _split(node["label"])
        node_rows.append(("node", node_id, node["role"], title, detail))
    edge_rows = [("edge", edge_id, edge["kind"], f'{edge["source"]} → {edge["target"]}', edge.get("label", "")) for edge_id, edge in sorted(layout["edges"].items())]
    group = layout["group"]
    rows = node_rows + edge_rows + [("group", group["id"], "boundary", group["label"], ", ".join(group["member_ids"]))]
    return '<details class="dp-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Collection</th><th scope="col">Semantic IDs</th><th scope="col">Role / kind</th><th scope="col">Nhãn / quan hệ</th><th scope="col">Chi tiết</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(value)+'</td>' for value in row)+'</tr>' for row in rows)+'</tbody></table></details>'
