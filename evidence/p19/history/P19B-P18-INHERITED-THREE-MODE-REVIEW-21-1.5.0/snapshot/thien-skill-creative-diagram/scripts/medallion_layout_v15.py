"""D-097 detailed five-stage medallion lifecycle in the approved P-18 grammar."""

from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH = 2000
HEIGHT = 1020
LANE_ORDER = ("tier-raw", "tier-anonymized", "tier-staging", "tier-aggregated", "tier-archive")
NODE_ORDER = ("dataset-raw", "dataset-anonymized", "dataset-staging", "dataset-aggregated", "dataset-archive")
EDGE_ORDER = ("promotion-mask", "promotion-clean", "promotion-aggregate", "promotion-lifecycle")
ANNOTATION_ORDER = ("path-sql", "path-notebook")
FOCAL_NODE = "dataset-aggregated"
ARCHIVE_NODE = "dataset-archive"
CARD_X = (30, 420, 810, 1200, 1590)
CARD_Y = 170
CARD_WIDTH = 350
CARD_HEIGHT = 650


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_medallion(plan):
    contract = plan.get("semantic_projection", {}).get("containment_contract", {})
    lanes = contract.get("ordered_layers", [])
    return {item.get("id") for item in lanes} == set(LANE_ORDER)


def _stage_material(node):
    parts = [part.strip() for part in node["label"].split(" | ")]
    _require(len(parts) == 7, f'D-097 stage material mismatch: {node["id"]}')
    return {
        "title": parts[0], "storage": parts[1], "tool": parts[2],
        "format": parts[3], "writer": parts[4],
        "examples": (parts[5], parts[6]),
    }


def layout_medallion(plan):
    projection = plan["semantic_projection"]
    contract = projection["containment_contract"]
    lanes = {item["id"]: item for item in contract["ordered_layers"]}
    nodes = {item["id"]: item for item in projection["nodes"]}
    edges = {item["id"]: item for item in projection["edges"]}
    annotations = {item["id"]: item for item in projection["annotations"]}

    _require(set(lanes) == set(LANE_ORDER), "D-097 tier inventory mismatch")
    _require(set(nodes) == set(NODE_ORDER), "D-097 stage inventory mismatch")
    _require(set(edges) == set(EDGE_ORDER), "D-097 promotion inventory mismatch")
    _require(set(annotations) == set(ANNOTATION_ORDER), "D-097 processing-path inventory mismatch")
    _require(sum(item.get("state") == "focal" for item in nodes.values()) == 1, "D-097 requires one focal stage")
    _require(sum(item.get("state") == "archive" for item in nodes.values()) == 1, "D-097 requires one archive stage")

    stages = {}
    for index, (lane_id, node_id, x) in enumerate(zip(LANE_ORDER, NODE_ORDER, CARD_X)):
        lane = lanes[lane_id]
        _require(lane["order"] == index, f"D-097 tier order mismatch: {lane_id}")
        _require(lane["member_ids"] == [node_id], f"D-097 tier ownership mismatch: {lane_id}")
        stages[node_id] = {
            "id": node_id,
            "lane_id": lane_id,
            "tier": lane["label"],
            "state": nodes[node_id].get("state", "default"),
            "box": (x, CARD_Y, CARD_WIDTH, CARD_HEIGHT),
            **_stage_material(nodes[node_id]),
        }

    promotions = []
    for index, edge_id in enumerate(EDGE_ORDER):
        edge = edges[edge_id]
        _require(edge["source"] == NODE_ORDER[index] and edge["target"] == NODE_ORDER[index + 1], f"D-097 promotion sequence mismatch: {edge_id}")
        _require(edge.get("directed") is True and edge.get("kind") == "promotion", f"D-097 promotion semantics mismatch: {edge_id}")
        promotions.append({
            "id": edge_id,
            "source": edge["source"], "target": edge["target"],
            "label": edge.get("label") or edge_id,
            "state": "focal" if edge_id == "promotion-aggregate" else "archive" if edge_id == "promotion-lifecycle" else "default",
        })

    paths = {}
    for annotation_id in ANNOTATION_ORDER:
        annotation = annotations[annotation_id]
        pieces = [piece.strip() for piece in annotation["text"].split(" | ", 1)]
        _require(len(pieces) == 2, f"D-097 processing path material mismatch: {annotation_id}")
        paths[annotation_id] = {
            "id": annotation_id, "kicker": pieces[0], "description": pieces[1],
            "targets": tuple(annotation["target_ids"]),
        }

    result = {
        "width": WIDTH, "height": HEIGHT, "stages": stages,
        "promotions": promotions, "paths": paths,
    }
    validate_medallion_layout(result)
    return result


