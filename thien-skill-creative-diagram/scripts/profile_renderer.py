"""Deterministic target-v2.1 renderer for the 45 structural profiles.

The renderer consumes validated semantic IR plus a pre-render profile plan.  It
dispatches to exactly one of the canonical 14 layout engines, emits an SVG
whose geometry carries the semantic IDs, and validates the resulting geometry
before the output pipeline is allowed to write it.  It never reads approved
sample bytes and has no generic-card fallback.
"""

from __future__ import annotations

import hashlib
import heapq
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Callable, Mapping, Sequence

from diagram_core import canonical_json
from semantic_grammars import derive_ridgeline_profiles
from structural_profiles import artifact_binding_attributes


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
RENDERER_VERSION = "profile-renderer-2.1.0"
GEOMETRY_DECIMALS = 2
GEOMETRY_TOLERANCE = 0.02
CANVAS_PRESETS = {
    "doc-inline": (960, 720), "doc-wide": (1440, 900),
    "slide-16x9": (1600, 900), "slide-4x3": (1600, 1200),
    "social-og": (1200, 630), "social-square": (1080, 1080),
    "print-a4-landscape": (1600, 1131), "print-letter-landscape": (1600, 1236),
    "fit": (1600, 1600),
}
ENGINE_PRIMITIVES = {
    "topology-and-zones": "zone-boundary",
    "integration-pipeline": "pipeline-stage",
    "runtime-deployment": "deployment-zone",
    "dependency-dag": "dag-rank",
    "directed-flow-state": "flow-rank",
    "lane-interaction": "interaction-lane",
    "time-planning": "time-rail",
    "work-experience": "work-column",
    "hierarchy": "hierarchy-rank",
    "containment-stack": "containment-layer",
    "compartment-model": "compartment-node",
    "spatial-matrix": "spatial-field",
    "quantitative": "plot-frame",
    "special-geometry": "special-spine",
}


