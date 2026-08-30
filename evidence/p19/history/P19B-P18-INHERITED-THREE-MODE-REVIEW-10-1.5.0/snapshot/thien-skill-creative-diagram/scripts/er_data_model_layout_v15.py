"""D-090 detailed article-domain ER layout from compartment semantic material."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 2000, 940
EXPECTED_ENTITIES = ("entity-author", "entity-article", "entity-tag", "entity-article-tag")
EXPECTED_RELATIONSHIPS = (
    "relation-author-writes-article",
    "relation-article-tagged-via",
    "relation-tag-used-by",
)
EXPECTED_MEMBER_COUNTS = {
    "entity-author": 5,
    "entity-article": 8,
    "entity-tag": 4,
    "entity-article-tag": 2,
}
BOXES = {
    "entity-author": (70, 260, 430, 330),
    "entity-article": (760, 145, 500, 530),
    "entity-tag": (1540, 145, 390, 335),
    "entity-article-tag": (1540, 570, 390, 220),
}
RELATIONSHIPS = {
    "relation-author-writes-article": {
        "source": "entity-author", "target": "entity-article", "label": "WRITES",
        "path": "M500 425 H760", "source_label": (524, 434), "target_label": (736, 434), "label_position": (630, 390),
    },
    "relation-article-tagged-via": {
        "source": "entity-article", "target": "entity-article-tag", "label": "TAGGED VIA",
        "path": "M1260 545 H1380 Q1420 545 1420 585 V655 Q1420 680 1450 680 H1540", "source_label": (1282, 555), "target_label": (1518, 690), "label_position": (1385, 520),
    },
    "relation-tag-used-by": {
        "source": "entity-tag", "target": "entity-article-tag", "label": "USED BY",
        "path": "M1735 480 V570", "source_label": (1752, 505), "target_label": (1752, 558), "label_position": (1810, 530),
    },
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_er_data_model(plan):
    contract = plan.get("semantic_projection", {}).get("compartment_contract", {})
    return {item.get("id") for item in contract.get("containers", [])} == set(EXPECTED_ENTITIES)


def layout_er_data_model(plan):
    contract = plan["semantic_projection"]["compartment_contract"]
    entities = {item["id"]: item for item in contract["containers"]}
    relations = {item["id"]: item for item in contract["relationships"]}
    _require(set(entities) == set(EXPECTED_ENTITIES), "D-090 entity material mismatch")
    _require(set(relations) == set(EXPECTED_RELATIONSHIPS), "D-090 relationship material mismatch")
    _require(entities["entity-article"]["role"] == "entity", "D-090 aggregate root must remain an entity")
    _require(entities["entity-article-tag"]["role"] == "associative-entity", "D-090 join node must be associative")
    member_ids = set()
    for entity_id, expected_count in EXPECTED_MEMBER_COUNTS.items():
        members = entities[entity_id]["members"]
        _require(len(members) == expected_count, f"D-090 member count mismatch: {entity_id}")
        for member in members:
            _require(member["kind"] == "attribute" and member.get("data_type"), "D-090 fields require typed attributes")
            _require(member["id"] not in member_ids, "D-090 duplicate member ID")
            _require(set(member.get("constraints", [])) <= {"primary-key", "foreign-key", "unique"}, "D-090 unsupported field constraint")
            member_ids.add(member["id"])
    _require(len(member_ids) == 19, "D-090 requires exactly 19 fields")
    for relation_id, specification in RELATIONSHIPS.items():
        relation = relations[relation_id]
        _require((relation["source"], relation["target"]) == (specification["source"], specification["target"]), f"D-090 endpoint mismatch: {relation_id}")
        _require(relation["kind"] == "one-to-many" and relation.get("source_multiplicity") == "1" and relation.get("target_multiplicity") == "N", f"D-090 cardinality mismatch: {relation_id}")
    layout = {
        "width": WIDTH, "height": HEIGHT,
        "entities": {item_id: {**entities[item_id], "box": BOXES[item_id]} for item_id in EXPECTED_ENTITIES},
        "relationships": {item_id: {**relations[item_id], **RELATIONSHIPS[item_id]} for item_id in EXPECTED_RELATIONSHIPS},
    }
    validate_er_data_model_layout(layout)
    return layout


def validate_er_data_model_layout(layout):
    for entity_id, item in layout["entities"].items():
        x, y, width, height = item["box"]
        _require(x >= 40 and y >= 40 and x + width <= WIDTH - 40 and y + height <= HEIGHT - 100, f"D-090 entity outside canvas: {entity_id}")
        required_height = 104 + len(item["members"]) * 43
        _require(height >= required_height, f"D-090 member rows overflow: {entity_id}")
    for relation_id, item in layout["relationships"].items():
        _require(item["path"].startswith("M") and item["path"].count("M") == 1, f"D-090 discontinuous relation: {relation_id}")


def er_data_model_css(tokens):
    return """
    .er-card{fill:var(--surface);stroke:var(--connector);stroke-width:2.1}
    .er-card.is-aggregate{fill:color-mix(in srgb,var(--accent-soft) 42%,var(--surface));stroke:var(--accent);stroke-width:2.7}
    .er-card.is-join{fill:color-mix(in srgb,var(--connector) 9%,var(--surface));stroke:var(--connector);stroke-width:2.1;stroke-dasharray:9 7}
    .er-header{fill:color-mix(in srgb,var(--connector) 6%,var(--surface))}
    .er-header.is-aggregate{fill:var(--accent-soft)}.er-header.is-join{fill:color-mix(in srgb,var(--connector) 13%,var(--surface))}
    .er-divider{stroke:var(--border);stroke-width:1.6}.er-divider.is-aggregate{stroke:var(--accent);opacity:.62}
    .er-kind{font:700 13px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}.er-kind.is-aggregate{fill:var(--accent-text)}
    .er-title{font:700 25px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .er-field,.er-type,.er-key{font:600 16px Menlo,Monaco,monospace;fill:var(--text)}.er-type{fill:var(--connector)}.er-key{font-weight:750}
    .er-relation{fill:none;stroke:var(--connector);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
    .er-relation-label,.er-cardinality{font:700 13px Menlo,Monaco,monospace;letter-spacing:1.5px;fill:var(--muted)}.er-cardinality{font-size:17px;letter-spacing:0;fill:var(--connector)}
    .er-legend-rule{stroke:var(--grid);stroke-width:1.3}.er-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}
    .er-legend-label{font:550 14px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}
    .er-details{overflow-x:auto}.er-details table{min-width:980px}
    """


def _text(x, y, value, css, anchor="start"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _card(entity_id, entity):
    x, y, width, height = entity["box"]
    aggregate = entity_id == "entity-article"
    join = entity_id == "entity-article-tag"
    modifier = " is-aggregate" if aggregate else " is-join" if join else ""
    kind = "ENTITY · AGGREGATE ROOT" if aggregate else "JOIN · ASSOCIATIVE ENTITY" if join else "ENTITY"
    parts = [f'<g data-er-entity-id="{entity_id}" data-er-role="{entity["role"]}">']
    parts.append(f'<rect class="er-card{modifier}" x="{x}" y="{y}" width="{width}" height="{height}" rx="11"/>')
    parts.append(f'<path class="er-header{modifier}" d="M{x+11} {y+1} H{x+width-11} Q{x+width-1} {y+1} {x+width-1} {y+11} V{y+82} H{x+1} V{y+11} Q{x+1} {y+1} {x+11} {y+1} Z"/>')
    parts.append(_text(x + 30, y + 32, kind, f"er-kind{modifier}"))
    parts.append(_text(x + 30, y + 65, entity["label"], "er-title"))
    parts.append(f'<line class="er-divider{" is-aggregate" if aggregate else ""}" x1="{x}" y1="{y+83}" x2="{x+width}" y2="{y+83}"/>')
    for index, member in enumerate(entity["members"]):
        baseline = y + 125 + index * 43
        constraints = set(member.get("constraints", []))
        symbol = "#" if "primary-key" in constraints else "→" if "foreign-key" in constraints else ""
        parts.append(f'<g data-er-member-id="{member["id"]}" data-er-owner-id="{entity_id}">')
        parts.append(_text(x + 30, baseline, symbol, "er-key"))
        parts.append(_text(x + 58, baseline, member["name"], "er-field"))
        parts.append(_text(x + width - 30, baseline, member["data_type"], "er-type", "end"))
        parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def render_er_data_model(plan):
    layout = layout_er_data_model(plan)
    parts = ['<g data-er-contract="D-090-four-entity-cardinality-model">']
    for entity_id in EXPECTED_ENTITIES:
        parts.append(_card(entity_id, layout["entities"][entity_id]))
    for relation_id in EXPECTED_RELATIONSHIPS:
        relation = layout["relationships"][relation_id]
        parts.append(f'<path class="er-relation" data-er-edge-id="{relation_id}" data-source="{relation["source"]}" data-target="{relation["target"]}" data-source-multiplicity="1" data-target-multiplicity="N" d="{relation["path"]}"/>')
        sx, sy = relation["source_label"]; tx, ty = relation["target_label"]; lx, ly = relation["label_position"]
        parts.append(_text(sx, sy, "1", "er-cardinality", "middle"))
        parts.append(_text(tx, ty, "N", "er-cardinality", "middle"))
        parts.append(_text(lx, ly, relation["label"], "er-relation-label", "middle"))
    legend_y = 850
    parts.append(f'<line class="er-legend-rule" x1="60" y1="{legend_y-28}" x2="1940" y2="{legend_y-28}"/>')
    parts.append(_text(60, legend_y, "CHÚ GIẢI", "er-legend-title"))
    parts.append(f'<rect class="er-card is-aggregate" x="60" y="{legend_y+22}" width="28" height="22" rx="4"/>')
    parts.append(_text(102, legend_y + 39, "Aggregate root", "er-legend-label"))
    parts.append(f'<rect class="er-card" x="360" y="{legend_y+22}" width="28" height="22" rx="4"/>')
    parts.append(_text(402, legend_y + 39, "Entity", "er-legend-label"))
    parts.append(f'<rect class="er-card is-join" x="590" y="{legend_y+22}" width="28" height="22" rx="4"/>')
    parts.append(_text(632, legend_y + 39, "Associative entity", "er-legend-label"))
    parts.append(_text(940, legend_y + 39, "#  Primary key", "er-legend-label"))
    parts.append(_text(1190, legend_y + 39, "→  Foreign key", "er-legend-label"))
    parts.append(_text(1510, legend_y + 39, "1 / N  Cardinality", "er-legend-label"))
    parts.append("</g>")
    return "".join(parts)


def validate_er_data_model_svg(svg):
    root = ET.fromstring(svg)
    entities = {item.attrib["data-er-entity-id"]: item for item in root.findall(".//*[@data-er-entity-id]")}
    members = {item.attrib["data-er-member-id"]: item for item in root.findall(".//*[@data-er-member-id]")}
    edges = {item.attrib["data-er-edge-id"]: item for item in root.findall(".//*[@data-er-edge-id]")}
    _require(set(entities) == set(EXPECTED_ENTITIES), "Serialized D-090 entity mismatch")
    _require(len(members) == 19, "Serialized D-090 member mismatch")
    _require(set(edges) == set(EXPECTED_RELATIONSHIPS), "Serialized D-090 relationship mismatch")
    _require(sum(item.attrib.get("data-er-role") == "associative-entity" for item in entities.values()) == 1, "Serialized D-090 join count mismatch")
    for edge_id, item in edges.items():
        specification = RELATIONSHIPS[edge_id]
        _require(item.tag == "path" and item.attrib.get("d") == specification["path"] and item.attrib.get("data-source") == specification["source"] and item.attrib.get("data-target") == specification["target"], f"Serialized D-090 route mismatch: {edge_id}")
        _require(item.attrib.get("data-source-multiplicity") == "1" and item.attrib.get("data-target-multiplicity") == "N", f"Serialized D-090 cardinality mismatch: {edge_id}")
    return {"entities": 4, "members": 19, "relationships": 3, "aggregate": 1, "join": 1}


def er_data_model_table(plan):
    layout = layout_er_data_model(plan)
    rows = []
    for entity_id in EXPECTED_ENTITIES:
        entity = layout["entities"][entity_id]
        entity_role = "Aggregate root" if entity_id == "entity-article" else "Associative entity" if entity_id == "entity-article-tag" else "Entity"
        for member in entity["members"]:
            constraints = ", ".join(member.get("constraints", [])) or "—"
            rows.append(f'<tr><td>{escape(entity["label"])}</td><td>{escape(entity_role)}</td><td><code>{escape(member["name"])}</code></td><td><code>{escape(member["data_type"])}</code></td><td>{escape(constraints)}</td></tr>')
    for relation_id in EXPECTED_RELATIONSHIPS:
        relation = layout["relationships"][relation_id]
        source = layout["entities"][relation["source"]]["label"]
        target = layout["entities"][relation["target"]]["label"]
        rows.append(f'<tr><td>{escape(source)} → {escape(target)}</td><td>Relationship</td><td><code>{escape(relation_id)}</code></td><td>one-to-many</td><td>1 / N</td></tr>')
    return (
        '<details class="er-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Bốn entity, mười chín field và ba quan hệ một-nhiều; PK/FK và cardinality được thể hiện bằng cả ký hiệu lẫn dữ liệu bảng.</p>'
        '<table><thead><tr><th scope="col">Entity / relation</th><th scope="col">Vai trò</th><th scope="col">Field / semantic ID</th><th scope="col">Kiểu</th><th scope="col">Ràng buộc</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
