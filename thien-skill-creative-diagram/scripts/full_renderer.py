"""P-07 static visual-coverage renderer for all 27 canonical types.

This module proves type/variant/pattern visual coverage with deterministic,
self-contained SVG. It is not the P-08 production exporter or motion layer.
"""

from __future__ import annotations

import hashlib
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape
from typing import Any, Iterable, Mapping, Sequence

from diagram_core import CANONICAL_TYPES, canonical_json
from semantic_grammars import validate_semantics
from visual_system import Rect, VisualError, load_visual_system, rects_overlap, validate_contrast


RENDERER_VERSION = "p07-static-coverage-1"
WIDTH = 1600
HEIGHT = 900


@dataclass(frozen=True)
class CoverageRender:
    diagram_type: str
    mode: str
    svg: str
    node_boxes: Mapping[str, Rect]
    validation: Mapping[str, Any]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.svg.encode("utf-8")).hexdigest()


def _id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "-", value)


def _lines(label: str, limit: int = 24) -> list[str]:
    words = label.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= limit:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _text_lines(x: float, y: float, label: str, css: str = "node-label", anchor: str = "middle", line_gap: int = 25) -> str:
    lines = _lines(label)
    spans = "".join(f'<tspan x="{x:.1f}" dy="{0 if index == 0 else line_gap}">{escape(line)}</tspan>' for index, line in enumerate(lines))
    return f'<text class="{css}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{spans}</text>'


