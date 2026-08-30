"""D-104 UML model remediated by the global D-105 connector policy."""
from __future__ import annotations

from collections import Counter
from html import escape
import xml.etree.ElementTree as ET

from connector_policy_v15 import (
    CONNECTOR_POLICY_ID, centered_port, evenly_distributed_ports,
    straight_path, validate_even_ports,
)


WIDTH, HEIGHT = 1840, 1320
EXPECTED_CONTAINERS = (
    "class-billing-service", "interface-payment-option", "class-digital-wallet",
    "class-wire-transfer", "class-invoice", "class-invoice-item", "class-account",
)
EXPECTED_RELATIONSHIPS = (
    "relation-service-uses-option", "relation-wallet-realizes-option",
    "relation-wire-realizes-option", "relation-invoice-owns-items",
    "relation-invoice-belongs-account",
)
EXPECTED_MEMBER_COUNTS = {
    "class-billing-service": 1, "interface-payment-option": 2,
    "class-digital-wallet": 3, "class-wire-transfer": 2,
    "class-invoice": 3, "class-invoice-item": 3, "class-account": 3,
}
BOXES = {
    "class-billing-service": (60, 70, 560, 165),
    "interface-payment-option": (680, 50, 1080, 205),
    "class-digital-wallet": (865, 425, 350, 230),
    "class-wire-transfer": (1225, 425, 350, 200),
    "class-invoice": (100, 800, 410, 250),
    "class-invoice-item": (720, 800, 410, 250),
    "class-account": (1300, 800, 410, 250),
}
INTERFACE_PORTS = evenly_distributed_ports(680, 1760, 2)
INTERFACE_CENTER_Y = centered_port(50, 255)
RELATIONSHIPS = {
    "relation-service-uses-option": {
        "source": "class-billing-service", "target": "interface-payment-option",
        "kind": "dependency", "path": straight_path((620, INTERFACE_CENTER_Y), (680, INTERFACE_CENTER_Y)), "label": "USES",
        "label_position": (650, 127), "marker_end": "url(#uml-open-arrow)",
        "route_priority": "straight", "port_rule": "single-centered",
    },
    "relation-wallet-realizes-option": {
        "source": "class-digital-wallet", "target": "interface-payment-option",
        "kind": "realization", "path": straight_path((INTERFACE_PORTS[0], 425), (INTERFACE_PORTS[0], 255)), "label": "",
        "label_position": None, "marker_end": "url(#uml-hollow-triangle)",
        "route_priority": "straight", "port_rule": "multiple-even",
    },
    "relation-wire-realizes-option": {
        "source": "class-wire-transfer", "target": "interface-payment-option",
        "kind": "realization", "path": straight_path((INTERFACE_PORTS[1], 425), (INTERFACE_PORTS[1], 255)), "label": "",
        "label_position": None, "marker_end": "url(#uml-hollow-triangle)",
        "route_priority": "straight", "port_rule": "multiple-even",
    },
    "relation-invoice-owns-items": {
        "source": "class-invoice", "target": "class-invoice-item",
        "kind": "composition", "path": "M510 925 H720", "label": "",
        "label_position": None, "marker_start": "url(#uml-filled-diamond)",
        "cardinalities": ((555, 925, "1"), (682, 925, "1..*")),
        "route_priority": "straight", "port_rule": "single-centered",
    },
    "relation-invoice-belongs-account": {
        "source": "class-invoice", "target": "class-account",
        "kind": "association", "path": "M305 1050 V1130 Q305 1150 325 1150 H1485 Q1505 1150 1505 1130 V1050",
        "label": "", "label_position": None, "marker_end": "url(#uml-open-arrow)",
        "cardinalities": ((335, 1084, "0..*"), (1505, 1084, "1")),
        "route_priority": "orthogonal-required", "port_rule": "single-centered",
        "route_exception": "avoid-domain-cards",
    },
}
LEGEND_KINDS = ("inheritance", "realization", "composition", "aggregation", "association", "dependency")


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_uml_class(plan):
    contract = plan.get("semantic_projection", {}).get("compartment_contract", {})
    return {item.get("id") for item in contract.get("containers", [])} == set(EXPECTED_CONTAINERS)