class ProfileRenderError(ValueError):
    """Fail-closed renderer or geometry error with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass(frozen=True)
class Route:
    edge_id: str
    source: str
    target: str
    points: tuple[tuple[float, float], ...]
    directed: bool
    family: str = "orthogonal"
    label: str = ""
    crossings: tuple[tuple[float, float], ...] = ()
    source_member: str | None = None
    target_member: str | None = None


@dataclass
class Layout:
    boxes: dict[str, Box] = field(default_factory=dict)
    routes: list[Route] = field(default_factory=list)
    emitted_ids: set[str] = field(default_factory=set)


THEMES = {
    "neutral-light": {"bg": "#F6F7F9", "panel": "#FFFFFF", "ink": "#18212F", "muted": "#5D6978", "line": "#334155", "soft": "#D9E0E8", "accent": "#2563EB", "accent2": "#0F766E", "warn": "#B45309"},
    "neutral-dark": {"bg": "#10151C", "panel": "#17202B", "ink": "#F2F5F8", "muted": "#AEB9C7", "line": "#CBD5E1", "soft": "#344255", "accent": "#60A5FA", "accent2": "#5EEAD4", "warn": "#FBBF24"},
    "editorial": {"bg": "#F4EFE6", "panel": "#FFFDF8", "ink": "#241F1A", "muted": "#6C6258", "line": "#453D34", "soft": "#D8CCBB", "accent": "#A23E2A", "accent2": "#315C56", "warn": "#9A6700"},
}


def _tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def _fmt(value: float) -> str:
    return f"{value:.{GEOMETRY_DECIMALS}f}".rstrip("0").rstrip(".")


def _quantize_point(point: tuple[float, float]) -> tuple[float, float]:
    """Use the exact coordinate lattice serialized into the SVG artifact."""

    return tuple(round(value, GEOMETRY_DECIMALS) for value in point)  # type: ignore[return-value]


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.:-]+", "-", value)


def _ordered(items: Sequence[Mapping[str, Any]], field_name: str = "order") -> list[Mapping[str, Any]]:
    return sorted(items, key=lambda item: (item.get(field_name, 10**9), str(item.get("id", ""))))


def _wrap(text: Any, limit: int = 24) -> list[str]:
    words = str(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    line = words[0]
    for word in words[1:]:
        if len(line) + 1 + len(word) <= limit:
            line += " " + word
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines[:4]


class SvgBuilder:
    def __init__(self, width: int, height: int, mode: str, title: str, binding: Mapping[str, Any]) -> None:
        self.width, self.height = width, height
        self.theme = THEMES[mode]
        attrs = {
            "viewBox": f"0 0 {width} {height}", "width": str(width), "height": str(height),
            "preserveAspectRatio": "xMidYMid meet",
            "role": "img", "aria-labelledby": "diagram-title diagram-description",
            "data-renderer-version": RENDERER_VERSION,
            "data-geometry-contract": "profile-renderer-v1",
            **artifact_binding_attributes(binding),
        }
        self.root = ET.Element(_tag("svg"), attrs)
        ET.SubElement(self.root, _tag("title"), {"id": "diagram-title"}).text = title
        ET.SubElement(self.root, _tag("desc"), {"id": "diagram-description"}).text = (
            f"{binding['selected_profile']} rendered by {binding['layout_engine']} with semantic IDs and validated geometry."
        )
        defs = ET.SubElement(self.root, _tag("defs"))
        marker = ET.SubElement(defs, _tag("marker"), {"id": "arrow", "markerWidth": "10", "markerHeight": "8", "refX": "9", "refY": "4", "orient": "auto", "markerUnits": "strokeWidth"})
        ET.SubElement(marker, _tag("path"), {"d": "M0,0 L10,4 L0,8 Z", "fill": self.theme["line"]})
        ET.SubElement(self.root, _tag("rect"), {"x": "0", "y": "0", "width": str(width), "height": str(height), "fill": self.theme["bg"]})
        self.text(title, 64, 62, size=30, weight="700")

    def element(self, name: str, attrs: Mapping[str, Any], parent: ET.Element | None = None) -> ET.Element:
        clean = {key: _fmt(value) if isinstance(value, float) else str(value) for key, value in attrs.items() if value is not None}
        return ET.SubElement(self.root if parent is None else parent, _tag(name), clean)

    def text(self, value: Any, x: float, y: float, *, size: int = 16, weight: str = "500", fill: str | None = None, anchor: str = "start", parent: ET.Element | None = None) -> ET.Element:
        item = self.element("text", {"x": x, "y": y, "font-family": "Inter, Noto Sans, Arial, Helvetica Neue, system-ui, sans-serif", "font-size": size, "font-weight": weight, "fill": fill or self.theme["ink"], "text-anchor": anchor}, parent)
        item.text = str(value)
        return item

    def primitive(
        self,
        primitive: str,
        box: Box,
        *,
        label: str = "",
        semantic_id: str | None = None,
        fill: str | None = None,
        radius: float = 16,
        member_ids: Sequence[str] = (),
        semantic_group: bool = False,
        presentation_shell: str | None = None,
    ) -> ET.Element:
        if semantic_group and (not semantic_id or presentation_shell):
            raise ProfileRenderError("renderer-group-receipt-invalid", "A semantic group needs one exact semantic ID and cannot also be a presentation shell.")
        attrs: dict[str, Any] = {"data-primitive": primitive, "data-x": box.x, "data-y": box.y, "data-w": box.w, "data-h": box.h}
        if semantic_id:
            attrs["data-semantic-id"] = semantic_id
        if member_ids:
            attrs["data-member-ids"] = " ".join(member_ids)
        if semantic_group:
            attrs["data-semantic-group-id"] = semantic_id
        if presentation_shell:
            attrs["data-presentation-shell"] = presentation_shell
        group = self.element("g", attrs)
        self.element("rect", {"x": box.x, "y": box.y, "width": box.w, "height": box.h, "rx": radius, "fill": fill or self.theme["panel"], "stroke": self.theme["soft"], "stroke-width": 2}, group)
        if label:
            self.text(label, box.x + 18, box.y + 28, size=14, weight="700", fill=self.theme["muted"], parent=group)
        return group

    def node(self, node: Mapping[str, Any], box: Box, layout: Layout, *, shape: str = "card", subtitle: str | None = None) -> None:
        node_id = str(node["id"])
        attrs: dict[str, Any] = {"id": f"node-{_safe_id(node_id)}", "data-node-id": node_id, "data-role": node.get("role", "item"), "data-x": box.x, "data-y": box.y, "data-w": box.w, "data-h": box.h}
        placement = node.get("placement")
        if isinstance(placement, Mapping):
            for field_name in ("zone", "host", "artifact", "replicas"):
                if placement.get(field_name) is not None:
                    attrs[f"data-placement-{field_name}"] = placement[field_name]
            attrs["data-placement-ports"] = " ".join(str(port) for port in placement.get("ports", ()))
        for field_name in ("start", "end"):
            if node.get(field_name) is not None:
                attrs[f"data-{field_name}"] = node[field_name]
        journey = node.get("journey")
        if isinstance(journey, Mapping):
            for field_name in ("stage_order", "action", "touchpoint", "sentiment"):
                if journey.get(field_name) is not None:
                    attrs[f"data-journey-{field_name.replace('_', '-')}"] = journey[field_name]
        group = self.element("g", attrs)
        if shape == "decision":
            points = f"{_fmt(box.cx)},{_fmt(box.y)} {_fmt(box.x + box.w)},{_fmt(box.cy)} {_fmt(box.cx)},{_fmt(box.y + box.h)} {_fmt(box.x)},{_fmt(box.cy)}"
            self.element("polygon", {"points": points, "fill": self.theme["panel"], "stroke": self.theme["accent"], "stroke-width": 3}, group)
        elif shape in {"start", "terminal", "initial"}:
            self.element("ellipse", {"cx": box.cx, "cy": box.cy, "rx": box.w / 2, "ry": box.h / 2, "fill": self.theme["panel"], "stroke": self.theme["accent2"], "stroke-width": 3}, group)
        elif shape == "artifact":
            self.element("path", {"d": f"M{_fmt(box.x)},{_fmt(box.y)} H{_fmt(box.x + box.w - 24)} L{_fmt(box.x + box.w)},{_fmt(box.y + 24)} V{_fmt(box.y + box.h)} H{_fmt(box.x)} Z", "fill": self.theme["panel"], "stroke": self.theme["accent2"], "stroke-width": 2}, group)
        else:
            self.element("rect", {"x": box.x, "y": box.y, "width": box.w, "height": box.h, "rx": 16, "fill": self.theme["panel"], "stroke": self.theme["accent"] if node.get("state") else self.theme["soft"], "stroke-width": 2}, group)
        lines = _wrap(node.get("label", node_id), max(10, int(box.w / 10)))
        top = box.cy - (len(lines) - 1) * 10
        for index, line in enumerate(lines):
            self.text(line, box.cx, top + index * 20, size=15, weight="650", anchor="middle", parent=group)
        if subtitle:
            self.text(subtitle, box.cx, box.y + box.h - 14, size=11, fill=self.theme["muted"], anchor="middle", parent=group)
        layout.boxes[node_id] = box
        layout.emitted_ids.add(node_id)

    def route(self, route: Route) -> None:
        attrs: dict[str, Any] = {
            "id": f"edge-{_safe_id(route.edge_id)}", "data-edge-id": route.edge_id,
            "data-source": route.source, "data-target": route.target, "data-route-family": route.family,
            "points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in route.points),
            "fill": "none", "stroke": self.theme["line"], "stroke-width": 2.5,
            "stroke-linejoin": "round", "stroke-linecap": "round",
        }
        if route.source_member:
            attrs["data-source-member"] = route.source_member
        if route.target_member:
            attrs["data-target-member"] = route.target_member
        if route.crossings:
            attrs["data-crossing-points"] = ";".join(f"{_fmt(x)},{_fmt(y)}" for x, y in route.crossings)
        if route.directed:
            attrs["marker-end"] = "url(#arrow)"
        if route.family == "ribbon":
            attrs["stroke-width"] = "12"
            attrs["stroke-opacity"] = "0.55"
        self.element("polyline", attrs)
        if route.label:
            mid = route.points[len(route.points) // 2]
            self.text(route.label, mid[0] + 8, mid[1] - 8, size=12, fill=self.theme["muted"])

    def crossing_bridge(self, route: Route, point: tuple[float, float]) -> None:
        """Draw an explicit visual overpass for a declared non-junction crossing."""

        segment = next(
            ((start, end) for start, end in zip(route.points, route.points[1:]) if _point_on_segment(point, start, end, interior=True)),
            None,
        )
        if segment is None:
            return
        (x1, y1), (x2, y2) = segment
        length = math.hypot(x2 - x1, y2 - y1)
        if length <= 1e-9:
            return
        unit_x, unit_y = (x2 - x1) / length, (y2 - y1) / length
        self.element("circle", {"cx": point[0], "cy": point[1], "r": 7, "fill": self.theme["bg"], "data-crossing-bridge": route.edge_id})
        self.element("line", {
            "x1": point[0] - unit_x * 8,
            "y1": point[1] - unit_y * 8,
            "x2": point[0] + unit_x * 8,
            "y2": point[1] + unit_y * 8,
            "stroke": self.theme["line"],
            "stroke-width": 2.5,
            "stroke-linecap": "round",
            "data-crossing-bridge-stroke": route.edge_id,
            "data-crossing-x": point[0],
            "data-crossing-y": point[1],
        })

    def finish(self) -> str:
        return ET.tostring(self.root, encoding="unicode", short_empty_elements=True)


def _segment_hits_box(start: tuple[float, float], end: tuple[float, float], box: Box, *, margin: float = 1.0) -> bool:
    x1, y1 = start
    x2, y2 = end
    minimum_x, maximum_x = box.x + margin, box.x + box.w - margin
    minimum_y, maximum_y = box.y + margin, box.y + box.h - margin
    if minimum_x >= maximum_x or minimum_y >= maximum_y:
        return False
    delta_x, delta_y = x2 - x1, y2 - y1
    lower, upper = 0.0, 1.0
    for coefficient, distance in (
        (-delta_x, x1 - minimum_x),
        (delta_x, maximum_x - x1),
        (-delta_y, y1 - minimum_y),
        (delta_y, maximum_y - y1),
    ):
        if abs(coefficient) < 1e-9:
            if distance < 0:
                return False
            continue
        ratio = distance / coefficient
        if coefficient < 0:
            lower = max(lower, ratio)
        else:
            upper = min(upper, ratio)
        if lower > upper:
            return False
    midpoint = (max(0.0, lower) + min(1.0, upper)) / 2
    x = x1 + midpoint * delta_x
    y = y1 + midpoint * delta_y
    return minimum_x < x < maximum_x and minimum_y < y < maximum_y


def _point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    interior: bool = False,
    tolerance: float = GEOMETRY_TOLERANCE,
) -> bool:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    delta_x, delta_y = x2 - x1, y2 - y1
    length = math.hypot(delta_x, delta_y)
    if length <= tolerance:
        return not interior and math.hypot(x - x1, y - y1) <= tolerance
    perpendicular_distance = abs(delta_x * (y - y1) - delta_y * (x - x1)) / length
    if perpendicular_distance > tolerance:
        return False
    parameter = ((x - x1) * delta_x + (y - y1) * delta_y) / (length * length)
    parameter_tolerance = tolerance / length
    if interior:
        return parameter_tolerance < parameter < 1.0 - parameter_tolerance
    return -parameter_tolerance <= parameter <= 1.0 + parameter_tolerance


def _boundary_side(point: tuple[float, float], box: Box, tolerance: float = 1.1) -> str:
    x, y = point
    candidates = {
        "left": abs(x - box.x),
        "right": abs(x - box.x - box.w),
        "top": abs(y - box.y),
        "bottom": abs(y - box.y - box.h),
    }
    side = min(candidates, key=candidates.get)  # type: ignore[arg-type]
    if candidates[side] > tolerance:
        raise ProfileRenderError("renderer-port-detached", "Route endpoint is not attached to a node boundary.")
    return side


def _spread_terminal_ports(routes: Sequence[Route], boxes: Mapping[str, Box]) -> list[Route]:
    """Allocate distinct boundary ports for fan-in and fan-out before routing QA."""

    mutable = [list(route.points) for route in routes]
    endpoints: dict[tuple[str, str], list[tuple[int, str, str]]] = {}
    for route_index, route in enumerate(routes):
        if route.family not in {"orthogonal", "ribbon", "fishbone"} or len(route.points) < 2:
            continue
        for endpoint_kind, node_id, point in (
            ("source", route.source, route.points[0]),
            ("target", route.target, route.points[-1]),
        ):
            if node_id not in boxes:
                continue
            side = _boundary_side(point, boxes[node_id])
            endpoints.setdefault((node_id, side), []).append((route_index, endpoint_kind, route.edge_id))
    for (node_id, side), members in endpoints.items():
        if len(members) < 2:
            continue
        box = boxes[node_id]
        horizontal_side = side in {"left", "right"}
        members.sort(
            key=lambda item: (
                boxes[routes[item[0]].source if item[1] == "target" else routes[item[0]].target].cy if horizontal_side else boxes[routes[item[0]].source if item[1] == "target" else routes[item[0]].target].cx,
                item[1],
                item[2],
            )
        )
        for slot_index, (route_index, endpoint_kind, _edge_id) in enumerate(members):
            points = mutable[route_index]
            coordinate = (
                box.y + box.h * (slot_index + 1) / (len(members) + 1)
                if horizontal_side
                else box.x + box.w * (slot_index + 1) / (len(members) + 1)
            )
            point_index = 0 if endpoint_kind == "source" else len(points) - 1
            adjacent_index = 1 if endpoint_kind == "source" else len(points) - 2
            x, y = points[point_index]
            adjacent_x, adjacent_y = points[adjacent_index]
            if horizontal_side:
                points[point_index] = (x, coordinate)
                points[adjacent_index] = (adjacent_x, coordinate)
            else:
                points[point_index] = (coordinate, y)
                points[adjacent_index] = (coordinate, adjacent_y)
    return [replace(route, points=tuple(mutable[index])) for index, route in enumerate(routes)]


def _collinear_overlap(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
    tolerance: float = 1e-6,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    vector = (first_end[0] - first_start[0], first_end[1] - first_start[1])
    other = (second_end[0] - second_start[0], second_end[1] - second_start[1])
    offset = (second_start[0] - first_start[0], second_start[1] - first_start[1])
    cross = vector[0] * other[1] - vector[1] * other[0]
    offset_cross = offset[0] * vector[1] - offset[1] * vector[0]
    length_squared = vector[0] ** 2 + vector[1] ** 2
    if abs(cross) > tolerance or abs(offset_cross) > tolerance or length_squared <= tolerance:
        return None
    parameters = [
        (offset[0] * vector[0] + offset[1] * vector[1]) / length_squared,
        ((second_end[0] - first_start[0]) * vector[0] + (second_end[1] - first_start[1]) * vector[1]) / length_squared,
    ]
    lower = max(0.0, min(parameters))
    upper = min(1.0, max(parameters))
    if (upper - lower) * math.sqrt(length_squared) > tolerance:
        return (
            (round(first_start[0] + lower * vector[0], 3), round(first_start[1] + lower * vector[1], 3)),
            (round(first_start[0] + upper * vector[0], 3), round(first_start[1] + upper * vector[1], 3)),
        )
    return None


def _segment_intersection(
    first_start: tuple[float, float],
    first_end: tuple[float, float],
    second_start: tuple[float, float],
    second_end: tuple[float, float],
    tolerance: float = 1e-6,
) -> tuple[float, float] | None:
    first = (first_end[0] - first_start[0], first_end[1] - first_start[1])
    second = (second_end[0] - second_start[0], second_end[1] - second_start[1])
    offset = (second_start[0] - first_start[0], second_start[1] - first_start[1])
    denominator = first[0] * second[1] - first[1] * second[0]
    if abs(denominator) <= tolerance:
        return None
    first_parameter = (offset[0] * second[1] - offset[1] * second[0]) / denominator
    second_parameter = (offset[0] * first[1] - offset[1] * first[0]) / denominator
    if -tolerance <= first_parameter <= 1 + tolerance and -tolerance <= second_parameter <= 1 + tolerance:
        return _quantize_point((
            first_start[0] + first_parameter * first[0],
            first_start[1] + first_parameter * first[1],
        ))
    return None


def _route_point_is_internal(point: tuple[float, float], points: Sequence[tuple[float, float]]) -> bool:
    """Return whether a contact belongs to a route but is not a semantic terminal."""

    if len(points) < 2 or _point_on_segment(point, points[0], points[0]) or _point_on_segment(point, points[-1], points[-1]):
        return False
    return any(_point_on_segment(point, start, end) for start, end in zip(points, points[1:]))


def _route_has_node_obstruction(route: Route, boxes: Mapping[str, Box]) -> bool:
    return any(
        _segment_hits_box(start, end, box)
        for start, end in zip(route.points, route.points[1:])
        for box in boxes.values()
    )


def _routes_have_forbidden_contact(left: Route, right: Route) -> bool:
    """Reject shared tracks and ambiguous contacts while allowing drawable overpasses."""

    contacts: dict[tuple[float, float], tuple[bool, bool]] = {}
    for left_segment in zip(left.points, left.points[1:]):
        for right_segment in zip(right.points, right.points[1:]):
            if _collinear_overlap(*left_segment, *right_segment):
                return True
            point = _segment_intersection(*left_segment, *right_segment)
            if point is None:
                continue
            previous = contacts.get(point, (False, False))
            contacts[point] = (
                previous[0] or _point_on_segment(point, *left_segment, interior=True),
                previous[1] or _point_on_segment(point, *right_segment, interior=True),
            )
    return any(
        not (
            _route_point_is_internal(point, left.points)
            and _route_point_is_internal(point, right.points)
            and (left_segment_interior or right_segment_interior)
        )
        for point, (left_segment_interior, right_segment_interior) in contacts.items()
    )


def _segment_route_crossing_penalty(
    start: tuple[float, float],
    end: tuple[float, float],
    occupied: Sequence[Route],
    route_start: tuple[float, float],
    route_end: tuple[float, float],
) -> float | None:
    """Score proper crossings and reject overlaps or segment-level T contacts."""

    penalty = 0.0
    for route in occupied:
        for other_start, other_end in zip(route.points, route.points[1:]):
            if _collinear_overlap(start, end, other_start, other_end):
                return None
            point = _segment_intersection(start, end, other_start, other_end)
            if point is None:
                continue
            candidate_segment_interior = _point_on_segment(point, start, end, interior=True)
            occupied_segment_interior = _point_on_segment(point, other_start, other_end, interior=True)
            candidate_route_internal = not (
                _point_on_segment(point, route_start, route_start)
                or _point_on_segment(point, route_end, route_end)
            )
            if not (
                candidate_route_internal
                and _route_point_is_internal(point, route.points)
                and (candidate_segment_interior or occupied_segment_interior)
            ):
                return None
            penalty += 24.0
    return penalty


def _orthogonal_detour(route: Route, boxes: Mapping[str, Box], occupied: Sequence[Route]) -> Route:
    """Find a deterministic rectilinear path around nodes and accepted routes."""

    clearance = 18.0
    route_start, route_end = route.points[0], route.points[-1]

    def outward_stub(point: tuple[float, float], node_id: str) -> tuple[float, float]:
        side = _boundary_side(point, boxes[node_id])
        unit = {
            "left": (-1.0, 0.0),
            "right": (1.0, 0.0),
            "top": (0.0, -1.0),
            "bottom": (0.0, 1.0),
        }[side]
        for distance in (18.0, 36.0, 54.0, 72.0, 90.0, 108.0, 126.0, 144.0, 12.0, 6.0):
            candidate = _quantize_point((point[0] + unit[0] * distance, point[1] + unit[1] * distance))
            if any(_segment_hits_box(point, candidate, box) for box in boxes.values()):
                continue
            if _segment_route_crossing_penalty(point, candidate, occupied, route_start, route_end) is not None:
                return candidate
        raise ProfileRenderError("renderer-route-obstruction", f"Edge {route.edge_id} cannot allocate a clear terminal stub at {node_id}.")

    start = outward_stub(route_start, route.source)
    end = outward_stub(route_end, route.target)
    x_values = {start[0], end[0]}
    y_values = {start[1], end[1]}
    for box in boxes.values():
        x_values.update((box.x - clearance, box.x, box.x + box.w, box.x + box.w + clearance))
        y_values.update((box.y - clearance, box.y, box.y + box.h, box.y + box.h + clearance))
    for accepted in occupied:
        for x, y in accepted.points:
            x_values.update((x - clearance, x + clearance))
            y_values.update((y - clearance, y + clearance))
    if boxes:
        x_values.update((min(box.x for box in boxes.values()) - clearance * 2, max(box.x + box.w for box in boxes.values()) + clearance * 2))
        y_values.update((min(box.y for box in boxes.values()) - clearance * 2, max(box.y + box.h for box in boxes.values()) + clearance * 2))
    xs = sorted(_quantize_point((value, 0.0))[0] for value in x_values)
    ys = sorted(_quantize_point((0.0, value))[1] for value in y_values)

    def point_is_available(point: tuple[float, float]) -> bool:
        if point in {start, end}:
            return True
        return not any(box.x < point[0] < box.x + box.w and box.y < point[1] < box.y + box.h for box in boxes.values())

    def segment_cost(first: tuple[float, float], second: tuple[float, float]) -> float | None:
        if any(_segment_hits_box(first, second, box) for box in boxes.values()):
            return None
        crossing_penalty = _segment_route_crossing_penalty(first, second, occupied, route_start, route_end)
        if crossing_penalty is None:
            return None
        return math.dist(first, second) + crossing_penalty

    points = {(x, y) for x in xs for y in ys if point_is_available((x, y))}
    points.update((start, end))
    by_y = {y: sorted(point for point in points if point[1] == y) for y in ys}
    by_x = {x: sorted((point for point in points if point[0] == x), key=lambda point: point[1]) for x in xs}
    neighbors: dict[tuple[float, float], list[tuple[tuple[float, float], str, float]]] = {point: [] for point in points}
    for members in by_y.values():
        for first, second in zip(members, members[1:]):
            cost = segment_cost(first, second)
            if cost is not None:
                neighbors[first].append((second, "h", cost))
                neighbors[second].append((first, "h", cost))
    for members in by_x.values():
        for first, second in zip(members, members[1:]):
            cost = segment_cost(first, second)
            if cost is not None:
                neighbors[first].append((second, "v", cost))
                neighbors[second].append((first, "v", cost))

    initial = (start, "")
    distances = {initial: 0.0}
    previous: dict[tuple[tuple[float, float], str], tuple[tuple[float, float], str]] = {}
    queue: list[tuple[float, tuple[float, float], str]] = [(0.0, start, "")]
    final_state: tuple[tuple[float, float], str] | None = None
    while queue:
        cost, point, incoming_direction = heapq.heappop(queue)
        state = (point, incoming_direction)
        if cost > distances.get(state, math.inf) + 1e-9:
            continue
        if point == end:
            final_state = state
            break
        for neighbor, direction, edge_cost in sorted(neighbors[point], key=lambda item: (item[0], item[1])):
            bend_cost = 18.0 if incoming_direction and incoming_direction != direction else 0.0
            candidate_cost = cost + edge_cost + bend_cost
            candidate_state = (neighbor, direction)
            if candidate_cost + 1e-9 >= distances.get(candidate_state, math.inf):
                continue
            distances[candidate_state] = candidate_cost
            previous[candidate_state] = state
            heapq.heappush(queue, (candidate_cost, neighbor, direction))
    if final_state is None:
        raise ProfileRenderError("renderer-route-obstruction", f"Edge {route.edge_id} has no unobstructed deterministic orthogonal route.")

    reversed_points = [final_state[0]]
    state = final_state
    while state != initial:
        state = previous[state]
        reversed_points.append(state[0])
    raw_points = [route_start, *reversed(reversed_points), route_end]
    compact: list[tuple[float, float]] = []
    for point in raw_points:
        if len(compact) >= 2:
            previous_point, last = compact[-2], compact[-1]
            if (previous_point[0] == last[0] == point[0]) or (previous_point[1] == last[1] == point[1]):
                compact[-1] = point
                continue
        compact.append(point)
    return replace(route, points=tuple(compact), crossings=())


def _resolve_route_conflicts(routes: Sequence[Route], boxes: Mapping[str, Box]) -> list[Route]:
    """Preserve clear paths and reroute only connectors with a concrete conflict."""

    accepted: list[Route] = []
    for route in routes:
        candidate = route
        if route.family in {"orthogonal", "ribbon"} and (
            _route_has_node_obstruction(route, boxes)
            or any(_routes_have_forbidden_contact(route, other) for other in accepted)
        ):
            try:
                candidate = _orthogonal_detour(route, boxes, accepted)
            except ProfileRenderError:
                # Existing routes can partition the visibility grid even when a
                # node-clear path only forms drawable overpasses. Recompute
                # without route tracks, then accept it only after the same
                # fail-closed pairwise contact check.
                candidate = _orthogonal_detour(route, boxes, ())
                conflicts = [other.edge_id for other in accepted if _routes_have_forbidden_contact(candidate, other)]
                if conflicts:
                    raise ProfileRenderError(
                        "renderer-route-obstruction",
                        f"Edge {route.edge_id} has no unobstructed deterministic route clear of {', '.join(conflicts)}.",
                    )
        accepted.append(candidate)
    return accepted


def _stagger_shared_trunks(routes: Sequence[Route]) -> list[Route]:
    """Move coincident standard Manhattan trunks onto deterministic parallel tracks."""

    mutable = [list(route.points) for route in routes]
    eligible = [
        index for index, route in enumerate(routes)
        if route.family in {"orthogonal", "ribbon"} and len(route.points) == 4
    ]
    adjacency: dict[int, set[int]] = {index: set() for index in eligible}
    for position, left_index in enumerate(eligible):
        left = mutable[left_index]
        for right_index in eligible[position + 1:]:
            right = mutable[right_index]
            if _collinear_overlap(left[1], left[2], right[1], right[2]):
                adjacency[left_index].add(right_index)
                adjacency[right_index].add(left_index)
    visited: set[int] = set()
    for seed in eligible:
        if seed in visited or not adjacency[seed]:
            continue
        stack = [seed]
        component: list[int] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(adjacency[current] - visited)
        component.sort(key=lambda index: routes[index].edge_id)
        base_x = sum(mutable[index][1][0] for index in component) / len(component)
        base_y = sum(mutable[index][1][1] for index in component) / len(component)
        vertical = all(abs(mutable[index][1][0] - mutable[index][2][0]) < 1e-6 for index in component)
        for rank, route_index in enumerate(component):
            offset = (rank - (len(component) - 1) / 2) * 12.0
            if vertical:
                mutable[route_index][1] = (base_x + offset, mutable[route_index][1][1])
                mutable[route_index][2] = (base_x + offset, mutable[route_index][2][1])
            else:
                mutable[route_index][1] = (mutable[route_index][1][0], base_y + offset)
                mutable[route_index][2] = (mutable[route_index][2][0], base_y + offset)
    return [replace(route, points=tuple(mutable[index])) for index, route in enumerate(routes)]


def _declare_proper_crossings(routes: Sequence[Route]) -> list[Route]:
    """Declare visual overpasses, including contacts at nonterminal route vertices."""

    crossings: dict[int, set[tuple[float, float]]] = {index: set() for index in range(len(routes))}
    for left_index, left in enumerate(routes):
        if left.family not in {"orthogonal", "ribbon", "message", "fishbone"}:
            continue
        for right_index in range(left_index + 1, len(routes)):
            right = routes[right_index]
            if right.family not in {"orthogonal", "ribbon", "message", "fishbone"}:
                continue
            for left_segment in zip(left.points, left.points[1:]):
                for right_segment in zip(right.points, right.points[1:]):
                    if _collinear_overlap(*left_segment, *right_segment):
                        continue
                    point = _segment_intersection(*left_segment, *right_segment)
                    if point is None:
                        continue
                    left_segment_interior = _point_on_segment(point, *left_segment, interior=True)
                    right_segment_interior = _point_on_segment(point, *right_segment, interior=True)
                    if (
                        _route_point_is_internal(point, left.points)
                        and _route_point_is_internal(point, right.points)
                        and (left_segment_interior or right_segment_interior)
                    ):
                        eligible = []
                        if left_segment_interior:
                            eligible.append(left_index)
                        if right_segment_interior:
                            eligible.append(right_index)
                        over_index = min(eligible, key=lambda index: routes[index].edge_id)
                        crossings[over_index].add(point)
    return [replace(route, crossings=tuple(sorted(crossings[index]))) for index, route in enumerate(routes)]


def _prepare_routes(routes: Sequence[Route], boxes: Mapping[str, Box]) -> list[Route]:
    prepared = _spread_terminal_ports(routes, boxes)
    prepared = _stagger_shared_trunks(prepared)
    canonical: list[Route] = []
    for route in prepared:
        points: list[tuple[float, float]] = []
        for raw_point in route.points:
            point = _quantize_point(raw_point)
            # Straight connectors naturally produce coincident Manhattan bends.
            # Keep the route canonical by removing only consecutive no-op
            # vertices; endpoint semantics and every non-zero leg are retained.
            if not points or point != points[-1]:
                points.append(point)
        canonical.append(replace(route, points=tuple(points)))
    prepared = canonical
    prepared = _resolve_route_conflicts(prepared, boxes)
    return _declare_proper_crossings(prepared)


def _right_left_route(edge: Mapping[str, Any], boxes: Mapping[str, Box], *, family: str = "orthogonal") -> Route:
    source, target = boxes[edge["source"]], boxes[edge["target"]]
    if abs(target.cx - source.cx) < 1:
        return _vertical_route(edge, boxes)
    if target.cx >= source.cx:
        start, end = (source.x + source.w, source.cy), (target.x, target.cy)
    else:
        start, end = (source.x, source.cy), (target.x + target.w, target.cy)
    middle = (start[0] + end[0]) / 2
    points = (start, (middle, start[1]), (middle, end[1]), end)
    obstacles = [box for node_id, box in boxes.items() if node_id not in {edge["source"], edge["target"]}]
    if family == "orthogonal" and any(_segment_hits_box(a, b, obstacle) for a, b in zip(points, points[1:]) for obstacle in obstacles):
        corridor = max(112.0, min(box.y for box in boxes.values()) - 24)
        points = ((source.cx, source.y), (source.cx, corridor), (target.cx, corridor), (target.cx, target.y))
    return Route(
        str(edge["id"]),
        str(edge["source"]),
        str(edge["target"]),
        points,
        bool(edge.get("directed")),
        family,
        str(edge.get("guard") or edge.get("label") or ""),
        source_member=str(edge["source_member"]) if edge.get("source_member") else None,
        target_member=str(edge["target_member"]) if edge.get("target_member") else None,
    )


def _box_boundary_toward(box: Box, target: tuple[float, float]) -> tuple[float, float]:
    """Return the rectangular boundary point on the center ray toward target."""

    delta_x, delta_y = target[0] - box.cx, target[1] - box.cy
    if abs(delta_x) <= 1e-12 and abs(delta_y) <= 1e-12:
        return (box.x + box.w, box.cy)
    candidates: list[float] = []
    if abs(delta_x) > 1e-12:
        candidates.append((box.w / 2) / abs(delta_x))
    if abs(delta_y) > 1e-12:
        candidates.append((box.h / 2) / abs(delta_y))
    scale = min(candidates)
    return (box.cx + delta_x * scale, box.cy + delta_y * scale)


def _vertical_route(edge: Mapping[str, Any], boxes: Mapping[str, Box]) -> Route:
    source, target = boxes[edge["source"]], boxes[edge["target"]]
    if target.cy >= source.cy:
        start, end = (source.cx, source.y + source.h), (target.cx, target.y)
    else:
        start, end = (source.cx, source.y), (target.cx, target.y + target.h)
    middle = (start[1] + end[1]) / 2
    return Route(
        str(edge["id"]),
        str(edge["source"]),
        str(edge["target"]),
        (start, (start[0], middle), (end[0], middle), end),
        bool(edge.get("directed")),
        "orthogonal",
        str(edge.get("guard") or edge.get("label") or ""),
        source_member=str(edge["source_member"]) if edge.get("source_member") else None,
        target_member=str(edge["target_member"]) if edge.get("target_member") else None,
    )


def _lane_handoff_route(edge: Mapping[str, Any], boxes: Mapping[str, Box], area: Box, slot: int) -> Route:
    """Route one swimlane handoff without traversing peer activities."""

    source, target = boxes[edge["source"]], boxes[edge["target"]]
    if abs(source.cy - target.cy) < 1:
        return _right_left_route(edge, boxes)

    unrelated = [box for node_id, box in boxes.items() if node_id not in {edge["source"], edge["target"]}]
    direct = _vertical_route(edge, boxes)
    if not any(_segment_hits_box(start, end, box) for start, end in zip(direct.points, direct.points[1:]) for box in unrelated):
        return direct

    left = min(box.x for box in boxes.values()) - 24 - slot * 12
    right = max(box.x + box.w for box in boxes.values()) + 24 + slot * 12
    preferred = [left, right] if (source.cx + target.cx) / 2 <= area.cx else [right, left]
    for corridor_x in preferred:
        use_left = corridor_x < area.cx
        start = (source.x if use_left else source.x + source.w, source.cy)
        end = (target.x if use_left else target.x + target.w, target.cy)
        points = (start, (corridor_x, start[1]), (corridor_x, end[1]), end)
        if any(_segment_hits_box(a, b, box) for a, b in zip(points, points[1:]) for box in unrelated):
            continue
        return Route(
            str(edge["id"]),
            str(edge["source"]),
            str(edge["target"]),
            points,
            bool(edge.get("directed")),
            "orthogonal",
            str(edge.get("guard") or edge.get("label") or ""),
        )
    raise ProfileRenderError("renderer-lane-route-unroutable", f"No obstacle-free handoff corridor exists for edge {edge['id']}.")


def _grid_positions(count: int, area: Box, *, columns: int | None = None, gap: float = 24) -> list[Box]:
    if count <= 0:
        return []
    cols = max(1, min(columns or math.ceil(math.sqrt(count)), count))
    rows = math.ceil(count / cols)
    width = (area.w - gap * (cols - 1)) / cols
    height = min(120.0, (area.h - gap * (rows - 1)) / rows)
    return [Box(area.x + (index % cols) * (width + gap), area.y + (index // cols) * (height + gap), width, height) for index in range(count)]


def _topology(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    nodes = list(ir["nodes"])
    groups = list(ir["groups"])
    member_owner = {member: group["id"] for group in groups for member in group["member_ids"] if member in {node["id"] for node in nodes}}
    zone_count = max(1, len(groups) + (1 if any(node["id"] not in member_owner for node in nodes) else 0))
    area = Box(64, 140, builder.width - 128, builder.height - 210)
    zone_w = (area.w - 28 * (zone_count - 1)) / zone_count
    zones: list[tuple[str | None, str, list[Mapping[str, Any]], bool, str | None]] = []
    outside = [node for node in nodes if node["id"] not in member_owner]
    if outside:
        zones.append((None, "External", outside, False, "external"))
    zones.extend((str(group["id"]), str(group["label"]), [node for node in nodes if node["id"] in group["member_ids"]], True, None) for group in groups)
    if not zones:
        zones = [(None, "Topology", nodes, False, "topology")]
    for index, (zone_id, label, members, semantic_group, presentation_shell) in enumerate(zones):
        zone = Box(area.x + index * (zone_w + 28), area.y, zone_w, area.h)
        builder.primitive(
            "zone-boundary",
            zone,
            label=label,
            semantic_id=zone_id,
            member_ids=[item["id"] for item in members] if semantic_group else (),
            semantic_group=semantic_group,
            presentation_shell=presentation_shell,
        )
        positions = _grid_positions(len(members), Box(zone.x + 22, zone.y + 58, zone.w - 44, zone.h - 84), columns=1)
        for node, box in zip(members, positions):
            builder.node(node, box, layout, subtitle=str(node.get("state") or node.get("role", "")))
    for edge in ir["edges"]:
        layout.routes.append(_right_left_route(edge, layout.boxes))
    for annotation in ir["annotations"]:
        builder.text(annotation["text"], 64, builder.height - 34, size=14, weight="650", fill=builder.theme["accent2"])
        layout.emitted_ids.add(annotation["id"])
    return layout


def _pipeline(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    role_rank = {"source": 0, "producer": 0, "transform": 1, "processor": 1, "platform-service": 1, "store": 2, "sink": 3, "consumer": 3}
    ranks: dict[int, list[Mapping[str, Any]]] = {}
    for node in ir["nodes"]:
        ranks.setdefault(role_rank.get(node["role"], 1), []).append(node)
    keys = sorted(ranks)
    area = Box(64, 160, builder.width - 128, builder.height - 250)
    stage_w = (area.w - 32 * (len(keys) - 1)) / max(1, len(keys))
    member_group = {member: group for group in ir["groups"] for member in group["member_ids"]}
    for column, rank in enumerate(keys):
        stage = Box(area.x + column * (stage_w + 32), area.y, stage_w, area.h)
        group_labels = {str(member_group[node["id"]]["label"]) for node in ranks[rank] if node["id"] in member_group}
        label = ", ".join(sorted(group_labels or {str(node["role"]) for node in ranks[rank]}))
        builder.primitive("pipeline-stage", stage, label=label.title(), semantic_id=f"stage-{rank}", member_ids=[node["id"] for node in ranks[rank]])
        for node, box in zip(ranks[rank], _grid_positions(len(ranks[rank]), Box(stage.x + 20, stage.y + 62, stage.w - 40, stage.h - 92), columns=1)):
            builder.node(node, box, layout, subtitle=str(node["role"]))
    for group in ir["groups"]:
        member_boxes = [layout.boxes[member] for member in group["member_ids"] if member in layout.boxes]
        if not member_boxes:
            continue
        left = min(box.x for box in member_boxes) - 12
        top = min(box.y for box in member_boxes) - 18
        right = max(box.x + box.w for box in member_boxes) + 12
        bottom = max(box.y + box.h for box in member_boxes) + 12
        builder.primitive(
            "pipeline-group",
            Box(left, top, right - left, bottom - top),
            label=str(group["label"]),
            semantic_id=str(group["id"]),
            member_ids=group["member_ids"],
            semantic_group=True,
            fill="none",
            radius=10,
        )
    for edge in ir["edges"]:
        layout.routes.append(_right_left_route(edge, layout.boxes))
    return layout


def _deployment(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    zones: dict[str, list[Mapping[str, Any]]] = {}
    for node in ir["nodes"]:
        zones.setdefault(str(node.get("placement", {}).get("zone", "Unassigned zone")), []).append(node)
    area = Box(64, 150, builder.width - 128, builder.height - 220)
    zone_w = (area.w - 32 * (len(zones) - 1)) / max(1, len(zones))
    # The request's first-seen trust/environment order is semantic reading order.
    # Alphabetic sorting can invert Edge -> App -> Data into a misleading back-route.
    for index, (zone_name, nodes) in enumerate(zones.items()):
        zone = Box(area.x + index * (zone_w + 32), area.y, zone_w, area.h)
        builder.primitive("deployment-zone", zone, label=zone_name, semantic_id=f"zone-{index}", member_ids=[node["id"] for node in nodes])
        for node, box in zip(nodes, _grid_positions(len(nodes), Box(zone.x + 22, zone.y + 62, zone.w - 44, zone.h - 92), columns=1)):
            placement = node.get("placement", {})
            host_box = Box(box.x, box.y, box.w, box.h)
            builder.primitive("deployment-host", host_box, label=str(placement.get("host", "host")), semantic_id=f"host-{node['id']}", member_ids=[node["id"]], fill=builder.theme["bg"], radius=10)
            ports = ", ".join(str(port) for port in placement.get("ports", ())) or "—"
            subtitle = f"{placement.get('artifact', 'artifact')} · ×{placement.get('replicas', 1)} · port {ports}"
            builder.node(node, Box(box.x + 18, box.y + 40, box.w - 36, max(58, box.h - 58)), layout, subtitle=subtitle)
    for edge in ir["edges"]:
        layout.routes.append(_right_left_route(edge, layout.boxes))
    return layout


def _rank_nodes(ir: Mapping[str, Any]) -> dict[int, list[Mapping[str, Any]]]:
    nodes = {item["id"]: item for item in ir["nodes"]}
    incoming = {node_id: 0 for node_id in nodes}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for edge in ir["edges"]:
        if edge["source"] in nodes and edge["target"] in nodes:
            outgoing[edge["source"]].append(edge["target"])
            incoming[edge["target"]] += 1
    queue = sorted(node_id for node_id, count in incoming.items() if count == 0) or sorted(nodes)[:1]
    rank = {node_id: 0 for node_id in queue}
    seen: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        for target in sorted(outgoing[current]):
            rank[target] = max(rank.get(target, 0), rank[current] + 1)
            incoming[target] -= 1
            if incoming[target] <= 0:
                queue.append(target)
    for node_id in nodes:
        rank.setdefault(node_id, max(rank.values(), default=-1) + 1)
    result: dict[int, list[Mapping[str, Any]]] = {}
    for node_id, node_rank in rank.items():
        result.setdefault(node_rank, []).append(nodes[node_id])
    return result


def _dag(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    ranks = _rank_nodes(ir)
    area = Box(64, 160, builder.width - 128, builder.height - 230)
    rank_w = (area.w - 28 * (len(ranks) - 1)) / max(1, len(ranks))
    for column, rank in enumerate(sorted(ranks)):
        band = Box(area.x + column * (rank_w + 28), area.y, rank_w, area.h)
        builder.primitive("dag-rank", band, label=f"Rank {rank + 1}", semantic_id=f"rank-{rank}", member_ids=[node["id"] for node in ranks[rank]])
        for node, box in zip(sorted(ranks[rank], key=lambda item: item["id"]), _grid_positions(len(ranks[rank]), Box(band.x + 18, band.y + 58, band.w - 36, band.h - 84), columns=1)):
            builder.node(node, box, layout)
    for index, edge in enumerate(ir["edges"]):
        source, target = layout.boxes[edge["source"]], layout.boxes[edge["target"]]
        if target.cx <= source.cx:
            corridor = area.y - 18 - index * 12
            points = ((source.cx, source.y), (source.cx, corridor), (target.cx, corridor), (target.cx, target.y))
            layout.routes.append(Route(edge["id"], edge["source"], edge["target"], points, bool(edge.get("directed")), "orthogonal", "cycle back-edge"))
        else:
            layout.routes.append(_right_left_route(edge, layout.boxes))
    return layout


def _directed(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    ranks = _rank_nodes(ir)
    area = Box(200, 145, builder.width - 400, builder.height - 210)
    rank_h = (area.h - 30 * (len(ranks) - 1)) / max(1, len(ranks))
    for row, rank in enumerate(sorted(ranks)):
        band = Box(area.x, area.y + row * (rank_h + 30), area.w, rank_h)
        builder.primitive("flow-rank", band, label=f"Step {rank + 1}", semantic_id=f"flow-rank-{rank}", member_ids=[node["id"] for node in ranks[rank]], fill=builder.theme["bg"], radius=8)
        boxes = _grid_positions(len(ranks[rank]), Box(band.x + 120, band.y + 18, band.w - 240, max(76, band.h - 30)), columns=len(ranks[rank]))
        for node, box in zip(sorted(ranks[rank], key=lambda item: item["id"]), boxes):
            shape = "decision" if node["role"] == "decision" else node["role"] if node["role"] in {"start", "terminal", "initial", "artifact"} else "card"
            builder.node(node, Box(box.x, box.y, min(box.w, 260), min(box.h, 100)), layout, shape=shape)
    for index, edge in enumerate(ir["edges"]):
        source, target = layout.boxes[edge["source"]], layout.boxes[edge["target"]]
        if target.cy <= source.cy:
            corridor = area.x + area.w + 24 + index * 14
            points = (
                (source.x + source.w, source.cy),
                (corridor, source.cy),
                (corridor, target.cy),
                (target.x + target.w, target.cy),
            )
            layout.routes.append(Route(
                str(edge["id"]),
                str(edge["source"]),
                str(edge["target"]),
                points,
                bool(edge.get("directed")),
                "orthogonal",
                str(edge.get("guard") or edge.get("label") or ""),
            ))
        else:
            layout.routes.append(_vertical_route(edge, layout.boxes))
    return layout


def _lanes(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    area = Box(64, 150, builder.width - 128, builder.height - 220)
    if ir["diagram"]["type"] == "sequence":
        participants = list(ir["nodes"])
        col_w = area.w / max(1, len(participants))
        for index, node in enumerate(participants):
            x = area.x + index * col_w
            lane = Box(x + 10, area.y, col_w - 20, area.h)
            builder.primitive("interaction-lane", lane, label=str(node["label"]), semantic_id=f"lifeline-{node['id']}", member_ids=[node["id"]], fill=builder.theme["bg"], radius=4)
            header = Box(lane.x + 12, lane.y + 40, lane.w - 24, 74)
            builder.node(node, header, layout, subtitle="participant")
            builder.element("line", {"x1": header.cx, "y1": header.y + header.h, "x2": header.cx, "y2": lane.y + lane.h - 24, "stroke": builder.theme["soft"], "stroke-width": 2, "stroke-dasharray": "8 7"})
        for index, edge in enumerate(_ordered(ir["edges"])):
            source, target = layout.boxes[edge["source"]], layout.boxes[edge["target"]]
            y = area.y + 170 + index * min(90, (area.h - 210) / max(1, len(ir["edges"])))
            start, end = (source.cx, y), (target.cx, y)
            layout.routes.append(Route(edge["id"], edge["source"], edge["target"], (start, end), bool(edge.get("directed")), "message", str(edge.get("label") or edge["kind"])))
    else:
        lanes = _ordered(ir["lanes"])
        lane_h = area.h / max(1, len(lanes))
        member_index = {member: lane for lane in lanes for member in lane["member_ids"]}
        order_by_node = {node["id"]: index for index, node in enumerate(ir["nodes"])}
        for index, lane_data in enumerate(lanes):
            lane = Box(area.x, area.y + index * lane_h, area.w, lane_h - 10)
            members = [node for node in ir["nodes"] if member_index.get(node["id"], {}).get("id") == lane_data["id"]]
            lane_group = builder.primitive("interaction-lane", lane, label=str(lane_data["label"]), semantic_id=str(lane_data["id"]), member_ids=[node["id"] for node in members], fill=builder.theme["bg"], radius=8)
            lane_group.set("data-lane-id", str(lane_data["id"]))
            lane_group.set("data-lane-order", str(lane_data["order"]))
            lane_group.set("data-lane-owner", str(lane_data["owner"]))
            positions = _grid_positions(len(members), Box(lane.x + 180, lane.y + 42, lane.w - 210, lane.h - 56), columns=max(1, len(members)))
            for node, box in zip(sorted(members, key=lambda item: order_by_node[item["id"]]), positions):
                builder.node(node, Box(box.x, box.y, min(240, box.w), min(88, box.h)), layout)
        for index, edge in enumerate(_ordered(ir["edges"])):
            layout.routes.append(_lane_handoff_route(edge, layout.boxes, area, index))
    return layout


def _parse_dt(value: str) -> float:
    return datetime.fromisoformat(value).timestamp()


def _time(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    nodes = list(ir["nodes"])
    starts = [_parse_dt(node["start"]) for node in nodes]
    ends = [_parse_dt(node.get("end", node["start"])) for node in nodes]
    minimum, maximum = min(starts), max(ends)
    span = max(1.0, maximum - minimum)
    area = Box(210, 170, builder.width - 290, builder.height - 260)
    rail = Box(area.x, area.y, area.w, 58)
    builder.primitive("time-rail", rail, label="Time", semantic_id="time-axis", fill=builder.theme["bg"], radius=4)
    builder.element("line", {"x1": area.x, "y1": area.y + 46, "x2": area.x + area.w, "y2": area.y + 46, "stroke": builder.theme["line"], "stroke-width": 3})
    builder.text(datetime.fromtimestamp(minimum).strftime("%Y-%m-%d"), area.x, area.y + 78, size=12, fill=builder.theme["muted"])
    builder.text(datetime.fromtimestamp(maximum).strftime("%Y-%m-%d"), area.x + area.w, area.y + 78, size=12, fill=builder.theme["muted"], anchor="end")
    if ir["diagram"]["type"] == "timeline":
        for index, node in enumerate(sorted(nodes, key=lambda item: item["start"])):
            x = area.x + (_parse_dt(node["start"]) - minimum) / span * area.w
            y = area.y + 90 + (index % 2) * 150
            builder.element("line", {"x1": x, "y1": area.y + 46, "x2": x, "y2": y, "stroke": builder.theme["accent"], "stroke-width": 2})
            date_label = datetime.fromisoformat(str(node["start"])).strftime("%Y-%m-%d")
            builder.node(
                node,
                Box(max(64, min(x - 95, builder.width - 254)), y, 190, 82),
                layout,
                shape="terminal" if node["role"] == "milestone" else "card",
                subtitle=date_label,
            )
    else:
        row_h = min(105, area.h / max(1, len(nodes)))
        for index, node in enumerate(sorted(nodes, key=lambda item: item["start"])):
            y = area.y + 84 + index * row_h
            x = area.x + (_parse_dt(node["start"]) - minimum) / span * area.w
            end_x = area.x + (_parse_dt(node["end"]) - minimum) / span * area.w
            date_range = f"{datetime.fromisoformat(node['start']).strftime('%d/%m')}→{datetime.fromisoformat(node['end']).strftime('%d/%m')}"
            builder.text(f"{node['label']} · {date_range}", 64, y + 32, size=14, weight="650")
            builder.node(
                node,
                Box(x, y, max(8, end_x - x), 58),
                layout,
            )
        for edge in ir["edges"]:
            layout.routes.append(_right_left_route(edge, layout.boxes))
    return layout


def _work(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    area = Box(64, 150, builder.width - 128, builder.height - 220)
    diagram_type = ir["diagram"]["type"]
    if diagram_type == "kanban":
        columns = list(ir["groups"])
        owner = {member: group for group in columns for member in group["member_ids"]}
    elif diagram_type == "story-map":
        backbone = sorted({int(node.get("story", {}).get("backbone_order", 0)) for node in ir["nodes"]})
        columns = [{"id": f"backbone-{value}", "label": f"Activity {value + 1}", "member_ids": [node["id"] for node in ir["nodes"] if int(node.get("story", {}).get("backbone_order", 0)) == value]} for value in backbone]
        owner = {member: group for group in columns for member in group["member_ids"]}
    else:
        columns = [{"id": f"journey-{index}", "label": node["label"], "member_ids": [node["id"]]} for index, node in enumerate(sorted(ir["nodes"], key=lambda item: item.get("journey", {}).get("stage_order", 0)))]
        owner = {member: group for group in columns for member in group["member_ids"]}
    col_w = (area.w - 20 * (len(columns) - 1)) / max(1, len(columns))
    for index, column in enumerate(columns):
        box = Box(area.x + index * (col_w + 20), area.y, col_w, area.h)
        extra = f" · WIP {column.get('wip_limit')}" if column.get("wip_limit") is not None else ""
        members = [node for node in ir["nodes"] if owner.get(node["id"], {}).get("id") == column["id"]]
        builder.primitive("work-column", box, label=str(column["label"]) + extra, semantic_id=str(column["id"]), member_ids=[node["id"] for node in members])
        positions = _grid_positions(len(members), Box(box.x + 18, box.y + 64, box.w - 36, box.h - 92), columns=1)
        for node, node_box in zip(members, positions):
            subtitle = ""
            if diagram_type == "kanban" and node.get("work", {}).get("blocked"):
                subtitle = "BLOCKED"
            elif diagram_type == "user-journey":
                journey = node.get("journey", {})
                sentiment = journey.get("sentiment")
                if isinstance(sentiment, (int, float)) and not isinstance(sentiment, bool):
                    sentiment_text = f"{float(sentiment):+.1f}"
                elif isinstance(sentiment, str):
                    sentiment_text = sentiment
                else:
                    sentiment_text = "—"
                subtitle = f"{journey.get('action', '')} · {journey.get('touchpoint', '')} · sentiment {sentiment_text}"
            elif diagram_type == "story-map":
                subtitle = str(node.get("story", {}).get("release_slice") or "Unassigned")
            builder.node(node, node_box, layout, subtitle=subtitle)
    return layout


def _hierarchy(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    hierarchy_ir = dict(ir)
    primary_edges: list[Mapping[str, Any]] = []
    primary_edge_ids: set[str] = set()
    parents: dict[str, list[str]] = {}
    for edge in ir["edges"]:
        if edge["kind"] == "reports-to":
            primary_edges.append({**edge, "source": edge["target"], "target": edge["source"]})
            primary_edge_ids.add(str(edge["id"]))
            parents.setdefault(str(edge["source"]), []).append(str(edge["target"]))
        elif edge["kind"] in {"parent", "branch"}:
            primary_edges.append(edge)
            primary_edge_ids.add(str(edge["id"]))
            parents.setdefault(str(edge["target"]), []).append(str(edge["source"]))
    # Secondary annotations/relations must not change primary hierarchy ranks.
    # A legacy hierarchy with no recognized primary kind retains deterministic
    # directed ranking, but still receives collision validation below.
    hierarchy_ir["edges"] = primary_edges or list(ir["edges"])
    if primary_edges:
        node_ids = {str(node["id"]) for node in ir["nodes"]}
        indegree = {node_id: 0 for node_id in node_ids}
        outgoing: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
        for edge in primary_edges:
            source, target = str(edge["source"]), str(edge["target"])
            outgoing[source].append(target)
            indegree[target] += 1
        queue = sorted(node_id for node_id, count in indegree.items() if count == 0)
        visited = 0
        while queue:
            current = queue.pop(0)
            visited += 1
            for target in sorted(outgoing[current]):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
                    queue.sort()
        if visited != len(node_ids):
            raise ProfileRenderError("renderer-hierarchy-cycle", "Primary hierarchy relations must form an acyclic forest.")
    ranks = _rank_nodes(hierarchy_ir)
    # A hierarchy is not an alphabetized DAG.  Order each subordinate tier by
    # the already placed manager tier, retaining request order within a manager
    # family.  This prevents sibling families from interleaving and creating
    # unavoidable coincident endpoint stems (the D-152 R09 failure mode).
    request_order = {str(node["id"]): index for index, node in enumerate(ir["nodes"])}
    placed_order: dict[str, float] = {}
    ordered_ranks: dict[int, list[Mapping[str, Any]]] = {}
    for rank in sorted(ranks):
        def family_key(node: Mapping[str, Any]) -> tuple[float, int, str]:
            parent_positions = [placed_order[parent] for parent in parents.get(str(node["id"]), []) if parent in placed_order]
            family_position = sum(parent_positions) / len(parent_positions) if parent_positions else float(request_order[str(node["id"])])
            return family_position, request_order[str(node["id"])], str(node["id"])

        ordered = sorted(ranks[rank], key=family_key)
        ordered_ranks[rank] = ordered
        for position, node in enumerate(ordered):
            placed_order[str(node["id"])] = float(position)
    ranks = ordered_ranks
    area = Box(64, 145, builder.width - 128, builder.height - 210)
    rank_h = area.h / max(1, len(ranks))
    for row, rank in enumerate(sorted(ranks)):
        band = Box(area.x, area.y + row * rank_h, area.w, rank_h - 12)
        builder.primitive("hierarchy-rank", band, label=f"Level {rank + 1}", semantic_id=f"level-{rank}", member_ids=[node["id"] for node in ranks[rank]], fill=builder.theme["bg"], radius=4)
        positions = _grid_positions(len(ranks[rank]), Box(band.x + 180, band.y + 32, band.w - 360, band.h - 48), columns=len(ranks[rank]))
        for node, box in zip(ranks[rank], positions):
            node_width = min(250, box.w)
            builder.node(node, Box(box.cx - node_width / 2, box.y, node_width, min(82, box.h)), layout)
    for index, edge in enumerate(ir["edges"]):
        if str(edge["id"]) in primary_edge_ids or not primary_edges:
            layout.routes.append(_vertical_route(edge, layout.boxes))
        else:
            # Secondary hierarchy relations are annotations, not rank edges.
            # Route same-rank peers laterally and cross-rank peers through the
            # first obstacle-free vertical/side corridor without changing the
            # primary tree ordering.
            layout.routes.append(_lane_handoff_route(edge, layout.boxes, area, index))
    return layout


def _containment(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    area = Box(100, 150, builder.width - 200, builder.height - 220)
    diagram_type = ir["diagram"]["type"]
    if diagram_type == "nested":
        groups = list(ir["groups"])
        by_id = {group["id"]: group for group in groups}
        depth: dict[str, int] = {}
        def group_depth(group: Mapping[str, Any]) -> int:
            parent = group.get("parent_group_id")
            return 0 if not parent else 1 + group_depth(by_id[parent])
        for group in groups:
            depth[group["id"]] = group_depth(group)
        for group in sorted(groups, key=lambda item: depth[item["id"]]):
            inset = depth[group["id"]] * 75
            box = Box(area.x + inset, area.y + inset, area.w - inset * 2, area.h - inset * 2)
            builder.primitive("containment-layer", box, label=group["label"], semantic_id=group["id"], member_ids=group["member_ids"])
        deepest = max(depth.values(), default=0)
        inner = Box(area.x + deepest * 75 + 45, area.y + deepest * 75 + 70, area.w - deepest * 150 - 90, area.h - deepest * 150 - 100)
        for node, box in zip(ir["nodes"], _grid_positions(len(ir["nodes"]), inner)):
            builder.node(node, box, layout)
    elif diagram_type == "pyramid-funnel":
        funnel_series = ir["series"][0]
        data = list(funnel_series["data"])
        unit = str(funnel_series.get("unit") or "").strip()
        max_value = max(float(item["value"]) for item in data) or 1
        tier_h = area.h / len(data)
        for index, item in enumerate(data):
            width = max(area.w * 0.25, area.w * float(item["value"]) / max_value)
            box = Box(area.cx - width / 2, area.y + index * tier_h, width, tier_h - 10)
            value_label = f"{item['domain']} · {item['value']}" + (f" {unit}" if unit else "")
            tier = builder.primitive("containment-layer", box, label=value_label, semantic_id=item["id"], fill=builder.theme["panel"], radius=4)
            tier.set("data-mark", "funnel-tier")
            tier.set("data-series-id", str(funnel_series["id"]))
            tier.set("data-visible-value-label", value_label)
            tier.set("data-visible-unit", unit)
            layout.emitted_ids.add(item["id"])
    else:
        lanes = _ordered(ir["lanes"])
        if not lanes:
            lanes = [{"id": f"layer-{index}", "label": node["label"], "member_ids": [node["id"]], "order": index} for index, node in enumerate(ir["nodes"])]
        layer_h = area.h / max(1, len(lanes))
        member_map = {node["id"]: node for node in ir["nodes"]}
        selected = str(profile.get("profile_binding", {}).get("selected_profile", ""))
        if selected == "layers":
            builder.root.set("data-presentation-variant-id", "layers")
            builder.root.set("data-reading-direction", "top-to-bottom")
            axis = builder.element(
                "g",
                {
                    "data-abstraction-axis": "true",
                    "data-abstraction-axis-label": "Mức trừu tượng",
                    "data-abstraction-axis-top": "Cao",
                    "data-abstraction-axis-bottom": "Thấp",
                },
            )
            axis_x = area.x - 42
            builder.element("line", {"x1": axis_x, "y1": area.y + 36, "x2": axis_x, "y2": area.y + area.h - 28, "stroke": builder.theme["muted"], "stroke-width": 2}, axis)
            builder.text("Mức trừu tượng", axis_x, area.y - 18, size=12, weight="700", anchor="middle", parent=axis)
            builder.text("Cao", axis_x, area.y + 22, size=11, weight="700", anchor="middle", parent=axis)
            builder.text("Thấp", axis_x, area.y + area.h - 8, size=11, weight="700", anchor="middle", parent=axis)
        for index, lane in enumerate(lanes):
            box = Box(area.x, area.y + index * layer_h, area.w, layer_h - 12)
            owner = str(lane.get("owner") or "").strip()
            label = f"{lane['label']} · {owner}" if owner else str(lane["label"])
            lane_group = builder.primitive("containment-layer", box, label=label, semantic_id=lane["id"], member_ids=lane["member_ids"])
            lane_group.set("data-lane-id", str(lane["id"]))
            lane_group.set("data-lane-order", str(lane["order"]))
            if lane.get("owner") is not None:
                lane_group.set("data-lane-owner", str(lane["owner"]))
            members = [member_map[item] for item in lane["member_ids"] if item in member_map]
            positions = _grid_positions(len(members), Box(box.x + 230, box.y + 18, box.w - 270, box.h - 36), columns=max(1, len(members)))
            for node, node_box in zip(members, positions):
                builder.node(node, node_box, layout)
        for edge in ir["edges"]:
            layout.routes.append(_vertical_route(edge, layout.boxes))
    return layout


def _compartments(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    member_anchors: dict[str, tuple[str, float]] = {}
    area = Box(64, 155, builder.width - 128, builder.height - 230)
    boxes = _grid_positions(len(ir["nodes"]), area, columns=min(3, len(ir["nodes"])))
    for node, box in zip(ir["nodes"], boxes):
        members = list(node.get("members", ()))
        height = max(150, 72 + len(members) * 30)
        actual = Box(box.x, box.y, box.w, min(height, area.h))
        group = builder.primitive("compartment-node", actual, label=node["label"], semantic_id=node["id"])
        group.set("data-node-id", str(node["id"]))
        group.set("data-role", str(node["role"]))
        builder.element("line", {"x1": actual.x, "y1": actual.y + 48, "x2": actual.x + actual.w, "y2": actual.y + 48, "stroke": builder.theme["soft"], "stroke-width": 2}, group)
        for index, member in enumerate(members):
            prefix = {"private": "−", "public": "+", "protected": "#"}.get(member.get("visibility"), "")
            label = f"{prefix}{member['name']}"
            if member.get("data_type"):
                data_type = str(member["data_type"])
                type_already_in_label = re.search(
                    rf"(?<![A-Za-z0-9_]){re.escape(data_type)}(?![A-Za-z0-9_])",
                    str(member["name"]),
                    flags=re.IGNORECASE,
                )
                if type_already_in_label is None:
                    label += f": {data_type}"
            constraint_badges = {
                "primary-key": "PK",
                "foreign-key": "FK",
                "not-null": "NN",
                "unique": "UQ",
            }
            constraints = [constraint_badges.get(str(value), str(value).upper()) for value in member.get("constraints", ())]
            if constraints:
                label += f"  [{' '.join(constraints)}]"
            row_y = actual.y + 76 + index * 28
            member_group = builder.element(
                "g",
                {
                    "data-member-id": member["id"],
                    "data-owner-node": node["id"],
                    "data-anchor-y": row_y - 5,
                },
                group,
            )
            builder.text(label, actual.x + 16, row_y, size=13, parent=member_group)
            member_anchors[str(member["id"])] = (str(node["id"]), row_y - 5)
            layout.emitted_ids.add(member["id"])
        layout.boxes[node["id"]] = actual
        layout.emitted_ids.add(node["id"])
    for edge in ir["edges"]:
        relation = str(edge.get("relation_kind") or edge.get("kind") or "")
        multiplicity = " · ".join(value for value in (str(edge.get("source_multiplicity") or ""), relation, str(edge.get("target_multiplicity") or "")) if value)
        source_member = str(edge.get("source_member") or "")
        target_member = str(edge.get("target_member") or "")
        if source_member in member_anchors and target_member in member_anchors:
            source_box, target_box = layout.boxes[edge["source"]], layout.boxes[edge["target"]]
            source_y, target_y = member_anchors[source_member][1], member_anchors[target_member][1]
            if target_box.cx >= source_box.cx:
                start, end = (source_box.x + source_box.w, source_y), (target_box.x, target_y)
            else:
                start, end = (source_box.x, source_y), (target_box.x + target_box.w, target_y)
            middle = (start[0] + end[0]) / 2
            layout.routes.append(
                Route(
                    str(edge["id"]),
                    str(edge["source"]),
                    str(edge["target"]),
                    (start, (middle, start[1]), (middle, end[1]), end),
                    bool(edge.get("directed")),
                    "orthogonal",
                    multiplicity,
                    source_member=source_member,
                    target_member=target_member,
                )
            )
        else:
            route = _right_left_route(edge, layout.boxes)
            layout.routes.append(replace(route, label=multiplicity))
    return layout


def _axis(ir: Mapping[str, Any], dimension: str) -> Mapping[str, Any] | None:
    return next((axis for axis in ir["axes"] if axis["dimension"] == dimension), None)


def _scale(value: float, minimum: float, maximum: float, start: float, end: float) -> float:
    return start + (value - minimum) / max(1e-12, maximum - minimum) * (end - start)


def _spatial(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    field = Box(190, 160, builder.width - 300, builder.height - 270)
    builder.primitive("spatial-field", field, label="Position carries meaning", semantic_id="spatial-field", fill=builder.theme["panel"], radius=6)
    diagram_type = ir["diagram"]["type"]
    if diagram_type in {"quadrant", "wardley-map"}:
        builder.element("line", {"x1": field.cx, "y1": field.y + 48, "x2": field.cx, "y2": field.y + field.h, "stroke": builder.theme["soft"], "stroke-width": 2})
        builder.element("line", {"x1": field.x, "y1": field.cy, "x2": field.x + field.w, "y2": field.cy, "stroke": builder.theme["soft"], "stroke-width": 2})
        x_axis, y_axis = _axis(ir, "x"), _axis(ir, "y")
        if x_axis:
            label = builder.text(x_axis["label"], field.cx, field.y + field.h + 32, size=14, weight="700", anchor="middle")
            for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
                if x_axis.get(name) is not None:
                    label.set(f"data-axis-{name.replace('_', '-')}", str(x_axis[name]))
        if y_axis:
            label = builder.text(y_axis["label"], field.x - 12, field.y + 28, size=14, weight="700", anchor="end")
            for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
                if y_axis.get(name) is not None:
                    label.set(f"data-axis-{name.replace('_', '-')}", str(y_axis[name]))
        if diagram_type == "quadrant":
            points = [(item, float(item["domain"]), float(item["value"])) for series in ir["series"] for item in series["data"]]
        else:
            points = [(node, float(node["strategy"]["evolution"]), float(node["strategy"]["value_chain_position"])) for node in ir["nodes"]]
        xmin, xmax = float((x_axis or {}).get("domain_min", 0)), float((x_axis or {}).get("domain_max", 1))
        ymin, ymax = float((y_axis or {}).get("domain_min", 0)), float((y_axis or {}).get("domain_max", 1))
        for item, x_value, y_value in points:
            x = _scale(x_value, xmin, xmax, field.x + 30, field.x + field.w - 30)
            y = _scale(y_value, ymin, ymax, field.y + field.h - 30, field.y + 70)
            if "role" in item:
                builder.node(item, Box(x - 80, y - 34, 160, 68), layout)
            else:
                builder.element("circle", {"cx": x, "cy": y, "r": 10, "fill": builder.theme["accent"], "data-semantic-id": item["id"], "data-mark": "point"})
                builder.text(item.get("label", item["id"]), x + 15, y - 10, size=12)
                layout.emitted_ids.add(item["id"])
        for edge in ir["edges"]:
            layout.routes.append(_right_left_route(edge, layout.boxes))
    elif diagram_type == "dp-security-matrix":
        cells = list(ir["nodes"])
        parsed = [str(node.get("secondary_label", "row|column")).split("|", 1) for node in cells]
        rows = list(dict.fromkeys(parts[0] for parts in parsed))
        cols = list(dict.fromkeys(parts[1] if len(parts) > 1 else "value" for parts in parsed))
        cell_w, cell_h = field.w / max(1, len(cols)), (field.h - 50) / max(1, len(rows))
        for r_index, row in enumerate(rows):
            builder.text(row, field.x - 20, field.y + 80 + r_index * cell_h + cell_h / 2, size=13, weight="650", anchor="end")
        for c_index, col in enumerate(cols):
            builder.text(col, field.x + c_index * cell_w + cell_w / 2, field.y + 40, size=13, weight="650", anchor="middle")
        for node, parts in zip(cells, parsed):
            r_index, c_index = rows.index(parts[0]), cols.index(parts[1] if len(parts) > 1 else "value")
            box = Box(field.x + c_index * cell_w + 8, field.y + 58 + r_index * cell_h, cell_w - 16, cell_h - 12)
            builder.node(node, box, layout, subtitle=str(node.get("state", "")))
    elif diagram_type == "venn":
        groups = list(ir["groups"])
        centers = [(field.cx - field.w * 0.16, field.cy), (field.cx + field.w * 0.16, field.cy)]
        for index, group in enumerate(groups[:2]):
            cx, cy = centers[index]
            builder.element("ellipse", {"cx": cx, "cy": cy, "rx": field.w * 0.27, "ry": field.h * 0.34, "fill": builder.theme["accent"] if index == 0 else builder.theme["accent2"], "fill-opacity": 0.16, "stroke": builder.theme["accent"] if index == 0 else builder.theme["accent2"], "stroke-width": 3, "data-semantic-id": group["id"], "data-mark": "set-region"})
            builder.text(group["label"], cx, field.y + 88, size=15, weight="700", anchor="middle")
            layout.emitted_ids.add(group["id"])
        for index, node in enumerate(ir["nodes"]):
            box = Box(field.cx - 85 + index * 180, field.cy - 35, 160, 70)
            builder.node(node, box, layout)
    return layout


def _plot_frame(
    builder: SvgBuilder,
    ir: Mapping[str, Any],
    *,
    transpose_axes: bool = False,
    local_amplitude: bool = False,
) -> Box:
    if transpose_axes:
        builder.root.set("data-axis-presentation-mapping", "semantic-y-to-horizontal semantic-x-to-vertical")
    elif local_amplitude:
        builder.root.set("data-axis-presentation-mapping", "semantic-y-to-local-ridge-amplitude semantic-x-to-horizontal")
    frame = Box(160, 165, builder.width - 260, builder.height - 285)
    frame_group = builder.primitive("plot-frame", frame, label="Shared scale", semantic_id="plot-frame", fill=builder.theme["panel"], radius=6)
    if local_amplitude:
        frame_label = next(child for child in frame_group if child.tag == _tag("text"))
        frame_label.set("data-ridgeline-header-role", "shared-scale-heading")
        frame_label.set("data-layout-band", "ridgeline-heading")
    plot_top_offset = 112 if local_amplitude else 64
    plot = Box(frame.x + 70, frame.y + plot_top_offset, frame.w - 110, frame.h - plot_top_offset - 46)
    builder.element("line", {"x1": plot.x, "y1": plot.y + plot.h, "x2": plot.x + plot.w, "y2": plot.y + plot.h, "stroke": builder.theme["line"], "stroke-width": 2})
    builder.element("line", {"x1": plot.x, "y1": plot.y, "x2": plot.x, "y2": plot.y + plot.h, "stroke": builder.theme["line"], "stroke-width": 2})
    for index in range(1, 5):
        y = plot.y + index * plot.h / 5
        builder.element("line", {"x1": plot.x, "y1": y, "x2": plot.x + plot.w, "y2": y, "stroke": builder.theme["soft"], "stroke-width": 1})
    x_axis = _axis(ir, "x") or _axis(ir, "angular")
    y_axis = _axis(ir, "y") or _axis(ir, "radial")
    if ir["diagram"]["type"] == "radar":
        x_axis = y_axis = None
    horizontal_axis, vertical_axis = (y_axis, x_axis) if transpose_axes else (x_axis, y_axis)
    if horizontal_axis:
        label = builder.text(horizontal_axis["label"], plot.cx, frame.y + frame.h - 18, size=13, weight="700", anchor="middle")
        for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
            if horizontal_axis.get(name) is not None:
                label.set(f"data-axis-{name.replace('_', '-')}", str(horizontal_axis[name]))
        label.set("data-axis-presentation", "horizontal")
    if vertical_axis:
        label_y = frame.y + 58 if local_amplitude else plot.y - 16
        label = builder.text(vertical_axis["label"], frame.x + 16, label_y, size=13, weight="700")
        for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
            if vertical_axis.get(name) is not None:
                label.set(f"data-axis-{name.replace('_', '-')}", str(vertical_axis[name]))
        label.set("data-axis-presentation", "local-ridge-amplitude" if local_amplitude else "vertical")
        if local_amplitude:
            label.set("data-ridgeline-header-role", "amplitude-axis-title")
            label.set("data-layout-band", "ridgeline-axis-title")
    return plot


SERIES_PATTERNS = (
    ("solid-circle", None, "circle"),
    ("dash-square", "10 6", "square"),
    ("dot-diamond", "2 5", "diamond"),
    ("dash-dot-triangle", "12 4 2 4", "triangle"),
)


def _series_style(builder: SvgBuilder, index: int) -> dict[str, str | None]:
    pattern_id, dash_array, marker_shape = SERIES_PATTERNS[index % len(SERIES_PATTERNS)]
    return {
        "pattern_id": pattern_id,
        "dash_array": dash_array,
        "marker_shape": marker_shape,
        "color": builder.theme["accent"] if index % 2 == 0 else builder.theme["accent2"],
    }


def _series_marker(
    builder: SvgBuilder,
    x: float,
    y: float,
    style: Mapping[str, str | None],
    attrs: Mapping[str, Any],
    *,
    parent: ET.Element | None = None,
) -> ET.Element:
    marker_attrs = {
        **attrs,
        "fill": style["color"],
        "stroke": builder.theme["bg"],
        "stroke-width": 1.5,
        "data-marker-shape": style["marker_shape"],
        "data-series-pattern": style["pattern_id"],
    }
    if style["marker_shape"] == "circle":
        return builder.element("circle", {**marker_attrs, "cx": x, "cy": y, "r": 8}, parent)
    if style["marker_shape"] == "square":
        return builder.element("rect", {**marker_attrs, "x": x - 8, "y": y - 8, "width": 16, "height": 16, "rx": 1}, parent)
    if style["marker_shape"] == "diamond":
        points = f"{_fmt(x)},{_fmt(y - 9)} {_fmt(x + 9)},{_fmt(y)} {_fmt(x)},{_fmt(y + 9)} {_fmt(x - 9)},{_fmt(y)}"
        return builder.element("polygon", {**marker_attrs, "points": points}, parent)
    points = f"{_fmt(x)},{_fmt(y - 9)} {_fmt(x + 9)},{_fmt(y + 8)} {_fmt(x - 9)},{_fmt(y + 8)}"
    return builder.element("polygon", {**marker_attrs, "points": points}, parent)


def _series_legend(builder: SvgBuilder, plot: Box, series_items: Sequence[Mapping[str, Any]]) -> None:
    if len(series_items) <= 1:
        return
    legend = builder.element("g", {"data-series-legend": "true", "data-series-count": len(series_items)})
    for index, series in enumerate(series_items):
        style = _series_style(builder, index)
        x = plot.x + index * 220
        y = plot.y - 76
        entry = builder.element(
            "g",
            {
                "data-series-legend-id": series["id"],
                "data-series-pattern": style["pattern_id"],
                "data-series-marker": style["marker_shape"],
            },
            legend,
        )
        _series_marker(builder, x, y, style, {"data-series-legend-mark": series["id"]}, parent=entry)
        label = builder.text(series["label"], x + 16, y + 5, size=12, weight="700", parent=entry)
        label.set("data-series-label-for", str(series["id"]))


def _bubble_series_legend(builder: SvgBuilder, plot: Box, series_items: Sequence[Mapping[str, Any]]) -> None:
    if len(series_items) <= 1:
        return
    legend = builder.element("g", {"data-series-legend": "true", "data-series-count": len(series_items), "data-series-legend-kind": "bubble-outline"})
    for index, series in enumerate(series_items):
        style = _series_style(builder, index)
        x = plot.x + index * 220
        y = plot.y - 76
        entry = builder.element(
            "g",
            {
                "data-series-legend-id": series["id"],
                "data-series-pattern": style["pattern_id"],
                "data-series-marker": "bubble-outline",
            },
            legend,
        )
        builder.element(
            "circle",
            {
                "cx": x,
                "cy": y,
                "r": 8,
                "fill": style["color"],
                "fill-opacity": 0.35,
                "stroke": style["color"],
                "stroke-width": 2,
                "stroke-dasharray": style["dash_array"],
                "data-series-legend-mark": series["id"],
                "data-series-pattern": style["pattern_id"],
            },
            entry,
        )
        label = builder.text(series["label"], x + 16, y + 5, size=12, weight="700", parent=entry)
        label.set("data-series-label-for", str(series["id"]))


def _quantitative(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    selected = profile["profile_binding"]["selected_profile"]
    plot = _plot_frame(
        builder,
        ir,
        transpose_axes=selected == "dumbbell",
        local_amplitude=selected == "ridgeline",
    )
    diagram_type = ir["diagram"]["type"]
    x_axis, y_axis = _axis(ir, "x"), _axis(ir, "y")
    if selected == "dumbbell":
        categories = [item["domain"] for item in ir["series"][0]["data"]]
        minimum = float(y_axis["domain_min"])
        maximum = float(y_axis["domain_max"])
        for index, series in enumerate(ir["series"]):
            builder.text(
                str(series["label"]),
                plot.x + index * 180,
                plot.y - 20,
                size=12,
                weight="700",
                fill=builder.theme["accent"] if index == 0 else builder.theme["accent2"],
            )
        for row, category in enumerate(categories):
            y = plot.y + (row + 0.5) * plot.h / len(categories)
            pair = [next(item for item in series["data"] if item["domain"] == category) for series in ir["series"]]
            xs = [_scale(float(item["value"]), minimum, maximum, plot.x, plot.x + plot.w) for item in pair]
            builder.element("line", {"x1": xs[0], "y1": y, "x2": xs[1], "y2": y, "stroke": builder.theme["line"], "stroke-width": 4, "data-mark": "comparison-segment"})
            builder.text(category, plot.x - 18, y + 5, size=13, anchor="end")
            for index, item in enumerate(pair):
                builder.element("circle", {"cx": xs[index], "cy": y, "r": 10, "fill": builder.theme["accent"] if index == 0 else builder.theme["accent2"], "data-semantic-id": item["id"], "data-mark": "endpoint", "data-value": item["value"]})
                builder.text(item["value"], xs[index], y - 16, size=11, weight="700", anchor="middle")
                layout.emitted_ids.add(item["id"])
            delta = float(pair[1]["value"]) - float(pair[0]["value"])
            delta_text = f"{delta:+g}" if delta else "0"
            delta_label = builder.text(delta_text, (xs[0] + xs[1]) / 2, y - 16, size=12, weight="700", anchor="middle")
            delta_label.set("data-mark", "comparison-delta")
            delta_label.set("data-domain", str(category))
            delta_label.set("data-delta", f"{delta:g}")
    elif selected == "slope-graph":
        minimum = float(y_axis["domain_min"])
        maximum = float(y_axis["domain_max"])
        left, right = plot.x + 80, plot.x + plot.w - 80
        _series_legend(builder, plot, ir["series"])
        builder.element("line", {"x1": left, "y1": plot.y, "x2": left, "y2": plot.y + plot.h, "stroke": builder.theme["soft"], "stroke-width": 2})
        builder.element("line", {"x1": right, "y1": plot.y, "x2": right, "y2": plot.y + plot.h, "stroke": builder.theme["soft"], "stroke-width": 2})
        states = [str(item.get("domain", "")) for item in ir["series"][0]["data"]]
        builder.text(states[0], left, plot.y - 18, size=13, weight="700", anchor="middle")
        builder.text(states[1], right, plot.y - 18, size=13, weight="700", anchor="middle")
        for series_index, series in enumerate(ir["series"]):
            style = _series_style(builder, series_index)
            first, second = series["data"]
            y1 = _scale(float(first["value"]), minimum, maximum, plot.y + plot.h, plot.y)
            y2 = _scale(float(second["value"]), minimum, maximum, plot.y + plot.h, plot.y)
            builder.element("line", {"x1": left, "y1": y1, "x2": right, "y2": y2, "stroke": style["color"], "stroke-width": 3, "stroke-dasharray": style["dash_array"], "data-mark": "slope", "data-series-id": series["id"], "data-series-pattern": style["pattern_id"]})
            for item, x, y in ((first, left, y1), (second, right, y2)):
                _series_marker(builder, x, y, style, {"data-semantic-id": item["id"], "data-mark": "endpoint", "data-value": item["value"], "data-series-id": series["id"]})
                builder.text(item["value"], x + (-12 if x == left else 12), y - 10, size=11, weight="700", anchor="end" if x == left else "start")
                layout.emitted_ids.add(item["id"])
            series_label = builder.text(series["label"], right + 14, y2 + 4, size=12)
            series_label.set("data-series-label-for", str(series["id"]))
            delta = float(second["value"]) - float(first["value"])
            delta_text = f"{delta:+g}" if delta else "0"
            delta_label = builder.text(delta_text, (left + right) / 2, (y1 + y2) / 2 - 10, size=12, weight="700", anchor="middle")
            delta_label.set("data-mark", "slope-delta")
            delta_label.set("data-series-id", str(series["id"]))
            delta_label.set("data-delta", f"{delta:g}")
    elif selected == "ridgeline":
        distributions = [series["distribution"] for series in ir["series"]]
        bin_edges = [float(value) for value in distributions[0]["bin_edges"]]
        derived = derive_ridgeline_profiles(ir)
        amplitude = min(70.0, plot.h / max(2, len(ir["series"]) + 1) * 0.62)
        x_min, x_max = float(x_axis["domain_min"]), float(x_axis["domain_max"])
        method = str(distributions[0]["method"])
        bandwidth = distributions[0]["bandwidth"]
        method_label = f"{method} · {len(bin_edges) - 1} bins"
        if bandwidth is not None:
            method_label += f" · bandwidth {bandwidth}"
        metadata_label = builder.text(
            f"{method_label} · global-max",
            plot.x,
            plot.y - 18,
            size=12,
            fill=builder.theme["muted"],
        )
        metadata_label.set("data-ridgeline-header-role", "distribution-metadata")
        metadata_label.set("data-layout-band", "ridgeline-distribution-metadata")
        for row, series in enumerate(ir["series"]):
            baseline = plot.y + (row + 1) * plot.h / (len(ir["series"]) + 1)
            amplitude_guide = builder.element(
                "g",
                {
                    "data-local-amplitude-series": series["id"],
                    "data-local-amplitude-axis-id": y_axis["id"],
                    "data-local-amplitude-min": y_axis["domain_min"],
                    "data-local-amplitude-max": y_axis["domain_max"],
                    "data-local-amplitude-normalization": distributions[row]["amplitude_normalization"],
                },
            )
            guide_x = plot.x + 8
            builder.element("line", {"x1": guide_x, "y1": baseline, "x2": guide_x, "y2": baseline - amplitude, "stroke": builder.theme["muted"], "stroke-width": 1}, amplitude_guide)
            builder.text(y_axis["domain_min"], guide_x + 5, baseline, size=9, fill=builder.theme["muted"], parent=amplitude_guide)
            builder.text(y_axis["domain_max"], guide_x + 5, baseline - amplitude + 4, size=9, fill=builder.theme["muted"], parent=amplitude_guide)
            centers = [float(value) for value in derived["grid"]]
            normalized_amplitudes = [float(value) for value in derived["amplitudes"][str(series["id"])]]
            points = [
                (
                    _scale(center, x_min, x_max, plot.x, plot.x + plot.w),
                    baseline - amplitude * normalized,
                )
                for center, normalized in zip(centers, normalized_amplitudes)
            ]
            path_points = [(plot.x, baseline), *points, (plot.x + plot.w, baseline)]
            builder.element("polyline", {
                "points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in path_points),
                "fill": builder.theme["accent"],
                "fill-opacity": 0.16,
                "stroke": builder.theme["accent"],
                "stroke-width": 2,
                "data-semantic-id": series["data"][0]["id"],
                "data-series-id": series["id"],
                "data-mark": "ridge",
                "data-bin-count": len(bin_edges) - 1,
                "data-distribution-method": distributions[row]["method"],
                "data-distribution-bandwidth": distributions[row]["bandwidth"],
                "data-normalization": distributions[row]["amplitude_normalization"],
                "data-ridge-baseline": baseline,
                "data-ridge-amplitude-pixels": amplitude,
            })
            builder.text(series["label"], plot.x - 16, baseline, size=12, anchor="end")
            layout.emitted_ids.add(series["data"][0]["id"])
    elif selected == "bubble":
        x_axis, y_axis, size_axis = _axis(ir, "x"), _axis(ir, "y"), _axis(ir, "size")
        max_radius = 34.0
        _bubble_series_legend(builder, plot, ir["series"])
        size_label = builder.text(
            f"{size_axis['label']} · {size_axis.get('unit') or 'unitless'} · {size_axis['domain_min']}..{size_axis['domain_max']} · area",
            plot.x + plot.w,
            plot.y - 18,
            size=12,
            fill=builder.theme["muted"],
            anchor="end",
        )
        for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
            if size_axis.get(name) is not None:
                size_label.set(f"data-axis-{name.replace('_', '-')}", str(size_axis[name]))
        size_label.set("data-axis-presentation", "size-area")
        size_label.set("data-size-legend", "true")
        size_label.set("data-size-legend-label", str(size_axis["label"]))
        size_label.set("data-size-legend-unit", str(size_axis.get("unit") or ""))
        size_label.set("data-size-legend-domain-min", str(size_axis["domain_min"]))
        size_label.set("data-size-legend-domain-max", str(size_axis["domain_max"]))
        for series_index, series in enumerate(ir["series"]):
            style = _series_style(builder, series_index)
            for item in series["data"]:
                x = _scale(float(item["x_value"]), float(x_axis["domain_min"]), float(x_axis["domain_max"]), plot.x, plot.x + plot.w)
                y = _scale(float(item["y_value"]), float(y_axis["domain_min"]), float(y_axis["domain_max"]), plot.y + plot.h, plot.y)
                radius = max_radius * math.sqrt(max(0.0, float(item["size_value"])) / max(1.0, float(size_axis["domain_max"])))
                builder.element("circle", {"cx": x, "cy": y, "r": radius, "fill": style["color"], "fill-opacity": 0.35, "stroke": style["color"], "stroke-width": 2, "stroke-dasharray": style["dash_array"], "data-semantic-id": item["id"], "data-series-id": series["id"], "data-series-pattern": style["pattern_id"], "data-mark": "bubble", "data-size-value": item["size_value"], "data-size-unit": item["size_unit"]})
                datum_label = builder.text(item.get("label", item["id"]), x, y - radius - 8, size=11, weight="700", anchor="middle")
                datum_label.set("data-label-for", str(item["id"]))
                layout.emitted_ids.add(item["id"])
    elif diagram_type in {"scatter-plot", "quadrant"}:
        x_min, x_max = float(x_axis["domain_min"]), float(x_axis["domain_max"])
        y_min, y_max = float(y_axis["domain_min"]), float(y_axis["domain_max"])
        _series_legend(builder, plot, ir["series"])
        for series_index, series in enumerate(ir["series"]):
            style = _series_style(builder, series_index)
            for item in series["data"]:
                x = _scale(float(item["domain"]), x_min, x_max, plot.x, plot.x + plot.w)
                y = _scale(float(item["value"]), y_min, y_max, plot.y + plot.h, plot.y)
                _series_marker(builder, x, y, style, {"data-semantic-id": item["id"], "data-mark": "observation", "data-series-id": series["id"]})
                builder.text(item.get("label", item["id"]), x + 13, y - 10, size=11)
                layout.emitted_ids.add(item["id"])
    elif diagram_type == "bar-chart":
        categories = [item["domain"] for item in ir["series"][0]["data"]]
        minimum, maximum = float(y_axis["domain_min"]), float(y_axis["domain_max"])
        zero_y = _scale(0.0, minimum, maximum, plot.y + plot.h, plot.y)
        category_slot = plot.w / len(categories)
        group_width = category_slot * 0.72
        bar_width = group_width / len(ir["series"])
        for series_index, series in enumerate(ir["series"]):
            color = builder.theme["accent"] if series_index % 2 == 0 else builder.theme["accent2"]
            builder.text(str(series["label"]), plot.x + series_index * 190, plot.y - 18, size=12, weight="700", fill=color)
            by_domain = {item["domain"]: item for item in series["data"]}
            for category_index, category in enumerate(categories):
                item = by_domain[category]
                value_y = _scale(float(item["value"]), minimum, maximum, plot.y + plot.h, plot.y)
                x = plot.x + category_index * category_slot + (category_slot - group_width) / 2 + series_index * bar_width
                top, height = min(value_y, zero_y), abs(zero_y - value_y)
                builder.element("rect", {"x": x, "y": top, "width": max(2.0, bar_width - 5), "height": height, "rx": 5, "fill": color, "data-semantic-id": item["id"], "data-mark": "bar", "data-series-id": series["id"], "data-value": item["value"]})
                builder.text(item["value"], x + (bar_width - 5) / 2, top - 8, size=11, weight="700", anchor="middle")
                layout.emitted_ids.add(item["id"])
        for category_index, category in enumerate(categories):
            builder.text(category, plot.x + category_index * category_slot + category_slot / 2, plot.y + plot.h + 24, size=12, anchor="middle")
    elif diagram_type == "line-chart":
        all_data = [item for series in ir["series"] for item in series["data"]]
        values = [float(item["value"]) for item in all_data if not item.get("missing")]
        minimum, maximum = min(values), max(values)
        for s_index, series in enumerate(ir["series"]):
            points = []
            for index, item in enumerate(series["data"]):
                x = plot.x + index * plot.w / max(1, len(series["data"]) - 1)
                y = _scale(float(item["value"]), minimum, maximum, plot.y + plot.h, plot.y)
                points.append((x, y))
                builder.element("circle", {"cx": x, "cy": y, "r": 6, "fill": builder.theme["accent2"], "data-semantic-id": item["id"], "data-mark": "series-point"})
                builder.text(item.get("domain", item["id"]), x, plot.y + plot.h + 22, size=11, anchor="middle")
                layout.emitted_ids.add(item["id"])
            builder.element("polyline", {"points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points), "fill": "none", "stroke": builder.theme["accent"] if s_index == 0 else builder.theme["accent2"], "stroke-width": 3, "data-mark": "series-line"})
    elif diagram_type in {"radar", "polar-chart"}:
        data = ir["series"][0]["data"]
        center, radius = (plot.cx, plot.cy), min(plot.w, plot.h) * 0.4
        visible_values = [float(item["value"]) for item in data if not item.get("missing")]
        maximum = max(visible_values, default=1) or 1
        points = []
        for index, item in enumerate(data):
            angle = -math.pi / 2 + 2 * math.pi * index / len(data)
            end = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
            builder.element("line", {"x1": center[0], "y1": center[1], "x2": end[0], "y2": end[1], "stroke": builder.theme["soft"], "stroke-width": 2})
            value_radius = 0 if item.get("missing") else radius * float(item["value"]) / maximum
            point = (center[0] + value_radius * math.cos(angle), center[1] + value_radius * math.sin(angle))
            points.append(point)
            builder.element("circle", {"cx": point[0], "cy": point[1], "r": 6, "fill": "none" if item.get("missing") else builder.theme["accent"], "stroke": builder.theme["accent"], "stroke-width": 2, "data-semantic-id": item["id"], "data-mark": "missing-point" if item.get("missing") else "radial-point"})
            axis_label = builder.text(item.get("domain", item["id"]), end[0], end[1], size=11, anchor="middle")
            if diagram_type == "radar" and index < len(ir["axes"]):
                axis = ir["axes"][index]
                axis_label.text = str(axis["label"])
                for name in ("id", "dimension", "scale", "domain_min", "domain_max", "unit"):
                    if axis.get(name) is not None:
                        axis_label.set(f"data-axis-{name.replace('_', '-')}", str(axis[name]))
                axis_label.set("data-axis-presentation", "radial-spoke")
            layout.emitted_ids.add(item["id"])
        builder.element("polygon", {"points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points), "fill": builder.theme["accent"], "fill-opacity": 0.18, "stroke": builder.theme["accent"], "stroke-width": 3, "data-mark": "radial-profile"})
    elif diagram_type == "treemap":
        nodes = list(ir["nodes"])
        total = sum(float(node.get("value", 1)) for node in nodes) or 1
        cursor = plot.x
        for node in nodes:
            width = plot.w * float(node.get("value", 1)) / total
            builder.node(node, Box(cursor, plot.y, width - 4, plot.h), layout, subtitle=str(node.get("value", "")))
            cursor += width
    return layout


def _special(builder: SvgBuilder, ir: Mapping[str, Any], profile: Mapping[str, Any]) -> Layout:
    layout = Layout()
    diagram_type = ir["diagram"]["type"]
    area = Box(100, 150, builder.width - 200, builder.height - 230)
    builder.primitive("special-spine", area, label=diagram_type, semantic_id="special-geometry", fill=builder.theme["bg"], radius=6)
    if diagram_type == "loop-flywheel":
        center, radius = (area.cx, area.cy + 20), min(area.w, area.h) * 0.32
        builder.element("circle", {"cx": center[0], "cy": center[1], "r": radius, "fill": "none", "stroke": builder.theme["soft"], "stroke-width": 18, "data-mark": "cycle-ring"})
        for index, node in enumerate(ir["nodes"]):
            angle = -math.pi / 2 + 2 * math.pi * index / len(ir["nodes"])
            builder.node(node, Box(center[0] + radius * math.cos(angle) - 85, center[1] + radius * math.sin(angle) - 38, 170, 76), layout)
        for edge in ir["edges"]:
            source, target = layout.boxes[edge["source"]], layout.boxes[edge["target"]]
            start = _box_boundary_toward(source, (target.cx, target.cy))
            end = _box_boundary_toward(target, (source.cx, source.cy))
            layout.routes.append(Route(edge["id"], edge["source"], edge["target"], (start, end), bool(edge.get("directed")), "cycle-arc"))
    elif diagram_type == "sankey":
        ranks = _rank_nodes(ir)
        rank_w = area.w / max(1, len(ranks))
        for column, rank in enumerate(sorted(ranks)):
            for row, node in enumerate(ranks[rank]):
                builder.node(node, Box(area.x + column * rank_w + 30, area.y + 120 + row * 130, min(210, rank_w - 60), 100), layout)
        for edge in ir["edges"]:
            route = _right_left_route(edge, layout.boxes, family="ribbon")
            layout.routes.append(route)
    else:
        effect = next(node for node in ir["nodes"] if node["role"] == "effect")
        causes = [node for node in ir["nodes"] if node["role"] == "cause"]
        spine_y = area.cy
        builder.element("line", {"x1": area.x + 80, "y1": spine_y, "x2": area.x + area.w - 260, "y2": spine_y, "stroke": builder.theme["line"], "stroke-width": 5, "data-mark": "cause-spine"})
        builder.node(effect, Box(area.x + area.w - 240, spine_y - 55, 210, 110), layout, shape="terminal")
        causes_by_id = {str(cause["id"]): cause for cause in causes}
        groups = list(ir["groups"])
        anchor_start = area.x + 250
        anchor_end = area.x + area.w - 460
        for group_index, group in enumerate(groups):
            anchor_x = anchor_start + group_index * (anchor_end - anchor_start) / max(1, len(groups) - 1)
            above = group_index % 2 == 0
            members = [causes_by_id[member] for member in group["member_ids"] if member in causes_by_id]
            member_width = 160.0
            total_width = len(members) * member_width + max(0, len(members) - 1) * 18
            member_boxes: list[Box] = []
            for member_index, cause in enumerate(members):
                x = anchor_x - total_width / 2 + member_index * (member_width + 18)
                box = Box(x, spine_y - 180 if above else spine_y + 96, member_width, 78)
                member_boxes.append(box)
                builder.node(cause, box, layout)
                start = (box.cx, box.y + box.h if above else box.y)
                attach = (anchor_x + (member_index - (len(members) - 1) / 2) * 22, spine_y)
                edge = next(item for item in ir["edges"] if item["source"] == cause["id"])
                layout.routes.append(Route(edge["id"], edge["source"], edge["target"], (start, attach, (layout.boxes[effect["id"]].x, spine_y)), bool(edge.get("directed")), "fishbone"))
            left = min(box.x for box in member_boxes) - 10
            top = min(box.y for box in member_boxes) - 32
            right = max(box.x + box.w for box in member_boxes) + 10
            bottom = max(box.y + box.h for box in member_boxes) + 12
            category_box = Box(left, top, right - left, bottom - top)
            builder.primitive(
                "fishbone-category",
                category_box,
                label=str(group["label"]),
                semantic_id=str(group["id"]),
                member_ids=group["member_ids"],
                semantic_group=True,
                fill="none",
                radius=8,
            )
            category_y = category_box.y + category_box.h if category_box.cy < spine_y else category_box.y
            builder.element("line", {"x1": category_box.cx, "y1": category_y, "x2": anchor_x, "y2": spine_y, "stroke": builder.theme["line"], "stroke-width": 3, "data-mark": "category-bone", "data-category-id": group["id"]})
    return layout


ENGINE_RENDERERS: dict[str, Callable[[SvgBuilder, Mapping[str, Any], Mapping[str, Any]], Layout]] = {
    "topology-and-zones": _topology,
    "integration-pipeline": _pipeline,
    "runtime-deployment": _deployment,
    "dependency-dag": _dag,
    "directed-flow-state": _directed,
    "lane-interaction": _lanes,
    "time-planning": _time,
    "work-experience": _work,
    "hierarchy": _hierarchy,
    "containment-stack": _containment,
    "compartment-model": _compartments,
    "spatial-matrix": _spatial,
    "quantitative": _quantitative,
    "special-geometry": _special,
}


def _required_semantic_ids(ir: Mapping[str, Any]) -> set[str]:
    ids = {str(item["id"]) for collection in ("nodes", "edges") for item in ir[collection]}
    for series in ir["series"]:
        ids.update(str(item["id"]) for item in series["data"])
    return ids


def render_profiled_svg(ir: Mapping[str, Any], raw_request: Mapping[str, Any], profile_plan: Mapping[str, Any]) -> str:
    """Render one validated plan through its exact executable layout engine."""

    binding = profile_plan.get("profile_binding")
    if not isinstance(binding, Mapping):
        raise ProfileRenderError("renderer-binding-missing", "A validated pre-render profile binding is required.")
    engine = str(binding.get("layout_engine", ""))
    if engine not in ENGINE_RENDERERS or set(ENGINE_RENDERERS) != set(ENGINE_PRIMITIVES):
        raise ProfileRenderError("renderer-engine-unsupported", "The selected layout engine has no exact executable renderer.")
    if binding.get("structural_override") != "none":
        raise ProfileRenderError("renderer-custom-structure-unsupported", "Custom structure needs a separately implemented renderer and cannot use a 45-profile claim.")
    width, height = CANVAS_PRESETS[str(raw_request.get("size", "fit"))]
    title = str(ir["diagram"]["title"])
    builder = SvgBuilder(width, height, str(binding["mode"]), title, binding)
    layout = ENGINE_RENDERERS[engine](builder, ir, profile_plan)
    layout.routes = _prepare_routes(layout.routes, layout.boxes)
    for route in layout.routes:
        builder.route(route)
        layout.emitted_ids.add(route.edge_id)
    for route in layout.routes:
        for crossing in route.crossings:
            builder.crossing_bridge(route, crossing)
    missing = _required_semantic_ids(ir) - layout.emitted_ids
    if missing:
        raise ProfileRenderError("renderer-semantic-loss", f"Renderer omitted semantic IDs: {', '.join(sorted(missing))}.")
    material = [str(item.get("label", item.get("text", ""))) for collection in ("nodes", "groups", "lanes", "series", "axes", "annotations") for item in ir[collection] if item.get("label", item.get("text", ""))]
    description = builder.root.find(_tag("desc"))
    if description is not None and material:
        description.text = f"{description.text or ''} Source labels: {'; '.join(material)}."
    builder.root.set("data-layout-sha256", hashlib.sha256(canonical_json({"boxes": {key: vars(value) for key, value in sorted(layout.boxes.items())}, "routes": [vars(route) for route in layout.routes]}).encode("utf-8")).hexdigest())
    svg = builder.finish()
    validate_rendered_geometry(svg, ir, binding)
    return svg


def _parse_box(element: ET.Element) -> Box:
    return Box(*(float(element.attrib[field]) for field in ("data-x", "data-y", "data-w", "data-h")))


def _points(value: str) -> tuple[tuple[float, float], ...]:
    return tuple(tuple(float(number) for number in pair.split(",")) for pair in value.split())  # type: ignore[return-value]


def _on_boundary(point: tuple[float, float], box: Box, tolerance: float = 1.1) -> bool:
    x, y = point
    within_x = box.x - tolerance <= x <= box.x + box.w + tolerance
    within_y = box.y - tolerance <= y <= box.y + box.h + tolerance
    return within_x and within_y and (abs(x - box.x) <= tolerance or abs(x - box.x - box.w) <= tolerance or abs(y - box.y) <= tolerance or abs(y - box.y - box.h) <= tolerance)


def _parse_declared_points(value: str) -> set[tuple[float, float]]:
    if not value:
        return set()
    try:
        return {tuple(float(number) for number in pair.split(",")) for pair in value.split(";")}  # type: ignore[misc]
    except (TypeError, ValueError) as error:
        raise ProfileRenderError("renderer-crossing-declaration-invalid", "Crossing declaration is not a valid coordinate list.") from error


def _junction_declarations(root: ET.Element) -> dict[tuple[float, float], tuple[str, frozenset[str]]]:
    declarations: dict[tuple[float, float], tuple[str, frozenset[str]]] = {}
    for element in root.iter():
        if not element.get("data-junction-id"):
            continue
        kind = element.get("data-junction-kind", "")
        members = frozenset(element.get("data-member-edge-ids", "").split())
        if kind not in {"merge", "split"} or len(members) < 2:
            raise ProfileRenderError("renderer-junction-declaration-invalid", "Declared junction needs merge/split semantics and at least two member edges.")
        try:
            point = (float(element.attrib["data-x"]), float(element.attrib["data-y"]))
        except (KeyError, ValueError) as error:
            raise ProfileRenderError("renderer-junction-declaration-invalid", "Declared junction needs numeric data-x/data-y coordinates.") from error
        if point in declarations:
            raise ProfileRenderError("renderer-junction-declaration-duplicate", "A junction coordinate was declared more than once.")
        declarations[point] = (kind, members)
    return declarations


def _validate_edge_collision_graph(
    root: ET.Element,
    edge_elements: Mapping[str, ET.Element],
    expected_edges: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a pairwise segment graph and fail closed on ambiguous connectivity."""

    routed: dict[str, tuple[tuple[float, float], ...]] = {
        edge_id: _points(element.get("points", "")) for edge_id, element in edge_elements.items()
    }
    declared_crossings = {
        edge_id: _parse_declared_points(element.get("data-crossing-points", ""))
        for edge_id, element in edge_elements.items()
    }
    junctions = _junction_declarations(root)
    terminal_groups: dict[str, list[tuple[str, tuple[float, float]]]] = {}
    for edge_id, edge in expected_edges.items():
        points = routed[edge_id]
        terminal_groups.setdefault(str(edge["source"]), []).append((edge_id, points[0]))
        terminal_groups.setdefault(str(edge["target"]), []).append((edge_id, points[-1]))
    fan_group_count = 0
    for node_id, members in terminal_groups.items():
        if len(members) < 2:
            continue
        fan_group_count += 1
        coordinates: dict[tuple[float, float], list[str]] = {}
        for edge_id, point in members:
            coordinates.setdefault(point, []).append(edge_id)
        collision = next((edge_ids for edge_ids in coordinates.values() if len(edge_ids) > 1), None)
        if collision:
            raise ProfileRenderError(
                "renderer-terminal-port-collision",
                f"Incident fan at node {node_id} reuses one terminal port for edges {', '.join(sorted(collision))}.",
            )

    edge_ids = sorted(routed)
    proper_crossings: set[tuple[str, str, tuple[float, float]]] = set()
    used_crossing_declarations: set[tuple[str, tuple[float, float]]] = set()
    used_junctions: set[tuple[float, float]] = set()
    segment_count = sum(max(0, len(points) - 1) for points in routed.values())
    for left_position, left_id in enumerate(edge_ids):
        left_points = routed[left_id]
        for right_id in edge_ids[left_position + 1:]:
            right_points = routed[right_id]
            point_contacts: dict[tuple[float, float], tuple[bool, bool]] = {}
            for left_segment in zip(left_points, left_points[1:]):
                for right_segment in zip(right_points, right_points[1:]):
                    overlap = _collinear_overlap(*left_segment, *right_segment)
                    if overlap:
                        direction_left = (left_segment[1][0] - left_segment[0][0], left_segment[1][1] - left_segment[0][1])
                        direction_right = (right_segment[1][0] - right_segment[0][0], right_segment[1][1] - right_segment[0][1])
                        opposing = direction_left[0] * direction_right[0] + direction_left[1] * direction_right[1] < 0
                        qualifier = "opposing-direction " if opposing else ""
                        raise ProfileRenderError(
                            "renderer-edge-overlap",
                            f"Edges {left_id} and {right_id} have a {qualifier}shared segment from {overlap[0]} to {overlap[1]}.",
                        )
                    point = _segment_intersection(*left_segment, *right_segment)
                    if point is None:
                        continue
                    left_interior = _point_on_segment(point, *left_segment, interior=True)
                    right_interior = _point_on_segment(point, *right_segment, interior=True)
                    previous = point_contacts.get(point, (False, False))
                    point_contacts[point] = (previous[0] or left_interior, previous[1] or right_interior)
            for point, (left_interior, right_interior) in point_contacts.items():
                pair = frozenset({left_id, right_id})
                if (
                    _route_point_is_internal(point, left_points)
                    and _route_point_is_internal(point, right_points)
                    and (left_interior or right_interior)
                ):
                    declared_by = [edge_id for edge_id in (left_id, right_id) if point in declared_crossings[edge_id]]
                    if len(declared_by) != 1:
                        raise ProfileRenderError(
                            "renderer-crossing-undeclared",
                            f"Edges {left_id} and {right_id} cross at {point} without one explicit overpass declaration.",
                        )
                    proper_crossings.add((left_id, right_id, point))
                    used_crossing_declarations.add((declared_by[0], point))
                    continue
                declaration = junctions.get(point)
                if declaration is None or not pair <= declaration[1]:
                    raise ProfileRenderError(
                        "renderer-junction-undeclared",
                        f"Edges {left_id} and {right_id} form an undeclared junction at {point}.",
                    )
                used_junctions.add(point)
    for edge_id, points in declared_crossings.items():
        if any((edge_id, point) not in used_crossing_declarations for point in points):
            raise ProfileRenderError("renderer-crossing-declaration-orphan", f"Edge {edge_id} declares a crossing that is not present in the collision graph.")
    bridge_counts: dict[tuple[str, tuple[float, float]], int] = {}
    bridge_stroke_counts: dict[tuple[str, tuple[float, float]], int] = {}
    for element in root.iter():
        edge_id = element.get("data-crossing-bridge")
        stroke_edge_id = element.get("data-crossing-bridge-stroke")
        if edge_id is not None:
            try:
                point = _quantize_point((float(element.attrib["cx"]), float(element.attrib["cy"])))
            except (KeyError, ValueError) as error:
                raise ProfileRenderError("renderer-crossing-bridge-invalid", "A crossing bridge needs numeric cx/cy coordinates.") from error
            key = (edge_id, point)
            bridge_counts[key] = bridge_counts.get(key, 0) + 1
        if stroke_edge_id is not None:
            try:
                point = _quantize_point((float(element.attrib["data-crossing-x"]), float(element.attrib["data-crossing-y"])))
                x1, y1, x2, y2 = (float(element.attrib[field]) for field in ("x1", "y1", "x2", "y2"))
            except (KeyError, ValueError) as error:
                raise ProfileRenderError("renderer-crossing-bridge-invalid", "A crossing bridge stroke needs numeric point and line coordinates.") from error
            if math.hypot(x2 - x1, y2 - y1) <= GEOMETRY_TOLERANCE or not _point_on_segment(point, (x1, y1), (x2, y2), interior=True):
                raise ProfileRenderError("renderer-crossing-bridge-invalid", "A crossing bridge stroke must visibly span its declared crossing point.")
            key = (stroke_edge_id, point)
            bridge_stroke_counts[key] = bridge_stroke_counts.get(key, 0) + 1
    if (
        set(bridge_counts) != used_crossing_declarations
        or set(bridge_stroke_counts) != used_crossing_declarations
        or any(count != 1 for count in (*bridge_counts.values(), *bridge_stroke_counts.values()))
    ):
        raise ProfileRenderError("renderer-crossing-bridge-mismatch", "Every declared overpass needs exactly one edge-scoped bridge circle and stroke, with no orphan receipt.")
    if set(junctions) != used_junctions:
        raise ProfileRenderError("renderer-junction-declaration-orphan", "A declared junction is not backed by an edge collision.")
    return {
        "segment_count": segment_count,
        "proper_crossings": len(proper_crossings),
        "declared_junctions": len(used_junctions),
        "terminal_fan_groups": fan_group_count,
        "shared_segments": 0,
        "undeclared_junctions": 0,
    }


