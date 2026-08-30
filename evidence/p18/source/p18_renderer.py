"""Original deterministic SVG/HTML renderer for the bounded P-18 pilot set."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Iterable, Mapping


SOURCE_DIR = Path(__file__).resolve().parent
REPO_ROOT = SOURCE_DIR.parents[2]
VISUAL_SYSTEM_PATH = REPO_ROOT / "thien-skill-creative-diagram" / "references" / "visual-system.json"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from p18_cases import CASE_META, MODES, build_case  # noqa: E402
from p18_visual_foundation import (  # noqa: E402
    BODY_TRANSFORM,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    INTENT_BY_CASE,
    PROFILE_BY_CASE,
    semantic_field_marker,
    type_legend,
    wrap_text,
)


WIDTH = CANVAS_WIDTH
HEIGHT = CANVAS_HEIGHT
PLOT_TOP = 166
PLOT_BOTTOM = 770
SVG_NS = "http://www.w3.org/2000/svg"


@dataclass(frozen=True)
class RenderedSpecimen:
    case_id: str
    mode: str
    filename: str
    svg: str
    html: str
    source_hash: str
    source_bundle_hash: str
    measurements: Mapping[str, Any]


def _system() -> dict[str, Any]:
    return json.loads(VISUAL_SYSTEM_PATH.read_text(encoding="utf-8"))


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def _fmt(value: float | int) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _text(x: float, y: float, value: str, css: str, *, anchor: str = "start", extra: str = "") -> str:
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{css}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'


def _wrapped(x: float, y: float, value: str, css: str, *, width_chars: int = 24, line_height: int = 23, anchor: str = "start") -> str:
    font_px = {"section": 22, "label": 20, "small": 16, "tiny": 15}.get(css, 16)
    weight = 720 if css in {"section", "label"} else 560
    # Existing renderer calls express the box as an approximate character
    # budget. Convert it to a physical width, then reserve lines by measured
    # glyph classes instead of splitting on character count.
    max_width = max(72.0, width_chars * font_px * 0.58)
    lines = wrap_text(value, max_width, font_px, weight=weight)
    tspans = "".join(f'<tspan x="{x:.2f}" dy="{0 if index == 0 else line_height}">{escape(line)}</tspan>' for index, line in enumerate(lines))
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{css}" text-anchor="{anchor}">{tspans}</text>'


def _theme(mode: str) -> dict[str, str]:
    tokens = _system()["modes"][mode]
    return {
        **tokens,
        "ink": tokens["text"],
        "quiet": tokens["muted"],
        "panel": tokens["surface"],
        "panel_alt": tokens["surface_alt"],
        "data_1": tokens["series_1"],
        "data_2": tokens["series_2"],
        "data_3": tokens["success"],
        "negative": tokens["danger"],
    }


def _defs(prefix: str, t: Mapping[str, str]) -> str:
    return f"""
    <defs>
      <marker id="{prefix}-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L9,4.5 L0,9 Z" fill="{t['connector']}"/></marker>
      <marker id="{prefix}-arrow-accent" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L9,4.5 L0,9 Z" fill="{t['data_1']}"/></marker>
      <pattern id="{prefix}-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="9" height="9" fill="{t['panel_alt']}"/><line x1="0" y1="0" x2="0" y2="9" stroke="{t['data_2']}" stroke-width="3" opacity=".55"/></pattern>
      <pattern id="{prefix}-dots" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.35" fill="{t['grid']}" opacity=".34"/></pattern>
    </defs>"""


def _svg_style(t: Mapping[str, str], prefix: str) -> str:
    font = _system()["primitives"]["font_stack"]
    return f"""
    text {{ font-family: {font}; fill: {t['ink']}; }}
    .case {{ font-family: {_system()['primitives']['mono_stack']}; font-size: 15px; font-weight: 760; letter-spacing: 1.6px; fill: {t['accent']}; }}
    .title {{ font-size: 44px; font-weight: 760; letter-spacing: -1px; }}
    .reading {{ font-size: 18px; font-weight: 500; fill: {t['quiet']}; }}
    .section {{ font-size: 22px; font-weight: 750; }}
    .label {{ font-size: 20px; font-weight: 700; }}
    .small {{ font-size: 16px; font-weight: 560; fill: {t['quiet']}; }}
    .tiny {{ font-family: {_system()['primitives']['mono_stack']}; font-size: 15px; font-weight: 620; fill: {t['quiet']}; letter-spacing: .2px; }}
    .number {{ font-family: {_system()['primitives']['mono_stack']}; font-size: 16px; font-weight: 760; font-variant-numeric: tabular-nums; }}
    .legend-heading {{ font-family: {_system()['primitives']['mono_stack']}; font-size: 15px; font-weight: 760; letter-spacing: 2.3px; fill: {t['quiet']}; }}
    .legend-label {{ font-size: 16px; font-weight: 620; fill: {t['quiet']}; }}
    .legend-insight {{ font-size: 16px; font-style: italic; font-weight: 540; fill: {t['quiet']}; }}
    .axis {{ stroke: {t['border']}; stroke-width: 1.5; }}
    .grid {{ stroke: {t['grid']}; stroke-width: 1; }}
    .route {{ fill: none; stroke: {t['connector']}; stroke-width: 2.5; stroke-linejoin: round; stroke-linecap: round; marker-end: url(#{prefix}-arrow); }}
    .route-accent {{ fill: none; stroke: {t['data_1']}; stroke-width: 2.5; stroke-linejoin: round; stroke-linecap: round; marker-end: url(#{prefix}-arrow-accent); }}
    .panel {{ fill: {t['panel']}; stroke: {t['border']}; stroke-width: 1.5; }}
    .panel-alt {{ fill: {t['panel_alt']}; stroke: {t['border']}; stroke-width: 1.2; }}
    .node {{ fill: {t['panel']}; stroke: {t['connector']}; stroke-width: 1.8; }}
    .node-accent {{ fill: {t['panel']}; stroke: {t['data_1']}; stroke-width: 2.4; }}
    """


def _header(case_id: str, mode: str, t: Mapping[str, str]) -> str:
    meta = CASE_META[case_id]
    return (
        f'<rect x="32" y="28" width="1376" height="112" rx="22" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1.5"/>'
        f'<rect x="32" y="28" width="9" height="112" rx="4.5" fill="{t["accent"]}"/>'
        + _text(64, 61, f'{case_id}  •  {meta["type"]}  •  {meta["capability"]}  •  {mode}', "case")
        + _text(64, 101, meta["title"], "title")
        + _text(1376, 101, meta["reading"], "reading", anchor="end")
    )


def _audit_rail(case_id: str, t: Mapping[str, str]) -> str:
    meta = CASE_META[case_id]
    return (
        f'<rect x="32" y="802" width="1376" height="66" rx="18" fill="{t["panel"]}" stroke="{t["border"]}" stroke-width="1.4"/>'
        + _text(58, 830, "EVIDENCE RAIL", "tiny")
        + _text(58, 852, "Exact semantics • direct labels • visible ledger • static complete frame", "small")
        + _text(1380, 842, f'{meta["capability"]} · motion=none · 1440×900', "small", anchor="end")
    )


def _architecture(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    zones = {
        "zone-public": (48, 198, 250, 520),
        "zone-app": (322, 198, 620, 520),
        "zone-data": (966, 198, 426, 244),
        "zone-audit": (966, 466, 426, 252),
    }
    node_rects = {
        "arch-applicant": (88, 405, 170, 82),
        "arch-api": (366, 405, 170, 82),
        "arch-approval": (650, 405, 206, 82),
        "arch-identity": (650, 254, 206, 76),
        "arch-notify": (650, 575, 206, 76),
        "arch-records": (1082, 284, 194, 82),
        "arch-audit": (1082, 550, 194, 82),
    }
    group_by_id = {group["id"]: group for group in ir["groups"]}
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    parts: list[str] = []
    for zone_id, (x, y, w, h) in zones.items():
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{t["panel_alt"]}" stroke="{t["border"]}" stroke-width="1.6" stroke-dasharray="7 6"/>')
        parts.append(_text(x + 20, y + 31, group_by_id[zone_id]["label"].upper(), "tiny"))
    route_specs = [
        ("arch-submit", "M258 446 H366"),
        ("arch-route", "M536 446 H650"),
        ("arch-verify", "M742 405 V330"),
        ("arch-verified", "M778 330 V405"),
        ("arch-store", "M856 431 H940 V325 H1082"),
        ("arch-log", "M856 459 H930 V591 H1082"),
        ("arch-notification", "M753 487 V575"),
    ]
    edge_by_id = {edge["id"]: edge for edge in ir["edges"]}
    for edge_id, d in route_specs:
        edge = edge_by_id[edge_id]
        parts.append(f'<path id="{prefix}-{edge_id}" class="route" d="{d}" data-edge-id="{edge_id}" data-source="{edge["source"]}" data-target="{edge["target"]}"/>')
    for node_id, (x, y, w, h) in node_rects.items():
        node = node_by_id[node_id]
        focus_class = "node-accent" if node_id == "arch-approval" else "node"
        parts.append(f'<g id="{prefix}-{node_id}" data-node-id="{node_id}"><rect class="{focus_class}" x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/><rect x="{x}" y="{y}" width="7" height="{h}" rx="3.5" fill="{t["accent"]}"/>{_wrapped(x + 18, y + 34, node["label"], "label", width_chars=22)}</g>')
    parts.append(_text(70, 752, "Bốn vùng tin cậy; không có cạnh bypass.", "small"))
    return "".join(parts), {"nodes": node_rects, "edge_count": len(route_specs), "zone_count": len(zones)}


def _swimlane(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    x0, lane_w, lane_y, lane_h = 146, 203, 240, 500
    lanes = sorted(ir["lanes"], key=lambda value: value["order"])
    parts: list[str] = []
    for index, lane_value in enumerate(lanes):
        x = x0 + index * lane_w
        fill = t["panel"] if index % 2 == 0 else t["panel_alt"]
        parts.append(f'<rect x="{x}" y="{lane_y}" width="{lane_w}" height="{lane_h}" fill="{fill}" stroke="{t["border"]}" stroke-width="1"/>')
        parts.append(_text(x + lane_w / 2, 270, lane_value["label"], "label", anchor="middle"))
    parts.append(f'<rect x="{x0 + lane_w}" y="188" width="{2 * lane_w}" height="38" rx="12" fill="{t["document_fill"]}" stroke="{t["document_stroke"]}"/><rect x="{x0 + 3 * lane_w}" y="188" width="{2 * lane_w}" height="38" rx="12" fill="{t["file_fill"]}" stroke="{t["file_stroke"]}"/>')
    parts.append(_text(x0 + 2 * lane_w, 213, "THỦ QUỸ", "tiny", anchor="middle"))
    parts.append(_text(x0 + 4 * lane_w, 213, "KẾ TOÁN TRƯỞNG", "tiny", anchor="middle"))
    positions = {
        "sw-check-customer": (x0 + 14, 308), "sw-check-mail": (x0 + lane_w + 14, 308),
        "sw-check-cash": (x0 + 2 * lane_w + 14, 308), "sw-check-bank": (x0 + 5 * lane_w + 14, 308),
        "sw-notice-customer": (x0 + 14, 445), "sw-notice-mail": (x0 + lane_w + 14, 445),
        "sw-notice-ar": (x0 + 3 * lane_w + 14, 445), "sw-listing-mail": (x0 + lane_w + 14, 595),
        "sw-listing-cash": (x0 + 2 * lane_w + 14, 595), "sw-listing-ledger": (x0 + 4 * lane_w + 14, 595),
        "sw-file-ar": (x0 + 3 * lane_w + 14, 675), "sw-file-ledger": (x0 + 4 * lane_w + 14, 675),
    }
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    w, h = 175, 54
    for node_id, (x, y) in positions.items():
        node = node_by_id[node_id]
        role_fill = {"money": t["money_fill"], "document": t["document_fill"], "listing": t["listing_fill"], "file": t["file_fill"]}[node["role"]]
        role_stroke = {"money": t["money_stroke"], "document": t["document_stroke"], "listing": t["listing_stroke"], "file": t["file_stroke"]}[node["role"]]
        parts.append(f'<rect id="{prefix}-{node_id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{role_fill}" stroke="{role_stroke}" stroke-width="1.8" data-node-id="{node_id}"/>')
        parts.append(_wrapped(x + w / 2, y + 23, node["label"], "small", width_chars=20, line_height=17, anchor="middle"))
    edge_by_id = {edge["id"]: edge for edge in ir["edges"]}
    routes = {
        "sw-e01": (321, 335, 349, 335), "sw-e02": (524, 335, 552, 335), "sw-e03": (727, 335, 1161, 335),
        "sw-e04": (321, 472, 349, 472), "sw-e05": (524, 472, 755, 472), "sw-e06": (842, 499, 842, 675),
        "sw-e07": (524, 622, 552, 622), "sw-e08": (727, 622, 958, 622), "sw-e09": (1045, 649, 1045, 675),
        "sw-e10": (930, 702, 958, 702),
    }
    label_positions = {
        "sw-e01": (335, 292),
        "sw-e02": (538, 292),
        "sw-e04": (335, 425),
        "sw-e07": (538, 575),
        "sw-e08": (914, 618),
        "sw-e09": (1100, 660),
        "sw-e10": (944, 652),
    }
    for edge_id, (x1, y1, x2, y2) in routes.items():
        edge = edge_by_id[edge_id]
        endpoint_attrs = f'data-edge-id="{edge_id}" data-source="{edge["source"]}" data-target="{edge["target"]}"'
        if edge_id == "sw-e08":
            # e08 crosses the vertical e06 handoff. The explicit bridge keeps
            # both route identities readable instead of drawing a false node.
            d = f'M{x1} {y1} H830 C836 {y1} 836 {y1-15} 842 {y1-15} C848 {y1-15} 848 {y1} 854 {y1} H{x2}'
            parts.append(f'<path id="{prefix}-{edge_id}" class="route" d="{d}" {endpoint_attrs} data-bridge-hop="true"/>')
        else:
            parts.append(f'<line id="{prefix}-{edge_id}" class="route" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {endpoint_attrs}/>')
        label_x, label_y = label_positions.get(edge_id, ((x1+x2)/2, (y1+y2)/2))
        parts.append(f'<rect x="{label_x-22:.1f}" y="{label_y-16:.1f}" width="44" height="28" rx="9" fill="{t["panel"]}" stroke="{t["border"]}" data-label-mask="true" data-clearance="8"/>')
        parts.append(_text(label_x, label_y+4, edge["label"], "tiny", anchor="middle"))
    parts.append(_text(154, 775, "Séc", "tiny")); parts.append(_text(220, 775, "Chứng từ", "tiny")); parts.append(_text(315, 775, "Bảng kê", "tiny")); parts.append(_text(395, 775, "Tệp lưu", "tiny"))
    return "".join(parts), {"nodes": positions, "edge_count": len(routes), "lane_count": len(lanes)}


def _sankey(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    node_pos = {
        "water-intake": (86, 375), "water-pretreat": (392, 330), "water-reject": (392, 625),
        "water-filter": (700, 310), "water-wash": (700, 625), "water-distribution": (1050, 278), "water-sludge": (1050, 610),
    }
    centers = {node_id: (x + 95, y + 34) for node_id, (x, y) in node_pos.items()}
    paths = {
        "water-e01": (centers["water-intake"], centers["water-pretreat"]),
        "water-e02": ((centers["water-intake"][0], centers["water-intake"][1] + 35), centers["water-reject"]),
        "water-e03": (centers["water-pretreat"], centers["water-filter"]),
        "water-e04": ((centers["water-pretreat"][0], centers["water-pretreat"][1] + 35), centers["water-wash"]),
        "water-e05": (centers["water-filter"], centers["water-distribution"]),
        "water-e06": ((centers["water-filter"][0], centers["water-filter"][1] + 35), centers["water-sludge"]),
    }
    colors = [t["data_1"], t["negative"], t["data_3"], t["data_2"], t["data_1"], t["negative"]]
    parts: list[str] = []
    measurements: dict[str, Any] = {"bands": {}}
    edge_by_id = {edge["id"]: edge for edge in ir["edges"]}
    for index, (edge_id, (start, end)) in enumerate(paths.items()):
        edge = edge_by_id[edge_id]
        width = float(edge["amount"]) * 0.64
        mx = (start[0] + end[0]) / 2
        d = f'M{start[0]:.1f},{start[1]:.1f} C{mx:.1f},{start[1]:.1f} {mx:.1f},{end[1]:.1f} {end[0]:.1f},{end[1]:.1f}'
        parts.append(f'<path id="{prefix}-{edge_id}" d="{d}" fill="none" stroke="{colors[index]}" stroke-width="{width:.2f}" stroke-opacity=".42" stroke-linecap="butt" data-edge-id="{edge_id}" data-source="{edge["source"]}" data-target="{edge["target"]}" data-amount="{edge["amount"]}" data-unit="ML/day" data-band-width="{width:.2f}"/>')
        label_x, label_y = mx, (start[1] + end[1]) / 2
        parts.append(f'<rect x="{label_x-38:.1f}" y="{label_y-17:.1f}" width="76" height="32" rx="9" fill="{t["panel"]}" stroke="{t["border"]}" data-label-mask="true" data-clearance="8"/>')
        parts.append(_text(label_x, label_y + 5, f'{edge["amount"]} ML/d', "tiny", anchor="middle"))
        measurements["bands"][edge_id] = {"amount": edge["amount"], "width": round(width, 2)}
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    for node_id, (x, y) in node_pos.items():
        parts.append(f'<rect id="{prefix}-{node_id}" x="{x}" y="{y}" width="190" height="68" rx="16" class="node" data-node-id="{node_id}"/>')
        parts.append(_text(x + 95, y + 31, node_by_id[node_id]["label"], "label", anchor="middle"))
        flow_total = sum(edge["amount"] for edge in ir["edges"] if edge["source"] == node_id) or sum(edge["amount"] for edge in ir["edges"] if edge["target"] == node_id)
        parts.append(_text(x + 95, y + 52, f'{flow_total} ML/day', "tiny", anchor="middle"))
    parts.append(_text(76, 750, "Conservation: Pretreatment 92 = 88 + 4 • Filtration 88 = 84 + 4", "small"))
    return "".join(parts), measurements


def _treemap(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    plot_x, plot_y, plot_w, plot_h = 70.0, 225.0, 1300.0, 500.0
    group_order = ["grant-community", "grant-environment", "grant-mobility"]
    group_by_id = {group["id"]: group for group in ir["groups"]}
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    colors = [t["data_1"], t["data_2"], t["data_3"], t["document_stroke"], t["file_stroke"], t["money_stroke"], t["negative"]]
    parts: list[str] = []
    measurements: dict[str, Any] = {"leaves": {}}
    cursor_x = plot_x
    color_index = 0
    for group_id in group_order:
        group = group_by_id[group_id]
        group_w = plot_w * float(group["declared_total"]) / 100.0
        cursor_y = plot_y
        parts.append(_text(cursor_x + 14, plot_y - 18, f'{group["label"]} · {group["declared_total"]}', "section"))
        for member_id in group["member_ids"]:
            node = node_by_id[member_id]
            leaf_h = plot_h * float(node["value"]) / float(group["declared_total"])
            area = group_w * leaf_h
            fill = colors[color_index % len(colors)]
            parts.append(f'<rect id="{prefix}-{member_id}" x="{cursor_x:.2f}" y="{cursor_y:.2f}" width="{group_w:.2f}" height="{leaf_h:.2f}" fill="{fill}" fill-opacity=".72" stroke="{t["canvas"]}" stroke-width="4" data-value="{node["value"]}" data-area="{area:.4f}" data-parent="{group_id}"/>')
            parts.append(_wrapped(cursor_x + 16, cursor_y + 31, node["label"], "label", width_chars=max(12, int(group_w / 15))))
            parts.append(_text(cursor_x + 16, cursor_y + leaf_h - 16, f'{node["value"]} units', "number"))
            measurements["leaves"][member_id] = {"value": node["value"], "area": round(area, 4), "parent": group_id}
            cursor_y += leaf_h
            color_index += 1
        cursor_x += group_w
    parts.append(f'<rect x="{plot_x}" y="{plot_y}" width="{plot_w}" height="{plot_h}" fill="none" stroke="{t["ink"]}" stroke-width="2"/>')
    parts.append(_text(70, 765, "Total 100 units • Community 40 • Environment 35 • Mobility 25", "small"))
    return "".join(parts), measurements


def _wardley(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    left, top, width, height = 165.0, 205.0, 1120.0, 520.0
    parts: list[str] = []
    for step in range(6):
        x = left + step / 5 * width
        y = top + step / 5 * height
        parts.append(f'<line class="grid" x1="{x}" y1="{top}" x2="{x}" y2="{top+height}"/>')
        parts.append(f'<line class="grid" x1="{left}" y1="{y}" x2="{left+width}" y2="{y}"/>')
        parts.append(_text(x, top + height + 28, f'{step/5:.1f}', "tiny", anchor="middle"))
    parts.append(f'<line x1="{left}" y1="{top+height}" x2="{left+width}" y2="{top+height}" stroke="{t["ink"]}" stroke-width="2"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top+height}" stroke="{t["ink"]}" stroke-width="2"/>')
    positions: dict[str, tuple[float, float]] = {}
    for node in ir["nodes"]:
        cx = left + node["strategy"]["evolution"] * width
        cy = top + (1 - node["strategy"]["value_chain_position"]) * height
        positions[node["id"]] = (cx, cy)
    for edge in ir["edges"]:
        x1, y1 = positions[edge["source"]]; x2, y2 = positions[edge["target"]]
        parts.append(f'<line id="{prefix}-{edge["id"]}" class="route" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" data-edge-id="{edge["id"]}" data-source="{edge["source"]}" data-target="{edge["target"]}"/>')
    for index, node in enumerate(ir["nodes"]):
        cx, cy = positions[node["id"]]
        parts.append(f'<circle id="{prefix}-{node["id"]}" cx="{cx:.2f}" cy="{cy:.2f}" r="11" fill="{t["data_1"]}" stroke="{t["canvas"]}" stroke-width="4" data-node-id="{node["id"]}" data-evolution="{node["strategy"]["evolution"]}" data-value-chain="{node["strategy"]["value_chain_position"]}"/>')
        dx = 18 if index % 2 == 0 else -18
        anchor = "start" if dx > 0 else "end"
        parts.append(_text(cx + dx, cy - 10, node["label"], "label", anchor=anchor))
        parts.append(_text(cx + dx, cy + 12, f'({node["strategy"]["evolution"]:.2f}, {node["strategy"]["value_chain_position"]:.2f})', "tiny", anchor=anchor))
    parts.append(_text(left + width / 2, 786, "Evolution →", "small", anchor="middle"))
    parts.append(_text(54, top + height / 2, "Value chain ↑", "small", extra=f'transform="rotate(-90 54 {top + height / 2})"', anchor="middle"))
    return "".join(parts), {"plot": [left, top, width, height], "positions": positions}


def _deployment(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    zones = {"Edge": (58, 208, 340, 520), "App": (428, 208, 480, 520), "Data": (938, 208, 444, 520)}
    positions = {
        "deploy-gateway": (126, 390, 210, 132),
        "deploy-approval": (485, 310, 190, 136),
        "deploy-worker": (650, 540, 190, 136),
        "deploy-postgres": (990, 300, 180, 136),
        "deploy-store": (1150, 540, 180, 136),
    }
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    parts: list[str] = []
    for zone, (x, y, w, h) in zones.items():
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" class="panel-alt"/>')
        parts.append(_text(x + 20, y + 34, zone.upper(), "case"))
    route_paths = {
        "deploy-e01": "M336 456 H455 V378 H485",
        "deploy-e02": "M675 360 H990",
        "deploy-e03": "M675 395 H920 V608 H1150",
        "deploy-e04": "M580 446 V520 H745 V540",
        "deploy-e05": "M840 608 H1150",
    }
    for edge in ir["edges"]:
        parts.append(f'<path id="{prefix}-{edge["id"]}" class="route" d="{route_paths[edge["id"]]}" data-edge-id="{edge["id"]}" data-source="{edge["source"]}" data-target="{edge["target"]}"/>')
    for node_id, (x, y, w, h) in positions.items():
        node = node_by_id[node_id]; p = node["placement"]
        focus_class = "node-accent" if node_id == "deploy-approval" else "node"
        parts.append(f'<g id="{prefix}-{node_id}" data-node-id="{node_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" class="{focus_class}"/><rect x="{x+14}" y="{y+14}" width="44" height="44" rx="12" fill="{t["data_1"]}" fill-opacity=".16" stroke="{t["data_1"]}"/><text x="{x+36}" y="{y+43}" class="number" text-anchor="middle">×{p["replicas"]}</text>{_text(x+70, y+34, p["host"], "label")}{_text(x+70, y+56, p["artifact"], "small")}{_text(x+16, y+92, f'Artifact: {p["artifact"]}', "tiny")}{_text(x+16, y+116, f'Port: {", ".join(p["ports"]) or "—"}', "tiny")}</g>')
    return "".join(parts), {"zones": zones, "nodes": positions, "edge_count": len(ir["edges"])}


def _journey(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    left, width = 90.0, 1260.0
    card_y, card_w, card_h = 215.0, 222.0, 188.0
    step = width / 5
    baseline, amplitude = 620.0, 145.0
    nodes = sorted(ir["nodes"], key=lambda value: value["journey"]["stage_order"])
    positions: list[tuple[float, float]] = []
    parts: list[str] = []
    for index, node in enumerate(nodes):
        x = left + index * step
        j = node["journey"]
        parts.append(f'<rect x="{x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="20" class="panel"/>')
        parts.append(_text(x + 18, card_y + 30, f'{index+1:02d} · {node["label"]}', "section"))
        parts.append(_wrapped(x + 18, card_y + 65, j["action"], "label", width_chars=20))
        parts.append(_text(x + 18, card_y + 139, j["touchpoint"], "small"))
        parts.append(_text(x + card_w - 18, card_y + 163, f'{j["sentiment"]:+.1f}', "number", anchor="end"))
        cx = x + card_w / 2
        cy = baseline - j["sentiment"] * amplitude
        positions.append((cx, cy))
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in positions)
    parts.append(f'<line class="grid" x1="{left}" y1="{baseline}" x2="{left+width-30}" y2="{baseline}"/>')
    parts.append(_text(left - 16, baseline + 5, "0", "tiny", anchor="end"))
    parts.append(f'<path d="{path}" fill="none" stroke="{t["data_1"]}" stroke-width="5" stroke-linejoin="round"/>')
    for index, ((cx, cy), node) in enumerate(zip(positions, nodes)):
        shape = "circle" if node["journey"]["sentiment"] >= 0 else "rect"
        if shape == "circle":
            parts.append(f'<circle id="{prefix}-{node["id"]}" cx="{cx}" cy="{cy}" r="10" fill="{t["data_3"]}" stroke="{t["canvas"]}" stroke-width="4" data-sentiment="{node["journey"]["sentiment"]}"/>')
        else:
            parts.append(f'<rect id="{prefix}-{node["id"]}" x="{cx-9}" y="{cy-9}" width="18" height="18" transform="rotate(45 {cx} {cy})" fill="{t["negative"]}" stroke="{t["canvas"]}" stroke-width="4" data-sentiment="{node["journey"]["sentiment"]}"/>')
        parts.append(_text(cx, cy - 18, f'{node["journey"]["sentiment"]:+.1f}', "tiny", anchor="middle"))
    parts.append(_text(90, 755, "● non-negative  ◆ negative  •  sentiment domain −1..1", "small"))
    return "".join(parts), {"sentiment_positions": positions, "domain": [-1, 1]}


def _fishbone(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    spine_y = 485.0
    branch_x = [270, 455, 640, 825, 1010]
    groups = ir["groups"]
    node_by_id = {node["id"]: node for node in ir["nodes"]}
    parts = [f'<line x1="150" y1="{spine_y}" x2="1130" y2="{spine_y}" stroke="{t["connector"]}" stroke-width="5" marker-end="url(#{prefix}-arrow)"/>']
    for index, (group, x) in enumerate(zip(groups, branch_x)):
        top_branch = index % 2 == 0
        tip_y = 250 if top_branch else 710
        parts.append(f'<line x1="{x}" y1="{spine_y}" x2="{x-95}" y2="{tip_y}" stroke="{t["data_1"] if top_branch else t["data_2"]}" stroke-width="3"/>')
        label_y = tip_y - 28 if top_branch else tip_y + 34
        parts.append(_text(x - 95, label_y, group["label"].upper(), "case", anchor="middle"))
        for cause_index, member_id in enumerate(group["member_ids"]):
            along = 0.42 + cause_index * 0.32
            bx = x + (x - 95 - x) * along
            by = spine_y + (tip_y - spine_y) * along
            direction = -1 if top_branch else 1
            parts.append(f'<line x1="{bx}" y1="{by}" x2="{bx+direction*78}" y2="{by}" stroke="{t["border"]}" stroke-width="2"/>')
            anchor = "end" if top_branch else "start"
            tx = bx - 8 if top_branch else bx + 8
            parts.append(_wrapped(tx, by - 8, node_by_id[member_id]["label"], "small", width_chars=22, line_height=17, anchor=anchor))
    effect = node_by_id["fish-effect"]
    parts.append(f'<rect id="{prefix}-fish-effect" x="1135" y="424" width="245" height="122" rx="24" fill="{t["negative"]}" fill-opacity=".13" stroke="{t["negative"]}" stroke-width="2.5"/>')
    parts.append(_wrapped(1257, 464, effect["label"], "section", width_chars=24, anchor="middle"))
    parts.append(_text(70, 790, "Phân tích nguyên nhân giả thuyết • chưa chứng minh quan hệ nhân quả", "small"))
    return "".join(parts), {"cause_count": 10, "group_count": 5, "effect_count": 1}


def _dumbbell(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    left, right, top = 280.0, 1280.0, 250.0
    plot_w = right - left
    before = {d["domain"]: d["value"] for d in ir["series"][0]["data"]}
    after = {d["domain"]: d["value"] for d in ir["series"][1]["data"]}
    parts: list[str] = []
    for value in range(0, 31, 5):
        x = left + value / 30 * plot_w
        parts.append(f'<line class="grid" x1="{x}" y1="210" x2="{x}" y2="690"/>')
        parts.append(_text(x, 718, str(value), "tiny", anchor="middle"))
    measurements: dict[str, Any] = {"categories": {}}
    for index, category in enumerate(before):
        y = top + index * 112
        x1 = left + before[category] / 30 * plot_w
        x2 = left + after[category] / 30 * plot_w
        gap = after[category] - before[category]
        parts.append(_text(left - 28, y + 5, category, "label", anchor="end"))
        parts.append(f'<line x1="{x1:.2f}" y1="{y}" x2="{x2:.2f}" y2="{y}" stroke="{t["data_1"]}" stroke-width="8" stroke-linecap="round" data-gap="{gap}" data-gap-px="{abs(x2-x1):.4f}"/>')
        parts.append(f'<circle cx="{x1:.2f}" cy="{y}" r="10" fill="{t["panel"]}" stroke="{t["data_2"]}" stroke-width="4" data-state="before" data-value="{before[category]}"/>')
        parts.append(f'<circle cx="{x2:.2f}" cy="{y}" r="10" fill="{t["data_3"]}" stroke="{t["canvas"]}" stroke-width="3" data-state="after" data-value="{after[category]}"/>')
        parts.append(_text(x1, y - 20, _fmt(before[category]), "number", anchor="middle"))
        parts.append(_text(x2, y - 20, _fmt(after[category]), "number", anchor="middle"))
        parts.append(_text(max(x1, x2) + 28, y + 5, f'Δ {gap:+}', "tiny"))
        measurements["categories"][category] = {"before": before[category], "after": after[category], "x_before": round(x1, 4), "x_after": round(x2, 4), "gap": gap}
    parts.append(_text((left+right)/2, 758, "Median response time (minutes) · zero-based shared domain", "small", anchor="middle"))
    parts.append(_text(92, 735, "○ Before", "small")); parts.append(_text(92, 760, "● After", "small"))
    return "".join(parts), measurements


def _slopegraph(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    x1, x2, top, bottom = 390.0, 1045.0, 220.0, 700.0
    max_value = 14.0
    colors = [t["data_1"], t["data_2"], t["data_3"]]
    parts: list[str] = []
    for tick in range(0, 15, 2):
        y = bottom - tick / max_value * (bottom - top)
        parts.append(f'<line class="grid" x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"/>')
        parts.append(_text(215, y + 5, str(tick), "tiny", anchor="end"))
    measurements: dict[str, Any] = {"series": {}}
    for index, s in enumerate(ir["series"]):
        q1, q2 = s["data"][0]["value"], s["data"][1]["value"]
        y1 = bottom - q1 / max_value * (bottom - top); y2 = bottom - q2 / max_value * (bottom - top)
        parts.append(f'<line id="{prefix}-{s["id"]}" x1="{x1}" y1="{y1:.2f}" x2="{x2}" y2="{y2:.2f}" stroke="{colors[index]}" stroke-width="5" data-q1="{q1}" data-q2="{q2}"/>')
        parts.append(f'<circle cx="{x1}" cy="{y1:.2f}" r="9" fill="{colors[index]}"/><circle cx="{x2}" cy="{y2:.2f}" r="9" fill="{colors[index]}"/>')
        parts.append(_text(x1 - 20, y1 + 5, f'{s["label"]}  {q1}', "label", anchor="end"))
        parts.append(_text(x2 + 20, y2 + 5, f'{q2}  {s["label"]}', "label"))
        direction = "increase" if q2 > q1 else "decrease" if q2 < q1 else "tie"
        parts.append(_text((x1+x2)/2, (y1+y2)/2 - 12, f'{q2-q1:+.1f} days · {direction}', "tiny", anchor="middle"))
        measurements["series"][s["label"]] = {"q1": q1, "q2": q2, "y1": round(y1, 4), "y2": round(y2, 4), "direction": direction}
    parts.append(_text(x1, 760, "Q1", "section", anchor="middle")); parts.append(_text(x2, 760, "Q2", "section", anchor="middle"))
    parts.append(_text(720, 786, "Shared scale: 0..14 days • Records increases; no improvement styling", "small", anchor="middle"))
    return "".join(parts), measurements


def _hist_counts(samples: Iterable[float], edges: list[float]) -> list[int]:
    values = list(samples); counts = [0] * (len(edges) - 1)
    for value in values:
        for index in range(len(counts)):
            if edges[index] <= value < edges[index + 1] or (index == len(counts) - 1 and value == edges[index + 1]):
                counts[index] += 1
                break
    return counts


def _ridgeline(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    left, right, width = 240.0, 1300.0, 1060.0
    edges = list(ir["series"][0]["distribution"]["bin_edges"])
    derived: list[tuple[Mapping[str, Any], list[int], list[float]]] = []
    global_max = 0.0
    for s in ir["series"]:
        samples = s["data"][0]["distribution_samples"]
        counts = _hist_counts(samples, edges)
        densities = [count / (len(samples) * (edges[i+1]-edges[i])) for i, count in enumerate(counts)]
        global_max = max(global_max, *densities)
        derived.append((s, counts, densities))
    baselines = [350.0, 515.0, 680.0]
    colors = [t["data_1"], t["data_2"], t["data_3"]]
    parts: list[str] = []
    measurements: dict[str, Any] = {"global_max_density": global_max, "series": {}}
    for tick in edges:
        x = left + tick / 12 * width
        parts.append(f'<line class="grid" x1="{x}" y1="220" x2="{x}" y2="710"/>')
        parts.append(_text(x, 745, _fmt(tick), "tiny", anchor="middle"))
    for index, (s, counts, densities) in enumerate(derived):
        baseline = baselines[index]
        step_w = width / len(counts)
        points = [(left, baseline)]
        for bin_index, density in enumerate(densities):
            x1 = left + bin_index * step_w; x2 = x1 + step_w
            y = baseline - (density / global_max if global_max else 0) * 104
            points.extend([(x1, y), (x2, y)])
        points.append((right, baseline))
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in points) + " Z"
        parts.append(f'<path id="{prefix}-{s["id"]}" d="{d}" fill="{colors[index]}" fill-opacity=".46" stroke="{colors[index]}" stroke-width="3" data-counts="{",".join(map(str, counts))}" data-global-max="{global_max:.12f}"/>')
        parts.append(_text(left - 24, baseline - 42, s["label"], "section", anchor="end"))
        parts.append(_text(left - 24, baseline - 18, "n=6", "tiny", anchor="end"))
        parts.append(_text(1350, baseline - 18, " / ".join(map(str, counts)), "tiny", anchor="end"))
        measurements["series"][s["label"]] = {"samples": s["data"][0]["distribution_samples"], "counts": counts, "densities": densities, "baseline": baseline}
    parts.append(_text((left+right)/2, 780, "Duration (minutes) · bins [0,2,4,6,8,10,12] · global-max amplitude", "small", anchor="middle"))
    return "".join(parts), measurements


def _bubble(ir: Mapping[str, Any], t: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Any]]:
    left, top, width, height = 170.0, 205.0, 1000.0, 520.0
    max_size = 5.2; max_area = 5200.0
    colors = [t["data_1"], t["data_2"], t["data_3"], t["negative"]]
    parts: list[str] = []
    for tick in range(0, 11, 2):
        x = left + tick / 10 * width; y = top + height - tick / 10 * height
        parts.append(f'<line class="grid" x1="{x}" y1="{top}" x2="{x}" y2="{top+height}"/><line class="grid" x1="{left}" y1="{y}" x2="{left+width}" y2="{y}"/>')
        parts.append(_text(x, top + height + 28, str(tick), "tiny", anchor="middle")); parts.append(_text(left - 20, y + 5, str(tick), "tiny", anchor="end"))
    measurements: dict[str, Any] = {"observations": {}}
    for index, point in enumerate(ir["series"][0]["data"]):
        cx = left + point["x_value"] / 10 * width
        cy = top + height - point["y_value"] / 10 * height
        area = max_area * point["size_value"] / max_size
        radius = math.sqrt(area / math.pi)
        label = point.get("label", point["id"])
        parts.append(f'<circle id="{prefix}-{point["id"]}" cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.6f}" fill="{colors[index]}" fill-opacity=".48" stroke="{colors[index]}" stroke-width="3" data-x="{point["x_value"]}" data-y="{point["y_value"]}" data-size="{point["size_value"]}" data-area="{area:.6f}"/>')
        parts.append(_text(cx, cy + 4, label, "label", anchor="middle"))
        parts.append(_text(cx, cy + 24, f'{point["size_value"]}M', "tiny", anchor="middle"))
        measurements["observations"][label] = {"x": point["x_value"], "y": point["y_value"], "size": point["size_value"], "cx": round(cx, 4), "cy": round(cy, 4), "area": round(area, 6)}
    parts.append(_text(left + width / 2, 780, "Impact →", "small", anchor="middle"))
    parts.append(_text(64, top + height / 2, "Effort ↑", "small", extra=f'transform="rotate(-90 64 {top + height / 2})"', anchor="middle"))
    legend_x = 1230
    parts.append(_text(legend_x, 260, "BUDGET", "case", anchor="middle"))
    for idx, size in enumerate((1.0, 2.5, 5.0)):
        area = max_area * size / max_size; r = math.sqrt(area / math.pi); cy = 350 + idx * 145
        parts.append(f'<circle cx="{legend_x}" cy="{cy}" r="{r:.3f}" fill="none" stroke="{t["border"]}" stroke-width="2"/>')
        parts.append(_text(legend_x, cy + r + 23, f'{size:.1f} budget_M', "tiny", anchor="middle"))
    return "".join(parts), measurements


RENDERERS = {
    "P18-C01-ARCH": _architecture,
    "P18-C02-SWIM": _swimlane,
    "P18-C03-SANKEY": _sankey,
    "P18-C04-TREEMAP": _treemap,
    "P18-C05-WARDLEY": _wardley,
    "P18-C06-DEPLOY": _deployment,
    "P18-C07-JOURNEY": _journey,
    "P18-C08-FISH": _fishbone,
    "P18-V17-DUMBBELL": _dumbbell,
    "P18-V18-SLOPE": _slopegraph,
    "P18-V19-RIDGE": _ridgeline,
    "P18-V20-BUBBLE": _bubble,
}


def _ledger(case_id: str, ir: Mapping[str, Any]) -> str:
    def table(headers: list[str], rows: list[list[str]]) -> str:
        head = "".join(f"<th scope=\"col\">{escape(value)}</th>" for value in headers)
        body = "".join("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>" for row in rows)
        return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

    if case_id == "P18-C01-ARCH":
        names = {node["id"]: node["label"] for node in ir["nodes"]}
        return table(["Quan hệ", "Nguồn", "Đích", "Hướng"], [[edge["id"], names[edge["source"]], names[edge["target"]], "directed"] for edge in ir["edges"]])
    if case_id == "P18-C02-SWIM":
        lane_rows = [[lane_value["order"] + 1, lane_value["label"], ", ".join(lane_value["member_ids"])] for lane_value in sorted(ir["lanes"], key=lambda value: value["order"])]
        edge_rows = [[edge["label"], edge["source"], edge["target"]] for edge in sorted(ir["edges"], key=lambda value: value["order"])]
        return table(["#", "Lane", "Artifacts"], lane_rows) + table(["Handoff", "Nguồn", "Đích"], edge_rows)
    if case_id == "P18-C03-SANKEY":
        names = {node["id"]: node["label"] for node in ir["nodes"]}
        return table(["Nguồn", "Đích", "Lưu lượng", "Đơn vị"], [[names[e["source"]], names[e["target"]], e["amount"], e["unit"]] for e in ir["edges"]])
    if case_id == "P18-C04-TREEMAP":
        return table(["Leaf", "Parent", "Value", "Unit"], [[n["label"], n["parent_group_id"], n["value"], n["unit"]] for n in ir["nodes"]])
    if case_id == "P18-C05-WARDLEY":
        return table(["Component", "Evolution", "Value-chain position"], [[n["label"], n["strategy"]["evolution"], n["strategy"]["value_chain_position"]] for n in ir["nodes"]])
    if case_id == "P18-C06-DEPLOY":
        return table(["Zone", "Host", "Artifact", "Replicas", "Ports"], [[n["placement"]["zone"], n["placement"]["host"], n["placement"]["artifact"], n["placement"]["replicas"], ", ".join(n["placement"]["ports"]) or "—"] for n in ir["nodes"]])
    if case_id == "P18-C07-JOURNEY":
        return table(["Stage", "Action", "Touchpoint", "Sentiment"], [[n["label"], n["journey"]["action"], n["journey"]["touchpoint"], n["journey"]["sentiment"]] for n in sorted(ir["nodes"], key=lambda value: value["journey"]["stage_order"])])
    if case_id == "P18-C08-FISH":
        node_names = {n["id"]: n["label"] for n in ir["nodes"]}
        return '<p class="hypothesis"><strong>Giới hạn diễn giải:</strong> đây là các giả thuyết phân tích nguyên nhân, không phải quan hệ nhân quả đã được chứng minh.</p>' + table(["Nhóm", "Nguyên nhân"], [[group["label"], node_names[item_id]] for group in ir["groups"] for item_id in group["member_ids"]])
    if case_id == "P18-V17-DUMBBELL":
        first = {d["domain"]: d["value"] for d in ir["series"][0]["data"]}; second = {d["domain"]: d["value"] for d in ir["series"][1]["data"]}
        return table(["Region", "Before", "After", "Gap", "Unit"], [[key, first[key], second[key], second[key] - first[key], "minutes"] for key in first])
    if case_id == "P18-V18-SLOPE":
        return table(["Series", "Q1", "Q2", "Direction", "Unit"], [[s["label"], s["data"][0]["value"], s["data"][1]["value"], "increase" if s["data"][1]["value"] > s["data"][0]["value"] else "decrease", "days"] for s in ir["series"]])
    if case_id == "P18-V19-RIDGE":
        return table(["Series", "Exact samples", "Method", "Bin edges", "Normalization"], [[s["label"], ", ".join(map(str, s["data"][0]["distribution_samples"])), s["distribution"]["method"], ", ".join(map(str, s["distribution"]["bin_edges"])), s["distribution"]["amplitude_normalization"]] for s in ir["series"]])
    if case_id == "P18-V20-BUBBLE":
        return table(["Project", "Impact", "Effort", "Budget", "Size unit"], [[d.get("label", d["id"]), d["x_value"], d["y_value"], d["size_value"], d["size_unit"]] for d in ir["series"][0]["data"]])
    raise ValueError(case_id)


def _html_shell(case_id: str, mode: str, svg: str, ledger: str, source_hash: str, source_bundle_hash: str, t: Mapping[str, str]) -> str:
    meta = CASE_META[case_id]
    filename = f'{meta["slug"]}--{mode}.html'
    mode_label = {"neutral-light": "Neutral light", "neutral-dark": "Neutral dark", "editorial": "Editorial"}[mode]
    return f"""<!doctype html>
<html lang="vi" data-case-id="{case_id}" data-mode="{mode}" data-source-hash="{source_hash}" data-source-bundle-hash="{source_bundle_hash}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{escape(meta['title'])} · {mode_label} · P-18</title>
  <style>
    :root{{--canvas:{t['canvas']};--panel:{t['panel']};--panel-alt:{t['panel_alt']};--ink:{t['ink']};--quiet:{t['quiet']};--border:{t['border']};--accent:{t['accent']};--focus:{t['data_1']};color-scheme:{'dark' if mode == 'neutral-dark' else 'light'};}}
    *{{box-sizing:border-box}} html{{background:var(--canvas);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    body{{margin:0;background:var(--canvas);color:var(--ink)}}
    a{{color:var(--accent);text-underline-offset:3px}} a:focus-visible{{outline:3px solid var(--focus);outline-offset:4px;border-radius:4px}}
    main,footer{{width:min(1536px,100%);margin-inline:auto;padding-inline:clamp(16px,3vw,48px)}}
    .artifact-frame{{width:min(1504px,100%);margin:0 auto;padding:34px clamp(22px,4vw,64px) 0;background:var(--canvas)}}
    .artifact-header{{min-height:142px;padding:0 14px 24px;display:grid;grid-template-columns:minmax(0,1fr) minmax(280px,520px);align-items:end;gap:48px;border-bottom:1px solid var(--border)}}
    .kicker{{margin:0 0 10px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:15px;font-weight:760;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}}
    h1{{font-size:clamp(40px,3.2vw,48px);line-height:1.02;margin:0;letter-spacing:-.035em}} .meta{{margin:12px 0 0;color:var(--quiet);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:15px}}
    .reading-copy{{margin:0;font-size:18px;line-height:1.55;color:var(--quiet)}}
    .gallery-link{{justify-self:end;align-self:start;font-size:15px}}
    figure{{margin:0;background:var(--canvas);overflow:hidden}}
    figure svg{{display:block;width:100%;height:auto;background:var(--canvas)}}
    .evidence{{margin-top:28px;border-top:1px solid var(--border);background:var(--canvas);padding:clamp(22px,3vw,34px) 14px}}
    .evidence h2{{margin:0 0 14px;font-size:22px}} .table-wrap{{overflow-x:auto;margin-block:12px}}
    table{{width:100%;border-collapse:collapse;font-size:.92rem}} th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}} th{{font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--quiet)}}
    .hypothesis{{padding:12px 14px;border-left:5px solid var(--accent);background:var(--panel-alt)}}
    footer{{padding-top:22px;padding-bottom:44px;color:var(--quiet);font-size:.84rem;line-height:1.65}} footer code{{overflow-wrap:anywhere;color:var(--ink)}}
    @media(max-width:800px){{.artifact-header{{grid-template-columns:1fr;gap:16px}}.gallery-link{{justify-self:start}}th,td{{padding:8px;font-size:.8rem}}}}
    @media print{{main,footer{{width:100%;padding-inline:0}}.artifact-frame{{padding-inline:0}}figure,.evidence{{break-inside:avoid}}a{{color:inherit}}}}
    @media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;transition:none!important;animation:none!important}}}}
  </style>
</head>
<body>
  <main>
    <article class="artifact-frame">
      <header class="artifact-header">
        <div><p class="kicker">{escape(meta['type'])} · {escape(meta['capability'])}</p><h1>{escape(meta['title'])}</h1><p class="meta">{mode_label} · motion=none · {PROFILE_BY_CASE[case_id]}</p></div>
        <div><a class="gallery-link" href="../index.html">← Gallery index</a><p class="reading-copy">{escape(meta['reading'])}</p></div>
      </header>
      <figure aria-label="{escape(meta['title'])}">{svg}</figure>
    </article>
    <section class="evidence" aria-labelledby="ledger-title"><h2 id="ledger-title">Exact semantic and data ledger</h2>{ledger}</section>
  </main>
  <footer>
    <strong>QA-only owner-review candidate.</strong> Clean-room-oriented independent reimplementation; no upstream gallery, code, CSS, template or asset used.<br>
    Case source SHA-256: <code>{source_hash}</code><br>
    Source bundle SHA-256: <code>{source_bundle_hash}</code><br>
    File identity: <code>gallery/{filename}</code>
  </footer>
</body>
</html>
"""


def render_specimen(case_id: str, mode: str, *, source_bundle_hash: str) -> RenderedSpecimen:
    if case_id not in RENDERERS:
        raise ValueError(f"Unknown P-18 case: {case_id}")
    if mode not in MODES:
        raise ValueError(f"Unknown visual mode: {mode}")
    ir = build_case(case_id)
    meta = CASE_META[case_id]
    t = _theme(mode)
    prefix = _safe_id(f"p18-{case_id}-{mode}")
    body, measurements = RENDERERS[case_id](ir, t, prefix)
    title_id, desc_id = f"{prefix}-title", f"{prefix}-desc"
    svg = f'''<svg xmlns="{SVG_NS}" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="{title_id} {desc_id}" lang="vi" data-case-id="{case_id}" data-mode="{mode}">
  <title id="{title_id}">{escape(meta['title'])}</title>
  <desc id="{desc_id}">{escape(meta['reading'])} Exact values and relations are repeated in the visible HTML ledger.</desc>
  <style>{_svg_style(t, prefix)}</style>
  {_defs(prefix, t)}
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="{t['canvas']}"/>
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="url(#{prefix}-dots)"/>
  {semantic_field_marker(PROFILE_BY_CASE[case_id])}
  <g class="semantic-composition" data-visual-intent="{escape(INTENT_BY_CASE[case_id])}" transform="{BODY_TRANSFORM}">{body}</g>
  {type_legend(case_id, t)}
</svg>'''
    source_hash = hashlib.sha256(json.dumps(ir, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    ledger = _ledger(case_id, ir)
    html = _html_shell(case_id, mode, svg, ledger, source_hash, source_bundle_hash, t)
    filename = f'{meta["slug"]}--{mode}.html'
    return RenderedSpecimen(case_id, mode, filename, svg, html, source_hash, source_bundle_hash, measurements)


__all__ = ["HEIGHT", "MODES", "RENDERERS", "RenderedSpecimen", "WIDTH", "render_specimen"]