def layout_uml_class(plan):
    contract = plan["semantic_projection"]["compartment_contract"]
    containers = {item["id"]: item for item in contract["containers"]}
    relations = {item["id"]: item for item in contract["relationships"]}
    _require(set(containers) == set(EXPECTED_CONTAINERS), "D-104 UML container material mismatch")
    _require(set(relations) == set(EXPECTED_RELATIONSHIPS), "D-104 UML relationship material mismatch")
    for item_id, expected_count in EXPECTED_MEMBER_COUNTS.items():
        _require(containers[item_id]["role"] == "class", f"D-104 container role mismatch: {item_id}")
        _require(len(containers[item_id]["members"]) == expected_count, f"D-104 member count mismatch: {item_id}")
    kinds = Counter(item.get("relation_kind") for item in relations.values())
    _require(kinds == Counter({"realization": 2, "dependency": 1, "composition": 1, "association": 1}), "D-104 UML relation-kind mix mismatch")
    for relation_id, specification in RELATIONSHIPS.items():
        relation = relations[relation_id]
        _require((relation["source"], relation["target"], relation["relation_kind"]) == (specification["source"], specification["target"], specification["kind"]), f"D-104 endpoint or relation mismatch: {relation_id}")
    _require(relations["relation-invoice-owns-items"].get("source_multiplicity") == "1" and relations["relation-invoice-owns-items"].get("target_multiplicity") == "1..*", "D-104 composition multiplicity mismatch")
    _require(relations["relation-invoice-belongs-account"].get("source_multiplicity") == "0..*" and relations["relation-invoice-belongs-account"].get("target_multiplicity") == "1", "D-104 association multiplicity mismatch")
    layout = {
        "width": WIDTH, "height": HEIGHT,
        "containers": {item_id: {**containers[item_id], "box": BOXES[item_id]} for item_id in EXPECTED_CONTAINERS},
        "relationships": {item_id: {**relations[item_id], **RELATIONSHIPS[item_id]} for item_id in EXPECTED_RELATIONSHIPS},
    }
    validate_uml_class_layout(layout)
    return layout


def validate_uml_class_layout(layout):
    validate_even_ports(680, 1760, INTERFACE_PORTS)
    _require(INTERFACE_CENTER_Y == 152.5, "D-105 single dependency port must be centered")
    for item_id, item in layout["containers"].items():
        x, y, width, height = item["box"]
        _require(x >= 40 and y >= 40 and x + width <= WIDTH - 40 and y + height <= 1070, f"D-104 class outside canvas: {item_id}")
        _require(height >= 95 + len(item["members"]) * 34, f"D-104 member overflow: {item_id}")
    for relation_id, item in layout["relationships"].items():
        _require(item["path"].startswith("M") and item["path"].count("M") == 1, f"D-104 relation must be one continuous path: {relation_id}")
        _require(item.get("route_priority") in {"straight", "orthogonal-required"}, f"D-105 route priority missing: {relation_id}")


def uml_class_css(tokens):
    return """
    .uml-card{fill:var(--surface);stroke:var(--text);stroke-width:2.1}.uml-card.is-interface{fill:color-mix(in srgb,var(--accent-soft) 48%,var(--surface));stroke:var(--accent);stroke-width:2.7}
    .uml-header{fill:color-mix(in srgb,var(--connector) 5%,var(--surface))}.uml-header.is-interface{fill:var(--accent-soft)}
    .uml-divider{stroke:var(--border);stroke-width:1.7}.uml-divider.is-interface{stroke:var(--accent);opacity:.55}
    .uml-stereotype{font:700 13px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--accent-text)}
    .uml-title{font:700 22px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .uml-member{font:600 15px Menlo,Monaco,monospace;fill:var(--text)}
    .uml-relation{fill:none;stroke:var(--connector);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}.uml-relation.is-dashed{stroke-dasharray:9 8}.uml-relation.is-realization{stroke:var(--accent)}
    .uml-relation-label,.uml-cardinality{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.4px;fill:var(--muted)}.uml-cardinality{font-size:14px;letter-spacing:0;fill:var(--text)}
    .uml-knockout{fill:var(--canvas);stroke:none}.uml-legend-rule{stroke:var(--grid);stroke-width:1.4}.uml-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}
    .uml-legend-label{font:550 12px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}.uml-legend-line{fill:none;stroke:var(--connector);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.uml-legend-line.is-dashed{stroke-dasharray:8 7}
    .uml-details{overflow-x:auto}.uml-details table{min-width:1040px}
    """


def _text(x, y, value, css, anchor="start"):
    return f'<text class="{css}" x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _member_text(member):
    symbol = "+" if member.get("visibility") == "public" else "−"
    if member["kind"] == "operation":
        value = member.get("signature") or f'{member["name"]}()'
    else:
        value = f'{member["name"]}: {member.get("data_type", "Any")}'
    return f"{symbol} {value}"