def validate_rendered_geometry(svg: str, ir: Mapping[str, Any], binding: Mapping[str, Any]) -> dict[str, Any]:
    """Validate actual SVG geometry, semantic coverage, ports, and route grammar."""

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise ProfileRenderError("renderer-svg-invalid", "Rendered SVG is not valid XML.") from error
    try:
        view_x, view_y, canvas_width, canvas_height = (float(value) for value in root.attrib["viewBox"].split())
        intrinsic_width = float(root.attrib["width"])
        intrinsic_height = float(root.attrib["height"])
    except (KeyError, TypeError, ValueError) as error:
        raise ProfileRenderError("renderer-canvas-invalid", "Rendered SVG needs numeric intrinsic dimensions and a four-value viewBox.") from error
    if (
        view_x != 0
        or view_y != 0
        or canvas_width <= 0
        or canvas_height <= 0
        or intrinsic_width <= 0
        or intrinsic_height <= 0
        or root.get("preserveAspectRatio") != "xMidYMid meet"
    ):
        raise ProfileRenderError("renderer-canvas-invalid", "Intrinsic canvas, viewBox, and aspect-ratio policy must describe one positive stable viewport.")
    bounded_receipts = 0
    for element in root.iter():
        if not all(field in element.attrib for field in ("data-x", "data-y", "data-w", "data-h")):
            continue
        receipt = _parse_box(element)
        bounded_receipts += 1
        if (
            receipt.w <= 0
            or receipt.h <= 0
            or receipt.x < -GEOMETRY_TOLERANCE
            or receipt.y < -GEOMETRY_TOLERANCE
            or receipt.x + receipt.w > canvas_width + GEOMETRY_TOLERANCE
            or receipt.y + receipt.h > canvas_height + GEOMETRY_TOLERANCE
        ):
            receipt_id = element.get("data-semantic-id") or element.get("data-node-id") or element.get("data-primitive") or "anonymous"
            raise ProfileRenderError("renderer-canvas-overflow", f"Rendered receipt {receipt_id} extends outside the canvas.")
    engine = str(binding["layout_engine"])
    selected_profile = str(binding.get("selected_profile", ""))
    if root.get("data-layout-engine") != engine or root.get("data-renderer-version") != RENDERER_VERSION:
        raise ProfileRenderError("renderer-receipt-mismatch", "Renderer receipt does not match the selected engine.")
    primitive = ENGINE_PRIMITIVES[engine]
    if not any(element.get("data-primitive") == primitive for element in root.iter()):
        raise ProfileRenderError("renderer-engine-grammar-missing", f"Engine {engine} omitted its required {primitive} primitive.")
    semantic_group_count = 0
    presentation_shells = [element for element in root.iter() if element.get("data-presentation-shell")]
    for shell in presentation_shells:
        if any(field in shell.attrib for field in ("data-semantic-id", "data-semantic-group-id", "data-member-ids")):
            raise ProfileRenderError("renderer-presentation-shell-semantic-leak", "Presentation shell cannot declare a semantic ID or semantic member set.")
    boxes: dict[str, Box] = {}
    for element in root.iter():
        node_id = element.get("data-node-id")
        if node_id:
            if node_id in boxes:
                raise ProfileRenderError("renderer-node-duplicate", f"Node {node_id} was emitted more than once.")
            boxes[node_id] = _parse_box(element)
    expected_nodes = {str(node["id"]) for node in ir["nodes"]}
    if set(boxes) != expected_nodes:
        raise ProfileRenderError("renderer-node-coverage", "Rendered node geometry does not exactly cover semantic nodes.")
    for node_id, box in boxes.items():
        if box.w <= 0 or box.h <= 0 or box.x < 0 or box.y < 0:
            raise ProfileRenderError("renderer-node-bounds", f"Node {node_id} has invalid bounds.")
    for element in root.iter():
        member_ids = element.get("data-member-ids", "").split()
        if not member_ids or not all(field in element.attrib for field in ("data-x", "data-y", "data-w", "data-h")):
            continue
        container = _parse_box(element)
        for member_id in member_ids:
            if member_id in boxes:
                member = boxes[member_id]
                if not (container.x <= member.cx <= container.x + container.w and container.y <= member.cy <= container.y + container.h):
                    raise ProfileRenderError("renderer-containment-breach", f"Node {member_id} is outside its rendered container.")
    expected_groups = {str(group["id"]): {str(member_id) for member_id in group["member_ids"]} for group in ir["groups"]}
    rendered_groups: dict[str, ET.Element] = {}
    for element in root.iter():
        group_id = element.get("data-semantic-group-id")
        if not group_id:
            continue
        if group_id in rendered_groups:
            raise ProfileRenderError("renderer-group-duplicate", f"Semantic group {group_id} was emitted more than once.")
        rendered_groups[group_id] = element
    group_receipt_required = engine in {"topology-and-zones", "integration-pipeline"} or ir["diagram"]["type"] == "fishbone"
    if group_receipt_required and set(rendered_groups) != set(expected_groups):
        raise ProfileRenderError("renderer-group-coverage", "Rendered group IDs do not exactly cover semantic groups from normalized IR.")
    if rendered_groups and not set(rendered_groups) <= set(expected_groups):
        raise ProfileRenderError("renderer-group-coverage", "Renderer invented a semantic group outside normalized IR.")
    for group_id, element in rendered_groups.items():
        expected_members = expected_groups[group_id]
        if element.get("data-semantic-id") != group_id:
            raise ProfileRenderError("renderer-group-receipt-mismatch", f"Semantic group {group_id} lost its exact ID receipt.")
        rendered_members = element.get("data-member-ids", "").split()
        if len(rendered_members) != len(set(rendered_members)) or set(rendered_members) != expected_members:
            raise ProfileRenderError("renderer-group-membership-drift", f"Semantic group {group_id} changed its exact member set.")
        if engine == "topology-and-zones" and element.get("data-primitive") != "zone-boundary":
            raise ProfileRenderError("renderer-group-receipt-mismatch", f"Topology group {group_id} lost its zone-boundary primitive.")
    semantic_group_count = len(rendered_groups)

    if engine == "runtime-deployment":
        expected_zone_members: list[list[str]] = []
        zone_index: dict[str, int] = {}
        for node in ir["nodes"]:
            zone_name = str(node.get("placement", {}).get("zone", "Unassigned zone"))
            if zone_name not in zone_index:
                zone_index[zone_name] = len(expected_zone_members)
                expected_zone_members.append([])
            expected_zone_members[zone_index[zone_name]].append(str(node["id"]))
        rendered_zones = [element for element in root.iter() if element.get("data-primitive") == "deployment-zone"]
        if [element.get("data-member-ids", "").split() for element in rendered_zones] != expected_zone_members:
            raise ProfileRenderError("renderer-deployment-zone-order", "Deployment zones changed first-seen request order or exact membership.")
        zone_x = [float(element.get("data-x", "nan")) for element in rendered_zones]
        if any(right <= left for left, right in zip(zone_x, zone_x[1:])):
            raise ProfileRenderError("renderer-deployment-zone-order", "Deployment zones do not progress left-to-right in first-seen order.")

    expected_lanes = {str(lane["id"]): lane for lane in ir["lanes"]}
    rendered_lanes = {element.get("data-lane-id"): element for element in root.iter() if element.get("data-lane-id")}
    if expected_lanes and engine in {"lane-interaction", "containment-stack"} and set(rendered_lanes) != set(expected_lanes):
        raise ProfileRenderError("renderer-lane-coverage", "Rendered lane IDs do not exactly cover normalized IR lanes.")
    for lane_id, lane in expected_lanes.items():
        element = rendered_lanes.get(lane_id)
        if element is None:
            continue
        if element.get("data-lane-order") != str(lane["order"]):
            raise ProfileRenderError("renderer-lane-order", f"Lane {lane_id} changed its declared order.")
        if element.get("data-lane-owner") != str(lane["owner"]):
            raise ProfileRenderError("renderer-lane-owner", f"Lane {lane_id} changed its declared owner.")
        rendered_members = element.get("data-member-ids", "").split()
        if len(rendered_members) != len(set(rendered_members)) or set(rendered_members) != set(lane["member_ids"]):
            raise ProfileRenderError("renderer-lane-membership", f"Lane {lane_id} changed its exact member set.")

    if selected_profile == "layers":
        if root.get("data-presentation-variant-id") != "layers" or root.get("data-reading-direction") != "top-to-bottom":
            raise ProfileRenderError("renderer-layer-presentation", "Layers must declare the exact top-to-bottom presentation mapping.")
        abstraction_axes = [element for element in root.iter() if element.get("data-abstraction-axis") == "true"]
        if len(abstraction_axes) != 1:
            raise ProfileRenderError("renderer-layer-presentation", "Layers need exactly one visible abstraction axis.")
        abstraction_axis = abstraction_axes[0]
        if (
            abstraction_axis.get("data-abstraction-axis-label") != "Mức trừu tượng"
            or abstraction_axis.get("data-abstraction-axis-top") != "Cao"
            or abstraction_axis.get("data-abstraction-axis-bottom") != "Thấp"
        ):
            raise ProfileRenderError("renderer-layer-presentation", "Layers changed the Cao-to-Thấp abstraction axis.")
        ordered_lane_elements = [rendered_lanes[str(lane["id"])] for lane in _ordered(ir["lanes"])]
        lane_boxes = [_parse_box(element) for element in ordered_lane_elements]
        if any(right.y <= left.y for left, right in zip(lane_boxes, lane_boxes[1:])):
            raise ProfileRenderError("renderer-layer-presentation", "Layer bands do not follow declared top-to-bottom lane order.")
        if lane_boxes and (len({round(box.x, GEOMETRY_DECIMALS) for box in lane_boxes}) != 1 or len({round(box.w, GEOMETRY_DECIMALS) for box in lane_boxes}) != 1):
            raise ProfileRenderError("renderer-layer-presentation", "Layer bands must share one full-width horizontal span.")

    expected_members = {
        str(member["id"]): str(node["id"])
        for node in ir["nodes"]
        for member in node.get("members", ())
    }
    rendered_members = {element.get("data-member-id"): element for element in root.iter() if element.get("data-member-id")}
    if expected_members and engine == "compartment-model" and set(rendered_members) != set(expected_members):
        raise ProfileRenderError("renderer-member-coverage", "Rendered member rows do not exactly cover normalized IR members.")
    for member_id, owner_id in expected_members.items():
        if member_id in rendered_members and rendered_members[member_id].get("data-owner-node") != owner_id:
            raise ProfileRenderError("renderer-member-owner", f"Member {member_id} moved to another compartment.")

    expected_axes = {str(axis["id"]): axis for axis in ir["axes"]}
    rendered_axes = {element.get("data-axis-id"): element for element in root.iter() if element.get("data-axis-id")}
    if expected_axes and engine in {"quantitative", "spatial-matrix"} and set(rendered_axes) != set(expected_axes):
        raise ProfileRenderError("renderer-axis-coverage", "Rendered axis receipts do not exactly cover normalized IR axes.")
    for axis_id, axis in expected_axes.items():
        element = rendered_axes.get(axis_id)
        if element is None:
            continue
        for field_name in ("dimension", "scale", "domain_min", "domain_max", "unit"):
            expected_value = axis.get(field_name)
            observed_value = element.get(f"data-axis-{field_name.replace('_', '-')}")
            if observed_value != (None if expected_value is None else str(expected_value)):
                raise ProfileRenderError("renderer-axis-receipt", f"Axis {axis_id} changed {field_name}.")

    if ir["diagram"]["type"] == "pyramid-funnel":
        funnel_series = ir["series"][0]
        unit = str(funnel_series.get("unit") or "").strip()
        tiers = {
            element.get("data-semantic-id"): element
            for element in root.iter()
            if element.get("data-mark") == "funnel-tier"
        }
        expected_data = {str(item["id"]): item for item in funnel_series["data"]}
        if set(tiers) != set(expected_data):
            raise ProfileRenderError("renderer-funnel-value-label", "Funnel tiers do not exactly cover source data.")
        for item_id, item in expected_data.items():
            tier = tiers[item_id]
            expected_label = f"{item['domain']} · {item['value']}" + (f" {unit}" if unit else "")
            visible_labels = [child.text or "" for child in tier if child.tag == _tag("text")]
            if (
                visible_labels != [expected_label]
                or tier.get("data-series-id") != str(funnel_series["id"])
                or tier.get("data-visible-value-label") != expected_label
                or tier.get("data-visible-unit") != unit
            ):
                raise ProfileRenderError("renderer-funnel-value-label", f"Funnel tier {item_id} omitted its exact visible value/unit label.")

    needs_series_identity = len(ir["series"]) > 1 and (
        selected_profile in {"slope-graph", "bubble"}
        or (ir["diagram"]["type"] in {"scatter-plot", "quadrant"} and selected_profile != "bubble")
    )
    if needs_series_identity:
        expected_series = {str(series["id"]): series for series in ir["series"]}
        legend_entries = {
            element.get("data-series-legend-id"): element
            for element in root.iter()
            if element.get("data-series-legend-id")
        }
        if set(legend_entries) != set(expected_series):
            raise ProfileRenderError("renderer-series-identity", "Quantitative legend does not exactly cover source series.")
        patterns = [legend_entries[series_id].get("data-series-pattern") for series_id in expected_series]
        if None in patterns or len(set(patterns)) != len(patterns):
            raise ProfileRenderError("renderer-series-identity", "Quantitative series need unique non-color patterns.")
        for series_id, series in expected_series.items():
            entry = legend_entries[series_id]
            legend_marks = [
                element
                for element in entry.iter()
                if element.get("data-series-legend-mark") == series_id
            ]
            labels = [
                element.text or ""
                for element in entry.iter()
                if element.get("data-series-label-for") == series_id
            ]
            if labels != [str(series["label"])] or len(legend_marks) != 1:
                raise ProfileRenderError("renderer-series-identity", f"Series {series_id} lost its exact visible legend label.")
            pattern = entry.get("data-series-pattern")
            if legend_marks[0].get("data-series-pattern") != pattern:
                raise ProfileRenderError("renderer-series-identity", f"Series {series_id} lost its exact legend-mark pattern binding.")
            expected_items = {str(item["id"]) for item in series["data"]}
            rendered_items = {
                str(element.get("data-semantic-id"))
                for element in root.iter()
                if element.get("data-series-id") == series_id
                and element.get("data-mark") in {"observation", "endpoint", "bubble"}
                and element.get("data-series-pattern") == pattern
            }
            if rendered_items != expected_items:
                raise ProfileRenderError("renderer-series-identity", f"Series {series_id} marks lost their exact pattern binding.")
            if selected_profile == "slope-graph":
                slope_lines = [
                    element for element in root.iter()
                    if element.get("data-mark") == "slope"
                    and element.get("data-series-id") == series_id
                    and element.get("data-series-pattern") == pattern
                ]
                if len(slope_lines) != 1:
                    raise ProfileRenderError("renderer-series-identity", f"Slope series {series_id} lost its exact line-pattern binding.")

    if selected_profile == "dumbbell":
        if root.get("data-axis-presentation-mapping") != "semantic-y-to-horizontal semantic-x-to-vertical":
            raise ProfileRenderError("renderer-axis-presentation", "Dumbbell must declare semantic axis transposition.")
        for dimension, presentation in (("x", "vertical"), ("y", "horizontal")):
            axis = _axis(ir, dimension)
            if axis and rendered_axes[str(axis["id"])].get("data-axis-presentation") != presentation:
                raise ProfileRenderError("renderer-axis-presentation", f"Dumbbell {dimension}-axis lost its {presentation} presentation mapping.")
    elif selected_profile == "ridgeline":
        if root.get("data-axis-presentation-mapping") != "semantic-y-to-local-ridge-amplitude semantic-x-to-horizontal":
            raise ProfileRenderError("renderer-axis-presentation", "Ridgeline must declare local amplitude mapping.")
        x_axis, y_axis = _axis(ir, "x"), _axis(ir, "y")
        if not x_axis or not y_axis:
            raise ProfileRenderError("renderer-axis-presentation", "Ridgeline requires exact x and y axes.")
        if rendered_axes[str(x_axis["id"])].get("data-axis-presentation") != "horizontal" or rendered_axes[str(y_axis["id"])].get("data-axis-presentation") != "local-ridge-amplitude":
            raise ProfileRenderError("renderer-axis-presentation", "Ridgeline axis receipts overstate a global vertical amplitude axis.")
        header_roles = {
            element.get("data-ridgeline-header-role"): element
            for element in root.iter()
            if element.get("data-ridgeline-header-role")
        }
        expected_header_roles = {
            "shared-scale-heading": "ridgeline-heading",
            "amplitude-axis-title": "ridgeline-axis-title",
            "distribution-metadata": "ridgeline-distribution-metadata",
        }
        if set(header_roles) != set(expected_header_roles):
            raise ProfileRenderError("renderer-ridgeline-header-layout", "Ridgeline must materialize exactly three independently bound header roles.")
        header_y = []
        for role, band in expected_header_roles.items():
            element = header_roles[role]
            if element.get("data-layout-band") != band:
                raise ProfileRenderError("renderer-ridgeline-header-layout", f"Ridgeline header role {role} changed its layout band.")
            try:
                header_y.append(float(element.attrib["y"]))
            except (KeyError, ValueError) as error:
                raise ProfileRenderError("renderer-ridgeline-header-layout", f"Ridgeline header role {role} omitted its bounded y coordinate.") from error
        if header_y != sorted(header_y) or min(right - left for left, right in zip(header_y, header_y[1:])) < 24:
            raise ProfileRenderError("renderer-ridgeline-header-layout", "Ridgeline header roles are not separated into collision-free vertical bands.")
        local_receipts = {
            element.get("data-local-amplitude-series"): element
            for element in root.iter()
            if element.get("data-local-amplitude-series")
        }
        if set(local_receipts) != {str(series["id"]) for series in ir["series"]}:
            raise ProfileRenderError("renderer-axis-presentation", "Ridgeline local amplitude receipts do not exactly cover series.")
        for series in ir["series"]:
            receipt = local_receipts[str(series["id"])]
            if (
                receipt.get("data-local-amplitude-axis-id") != str(y_axis["id"])
                or receipt.get("data-local-amplitude-min") != str(y_axis["domain_min"])
                or receipt.get("data-local-amplitude-max") != str(y_axis["domain_max"])
                or receipt.get("data-local-amplitude-normalization") != str(series["distribution"]["amplitude_normalization"])
            ):
                raise ProfileRenderError("renderer-axis-presentation", f"Ridgeline series {series['id']} changed its local amplitude scale.")
        derived_profiles = derive_ridgeline_profiles(ir)
        ridges = {
            element.get("data-series-id"): element
            for element in root.iter()
            if element.get("data-mark") == "ridge"
        }
        if set(ridges) != {str(series["id"]) for series in ir["series"]}:
            raise ProfileRenderError("renderer-ridgeline-profile", "Ridgeline shapes do not exactly cover source series.")
        domain_min, domain_max = float(x_axis["domain_min"]), float(x_axis["domain_max"])
        for series in ir["series"]:
            series_id = str(series["id"])
            ridge = ridges[series_id]
            distribution = series["distribution"]
            expected_bandwidth = distribution["bandwidth"]
            if (
                ridge.get("data-distribution-method") != str(distribution["method"])
                or ridge.get("data-distribution-bandwidth") != (None if expected_bandwidth is None else _fmt(float(expected_bandwidth)))
                or ridge.get("data-bin-count") != str(distribution["bin_count"])
                or ridge.get("data-normalization") != str(distribution["amplitude_normalization"])
            ):
                raise ProfileRenderError("renderer-ridgeline-profile", f"Ridgeline series {series_id} changed its derivation contract.")
            try:
                baseline = float(ridge.attrib["data-ridge-baseline"])
                amplitude_pixels = float(ridge.attrib["data-ridge-amplitude-pixels"])
            except (KeyError, ValueError) as error:
                raise ProfileRenderError("renderer-ridgeline-profile", f"Ridgeline series {series_id} omitted numeric scale receipts.") from error
            points = _points(ridge.get("points", ""))
            grid = [float(value) for value in derived_profiles["grid"]]
            amplitudes = [float(value) for value in derived_profiles["amplitudes"][series_id]]
            if len(points) != len(grid) + 2 or abs(points[0][1] - baseline) > GEOMETRY_TOLERANCE or abs(points[-1][1] - baseline) > GEOMETRY_TOLERANCE:
                raise ProfileRenderError("renderer-ridgeline-profile", f"Ridgeline series {series_id} changed its baseline-terminated shape.")
            left_x, right_x = points[0][0], points[-1][0]
            for observed, grid_value, normalized in zip(points[1:-1], grid, amplitudes):
                expected_x = _scale(grid_value, domain_min, domain_max, left_x, right_x)
                expected_y = baseline - amplitude_pixels * normalized
                if abs(observed[0] - expected_x) > GEOMETRY_TOLERANCE or abs(observed[1] - expected_y) > GEOMETRY_TOLERANCE:
                    raise ProfileRenderError("renderer-ridgeline-profile", f"Ridgeline series {series_id} does not match its canonical derived density.")

    if engine == "hierarchy":
        for edge in ir["edges"]:
            if edge["kind"] == "reports-to" and not boxes[edge["target"]].cy < boxes[edge["source"]].cy:
                raise ProfileRenderError("renderer-reporting-rank-direction", "A reports-to manager must render above the subordinate.")
    node_items = sorted(boxes.items())
    for index, (left_id, left) in enumerate(node_items):
        for right_id, right in node_items[index + 1:]:
            overlap_w = min(left.x + left.w, right.x + right.w) - max(left.x, right.x)
            overlap_h = min(left.y + left.h, right.y + right.h) - max(left.y, right.y)
            if overlap_w > 1 and overlap_h > 1:
                raise ProfileRenderError("renderer-node-overlap", f"Nodes {left_id} and {right_id} overlap.")
    edge_elements = {element.get("data-edge-id"): element for element in root.iter() if element.get("data-edge-id")}
    expected_edges = {str(edge["id"]): edge for edge in ir["edges"]}
    if set(edge_elements) != set(expected_edges):
        raise ProfileRenderError("renderer-edge-coverage", "Rendered connector geometry does not exactly cover semantic edges.")
    for edge_id, edge in expected_edges.items():
        element = edge_elements[edge_id]
        if element.get("data-source") != edge["source"] or element.get("data-target") != edge["target"]:
            raise ProfileRenderError("renderer-edge-endpoint", f"Edge {edge_id} changed its semantic endpoints.")
        for field_name in ("source_member", "target_member"):
            expected_member = edge.get(field_name)
            observed_member = element.get(f"data-{field_name.replace('_', '-')}")
            if observed_member != (None if expected_member is None else str(expected_member)):
                raise ProfileRenderError("renderer-edge-member-endpoint", f"Edge {edge_id} changed its named member endpoint.")
        points = _points(element.get("points", ""))
        if len(points) < 2:
            raise ProfileRenderError("renderer-route-empty", f"Edge {edge_id} has no continuous route.")
        if any(
            x < -GEOMETRY_TOLERANCE
            or y < -GEOMETRY_TOLERANCE
            or x > canvas_width + GEOMETRY_TOLERANCE
            or y > canvas_height + GEOMETRY_TOLERANCE
            for x, y in points
        ):
            raise ProfileRenderError("renderer-canvas-overflow", f"Edge {edge_id} extends outside the canvas.")
        family = element.get("data-route-family")
        if family in {"orthogonal", "ribbon"} and any(abs(x1 - x2) > 1e-6 and abs(y1 - y2) > 1e-6 for (x1, y1), (x2, y2) in zip(points, points[1:])):
            raise ProfileRenderError("renderer-route-family", f"Edge {edge_id} violates orthogonal routing.")
        if family in {"orthogonal", "ribbon", "message", "fishbone", "cycle-arc"}:
            for node_id, box in boxes.items():
                if node_id in {edge["source"], edge["target"]}:
                    continue
                if any(_segment_hits_box(start, end, box) for start, end in zip(points, points[1:])):
                    raise ProfileRenderError("renderer-route-obstruction", f"Edge {edge_id} crosses unrelated node {node_id}.")
        if boxes and edge["source"] in boxes and edge["target"] in boxes and family != "message":
            if not _on_boundary(points[0], boxes[edge["source"]]) or not _on_boundary(points[-1], boxes[edge["target"]]):
                raise ProfileRenderError("renderer-port-detached", f"Edge {edge_id} is detached from a source or target boundary.")
            if any(
                _segment_hits_box(start, end, boxes[edge[endpoint]])
                for endpoint in ("source", "target")
                for start, end in zip(points, points[1:])
            ):
                raise ProfileRenderError("renderer-route-endpoint-interior", f"Edge {edge_id} traverses a source or target node interior.")
        if edge.get("directed") and element.get("marker-end") != "url(#arrow)":
            raise ProfileRenderError("renderer-arrow-missing", f"Directed edge {edge_id} has no arrowhead.")
    collision_graph = _validate_edge_collision_graph(root, edge_elements, expected_edges)
    if selected_profile == "dumbbell":
        if len(ir["series"]) != 2:
            raise ProfileRenderError("renderer-comparison-contract", "Dumbbell requires exactly two comparison series.")
        comparison_deltas = {
            element.get("data-domain"): element
            for element in root.iter()
            if element.get("data-mark") == "comparison-delta"
        }
        first_by_domain = {str(item["domain"]): item for item in ir["series"][0]["data"]}
        second_by_domain = {str(item["domain"]): item for item in ir["series"][1]["data"]}
        if set(comparison_deltas) != set(first_by_domain) or set(first_by_domain) != set(second_by_domain):
            raise ProfileRenderError("renderer-comparison-contract", "Dumbbell delta labels do not exactly cover comparison domains.")
        for domain, first in first_by_domain.items():
            delta = float(second_by_domain[domain]["value"]) - float(first["value"])
            expected_value = f"{delta:g}"
            expected_text = f"{delta:+g}" if delta else "0"
            element = comparison_deltas[domain]
            if element.get("data-delta") != expected_value or (element.text or "") != expected_text:
                raise ProfileRenderError("renderer-comparison-contract", f"Dumbbell domain {domain} has an incorrect visible signed gap.")
    elif selected_profile == "slope-graph":
        slope_deltas = {
            element.get("data-series-id"): element
            for element in root.iter()
            if element.get("data-mark") == "slope-delta"
        }
        if set(slope_deltas) != {str(series["id"]) for series in ir["series"]}:
            raise ProfileRenderError("renderer-comparison-contract", "Slope delta labels do not exactly cover series.")
        for series in ir["series"]:
            first, second = series["data"]
            delta = float(second["value"]) - float(first["value"])
            expected_value = f"{delta:g}"
            expected_text = f"{delta:+g}" if delta else "0"
            element = slope_deltas[str(series["id"])]
            if element.get("data-delta") != expected_value or (element.text or "") != expected_text:
                raise ProfileRenderError("renderer-comparison-contract", f"Slope series {series['id']} has an incorrect visible delta.")
    elif selected_profile == "bubble":
        size_axis = _axis(ir, "size")
        legends = [element for element in root.iter() if element.get("data-size-legend") == "true"]
        if size_axis is None or len(legends) != 1:
            raise ProfileRenderError("renderer-size-legend", "Bubble needs exactly one source-bound size legend.")
        legend = legends[0]
        for field_name in ("label", "unit", "domain_min", "domain_max"):
            expected_value = size_axis.get(field_name)
            expected_text = "" if expected_value is None else str(expected_value)
            if legend.get(f"data-size-legend-{field_name.replace('_', '-')}") != expected_text:
                raise ProfileRenderError("renderer-size-legend", f"Bubble size legend changed {field_name}.")
        bubbles = {
            str(element.get("data-semantic-id")): element
            for element in root.iter()
            if element.get("data-mark") == "bubble"
        }
        expected_items = {
            str(item["id"]): (str(series["id"]), item)
            for series in ir["series"]
            for item in series["data"]
        }
        if set(bubbles) != set(expected_items):
            raise ProfileRenderError("renderer-bubble-geometry", "Bubble marks do not exactly cover every series datum.")
        plot_frames = [element for element in root.iter() if element.get("data-primitive") == "plot-frame"]
        x_axis, y_axis = _axis(ir, "x"), _axis(ir, "y")
        if len(plot_frames) != 1 or x_axis is None or y_axis is None:
            raise ProfileRenderError("renderer-bubble-geometry", "Bubble needs one plot frame and exact x/y axes.")
        frame = _parse_box(plot_frames[0])
        plot = Box(frame.x + 70, frame.y + 64, frame.w - 110, frame.h - 110)
        datum_labels = {
            str(element.get("data-label-for")): element
            for element in root.iter()
            if element.get("data-label-for")
        }
        if set(datum_labels) != set(expected_items):
            raise ProfileRenderError("renderer-bubble-geometry", "Bubble visible labels do not exactly cover every datum.")
        for item_id, (series_id, item) in expected_items.items():
            element = bubbles[item_id]
            expected_x = _scale(float(item["x_value"]), float(x_axis["domain_min"]), float(x_axis["domain_max"]), plot.x, plot.x + plot.w)
            expected_y = _scale(float(item["y_value"]), float(y_axis["domain_min"]), float(y_axis["domain_max"]), plot.y + plot.h, plot.y)
            expected_radius = 34.0 * math.sqrt(max(0.0, float(item["size_value"])) / max(1.0, float(size_axis["domain_max"])))
            if (
                element.get("data-series-id") != series_id
                or element.get("data-size-unit") != str(item["size_unit"])
                or element.get("data-size-value") != _fmt(float(item["size_value"]))
                or abs(float(element.get("cx", "nan")) - expected_x) > GEOMETRY_TOLERANCE
                or abs(float(element.get("cy", "nan")) - expected_y) > GEOMETRY_TOLERANCE
                or abs(float(element.get("r", "nan")) - expected_radius) > GEOMETRY_TOLERANCE
                or (datum_labels[item_id].text or "") != str(item.get("label", item_id))
            ):
                raise ProfileRenderError("renderer-bubble-geometry", f"Bubble datum {item_id} changed its series, coordinates, area, unit, or visible label.")
    mark_ids = {str(item["id"]) for series in ir["series"] for item in series["data"]}
    rendered_mark_ids = [
        str(element.get("data-semantic-id"))
        for element in root.iter()
        if element.get("data-semantic-id") in mark_ids
    ]
    if set(rendered_mark_ids) != mark_ids or len(rendered_mark_ids) != len(mark_ids):
        raise ProfileRenderError("renderer-mark-coverage", "Rendered quantitative marks must cover every semantic datum exactly once.")
    return {
        "status": "pass",
        "engine": engine,
        "nodes": len(boxes),
        "edges": len(edge_elements),
        "marks": len(mark_ids),
        "primitive": primitive,
        "semantic_groups": semantic_group_count,
        "semantic_group_validation": "pass" if group_receipt_required else "not-applicable",
        "semantic_lanes": len(rendered_lanes),
        "semantic_lane_validation": "pass" if expected_lanes and engine in {"lane-interaction", "containment-stack"} else "not-applicable",
        "semantic_members": len(rendered_members),
        "semantic_member_validation": "pass" if expected_members and engine == "compartment-model" else "not-applicable",
        "semantic_axes": len(rendered_axes),
        "semantic_axis_validation": "pass" if expected_axes and engine in {"quantitative", "spatial-matrix"} else "not-applicable",
        "presentation_shells": len(presentation_shells),
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
            "preserve_aspect_ratio": "xMidYMid meet",
            "bounded_receipts": bounded_receipts,
            "overflow": 0,
        },
        "collision_graph": collision_graph,
    }


__all__ = [
    "CANVAS_PRESETS", "ENGINE_PRIMITIVES", "ENGINE_RENDERERS", "ProfileRenderError",
    "RENDERER_VERSION", "render_profiled_svg", "validate_rendered_geometry",
]
