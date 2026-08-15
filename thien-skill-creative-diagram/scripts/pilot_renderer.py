"""Deterministic P-06 pilot renderer for three explicitly bounded cases.

This module is not the full renderer/exporter planned for P-07/P-08. It accepts
only the original, validated P-06 pilot fixtures and emits static HTML/SVG.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Iterable, Mapping

from diagram_core import canonical_json, semantic_hash
from pilot_cases import PILOT_BUILDERS, build_pilot
from visual_system import Rect, Route, VisualError, load_visual_system, validate_contrast, validate_geometry


RENDERER_VERSION = "p06-pilot-1"
MODE_IDS = ("neutral-light", "neutral-dark", "editorial")
CANVASES = {
    "architecture": (1440, 900),
    "bar-chart": (1440, 900),
    "swimlane": (1600, 900),
}


@dataclass(frozen=True)
class RenderResult:
    case_name: str
    mode: str
    width: int
    height: int
    svg: str
    html: str
    node_bounds: Mapping[str, Rect]
    routes: tuple[Route, ...]
    validation: Mapping[str, Any]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def _svg_text(x: float, y: float, text: str, *, css_class: str, anchor: str = "start", extra: str = "") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" text-anchor="{anchor}" {extra}>{escape(text)}</text>'


def _wrapped_text(rect: Rect, text: str, *, css_class: str = "node-label", max_chars: int = 24) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if not lines:
        lines = [text]
    if len(lines) > 3:
        raise VisualError("label-density", f"Label requires more than three lines: {text}")
    line_height = 24
    first_y = rect.center_y - (len(lines) - 1) * line_height / 2 + 5
    tspans = "".join(f'<tspan x="{rect.center_x:.1f}" y="{first_y + index * line_height:.1f}">{escape(line)}</tspan>' for index, line in enumerate(lines))
    return f'<text class="{css_class}" text-anchor="middle">{tspans}</text>'


def _style(tokens: Mapping[str, str], primitives: Mapping[str, Any]) -> str:
    font_stack = primitives["font_stack"]
    return f"""
    .canvas {{ fill: {tokens['canvas']}; }}
    .surface {{ fill: {tokens['surface']}; stroke: {tokens['border']}; stroke-width: 2; }}
    .surface-alt {{ fill: {tokens['surface_alt']}; stroke: {tokens['border']}; stroke-width: 1.5; }}
    .title {{ font: 700 {primitives['font_title']}px {font_stack}; fill: {tokens['text']}; letter-spacing: -0.4px; }}
    .eyebrow {{ font: 700 14px {font_stack}; fill: {tokens['accent']}; letter-spacing: 1.8px; }}
    .heading {{ font: 700 {primitives['font_heading']}px {font_stack}; fill: {tokens['text']}; }}
    .label {{ font: 600 {primitives['font_label']}px {font_stack}; fill: {tokens['text']}; }}
    .node-label {{ font: 650 {primitives['font_label']}px {font_stack}; fill: {tokens['text']}; }}
    .annotation {{ font: 500 {primitives['font_annotation']}px {font_stack}; fill: {tokens['muted']}; }}
    .numeric {{ font: 700 {primitives['font_label']}px {font_stack}; fill: {tokens['text']}; font-variant-numeric: tabular-nums; }}
    .route {{ fill: none; stroke: {tokens['connector']}; stroke-width: 2.4; stroke-linejoin: round; stroke-linecap: round; marker-end: url(#arrow); }}
    .route-denied {{ fill: none; stroke: {tokens['danger']}; stroke-width: 2.4; stroke-dasharray: 8 6; marker-end: url(#arrow-danger); }}
    .route-badge {{ fill: {tokens['surface']}; stroke: {tokens['border']}; stroke-width: 1; }}
    .lane-divider {{ stroke: {tokens['border']}; stroke-width: 1; }}
    .grid {{ stroke: {tokens['grid']}; stroke-width: 1; }}
    """


def _defs(tokens: Mapping[str, str]) -> str:
    return f"""
    <defs>
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M 0 0 L 9 5 L 0 10 z" fill="{tokens['connector']}"/></marker>
      <marker id="arrow-danger" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M 0 0 L 9 5 L 0 10 z" fill="{tokens['danger']}"/></marker>
      <pattern id="series-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="{tokens['series_2']}"/><line x1="0" y1="0" x2="0" y2="8" stroke="{tokens['canvas']}" stroke-width="2" opacity="0.55"/></pattern>
      <pattern id="denied-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="{tokens['surface']}"/><line x1="0" y1="0" x2="0" y2="8" stroke="{tokens['danger']}" stroke-width="2" opacity="0.35"/></pattern>
    </defs>
    """


def _svg_shell(width: int, height: int, title: str, description: str, body: str, tokens: Mapping[str, str], primitives: Mapping[str, Any], *, artifact_id: str) -> str:
    title_id = f"{artifact_id}-title"
    desc_id = f"{artifact_id}-desc"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="{title_id} {desc_id}" lang="vi">
  <title id="{title_id}">{escape(title)}</title>
  <desc id="{desc_id}">{escape(description)}</desc>
  <style>{_style(tokens, primitives)}</style>
  {_defs(tokens)}
  <rect class="canvas" x="0" y="0" width="{width}" height="{height}"/>
  {body}
</svg>
"""


def _route_path(route: Route) -> str:
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in route.points)


def _horizontal_route(edge: Mapping[str, Any], source: Rect, target: Rect) -> Route:
    if target.center_x >= source.center_x:
        start = (source.right, source.center_y)
        end = (target.left, target.center_y)
    else:
        start = (source.left, source.center_y)
        end = (target.right, target.center_y)
    middle_x = (start[0] + end[0]) / 2
    points = (start, (middle_x, start[1]), (middle_x, end[1]), end)
    return Route(edge["id"], edge["source"], edge["target"], points)


def _vertical_route(edge: Mapping[str, Any], source: Rect, target: Rect) -> Route:
    if target.center_y >= source.center_y:
        start = (source.center_x, source.bottom)
        end = (target.center_x, target.top)
    else:
        start = (source.center_x, source.top)
        end = (target.center_x, target.bottom)
    middle_y = (start[1] + end[1]) / 2
    points = (start, (start[0], middle_y), (end[0], middle_y), end)
    return Route(edge["id"], edge["source"], edge["target"], points)


def _render_route(route: Route, label: str | None, *, denied: bool = False) -> str:
    css_class = "route-denied" if denied else "route"
    path = f'<path id="visual-{escape(route.edge_id)}" class="{css_class}" d="{_route_path(route)}"/>'
    if not label:
        return path
    segment_index = max(0, (len(route.points) - 2) // 2)
    first, second = route.points[segment_index], route.points[segment_index + 1]
    x = (first[0] + second[0]) / 2
    y = (first[1] + second[1]) / 2
    width = max(46, len(label) * 10.4 + 18)
    badge = f'<rect class="route-badge" x="{x - width / 2:.1f}" y="{y - 19:.1f}" width="{width:.1f}" height="34" rx="10"/>'
    return path + badge + _svg_text(x, y + 7, label, css_class="annotation", anchor="middle")


def _render_signal_card(node: Mapping[str, Any], rect: Rect, tokens: Mapping[str, str]) -> str:
    denied = node.get("state") == "denied"
    fill = "url(#denied-hatch)" if denied else tokens["surface"]
    stroke = tokens["danger"] if denied else tokens["border"]
    rail = tokens["danger"] if denied else tokens["accent"]
    role = node["role"].replace("-", " ").upper()
    return (
        f'<g id="visual-{escape(node["id"])}">'
        f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" width="{rect.width:.1f}" height="{rect.height:.1f}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" width="7" height="{rect.height:.1f}" rx="3.5" fill="{rail}"/>'
        + _svg_text(rect.x + 18, rect.y + 22, role, css_class="eyebrow")
        + _wrapped_text(Rect(rect.x + 8, rect.y + 18, rect.width - 16, rect.height - 8), node["label"], max_chars=21)
        + "</g>"
    )


def _architecture_layout(ir: Mapping[str, Any], width: int, height: int) -> tuple[dict[str, Rect], dict[str, Rect], tuple[Route, ...]]:
    nodes_by_id = {node["id"]: node for node in ir["nodes"]}
    grouped = {member for group in ir["groups"] for member in group["member_ids"]}
    ungrouped = [node for node in ir["nodes"] if node["id"] not in grouped]
    group_width = 330
    group_gap = 38
    first_group_x = 238
    group_rects: dict[str, Rect] = {}
    node_rects: dict[str, Rect] = {}
    for index, group in enumerate(ir["groups"]):
        group_x = first_group_x + index * (group_width + group_gap)
        group_rects[group["id"]] = Rect(group_x, 174, group_width, 610)
        members = [nodes_by_id[item_id] for item_id in group["member_ids"]]
        count = len(members)
        usable_height = 500
        step = usable_height / max(1, count)
        for member_index, node in enumerate(members):
            node_rects[node["id"]] = Rect(group_x + 54, 244 + member_index * step, 222, 92)
    for index, node in enumerate(ungrouped):
        node_rects[node["id"]] = Rect(42, 350 + index * 142, 164, 92)
    routes: list[Route] = []
    for edge in ir["edges"]:
        source = node_rects[edge["source"]]
        target = node_rects[edge["target"]]
        route = _horizontal_route(edge, source, target) if abs(target.center_x - source.center_x) >= abs(target.center_y - source.center_y) else _vertical_route(edge, source, target)
        routes.append(route)
    validate_geometry(Rect(32, 150, width - 64, height - 184), node_rects, routes)
    return node_rects, group_rects, tuple(routes)


def _render_architecture(ir: Mapping[str, Any], mode: str, system: Mapping[str, Any]) -> RenderResult:
    width, height = CANVASES["architecture"]
    tokens = system["modes"][mode]
    primitives = system["primitives"]
    nodes, groups, routes = _architecture_layout(ir, width, height)
    parts = [_svg_text(48, 52, "PILOT • ARCHITECTURE • CAP-P05", css_class="eyebrow"), _svg_text(48, 92, ir["diagram"]["title"], css_class="title"), _svg_text(48, 122, "Tuyến chuẩn được ký, kiểm soát và lưu vết; đường tắt được ghi rõ là bị từ chối.", css_class="annotation")]
    for group in ir["groups"]:
        rect = groups[group["id"]]
        parts.append(f'<rect class="surface-alt" x="{rect.x:.1f}" y="{rect.y:.1f}" width="{rect.width:.1f}" height="{rect.height:.1f}" rx="18"/>')
        parts.append(_svg_text(rect.x + 22, rect.y + 34, group["label"], css_class="heading"))
    edges_by_id = {edge["id"]: edge for edge in ir["edges"]}
    for route in routes:
        edge = edges_by_id[route.edge_id]
        parts.append(_render_route(route, edge.get("label"), denied="deny" in edge["id"]))
    for node in ir["nodes"]:
        parts.append(_render_signal_card(node, nodes[node["id"]], tokens))
    parts.append(f'<rect x="48" y="816" width="16" height="16" rx="4" fill="{tokens["accent"]}"/><text x="76" y="829" class="annotation">Tuyến chuẩn</text>')
    parts.append(f'<rect x="188" y="816" width="16" height="16" rx="4" fill="url(#denied-hatch)" stroke="{tokens["danger"]}"/><text x="216" y="829" class="annotation">Tuyến bị từ chối</text>')
    description = "Sơ đồ kiến trúc nhiều kết nối gồm ba vùng xây dựng, kiểm soát và vận hành; tuyến phát hành chuẩn đi qua cổng chính sách và kho gói đã ký, còn đường tắt bị từ chối."
    artifact_id = _safe_id(f"pilot-architecture-{mode}")
    svg = _svg_shell(width, height, ir["diagram"]["title"], description, "".join(parts), tokens, primitives, artifact_id=artifact_id)
    validation = {"geometry": {"nodes": len(nodes), "routes": len(routes), "status": "pass"}, "contrast": "pass", "semantic_ir_hash": semantic_hash(ir)}
    return _finish("architecture", mode, ir, svg, nodes, routes, validation, width, height)


def _bar_description(ir: Mapping[str, Any]) -> str:
    fragments = []
    for series in ir["series"]:
        values = ", ".join(f"{datum['domain']}: {datum['value']} {series['unit']}" for datum in series["data"])
        fragments.append(f"{series['label']} — {values}")
    return "Biểu đồ cột nhóm với dữ liệu tổng hợp. " + "; ".join(fragments) + ". Trục giá trị bắt đầu từ 0."


def _render_bar(ir: Mapping[str, Any], mode: str, system: Mapping[str, Any]) -> RenderResult:
    width, height = CANVASES["bar-chart"]
    tokens = system["modes"][mode]
    primitives = system["primitives"]
    plot = Rect(130, 196, 1210, 540)
    y_axis = next(axis for axis in ir["axes"] if axis["dimension"] == "y")
    maximum = float(y_axis["domain_max"])
    domains = [datum["domain"] for datum in ir["series"][0]["data"]]
    group_width = plot.width / len(domains)
    bar_width = 66
    gap = 18
    parts = [_svg_text(48, 52, "PILOT • GROUPED BAR • CAP-V05", css_class="eyebrow"), _svg_text(48, 92, ir["diagram"]["title"], css_class="title"), _svg_text(48, 122, "Dữ liệu tổng hợp nguyên bản • Đơn vị: sự cố • Trục bắt đầu tại 0", css_class="annotation")]
    for value in range(0, int(maximum) + 1, 5):
        y = plot.bottom - value / maximum * plot.height
        parts.append(f'<line class="grid" x1="{plot.left:.1f}" y1="{y:.1f}" x2="{plot.right:.1f}" y2="{y:.1f}"/>')
        parts.append(_svg_text(plot.left - 18, y + 5, str(value), css_class="annotation", anchor="end"))
    parts.append(f'<line x1="{plot.left:.1f}" y1="{plot.bottom:.1f}" x2="{plot.right:.1f}" y2="{plot.bottom:.1f}" stroke="{tokens["text"]}" stroke-width="2"/>')
    for domain_index, domain in enumerate(domains):
        center = plot.left + group_width * (domain_index + 0.5)
        parts.append(_svg_text(center, plot.bottom + 38, str(domain), css_class="label", anchor="middle"))
        total_width = len(ir["series"]) * bar_width + (len(ir["series"]) - 1) * gap
        for series_index, series in enumerate(ir["series"]):
            datum = series["data"][domain_index]
            value = float(datum["value"])
            bar_height = value / maximum * plot.height
            x = center - total_width / 2 + series_index * (bar_width + gap)
            y = plot.bottom - bar_height
            fill = tokens["series_1"] if series_index == 0 else "url(#series-hatch)"
            parts.append(f'<rect id="visual-{escape(datum["id"])}" x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" rx="8" fill="{fill}"/>')
            parts.append(_svg_text(x + bar_width / 2, y - 10, str(datum["value"]), css_class="numeric", anchor="middle"))
    legend_y = 810
    for index, series in enumerate(ir["series"]):
        x = 130 + index * 220
        fill = tokens["series_1"] if index == 0 else "url(#series-hatch)"
        parts.append(f'<rect x="{x}" y="{legend_y}" width="20" height="20" rx="5" fill="{fill}"/>')
        parts.append(_svg_text(x + 32, legend_y + 15, series["label"], css_class="label"))
    description = _bar_description(ir)
    artifact_id = _safe_id(f"pilot-bar-{mode}")
    svg = _svg_shell(width, height, ir["diagram"]["title"], description, "".join(parts), tokens, primitives, artifact_id=artifact_id)
    validation = {"geometry": {"plot_in_bounds": plot.right <= width - 32 and plot.bottom <= height - 32, "status": "pass"}, "contrast": "pass", "quantitative": {"zero_baseline": y_axis["domain_min"] == 0, "values": [[datum["value"] for datum in series["data"]] for series in ir["series"]]}, "semantic_ir_hash": semantic_hash(ir)}
    return _finish("bar-chart", mode, ir, svg, {}, (), validation, width, height)


ROLE_TRACKS = {"money": 262, "document": 408, "listing": 554, "file": 700}


def _swimlane_layout(ir: Mapping[str, Any], width: int, height: int) -> tuple[dict[str, Rect], tuple[Route, ...], dict[str, Rect]]:
    lanes = sorted(ir["lanes"], key=lambda item: item["order"])
    lane_left = 36
    lane_width = (width - 72) / len(lanes)
    lane_rects = {lane["id"]: Rect(lane_left + index * lane_width, 150, lane_width, 660) for index, lane in enumerate(lanes)}
    lane_by_node = {node_id: lane["id"] for lane in lanes for node_id in lane["member_ids"]}
    node_rects: dict[str, Rect] = {}
    for node in ir["nodes"]:
        lane_rect = lane_rects[lane_by_node[node["id"]]]
        node_rects[node["id"]] = Rect(lane_rect.x + 24, ROLE_TRACKS[node["role"]], lane_rect.width - 48, 82)
    routes: list[Route] = []
    for edge in ir["edges"]:
        source = node_rects[edge["source"]]
        target = node_rects[edge["target"]]
        route = _horizontal_route(edge, source, target) if source.center_y == target.center_y else _vertical_route(edge, source, target)
        routes.append(route)
    validate_geometry(Rect(28, 148, width - 56, height - 172), node_rects, routes)
    return node_rects, tuple(routes), lane_rects


def _ticket_path(rect: Rect) -> str:
    notch = 9
    return f"M {rect.x + 10:.1f} {rect.y:.1f} H {rect.right - 10:.1f} Q {rect.right:.1f} {rect.y:.1f} {rect.right:.1f} {rect.y + 10:.1f} V {rect.center_y - notch:.1f} Q {rect.right - notch:.1f} {rect.center_y:.1f} {rect.right:.1f} {rect.center_y + notch:.1f} V {rect.bottom - 10:.1f} Q {rect.right:.1f} {rect.bottom:.1f} {rect.right - 10:.1f} {rect.bottom:.1f} H {rect.x + 10:.1f} Q {rect.x:.1f} {rect.bottom:.1f} {rect.x:.1f} {rect.bottom - 10:.1f} V {rect.center_y + notch:.1f} Q {rect.x + notch:.1f} {rect.center_y:.1f} {rect.x:.1f} {rect.center_y - notch:.1f} V {rect.y + 10:.1f} Q {rect.x:.1f} {rect.y:.1f} {rect.x + 10:.1f} {rect.y:.1f} Z"


def _render_semantic_node(node: Mapping[str, Any], rect: Rect, tokens: Mapping[str, str]) -> str:
    role = node["role"]
    parts = [f'<g id="visual-{escape(node["id"])}">']
    if role == "money":
        parts.append(f'<path d="{_ticket_path(rect)}" fill="{tokens["money_fill"]}" stroke="{tokens["money_stroke"]}" stroke-width="2"/>')
        parts.append(f'<line x1="{rect.x + 18:.1f}" y1="{rect.bottom - 13:.1f}" x2="{rect.right - 18:.1f}" y2="{rect.bottom - 13:.1f}" stroke="{tokens["money_stroke"]}" stroke-width="2"/>')
    elif role == "document":
        fold = 18
        points = f"{rect.x},{rect.y} {rect.right - fold},{rect.y} {rect.right},{rect.y + fold} {rect.right},{rect.bottom} {rect.x},{rect.bottom}"
        parts.append(f'<polygon points="{points}" fill="{tokens["document_fill"]}" stroke="{tokens["document_stroke"]}" stroke-width="2"/>')
        parts.append(f'<polyline points="{rect.right - fold},{rect.y} {rect.right - fold},{rect.y + fold} {rect.right},{rect.y + fold}" fill="none" stroke="{tokens["document_stroke"]}" stroke-width="2"/>')
    elif role == "listing":
        parts.append(f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" width="{rect.width:.1f}" height="{rect.height:.1f}" rx="8" fill="{tokens["listing_fill"]}" stroke="{tokens["listing_stroke"]}" stroke-width="2"/>')
        for offset in (15, 24, 33):
            parts.append(f'<line aria-hidden="true" x1="{rect.x + 14:.1f}" y1="{rect.y + offset:.1f}" x2="{rect.x + 52:.1f}" y2="{rect.y + offset:.1f}" stroke="{tokens["listing_stroke"]}" stroke-width="2" opacity="0.7"/>')
    elif role == "file":
        tab_width = min(88, rect.width * 0.44)
        path = f"M {rect.x:.1f} {rect.y + 16:.1f} H {rect.x + tab_width:.1f} L {rect.x + tab_width + 16:.1f} {rect.y:.1f} H {rect.right:.1f} V {rect.bottom:.1f} H {rect.x:.1f} Z"
        parts.append(f'<path d="{path}" fill="{tokens["file_fill"]}" stroke="{tokens["file_stroke"]}" stroke-width="2"/>')
    else:
        raise VisualError("shape-role-unsupported", f"No P-06 semantic shape for role {role}.")
    parts.append(f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" width="7" height="{rect.height:.1f}" rx="3.5" fill="{tokens["accent"]}"/>')
    parts.append(_wrapped_text(Rect(rect.x + 8, rect.y, rect.width - 16, rect.height), node["label"], max_chars=22))
    parts.append("</g>")
    return "".join(parts)


def _render_swimlane(ir: Mapping[str, Any], mode: str, system: Mapping[str, Any]) -> RenderResult:
    width, height = CANVASES["swimlane"]
    tokens = system["modes"][mode]
    primitives = system["primitives"]
    nodes, routes, lanes = _swimlane_layout(ir, width, height)
    parts = [_svg_text(36, 42, "PILOT • GROUPED SWIMLANE • REF-001", css_class="eyebrow"), _svg_text(36, 82, ir["diagram"]["title"], css_class="title"), _svg_text(36, 112, "Theo dõi độc lập séc, chứng từ, bảng kê và tệp lưu qua sáu đơn vị.", css_class="annotation")]
    sorted_lanes = sorted(ir["lanes"], key=lambda item: item["order"])
    for index, lane in enumerate(sorted_lanes):
        rect = lanes[lane["id"]]
        fill = tokens["surface"] if index % 2 == 0 else tokens["surface_alt"]
        parts.append(f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" width="{rect.width:.1f}" height="{rect.height:.1f}" fill="{fill}" opacity="0.72"/>')
        parts.append(f'<line class="lane-divider" x1="{rect.x:.1f}" y1="{rect.y:.1f}" x2="{rect.x:.1f}" y2="{rect.bottom:.1f}"/>')
        parts.append(_svg_text(rect.center_x, 190, lane["label"], css_class="heading", anchor="middle"))
    last_lane = lanes[sorted_lanes[-1]["id"]]
    parts.append(f'<line class="lane-divider" x1="{last_lane.right:.1f}" y1="150" x2="{last_lane.right:.1f}" y2="810"/>')
    for annotation in ir["annotations"]:
        if not annotation["text"].startswith("owner-group:"):
            continue
        label = annotation["text"].split(":", 1)[1]
        target_rects = [lanes[item_id] for item_id in annotation["target_ids"]]
        left = min(rect.left for rect in target_rects)
        right = max(rect.right for rect in target_rects)
        parts.append(f'<rect x="{left + 4:.1f}" y="116" width="{right - left - 8:.1f}" height="38" rx="12" fill="{tokens["accent"]}"/>')
        parts.append(_svg_text((left + right) / 2, 141, label.upper(), css_class="label", anchor="middle", extra=f'fill="{tokens["on_accent"]}" style="fill:{tokens["on_accent"]}"'))
    edges_by_id = {edge["id"]: edge for edge in ir["edges"]}
    for route in routes:
        parts.append(_render_route(route, edges_by_id[route.edge_id].get("label")))
    for node in ir["nodes"]:
        parts.append(_render_semantic_node(node, nodes[node["id"]], tokens))
    legend = (("money", "Séc"), ("document", "Chứng từ đối chiếu"), ("listing", "Bảng kê"), ("file", "Tệp lưu"))
    legend_y = 842
    for index, (role, label) in enumerate(legend):
        x = 36 + index * 250
        sample = Rect(x, legend_y - 17, 30, 24)
        mini_node = {"id": f"legend-{role}", "role": role, "label": ""}
        parts.append(_render_semantic_node(mini_node, sample, tokens).replace('<text class="node-label" text-anchor="middle"><tspan x="', '<text aria-hidden="true" opacity="0" class="node-label" text-anchor="middle"><tspan x="'))
        parts.append(_svg_text(x + 42, legend_y, label, css_class="label"))
    description = "Swimlane tiếng Việt gồm sáu đơn vị: Khách hàng, Phòng thư, Thu tiền, Phải thu, Sổ cái và Ngân hàng. Thủ quỹ quản lý Phòng thư và Thu tiền; Kế toán trưởng quản lý Phải thu và Sổ cái. Các handoff (1) đến (5) nối séc, giấy báo chuyển tiền, bảng kê chuyển tiền, tệp phải thu và tệp sổ cái."
    artifact_id = _safe_id(f"pilot-swimlane-{mode}")
    svg = _svg_shell(width, height, ir["diagram"]["title"], description, "".join(parts), tokens, primitives, artifact_id=artifact_id)
    validation = {"geometry": {"nodes": len(nodes), "routes": len(routes), "status": "pass"}, "contrast": "pass", "benchmark": {"lanes": 6, "owner_groups": 2, "handoffs": sorted({edge["label"] for edge in ir["edges"]}), "roles": sorted({node["role"] for node in ir["nodes"]})}, "semantic_ir_hash": semantic_hash(ir)}
    return _finish("swimlane", mode, ir, svg, nodes, routes, validation, width, height)


def _data_table(ir: Mapping[str, Any]) -> str:
    if not ir["series"]:
        return ""
    headers = "".join(f"<th scope=\"col\">{escape(str(datum['domain']))}</th>" for datum in ir["series"][0]["data"])
    rows = []
    for series in ir["series"]:
        cells = "".join(f"<td>{escape(str(datum['value']))} {escape(str(series['unit']))}</td>" for datum in series["data"])
        rows.append(f"<tr><th scope=\"row\">{escape(series['label'])}</th>{cells}</tr>")
    return f'<table class="data-table"><caption>Dữ liệu chính xác của biểu đồ</caption><thead><tr><th scope="col">Chuỗi</th>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def _html_shell(ir: Mapping[str, Any], svg: str, mode: str) -> str:
    editorial_note = '<aside><strong>Ghi chú biên tập</strong><p>Ưu tiên cấu trúc, quan hệ và khả năng truy vết trước trang trí.</p></aside>' if mode == "editorial" else ""
    return f"""<!doctype html>
<html lang="{escape(ir['diagram']['language'])}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(ir['diagram']['title'])}</title>
<style>
html,body{{margin:0;padding:0;background:#fff;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}}main{{max-width:1600px;margin:auto;padding:16px}}.frame{{overflow:auto;border-radius:16px}}svg{{display:block;width:100%;height:auto;min-width:720px}}aside{{margin:16px 0 0;padding:16px 20px;border-left:4px solid #A3422E;background:#F2EFE9;color:#1F272D}}aside p{{margin:4px 0 0}}.data-table{{border-collapse:collapse;margin:20px 0;width:100%;max-width:900px}}.data-table caption{{font-weight:700;text-align:left;margin-bottom:8px}}th,td{{border:1px solid #9BA6B4;padding:8px 10px;text-align:left}}@media print{{main{{padding:0}}aside{{display:none}}.frame{{overflow:visible}}svg{{min-width:0}}}}
</style>
</head>
<body><main><div class="frame">{svg}</div>{editorial_note}{_data_table(ir)}</main></body></html>
"""


def _validate_serialization(svg: str, html: str) -> dict[str, Any]:
    lowered = (svg + html).lower().replace('xmlns="http://www.w3.org/2000/svg"', "")
    forbidden = ("<script", "http://", "https://", "file://", "javascript:", "onload=", "onclick=")
    found = [token for token in forbidden if token in lowered]
    if found:
        raise VisualError("external-or-executable-content", f"Forbidden serialized content: {found[0]}")
    ids = re.findall(r'\bid="([^"]+)"', svg)
    if len(ids) != len(set(ids)):
        raise VisualError("duplicate-svg-id", "SVG IDs must be unique.")
    if "<title " not in svg or "<desc " not in svg or 'role="img"' not in svg:
        raise VisualError("accessible-name-missing", "SVG requires title, description, and image role.")
    return {"self_contained": True, "unique_ids": len(ids), "accessible_name": True, "status": "pass"}


def _finish(case_name: str, mode: str, ir: Mapping[str, Any], svg: str, nodes: Mapping[str, Rect], routes: Iterable[Route], validation: Mapping[str, Any], width: int, height: int) -> RenderResult:
    html = _html_shell(ir, svg, mode)
    serialization = _validate_serialization(svg, html)
    combined = dict(validation)
    combined["serialization"] = serialization
    combined["renderer_version"] = RENDERER_VERSION
    combined["mode"] = mode
    return RenderResult(case_name, mode, width, height, svg, html, dict(nodes), tuple(routes), combined)


RENDERERS = {"architecture": _render_architecture, "bar-chart": _render_bar, "swimlane": _render_swimlane}


def render_pilot(case_name: str, mode: str) -> RenderResult:
    if case_name not in RENDERERS:
        raise VisualError("pilot-case-unsupported", f"P-06 does not support visual case {case_name}.")
    if mode not in MODE_IDS:
        raise VisualError("visual-mode-unsupported", f"Unsupported approved mode: {mode}.")
    system = load_visual_system()
    validate_contrast(system)
    ir = build_pilot(case_name)
    return RENDERERS[case_name](ir, mode, system)


def _write_artifact(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _contact_sheet_html(artifacts: Iterable[Mapping[str, Any]]) -> str:
    cards = []
    for artifact in artifacts:
        cards.append(
            f'<figure><figcaption><strong>{escape(str(artifact["case"]))}</strong><span>{escape(str(artifact["mode"]))}</span></figcaption>'
            f'<img src="{escape(str(artifact["svg"]))}" alt="Golden candidate {escape(str(artifact["case"]))}, mode {escape(str(artifact["mode"]))}"></figure>'
        )
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P-06 golden candidates</title><style>
body{{margin:0;padding:32px;background:#E7EBF0;color:#172033;font-family:system-ui,-apple-system,'Segoe UI',sans-serif}}header{{max-width:1800px;margin:0 auto 24px}}h1{{margin:0 0 8px;font-size:32px}}p{{margin:0;color:#526175;font-size:18px}}main{{max-width:1800px;margin:auto;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}figure{{margin:0;background:#fff;border:1px solid #AEBAC9;border-radius:16px;overflow:hidden;box-shadow:0 8px 26px rgba(23,32,51,.08)}}figcaption{{display:flex;justify-content:space-between;padding:12px 16px;font-size:16px}}figcaption span{{color:#526175}}img{{display:block;width:100%;height:auto;background:#fff}}@media(max-width:1100px){{main{{grid-template-columns:1fr}}}}</style></head><body><header><h1>P-06 · Original visual direction</h1><p>9 static candidates · 3 pilot families × 3 approved modes · owner review required</p></header><main>{"".join(cards)}</main></body></html>"""


def generate_pilots(output_dir: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for case_name in RENDERERS:
        for mode in MODE_IDS:
            result = render_pilot(case_name, mode)
            stem = f"pilot-{case_name}-{mode}"
            svg_path = output_dir / f"{stem}.svg"
            html_path = output_dir / f"{stem}.html"
            svg_hash = _write_artifact(svg_path, result.svg)
            html_hash = _write_artifact(html_path, result.html)
            artifacts.append({"case": case_name, "mode": mode, "svg": svg_path.name, "svg_sha256": svg_hash, "html": html_path.name, "html_sha256": html_hash, "validation": result.validation})
    contact_sheet_hash = _write_artifact(output_dir / "contact-sheet.html", _contact_sheet_html(artifacts))
    manifest = {"schema_version": "1.0", "renderer_version": RENDERER_VERSION, "artifact_count": len(artifacts) * 2, "artifacts": artifacts, "qa_artifacts": [{"path": "contact-sheet.html", "sha256": contact_sheet_hash}], "source": "original P-06 pilot fixtures", "approval": "golden-candidate; owner review required"}
    manifest_content = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    _write_artifact(output_dir / "pilot-manifest.json", manifest_content)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate original P-06 static pilot candidates.")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = generate_pilots(args.output_dir.resolve())
    print(canonical_json({"artifact_count": manifest["artifact_count"], "status": "generated"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