def _card(item_id, item):
    x, y, width, height = item["box"]
    interface = item_id == "interface-payment-option"
    header_height = 78 if interface else 72
    modifier = " is-interface" if interface else ""
    parts = [f'<g data-uml-container-id="{item_id}" data-uml-role="{"interface" if interface else "class"}">']
    parts.append(f'<rect class="uml-card{modifier}" x="{x}" y="{y}" width="{width}" height="{height}" rx="11"/>')
    parts.append(f'<path class="uml-header{modifier}" d="M{x+11} {y+1} H{x+width-11} Q{x+width-1} {y+1} {x+width-1} {y+11} V{y+header_height} H{x+1} V{y+11} Q{x+1} {y+1} {x+11} {y+1} Z"/>')
    if interface:
        parts.append(_text(x + width / 2, y + 27, "«interface»", "uml-stereotype", "middle"))
        parts.append(_text(x + width / 2, y + 59, item["label"], "uml-title", "middle"))
    else:
        parts.append(_text(x + width / 2, y + 45, item["label"], "uml-title", "middle"))
    parts.append(f'<line class="uml-divider{modifier}" x1="{x}" y1="{y+header_height}" x2="{x+width}" y2="{y+header_height}"/>')
    for index, member in enumerate(item["members"]):
        parts.append(f'<g data-uml-member-id="{member["id"]}" data-uml-owner-id="{item_id}">')
        parts.append(_text(x + 28, y + header_height + 39 + index * 36, _member_text(member), "uml-member"))
        parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def _cardinality(relation_id, index, x, y, value):
    width = max(26, len(value) * 10 + 12)
    return (
        f'<rect class="uml-knockout" x="{x-width/2:.2f}" y="{y-16:.2f}" width="{width:.2f}" height="25" rx="3" data-uml-cardinality-knockout="{relation_id}:{index}"/>'
        + _text(x, y + 3, value, "uml-cardinality", "middle").replace(">", f' data-uml-cardinality="{relation_id}:{index}" data-cardinality-value="{escape(value)}">', 1)
    )


def _defs():
    return '''<defs>
    <marker id="uml-open-arrow" markerWidth="15" markerHeight="15" refX="13" refY="7.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L13 7.5 L1 14" fill="none" stroke="var(--connector)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker>
    <marker id="uml-hollow-triangle" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L16 9 L1 17 Z" fill="var(--canvas)" stroke="var(--accent)" stroke-width="2"/></marker>
    <marker id="uml-filled-diamond" markerWidth="20" markerHeight="16" refX="2" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 8 L9 2 L17 8 L9 14 Z" fill="var(--text)" stroke="var(--text)" stroke-width="1.5"/></marker>
    <marker id="uml-hollow-diamond" markerWidth="20" markerHeight="16" refX="2" refY="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 8 L9 2 L17 8 L9 14 Z" fill="var(--canvas)" stroke="var(--connector)" stroke-width="1.5"/></marker>
    <marker id="uml-hollow-triangle-muted" markerWidth="18" markerHeight="18" refX="16" refY="9" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L16 9 L1 17 Z" fill="var(--canvas)" stroke="var(--connector)" stroke-width="2"/></marker>
    </defs>'''


def _legend():
    y = 1230
    starts = (60, 350, 640, 930, 1220, 1510)
    labels = ("Inheritance", "Realization", "Composition · owns", "Aggregation · has", "Association", "Dependency · uses")
    parts = [f'<line class="uml-legend-rule" x1="60" y1="1190" x2="1780" y2="1190"/>', _text(60, 1215, "CHÚ GIẢI · QUAN HỆ", "uml-legend-title")]
    for kind, label, x in zip(LEGEND_KINDS, labels, starts):
        css = "uml-legend-line is-dashed" if kind in {"realization", "dependency"} else "uml-legend-line"
        marker_start = ' marker-start="url(#uml-filled-diamond)"' if kind == "composition" else ' marker-start="url(#uml-hollow-diamond)"' if kind == "aggregation" else ""
        marker_end = ' marker-end="url(#uml-hollow-triangle-muted)"' if kind in {"inheritance", "realization"} else ' marker-end="url(#uml-open-arrow)"' if kind in {"association", "dependency"} else ""
        parts.append(f'<g data-uml-legend-kind="{kind}"><path class="{css}" d="M{x} {y} H{x+48}"{marker_start}{marker_end}/>{_text(x+66, y+5, label, "uml-legend-label")}</g>')
    return "".join(parts)


