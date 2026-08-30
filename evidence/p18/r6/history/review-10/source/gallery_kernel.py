"""P-18R6 neutral-light engine anchors.

This QA-only module is an original, engine-specific implementation.  It reuses
the approved P-18R5 font-resolution contract as an internal dependency, but it
does not import or adapt the rejected P-18R3 renderer or any upstream visual
asset.  Every function below owns a distinct geometry/silhouette.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import importlib.util
from math import sqrt
from pathlib import Path
import sys
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[4]
R5_KERNEL_PATH = ROOT / "evidence/p18/r5/source/master_visual_kernel.py"
_R5_NAME = "p18r5_master_visual_kernel"
_SPEC = importlib.util.spec_from_file_location(_R5_NAME, R5_KERNEL_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Unable to load frozen P-18R5 master visual kernel")
_R5 = importlib.util.module_from_spec(_SPEC)
sys.modules[_R5_NAME] = _R5
_SPEC.loader.exec_module(_R5)


TOKENS = {
    "canvas": "#f7f6f2",
    "paper": "#fbfaf7",
    "surface": "#ffffff",
    "surface_soft": "#eeece7",
    "surface_slate": "#e8ebee",
    "ink": "#252b3c",
    "ink_soft": "#53627b",
    "ink_faint": "#778194",
    "line": "#4f5e76",
    "line_soft": "#c7ccd2",
    "grid": "#d9d7d2",
    "accent": "#f26a32",
    "accent_soft": "#f8e7dd",
    "accent_text": "#df5522",
    "blue": "#2f65af",
    "green": "#7c9167",
    "amber": "#b9894b",
    "plum": "#756b7f",
}

CORNER_STYLES = frozenset({"rounded", "straight"})


@dataclass(frozen=True)
class Anchor:
    order: int
    engine: str
    canonical_type: str
    filename: str
    title: str
    takeaway: str
    svg: str
    facts: tuple[tuple[str, str], ...]


def _load_typography():
    resolved = _R5.resolve_default_typography()
    return resolved, _R5.FontMetricEngine(resolved)


TYPOGRAPHY, METRICS = _load_typography()


def resolved_family(role: str) -> str:
    return TYPOGRAPHY[role].resolved_family


def _attrs(values: dict[str, object]) -> str:
    return " ".join(f'{escape(str(key))}="{escape(str(value))}"' for key, value in values.items())


def _text(x: float, y: float, value: str, cls: str = "material", anchor: str = "start", **extra: object) -> str:
    attrs = {"class": cls, "x": f"{x:.1f}", "y": f"{y:.1f}", "text-anchor": anchor, **extra}
    return f"<text {_attrs(attrs)}>{escape(value)}</text>"


def _tspans(x: float, y: float, lines: Iterable[str], cls: str, line_height: int, anchor: str = "start") -> str:
    content = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        content.append(f'<tspan x="{x:.1f}" dy="{dy}">{escape(line)}</tspan>')
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{"".join(content)}</text>'


def _rect(x: float, y: float, w: float, h: float, cls: str = "node", rx: float = 14, **extra: object) -> str:
    attrs = {"class": cls, "x": x, "y": y, "width": w, "height": h, "rx": rx, **extra}
    return f"<rect {_attrs(attrs)}/>"


def _line(x1: float, y1: float, x2: float, y2: float, cls: str = "wire", **extra: object) -> str:
    return f'<line {_attrs({"class": cls, "x1": x1, "y1": y1, "x2": x2, "y2": y2, **extra})}/>'


def _path(d: str, cls: str = "wire", **extra: object) -> str:
    return f'<path {_attrs({"class": cls, "d": d, **extra})}/>'


def orthogonal_route_d(
    points: Iterable[tuple[float, float]],
    corner_style: str = "rounded",
    radius: float = 14.0,
) -> str:
    """Serialize one chart-level orthogonal corner policy."""

    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    route = tuple(_R5.Point(float(x), float(y)) for x, y in points)
    if len(route) < 2:
        raise ValueError("A route needs at least two points")
    if corner_style == "rounded":
        return _R5.rounded_orthogonal_path(route, radius)
    return " ".join(
        [f"M {route[0].x:.2f} {route[0].y:.2f}"]
        + [f"L {point.x:.2f} {point.y:.2f}" for point in route[1:]]
    )


def _orthogonal_path(
    points: Iterable[tuple[float, float]],
    cls: str = "wire",
    *,
    marker: str | None = None,
    radius: float = 14.0,
    corner_style: str = "rounded",
    **extra: object,
) -> str:
    """Serialize an orthogonal route under one chart-level corner policy."""

    route = tuple((float(x), float(y)) for x, y in points)
    attrs: dict[str, object] = {
        "data-route-style": f"{corner_style}-orthogonal",
        "data-corner-style": corner_style,
        "data-turn-count": max(0, len(route) - 2),
        **extra,
    }
    if marker:
        attrs["marker-end"] = marker
    return _path(orthogonal_route_d(route, corner_style, radius), cls, **attrs)


def _straight_bridged_route_d(
    route: tuple[object, ...],
    mark: object,
    segment_index: int,
    direction: float,
) -> str:
    """Keep chart corners sharp while preserving the shared cubic hop geometry."""

    commands = [f"M {route[0].x:.2f} {route[0].y:.2f}"]
    hop = _R5.bridge_open_hop_path(mark, direction)
    hop_commands = hop.split(" ", 3)[3]
    hop_start_x = mark.point.x - direction * mark.radius
    for index, point in enumerate(route[1:]):
        if index == segment_index:
            commands.extend(
                [
                    f"L {hop_start_x:.2f} {mark.point.y:.2f}",
                    hop_commands,
                    f"L {point.x:.2f} {point.y:.2f}",
                ]
            )
        else:
            commands.append(f"L {point.x:.2f} {point.y:.2f}")
    return " ".join(commands)


def _bridged_orthogonal_components(
    points: Iterable[tuple[float, float]],
    bridge: tuple[float, float, int, float],
    *,
    edge_id: str,
    cls: str = "wire",
    marker: str = "url(#arrow)",
    radius: float = 14.0,
    corner_style: str = "rounded",
) -> tuple[str, str]:
    """Render one route-integrated hop with the exact R5 continuity contract."""

    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    route = tuple(_R5.Point(float(x), float(y)) for x, y in points)
    bx, by, segment_index, bridge_radius = bridge
    if not 0 <= segment_index < len(route) - 1:
        raise ValueError("Bridge segment index is outside the route")
    segment_start, segment_end = route[segment_index], route[segment_index + 1]
    if abs(segment_start.y - segment_end.y) >= 0.001:
        raise ValueError("Bridge must be attached to a horizontal route segment")
    direction = 1.0 if segment_end.x >= segment_start.x else -1.0
    mark = _R5.BridgeMark(_R5.Point(bx, by), "horizontal", segment_index, bridge_radius)
    routed = (
        _R5.bridged_orthogonal_path(route, (mark,), radius)
        if corner_style == "rounded"
        else _straight_bridged_route_d(route, mark, segment_index, direction)
    )
    hop = _R5.bridge_open_hop_path(mark, direction)
    underlay = _R5.bridge_crown_underlay_path(mark, direction)
    main = _path(
        routed,
        cls,
        **{
            "data-edge-id": edge_id,
            "data-route-style": f"{corner_style}-orthogonal",
            "data-corner-style": corner_style,
            "data-turn-count": max(0, len(route) - 2),
            "data-path-bridges-integrated": "true",
            "marker-end": marker,
        },
    )
    group_attrs = {
        "class": "bridge-mark",
        "data-bridge-edge": edge_id,
        "data-bridge-segment": segment_index,
        "data-bridge-orientation": "horizontal",
        "data-bridge-x": f"{bx:.2f}",
        "data-bridge-y": f"{by:.2f}",
        "data-bridge-radius": f"{bridge_radius:.2f}",
        "data-bridge-direction": "right" if direction > 0 else "left",
        "data-hop-geometry-shared": "true",
        "data-underlay-scope": "central-crown",
        "data-join-continuity": "true",
    }
    group = (
        f'<g {_attrs(group_attrs)}>'
        + _path(underlay, "bridge-hop-underlay", **{"data-bridge-role": "underlay"})
        + _path(hop, "bridge-hop", **{"data-bridge-role": "hop"})
        + "</g>"
    )
    return main, group


def _bridged_orthogonal_path(
    points: Iterable[tuple[float, float]],
    bridge: tuple[float, float, int, float],
    *,
    edge_id: str,
    cls: str = "wire",
    marker: str = "url(#arrow)",
    radius: float = 14.0,
    corner_style: str = "rounded",
) -> str:
    """Compatibility wrapper for diagrams that need one immediate bridge repaint."""

    main, group = _bridged_orthogonal_components(
        points,
        bridge,
        edge_id=edge_id,
        cls=cls,
        marker=marker,
        radius=radius,
        corner_style=corner_style,
    )
    return main + group


def _circle(cx: float, cy: float, r: float, cls: str = "dot", **extra: object) -> str:
    return f'<circle {_attrs({"class": cls, "cx": cx, "cy": cy, "r": r, **extra})}/>'


def _zone(
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    zone_id: str,
    *,
    parent_id: str | None = None,
    child_layout: str,
    minimum_child_padding: float = 24,
    filled: bool = True,
    radius: float = 20,
) -> str:
    """Emit one measurable containment parent for geometry QA."""

    if child_layout not in {"row", "column", "single"}:
        raise ValueError(f"Unsupported containment child layout: {child_layout}")
    attrs: dict[str, object] = {
        "class": "containment-zone",
        "data-zone-id": zone_id,
        "data-box-x": f"{x:.2f}",
        "data-box-y": f"{y:.2f}",
        "data-box-width": f"{width:.2f}",
        "data-box-height": f"{height:.2f}",
        "data-child-layout": child_layout,
        "data-minimum-child-padding": f"{minimum_child_padding:.2f}",
        "data-group-centering": "both-axes",
    }
    if parent_id is not None:
        attrs["data-parent-id"] = parent_id
    boundary_class = "zone-fill" if filled else "zone"
    return (
        f'<g {_attrs(attrs)}>'
        + _rect(x, y, width, height, boundary_class, radius)
        + _text(x + 28, y + 40, label, "kicker")
        + "</g>"
    )


def _node(
    x: float,
    y: float,
    title: str,
    subtitle: str,
    badge: str,
    *,
    width: float = 0,
    height: float = 124,
    focal: bool = False,
    muted: bool = False,
    title_role: str = "node_title",
    node_id: str | None = None,
    parent_id: str | None = None,
) -> tuple[str, float]:
    measured = METRICS.measure(title_role, title).width
    computed = min(410.0, max(246.0, measured + 72.0))
    w = max(width, computed)
    classes = "node-card focal" if focal else "node-card muted" if muted else "node-card"
    badge_w = max(54, METRICS.measure("technical", badge).width + 22)
    group_attrs: dict[str, object] = {
        "class": classes,
        "data-measured-title-width": f"{measured:.2f}",
        "data-card-width": f"{w:.2f}",
        "data-box-x": f"{x:.2f}",
        "data-box-y": f"{y:.2f}",
        "data-box-width": f"{w:.2f}",
        "data-box-height": f"{height:.2f}",
    }
    if node_id is not None:
        group_attrs["data-node-id"] = node_id
    if parent_id is not None:
        group_attrs["data-parent-id"] = parent_id
    parts = [
        f'<g {_attrs(group_attrs)}>',
        _rect(x, y, w, height, "node-boundary", 14),
        _rect(x + 18, y + 16, badge_w, 28, "badge", 6),
        _text(x + 18 + badge_w / 2, y + 36, badge, "badge-text", "middle"),
        _text(x + w / 2, y + 76, title, "node-title", "middle"),
        _text(x + w / 2, y + 105, subtitle, "mono", "middle"),
        "</g>",
    ]
    return "".join(parts), w


def _legend(y: float, width: float, items: tuple[tuple[str, str], ...], note: str = "") -> str:
    parts = [_line(52, y, width - 52, y, "legend-rule"), _text(56, y + 38, "LEGEND", "kicker")]
    x = 210.0
    for kind, label in items:
        if kind == "accent":
            parts.extend([_rect(x, y + 20, 28, 24, "legend-accent", 5), _text(x + 42, y + 39, label, "legend-text")])
        elif kind == "line":
            parts.extend([_line(x, y + 34, x + 42, y + 34, "wire"), _text(x + 58, y + 39, label, "legend-text")])
        elif kind == "dash":
            parts.extend([_line(x, y + 34, x + 42, y + 34, "wire dashed"), _text(x + 58, y + 39, label, "legend-text")])
        elif kind == "dot":
            parts.extend([_circle(x + 14, y + 32, 8, "dot"), _text(x + 42, y + 39, label, "legend-text")])
        x += max(205, METRICS.measure("material", label).width + 118)
    if note:
        parts.append(_text(width - 56, y + 39, note, "legend-note", "end"))
    return "".join(parts)


def _svg_shell(
    engine: str,
    canonical_type: str,
    title: str,
    description: str,
    width: int,
    height: int,
    body: str,
    *,
    semantic_ratio: float = 0.84,
    takeaway_id: str = "focal",
    connector_corner_style: str | None = None,
) -> str:
    human = resolved_family("node_title")
    mono = resolved_family("technical")
    display = resolved_family("display")
    css = f"""
      text{{font-family:'{escape(human)}';fill:{TOKENS['ink']};text-rendering:geometricPrecision}}
      .display{{font-family:'{escape(display)}';font-size:48px;font-weight:400}}
      .node-title{{font-size:24px;font-weight:650}}
      .material{{font-size:16px;font-weight:500}}
      .material-strong{{font-size:18px;font-weight:650}}
      .mono,.badge-text,.kicker,.legend-note{{font-family:'{escape(mono)}';font-size:16px}}
      .mono{{fill:{TOKENS['ink_soft']}}}
      .kicker{{font-size:14px;font-weight:700;letter-spacing:2.1px;fill:{TOKENS['ink_faint']}}}
      .relationship-label{{font-family:'{escape(mono)}';font-size:16px;font-weight:700;letter-spacing:.5px;fill:{TOKENS['ink_faint']}}}
      .axis-note{{font-family:'{escape(mono)}';font-size:16px;font-weight:700;letter-spacing:1.2px;fill:{TOKENS['ink_soft']}}}
      .badge-text{{font-size:14px;font-weight:700;letter-spacing:1px;fill:{TOKENS['ink_soft']}}}
      .node-boundary{{fill:{TOKENS['surface']};stroke:{TOKENS['line']};stroke-width:2.2}}
      .node-card.focal .node-boundary{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2.8}}
      .node-card.muted .node-boundary{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line_soft']}}}
      .badge{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line_soft']};stroke-width:1.2}}
      .focal .badge{{fill:#fff3ec;stroke:{TOKENS['accent']}}}
      .focal .badge-text{{fill:{TOKENS['accent_text']}}}
      .wire{{fill:none;stroke:{TOKENS['line']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
      .wire.soft{{stroke:{TOKENS['line_soft']};stroke-width:2}}
      .wire.accent{{stroke:{TOKENS['accent']};stroke-width:3.6}}
      .wire.blue{{stroke:{TOKENS['blue']}}}
      .wire.green{{stroke:{TOKENS['green']}}}
      .wire.dashed{{stroke-dasharray:9 9}}
      .bridge-hop-underlay{{fill:none;stroke:{TOKENS['canvas']};stroke-width:11;stroke-linecap:round;stroke-linejoin:round}}
      .bridge-hop{{fill:none;stroke:{TOKENS['line']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
      .zone{{fill:none;stroke:{TOKENS['line_soft']};stroke-width:1.6}}
      .zone-fill{{fill:{TOKENS['surface_soft']};fill-opacity:.55;stroke:{TOKENS['line_soft']};stroke-width:1.6}}
      .grid{{stroke:{TOKENS['grid']};stroke-width:1.4}}
      .dot{{fill:{TOKENS['ink']}}}
      .accent-dot{{fill:{TOKENS['accent']}}}
      .legend-rule{{stroke:{TOKENS['grid']};stroke-width:1.5}}
      .legend-accent{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2}}
      .legend-text{{font-size:16px;fill:{TOKENS['ink_soft']}}}
      .legend-note{{font-size:14px;font-style:italic;fill:{TOKENS['ink_soft']}}}
      .band{{fill:{TOKENS['surface_slate']};stroke:{TOKENS['line_soft']};stroke-width:1.5}}
      .band.focal{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']};stroke-width:2.3}}
      .matrix-focal-region{{fill:{TOKENS['accent_soft']};stroke:none}}
      .pyramid-layer-fill{{fill:{TOKENS['surface_slate']};stroke:none}}
      .pyramid-layer-fill.focal{{fill:{TOKENS['accent_soft']}}}
      .pyramid-outer-outline,.pyramid-divider{{fill:none;stroke:{TOKENS['line_soft']};stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}}
      .pyramid-apex-outline,.pyramid-divider.focal{{fill:none;stroke:{TOKENS['accent']};stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round}}
      .pyramid-annotation{{font-family:'{escape(mono)}';font-size:16px;font-weight:650;letter-spacing:1px;fill:{TOKENS['ink_faint']}}}
      .pyramid-annotation.accent{{fill:{TOKENS['accent_text']}}}
      .label-mask{{fill:{TOKENS['canvas']}}}
      .axis{{stroke:{TOKENS['line']};stroke-width:2.2}}
    """
    corner_attrs = ""
    if connector_corner_style is not None:
        if connector_corner_style not in CORNER_STYLES:
            raise ValueError(f"Unsupported connector corner style: {connector_corner_style}")
        corner_attrs = (
            f' data-connector-corner-style="{connector_corner_style}"'
            ' data-corner-style-options="rounded straight"'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}"
      role="img" aria-labelledby="anchor-title anchor-desc" data-layout-engine="{escape(engine)}"
      data-canonical-type="{escape(canonical_type)}" data-mode="neutral-light" data-semantic-ratio="{semantic_ratio:.2f}"
      data-min-label-clearance="8" data-font-measured="true" data-no-global-transform="true"
      data-takeaway-node="{escape(takeaway_id)}" data-resolved-human-font="{escape(human)}" data-resolved-mono-font="{escape(mono)}"{corner_attrs}>
      <title id="anchor-title">{escape(title)}</title>
      <desc id="anchor-desc">{escape(description)}</desc>
      <defs>
        <pattern id="dot-field" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{TOKENS['grid']}" opacity=".34"/></pattern>
        <marker id="arrow" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="{TOKENS['line']}"/></marker>
        <marker id="arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="{TOKENS['accent']}"/></marker>
        <style>{css}</style>
      </defs>
      <rect width="{width}" height="{height}" fill="{TOKENS['canvas']}"/>
      <rect width="{width}" height="{height}" fill="url(#dot-field)"/>
      {body}
    </svg>'''


def topology_anchor(corner_style: str = "rounded") -> Anchor:
    w, h = 1680, 940
    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    parts = [
        _zone(60, 90, 310, 590, "EDGE", "topology-edge", child_layout="single"),
        _zone(400, 90, 640, 590, "APPLICATION", "topology-application", child_layout="row"),
        _zone(1080, 90, 540, 590, "CONTENT", "topology-content", child_layout="column"),
    ]
    n1, _ = _node(92, 323, "Reader", "browser · public", "EXT", width=246, muted=True, node_id="topology-reader", parent_id="topology-edge")
    n2, _ = _node(430, 323, "Cloud edge", "cache · TLS", "EDGE", width=260, node_id="topology-cloud-edge", parent_id="topology-application")
    n3, _ = _node(730, 323, "Astro origin", "SSR · MDX", "ORIG", width=280, focal=True, node_id="topology-astro-origin", parent_id="topology-application")
    n4, _ = _node(1200, 190, "MDX bundle", "content/*.mdx", "BUN", width=300, node_id="topology-mdx-bundle", parent_id="topology-content")
    n5, _ = _node(1200, 456, "Media store", "assets · OG", "STORE", width=300, node_id="topology-media-store", parent_id="topology-content")
    parts += [n1, n2, n3, n4, n5]
    parts += [
        _orthogonal_path(((338, 385), (430, 385)), "wire blue", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((690, 385), (730, 385)), "wire accent", marker="url(#arrow-accent)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((1010, 361), (1140, 361), (1140, 252), (1200, 252)), "wire", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((1010, 409), (1140, 409), (1140, 518), (1200, 518)), "wire", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _text(384, 368, "HTTPS", "kicker", "middle"), _text(710, 368, "SSR", "kicker", "middle"),
        _text(1124, 342, "READ", "kicker", "end"), _text(1124, 448, "QUERY", "kicker", "end"),
        _legend(748, w, (("accent", "focal origin"), ("line", "request / dependency"), ("dash", "external / async")), "Boundary carries trust context."),
    ]
    svg = _svg_shell("topology-and-zones", "architecture", "Kiến trúc nội dung tại edge", "Ba vùng tin cậy; origin là điểm hội tụ giữa edge và hai nguồn nội dung.", w, h, "".join(parts), connector_corner_style=corner_style)
    return Anchor(1, "topology-and-zones", "architecture", "01-topology-and-zones--neutral-light", "Architecture anchor", "Origin là điểm hội tụ và ranh giới tin cậy chính.", svg, (("focal", "Astro origin"), ("zones", "EDGE / APPLICATION / CONTENT"), ("flow", "Reader → edge → origin → content")))


def integration_anchor(corner_style: str = "rounded") -> Anchor:
    w, h = 1680, 940
    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    parts = [
        _zone(52, 78, 390, 638, "COLLECT", "integration-collect", child_layout="column"),
        _zone(476, 78, 590, 638, "TRANSFORM", "integration-transform", child_layout="single"),
        _zone(1100, 78, 528, 638, "SERVE", "integration-serve", child_layout="column"),
    ]
    n1, _ = _node(87, 210, "Order events", "JSON · every minute", "SRC", width=320, node_id="integration-order-events", parent_id="integration-collect")
    n2, _ = _node(87, 460, "Inventory files", "CSV · nightly", "SRC", width=320, muted=True, node_id="integration-inventory-files", parent_id="integration-collect")
    n3, _ = _node(521, 335, "Normalize contracts", "schema · dedupe", "STEP", width=500, focal=True, node_id="integration-normalize", parent_id="integration-transform")
    n4, _ = _node(1149, 210, "Analytics mart", "partitioned tables", "DB", width=430, node_id="integration-analytics-mart", parent_id="integration-serve")
    n5, _ = _node(1149, 460, "Alert stream", "exceptions only", "API", width=430, node_id="integration-alert-stream", parent_id="integration-serve")
    parts += [n1, n2, n3, n4, n5]
    parts += [
        _orthogonal_path(((407, 272), (480, 272), (480, 369), (521, 369)), "wire blue", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((407, 522), (480, 522), (480, 425), (521, 425)), "wire dashed", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((1021, 369), (1100, 369), (1100, 272), (1149, 272)), "wire accent", marker="url(#arrow-accent)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((1021, 425), (1100, 425), (1100, 522), (1149, 522)), "wire", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _text(462, 255, "STREAM", "kicker", "middle"), _text(462, 545, "BATCH", "kicker", "middle"),
        _text(1084, 351, "CURATED", "kicker", "middle"), _text(1082, 448, "EXCEPTIONS", "kicker", "middle"),
        _legend(784, w, (("line", "data movement"), ("dash", "scheduled batch"), ("accent", "contract boundary")), "One transform, two outputs."),
    ]
    svg = _svg_shell("integration-pipeline", "data-flow", "Tích hợp đơn hàng và tồn kho", "Hai nguồn hội tụ tại bước chuẩn hóa trước khi tách thành mart và alert stream.", w, h, "".join(parts), connector_corner_style=corner_style)
    return Anchor(2, "integration-pipeline", "data-flow", "02-integration-pipeline--neutral-light", "Integration anchor", "Chuẩn hóa hợp đồng là nút kiểm soát trung tâm.", svg, (("sources", "Order events; Inventory files"), ("control", "Normalize contracts"), ("outputs", "Analytics mart; Alert stream")))


def deployment_anchor(corner_style: str = "rounded") -> Anchor:
    w, h = 1540, 980
    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    parts = [
        _zone(58, 80, 1424, 674, "REGION · SINGAPORE", "deployment-region", child_layout="row", minimum_child_padding=48, radius=24),
        _zone(106, 152, 902, 530, "KUBERNETES CLUSTER", "deployment-cluster", parent_id="deployment-region", child_layout="row", minimum_child_padding=50, filled=False),
        _zone(1042, 152, 392, 530, "MANAGED DATA", "deployment-managed", parent_id="deployment-region", child_layout="column", minimum_child_padding=40, filled=False),
        _zone(156, 237, 378, 360, "NODE POOL A", "deployment-pool-a", parent_id="deployment-cluster", child_layout="single", minimum_child_padding=34, radius=18),
        _zone(580, 237, 378, 360, "NODE POOL B", "deployment-pool-b", parent_id="deployment-cluster", child_layout="single", minimum_child_padding=34, radius=18),
    ]
    a, _ = _node(190, 355, "API · 3 replicas", "health /ready", "POD", width=310, focal=True, node_id="deployment-api", parent_id="deployment-pool-a")
    b, _ = _node(614, 355, "Worker · 5 replicas", "queue consumers", "POD", width=310, node_id="deployment-worker", parent_id="deployment-pool-b")
    c, _ = _node(1082, 256, "Postgres", "multi-AZ", "DB", width=312, node_id="deployment-postgres", parent_id="deployment-managed")
    d, _ = _node(1082, 454, "Object storage", "encrypted", "OBJ", width=312, muted=True, node_id="deployment-object-storage", parent_id="deployment-managed")
    parts += [a, b, c, d]
    parts += [
        _orthogonal_path(((500, 417), (614, 417)), "wire", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((924, 403), (1025, 403), (1025, 318), (1082, 318)), "wire accent", marker="url(#arrow-accent)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _orthogonal_path(((924, 431), (1025, 431), (1025, 516), (1082, 516)), "wire", marker="url(#arrow)", corner_style=corner_style, **{"data-remediation": "D-062"}),
        _text(557, 400, "JOBS", "kicker", "middle"), _text(1010, 301, "SQL", "kicker", "middle"),
        _legend(824, w, (("accent", "public workload"), ("line", "runtime dependency"), ("dash", "external boundary")), "Containment is the deployment truth."),
    ]
    svg = _svg_shell("runtime-deployment", "deployment", "Triển khai dịch vụ theo vùng", "Nested region, cluster, node pool và managed-data boundaries cho thấy runtime placement.", w, h, "".join(parts), connector_corner_style=corner_style)
    return Anchor(3, "runtime-deployment", "deployment", "03-runtime-deployment--neutral-light", "Deployment anchor", "API public nằm trong cluster và phụ thuộc managed data ngoài cluster.", svg, (("region", "Singapore"), ("cluster", "Kubernetes"), ("workloads", "API; Worker"), ("managed", "Postgres; Object storage")))


def dependency_anchor(corner_style: str = "rounded") -> Anchor:
    w, h = 1540, 1200
    if corner_style not in CORNER_STYLES:
        raise ValueError(f"Unsupported connector corner style: {corner_style}")
    parts = []
    for index, y in enumerate((104, 324, 544, 764)):
        parts.extend([_text(62, y + 18, f"RANK {index}", "kicker"), _line(180, y + 40, 1480, y + 40, "grid")])
    positions = {
        "web": (300, 82), "admin": (930, 82), "api": (260, 302), "ui": (900, 302),
        "types": (390, 522), "db": (930, 522), "tokens": (180, 742), "utils": (650, 742), "zod": (1080, 742),
    }
    specs = [
        ("web", "web", "apps/web", "APP", False, False), ("admin", "admin", "apps/admin", "APP", False, False),
        ("api", "api", "services/api", "SVC", False, False), ("ui", "ui-kit", "packages/ui-kit", "PKG", False, False),
        ("types", "shared-types", "packages/shared-types", "PKG", True, False), ("db", "database", "services/db", "SVC", False, False),
        ("tokens", "tokens", "packages/tokens", "PKG", False, True), ("utils", "utils", "packages/utils", "PKG", False, False),
        ("zod", "zod", "external · npm", "EXT", False, True),
    ]
    boxes: dict[str, tuple[float, float, float]] = {}
    for key, title, sub, badge, focal, muted in specs:
        x, y = positions[key]
        item, width = _node(x, y, title, sub, badge, width=280, focal=focal, muted=muted)
        boxes[key] = (x, y, width)
        parts.append(item)
    route_attrs = {"data-remediation": "D-061", "data-corner-policy-scope": "whole-chart"}
    connector_attrs = {
        "data-dependency-connectors": "true",
        "data-connector-corner-style": corner_style,
        "data-rank-step": "220",
        "data-inter-rank-gap": "96",
        "data-corridor-midpoint-step": "220",
        "data-lower-corridor-midpoint": "694",
        "data-lower-corridor-pitch": "20",
        "data-crossing-count": "2",
        "data-bridge-paint-order": "base-routes then bridge-repaints",
    }
    base_routes = [
        _orthogonal_path(((400, 206), (400, 302)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-web-api"}),
        _orthogonal_path(((480, 206), (480, 254), (970, 254), (970, 302)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-web-ui"}),
        _orthogonal_path(((1070, 206), (1070, 302)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-admin-ui"}),
        _orthogonal_path(((400, 426), (400, 474), (480, 474), (480, 522)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-api-types"}),
        _orthogonal_path(((1040, 426), (1040, 474), (580, 474), (580, 522)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-ui-types"}),
        _orthogonal_path(((930, 584), (670, 584)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-db-types"}),
        _orthogonal_path(((480, 646), (480, 674), (320, 674), (320, 742)), marker="url(#arrow)", corner_style=corner_style, **route_attrs, **{"data-edge-id": "dependency-types-tokens"}),
    ]
    utils_route, utils_bridge = _bridged_orthogonal_components(
        ((530, 646), (530, 694), (790, 694), (790, 742)),
        (580, 694, 1, 14),
        edge_id="dependency-types-utils",
        corner_style=corner_style,
    )
    zod_route, zod_bridge = _bridged_orthogonal_components(
        ((580, 646), (580, 714), (1220, 714), (1220, 742)),
        (790, 714, 1, 14),
        edge_id="dependency-types-zod",
        corner_style=corner_style,
    )
    cycle_route = _orthogonal_path(
        ((790, 866), (790, 950), (320, 950), (320, 866)),
        "wire accent dashed",
        marker="url(#arrow-accent)",
        corner_style=corner_style,
        **route_attrs,
        **{"data-edge-id": "dependency-cycle-utils-tokens"},
    )
    parts.append(f'<g {_attrs(connector_attrs)}>')
    parts.extend(base_routes + [utils_route, zod_route, cycle_route])
    parts.extend([utils_bridge, zod_bridge, "</g>"])
    parts += [
        _text(555, 1010, "CYCLE · MUST BREAK", "kicker", "middle"),
        _legend(1100, w, (("accent", "high fan-in"), ("line", "dependency"), ("dash", "cycle back-edge"))),
    ]
    svg = _svg_shell(
        "dependency-dag",
        "dependency-graph",
        "Phụ thuộc package theo rank",
        "Các package được xếp rank; shared-types có fan-in cao và một cycle back-edge được đánh dấu.",
        w,
        h,
        "".join(parts),
        semantic_ratio=.88,
        connector_corner_style=corner_style,
    )
    return Anchor(4, "dependency-dag", "dependency-graph", "04-dependency-dag--neutral-light", "Dependency anchor", "shared-types là điểm hội tụ; cycle tokens → utils phải được phá.", svg, (("ranks", "0–3"), ("focal", "shared-types"), ("risk", "cycle back-edge")))


def directed_anchor() -> Anchor:
    w, h = 1240, 1160
    parts = []
    def diamond(cx: float, cy: float, rw: float, rh: float, label: tuple[str, str], focal: bool = False) -> str:
        cls = "band focal" if focal else "band"
        points = f"{cx},{cy-rh} {cx+rw},{cy} {cx},{cy+rh} {cx-rw},{cy}"
        return f'<polygon class="{cls}" points="{points}"/>' + _tspans(cx, cy - 6, label, "node-title", 29, "middle")
    start, _ = _node(420, 72, "New request", "signal received", "START", width=400, muted=True)
    step, _ = _node(420, 250, "Validate evidence", "owner · timestamp", "STEP", width=400)
    end, _ = _node(420, 918, "Release decision", "record rationale", "END", width=400, focal=True)
    parts += [start, step]
    parts += [diamond(620, 500, 240, 110, ("Material", "exception?")), diamond(620, 750, 240, 110, ("Control", "effective?"), True), end]
    parts += [
        _path("M620 196 V250", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 374 V390", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 610 V640", "wire", **{"marker-end": "url(#arrow)"}),
        _path("M620 860 V918", "wire accent", **{"marker-end": "url(#arrow-accent)"}),
        '<g data-no-branch-width="220" data-no-return-target="Validate evidence" data-remediation="D-060-03">',
        _path("M860 500 H1080", "wire", **{"data-branch": "material-no"}),
        _path("M860 750 H1080", "wire", **{"data-branch": "control-no"}),
        _orthogonal_path(((1080, 750), (1080, 312), (820, 312)), "wire", marker="url(#arrow)", **{"data-return-target": "validate-evidence"}),
        '</g>',
        _text(960, 478, "NO", "kicker", "middle"), _text(960, 728, "NO", "kicker", "middle"), _text(644, 630, "YES", "kicker"), _text(644, 896, "YES", "kicker"),
        _legend(1060, w, (("accent", "approved path"), ("line", "branch"), ("dot", "decision point"))),
    ]
    svg = _svg_shell("directed-flow-state", "flowchart", "Luồng quyết định phát hành", "Hai decision diamond tách ngoại lệ và hiệu lực kiểm soát; happy path đi đến release decision.", w, h, "".join(parts), semantic_ratio=.91)
    return Anchor(5, "directed-flow-state", "flowchart", "05-directed-flow-state--neutral-light", "Directed flow anchor", "Chỉ ngoại lệ trọng yếu với kiểm soát hiệu lực mới đi đến release.", svg, (("start", "New request"), ("decisions", "Material exception; Control effective"), ("end", "Release decision")))


def time_anchor() -> Anchor:
    w, h = 1680, 860
    y = 410
    parts = [_line(120, y, 1560, y, "axis"), _line(120, y - 18, 120, y + 18, "axis"), _line(1560, y - 18, 1560, y + 18, "axis")]
    events = [
        (160, "FEB 2025", "Baseline", "inventory locked", False, -1),
        (430, "APR 2025", "Contract v1", "semantic IR", False, 1),
        (810, "SEP 2025", "Kernel", "typography pass", False, -1),
        (1180, "JAN 2026", "Anchor review", "14 engines", True, 1),
        (1518, "APR 2026", "Coverage", "39 + 4", True, -1),
    ]
    for x, date, title, sub, focal, direction in events:
        cls = "accent-dot" if focal else "dot"
        line_cls = "wire accent" if focal else "wire soft"
        if direction == 1:
            leader_end, date_y, title_y, sub_y = 258, 154, 194, 226
            group_attrs = {
                "class": "time-event top-event",
                "data-label-position": "above-leader",
                "data-text-bottom": "232",
                "data-leader-end": str(leader_end),
                "data-label-clearance": "26",
            }
        else:
            leader_end, date_y, title_y, sub_y = 548, 586, 626, 658
            group_attrs = {"class": "time-event bottom-event", "data-label-position": "below-leader"}
        parts += [f'<g {_attrs(group_attrs)}>', _circle(x, y, 11 if focal else 8, cls), _line(x, y, x, leader_end, line_cls), _text(x, date_y, date, "kicker", "middle"), _text(x, title_y, title, "node-title", "middle"), _text(x, sub_y, sub, "mono", "middle"), "</g>"]
    parts += [_legend(738, w, (("dot", "event"), ("accent", "major milestone")), "Spacing is proportional to elapsed time.")]
    svg = _svg_shell("time-planning", "timeline", "Lộ trình semantic đến coverage", "Năm mốc theo thời gian thực; hai mốc coral đánh dấu anchor review và full coverage.", w, h, "".join(parts), semantic_ratio=.87)
    return Anchor(7, "time-planning", "timeline", "07-time-planning--neutral-light", "Timeline anchor", "Anchor review là mốc chuyển từ foundation sang coverage.", svg, (("span", "Feb 2025–Apr 2026"), ("milestones", "Anchor review; Coverage")))


def experience_anchor() -> Anchor:
    w, h = 1660, 980
    columns = [(190, "DISCOVER"), (550, "VERIFY"), (910, "DECIDE"), (1270, "ACT")]
    parts = []
    for x, label in columns:
        parts += [_rect(x, 78, 320, 104, "band", 14), _text(x + 160, 126, label, "node-title", "middle"), _text(x + 160, 157, "moment", "kicker", "middle"), _line(x - 20, 204, x - 20, 748, "grid")]
    rows = [(250, "ACTION"), (410, "THOUGHT"), (570, "EMOTION")]
    for y, label in rows:
        parts += [_text(58, y + 18, label, "kicker"), _line(170, y + 42, 1600, y + 42, "grid")]
    actions = ["Find policy", "Check source", "Compare options", "Record choice"]
    thoughts = ["Is this current?", "Can I trust it?", "What changes?", "Who owns follow-up?"]
    emotion = [3, 2, 4, 5]
    for index, (x, _) in enumerate(columns):
        parts += [_rect(x + 18, 230, 284, 78, "node-boundary", 12), _text(x + 160, 278, actions[index], "material-strong", "middle")]
        focus = index == 2
        parts += [_rect(x + 18, 390, 284, 78, "band focal" if focus else "node-boundary", 12), _text(x + 160, 438, thoughts[index], "material-strong", "middle")]
        parts += [_circle(x + 160, 618, 14 + emotion[index] * 3, "accent-dot" if focus else "dot"), _text(x + 160, 680, f"confidence {emotion[index]}/5", "mono", "middle")]
    parts += [_path("M350 618 C520 548 710 666 1070 618 S1390 560 1430 618", "wire accent"), _legend(820, w, (("line", "experience trace"), ("accent", "decision moment"), ("dot", "confidence")), "Rows separate behavior, cognition and feeling.")]
    svg = _svg_shell("work-experience", "user-journey", "Hành trình ra quyết định có bằng chứng", "Bốn moment theo hàng action, thought và emotion; Decide là friction/focal moment.", w, h, "".join(parts))
    return Anchor(8, "work-experience", "user-journey", "08-work-experience--neutral-light", "Experience anchor", "Khâu so sánh lựa chọn là thời điểm cần hỗ trợ rõ nhất.", svg, (("moments", "Discover; Verify; Decide; Act"), ("rows", "Action; Thought; Emotion"), ("focal", "Decide")))


def hierarchy_anchor() -> Anchor:
    w, h = 1600, 960
    parts = [_text(58, 180, "COMMAND", "kicker"), _line(180, 208, 1540, 208, "grid"), _text(58, 440, "DOMAINS", "kicker"), _line(180, 468, 1540, 468, "grid"), _text(58, 698, "PODS", "kicker")]
    root, _ = _node(570, 80, "Operating lead", "priority · arbitration", "FRONT", width=460, focal=True)
    parts.append(root)
    mids = [(173, "Growth", "acquisition"), (593, "Content", "editorial"), (913, "Commerce", "orders"), (1268, "Systems", "platform")]
    for x, title, sub in mids:
        node, _ = _node(x, 338, title, sub, "POD", width=260)
        parts.append(node)
    parts += [
        _line(800, 204, 800, 270, "wire", **{"data-parent": "Operating lead", "data-role": "trunk"}),
        _line(303, 270, 1398, 270, "wire", **{"data-role": "domain-bus"}),
        *[_line(center, 270, center, 338, "wire", **{"data-entry-alignment": "center"}) for center in (303, 723, 1043, 1398)],
    ]
    leaves = [(40, "Media", "ads"), (320, "CRM", "lifecycle"), (600, "Writer", "copy"), (920, "Store", "checkout"), (1275, "Runtime", "agents")]
    for x, title, sub in leaves:
        node, _ = _node(x, 626, title, sub, "SPEC", width=230, muted=True)
        parts.append(node)
    parts += [
        _line(303, 462, 303, 554, "wire", **{"data-parent": "Growth", "data-role": "child-trunk"}),
        _line(163, 554, 443, 554, "wire", **{"data-role": "child-bus"}),
        _line(163, 554, 163, 626, "wire", **{"data-parent": "Growth", "data-child": "Media", "data-entry-alignment": "center"}),
        _line(443, 554, 443, 626, "wire", **{"data-parent": "Growth", "data-child": "CRM", "data-entry-alignment": "center"}),
        _line(723, 462, 723, 626, "wire", **{"data-parent": "Content", "data-child": "Writer", "data-entry-alignment": "center", "data-route-priority": "straight"}),
        _line(1043, 462, 1043, 626, "wire", **{"data-parent": "Commerce", "data-child": "Store", "data-entry-alignment": "center", "data-route-priority": "straight"}),
        _line(1398, 462, 1398, 626, "wire", **{"data-parent": "Systems", "data-child": "Runtime", "data-entry-alignment": "center", "data-route-priority": "straight"}),
        _legend(850, w, (("accent", "front door"), ("line", "accountability"), ("dash", "unfilled role")), "Ownership descends; escalation returns to one front door."),
    ]
    svg = _svg_shell("hierarchy", "org-chart", "Mô hình điều phối theo domain", "Một front door phân nhánh thành bốn domain và các specialist pod.", w, h, "".join(parts), semantic_ratio=.88)
    return Anchor(9, "hierarchy", "org-chart", "09-hierarchy--neutral-light", "Hierarchy anchor", "Operating lead là front door duy nhất; domain ownership phân nhánh rõ.", svg, (("root", "Operating lead"), ("domains", "Growth; Content; Commerce; Systems"), ("leaves", "Five specialist pods")))


def containment_anchor() -> Anchor:
    w, h = 1420, 1000
    apex_x, apex_y = 750.0, 112.0
    base_left_x, base_right_x, base_y = 250.0, 1250.0, 750.0
    axis_x = 90.0
    minimum_axis_clearance = 140.0
    minimum_text_inset = 8.0
    minimum_annotation_clearance = 56.0
    annotation_visual_gap = 72.0
    annotation_gap_tolerance = 0.01
    cuts = (apex_y, 340.0, 490.0, 625.0, base_y)
    labels = (
        ("Flagship decision", "rare · highest leverage", 270.0, 307.0),
        ("Operating principles", "quarterly · durable", 414.0, 446.0),
        ("Reusable playbooks", "monthly · repeatable", 552.0, 584.0),
        ("Daily procedures", "daily · volume work", 682.0, 714.0),
    )
    annotation_specs = (
        ("THE APEX", 232.0, 0, "semantic"),
        ("~4 / YR", 414.0, 1, "cadence-quarterly"),
        ("~12 / YR", 552.0, 2, "cadence-monthly"),
        ("~240 / YR", 682.0, 3, "cadence-workdays"),
    )

    def side_x(y: float, base_x: float) -> float:
        progress = (y - apex_y) / (base_y - apex_y)
        return apex_x + (base_x - apex_x) * progress

    annotations = []
    for value, baseline_y, layer_index, note_kind in annotation_specs:
        measured = METRICS.measure("technical", value)
        bbox_height = measured.ascent + measured.descent
        bbox_center_y = baseline_y - measured.ascent + bbox_height / 2
        x = round(side_x(bbox_center_y, base_right_x) + annotation_visual_gap, 2)
        actual_gap = x - side_x(bbox_center_y, base_right_x)
        annotations.append((value, x, baseline_y, layer_index, note_kind, bbox_center_y, actual_gap))

    boundaries = tuple((round(side_x(y, base_left_x), 2), round(side_x(y, base_right_x), 2), y) for y in cuts)
    layer_points = (
        ((apex_x, apex_y), (boundaries[1][1], cuts[1]), (boundaries[1][0], cuts[1])),
        ((boundaries[1][0], cuts[1]), (boundaries[1][1], cuts[1]), (boundaries[2][1], cuts[2]), (boundaries[2][0], cuts[2])),
        ((boundaries[2][0], cuts[2]), (boundaries[2][1], cuts[2]), (boundaries[3][1], cuts[3]), (boundaries[3][0], cuts[3])),
        ((boundaries[3][0], cuts[3]), (boundaries[3][1], cuts[3]), (base_right_x, base_y), (base_left_x, base_y)),
    )
    group_attrs = {
        "class": "pyramid-stack",
        "data-pyramid-silhouette": "continuous-triangle",
        "data-remediation": "D-063",
        "data-text-remediation": "D-064",
        "data-annotation-remediation": "D-065",
        "data-apex-x": f"{apex_x:.2f}",
        "data-apex-y": f"{apex_y:.2f}",
        "data-base-left-x": f"{base_left_x:.2f}",
        "data-base-right-x": f"{base_right_x:.2f}",
        "data-base-y": f"{base_y:.2f}",
        "data-axis-x": f"{axis_x:.2f}",
        "data-min-axis-clearance": f"{minimum_axis_clearance:.2f}",
        "data-actual-axis-clearance": f"{base_left_x - axis_x:.2f}",
        "data-layer-count": "4",
        "data-shared-boundary-count": "3",
        "data-shared-boundary-rendering": "single-stroke",
        "data-min-text-polygon-inset": f"{minimum_text_inset:.2f}",
        "data-annotation-count": "4",
        "data-min-annotation-clearance": f"{minimum_annotation_clearance:.2f}",
        "data-annotation-side": "right",
        "data-annotation-gap-metric": "bbox-left-at-vertical-center-to-outer-triangle-right-edge",
        "data-annotation-visual-gap-target": f"{annotation_visual_gap:.2f}",
        "data-annotation-gap-tolerance": f"{annotation_gap_tolerance:.2f}",
    }
    parts = [f'<g {_attrs(group_attrs)}>']
    for index, points in enumerate(layer_points):
        point_string = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        shape = "triangle" if index == 0 else "trapezoid"
        cls = "pyramid-layer-fill focal" if index == 0 else "pyramid-layer-fill"
        parts.append(
            f'<polygon class="{cls}" points="{point_string}" data-pyramid-layer="{index}" '
            f'data-layer-shape="{shape}" data-top-y="{cuts[index]:.2f}" data-bottom-y="{cuts[index + 1]:.2f}"/>'
        )
    parts.append(
        _path(
            f"M {apex_x:.2f} {apex_y:.2f} L {base_right_x:.2f} {base_y:.2f} L {base_left_x:.2f} {base_y:.2f} Z",
            "pyramid-outer-outline",
            **{"data-role": "outer-triangle-outline"},
        )
    )
    parts.append(
        _path(
            f"M {boundaries[1][0]:.2f} {cuts[1]:.2f} L {apex_x:.2f} {apex_y:.2f} L {boundaries[1][1]:.2f} {cuts[1]:.2f}",
            "pyramid-apex-outline",
            **{"data-role": "apex-two-side-outline"},
        )
    )
    for index, (left_x, right_x, y) in enumerate(boundaries[1:-1]):
        parts.append(
            _line(
                left_x,
                y,
                right_x,
                y,
                "pyramid-divider focal" if index == 0 else "pyramid-divider",
                **{
                    "data-shared-boundary-index": index,
                    "data-boundary-render-count": "1",
                    "data-adjacent-layers": f"{index} {index + 1}",
                },
            )
        )
    for layer_index, (title, sub, title_y, sub_y) in enumerate(labels):
        for value, baseline_y, role, cls in (
            (title, title_y, "node_title", "node-title"),
            (sub, sub_y, "technical", "mono"),
        ):
            measured = METRICS.measure(role, value)
            bbox_height = measured.ascent + measured.descent
            parts.append(
                _text(
                    apex_x,
                    baseline_y,
                    value,
                    cls,
                    "middle",
                    **{
                        "data-pyramid-text-layer": layer_index,
                        "data-text-role": role,
                        "data-bbox-x": f"{apex_x - measured.width / 2:.2f}",
                        "data-bbox-y": f"{baseline_y - measured.ascent:.2f}",
                        "data-bbox-width": f"{measured.width:.2f}",
                        "data-bbox-height": f"{bbox_height:.2f}",
                        "data-minimum-polygon-inset": f"{minimum_text_inset:.2f}",
                        "data-font-size-preserved": "true",
                    },
                )
            )
    parts.append("</g>")
    for value, x, y, layer_index, note_kind, bbox_center_y, actual_gap in annotations:
        measured = METRICS.measure("technical", value)
        annotation_attrs = {
            "class": "pyramid-annotation accent" if layer_index == 0 else "pyramid-annotation",
            "x": f"{x:.2f}",
            "y": f"{y:.1f}",
            "text-anchor": "start",
            "data-pyramid-annotation": layer_index,
            "data-note-kind": note_kind,
            "data-bbox-x": f"{x:.2f}",
            "data-bbox-y": f"{y - measured.ascent:.2f}",
            "data-bbox-width": f"{measured.width:.2f}",
            "data-bbox-height": f"{measured.ascent + measured.descent:.2f}",
            "data-bbox-center-y": f"{bbox_center_y:.2f}",
            "data-visual-gap-target": f"{annotation_visual_gap:.2f}",
            "data-visual-gap-actual": f"{actual_gap:.2f}",
            "data-gap-reference": "bbox-vertical-center-to-outer-triangle-right-edge",
            "data-minimum-polygon-clearance": f"{minimum_annotation_clearance:.2f}",
            "data-semantic-binding": "apex" if layer_index == 0 else labels[layer_index][1],
        }
        parts.append(f"<text {_attrs(annotation_attrs)}>{escape(value)}</text>")
    parts += [
        _line(axis_x, 770, axis_x, 86, "axis", **{"marker-end": "url(#arrow)", "data-role": "leverage-axis", "data-polygon-clearance": f"{base_left_x - axis_x:.2f}"}),
        _text(54, 430, "RARER · HIGHER LEVERAGE", "kicker", "middle", transform="rotate(-90 54 430)"),
        _legend(882, w, (("accent", "apex"), ("line", "supporting layer")), "The base funds the apex; the apex defines the base."),
    ]
    svg = _svg_shell("containment-stack", "pyramid-funnel", "Tháp vận hành từ thủ tục đến quyết định", "Bốn lớp thu hẹp theo độ hiếm và đòn bẩy; apex là focal layer.", w, h, "".join(parts), semantic_ratio=.89)
    return Anchor(10, "containment-stack", "pyramid-funnel", "10-containment-stack--neutral-light", "Containment anchor", "Quy trình khối lượng lớn ở đáy tài trợ cho quyết định đòn bẩy cao ở đỉnh.", svg, (("layers", "4"), ("apex", "Flagship decision"), ("base", "Daily procedures")))


def compartment_anchor() -> Anchor:
    w, h = 1700, 1000
    top_center_y = 310.0
    order_center_x = 850.0
    horizontal_padding = 24.0
    bottom_padding = 32.0
    first_field_baseline = 128.0
    field_step = 38.0

    def entity_height(field_count: int) -> float:
        technical = METRICS.measure("technical", "Hg")
        return first_field_baseline + (field_count - 1) * field_step + technical.descent + bottom_padding

    entity_specs = [
        ("customer", 70.0, 390.0, "CUSTOMER", ("# id          uuid", "email         text · unique", "segment       enum", "created_at    timestamp"), False, False, True),
        ("order", 635.0, 430.0, "ORDER", ("# id          uuid", "→ customer_id uuid", "status        enum", "total         decimal", "placed_at     timestamp"), True, False, True),
        ("payment", 1240.0, 390.0, "PAYMENT", ("# id          uuid", "→ order_id    uuid", "provider      text", "amount        decimal", "captured_at   timestamp"), False, False, True),
        ("order-item", 655.0, 390.0, "ORDER_ITEM", ("→ order_id    uuid", "→ sku_id      uuid", "quantity      int", "unit_price    decimal"), False, True, False),
    ]
    entities: dict[str, tuple[float, float, float, float]] = {}
    parts = [
        '<g data-schema-layout="D-066" data-top-row-center-y="310.00" '
        'data-order-center-x="850.00" data-minimum-bottom-padding="24.00" '
        'data-minimum-relationship-label-node-clearance="8.00">'
    ]
    for entity_id, x, width, title, fields, focal, muted, top_row in entity_specs:
        height = entity_height(len(fields))
        y = top_center_y - height / 2 if top_row else 570.0
        entities[entity_id] = (x, y, width, height)
        cls = "node-card focal" if focal else "node-card muted" if muted else "node-card"
        center_x, center_y = x + width / 2, y + height / 2
        parts += [
            f'<g {_attrs({"class": cls, "data-schema-entity": entity_id, "data-box-x": f"{x:.2f}", "data-box-y": f"{y:.2f}", "data-box-width": f"{width:.2f}", "data-box-height": f"{height:.2f}", "data-center-x": f"{center_x:.2f}", "data-center-y": f"{center_y:.2f}", "data-horizontal-padding": f"{horizontal_padding:.2f}", "data-content-bottom-padding": f"{bottom_padding:.2f}", "data-field-count": len(fields), "data-top-row": str(top_row).lower()})}>',
            _rect(x, y, width, height, "node-boundary", 14),
            _text(x + horizontal_padding, y + 34, "ENTITY", "kicker"),
            _text(x + horizontal_padding, y + 70, title, "node-title"),
            _line(x, y + 86, x + width, y + 86, "grid"),
        ]
        for index, field in enumerate(fields):
            baseline = y + first_field_baseline + index * field_step
            measured = METRICS.measure("technical", field)
            parts.append(
                _text(
                    x + horizontal_padding,
                    baseline,
                    field,
                    "mono",
                    **{
                        "data-field-index": index,
                        "data-field-bbox-bottom": f"{baseline + measured.descent:.2f}",
                        "data-last-field": str(index == len(fields) - 1).lower(),
                    },
                )
            )
        parts.append("</g>")

    def horizontal_relationship(source_id: str, target_id: str, label: str) -> str:
        source_x, source_y, source_w, source_h = entities[source_id]
        target_x, target_y, _, target_h = entities[target_id]
        source_center_y = source_y + source_h / 2
        target_center_y = target_y + target_h / 2
        corridor_left = source_x + source_w
        corridor_right = target_x
        label_center_x = (corridor_left + corridor_right) / 2
        label_baseline_y = source_center_y - 28
        measured = METRICS.measure("technical", label)
        rendered_width = measured.width + max(0, len(label) - 1) * 0.5
        bbox_x = label_center_x - rendered_width / 2
        bbox_y = label_baseline_y - measured.ascent
        left_clearance = bbox_x - corridor_left
        right_clearance = corridor_right - (bbox_x + rendered_width)
        return (
            _line(
                corridor_left,
                source_center_y,
                corridor_right,
                target_center_y,
                "wire",
                **{
                    "data-schema-relationship": f"{source_id}-to-{target_id}",
                    "data-source": source_id,
                    "data-target": target_id,
                    "data-entry-alignment": "center",
                    "data-axis": "horizontal",
                },
            )
            + _text(
                label_center_x,
                label_baseline_y,
                label,
                "relationship-label",
                "middle",
                **{
                    "data-relationship-label": f"{source_id}-to-{target_id}",
                    "data-bbox-x": f"{bbox_x:.2f}",
                    "data-bbox-y": f"{bbox_y:.2f}",
                    "data-bbox-width": f"{rendered_width:.2f}",
                    "data-bbox-height": f"{measured.ascent + measured.descent:.2f}",
                    "data-corridor-left": f"{corridor_left:.2f}",
                    "data-corridor-right": f"{corridor_right:.2f}",
                    "data-left-node-clearance": f"{left_clearance:.2f}",
                    "data-right-node-clearance": f"{right_clearance:.2f}",
                    "data-minimum-node-clearance": "8.00",
                    "data-label-axis": "horizontal",
                },
            )
        )

    order_x, order_y, order_w, order_h = entities["order"]
    item_x, item_y, item_w, _ = entities["order-item"]
    vertical_label = "1 · CONTAINS · N"
    vertical_measured = METRICS.measure("technical", vertical_label)
    vertical_rendered_width = vertical_measured.width + max(0, len(vertical_label) - 1) * 0.5
    vertical_label_x = order_center_x + 22
    vertical_label_baseline = (order_y + order_h + item_y) / 2 + 6
    vertical_bbox_y = vertical_label_baseline - vertical_measured.ascent
    parts += [
        '<g data-schema-relationships="true" data-remediation="D-066">',
        horizontal_relationship("customer", "order", "1 · PLACES · N"),
        horizontal_relationship("order", "payment", "1 · PAID BY · N"),
        _line(
            order_center_x,
            order_y + order_h,
            item_x + item_w / 2,
            item_y,
            "wire",
            **{
                "data-schema-relationship": "order-to-order-item",
                "data-source": "order",
                "data-target": "order-item",
                "data-entry-alignment": "center",
                "data-axis": "vertical",
            },
        ),
        _text(
            vertical_label_x,
            vertical_label_baseline,
            vertical_label,
            "relationship-label",
            **{
                "data-relationship-label": "order-to-order-item",
                "data-bbox-x": f"{vertical_label_x:.2f}",
                "data-bbox-y": f"{vertical_bbox_y:.2f}",
                "data-bbox-width": f"{vertical_rendered_width:.2f}",
                "data-bbox-height": f"{vertical_measured.ascent + vertical_measured.descent:.2f}",
                "data-corridor-top": f"{order_y + order_h:.2f}",
                "data-corridor-bottom": f"{item_y:.2f}",
                "data-top-node-clearance": f"{vertical_bbox_y - (order_y + order_h):.2f}",
                "data-bottom-node-clearance": f"{item_y - (vertical_bbox_y + vertical_measured.ascent + vertical_measured.descent):.2f}",
                "data-minimum-node-clearance": "8.00",
                "data-label-axis": "vertical",
            },
        ),
        "</g>",
        "</g>",
        _legend(900, w, (("accent", "aggregate root"), ("line", "relationship"), ("dash", "join / dependent")), "# primary key · → foreign key · 1/N cardinality"),
    ]
    svg = _svg_shell("compartment-model", "database-schema", "Mô hình đơn hàng và thanh toán", "Bốn entity compartment với primary key, foreign key và cardinality rõ ràng.", w, h, "".join(parts))
    return Anchor(11, "compartment-model", "database-schema", "11-compartment-model--neutral-light", "Compartment anchor", "ORDER là aggregate root nối khách hàng, thanh toán và line item.", svg, (("entities", "Customer; Order; Payment; Order item"), ("root", "Order"), ("cardinality", "1:N")))


def matrix_anchor() -> Anchor:
    w, h = 1500, 980
    left, top, right, bottom = 190, 120, 1370, 758
    midx, midy = (left + right) / 2, (top + bottom) / 2
    vertical_note_offset_x = 24.0
    horizontal_note_offset_y = 42.0
    minimum_axis_clearance = 16.0

    def axis_note(
        value: str,
        x: float,
        baseline_y: float,
        anchor: str,
        *,
        note_id: str,
        axis: str,
        direction: str,
        arrow_placement: str,
        field_edge: str,
        axis_endpoint_x: float,
        axis_endpoint_y: float,
        axis_clearance: float,
    ) -> str:
        measured = METRICS.measure("technical", value)
        if anchor == "end":
            bbox_x = x - measured.width
        elif anchor == "middle":
            bbox_x = x - measured.width / 2
        else:
            bbox_x = x
        bbox_y = baseline_y - measured.ascent
        return _text(
            x,
            baseline_y,
            value,
            "axis-note",
            anchor,
            **{
                "data-axis-note": note_id,
                "data-axis": axis,
                "data-direction": direction,
                "data-arrow-placement": arrow_placement,
                "data-field-edge": field_edge,
                "data-axis-endpoint-x": f"{axis_endpoint_x:.2f}",
                "data-axis-endpoint-y": f"{axis_endpoint_y:.2f}",
                "data-bbox-x": f"{bbox_x:.2f}",
                "data-bbox-y": f"{bbox_y:.2f}",
                "data-bbox-width": f"{measured.width:.2f}",
                "data-bbox-height": f"{measured.ascent + measured.descent:.2f}",
                "data-axis-clearance": f"{axis_clearance:.2f}",
                "data-minimum-axis-clearance": f"{minimum_axis_clearance:.2f}",
                "data-vertical-offset-x": f"{x - midx:.2f}",
                "data-horizontal-offset-y": f"{baseline_y - midy:.2f}",
            },
        )

    top_note_baseline = top - 20.0
    horizontal_note_baseline = midy + horizontal_note_offset_y
    bottom_note_baseline = bottom + 46.0
    top_metrics = METRICS.measure("technical", "↑ HIGH IMPACT")
    horizontal_metrics = METRICS.measure("technical", "← LOW EFFORT")
    bottom_metrics = METRICS.measure("technical", "↓ LOW IMPACT")
    top_clearance = top - (top_note_baseline + top_metrics.descent)
    horizontal_clearance = horizontal_note_baseline - horizontal_metrics.ascent - midy
    bottom_clearance = bottom_note_baseline - bottom_metrics.ascent - bottom
    parts = [
        _rect(
            left,
            top,
            midx - left,
            midy - top,
            "matrix-focal-region",
            0,
            **{
                "data-focal-region-contract": "D-068",
                "data-fill-role": "accent-soft",
                "data-stroke": "none",
            },
        ),
        _line(left, midy, right, midy, "axis"), _line(midx, top, midx, bottom, "axis"),
        _text(left + 30, top + 46, "DO FIRST", "kicker"), _text(midx + 30, top + 46, "MAJOR PROJECTS", "kicker"),
        _text(left + 30, bottom - 28, "QUICK WINS", "kicker"), _text(right - 30, bottom - 28, "AVOID", "kicker", "end"),
        '<g data-axis-annotation-contract="D-067" data-axis-note-count="4" '
        f'data-axis-center-x="{midx:.2f}" data-axis-center-y="{midy:.2f}" '
        f'data-vertical-note-offset-x="{vertical_note_offset_x:.2f}" '
        f'data-horizontal-note-offset-y="{horizontal_note_offset_y:.2f}" '
        f'data-minimum-axis-clearance="{minimum_axis_clearance:.2f}">',
        axis_note(
            "↑ HIGH IMPACT", midx + vertical_note_offset_x, top_note_baseline, "start",
            note_id="high-impact", axis="impact", direction="positive", arrow_placement="prefix",
            field_edge="top", axis_endpoint_x=midx, axis_endpoint_y=top, axis_clearance=top_clearance,
        ),
        axis_note(
            "← LOW EFFORT", left, horizontal_note_baseline, "start",
            note_id="low-effort", axis="effort", direction="negative", arrow_placement="prefix",
            field_edge="left", axis_endpoint_x=left, axis_endpoint_y=midy, axis_clearance=horizontal_clearance,
        ),
        axis_note(
            "↓ LOW IMPACT", midx + vertical_note_offset_x, bottom_note_baseline, "start",
            note_id="low-impact", axis="impact", direction="negative", arrow_placement="prefix",
            field_edge="bottom", axis_endpoint_x=midx, axis_endpoint_y=bottom, axis_clearance=bottom_clearance,
        ),
        axis_note(
            "HIGH EFFORT →", right, horizontal_note_baseline, "end",
            note_id="high-effort", axis="effort", direction="positive", arrow_placement="suffix",
            field_edge="right", axis_endpoint_x=right, axis_endpoint_y=midy, axis_clearance=horizontal_clearance,
        ),
        "</g>",
    ]
    points = [
        (360, 240, "Freeze contract", True), (550, 356, "Update glossary", False), (980, 240, "Engine gallery", False),
        (1180, 320, "Full adapter pass", False), (410, 610, "Fix one label", False), (1040, 610, "Rewrite package", False),
    ]
    for x, y, label, focal in points:
        parts += [_circle(x, y, 13 if focal else 9, "accent-dot" if focal else "dot"), _text(x + 24, y + 7, label, "material-strong")]
    parts += [_legend(872, w, (("accent", "start now"), ("dot", "candidate")), "Position is the signal; coral is reserved for one action.")]
    svg = _svg_shell("spatial-matrix", "quadrant", "Ma trận effort và impact", "Sáu initiative được định vị trên hai trục; Freeze contract là hành động duy nhất được ưu tiên.", w, h, "".join(parts), semantic_ratio=.82)
    return Anchor(12, "spatial-matrix", "quadrant", "12-spatial-matrix--neutral-light", "Spatial matrix anchor", "Freeze contract là hành động high-impact/low-effort cần làm trước.", svg, (("x", "Effort"), ("y", "Impact"), ("focal", "Freeze contract")))


def quantitative_anchor() -> Anchor:
    w, h = 1500, 980
    left, top, right, bottom = 170, 110, 1370, 740
    parts = [_line(left, bottom, right, bottom, "axis"), _line(left, top, left, bottom, "axis", **{"marker-end": "url(#arrow)"})]
    for value in range(0, 101, 20):
        y = bottom - value * 5.6
        parts += [_line(left, y, right, y, "grid"), _text(left - 26, y + 6, str(value), "mono", "end")]
    for value in range(0, 101, 20):
        x = left + value * 11.5
        parts += [_line(x, bottom, x, bottom + 10, "axis"), _text(x, bottom + 42, str(value), "mono", "middle")]
    data = [
        (24, 72, 18, "Manual review", False), (42, 58, 32, "Rules engine", False),
        (62, 78, 46, "Hybrid", True), (78, 52, 24, "Auto-approve", False), (88, 32, 14, "Fast path", False),
    ]
    for xv, yv, size, label, focal in data:
        x = left + xv * 11.5; y = bottom - yv * 5.6; r = sqrt(size) * 5.2
        fill = TOKENS["accent"] if focal else TOKENS["ink"]
        opacity = ".80" if focal else ".24"
        parts += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" fill-opacity="{opacity}" stroke="{fill}" stroke-width="2" data-x="{xv}" data-y="{yv}" data-size="{size}"/>', _text(x + r + 12, y + 6, label, "material")]
    parts += [_text((left+right)/2, 838, "AUTOMATION %", "kicker", "middle"), _text(62, (top+bottom)/2, "CONTROL CONFIDENCE", "kicker", "middle", transform=f"rotate(-90 62 {(top+bottom)/2})"), _legend(878, w, (("accent", "recommended"), ("dot", "alternative")), "Bubble area encodes monthly volume; exact values are in the accessible table.")]
    svg = _svg_shell("quantitative", "scatter-plot", "Tự động hóa, kiểm soát và khối lượng", "Năm phương án trên hai trục; diện tích bubble mã hóa volume và Hybrid là focal recommendation.", w, h, "".join(parts), semantic_ratio=.83)
    return Anchor(13, "quantitative", "scatter-plot", "13-quantitative--neutral-light", "Quantitative anchor", "Hybrid cân bằng automation 62, confidence 78 và volume 46.", svg, tuple((label, f"automation={x}; confidence={y}; volume={size}") for x, y, size, label, _ in data))


def special_anchor() -> Anchor:
    w, h = 1640, 960
    parts = [_text(84, 120, "INTAKE", "kicker"), _text(710, 120, "ROUTING", "kicker"), _text(1400, 120, "OUTCOME", "kicker")]
    nodes = [
        (90, 210, 42, 300, "Monthly budget", "12,000 min", True),
        (720, 170, 30, 220, "Unit tests", "5,200 min", False),
        (720, 430, 30, 190, "E2E", "4,000 min", True),
        (720, 670, 30, 120, "Build + lint", "2,800 min", False),
        (1420, 190, 30, 340, "Passed", "9,400 min", False),
        (1420, 590, 30, 130, "Failed", "1,600 min", False),
        (1420, 770, 30, 72, "Flaked", "1,000 min", True),
    ]
    for x, y, nw, nh, title, sub, focal in nodes:
        color = TOKENS["accent"] if focal and title == "Flaked" else TOKENS["ink"]
        parts += [f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" fill="{color}" rx="4"/>', _text(x - 16 if x > 1000 else x + nw + 16, y + nh/2 - 6, title, "node-title", "end" if x > 1000 else "start"), _text(x - 16 if x > 1000 else x + nw + 16, y + nh/2 + 24, sub, "mono", "end" if x > 1000 else "start")]
    ribbons = [
        ("M132 250 C330 250 510 220 720 220 L720 390 C510 390 330 400 132 400 Z", TOKENS["line_soft"], .74),
        ("M132 410 C360 410 520 470 720 470 L720 610 C520 610 360 560 132 560 Z", TOKENS["line_soft"], .74),
        ("M132 570 C350 570 540 700 720 700 L720 790 C540 790 350 680 132 680 Z", TOKENS["line_soft"], .74),
        ("M750 200 C980 200 1190 210 1420 230 L1420 480 C1180 440 980 370 750 360 Z", TOKENS["line_soft"], .72),
        ("M750 470 C980 470 1190 470 1420 470 L1420 610 C1190 610 980 610 750 610 Z", TOKENS["line_soft"], .72),
        ("M750 700 C980 700 1190 540 1420 520 L1420 610 C1190 640 980 760 750 780 Z", TOKENS["line_soft"], .72),
        ("M750 360 C980 360 1190 800 1420 790 L1420 842 C1190 850 980 440 750 390 Z", TOKENS["accent"], .32),
    ]
    parts = [f'<path d="{d}" fill="{color}" fill-opacity="{opacity}" stroke="none"/>' for d, color, opacity in ribbons] + parts
    parts += [_legend(860, w, (("line", "stage routing"), ("accent", "flaked rerun"), ("dot", "stage total")), "Ribbon width is proportional; totals reconcile to 12,000 minutes.")]
    svg = _svg_shell("special-geometry", "sankey", "Phân bổ CI minutes theo outcome", "Các ribbon bảo toàn tổng 12,000 phút qua stage và outcome; flaked path được nhấn coral.", w, h, "".join(parts), semantic_ratio=.84)
    return Anchor(14, "special-geometry", "sankey", "14-special-geometry--neutral-light", "Special geometry anchor", "Flaked reruns tiêu tốn 1,000 trên 12,000 CI minutes.", svg, (("budget", "12000"), ("stages", "5200 + 4000 + 2800 = 12000"), ("outcomes", "9400 + 1600 + 1000 = 12000"), ("flaked", "1000")))


def anchors_without_swimlane() -> tuple[Anchor, ...]:
    builders: tuple[Callable[[], Anchor], ...] = (
        topology_anchor, integration_anchor, deployment_anchor, dependency_anchor,
        directed_anchor, time_anchor, experience_anchor, hierarchy_anchor,
        containment_anchor, compartment_anchor, matrix_anchor, quantitative_anchor,
        special_anchor,
    )
    return tuple(builder() for builder in builders)


def render_html(anchor: Anchor) -> str:
    rows = "".join(f"<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>" for key, value in anchor.facts)
    receipts = []
    for role in ("display", "material", "technical"):
        resolved = TYPOGRAPHY[role]
        source = "disclosed fallback" if resolved.fallback_used else "preferred default"
        receipts.append(f"<span><strong>{escape(resolved.resolved_family)}</strong> · {source}</span>")
    return f'''<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(anchor.title)} · P-18R6</title>
  <style>
    :root{{--paper:#eeece7;--ink:#252b3c;--muted:#687286;}}
    *{{box-sizing:border-box}} html,body{{margin:0;min-height:100%;background:var(--paper);color:var(--ink)}}
    body{{font-family:'{escape(resolved_family('material'))}',sans-serif;padding:48px 24px 80px}}
    main{{width:min(100%,1720px);margin:auto}} header{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;margin-bottom:24px}}
    .eyebrow{{margin:0 0 8px;font-family:'{escape(resolved_family('technical'))}',monospace;font-size:14px;letter-spacing:.16em;color:#f26a32}}
    h1{{margin:0;font-family:'{escape(resolved_family('display'))}',serif;font-size:48px;line-height:1.06;font-weight:400}}
    .lede{{max-width:760px;margin:10px 0 0;font-size:16px;line-height:1.55;color:var(--muted)}}
    .receipts{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px}} .receipts span{{padding:7px 10px;border:1px solid #c9cdd2;border-radius:7px;background:#ffffff8a;font:12px '{escape(resolved_family('technical'))}',monospace;color:#657086}}
    .artifact-frame{{overflow:hidden;border:1px solid #d8d6d1;border-radius:18px;background:#f7f6f2;box-shadow:0 20px 60px #2d34431a}}
    .artifact-frame svg{{display:block;width:100%;height:auto}} .evidence{{margin-top:24px;padding:24px;border:1px solid #d8d6d1;border-radius:14px;background:#ffffff8a}}
    .evidence h2{{margin:0 0 8px;font-size:20px}} .evidence p{{margin:0 0 14px;font-size:16px;color:var(--muted)}} table{{border-collapse:collapse;width:100%;font-size:14px}} th,td{{padding:10px 12px;border-top:1px solid #d8d6d1;text-align:left}}
    @media(max-width:820px){{body{{padding:24px 12px 48px}}header{{grid-template-columns:1fr}}.receipts{{justify-content:flex-start}}h1{{font-size:40px}}.evidence{{overflow-x:auto}}}}
    @media print{{body{{padding:0;background:#fff}}header,.evidence{{display:none}}.artifact-frame{{border:0;box-shadow:none}}}}
  </style>
</head>
<body><main>
  <header><div><p class="eyebrow">P‑18R6 · NEUTRAL LIGHT · ENGINE {anchor.order:02d}</p><h1>{escape(anchor.title)}</h1><p class="lede">{escape(anchor.takeaway)}</p></div><div class="receipts" aria-label="Resolved font receipt">{"".join(receipts)}</div></header>
  <section class="artifact-frame" aria-label="Canonical engine anchor">{anchor.svg}</section>
  <section class="evidence" aria-labelledby="evidence-heading"><h2 id="evidence-heading">Semantic projection</h2><p>Nằm ngoài canonical screenshot và không tham gia masked blind/five-second review.</p><table><tbody>{rows}</tbody></table></section>
</main></body></html>'''


__all__ = [
    "Anchor",
    "CORNER_STYLES",
    "TOKENS",
    "TYPOGRAPHY",
    "anchors_without_swimlane",
    "dependency_anchor",
    "deployment_anchor",
    "integration_anchor",
    "orthogonal_route_d",
    "render_html",
    "resolved_family",
    "topology_anchor",
]
