"""Original P-06 visual tokens, geometry primitives, and hard checks."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
TOKEN_PATH = SCRIPT_DIR.parent / "references" / "visual-system.json"


class VisualError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    def expanded(self, amount: float) -> "Rect":
        return Rect(self.x - amount, self.y - amount, self.width + 2 * amount, self.height + 2 * amount)


@dataclass(frozen=True)
class Route:
    edge_id: str
    source_id: str
    target_id: str
    points: tuple[tuple[float, float], ...]


def load_visual_system() -> dict[str, Any]:
    with TOKEN_PATH.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if set(value) != {"schema_version", "primitives", "modes"} or value["schema_version"] != "1.0":
        raise VisualError("token-schema-invalid", "Visual token file does not match the P-06 contract.")
    if set(value["modes"]) != {"neutral-light", "neutral-dark", "editorial"}:
        raise VisualError("mode-inventory-invalid", "Exactly the three approved static modes are required.")
    return value


def _rgb(hex_color: str) -> tuple[float, float, float]:
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith("#"):
        raise VisualError("color-invalid", f"Invalid opaque color token: {hex_color!r}")
    try:
        return tuple(int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5))  # type: ignore[return-value]
    except ValueError as error:
        raise VisualError("color-invalid", f"Invalid opaque color token: {hex_color!r}") from error


def relative_luminance(hex_color: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
    red, green, blue = (_rgb(hex_color))
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def contrast_report(system: Mapping[str, Any]) -> list[dict[str, Any]]:
    pairs = (
        ("text", "canvas", 4.5),
        ("text", "surface", 4.5),
        ("muted", "canvas", 4.5),
        ("on_accent", "accent", 4.5),
        ("money_text", "money_fill", 4.5),
        ("document_stroke", "document_fill", 3.0),
        ("file_stroke", "file_fill", 3.0),
        ("series_1", "canvas", 3.0),
        ("series_2", "canvas", 3.0),
    )
    report: list[dict[str, Any]] = []
    for mode, tokens in system["modes"].items():
        for foreground, background, threshold in pairs:
            ratio = contrast_ratio(tokens[foreground], tokens[background])
            report.append({"mode": mode, "foreground": foreground, "background": background, "ratio": round(ratio, 3), "threshold": threshold, "status": "pass" if ratio >= threshold else "fail"})
    return report


def rects_overlap(first: Rect, second: Rect, gap: float = 0) -> bool:
    return not (
        first.right + gap <= second.left
        or second.right + gap <= first.left
        or first.bottom + gap <= second.top
        or second.bottom + gap <= first.top
    )


def segment_intersects_rect(start: tuple[float, float], end: tuple[float, float], rect: Rect) -> bool:
    x1, y1 = start
    x2, y2 = end
    if x1 == x2:
        return rect.left < x1 < rect.right and max(min(y1, y2), rect.top) < min(max(y1, y2), rect.bottom)
    if y1 == y2:
        return rect.top < y1 < rect.bottom and max(min(x1, x2), rect.left) < min(max(x1, x2), rect.right)
    raise VisualError("route-not-orthogonal", "Pilot routes must use orthogonal segments.")


def route_intersects_rect(route: Route, rect: Rect) -> bool:
    return any(segment_intersects_rect(start, end, rect) for start, end in zip(route.points, route.points[1:]))


def _on_boundary(point: tuple[float, float], rect: Rect, tolerance: float = 0.1) -> bool:
    x, y = point
    horizontal = rect.left - tolerance <= x <= rect.right + tolerance and (math.isclose(y, rect.top, abs_tol=tolerance) or math.isclose(y, rect.bottom, abs_tol=tolerance))
    vertical = rect.top - tolerance <= y <= rect.bottom + tolerance and (math.isclose(x, rect.left, abs_tol=tolerance) or math.isclose(x, rect.right, abs_tol=tolerance))
    return horizontal or vertical


def validate_geometry(canvas: Rect, nodes: Mapping[str, Rect], routes: Iterable[Route], *, minimum_gap: float = 8) -> dict[str, Any]:
    node_items = list(nodes.items())
    for node_id, rect in node_items:
        if rect.left < canvas.left or rect.top < canvas.top or rect.right > canvas.right or rect.bottom > canvas.bottom:
            raise VisualError("node-out-of-bounds", f"Node {node_id} is outside the canvas.")
    for index, (first_id, first) in enumerate(node_items):
        for second_id, second in node_items[index + 1:]:
            if rects_overlap(first, second, minimum_gap):
                raise VisualError("node-overlap", f"Nodes {first_id} and {second_id} overlap or violate clearance.")
    route_count = 0
    for route in routes:
        route_count += 1
        if route.source_id not in nodes or route.target_id not in nodes:
            raise VisualError("route-endpoint-missing", f"Route {route.edge_id} has a missing endpoint.")
        if len(route.points) < 2 or not _on_boundary(route.points[0], nodes[route.source_id]) or not _on_boundary(route.points[-1], nodes[route.target_id]):
            raise VisualError("route-endpoint-invalid", f"Route {route.edge_id} is not attached to both node bounds.")
        for node_id, rect in nodes.items():
            if node_id not in {route.source_id, route.target_id} and route_intersects_rect(route, rect.expanded(1)):
                raise VisualError("route-crosses-node", f"Route {route.edge_id} crosses unrelated node {node_id}.")
    return {"nodes": len(nodes), "routes": route_count, "status": "pass"}


def validate_contrast(system: Mapping[str, Any]) -> list[dict[str, Any]]:
    report = contrast_report(system)
    failures = [item for item in report if item["status"] != "pass"]
    if failures:
        first = failures[0]
        raise VisualError("contrast-failure", f"{first['mode']} {first['foreground']} on {first['background']} is {first['ratio']}.")
    return report


__all__ = ["Rect", "Route", "VisualError", "contrast_ratio", "contrast_report", "load_visual_system", "route_intersects_rect", "validate_contrast", "validate_geometry"]
