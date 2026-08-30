"""D-110 detailed state machine in the approved P-18 visual grammar."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 2000, 980
CARD_W, CARD_H = 340, 170
CARD_BOXES = {
    "state-working": (240, 330, CARD_W, CARD_H),
    "state-quality": (700, 330, CARD_W, CARD_H),
    "state-live": (1160, 330, CARD_W, CARD_H),
    "state-retired": (1160, 620, CARD_W, CARD_H),
}
NODE_IDS = ("state-entry", "state-working", "state-quality", "state-live", "state-retired", "state-closed")
EDGE_IDS = (
    "transition-entry", "transition-submit", "transition-confirm",
    "transition-revise", "transition-retire", "transition-close",
)


def _require(value, message):
    if not value:
        raise ValueError(message)


def _split_label(label):
    parts = [part.strip() for part in label.split(" | ", 1)]
    return parts[0], parts[1] if len(parts) == 2 else ""


def is_detailed_state_machine(plan):
    projection = plan.get("semantic_projection", {})
    return (
        {item.get("id") for item in projection.get("nodes", [])} == set(NODE_IDS)
        and {item.get("id") for item in projection.get("edges", [])} == set(EDGE_IDS)
    )


def layout_state_machine(plan):
    projection = plan["semantic_projection"]
    nodes = {item["id"]: item for item in projection["nodes"]}
    edges = {item["id"]: item for item in projection["edges"]}
    _require(set(nodes) == set(NODE_IDS), "D-110 state inventory mismatch")
    _require(set(edges) == set(EDGE_IDS), "D-110 transition inventory mismatch")
    _require(nodes["state-entry"]["role"] == "initial" and nodes["state-closed"]["role"] == "terminal", "D-110 endpoint roles mismatch")
    _require(all(nodes[item]["role"] == "state" for item in CARD_BOXES), "D-110 stable-state role mismatch")
    expected = {
        "transition-entry": ("state-entry", "state-working"),
        "transition-submit": ("state-working", "state-quality"),
        "transition-confirm": ("state-quality", "state-live"),
        "transition-revise": ("state-quality", "state-working"),
        "transition-retire": ("state-live", "state-retired"),
        "transition-close": ("state-retired", "state-closed"),
    }
    for edge_id, endpoints in expected.items():
        edge = edges[edge_id]
        _require((edge["source"], edge["target"]) == endpoints and edge["kind"] == "transition" and edge["directed"], f"D-110 transition mismatch: {edge_id}")
    layout = {
        "width": WIDTH,
        "height": HEIGHT,
        "nodes": nodes,
        "edges": edges,
        "card_boxes": CARD_BOXES,
        "initial": (110, 415),
        "terminal": (1330, 900),
    }
    validate_state_machine_layout(layout)
    return layout


def validate_state_machine_layout(layout):
    boxes = list(layout["card_boxes"].values())
    for x, y, width, height in boxes:
        _require(180 < x and x + width < 1800 and 120 < y and y + height < 850, "D-110 state card outside content bounds")
    for index, (ax, ay, aw, ah) in enumerate(boxes):
        for bx, by, bw, bh in boxes[index + 1:]:
            _require(ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay, "D-110 state card overlap")
    _require(CARD_BOXES["state-quality"][1] == CARD_BOXES["state-working"][1] == CARD_BOXES["state-live"][1], "D-110 primary state rail must align")
    _require(CARD_BOXES["state-live"][0] + CARD_W / 2 == CARD_BOXES["state-retired"][0] + CARD_W / 2 == layout["terminal"][0], "D-110 vertical lifecycle centers must align")


def state_machine_css(tokens):
    return '''
.stmc-state{fill:var(--surface);stroke:var(--connector);stroke-width:1.15}.stmc-state.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.45}.stmc-state.retired{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.05}
.stmc-badge{fill:var(--surface-alt);stroke:var(--border);stroke-width:.9}.stmc-badge.focal{fill:color-mix(in srgb,var(--accent-soft) 64%,var(--surface));stroke:var(--accent)}.stmc-badge-text{font:700 10px Menlo,Monaco,monospace;letter-spacing:1.4px;fill:var(--muted)}.stmc-badge-text.focal{fill:var(--accent-text)}
.stmc-title{font:650 21px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.stmc-subtitle{font:600 13px Menlo,Monaco,monospace;fill:var(--muted)}.stmc-subtitle.focal{fill:var(--accent-text)}
.stmc-transition{fill:none;stroke:var(--connector);stroke-width:1.2;stroke-linecap:round;stroke-linejoin:round}.stmc-transition.accent{stroke:var(--accent);stroke-width:1.45}.stmc-return{stroke-dasharray:9 8}.stmc-endpoint{fill:var(--text);stroke:none}.stmc-terminal-ring{fill:none;stroke:var(--connector);stroke-width:1.5}.stmc-terminal-core{fill:var(--connector);stroke:none}
.stmc-action-bg{fill:var(--canvas)}.stmc-action{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.5px;fill:var(--muted)}.stmc-action.accent{fill:var(--accent-text)}.stmc-note{font:600 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}
.stmc-legend-rule{stroke:var(--grid);stroke-width:1}.stmc-legend-title{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}.stmc-legend-text{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.stmc-details{overflow-x:auto}.stmc-details table{min-width:980px}
'''


def _card(node_id, node, x, y, css=""):
    title, subtitle = _split_label(node["label"])
    focal = node_id == "state-live"
    badge_class = "stmc-badge focal" if focal else "stmc-badge"
    badge_text_class = "stmc-badge-text focal" if focal else "stmc-badge-text"
    subtitle_class = "stmc-subtitle focal" if focal else "stmc-subtitle"
    state_class = "stmc-state" + (" focal" if focal else " retired" if node_id == "state-retired" else "")
    return (
        f'<g data-state-machine-node="{node_id}" data-state-code="{escape(str(node.get("state", "")))}">'
        f'<rect class="{state_class}" x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="14"/>'
        f'<rect class="{badge_class}" x="{x+18}" y="{y+16}" width="92" height="26" rx="5"/>'
        f'<text class="{badge_text_class}" x="{x+64}" y="{y+34}" text-anchor="middle">TRẠNG THÁI</text>'
        f'<text class="stmc-title" x="{x+CARD_W/2}" y="{y+94}" text-anchor="middle">{escape(title)}</text>'
        f'<text class="{subtitle_class}" x="{x+CARD_W/2}" y="{y+126}" text-anchor="middle">{escape(subtitle)}</text></g>'
    )


def _action(x, y, width, label, focal=False):
    css = "stmc-action accent" if focal else "stmc-action"
    return f'<rect class="stmc-action-bg" x="{x-width/2}" y="{y-18}" width="{width}" height="25" rx="4"/><text class="{css}" x="{x}" y="{y}" text-anchor="middle">{escape(label)}</text>'


def render_state_machine(plan):
    layout = layout_state_machine(plan)
    nodes, edges = layout["nodes"], layout["edges"]
    parts = [
        '<g data-state-machine-contract="D-110-detailed-lifecycle" data-attachment-policy="D-105-centered-and-even" data-route-priority="straight-first-rounded-orthogonal-exception">',
        '<defs><marker id="stmc-arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker></defs>',
    ]
    for node_id, box in CARD_BOXES.items():
        parts.append(_card(node_id, nodes[node_id], box[0], box[1]))
    parts.extend([
        '<circle class="stmc-endpoint" data-state-machine-node="state-entry" cx="110" cy="415" r="14"/>',
        '<circle class="stmc-terminal-ring" data-state-machine-node="state-closed" cx="1330" cy="900" r="24"/><circle class="stmc-terminal-core" cx="1330" cy="900" r="15"/>',
        '<line class="stmc-transition" data-transition-id="transition-entry" data-route-kind="straight" data-source-anchor="center" data-target-anchor="center-left" x1="124" y1="415" x2="240" y2="415" marker-end="url(#arrow)"/>',
        '<line class="stmc-transition" data-transition-id="transition-submit" data-route-kind="straight" data-source-anchor="center-right" data-target-anchor="center-left" x1="580" y1="415" x2="700" y2="415" marker-end="url(#arrow)"/>',
        '<line class="stmc-transition accent" data-transition-id="transition-confirm" data-route-kind="straight" data-source-anchor="center-right" data-target-anchor="center-left" x1="1040" y1="415" x2="1160" y2="415" marker-end="url(#stmc-arrow-accent)"/>',
        '<line class="stmc-transition" data-transition-id="transition-retire" data-route-kind="straight" data-source-anchor="center-bottom" data-target-anchor="center-top" x1="1330" y1="500" x2="1330" y2="620" marker-end="url(#arrow)"/>',
        '<line class="stmc-transition" data-transition-id="transition-close" data-route-kind="straight" data-source-anchor="center-bottom" data-target-anchor="center" x1="1330" y1="790" x2="1330" y2="874" marker-end="url(#arrow)"/>',
        '<path class="stmc-transition stmc-return" data-transition-id="transition-revise" data-route-kind="rounded-orthogonal" data-route-exception="return-transition-avoids-forward-lane" data-corner-style="rounded" data-source-anchor="center-top" data-target-anchor="center-top" d="M870 330 L870 212 Q870 192 850 192 L430 192 Q410 192 410 212 L410 330" marker-end="url(#arrow)"/>',
        _action(640, 397, 104, edges["transition-submit"]["label"]),
        _action(1100, 397, 104, edges["transition-confirm"]["label"], True),
        _action(1330, 568, 90, edges["transition-retire"]["label"]),
        _action(1330, 842, 64, edges["transition-close"]["label"]),
        _action(640, 174, 226, edges["transition-revise"]["label"]),
        '<line class="stmc-legend-rule" x1="56" y1="940" x2="1944" y2="940"/><text class="stmc-legend-title" x="56" y="968">CHÚ GIẢI</text><circle class="stmc-endpoint" cx="190" cy="962" r="7"/><text class="stmc-legend-text" x="210" y="967">Điểm bắt đầu</text><rect class="stmc-state focal" x="382" y="952" width="26" height="18" rx="4"/><text class="stmc-legend-text" x="422" y="967">Trạng thái đang hiệu lực</text><line class="stmc-transition stmc-return" x1="714" y1="961" x2="766" y2="961"/><text class="stmc-legend-text" x="782" y="967">Luồng trả lại</text></g>',
    ])
    return "".join(parts)


def validate_state_machine_svg(svg):
    root = ET.fromstring(svg)
    nodes = {item.attrib["data-state-machine-node"] for item in root.findall(".//*[@data-state-machine-node]")}
    transitions = {item.attrib["data-transition-id"]: item for item in root.findall(".//*[@data-transition-id]")}
    _require(nodes == set(NODE_IDS), "D-110 serialized node inventory mismatch")
    _require(set(transitions) == set(EDGE_IDS), "D-110 serialized transition inventory mismatch")
    _require(sum(item.attrib.get("data-route-kind") == "straight" for item in transitions.values()) == 5, "D-110 straight-first route count mismatch")
    returned = transitions["transition-revise"]
    _require(returned.attrib.get("data-route-kind") == "rounded-orthogonal" and returned.attrib.get("data-route-exception") == "return-transition-avoids-forward-lane", "D-110 return-route exception missing")
    _require(all("center" in item.attrib.get("data-source-anchor", "") and "center" in item.attrib.get("data-target-anchor", "") for item in transitions.values()), "D-110 connector attachments must be centered")
    _require(not root.findall(".//*[@class='bridge']"), "D-110 bridge overlays are forbidden")
    return {"states": 4, "initial_markers": 1, "terminal_markers": 1, "straight_transitions": 5, "return_transitions": 1, "centered_attachments": 12}


def state_machine_table(plan):
    layout = layout_state_machine(plan)
    rows = []
    for node_id in ("state-working", "state-quality", "state-live", "state-retired"):
        node = layout["nodes"][node_id]
        title, subtitle = _split_label(node["label"])
        rows.append(("state", node_id, title, subtitle, node.get("state", ""), "focal" if node_id == "state-live" else "default"))
    for edge_id in EDGE_IDS:
        edge = layout["edges"][edge_id]
        rows.append(("transition", edge_id, edge["source"], edge["target"], edge.get("label", ""), edge.get("guard", "")))
    return '<details class="stmc-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Loại</th><th>ID</th><th>Nguồn / nhãn</th><th>Đích / mô tả</th><th>Trạng thái / hành động</th><th>Guard / nhấn</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></details>'