def validate_medallion_layout(layout):
    boxes = [layout["stages"][node_id]["box"] for node_id in NODE_ORDER]
    _require(all(y == CARD_Y and width == CARD_WIDTH and height == CARD_HEIGHT for _, y, width, height in boxes), "D-097 card geometry mismatch")
    _require(all(boxes[index][0] + CARD_WIDTH < boxes[index + 1][0] for index in range(4)), "D-097 cards must not overlap")
    _require(boxes[0][0] >= 0 and boxes[-1][0] + CARD_WIDTH <= layout["width"], "D-097 cards escape viewBox")
    _require(sum(stage["state"] == "focal" for stage in layout["stages"].values()) == 1, "D-097 focal count mismatch")
    _require(sum(stage["state"] == "archive" for stage in layout["stages"].values()) == 1, "D-097 archive count mismatch")
    _require(len(layout["promotions"]) == 4 and len(layout["paths"]) == 2, "D-097 supporting material count mismatch")


def medallion_css(tokens):
    return '''
.md-transition{fill:none;stroke:var(--connector);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}.md-transition.focal{stroke:var(--accent);stroke-width:3}.md-transition.archive{stroke-dasharray:9 7}
.md-transition-label{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.5px;fill:var(--muted)}.md-transition-label.focal{fill:var(--accent-text)}
.md-card{fill:var(--surface);stroke:var(--connector);stroke-width:2.2}.md-card.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.8}.md-card.archive{fill:var(--surface-alt);stroke:var(--connector);stroke-width:2.2;stroke-dasharray:9 7}
.md-tier{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.4px;fill:var(--muted)}.md-tier.focal{fill:var(--accent-text)}.md-title{font:650 24px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.md-title.focal{fill:var(--accent-text)}
.md-storage{font:600 14px Menlo,Monaco,monospace;fill:var(--muted)}.md-storage.focal{fill:var(--accent-text)}.md-divider{stroke:var(--grid);stroke-width:1.3}.md-field{font:650 16px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.md-value{font:500 14px Menlo,Monaco,monospace;fill:var(--muted)}
.md-example-kicker{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.4px;fill:var(--muted)}.md-example{font:600 14px Menlo,Monaco,monospace;fill:var(--muted)}.md-example.focal{fill:var(--accent-text)}
.md-state-tag{fill:var(--accent);stroke:none}.md-state-tag.archive{fill:var(--connector)}.md-state-tag-text{font:700 10px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--on-accent)}
.md-path-card{fill:color-mix(in srgb,var(--surface) 78%,var(--canvas));stroke:var(--border);stroke-width:1.5}.md-path-tag{fill:var(--surface);stroke:var(--border);stroke-width:1.3}.md-path-kicker{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--muted)}.md-path-title{font:650 17px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.md-path-detail{font:500 13px Menlo,Monaco,monospace;fill:var(--muted)}.md-details{overflow-x:auto}.md-details table{min-width:1040px}
'''


def _marker_defs():
    return (
        '<defs>'
        '<marker id="md-arrow" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--connector)"/></marker>'
        '<marker id="md-arrow-focal" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker>'
        '</defs>'
    )


