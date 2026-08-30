"""D-111 detailed sequence diagram in the approved P-18 visual grammar."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 2000, 1140
CARD_W, CARD_H, CARD_Y = 300, 116, 100
PARTICIPANT_X = {
    "participant-editor": 300,
    "participant-edge": 760,
    "participant-origin": 1220,
    "participant-metrics": 1680,
}
PARTICIPANT_IDS = tuple(PARTICIPANT_X)
PARTICIPANT_CODES = {
    "participant-editor": "EXT",
    "participant-edge": "EDGE",
    "participant-origin": "GỐC",
    "participant-metrics": "ASY",
}
MESSAGE_IDS = (
    "message-open", "message-origin", "message-render",
    "message-html", "message-cached", "message-view",
)


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_sequence(plan):
    projection = plan.get("semantic_projection", {})
    return (
        {item.get("id") for item in projection.get("nodes", [])} == set(PARTICIPANT_IDS)
        and {item.get("id") for item in projection.get("edges", [])} == set(MESSAGE_IDS)
    )


def layout_sequence(plan):
    projection = plan["semantic_projection"]
    nodes = {item["id"]: item for item in projection["nodes"]}
    edges = {item["id"]: item for item in projection["edges"]}
    _require(set(nodes) == set(PARTICIPANT_IDS), "D-111 participant inventory mismatch")
    _require(set(edges) == set(MESSAGE_IDS), "D-111 message inventory mismatch")
    _require([item["id"] for item in sorted(edges.values(), key=lambda item: item["order"])] == list(MESSAGE_IDS), "D-111 chronological order mismatch")
    expected = {
        "message-open": ("participant-editor", "participant-edge", "request"),
        "message-origin": ("participant-edge", "participant-origin", "request"),
        "message-render": ("participant-origin", "participant-origin", "message"),
        "message-html": ("participant-origin", "participant-edge", "return"),
        "message-cached": ("participant-edge", "participant-editor", "response"),
        "message-view": ("participant-editor", "participant-metrics", "async"),
    }
    for message_id, contract in expected.items():
        edge = edges[message_id]
        _require((edge["source"], edge["target"], edge["kind"]) == contract and edge["directed"], f"D-111 message mismatch: {message_id}")
    cards = {node_id: (x - CARD_W / 2, CARD_Y, CARD_W, CARD_H) for node_id, x in PARTICIPANT_X.items()}
    layout = {
        "width": WIDTH,
        "height": HEIGHT,
        "nodes": nodes,
        "edges": edges,
        "participant_x": PARTICIPANT_X,
        "card_boxes": cards,
        "lifeline": (CARD_Y + CARD_H, 1020),
        "activations": {
            "activation-edge": (752, 340, 16, 450, "participant-edge"),
            "activation-origin": (1212, 450, 16, 270, "participant-origin"),
        },
        "message_y": {
            "message-open": 340,
            "message-origin": 450,
            "message-render": 540,
            "message-html": 705,
            "message-cached": 790,
            "message-view": 920,
        },
    }
    validate_sequence_layout(layout)
    return layout


def validate_sequence_layout(layout):
    xs = list(layout["participant_x"].values())
    _require(xs == sorted(xs) and len(set(xs)) == 4, "D-111 participant order/spacing mismatch")
    _require(xs[1] - xs[0] == xs[2] - xs[1] == xs[3] - xs[2] == 460, "D-111 participant spacing must be even")
    for node_id, (x, y, width, height) in layout["card_boxes"].items():
        _require(x + width / 2 == layout["participant_x"][node_id], f"D-111 card/lifeline center drift: {node_id}")
        _require(40 < x and x + width < WIDTH - 40 and 40 < y and y + height < 260, f"D-111 participant card out of bounds: {node_id}")
    ys = list(layout["message_y"].values())
    _require(ys == sorted(ys) and len(set(ys)) == 6, "D-111 message chronology must be visually monotonic")
    for _, (x, y, width, height, owner) in layout["activations"].items():
        _require(x + width / 2 == layout["participant_x"][owner], f"D-111 activation/lifeline center drift: {owner}")
        _require(layout["lifeline"][0] < y < y + height < layout["lifeline"][1], "D-111 activation outside lifeline")


def sequence_css(tokens):
    return '''
.seq-participant{fill:var(--surface);stroke:var(--connector);stroke-width:1.2}.seq-participant.edge{fill:var(--surface-alt);stroke:var(--border)}.seq-participant.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}.seq-participant.async{fill:var(--surface);stroke:var(--border);stroke-width:1.1;stroke-dasharray:8 7}
.seq-badge{fill:var(--surface-alt);stroke:var(--border);stroke-width:.9}.seq-badge.focal{fill:color-mix(in srgb,var(--accent-soft) 64%,var(--surface));stroke:var(--accent)}.seq-badge-text{font:700 10px Menlo,Monaco,monospace;letter-spacing:1.4px;fill:var(--muted)}.seq-badge-text.focal{fill:var(--accent-text)}
.seq-title{font:650 20px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.seq-detail{font:600 13px Menlo,Monaco,monospace;fill:var(--muted)}.seq-lifeline{fill:none;stroke:var(--border);stroke-width:1;stroke-dasharray:7 7}.seq-activation{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1}
.seq-message{fill:none;stroke:var(--connector);stroke-width:1.25;stroke-linecap:round;stroke-linejoin:round}.seq-message.request{stroke:var(--series-1);stroke-width:1.45}.seq-message.return,.seq-message.async{stroke-dasharray:10 8}.seq-message.primary{stroke:var(--accent);stroke-width:1.65}.seq-message.self{stroke-width:1.2}
.seq-label-bg{fill:var(--canvas)}.seq-label{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.35px;fill:var(--muted)}.seq-label.request{fill:var(--series-1)}.seq-label.primary{fill:var(--accent-text)}
.seq-legend-rule{stroke:var(--grid);stroke-width:1}.seq-legend-title{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}.seq-legend-text{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.seq-details{overflow-x:auto}.seq-details table{min-width:1080px}
'''


def _participant(node_id, node, cx):
    x = cx - CARD_W / 2
    title, detail = [part.strip() for part in str(node["label"]).split(" | ", 1)]
    kind = node.get("state", "")
    card_class = "seq-participant" + (" focal" if kind in {"origin", "focal"} else f" {kind}" if kind in {"edge", "async"} else "")
    badge_class = "seq-badge focal" if kind in {"origin", "focal"} else "seq-badge"
    badge_text = "seq-badge-text focal" if kind in {"origin", "focal"} else "seq-badge-text"
    return (
        f'<g data-sequence-participant="{node_id}" data-participant-kind="{escape(str(kind))}" data-lifeline-x="{cx}">'
        f'<rect class="{card_class}" x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="14"/>'
        f'<rect class="{badge_class}" x="{x+18}" y="{CARD_Y+16}" width="68" height="26" rx="5"/>'
        f'<text class="{badge_text}" x="{x+52}" y="{CARD_Y+34}" text-anchor="middle">{escape(PARTICIPANT_CODES[node_id])}</text>'
        f'<text class="seq-title" x="{cx}" y="{CARD_Y+70}" text-anchor="middle">{escape(title)}</text>'
        f'<text class="seq-detail" x="{cx}" y="{CARD_Y+96}" text-anchor="middle">{escape(detail)}</text></g>'
    )


def _message_label(cx, y, width, label, css=""):
    class_name = "seq-label" + (f" {css}" if css else "")
    return f'<rect class="seq-label-bg" x="{cx-width/2}" y="{y-21}" width="{width}" height="25" rx="4"/><text class="{class_name}" x="{cx}" y="{y-3}" text-anchor="middle">{escape(label)}</text>'


def render_sequence(plan):
    layout = layout_sequence(plan)
    nodes, edges = layout["nodes"], layout["edges"]
    parts = [
        '<g data-sequence-contract="D-111-detailed-interaction" data-attachment-policy="D-105-centered-and-even" data-route-priority="straight-first-rounded-self-call-exception">',
        '<defs><marker id="seq-arrow-request" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--series-1)"/></marker><marker id="seq-arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker></defs>',
    ]
    for node_id in PARTICIPANT_IDS:
        parts.append(_participant(node_id, nodes[node_id], PARTICIPANT_X[node_id]))
    for node_id, cx in PARTICIPANT_X.items():
        parts.append(f'<line class="seq-lifeline" data-lifeline-owner="{node_id}" x1="{cx}" y1="216" x2="{cx}" y2="1020"/>')
    for activation_id, (x, y, width, height, owner) in layout["activations"].items():
        parts.append(f'<rect class="seq-activation" data-activation-id="{activation_id}" data-activation-owner="{owner}" x="{x}" y="{y}" width="{width}" height="{height}"/>')
    parts.extend([
        '<line class="seq-message request" data-sequence-message="message-open" data-route-kind="straight" data-order="0" data-source-anchor="lifeline-axis" data-target-anchor="activation-left" x1="300" y1="340" x2="752" y2="340" marker-end="url(#seq-arrow-request)"/>',
        '<line class="seq-message" data-sequence-message="message-origin" data-route-kind="straight" data-order="1" data-source-anchor="activation-right" data-target-anchor="activation-left" x1="768" y1="450" x2="1212" y2="450" marker-end="url(#arrow)"/>',
        '<path class="seq-message self" data-sequence-message="message-render" data-route-kind="rounded-orthogonal" data-route-exception="self-call-requires-return-to-same-lifeline" data-corner-style="rounded" data-order="2" data-source-anchor="activation-right" data-target-anchor="activation-right" d="M1228 540 L1370 540 Q1390 540 1390 560 L1390 595 Q1390 615 1370 615 L1228 615" marker-end="url(#arrow)"/>',
        '<line class="seq-message return" data-sequence-message="message-html" data-route-kind="straight" data-order="3" data-source-anchor="activation-left" data-target-anchor="activation-right" x1="1212" y1="705" x2="768" y2="705" marker-end="url(#arrow)"/>',
        '<line class="seq-message primary" data-sequence-message="message-cached" data-route-kind="straight" data-order="4" data-source-anchor="activation-left" data-target-anchor="lifeline-axis" x1="752" y1="790" x2="300" y2="790" marker-end="url(#seq-arrow-accent)"/>',
        '<line class="seq-message async" data-sequence-message="message-view" data-route-kind="straight" data-order="5" data-source-anchor="lifeline-axis" data-target-anchor="lifeline-axis" x1="300" y1="920" x2="1680" y2="920" marker-end="url(#arrow)"/>',
        _message_label(526, 340, 250, edges["message-open"]["label"], "request"),
        _message_label(990, 450, 286, edges["message-origin"]["label"]),
        _message_label(1450, 585, 160, edges["message-render"]["label"]),
        _message_label(990, 705, 220, edges["message-html"]["label"]),
        _message_label(526, 790, 282, edges["message-cached"]["label"], "primary"),
        _message_label(990, 920, 260, edges["message-view"]["label"]),
        '<line class="seq-legend-rule" x1="56" y1="1068" x2="1944" y2="1068"/><text class="seq-legend-title" x="56" y="1104">CHÚ GIẢI</text>',
        '<rect class="seq-participant focal" x="170" y="1086" width="28" height="20" rx="4"/><text class="seq-legend-text" x="212" y="1103">Participant trọng tâm</text>',
        '<rect class="seq-activation" x="440" y="1082" width="10" height="28"/><text class="seq-legend-text" x="468" y="1103">Activation</text>',
        '<line class="seq-message request" x1="650" y1="1098" x2="704" y2="1098" marker-end="url(#seq-arrow-request)"/><text class="seq-legend-text" x="722" y="1103">Request</text>',
        '<line class="seq-message return" x1="900" y1="1098" x2="954" y2="1098" marker-end="url(#arrow)"/><text class="seq-legend-text" x="972" y="1103">Return / async</text>',
        '<line class="seq-message primary" x1="1240" y1="1098" x2="1294" y2="1098" marker-end="url(#seq-arrow-accent)"/><text class="seq-legend-text" x="1312" y="1103">Phản hồi chính</text></g>',
    ])
    return "".join(parts)


def validate_sequence_svg(svg):
    root = ET.fromstring(svg)
    participants = {item.attrib["data-sequence-participant"]: item for item in root.findall(".//*[@data-sequence-participant]")}
    lifelines = {item.attrib["data-lifeline-owner"]: item for item in root.findall(".//*[@data-lifeline-owner]")}
    activations = root.findall(".//*[@data-activation-id]")
    messages = {item.attrib["data-sequence-message"]: item for item in root.findall(".//*[@data-sequence-message]")}
    _require(set(participants) == set(PARTICIPANT_IDS), "D-111 serialized participant inventory mismatch")
    _require(set(lifelines) == set(PARTICIPANT_IDS), "D-111 serialized lifeline inventory mismatch")
    _require(len(activations) == 2, "D-111 activation inventory mismatch")
    _require(set(messages) == set(MESSAGE_IDS), "D-111 serialized message inventory mismatch")
    _require([item.attrib["data-sequence-message"] for item in sorted(messages.values(), key=lambda item: int(item.attrib["data-order"]))] == list(MESSAGE_IDS), "D-111 serialized chronology mismatch")
    _require(sum(item.attrib.get("data-route-kind") == "straight" for item in messages.values()) == 5, "D-111 straight-first message count mismatch")
    self_call = messages["message-render"]
    _require(self_call.attrib.get("data-route-kind") == "rounded-orthogonal" and self_call.attrib.get("data-route-exception") == "self-call-requires-return-to-same-lifeline", "D-111 self-call exception missing")
    _require(all(float(participants[node_id].attrib["data-lifeline-x"]) == float(lifelines[node_id].attrib["x1"]) == float(lifelines[node_id].attrib["x2"]) for node_id in PARTICIPANT_IDS), "D-111 card/lifeline center alignment drift")
    _require(not root.findall(".//*[@class='bridge']"), "D-111 bridge overlays are forbidden")
    return {
        "participants": 4,
        "lifelines": 4,
        "activations": 2,
        "messages": 6,
        "straight_messages": 5,
        "self_messages": 1,
        "dashed_messages": 2,
        "focal_messages": 1,
        "centered_card_lifelines": 4,
    }


def sequence_table(plan):
    layout = layout_sequence(plan)
    rows = []
    for node_id in PARTICIPANT_IDS:
        node = layout["nodes"][node_id]
        title, detail = [part.strip() for part in str(node["label"]).split(" | ", 1)]
        rows.append(("participant", node_id, title, detail, node.get("state", ""), PARTICIPANT_CODES[node_id]))
    for message_id in MESSAGE_IDS:
        edge = layout["edges"][message_id]
        rows.append(("message", message_id, edge["source"], edge["target"], edge["kind"], f'{edge["order"]}: {edge.get("label", "")}'))
    return '<details class="seq-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Loại</th><th>ID</th><th>Nguồn / tên</th><th>Đích / mô tả</th><th>Vai trò / kiểu</th><th>Mã / thứ tự và nhãn</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></details>'