def render_uml_class(plan):
    layout = layout_uml_class(plan)
    parts = [f'<g data-uml-class-contract="D-104-seven-container-five-relation-model" data-connector-policy="{CONNECTOR_POLICY_ID}" data-route-priority="straight-first">', _defs()]
    for item_id in EXPECTED_CONTAINERS:
        parts.append(_card(item_id, layout["containers"][item_id]))
    for relation_id in EXPECTED_RELATIONSHIPS:
        relation = layout["relationships"][relation_id]
        css = "uml-relation"
        if relation["kind"] in {"dependency", "realization"}:
            css += " is-dashed"
        if relation["kind"] == "realization":
            css += " is-realization"
        marker_start = f' marker-start="{relation["marker_start"]}"' if relation.get("marker_start") else ""
        marker_end = f' marker-end="{relation["marker_end"]}"' if relation.get("marker_end") else ""
        exception = f' data-route-exception="{relation["route_exception"]}"' if relation.get("route_exception") else ""
        parts.append(f'<path class="{css}" data-uml-relation-id="{relation_id}" data-relation-kind="{relation["kind"]}" data-source="{relation["source"]}" data-target="{relation["target"]}" data-continuous-subpaths="1" data-port-rule="{relation["port_rule"]}" data-route-priority="{relation["route_priority"]}"{exception} d="{relation["path"]}"{marker_start}{marker_end}/>')
        if relation.get("label_position"):
            lx, ly = relation["label_position"]
            parts.append(_text(lx, ly, relation["label"], "uml-relation-label", "middle"))
        for index, cardinality in enumerate(relation.get("cardinalities", ()), 1):
            parts.append(_cardinality(relation_id, index, *cardinality))
    parts.append(_legend())
    parts.append("</g>")
    return "".join(parts)


def validate_uml_class_svg(svg):
    root = ET.fromstring(svg)
    containers = {item.attrib["data-uml-container-id"]: item for item in root.findall(".//*[@data-uml-container-id]")}
    members = {item.attrib["data-uml-member-id"]: item for item in root.findall(".//*[@data-uml-member-id]")}
    relations = {item.attrib["data-uml-relation-id"]: item for item in root.findall(".//*[@data-uml-relation-id]")}
    legends = {item.attrib["data-uml-legend-kind"]: item for item in root.findall(".//*[@data-uml-legend-kind]")}
    cardinalities = root.findall(".//*[@data-uml-cardinality]")
    _require(set(containers) == set(EXPECTED_CONTAINERS), "Serialized D-104 container mismatch")
    _require(len(members) == 17, "Serialized D-104 member mismatch")
    _require(set(relations) == set(EXPECTED_RELATIONSHIPS), "Serialized D-104 relation mismatch")
    _require(set(legends) == set(LEGEND_KINDS), "Serialized D-104 legend mismatch")
    _require(len(cardinalities) == 4, "Serialized D-104 cardinality mismatch")
    for relation_id, item in relations.items():
        specification = RELATIONSHIPS[relation_id]
        _require(item.tag == "path" and item.attrib.get("d") == specification["path"], f"Serialized D-104 route mismatch: {relation_id}")
        _require(item.attrib.get("data-continuous-subpaths") == "1" and item.attrib.get("d", "").count("M") == 1, f"Serialized D-104 discontinuity: {relation_id}")
        _require(item.attrib.get("data-relation-kind") == specification["kind"], f"Serialized D-104 kind mismatch: {relation_id}")
        _require(item.attrib.get("data-port-rule") == specification["port_rule"], f"Serialized D-105 port rule mismatch: {relation_id}")
        _require(item.attrib.get("data-route-priority") == specification["route_priority"], f"Serialized D-105 route priority mismatch: {relation_id}")
    _require(relations["relation-invoice-belongs-account"].attrib.get("d", "").count("Q") == 2, "D-104 association requires rounded 90-degree corners")
    return {"containers": 7, "members": 17, "relationships": 5, "legend_kinds": 6, "cardinalities": 4}


def uml_class_table(plan):
    layout = layout_uml_class(plan)
    rows = []
    for item_id in EXPECTED_CONTAINERS:
        item = layout["containers"][item_id]
        displayed_role = "Interface" if item_id == "interface-payment-option" else "Class"
        for nested in item["members"]:
            detail = nested.get("signature") if nested["kind"] == "operation" else nested.get("data_type")
            rows.append(f'<tr><td>{escape(item["label"])}</td><td>{displayed_role}</td><td>{escape(nested["kind"])}</td><td><code>{escape(nested["name"])}</code></td><td><code>{escape(str(detail))}</code></td></tr>')
    for relation_id in EXPECTED_RELATIONSHIPS:
        item = layout["relationships"][relation_id]
        multiplicity = f'{item.get("source_multiplicity") or "—"} → {item.get("target_multiplicity") or "—"}'
        rows.append(f'<tr><td colspan="2">{escape(relation_id)}</td><td>{escape(item["kind"])}</td><td><code>{escape(item["source"])} → {escape(item["target"])}</code></td><td>{escape(multiplicity)}</td></tr>')
    return '<details class="uml-details"><summary>Dữ liệu UML thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Container / relation</th><th scope="col">Role</th><th scope="col">Kind</th><th scope="col">Member / endpoints</th><th scope="col">Signature / cardinality</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></details>"