def render_medallion(plan):
    layout = layout_medallion(plan)
    parts = ['<g data-medallion-contract="D-097-five-stage-lifecycle">', _marker_defs()]

    for index, promotion in enumerate(layout["promotions"]):
        x1 = CARD_X[index] + CARD_WIDTH / 2
        x2 = CARD_X[index + 1] + CARD_WIDTH / 2
        state = promotion["state"]
        css = "md-transition" + (" focal" if state == "focal" else " archive" if state == "archive" else "")
        label_css = "md-transition-label" + (" focal" if state == "focal" else "")
        marker = "md-arrow-focal" if state == "focal" else "md-arrow"
        path = f"M{x1:g} {CARD_Y:g} C{x1:g} 78 {x2:g} 78 {x2:g} {CARD_Y:g}"
        parts.append(
            f'<g data-transition-id="{promotion["id"]}" data-source="{promotion["source"]}" data-target="{promotion["target"]}" data-state="{state}">'
            f'<path class="{css}" d="{path}" marker-end="url(#{marker})"/>'
            f'<text class="{label_css}" x="{(x1+x2)/2:g}" y="54" text-anchor="middle">{escape(promotion["label"])}</text>'
            '</g>'
        )

    for index, node_id in enumerate(NODE_ORDER):
        stage = layout["stages"][node_id]
        x, y, width, height = stage["box"]
        state = stage["state"]
        state_class = " focal" if state == "focal" else " archive" if state == "archive" else ""
        parts.append(
            f'<g data-stage-id="{node_id}" data-tier-id="{stage["lane_id"]}" data-order="{index}" data-state="{state}" data-fields="tool format writer examples">'
            f'<rect class="md-card{state_class}" x="{x}" y="{y}" width="{width}" height="{height}" rx="14"/>'
            f'<text class="md-tier{state_class if state == "focal" else ""}" x="{x+20}" y="{y+28}">{escape(stage["tier"])}</text>'
            f'<text class="md-title{state_class if state == "focal" else ""}" x="{x+width/2:g}" y="{y+68}" text-anchor="middle">{escape(stage["title"])}</text>'
            f'<text class="md-storage{state_class if state == "focal" else ""}" x="{x+width/2:g}" y="{y+112}" text-anchor="middle">{escape(stage["storage"])}</text>'
            f'<line class="md-divider" x1="{x+20}" y1="{y+142}" x2="{x+width-20}" y2="{y+142}"/>'
            f'<text class="md-field" x="{x+28}" y="{y+205}">Công cụ</text>'
            f'<text class="md-value" x="{x+28}" y="{y+234}">{escape(stage["tool"])}</text>'
            f'<text class="md-field" x="{x+28}" y="{y+304}">Định dạng</text>'
            f'<text class="md-value" x="{x+28}" y="{y+333}">{escape(stage["format"])}</text>'
            f'<text class="md-field" x="{x+28}" y="{y+403}">Chủ trì</text>'
            f'<text class="md-value" x="{x+28}" y="{y+432}">{escape(stage["writer"])}</text>'
            f'<text class="md-example-kicker" x="{x+28}" y="{y+525}">VÍ DỤ THƯƠNG MẠI</text>'
            f'<text class="md-example{state_class if state == "focal" else ""}" x="{x+28}" y="{y+560}">{escape(stage["examples"][0])}</text>'
            f'<text class="md-example{state_class if state == "focal" else ""}" x="{x+28}" y="{y+590}">{escape(stage["examples"][1])}</text>'
        )
        if state in ("focal", "archive"):
            tag_text = "TRỌNG TÂM" if state == "focal" else "LƯU TRỮ"
            parts.append(
                f'<rect class="md-state-tag{state_class}" x="{x+width-114}" y="{y+14}" width="94" height="23" rx="4"/>'
                f'<text class="md-state-tag-text" x="{x+width-67}" y="{y+30}" text-anchor="middle">{tag_text}</text>'
            )
        parts.append('</g>')

    path_boxes = {"path-sql": (30, 855, 950, 130), "path-notebook": (1020, 855, 950, 130)}
    for path_id in ANNOTATION_ORDER:
        item = layout["paths"][path_id]
        x, y, width, height = path_boxes[path_id]
        parts.append(
            f'<g data-processing-path-id="{path_id}" data-target-count="{len(item["targets"])}">'
            f'<rect class="md-path-card" x="{x}" y="{y}" width="{width}" height="{height}" rx="13"/>'
            f'<rect class="md-path-tag" x="{x+18}" y="{y+17}" width="150" height="26" rx="4"/>'
            f'<text class="md-path-kicker" x="{x+93}" y="{y+35}" text-anchor="middle">{escape(item["kicker"])}</text>'
            f'<text class="md-path-title" x="{x+190}" y="{y+39}">{"Biến đổi có thể lặp lại" if path_id == "path-sql" else "Khám phá có kiểm soát"}</text>'
            f'<text class="md-path-detail" x="{x+190}" y="{y+78}">{escape(item["description"])}</text>'
            '</g>'
        )
    parts.append('</g>')
    return ''.join(parts)


def validate_medallion_svg(svg):
    root = ET.fromstring(svg)
    contract = root.find('.//*[@data-medallion-contract]')
    _require(contract is not None, "D-097 serialized contract missing")
    stages = {item.attrib["data-stage-id"]: item for item in root.findall('.//*[@data-stage-id]')}
    transitions = {item.attrib["data-transition-id"]: item for item in root.findall('.//*[@data-transition-id]')}
    paths = {item.attrib["data-processing-path-id"]: item for item in root.findall('.//*[@data-processing-path-id]')}
    _require(set(stages) == set(NODE_ORDER), "D-097 serialized stage mismatch")
    _require(set(transitions) == set(EDGE_ORDER), "D-097 serialized transition mismatch")
    _require(set(paths) == set(ANNOTATION_ORDER), "D-097 serialized path mismatch")
    _require([stages[node_id].attrib["data-order"] for node_id in NODE_ORDER] == [str(index) for index in range(5)], "D-097 serialized order mismatch")
    _require(sum(item.attrib["data-state"] == "focal" for item in stages.values()) == 1, "D-097 serialized focal mismatch")
    _require(sum(item.attrib["data-state"] == "archive" for item in stages.values()) == 1, "D-097 serialized archive mismatch")
    _require(all(item.find('.//path') is not None and item.find('.//path').attrib.get("marker-end", "").startswith("url(#md-arrow") for item in transitions.values()), "D-097 promotions must be continuous directed paths")
    _require(all(item.attrib["data-fields"] == "tool format writer examples" for item in stages.values()), "D-097 serialized stage fields mismatch")
    return {"stages": 5, "promotions": 4, "focal_stages": 1, "archive_stages": 1, "processing_paths": 2}


def medallion_table(plan):
    layout = layout_medallion(plan)
    rows = []
    for node_id in NODE_ORDER:
        stage = layout["stages"][node_id]
        rows.append((stage["tier"], node_id, stage["title"], stage["storage"], stage["tool"], stage["format"], stage["writer"], " / ".join(stage["examples"]), stage["state"]))
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows)
    return '<details class="md-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Tầng</th><th>Semantic ID</th><th>Tên</th><th>Kho</th><th>Công cụ</th><th>Định dạng</th><th>Chủ trì</th><th>Ví dụ</th><th>Trạng thái</th></tr></thead><tbody>' + body + '</tbody></table></details>'