def _shell(diagram_type: str, mode: str, title: str, description: str, body: str, tokens: Mapping[str, str], coverage_badge: bool) -> str:
    prefix = _id(f"p07-{diagram_type}-{mode}")
    font = load_visual_system()["primitives"]["font_stack"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="{prefix}-title {prefix}-desc" lang="vi">
<title id="{prefix}-title">{escape(title)}</title>
<desc id="{prefix}-desc">{escape(description)}</desc>
<defs>
  <marker id="{prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{tokens['connector']}"/></marker>
  <pattern id="{prefix}-hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="{tokens['border']}" stroke-width="3"/></pattern>
</defs>
<style>
.title{{font:700 32px {font};fill:{tokens['text']}}}.subtitle{{font:500 18px {font};fill:{tokens['muted']}}}.heading{{font:700 21px {font};fill:{tokens['text']}}}.node-label{{font:650 18px {font};fill:{tokens['text']}}}.annotation{{font:500 16px {font};fill:{tokens['muted']}}}.numeric{{font:700 17px {font};fill:{tokens['text']};font-variant-numeric:tabular-nums}}.edge-label{{font:600 15px {font};fill:{tokens['text']}}}
</style>
<rect width="{WIDTH}" height="{HEIGHT}" fill="{tokens['canvas']}"/>
{f'<text class="subtitle" x="56" y="56">P-07 · {escape(diagram_type)} · static coverage</text>' if coverage_badge else ''}
<text class="title" x="56" y="100">{escape(title)}</text>
{body}
</svg>'''


def _node_shape(node: Mapping[str, Any], rect: Rect, tokens: Mapping[str, str], prefix: str) -> str:
    role = str(node["role"])
    label = str(node["label"])
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    fill = tokens["surface"]
    stroke = tokens["border"]
    if role in {"start", "initial", "terminal"}:
        shape = f'<rect id="{prefix}-{_id(node["id"])}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    elif role == "decision":
        points = f"{x + w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
        shape = f'<polygon id="{prefix}-{_id(node["id"])}" points="{points}" fill="{tokens["money_fill"]}" stroke="{tokens["money_stroke"]}" stroke-width="2"/>'
    elif role in {"artifact", "document"}:
        fold = 22
        path = f"M{x},{y} H{x+w-fold} L{x+w},{y+fold} V{y+h} H{x} Z M{x+w-fold},{y} V{y+fold} H{x+w}"
        shape = f'<path id="{prefix}-{_id(node["id"])}" d="{path}" fill="{tokens["document_fill"]}" stroke="{tokens["document_stroke"]}" stroke-width="2"/>'
    elif role in {"dataset", "sink", "source"}:
        shape = f'<rect id="{prefix}-{_id(node["id"])}" x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{tokens["file_fill"]}" stroke="{tokens["file_stroke"]}" stroke-width="2"/>'
    else:
        shape = f'<rect id="{prefix}-{_id(node["id"])}" x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/><rect x="{x}" y="{y}" width="7" height="{h}" rx="3" fill="{tokens["accent"]}"/>'
    lines = _lines(label)
    text_y = y + h / 2 - (len(lines) - 1) * 12 + 6
    return shape + _text_lines(x + w / 2, text_y, label)


def _generic_graph(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str, columns_override: int | None = None) -> tuple[str, dict[str, Rect]]:
    nodes = list(ir["nodes"])
    columns = columns_override or min(4, max(1, len(nodes)))
    rows = max(1, math.ceil(len(nodes) / columns))
    gap_x, gap_y = 48, 56
    node_w = min(280, (WIDTH - 160 - gap_x * (columns - 1)) / columns)
    node_h = min(150, (HEIGHT - 300 - gap_y * (rows - 1)) / rows)
    boxes: dict[str, Rect] = {}
    for index, node in enumerate(nodes):
        row, column = divmod(index, columns)
        boxes[node["id"]] = Rect(80 + column * (node_w + gap_x), 220 + row * (node_h + gap_y), node_w, node_h)
    body: list[str] = []
    for group in ir["groups"]:
        members = [boxes[item] for item in group["member_ids"] if item in boxes]
        if not members:
            continue
        left = min(rect.left for rect in members) - 22
        top = min(rect.top for rect in members) - 42
        right = max(rect.right for rect in members) + 22
        bottom = max(rect.bottom for rect in members) + 22
        body.append(f'<rect id="{prefix}-{_id(group["id"])}" x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" rx="18" fill="{tokens["surface_alt"]}" stroke="{tokens["border"]}" stroke-width="2" stroke-dasharray="8 6"/>')
        body.append(f'<text class="heading" x="{left+16}" y="{top+28}">{escape(str(group["label"]))}</text>')
    for edge in ir["edges"]:
        if edge["source"] not in boxes or edge["target"] not in boxes:
            continue
        source, target = boxes[edge["source"]], boxes[edge["target"]]
        if source.center_x <= target.center_x:
            start, end = (source.right, source.center_y), (target.left, target.center_y)
        else:
            start, end = (source.left, source.center_y), (target.right, target.center_y)
        mid_x = (start[0] + end[0]) / 2
        dash = ' stroke-dasharray="9 7"' if edge["kind"] in {"rejection", "exception", "deny"} else ""
        body.append(f'<path id="{prefix}-{_id(edge["id"])}" d="M{start[0]},{start[1]} H{mid_x} V{end[1]} H{end[0]}" fill="none" stroke="{tokens["connector"]}" stroke-width="3" marker-end="url(#{prefix}-arrow)"{dash}/>' )
        label = edge.get("label") or edge.get("guard") or edge["kind"]
        body.append(f'<text class="edge-label" x="{mid_x}" y="{min(start[1],end[1])-8}" text-anchor="middle">{escape(str(label))}</text>')
    for node in nodes:
        body.append(_node_shape(node, boxes[node["id"]], tokens, prefix))
    for annotation in ir["annotations"]:
        body.append(f'<text class="annotation" x="80" y="{HEIGHT-54}">{escape(str(annotation["text"]))}</text>')
    return "".join(body), boxes


def _sequence(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    nodes = list(ir["nodes"])
    step = (WIDTH - 180) / max(1, len(nodes))
    boxes = {node["id"]: Rect(90 + index * step, 190, min(240, step - 24), 76) for index, node in enumerate(nodes)}
    body: list[str] = []
    for index, group in enumerate(ir["groups"]):
        body.append(f'<rect id="{prefix}-{_id(group["id"])}" x="64" y="{300+index*90}" width="1472" height="76" rx="12" fill="none" stroke="{tokens["accent"]}" stroke-width="2" stroke-dasharray="9 7"/><text class="annotation" x="84" y="{326+index*90}">{escape(str(group["label"]))}</text>')
    for node in nodes:
        rect = boxes[node["id"]]
        body.append(_node_shape(node, rect, tokens, prefix))
        body.append(f'<line x1="{rect.center_x}" y1="{rect.bottom}" x2="{rect.center_x}" y2="790" stroke="{tokens["border"]}" stroke-width="2" stroke-dasharray="8 8"/>')
    y = 330
    for edge in sorted(ir["edges"], key=lambda item: (item.get("order", 0), item["id"])):
        source, target = boxes[edge["source"]], boxes[edge["target"]]
        body.append(f'<line id="{prefix}-{_id(edge["id"])}" x1="{source.center_x}" y1="{y}" x2="{target.center_x}" y2="{y}" stroke="{tokens["connector"]}" stroke-width="3" marker-end="url(#{prefix}-arrow)"/>')
        body.append(f'<text class="edge-label" x="{(source.center_x+target.center_x)/2}" y="{y-12}" text-anchor="middle">{escape(str(edge.get("label") or edge["kind"]))}</text>')
        y += 86
    return "".join(body), boxes


def _timeline(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    nodes = list(ir["nodes"])
    xs = [180 + index * ((WIDTH - 360) / max(1, len(nodes) - 1)) for index in range(len(nodes))]
    body = [f'<line x1="150" y1="470" x2="1450" y2="470" stroke="{tokens["connector"]}" stroke-width="4"/>']
    boxes: dict[str, Rect] = {}
    for index, node in enumerate(nodes):
        y = 280 if index % 2 == 0 else 550
        rect = Rect(xs[index] - 125, y, 250, 110)
        boxes[node["id"]] = rect
        body.append(f'<line x1="{xs[index]}" y1="{rect.bottom if y<470 else rect.top}" x2="{xs[index]}" y2="470" stroke="{tokens["connector"]}" stroke-width="2"/>')
        body.append(f'<circle cx="{xs[index]}" cy="470" r="11" fill="{tokens["accent"]}"/>')
        body.append(_node_shape(node, rect, tokens, prefix))
        body.append(f'<text class="annotation" x="{xs[index]}" y="{rect.bottom+26 if y<470 else rect.top-14}" text-anchor="middle">{escape(str(node.get("start", "")))}</text>')
    return "".join(body), boxes


def _lanes(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    lanes = sorted(ir["lanes"], key=lambda item: (item["order"], item["id"]))
    lane_h = min(210, (HEIGHT - 210) / max(1, len(lanes)))
    boxes: dict[str, Rect] = {}
    body: list[str] = []
    node_map = {node["id"]: node for node in ir["nodes"]}
    for lane_index, lane in enumerate(lanes):
        y = 160 + lane_index * lane_h
        body.append(f'<rect id="{prefix}-{_id(lane["id"])}" x="56" y="{y}" width="1488" height="{lane_h}" fill="{tokens["surface_alt"]}" fill-opacity="{0.55 if lane_index%2==0 else 0.25}" stroke="{tokens["border"]}"/>')
        body.append(f'<text class="heading" x="76" y="{y+34}">{escape(str(lane["label"]))}</text>')
        members = [node_map[item] for item in lane["member_ids"] if item in node_map]
        step = (WIDTH - 300) / max(1, len(members))
        for member_index, node in enumerate(members):
            rect = Rect(230 + member_index * step, y + 54, min(270, step - 30), min(112, lane_h - 70))
            boxes[node["id"]] = rect
    unplaced = [node for node in ir["nodes"] if node["id"] not in boxes]
    for index, node in enumerate(unplaced):
        boxes[node["id"]] = Rect(230 + index * 300, 710, 260, 100)
    for edge in ir["edges"]:
        if edge["source"] in boxes and edge["target"] in boxes:
            source, target = boxes[edge["source"]], boxes[edge["target"]]
            body.append(f'<path id="{prefix}-{_id(edge["id"])}" d="M{source.right},{source.center_y} H{target.left}" stroke="{tokens["connector"]}" stroke-width="3" fill="none" marker-end="url(#{prefix}-arrow)"/>')
    for node in ir["nodes"]:
        body.append(_node_shape(node, boxes[node["id"]], tokens, prefix))
    for index, annotation in enumerate(ir["annotations"]):
        body.append(f'<text class="annotation" x="80" y="{HEIGHT-54-index*26}">{escape(str(annotation["text"]))}</text>')
    return "".join(body), boxes


def _cartesian(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str, kind: str) -> tuple[str, dict[str, Rect]]:
    left, top, right, bottom = 170, 180, 1460, 740
    body = [f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="{tokens["text"]}" stroke-width="3"/>']
    for axis in ir["axes"]:
        if axis["dimension"] == "x":
            body.append(f'<text class="heading" x="{(left+right)/2}" y="{bottom+78}" text-anchor="middle">{escape(str(axis["label"]))}</text>')
        elif axis["dimension"] == "y":
            body.append(f'<text class="heading" x="84" y="{(top+bottom)/2}" text-anchor="middle" transform="rotate(-90 84 {(top+bottom)/2})">{escape(str(axis["label"]))}</text>')
    all_values = [datum["value"] for series in ir["series"] for datum in series["data"] if datum["value"] is not None]
    axis_y = next((axis for axis in ir["axes"] if axis["dimension"] in {"y", "radial"}), None)
    y_min = float(axis_y.get("domain_min", min([0.0] + [float(v) for v in all_values])) if axis_y else min([0.0] + [float(v) for v in all_values]))
    stacked = kind == "bar-chart" and "CAP-V06" in ir["diagram"].get("variant_ids", []) and len(ir["series"]) > 1
    stacked_max = max([sum(max(0.0, float(series["data"][index]["value"] or 0)) for series in ir["series"]) for index in range(len(ir["series"][0]["data"]))] or [1.0]) if stacked else None
    stacked_min = min([sum(min(0.0, float(series["data"][index]["value"] or 0)) for series in ir["series"]) for index in range(len(ir["series"][0]["data"]))] or [0.0]) if stacked else None
    if stacked_min is not None:
        y_min = min(y_min, float(stacked_min))
    y_max = float(max(float(axis_y.get("domain_max", 1.0)) if axis_y else 1.0, stacked_max) if stacked_max is not None else (axis_y.get("domain_max", max([1.0] + [float(v) for v in all_values])) if axis_y else max([1.0] + [float(v) for v in all_values])))
    if y_max == y_min:
        y_max += 1
    zero_y = bottom - (0.0 - y_min) / (y_max - y_min) * (bottom - top)
    axis_y_position = zero_y if kind == "bar-chart" else bottom
    body.insert(0, f'<line data-zero-baseline="{str(kind == "bar-chart").lower()}" x1="{left}" y1="{axis_y_position}" x2="{right}" y2="{axis_y_position}" stroke="{tokens["text"]}" stroke-width="3"/>')
    domains: list[Any] = []
    for series in ir["series"]:
        for datum in series["data"]:
            if datum["domain"] not in domains:
                domains.append(datum["domain"])
    x_step = (right - left) / max(1, len(domains))
    palette = [tokens["series_1"], tokens["series_2"], tokens["accent"], tokens["success"]]
    stack_offsets_positive = [0.0 for _ in domains]
    stack_offsets_negative = [0.0 for _ in domains]
    for s_index, series in enumerate(ir["series"]):
        points: list[str] = []
        for index, datum in enumerate(series["data"]):
            if datum["value"] is None:
                continue
            x = left + (domains.index(datum["domain"]) + 0.5) * x_step
            y = bottom - (float(datum["value"]) - y_min) / (y_max - y_min) * (bottom - top)
            color = palette[s_index % len(palette)]
            if kind == "bar-chart":
                bar_w = min(70, x_step / (len(ir["series"]) + 1))
                if stacked:
                    domain_index = domains.index(datum["domain"])
                    offsets = stack_offsets_positive if float(datum["value"]) >= 0 else stack_offsets_negative
                    base_value = offsets[domain_index]
                    top_value = base_value + float(datum["value"])
                    stacked_y = bottom - (top_value-y_min)/(y_max-y_min)*(bottom-top)
                    base_y = bottom - (base_value-y_min)/(y_max-y_min)*(bottom-top)
                    bx = x - min(92, x_step*0.5)/2
                    body.append(f'<rect id="{prefix}-{_id(datum["id"])}" x="{bx}" y="{min(stacked_y,base_y)}" width="{min(92,x_step*0.5)}" height="{abs(base_y-stacked_y)}" fill="{color}" stroke="{tokens["canvas"]}" stroke-width="2"/>')
                    y = stacked_y
                    offsets[domain_index] = top_value
                else:
                    bx = x + (s_index - (len(ir["series"])-1)/2) * bar_w - bar_w/2
                    body.append(f'<rect id="{prefix}-{_id(datum["id"])}" x="{bx}" y="{min(y,zero_y)}" width="{bar_w-6}" height="{abs(zero_y-y)}" rx="8" fill="{color}"/>')
            else:
                body.append(f'<circle id="{prefix}-{_id(datum["id"])}" cx="{x}" cy="{y}" r="9" fill="{color}" stroke="{tokens["surface"]}" stroke-width="3"/>')
                points.append(f"{x},{y}")
            label_y = y - 14 if float(datum["value"]) >= 0 else y + 28
            body.append(f'<text class="numeric" x="{x}" y="{label_y}" text-anchor="middle">{escape(str(datum["value"]))}</text>')
        if kind == "line-chart" and len(points) > 1:
            body.insert(2, f'<polyline points="{" ".join(points)}" fill="none" stroke="{palette[s_index % len(palette)]}" stroke-width="4"/>')
        body.append(f'<text class="annotation" x="{right-220}" y="{top+28+s_index*28}">{escape(str(series["label"]))}</text>')
    for index, domain in enumerate(domains):
        x = left + (index + 0.5) * x_step
        body.append(f'<text class="annotation" x="{x}" y="{bottom+34}" text-anchor="middle">{escape(str(domain))}</text>')
    body.append(f'<text class="annotation" x="{left}" y="{HEIGHT-55}">{escape(" · ".join(f"{series["label"]}: " + ", ".join(f"{datum["domain"]}={datum["value"]}" for datum in series["data"]) for series in ir["series"]))}</text>')
    return "".join(body), {}


def _radar(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    cx, cy, radius = 800, 470, 270
    axes = ir["axes"]
    count = max(3, len(axes))
    body: list[str] = []
    for ring in range(1, 6):
        points = []
        for index in range(count):
            angle = -math.pi/2 + 2*math.pi*index/count
            points.append(f"{cx+radius*ring/5*math.cos(angle)},{cy+radius*ring/5*math.sin(angle)}")
        body.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="{tokens["grid"]}"/>')
    for index in range(count):
        angle = -math.pi/2 + 2*math.pi*index/count
        x, y = cx+radius*math.cos(angle), cy+radius*math.sin(angle)
        body.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{tokens["grid"]}"/>')
        label = axes[index]["label"] if index < len(axes) else str(index+1)
        body.append(f'<text class="annotation" x="{cx+(radius+34)*math.cos(angle)}" y="{cy+(radius+34)*math.sin(angle)}" text-anchor="middle">{escape(str(label))}</text>')
    for s_index, series in enumerate(ir["series"]):
        points = []
        for index, datum in enumerate(series["data"]):
            axis = axes[index]
            minimum, maximum = float(axis["domain_min"]), float(axis["domain_max"])
            value = minimum if datum["value"] is None else float(datum["value"])
            normalized = 0 if maximum == minimum else (value-minimum)/(maximum-minimum)
            angle = -math.pi/2 + 2*math.pi*index/count
            points.append(f"{cx+radius*normalized*math.cos(angle)},{cy+radius*normalized*math.sin(angle)}")
        body.append(f'<polygon id="{prefix}-{_id(series["id"])}" points="{" ".join(points)}" fill="{tokens["series_1"]}" fill-opacity="0.22" stroke="{tokens["series_1"]}" stroke-width="4"/>')
    body.append(f'<text class="annotation" x="56" y="840">{escape(" · ".join(f"{s["label"]}: " + ", ".join(f"{d["domain"]}={d["value"]}" for d in s["data"]) for s in ir["series"]))}</text>')
    return "".join(body), {}


def _loop(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    nodes = list(ir["nodes"])
    cx, cy, radius = 800, 480, 270
    boxes: dict[str, Rect] = {}
    for index, node in enumerate(nodes):
        angle = -math.pi/2 + 2*math.pi*index/max(1,len(nodes))
        boxes[node["id"]] = Rect(cx+radius*math.cos(angle)-120, cy+radius*math.sin(angle)-52, 240, 104)
    body: list[str] = []
    for edge in ir["edges"]:
        source, target = boxes[edge["source"]], boxes[edge["target"]]
        body.append(f'<path id="{prefix}-{_id(edge["id"])}" d="M{source.center_x},{source.center_y} Q{cx},{cy} {target.center_x},{target.center_y}" fill="none" stroke="{tokens["connector"]}" stroke-width="4" marker-end="url(#{prefix}-arrow)"/>')
    for node in nodes:
        body.append(_node_shape(node, boxes[node["id"]], tokens, prefix))
    body.append(f'<circle cx="{cx}" cy="{cy}" r="76" fill="{tokens["surface_alt"]}" stroke="{tokens["accent"]}" stroke-width="3"/><text class="heading" x="{cx}" y="{cy+7}" text-anchor="middle">Chu trình</text>')
    return "".join(body), boxes


def _nested_or_venn(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str, venn: bool) -> tuple[str, dict[str, Rect]]:
    body: list[str] = []
    boxes: dict[str, Rect] = {}
    groups = list(ir["groups"])
    if venn:
        centers = [(650,470),(940,470),(800,610)]
        for index, group in enumerate(groups):
            cx, cy = centers[index % len(centers)]
            body.append(f'<circle id="{prefix}-{_id(group["id"])}" cx="{cx}" cy="{cy}" r="220" fill="{tokens["accent"]}" fill-opacity="0.13" stroke="{tokens["accent"]}" stroke-width="3"/><text class="heading" x="{cx}" y="{cy-190}" text-anchor="middle">{escape(str(group["label"]))}</text>')
        for index, node in enumerate(ir["nodes"]):
            rect = Rect(680+index*270, 430+index*120, 240, 96); boxes[node["id"]]=rect; body.append(_node_shape(node,rect,tokens,prefix))
    else:
        for index, group in enumerate(groups):
            inset = index * 90
            body.append(f'<rect id="{prefix}-{_id(group["id"])}" x="{180+inset}" y="{180+inset}" width="{1240-2*inset}" height="{560-2*inset}" rx="28" fill="{tokens["surface_alt"]}" fill-opacity="0.35" stroke="{tokens["border"]}" stroke-width="3"/><text class="heading" x="{210+inset}" y="{220+inset}">{escape(str(group["label"]))}</text>')
        for index,node in enumerate(ir["nodes"]):
            rect=Rect(610+index*280,390,250,110);boxes[node["id"]]=rect;body.append(_node_shape(node,rect,tokens,prefix))
    return "".join(body), boxes


def _funnel(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    series = ir["series"][0]
    values = [float(d["value"]) for d in series["data"] if d["value"] is not None]
    maximum = max(values or [1])
    body: list[str] = [f'<text class="heading" x="800" y="154" text-anchor="middle">{escape(str(series["label"]))}</text>']
    y = 190
    for index, datum in enumerate(series["data"]):
        value = 0 if datum["value"] is None else float(datum["value"])
        width = 360 + 760 * (value / maximum)
        x = (WIDTH-width)/2
        points=f"{x},{y} {x+width},{y} {x+width-70},{y+105} {x+70},{y+105}"
        body.append(f'<polygon id="{prefix}-{_id(datum["id"])}" points="{points}" fill="{tokens["series_1"]}" fill-opacity="{0.88-index*0.12}" stroke="{tokens["surface"]}" stroke-width="3"/><text class="node-label" x="800" y="{y+48}" text-anchor="middle">{escape(str(datum["domain"]))}</text><text class="numeric" x="800" y="{y+76}" text-anchor="middle">{escape(str(datum["value"]))} {escape(str(series.get("unit") or ""))}</text>')
        y += 118
    return "".join(body), {}


def _gantt(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    tasks = list(ir["nodes"])
    body: list[str] = []
    boxes: dict[str, Rect] = {}
    for index, task in enumerate(tasks):
        y = 220 + index*150
        body.append(f'<text class="node-label" x="80" y="{y+38}">{escape(str(task["label"]))}</text>')
        rect=Rect(430+index*180,y,520,72);boxes[task["id"]]=rect
        body.append(f'<rect id="{prefix}-{_id(task["id"])}" x="{rect.x}" y="{rect.y}" width="{rect.width}" height="{rect.height}" rx="12" fill="{tokens["series_1"]}"/><text class="node-label" x="{rect.center_x}" y="{rect.center_y+7}" text-anchor="middle">{escape(str(task.get("start","")))} → {escape(str(task.get("end","")))}</text>')
    return "".join(body), boxes


def _matrix(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    cells = list(ir["nodes"])
    identities = [cell.get("secondary_label", "|").split("|",1) for cell in cells]
    rows = sorted({pair[0] for pair in identities}); columns=sorted({pair[1] for pair in identities})
    cell_w,cell_h=260,100;start_x,start_y=420,230
    body: list[str]=[];boxes:dict[str,Rect]={}
    for index,column in enumerate(columns): body.append(f'<text class="heading" x="{start_x+index*cell_w+cell_w/2}" y="190" text-anchor="middle">{escape(column)}</text>')
    for index,row in enumerate(rows): body.append(f'<text class="heading" x="100" y="{start_y+index*cell_h+60}">{escape(row)}</text>')
    state_tokens={"allow":tokens["success"],"deny":tokens["danger"],"conditional":tokens["series_2"],"unknown":tokens["muted"]}
    for cell,pair in zip(cells,identities):
        rect=Rect(start_x+columns.index(pair[1])*cell_w,start_y+rows.index(pair[0])*cell_h,cell_w-8,cell_h-8);boxes[cell["id"]]=rect
        state=cell.get("state","unknown");color=state_tokens.get(state,tokens["muted"]);hatch=f' fill="url(#{prefix}-hatch)"' if state in {"conditional","unknown"} else f' fill="{color}" fill-opacity="0.16"'
        body.append(f'<rect id="{prefix}-{_id(cell["id"])}" x="{rect.x}" y="{rect.y}" width="{rect.width}" height="{rect.height}" rx="10"{hatch} stroke="{color}" stroke-width="3"/><text class="node-label" x="{rect.center_x}" y="{rect.center_y-6}" text-anchor="middle">{escape(str(cell["label"]))}</text><text class="annotation" x="{rect.center_x}" y="{rect.center_y+24}" text-anchor="middle">{escape(state.upper())}</text>')
    body.append(f'<text class="annotation" x="80" y="820">{escape(" · ".join(f"{pair[0]}/{pair[1]}={cell.get('state','unknown')}" for cell,pair in zip(cells,identities)))}</text>')
    return "".join(body), boxes


def _render_body(ir: Mapping[str, Any], tokens: Mapping[str, str], prefix: str) -> tuple[str, dict[str, Rect]]:
    diagram_type = ir["diagram"]["type"]
    if diagram_type == "sequence": return _sequence(ir,tokens,prefix)
    if diagram_type == "timeline": return _timeline(ir,tokens,prefix)
    if diagram_type in {"swimlane","layer-stack","medallion","process"} and ir["lanes"]: return _lanes(ir,tokens,prefix)
    if diagram_type in {"bar-chart","line-chart","scatter-plot","quadrant"}: return _cartesian(ir,tokens,prefix,diagram_type)
    if diagram_type == "radar": return _radar(ir,tokens,prefix)
    if diagram_type == "loop-flywheel": return _loop(ir,tokens,prefix)
    if diagram_type in {"nested","venn"}: return _nested_or_venn(ir,tokens,prefix,diagram_type=="venn")
    if diagram_type == "pyramid-funnel": return _funnel(ir,tokens,prefix)
    if diagram_type == "gantt": return _gantt(ir,tokens,prefix)
    if diagram_type == "dp-security-matrix": return _matrix(ir,tokens,prefix)
    return _generic_graph(ir,tokens,prefix,1 if "CAP-V10" in ir["diagram"].get("variant_ids", []) else None)


def _validate_svg(svg: str, boxes: Mapping[str, Rect], ir: Mapping[str, Any]) -> dict[str, Any]:
    try: ET.fromstring(svg)
    except ET.ParseError as error: raise VisualError("svg-invalid", f"Generated SVG is invalid: {error}.") from error
    lowered=svg.lower().replace('xmlns="http://www.w3.org/2000/svg"',"")
    if any(token in lowered for token in ("<script","http://","https://","file://","javascript:","onload=","onclick=")):
        raise VisualError("svg-unsafe", "Generated SVG contains executable or external content.")
    ids=re.findall(r'\bid="([^"]+)"',svg)
    if len(ids)!=len(set(ids)): raise VisualError("duplicate-svg-id","Generated SVG IDs must be unique.")
    for node_id,rect in boxes.items():
        if rect.left<32 or rect.top<120 or rect.right>WIDTH-32 or rect.bottom>HEIGHT-32: raise VisualError("node-out-of-bounds",f"Node {node_id} is outside the canvas.")
    items=list(boxes.items())
    for index,(first_id,first) in enumerate(items):
        for second_id,second in items[index+1:]:
            if rects_overlap(first,second,4): raise VisualError("node-overlap",f"Nodes {first_id} and {second_id} overlap.")
    rendered_text=" ".join(ET.fromstring(svg).itertext())
    material=[str(item.get("label",item.get("text",""))) for collection in ("nodes","groups","lanes","series","axes","annotations") for item in ir[collection]]
    missing=[label for label in material if label and label not in rendered_text]
    if missing: raise VisualError("material-label-missing",f"Material label is missing from SVG: {missing[0]}.")
    return {"status":"pass","self_contained":True,"unique_ids":len(ids),"node_count":len(boxes),"material_labels":len(material)}


def render_static(ir_value: Mapping[str, Any], mode: str = "neutral-light", *, coverage_badge: bool = True) -> CoverageRender:
    ir=validate_semantics(ir_value)
    if ir["diagram"]["type"] not in CANONICAL_TYPES: raise VisualError("type-unsupported","Type is outside the canonical inventory.")
    system=load_visual_system();validate_contrast(system)
    if mode not in system["modes"]: raise VisualError("mode-unsupported","Mode is outside the approved three-mode system.")
    tokens=system["modes"][mode];prefix=_id(f"p07-{ir['diagram']['type']}-{mode}")
    body,boxes=_render_body(ir,tokens,prefix)
    variants=set(ir["diagram"].get("variant_ids",[]))
    if "CAP-V12" in variants:
        body=f'<rect x="42" y="132" width="1516" height="718" rx="26" fill="url(#{prefix}-hatch)" opacity="0.08"/>'+body
    if "CAP-V13" in variants:
        body+=f'<rect x="560" y="782" width="480" height="54" rx="12" fill="{tokens["surface"]}" stroke="{tokens["accent"]}" stroke-width="3"/><text class="annotation" x="800" y="816" text-anchor="middle">Terminal frame · complete static state</text>'
    for index,annotation in enumerate(ir["annotations"]):
        body+=f'<text class="annotation" x="56" y="{860-index*24}">{escape(str(annotation["text"]))}</text>'
    description=f"Static {ir['diagram']['type']} visual preserving {len(ir['nodes'])} nodes, {len(ir['edges'])} edges, and {len(ir['series'])} quantitative series."
    svg=_shell(ir["diagram"]["type"],mode,ir["diagram"]["title"],description,body,tokens,coverage_badge)
    validation=_validate_svg(svg,boxes,ir)
    return CoverageRender(ir["diagram"]["type"],mode,svg,boxes,{**validation,"renderer_version":RENDERER_VERSION,"ir_hash":hashlib.sha256(canonical_json(ir).encode()).hexdigest()})


__all__=["CoverageRender","RENDERER_VERSION","render_static"]
