"""P-19B three-mode standalone HTML renderer for the v1.5 gallery.

This module consumes the validated P-19A adapter plan and emits one complete,
self-contained HTML document.  It has no network dependency, no script
runtime, and no generic/unknown fallback.  Every approved adapter id is bound
to an explicit visual recipe while the three modes share identical semantics
and geometry.
"""

from __future__ import annotations

from html import escape
import json
import math
import re
from typing import Any, Callable, Mapping
import xml.etree.ElementTree as ET

from gantt_layout_v15 import gantt_css, gantt_table, layout_gantt, render_gantt
from flywheel_layout_v15 import flywheel_css, flywheel_table, layout_flywheel, render_flywheel
from fishbone_layout_v15 import fishbone_css, fishbone_table, layout_fishbone, render_fishbone
from dp_integration_layout_v15 import (
    dp_integration_css, dp_integration_table, is_detailed_dp_integration,
    layout_dp_integration, render_dp_integration, validate_dp_integration_svg,
)
from bar_chart_layout_v15 import (
    bar_chart_css, bar_chart_table, is_detailed_bar_chart,
    layout_bar_chart, render_bar_chart, validate_bar_chart_svg,
)
from line_chart_layout_v15 import (
    is_detailed_line_chart, layout_line_chart, line_chart_css,
    line_chart_table, render_line_chart, validate_line_chart_svg,
)
from scatter_chart_layout_v15 import (
    is_detailed_scatter_chart, layout_scatter_chart, render_scatter_chart,
    scatter_chart_css, scatter_chart_table, validate_scatter_chart_svg,
)
from radar_layout_v15 import (
    is_detailed_radar, layout_radar, radar_css, radar_table,
    render_radar, validate_radar_svg,
)
from dp_security_matrix_layout_v15 import (
    dp_security_matrix_css, dp_security_matrix_table,
    is_detailed_dp_security_matrix, layout_dp_security_matrix,
    render_dp_security_matrix, validate_dp_security_matrix_svg,
)
from er_data_model_layout_v15 import (
    er_data_model_css, er_data_model_table, is_detailed_er_data_model,
    layout_er_data_model, render_er_data_model, validate_er_data_model_svg,
)
from uml_class_layout_v15 import (
    is_detailed_uml_class, layout_uml_class, render_uml_class,
    uml_class_css, uml_class_table, validate_uml_class_svg,
)
from high_level_layout_v15 import (
    high_level_css, high_level_table, is_detailed_high_level,
    layout_high_level, render_high_level, validate_high_level_svg,
)
from it_current_state_layout_v15 import (
    is_detailed_it_current_state, it_current_state_css, it_current_state_table,
    layout_it_current_state, render_it_current_state,
    validate_it_current_state_svg,
)
from kanban_layout_v15 import (
    is_detailed_kanban, kanban_css, kanban_table, layout_kanban,
    render_kanban, validate_kanban_svg,
)
from layers_layout_v15 import (
    is_detailed_layers, layers_css, layers_table, layout_layers,
    render_layers, validate_layers_svg,
)
from medallion_layout_v15 import (
    is_detailed_medallion, layout_medallion, medallion_css,
    medallion_table, render_medallion, validate_medallion_svg,
)
from polar_chart_layout_v15 import (
    is_detailed_polar_chart, layout_polar_chart, polar_chart_css,
    polar_chart_table, render_polar_chart, validate_polar_chart_svg,
)
from wardley_map_layout_v15 import (
    is_detailed_wardley_map, layout_wardley_map, render_wardley_map,
    validate_wardley_map_svg, wardley_map_css, wardley_map_table,
)
from venn_layout_v15 import (
    is_detailed_venn, layout_venn, render_venn, validate_venn_svg,
    venn_css, venn_table,
)
from treemap_layout_v15 import (
    is_detailed_treemap, layout_treemap, render_treemap,
    treemap_css, treemap_table, validate_treemap_svg,
)
from tree_layout_v15 import (
    is_detailed_tree, layout_tree, render_tree, tree_css, tree_table,
    validate_tree_svg,
)
from story_map_layout_v15 import (
    is_detailed_story_map, layout_story_map, render_story_map,
    story_map_css, story_map_table, validate_story_map_svg,
)
from state_machine_layout_v15 import (
    is_detailed_state_machine, layout_state_machine, render_state_machine,
    state_machine_css, state_machine_table, validate_state_machine_svg,
)
from sequence_layout_v15 import (
    is_detailed_sequence, layout_sequence, render_sequence,
    sequence_css, sequence_table, validate_sequence_svg,
)
from connector_policy_v15 import CONNECTOR_POLICY_ID, ROUTE_PRIORITY
from visual_adapters_v15 import CAPABILITY_ADAPTERS, TYPE_ADAPTERS, adapt_visual
P19B_SCHEMA_VERSION = "1.1"
P19B_CANDIDATE_ID = "P19B-P18-INHERITED-THREE-MODE-REVIEW-34-1.5.0"
P18_PARENT_CANDIDATE_ID = "P18R6-FOURTEEN-ENGINE-NEUTRAL-LIGHT-REVIEW-17-1.5.0"
P18_PARENT_MANIFEST_SHA256 = "7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a"
MODES = ("neutral-light", "neutral-dark", "editorial")
VIEWBOX = (0, 0, 1200, 760)

# D-080: all modes derive from the owner-approved P-18R6 review-17 visual
# grammar. Neutral-light preserves the exact P-18 roles; dark/editorial change
# semantic color roles only and never geometry or typography roles.
P18_VISUAL_MODES: dict[str, dict[str, str]] = {
    "neutral-light": {
        "paper": "#eeece7", "canvas": "#f7f6f2", "surface": "#ffffff",
        "surface_alt": "#eeece7", "text": "#252b3c", "muted": "#687286",
        "border": "#c7ccd2", "connector": "#4f5e76", "grid": "#d9d7d2",
        "accent": "#f26a32", "accent_soft": "#f8e7dd", "accent_text": "#df5522",
        "blue": "#2f65af", "green": "#7c9167", "amber": "#b9894b",
        "plum": "#756b7f", "danger": "#b9473f", "on_accent": "#ffffff",
    },
    "neutral-dark": {
        "paper": "#171b24", "canvas": "#1c2230", "surface": "#252c3a",
        "surface_alt": "#303746", "text": "#f4f0e8", "muted": "#b8c0cf",
        "border": "#596475", "connector": "#c9d1de", "grid": "#414a58",
        "accent": "#f26a32", "accent_soft": "#4c2d25", "accent_text": "#ff9a74",
        "blue": "#78a5e8", "green": "#a5b98c", "amber": "#d5aa70",
        "plum": "#a89bb3", "danger": "#ef7d73", "on_accent": "#171b24",
    },
    "editorial": {
        "paper": "#e9e3d8", "canvas": "#f7f3ea", "surface": "#fffdf8",
        "surface_alt": "#e9e3d8", "text": "#252b3c", "muted": "#6d685f",
        "border": "#c9c1b4", "connector": "#4f5e76", "grid": "#d8d0c2",
        "accent": "#f26a32", "accent_soft": "#f8e7dd", "accent_text": "#c84c1f",
        "blue": "#365f96", "green": "#748765", "amber": "#a87d45",
        "plum": "#71697a", "danger": "#a8443c", "on_accent": "#ffffff",
    },
}


class GalleryRenderError(ValueError):
    """Fail-closed P-19B renderer error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _text(value: Any) -> str:
    return escape(str(value), quote=True)


def _labels(plan: Mapping[str, Any], collection: str, fallback: tuple[str, ...]) -> list[str]:
    values = [str(item.get("label") or item.get("id")) for item in plan["semantic_projection"].get(collection, [])]
    return values or list(fallback)


def _svg_text(x: float, y: float, value: str, css: str = "label", anchor: str = "middle") -> str:
    return f'<text class="{css}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{_text(value)}</text>'


def _card(x: float, y: float, w: float, h: float, label: str, *, css: str = "node", radius: int = 18, parent: str | None = None) -> str:
    binding = f' data-parent-container="{_text(parent)}"' if parent else ""
    return (
        f'<g class="node-card"{binding}><rect class="{css}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}"/>'
        f'{_svg_text(x + w / 2, y + h / 2 + 6, label)}</g>'
    )


def _line(x1: float, y1: float, x2: float, y2: float, *, arrow: bool = False, css: str = "connector") -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<line class="{css}" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"{marker}/>'


def _poly(points: list[tuple[float, float]], *, css: str = "connector", close: bool = False) -> str:
    encoded = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    tag = "polygon" if close else "polyline"
    return f'<{tag} class="{css}" points="{encoded}"/>'


def _centered_enclosure(children: list[tuple[float, float, float, float]], *, padding: float = 24, min_height: float = 0) -> tuple[float, float, float, float]:
    """Derive the parent from the child union; preserve child coordinates."""
    if (not children or not math.isfinite(padding) or padding < 0
            or not math.isfinite(min_height) or min_height < 0
            or any(len(box) != 4 or not all(math.isfinite(v) for v in box)
                   or box[2] <= 0 or box[3] <= 0 for box in children)):
        raise GalleryRenderError("enclosure-invalid", "Finite positive child bounds and nonnegative padding required.")
    left = min(box[0] for box in children)
    top = min(box[1] for box in children)
    right = max(box[0] + box[2] for box in children)
    bottom = max(box[1] + box[3] for box in children)
    width, height = right - left + 2 * padding, max(bottom - top + 2 * padding, min_height)
    return ((left + right - width) / 2, (top + bottom - height) / 2, width, height)


def _orthogonal_path(points: list[tuple[float, float]], *, corner_style: str = "rounded", radius: float = 30) -> str:
    """One subpath; rounded joins and straight corners never need erase overlays."""
    if corner_style not in ("rounded", "straight"):
        raise GalleryRenderError("corner-style-invalid", "Expected rounded or straight corners.")
    if len(points) < 2 or not math.isfinite(radius) or radius < 0 or any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in points):
        raise GalleryRenderError("route-invalid", "Expected a finite orthogonal route.")
    vectors = []
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = bx - ax, by - ay
        if (dx == 0) == (dy == 0):
            raise GalleryRenderError("route-invalid", "Zero-length or diagonal segment.")
        length = abs(dx) + abs(dy)
        vectors.append((dx / length, dy / length, length))
    commands = [f"M{points[0][0]:g} {points[0][1]:g}"]
    for index, (x, y) in enumerate(points[1:-1], 1):
        ux, uy, before = vectors[index - 1]
        vx, vy, after = vectors[index]
        if ux * vx + uy * vy < 0:
            raise GalleryRenderError("route-invalid", "Immediate reversal is not a corner.")
        if corner_style == "rounded" and (ux, uy) != (vx, vy) and radius:
            bend = min(radius, before / 2, after / 2)
            commands.extend((f"L{x - ux * bend:g} {y - uy * bend:g}",
                             f"Q{x:g} {y:g} {x + vx * bend:g} {y + vy * bend:g}"))
        else:
            commands.append(f"L{x:g} {y:g}")
    commands.append(f"L{points[-1][0]:g} {points[-1][1]:g}")
    return " ".join(commands)


def validate_target_geometry(svg: str, diagram_type: str) -> dict[str, Any]:
    """Focused D-081 assertions against emitted shapes, not metadata claims."""
    if diagram_type not in ("dp-integration", "swimlane", "sequence", "bar-chart", "line-chart", "polar-chart", "wardley-map", "venn", "dp-security-matrix", "er-data-model", "high-level", "it-current-state", "kanban", "story-map", "state-machine", "layer-stack", "medallion", "tree"):
        return {}
    root = ET.fromstring(svg)
    if diagram_type == "sequence":
        if root.find(".//*[@data-sequence-contract]") is None:
            return {}
        try:
            return validate_sequence_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("sequence-invalid", str(error)) from error
    if diagram_type == "state-machine":
        if root.find(".//*[@data-state-machine-contract]") is None:
            return {}
        try:
            return validate_state_machine_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("state-machine-invalid", str(error)) from error
    if diagram_type == "story-map":
        if root.find(".//*[@data-story-map-contract]") is None:
            return {}
        try:
            return validate_story_map_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("story-map-invalid", str(error)) from error
    if diagram_type == "tree":
        if root.find(".//*[@data-tree-contract]") is None:
            return {}
        try:
            return validate_tree_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("tree-invalid", str(error)) from error
    if diagram_type == "medallion":
        if root.find(".//*[@data-medallion-contract]") is None:
            return {}
        try:
            return validate_medallion_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("medallion-invalid", str(error)) from error
    if diagram_type == "layer-stack":
        if root.find(".//*[@data-layers-contract]") is None:
            return {}
        try:
            return validate_layers_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("layers-invalid", str(error)) from error
    if diagram_type == "kanban":
        if root.find(".//*[@data-kb-contract]") is None:
            return {}
        try:
            return validate_kanban_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("kanban-invalid", str(error)) from error
    if diagram_type == "it-current-state":
        if root.find(".//*[@data-ics-contract]") is None:
            return {}
        try:
            return validate_it_current_state_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("it-current-state-invalid", str(error)) from error
    if diagram_type == "high-level":
        if root.find(".//*[@data-hl-contract]") is None:
            return {}
        try:
            return validate_high_level_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("high-level-invalid", str(error)) from error
    if diagram_type == "er-data-model":
        if root.find(".//*[@data-er-entity-id]") is None:
            return {}
        try:
            return validate_er_data_model_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("er-data-model-invalid", str(error)) from error
    if diagram_type == "uml-class":
        if root.find(".//*[@data-uml-class-contract]") is None:
            return {}
        try:
            return validate_uml_class_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("uml-class-invalid", str(error)) from error
    if diagram_type == "dp-security-matrix":
        if root.find(".//*[@data-matrix-cell-id]") is None:
            return {}
        try:
            return validate_dp_security_matrix_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("security-matrix-invalid", str(error)) from error
    if diagram_type == "bar-chart":
        if root.find(".//*[@data-bar-id]") is None:
            return {}
        try:
            return validate_bar_chart_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("bar-chart-invalid", str(error)) from error
    if diagram_type == "line-chart":
        if root.find(".//*[@data-line-chart-contract]") is None:
            return {}
        try:
            return validate_line_chart_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("line-chart-invalid", str(error)) from error
    if diagram_type == "scatter-plot":
        if root.find(".//*[@data-scatter-chart-contract]") is None:
            return {}
        try:
            return validate_scatter_chart_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("scatter-chart-invalid", str(error)) from error
    if diagram_type == "radar":
        if root.find(".//*[@data-radar-contract]") is None:
            return {}
        try:
            return validate_radar_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("radar-invalid", str(error)) from error
    if diagram_type == "polar-chart":
        if root.find(".//*[@data-polar-chart-contract]") is None:
            return {}
        try:
            return validate_polar_chart_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("polar-chart-invalid", str(error)) from error
    if diagram_type == "wardley-map":
        if root.find(".//*[@data-wardley-map-contract]") is None:
            return {}
        try:
            return validate_wardley_map_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("wardley-map-invalid", str(error)) from error
    if diagram_type == "venn":
        if root.find(".//*[@data-venn-contract]") is None:
            return {}
        try:
            return validate_venn_svg(svg)
        except ValueError as error:
            raise GalleryRenderError("venn-invalid", str(error)) from error
    if diagram_type == "dp-integration":
        if root.find(".//*[@data-dp-group-id='boundary-data-platform']") is not None:
            try:
                return validate_dp_integration_svg(svg)
            except ValueError as error:
                raise GalleryRenderError("dp-topology-invalid", str(error)) from error
        parent = root.find(".//*[@id='integration-api-zone']")
        group = root.find(".//*[@data-parent-container='integration-api-zone']")
        child = group.find("rect") if group is not None else None
        if parent is None or child is None:
            raise GalleryRenderError("enclosure-invalid", "Missing parent/child binding.")
        px, py, pw, ph = (float(parent.attrib[key]) for key in ("x", "y", "width", "height"))
        cx, cy, cw, ch = (float(child.attrib[key]) for key in ("x", "y", "width", "height"))
        gaps = [cx - px, cy - py, px + pw - cx - cw, py + ph - cy - ch]
        errors = [abs(px + pw / 2 - cx - cw / 2), abs(py + ph / 2 - cy - ch / 2)]
        if not all(math.isfinite(v) for v in gaps + errors) or min(gaps) < 24 or max(errors) > .01:
            raise GalleryRenderError("enclosure-invalid", "Child must be contained with symmetric minimum 24px padding.")
        return {"padding_ltrb": gaps, "center_error_xy": errors}
    paths = [e for e in root.iter("path") if e.attrib.get("data-connector-id") == "swimlane-handoff"]
    if len(paths) != 1:
        raise GalleryRenderError("connector-discontinuous", "Exactly one semantic handoff path required.")
    path = paths[0]
    style = path.attrib.get("data-corner-style")
    expected = _orthogonal_path([(460, 265), (650, 265), (650, 445), (740, 445)], corner_style=style)
    if (path.attrib.get("d") != expected or path.attrib.get("class") != "connector"
            or path.attrib.get("marker-end") != "url(#arrow)"
            or any(e.tag in ("mask", "clipPath") or "bridge" in e.attrib.get("class", "").split() for e in root.iter())
            or any(key in path.attrib for key in ("style", "stroke", "opacity", "stroke-opacity", "stroke-dasharray", "mask", "clip-path"))):
        raise GalleryRenderError("connector-discontinuous", "Handoff must be one visible unmasked contiguous path.")
    # In this two-node lane there is no connector crossing needing an underlay.
    other_routes = [e for e in root.iter("path") if e is not path and e.attrib.get("class")]
    if other_routes:
        raise GalleryRenderError("connector-discontinuous", "Unexpected overlay in the handoff artwork.")
    return {"corner_style": style, "semantic_paths": 1, "erase_overlays": 0,
            "start": [460, 265], "end": [740, 445], "continuous_subpaths": len(re.findall("M", expected))}


def _topology(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "high-level" and is_detailed_high_level(plan):
        return render_high_level(plan, plan.get("connector_corner_style", "rounded"))
    if kind == "it-current-state" and is_detailed_it_current_state(plan):
        return render_it_current_state(plan, plan.get("connector_corner_style", "rounded"))
    labels = _labels(plan, "nodes", ("Input", "Core", "Output"))
    if kind == "architecture":
        return '<rect class="zone" x="170" y="155" width="860" height="390" rx="30"/>' + _svg_text(205, 192, "TRUST ZONE", "micro", "start") + _card(230, 280, 240, 110, labels[0]) + _line(470, 335, 700, 335, arrow=True) + _card(700, 280, 260, 110, labels[-1], css="node focal")
    if kind == "it-current-state":
        return _card(150, 220, 270, 130, labels[0], css="node warning") + _line(420, 285, 760, 285, arrow=True) + _card(760, 220, 290, 130, labels[-1], css="node focal") + '<circle class="status danger-fill" cx="380" cy="245" r="10"/><circle class="status success-fill" cx="1010" cy="245" r="10"/>' + _svg_text(285, 430, "LEGACY", "micro") + _svg_text(905, 430, "ACTIVE", "micro")
    return '<rect class="zone" x="105" y="170" width="990" height="360" rx="26"/>' + "".join(_card(160 + i * 330, 285, 220, 100, label, css="node focal" if i == 1 else "node") for i, label in enumerate((labels + ["Govern"] * 3)[:3])) + _line(380, 335, 490, 335, arrow=True) + _line(710, 335, 820, 335, arrow=True) + '<rect class="accent-band" x="160" y="455" width="880" height="26" rx="13"/>' + _svg_text(600, 475, "CROSS-CUTTING GOVERNANCE", "micro")


def _pipeline(plan: Mapping[str, Any]) -> str:
    if plan["adapter"]["canonical_type"] == "dp-integration" and is_detailed_dp_integration(plan):
        return render_dp_integration(plan)
    labels = _labels(plan, "nodes", ("Source", "Transform", "Consumer"))
    kind = plan["adapter"]["canonical_type"]
    cards = []
    boxes = [(120 + index * 370, 275, 260, 120) for index in range(3)]
    for index, label in enumerate((labels + ["Transform", "Consumer"])[:3]):
        x, y, w, h = boxes[index]
        css = "node focal" if (kind == "dp-integration" and index == 1) else "node"
        parent = "integration-api-zone" if kind == "dp-integration" and index == 1 else None
        cards.append(_card(x, y, w, h, label, css=css, parent=parent))
        if index < 2:
            cards.append(_line(x + 260, 335, x + 370, 335, arrow=True))
    boundary = ""
    if kind == "dp-integration":
        x, y, w, h = _centered_enclosure([boxes[1]], padding=24, min_height=290)
        boundary = f'<rect id="integration-api-zone" class="zone dashed" data-min-padding="24" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="26"/>'
    return boundary + "".join(cards) + _svg_text(600, 520, "SOURCE → TRANSFORM → SINK", "micro")


def _deployment(plan: Mapping[str, Any]) -> str:
    labels = _labels(plan, "nodes", ("API", "Database"))
    return '<rect class="zone" x="105" y="150" width="440" height="420" rx="28"/>' + '<rect class="zone" x="655" y="150" width="440" height="420" rx="28"/>' + _svg_text(145, 190, "APPLICATION ZONE", "micro", "start") + _svg_text(695, 190, "DATA ZONE", "micro", "start") + _card(170, 270, 310, 140, labels[0], css="node focal") + _card(720, 270, 310, 140, labels[-1]) + _line(480, 340, 720, 340, arrow=True) + _svg_text(600, 320, "8443 → 5432", "micro")


def _dependency(plan: Mapping[str, Any]) -> str:
    labels = _labels(plan, "nodes", ("A", "B", "C"))
    a, b, c = (labels + ["B", "C"])[:3]
    return _card(130, 300, 220, 100, a) + _card(490, 175, 220, 100, b, css="node focal") + _card(850, 300, 220, 100, c) + _line(350, 350, 490, 225, arrow=True) + _line(710, 225, 850, 350, arrow=True) + '<path class="connector backedge" d="M960 400 C960 570 240 570 240 400" marker-end="url(#arrow)"/>' + _svg_text(600, 600, "EXPLICIT CYCLE BACK-EDGE", "micro")


def _directed(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Start", "Review", "Done"))
    if kind == "flowchart":
        return '<ellipse class="node" cx="220" cy="350" rx="120" ry="58"/>' + _svg_text(220, 356, labels[0]) + _line(340, 350, 500, 350, arrow=True) + '<polygon class="node focal" points="600,240 710,350 600,460 490,350"/>' + _svg_text(600, 356, labels[1]) + _line(710, 350, 875, 245, arrow=True) + _line(710, 350, 875, 455, arrow=True) + _card(875, 190, 230, 100, labels[2]) + _card(875, 405, 230, 100, labels[-1]) + _svg_text(780, 270, "YES", "micro") + _svg_text(780, 445, "NO", "micro")
    if kind == "state-machine":
        if is_detailed_state_machine(plan):
            return render_state_machine(plan)
        return '<circle class="ink-fill" cx="130" cy="350" r="18"/>' + _line(148, 350, 285, 350, arrow=True) + _card(285, 290, 250, 120, labels[0], radius=60) + _line(535, 350, 680, 350, arrow=True) + _card(680, 290, 250, 120, labels[1], css="node focal", radius=60) + _line(930, 350, 1040, 350, arrow=True) + '<circle class="terminal" cx="1080" cy="350" r="28"/><circle class="terminal" cx="1080" cy="350" r="19"/>'
    return _card(130, 285, 260, 130, labels[0]) + _line(390, 350, 560, 350, arrow=True) + '<path class="document" d="M560 275 H890 V405 Q808 365 725 405 Q642 445 560 405 Z"/>' + _svg_text(725, 340, labels[-1]) + _svg_text(600, 510, "ACTIVITY → ARTIFACT", "micro")


def _lane(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Sender", "Receiver"))
    if kind == "sequence":
        if is_detailed_sequence(plan):
            return render_sequence(plan)
        x1, x2 = 340, 860
        return _card(x1 - 110, 130, 220, 80, labels[0]) + _card(x2 - 110, 130, 220, 80, labels[-1]) + _line(x1, 210, x1, 590, css="lifeline") + _line(x2, 210, x2, 590, css="lifeline") + _line(x1, 310, x2, 310, arrow=True) + _line(x2, 450, x1, 450, arrow=True, css="connector dashed") + _svg_text(600, 290, "REQUEST", "micro") + _svg_text(600, 430, "RESPONSE", "micro")
    corner_style = plan.get("connector_corner_style", "rounded")
    route = _orthogonal_path([(460, 265), (650, 265), (650, 445), (740, 445)], corner_style=corner_style)
    return '<rect class="lane" x="90" y="150" width="1020" height="190"/><rect class="lane alt" x="90" y="340" width="1020" height="190"/>' + _svg_text(125, 190, "REQUESTER", "micro", "start") + _svg_text(125, 380, "REVIEWER", "micro", "start") + _card(210, 220, 250, 90, labels[0]) + _card(740, 400, 250, 90, labels[-1], css="node focal") + f'<path class="connector" data-connector-id="swimlane-handoff" data-corner-style="{corner_style}" d="{route}" marker-end="url(#arrow)"/>'


def _time(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Discover", "Build"))
    if kind == "timeline":
        return _line(140, 370, 1060, 370, arrow=True, css="axis") + "".join(f'<circle class="point {"focal" if i == 1 else ""}" cx="{x}" cy="370" r="16"/>{_line(x, 370, x, 250 if i % 2 == 0 else 490, css="leader")}{_svg_text(x, 225 if i % 2 == 0 else 535, label)}' for i, (x, label) in enumerate(zip((280, 600, 920), (labels + ["Close"])[:3])))
    return render_gantt(plan)


def _work(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Discover", "Submit"))
    if kind == "kanban":
        if is_detailed_kanban(plan):
            return render_kanban(plan)
        return "".join(f'<g><rect class="column" x="{100+i*350}" y="160" width="300" height="420" rx="20"/>{_svg_text(125+i*350, 205, title, "micro", "start")}{_card(135+i*350, 250, 230, 115, (labels+["Done"])[i], css="node warning" if i==1 else "node")}</g>' for i, title in enumerate(("READY · 1/2", "REVIEW · 1/1", "DONE · 1")))
    if kind == "story-map" and is_detailed_story_map(plan):
        return render_story_map(plan)
    if kind == "user-journey":
        items = []
        for i, label in enumerate((labels + ["Complete"])[:3]):
            x = 125 + i * 350
            items.append(_card(x, 190, 250, 105, label, css="node focal" if i == 1 else "node"))
            items.append(_line(x + 125, 315, x + 125, 520, css="sentiment"))
            items.append(f'<circle class="point" cx="{x+125}" cy="{430 + (i-1)*45}" r="16"/>')
        return _line(130, 430, 1070, 430, css="axis") + "".join(items) + _svg_text(90, 345, "+", "micro") + _svg_text(90, 540, "−", "micro")
    return '<line class="cutline" x1="90" y1="410" x2="1110" y2="410"/>' + _svg_text(105, 398, "RELEASE CUT", "micro", "start") + "".join(_card(130 + i * 340, 180, 260, 110, label, css="node focal" if i == 0 else "node") + _card(130 + i * 340, 460, 260, 90, f"Slice {i+1}") for i, label in enumerate((labels + ["Export"])[:3]))


def _hierarchy(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "tree" and is_detailed_tree(plan):
        return render_tree(plan)
    labels = _labels(plan, "nodes", ("Root", "Branch", "Leaf"))
    root, branch, leaf = (labels + ["Branch", "Leaf"])[:3]
    root_label = root if kind == "tree" else labels[-1]
    return _card(475, 130, 250, 100, root_label, css="node focal") + _line(600, 230, 600, 330) + _line(300, 330, 900, 330) + _line(300, 330, 300, 420, arrow=True) + _line(900, 330, 900, 420, arrow=True) + _card(170, 420, 260, 100, branch) + _card(770, 420, 260, 100, leaf) + _svg_text(600, 600, "PRIMARY HIERARCHY", "micro")


def _containment(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "layer-stack" and is_detailed_layers(plan):
        return render_layers(plan)
    if kind == "medallion" and is_detailed_medallion(plan):
        return render_medallion(plan)
    labels = _labels(plan, "nodes", ("Core", "Service"))
    if kind == "nested":
        return '<rect class="zone" x="130" y="130" width="940" height="500" rx="34"/>' + _svg_text(175, 180, "PLATFORM", "micro", "start") + '<rect class="zone alt" x="280" y="235" width="640" height="300" rx="28"/>' + _svg_text(320, 280, "DOMAIN", "micro", "start") + _card(445, 335, 310, 110, labels[0], css="node focal")
    if kind in {"layer-stack", "medallion"}:
        names = (labels + ["Curated", "Serving"])[:3] if kind == "medallion" else ("EDGE", "SERVICE", "DATA")
        return "".join(f'<rect class="tier {"focal" if i==1 else ""}" x="{170+i*45}" y="{180+i*135}" width="{860-i*90}" height="105" rx="18"/>{_svg_text(600, 245+i*135, label)}' for i, label in enumerate(names))
    values = (100, 64, 35)
    names = ("AWARE", "CONSIDER", "ACT")
    points = [(180, 170), (1020, 170), (850, 590), (350, 590)]
    return _poly(points, css="funnel", close=True) + _line(250, 310, 950, 310, css="tierline") + _line(300, 450, 900, 450, css="tierline") + "".join(_svg_text(600, 250 + i * 140, f"{names[i]} · {values[i]}") for i in range(3))


def _compartment(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "er-data-model" and is_detailed_er_data_model(plan):
        return render_er_data_model(plan)
    if kind == "uml-class" and is_detailed_uml_class(plan):
        return render_uml_class(plan)
    labels = _labels(plan, "nodes", ("Customer", "Order"))
    member_labels = {"er-data-model": ("id · PK", "name · text"), "uml-class": ("− id: UUID", "+ submit(): void"), "database-schema": ("id · uuid · PK", "customer_id · uuid · FK")}[kind]
    left = _card(120, 190, 350, 330, labels[0], css="node compartment", radius=10)
    right = _card(730, 190, 350, 330, labels[-1], css="node compartment", radius=10)
    dividers = _line(120, 275, 470, 275, css="divider") + _line(730, 275, 1080, 275, css="divider")
    members = _svg_text(150, 335, member_labels[0], "body", "start") + _svg_text(150, 385, member_labels[1], "body", "start") + _svg_text(760, 335, member_labels[0], "body", "start") + _svg_text(760, 385, member_labels[1], "body", "start")
    relation = _line(470, 355, 730, 355) + _svg_text(600, 335, "1  ·  N", "micro")
    return left + right + dividers + members + relation + _svg_text(600, 590, kind.replace("-", " ").upper(), "micro")


def _spatial(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    if kind == "wardley-map" and is_detailed_wardley_map(plan):
        return render_wardley_map(plan)
    if kind == "venn":
        if is_detailed_venn(plan):
            return render_venn(plan)
        return '<circle class="set series-one" cx="475" cy="365" r="215"/><circle class="set series-two" cx="725" cy="365" r="215"/>' + _svg_text(350, 370, "SET A") + _svg_text(850, 370, "SET B") + _svg_text(600, 370, "SHARED", "label focal-text")
    if kind == "dp-security-matrix":
        if is_detailed_dp_security_matrix(plan):
            return render_dp_security_matrix(plan)
        cells = []
        states = ("allow", "conditional", "allow", "deny")
        for i, state in enumerate(states):
            x = 400 + (i % 2) * 260; y = 240 + (i // 2) * 150
            cells.append(f'<rect class="matrix-cell {state}" x="{x}" y="{y}" width="240" height="130" rx="12"/>{_svg_text(x+120,y+72,state.upper(),"micro")}' )
        return _svg_text(250, 310, "READER", "micro") + _svg_text(250, 460, "ADMIN", "micro") + _svg_text(520, 195, "STORE", "micro") + _svg_text(780, 195, "API", "micro") + "".join(cells)
    axis = _line(170, 570, 1060, 570, arrow=True, css="axis") + _line(170, 570, 170, 135, arrow=True, css="axis")
    if kind == "quadrant":
        return axis + _line(615, 135, 615, 570, css="gridline") + _line(170, 350, 1060, 350, css="gridline") + '<circle class="point focal" cx="850" cy="230" r="18"/><circle class="point" cx="370" cy="460" r="18"/>' + _svg_text(1030, 610, "IMPACT", "micro") + _svg_text(130, 150, "LIKELIHOOD", "micro", "end")
    return axis + _line(170, 245, 1060, 245, css="gridline") + _line(170, 405, 1060, 405, css="gridline") + '<circle class="point focal" cx="360" cy="215" r="22"/><circle class="point" cx="750" cy="390" r="22"/>' + _line(360, 215, 750, 390) + _svg_text(350, 175, "NEED", "micro") + _svg_text(760, 435, "SERVICE", "micro") + _svg_text(1040, 610, "EVOLUTION", "micro")


def _quantitative(plan: Mapping[str, Any]) -> str:
    adapter_id = plan["adapter"]["adapter_id"]
    kind = plan["adapter"]["canonical_type"]
    axis = _line(150, 590, 1060, 590, arrow=True, css="axis") + _line(150, 590, 150, 140, arrow=True, css="axis")
    if adapter_id == "capability:CAP-V17":
        return axis + _line(300, 300, 790, 300, css="series-line") + _line(420, 460, 900, 460, css="series-line") + '<circle class="point series-one-fill" cx="300" cy="300" r="18"/><circle class="point series-two-fill" cx="790" cy="300" r="18"/><circle class="point series-one-fill" cx="420" cy="460" r="18"/><circle class="point series-two-fill" cx="900" cy="460" r="18"/>' + _svg_text(260, 306, "A", "micro", "end") + _svg_text(380, 466, "B", "micro", "end")
    if adapter_id == "capability:CAP-V18":
        return axis + _line(330, 455, 870, 235, css="series-line") + _line(330, 260, 870, 390, css="series-line second") + _svg_text(330, 630, "BEFORE", "micro") + _svg_text(870, 630, "AFTER", "micro") + _svg_text(300, 455, "Alpha 2", "micro", "end") + _svg_text(900, 235, "8 Alpha", "micro", "start") + _svg_text(300, 260, "Beta 7", "micro", "end") + _svg_text(900, 390, "4 Beta", "micro", "start")
    if adapter_id == "capability:CAP-V19":
        ridges=[]
        for i, y in enumerate((300, 470)):
            pts=[(220+x*95, y-math.sin(x/5*math.pi)*95) for x in range(6)]
            ridges.append(_poly(pts, css="ridge")+_svg_text(190,y+5,("NORTH","SOUTH")[i],"micro","end"))
        return axis+"".join(ridges)
    if adapter_id == "capability:CAP-V20":
        return axis + '<circle class="bubble series-one" cx="420" cy="350" r="10"/><circle class="bubble series-two" cx="810" cy="420" r="74"/>' + _svg_text(420, 320, "0", "micro") + _svg_text(810, 425, "25", "label") + _svg_text(1045, 630, "X", "micro") + _svg_text(120, 155, "Y", "micro")
    if kind == "bar-chart":
        if is_detailed_bar_chart(plan):
            return render_bar_chart(plan)
        return axis + '<rect class="bar" x="300" y="360" width="180" height="230"/><rect class="bar focal" x="650" y="245" width="180" height="345"/>' + _svg_text(390, 630, "JAN · 12", "micro") + _svg_text(740, 630, "FEB · 18", "micro")
    if kind == "line-chart":
        if is_detailed_line_chart(plan):
            return render_line_chart(plan)
        return axis + _poly([(230,470),(470,395),(710,300),(950,220)],css="series-line") + ''.join(f'<circle class="point focal" cx="{x}" cy="{y}" r="12"/>' for x,y in [(230,470),(470,395),(710,300),(950,220)])
    if kind == "scatter-plot":
        if is_detailed_scatter_chart(plan):
            return render_scatter_chart(plan)
        return axis + ''.join(f'<circle class="point {"focal" if i==2 else ""}" cx="{x}" cy="{y}" r="16"/>' for i,(x,y) in enumerate([(300,450),(520,300),(790,210),(900,430)])) + _svg_text(810, 190, "OUTLIER", "micro")
    if kind == "radar":
        if is_detailed_radar(plan):
            return render_radar(plan)
        center=(600,370); radii=(85,170,255); parts=[]
        for r in radii:
            parts.append(_poly([(center[0]+math.cos(-math.pi/2+i*2*math.pi/5)*r,center[1]+math.sin(-math.pi/2+i*2*math.pi/5)*r) for i in range(5)],css="gridshape",close=True))
        values=(.8,.55,.9,.68,.45)
        parts.append(_poly([(center[0]+math.cos(-math.pi/2+i*2*math.pi/5)*255*values[i],center[1]+math.sin(-math.pi/2+i*2*math.pi/5)*255*values[i]) for i in range(5)],css="radarshape",close=True))
        return ''.join(parts)
    if kind == "polar-chart":
        if is_detailed_polar_chart(plan):
            return render_polar_chart(plan)
        center=(600,380); parts=[]
        for i,r in enumerate((210,130,55,175)):
            a1=-90+i*90; a2=a1+72
            x1=center[0]+math.cos(math.radians(a1))*r; y1=center[1]+math.sin(math.radians(a1))*r
            x2=center[0]+math.cos(math.radians(a2))*r; y2=center[1]+math.sin(math.radians(a2))*r
            parts.append(f'<path class="polar {"focal" if i==0 else ""}" d="M600 380 L{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f} Z"/>')
        return ''.join(parts)
    if kind == "treemap" and is_detailed_treemap(plan):
        return render_treemap(plan)
    return '<rect class="zone" x="120" y="150" width="960" height="450" rx="18"/><rect class="tile focal" x="140" y="180" width="560" height="390"/><rect class="tile" x="720" y="180" width="340" height="185"/><rect class="tile alt" x="720" y="385" width="340" height="185"/>' + _svg_text(420, 390, "A · 60") + _svg_text(890, 280, "B · 25") + _svg_text(890, 485, "C · 15")


def _special(plan: Mapping[str, Any]) -> str:
    kind = plan["adapter"]["canonical_type"]
    labels = _labels(plan, "nodes", ("Learn", "Build", "Measure"))
    if kind == "loop-flywheel":
        return render_flywheel(plan)
    if kind == "fishbone":
        return render_fishbone(plan)
    # Sankey: bar heights and ribbon widths share one disclosed linear scale.
    return '<rect class="flowbar" x="120" y="245" width="48" height="250"/><rect class="flowbar focal" x="575" y="245" width="48" height="250"/><rect class="flowbar" x="1030" y="245" width="48" height="250"/>' + '<path class="ribbon series-one" d="M168 245 C330 245 413 245 575 245 L575 495 C413 495 330 495 168 495 Z"/><path class="ribbon series-two" d="M623 245 C785 245 868 245 1030 245 L1030 495 C868 495 785 495 623 495 Z"/>' + _svg_text(144, 220, labels[0]) + _svg_text(599, 220, labels[1]) + _svg_text(1054, 220, labels[-1]) + _svg_text(372, 380, "25", "label") + _svg_text(826, 380, "25", "label")


ENGINE_RENDERERS: dict[str, Callable[[Mapping[str, Any]], str]] = {
    "topology-and-zones": _topology,
    "integration-pipeline": _pipeline,
    "runtime-deployment": _deployment,
    "dependency-dag": _dependency,
    "directed-flow-state": _directed,
    "lane-interaction": _lane,
    "time-planning": _time,
    "work-experience": _work,
    "hierarchy": _hierarchy,
    "containment-stack": _containment,
    "compartment-model": _compartment,
    "spatial-matrix": _spatial,
    "quantitative": _quantitative,
    "special-geometry": _special,
}


def _data_rows(plan: Mapping[str, Any]) -> str:
    inventory = plan["material_inventory"]["by_collection"]
    rows = []
    for collection in ("nodes", "edges", "groups", "lanes", "series", "axes", "annotations"):
        ids = inventory.get(collection, [])
        if ids:
            rows.append(f"<tr><th scope=\"row\">{_text(collection)}</th><td>{_text(', '.join(ids))}</td><td>{len(ids)}</td></tr>")
    if not rows:
        rows.append('<tr><th scope="row">material</th><td>Validated semantic projection</td><td>1</td></tr>')
    return "".join(rows)


def _css(tokens: Mapping[str, str], mode: str) -> str:
    editorial = "Georgia, 'Times New Roman', serif" if mode == "editorial" else "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    return f"""
    :root{{--canvas:{tokens['canvas']};--surface:{tokens['surface']};--surface-alt:{tokens['surface_alt']};--text:{tokens['text']};--muted:{tokens['muted']};--border:{tokens['border']};--accent:{tokens['accent']};--on-accent:{tokens['on_accent']};--connector:{tokens['connector']};--series-1:{tokens['series_1']};--series-2:{tokens['series_2']};--grid:{tokens['grid']};--success:{tokens['success']};--danger:{tokens['danger']}}}
    *{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:var(--canvas);color:var(--text)}}body{{font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif;padding:24px}}main{{width:min(100%,1320px);margin:auto}}header{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;margin:4px 0 22px}}.eyebrow{{margin:0 0 8px;font:700 13px ui-monospace,monospace;letter-spacing:.14em;color:var(--accent)}}h1{{margin:0;font-family:{editorial};font-size:clamp(30px,5vw,54px);line-height:1.03;font-weight:{'500' if mode=='editorial' else '750'}}}.takeaway{{max-width:760px;margin:10px 0 0;color:var(--muted);font-size:16px;line-height:1.55}}.badge{{align-self:start;border:1px solid var(--border);border-radius:999px;padding:9px 13px;font:700 12px ui-monospace,monospace;color:var(--muted)}}.artifact-frame{{border:1px solid var(--border);border-radius:{'2px' if mode=='editorial' else '22px'};background:var(--surface);overflow:hidden;box-shadow:0 18px 55px color-mix(in srgb,var(--text) 10%,transparent)}}svg{{display:block;width:100%;height:auto;background:var(--surface)}}.label{{font:650 18px ui-sans-serif,system-ui,sans-serif;fill:var(--text)}}.label.focal-text{{fill:var(--accent)}}.body{{font:500 16px ui-sans-serif,system-ui,sans-serif;fill:var(--text)}}.micro{{font:750 12px ui-monospace,monospace;letter-spacing:.08em;fill:var(--muted)}}.node,.zone,.lane,.column,.tier,.tile,.matrix-cell{{fill:var(--surface);stroke:var(--border);stroke-width:2}}.zone{{fill:var(--surface-alt)}}.zone.alt,.lane.alt,.tile.alt{{fill:var(--canvas)}}.zone.dashed{{stroke-dasharray:8 7}}.node.focal,.tier.focal,.tile.focal{{fill:color-mix(in srgb,var(--accent) 14%,var(--surface));stroke:var(--accent);stroke-width:3}}.node.warning{{fill:color-mix(in srgb,var(--danger) 11%,var(--surface));stroke:var(--danger)}}.connector,.axis,.leader,.lifeline,.divider,.gridline,.tierline,.bone,.spine{{fill:none;stroke:var(--connector);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}.axis{{stroke-width:2}}.gridline,.divider,.tierline{{stroke:var(--grid);stroke-width:2}}.leader,.lifeline{{stroke-dasharray:7 7}}.bridge{{fill:none;stroke:var(--surface);stroke-width:8}}.backedge{{stroke-dasharray:10 8}}.status,.point,.terminal,.bubble{{fill:var(--surface);stroke:var(--connector);stroke-width:3}}.point.focal{{fill:var(--accent);stroke:var(--on-accent)}}.success-fill{{fill:var(--success);stroke:none}}.danger-fill{{fill:var(--danger);stroke:none}}.ink-fill{{fill:var(--text)}}.terminal{{fill:none}}.accent-band{{fill:color-mix(in srgb,var(--accent) 18%,var(--surface))}}.bar,.flowbar{{fill:var(--series-1)}}.bar.focal,.flowbar.focal{{fill:var(--series-2)}}.cutline{{stroke:var(--danger);stroke-width:3;stroke-dasharray:12 8}}.sentiment{{stroke:var(--grid);stroke-width:8}}.compartment{{fill:var(--surface)}}.set{{fill:color-mix(in srgb,var(--series-1) 26%,transparent);stroke:var(--series-1);stroke-width:3}}.set.series-two{{fill:color-mix(in srgb,var(--series-2) 26%,transparent);stroke:var(--series-2)}}.allow{{fill:color-mix(in srgb,var(--success) 22%,var(--surface));stroke:var(--success)}}.conditional{{fill:color-mix(in srgb,var(--accent) 20%,var(--surface));stroke:var(--accent)}}.deny{{fill:color-mix(in srgb,var(--danger) 18%,var(--surface));stroke:var(--danger)}}.series-line,.ridge,.gridshape,.radarshape{{fill:none;stroke:var(--series-1);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.series-line.second{{stroke:var(--series-2)}}.series-one-fill{{fill:var(--series-1)}}.series-two-fill{{fill:var(--series-2)}}.ridge{{stroke-width:7}}.gridshape{{stroke:var(--grid);stroke-width:2}}.radarshape{{fill:color-mix(in srgb,var(--series-1) 20%,transparent)}}.polar{{fill:color-mix(in srgb,var(--series-1) 25%,var(--surface));stroke:var(--series-1);stroke-width:3}}.polar.focal{{fill:color-mix(in srgb,var(--series-2) 42%,var(--surface));stroke:var(--series-2)}}.bubble.series-one{{fill:var(--series-1)}}.bubble.series-two{{fill:color-mix(in srgb,var(--series-2) 52%,var(--surface));stroke:var(--series-2)}}.funnel{{fill:color-mix(in srgb,var(--accent) 13%,var(--surface));stroke:var(--accent);stroke-width:3}}.ribbon{{stroke:none;opacity:.58}}.ribbon.series-one{{fill:var(--series-1)}}.ribbon.series-two{{fill:var(--series-2)}}.document{{fill:var(--surface-alt);stroke:var(--accent);stroke-width:3}}.facts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;margin-top:14px;border:1px solid var(--border);background:var(--border)}}.fact{{padding:14px;background:var(--surface)}}.fact span{{display:block;color:var(--muted);font:700 11px ui-monospace,monospace;letter-spacing:.08em}}.fact strong{{display:block;margin-top:5px;font-size:14px;overflow-wrap:anywhere}}details{{margin-top:14px;border:1px solid var(--border);border-radius:14px;background:var(--surface)}}summary{{cursor:pointer;padding:14px 16px;font-weight:750}}summary:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:10px 16px;border-top:1px solid var(--border);text-align:left;vertical-align:top}}th{{width:18%;color:var(--muted)}}td:last-child{{width:8%;font-variant-numeric:tabular-nums}}@media(max-width:720px){{body{{padding:12px}}header{{grid-template-columns:1fr}}.facts{{grid-template-columns:1fr}}.artifact-frame{{overflow:auto}}svg{{min-width:760px}}}}@media print{{body{{padding:0}}.artifact-frame{{box-shadow:none}}details{{display:block}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;animation:none!important;transition:none!important}}}}
    """


def _p18_css(tokens: Mapping[str, str]) -> str:
    """Return the P-18 review-17 inherited shell and SVG visual grammar."""

    return f"""
    :root{{--paper:{tokens['paper']};--canvas:{tokens['canvas']};--surface:{tokens['surface']};--surface-alt:{tokens['surface_alt']};--text:{tokens['text']};--muted:{tokens['muted']};--border:{tokens['border']};--accent:{tokens['accent']};--accent-soft:{tokens['accent_soft']};--accent-text:{tokens['accent_text']};--on-accent:{tokens['on_accent']};--connector:{tokens['connector']};--series-1:{tokens['blue']};--series-2:{tokens['accent']};--series-3:{tokens['green']};--series-4:{tokens['amber']};--grid:{tokens['grid']};--success:{tokens['green']};--danger:{tokens['danger']}}}
    *{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:var(--paper);color:var(--text)}}body{{font-family:'Avenir Next',Avenir,'Segoe UI',sans-serif;padding:48px 24px 80px}}main{{width:min(100%,1320px);margin:auto}}header{{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;margin-bottom:24px}}.eyebrow{{margin:0 0 8px;font:700 13px Menlo,Monaco,monospace;letter-spacing:.16em;color:var(--accent)}}h1{{margin:0;font:400 clamp(38px,5vw,52px)/1.06 Georgia,'Times New Roman',serif}}.takeaway{{max-width:760px;margin:10px 0 0;color:var(--muted);font-size:16px;line-height:1.55}}.receipts{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;max-width:440px}}.receipts span{{padding:7px 10px;border:1px solid var(--border);border-radius:7px;background:color-mix(in srgb,var(--surface) 68%,transparent);font:12px Menlo,Monaco,monospace;color:var(--muted)}}.artifact-frame{{margin:0;overflow:hidden;border:1px solid var(--border);border-radius:18px;background:var(--canvas);box-shadow:0 20px 60px color-mix(in srgb,var(--text) 10%,transparent)}}svg{{display:block;width:100%;height:auto;background:var(--canvas)}}.label{{font:650 18px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}}.label.focal-text{{fill:var(--accent-text)}}.body{{font:500 16px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}}.micro{{font:700 12px Menlo,Monaco,monospace;letter-spacing:.1em;fill:var(--muted)}}.node,.zone,.lane,.column,.tier,.tile,.matrix-cell{{fill:var(--surface);stroke:var(--connector);stroke-width:2.2}}.zone,.column{{fill:var(--surface-alt);stroke:var(--border);stroke-width:1.6}}.zone.alt,.lane.alt,.tile.alt{{fill:var(--canvas)}}.zone.dashed{{stroke-dasharray:8 7}}.node.focal,.tier.focal,.tile.focal{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.8}}.node.warning{{fill:color-mix(in srgb,var(--danger) 11%,var(--surface));stroke:var(--danger)}}.connector,.axis,.leader,.lifeline,.divider,.gridline,.tierline,.bone,.spine{{fill:none;stroke:var(--connector);stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}.axis{{stroke-width:2.2}}.gridline,.divider,.tierline{{stroke:var(--grid);stroke-width:1.4}}.leader,.lifeline{{stroke-dasharray:9 9}}.bridge{{fill:none;stroke:var(--canvas);stroke-width:11;stroke-linecap:round}}.backedge{{stroke-dasharray:10 8}}.status,.point,.terminal,.bubble{{fill:var(--surface);stroke:var(--connector);stroke-width:3}}.point.focal{{fill:var(--accent);stroke:var(--on-accent)}}.success-fill{{fill:var(--success);stroke:none}}.danger-fill{{fill:var(--danger);stroke:none}}.ink-fill{{fill:var(--text)}}.terminal{{fill:none}}.accent-band{{fill:var(--accent-soft)}}.bar,.flowbar{{fill:var(--series-1)}}.bar.focal,.flowbar.focal{{fill:var(--series-2)}}.cutline{{stroke:var(--danger);stroke-width:3;stroke-dasharray:12 8}}.sentiment{{stroke:var(--grid);stroke-width:8}}.compartment{{fill:var(--surface)}}.set{{fill:color-mix(in srgb,var(--series-1) 24%,transparent);stroke:var(--series-1);stroke-width:3}}.set.series-two{{fill:color-mix(in srgb,var(--series-2) 24%,transparent);stroke:var(--series-2)}}.allow{{fill:color-mix(in srgb,var(--success) 22%,var(--surface));stroke:var(--success)}}.conditional{{fill:var(--accent-soft);stroke:var(--accent)}}.deny{{fill:color-mix(in srgb,var(--danger) 18%,var(--surface));stroke:var(--danger)}}.series-line,.ridge,.gridshape,.radarshape{{fill:none;stroke:var(--series-1);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}.series-line.second{{stroke:var(--series-2)}}.series-one-fill{{fill:var(--series-1)}}.series-two-fill{{fill:var(--series-2)}}.ridge{{stroke-width:7}}.gridshape{{stroke:var(--grid);stroke-width:2}}.radarshape{{fill:color-mix(in srgb,var(--series-1) 18%,transparent)}}.polar{{fill:color-mix(in srgb,var(--series-1) 24%,var(--surface));stroke:var(--series-1);stroke-width:3}}.polar.focal{{fill:var(--accent-soft);stroke:var(--accent)}}.bubble.series-one{{fill:var(--series-1)}}.bubble.series-two{{fill:color-mix(in srgb,var(--series-2) 48%,var(--surface));stroke:var(--series-2)}}.funnel{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.3}}.ribbon{{stroke:none;opacity:.46}}.ribbon.series-one{{fill:var(--grid)}}.ribbon.series-two{{fill:var(--accent)}}.document{{fill:var(--surface-alt);stroke:var(--accent);stroke-width:2.8}}.visual-signature .legend-rule{{stroke:var(--grid);stroke-width:1.5}}.visual-signature .legend-swatch{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2}}.facts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;margin-top:24px;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--border)}}.fact{{padding:15px 16px;background:color-mix(in srgb,var(--surface) 72%,transparent)}}.fact span{{display:block;color:var(--muted);font:700 11px Menlo,Monaco,monospace;letter-spacing:.1em}}.fact strong{{display:block;margin-top:5px;font-size:14px;overflow-wrap:anywhere}}details{{margin-top:14px;border:1px solid var(--border);border-radius:14px;background:color-mix(in srgb,var(--surface) 72%,transparent)}}summary{{cursor:pointer;padding:14px 16px;font-weight:650}}summary:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:10px 16px;border-top:1px solid var(--border);text-align:left;vertical-align:top}}th{{width:18%;color:var(--muted)}}td:last-child{{width:8%;font-variant-numeric:tabular-nums}}@media(max-width:820px){{body{{padding:24px 12px 48px}}header{{grid-template-columns:1fr}}.receipts{{justify-content:flex-start;max-width:none}}h1{{font-size:40px}}.facts{{grid-template-columns:1fr}}.artifact-frame{{overflow:auto}}svg{{min-width:760px}}}}@media print{{body{{padding:0;background:#fff}}header,.facts,details{{display:none}}.artifact-frame{{border:0;box-shadow:none}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto!important;animation:none!important;transition:none!important}}}}
    """


def render_gallery_html(ir_value: Mapping[str, Any], mode: str, fixture_id: str, *, connector_corner_style: str | None = None) -> str:
    """Render one deterministic self-contained P-19B specimen HTML."""

    if mode not in MODES:
        raise GalleryRenderError("mode-invalid", f"Unsupported mode: {mode!r}")
    if not fixture_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in fixture_id):
        raise GalleryRenderError("fixture-id-invalid", "Fixture id must be a safe non-empty token.")
    plan = adapt_visual(ir_value)
    adapter = plan["adapter"]
    if connector_corner_style is not None:
        if adapter["canonical_type"] not in ("swimlane", "high-level", "it-current-state") or connector_corner_style not in ("rounded", "straight"):
            raise GalleryRenderError("corner-style-invalid", "This focused corner override is supported for swimlane, high-level and it-current-state only.")
        plan["connector_corner_style"] = connector_corner_style
    engine = adapter["layout_engine"]
    if engine not in ENGINE_RENDERERS:
        raise GalleryRenderError("engine-unbound", f"No renderer is bound for {engine!r}")
    tokens = P18_VISUAL_MODES[mode]
    is_layers_variant = fixture_id == "type-layers" and adapter["canonical_type"] == "layer-stack" and is_detailed_layers(plan)
    is_scatter_variant = fixture_id == "type-scatter-chart" and adapter["canonical_type"] == "scatter-plot" and is_detailed_scatter_chart(plan)
    identity = "layers" if is_layers_variant else "scatter-chart" if is_scatter_variant else adapter["capability_id"] or adapter["canonical_type"]
    parent = "layer-stack" if is_layers_variant else "scatter-plot" if is_scatter_variant else adapter["canonical_type"] if adapter["capability_id"] else "none"
    silhouette = "five-band-abstraction-stack" if is_layers_variant else "quantitative-performance-scatter-with-trend" if is_scatter_variant else adapter["silhouette"]
    title = str(ir_value["diagram"]["title"])
    description = str(plan["accessibility_contract"]["description"])
    detailed_types = ("gantt", "loop-flywheel", "dp-integration", "sequence", "bar-chart", "line-chart", "scatter-plot", "radar", "polar-chart", "treemap", "wardley-map", "venn", "dp-security-matrix", "er-data-model", "uml-class", "high-level", "it-current-state", "kanban", "story-map", "state-machine", "layer-stack", "medallion", "tree")
    detailed_ready = (
        (adapter["canonical_type"] != "dp-integration" or is_detailed_dp_integration(plan))
        and (adapter["canonical_type"] != "sequence" or is_detailed_sequence(plan))
        and (adapter["canonical_type"] != "bar-chart" or is_detailed_bar_chart(plan))
        and (adapter["canonical_type"] != "line-chart" or is_detailed_line_chart(plan))
        and (adapter["canonical_type"] != "scatter-plot" or is_detailed_scatter_chart(plan))
        and (adapter["canonical_type"] != "radar" or is_detailed_radar(plan))
        and (adapter["canonical_type"] != "polar-chart" or is_detailed_polar_chart(plan))
        and (adapter["canonical_type"] != "treemap" or is_detailed_treemap(plan))
        and (adapter["canonical_type"] != "wardley-map" or is_detailed_wardley_map(plan))
        and (adapter["canonical_type"] != "venn" or is_detailed_venn(plan))
        and (adapter["canonical_type"] != "dp-security-matrix" or is_detailed_dp_security_matrix(plan))
        and (adapter["canonical_type"] != "er-data-model" or is_detailed_er_data_model(plan))
        and (adapter["canonical_type"] != "uml-class" or is_detailed_uml_class(plan))
        and (adapter["canonical_type"] != "high-level" or is_detailed_high_level(plan))
        and (adapter["canonical_type"] != "it-current-state" or is_detailed_it_current_state(plan))
        and (adapter["canonical_type"] != "kanban" or is_detailed_kanban(plan))
        and (adapter["canonical_type"] != "story-map" or is_detailed_story_map(plan))
        and (adapter["canonical_type"] != "state-machine" or is_detailed_state_machine(plan))
        and (adapter["canonical_type"] != "layer-stack" or is_detailed_layers(plan))
        and (adapter["canonical_type"] != "medallion" or is_detailed_medallion(plan))
        and (adapter["canonical_type"] != "tree" or is_detailed_tree(plan))
    )
    takeaway = _text(description) if adapter["canonical_type"] in detailed_types and detailed_ready else f"{_text(adapter['semantic_focus'].capitalize())}. {_text(adapter['accessible_alternative'].capitalize())}."
    svg_id = f"diagram-{fixture_id}-{mode}"
    artwork = ENGINE_RENDERERS[engine](plan)
    validate_target_geometry(f"<svg>{artwork}</svg>", adapter["canonical_type"])
    signature = '<g class="visual-signature" aria-hidden="true"><line class="legend-rule" x1="52" y1="690" x2="1148" y2="690"/><rect class="legend-swatch" x="56" y="710" width="24" height="20" rx="5"/><text class="micro" x="92" y="725">FOCAL SIGNAL</text><line class="connector" x1="256" y1="720" x2="300" y2="720"/><text class="micro" x="316" y="725">RELATION / FLOW</text><text class="micro" x="1144" y="725" text-anchor="end">P18 REVIEW‑17 VISUAL LINEAGE</text></g>'
    canvas_width, canvas_height = (layout_gantt(plan)[key] for key in ("width", "height")) if adapter["canonical_type"] == "gantt" else (1200, 760)
    if adapter["canonical_type"] == "gantt":
        signature = ""  # Gantt owns its task/gate/phase legend.
    if adapter["canonical_type"] == "loop-flywheel":
        flywheel = layout_flywheel(plan)
        canvas_width, canvas_height = flywheel['width'], flywheel['height']
        signature = ""  # Ring and inward spokes carry the visual hierarchy.
    if adapter["canonical_type"] == "fishbone":
        fishbone = layout_fishbone(plan)
        canvas_width, canvas_height = fishbone['width'], fishbone['height']
        signature = ""  # Fishbone owns its category/cause/effect legend.
    if adapter["canonical_type"] == "dp-integration" and is_detailed_dp_integration(plan):
        dp_layout = layout_dp_integration(plan)
        canvas_width, canvas_height = dp_layout['width'], dp_layout['height']
        signature = ""  # Detailed integration topology owns its type-key legend.
    if adapter["canonical_type"] == "bar-chart" and is_detailed_bar_chart(plan):
        bar_layout = layout_bar_chart(plan)
        canvas_width, canvas_height = bar_layout["width"], bar_layout["height"]
        signature = ""  # Detailed bar chart owns its axes, direct labels and legend.
    if adapter["canonical_type"] == "line-chart" and is_detailed_line_chart(plan):
        line_layout = layout_line_chart(plan)
        canvas_width, canvas_height = line_layout["width"], line_layout["height"]
        signature = ""  # Detailed line chart owns its axes, exact values and legend.
    if adapter["canonical_type"] == "scatter-plot" and is_detailed_scatter_chart(plan):
        scatter_layout = layout_scatter_chart(plan)
        canvas_width, canvas_height = scatter_layout["width"], scatter_layout["height"]
        signature = ""  # Detailed scatter chart owns its axes, points, trend and legend.
    if adapter["canonical_type"] == "radar" and is_detailed_radar(plan):
        radar_layout = layout_radar(plan)
        canvas_width, canvas_height = radar_layout["width"], radar_layout["height"]
        signature = ""  # Detailed radar owns its shared scale, profiles and legend.
    if adapter["canonical_type"] == "polar-chart" and is_detailed_polar_chart(plan):
        polar_layout = layout_polar_chart(plan)
        canvas_width, canvas_height = polar_layout["width"], polar_layout["height"]
        signature = ""  # Detailed polar chart owns its rings, direct labels and peak note.
    if adapter["canonical_type"] == "treemap" and is_detailed_treemap(plan):
        treemap_layout = layout_treemap(plan)
        canvas_width, canvas_height = treemap_layout["width"], treemap_layout["height"]
        signature = ""  # Detailed Treemap owns its area legend and small-tile disclosure.
    if adapter["canonical_type"] == "wardley-map" and is_detailed_wardley_map(plan):
        wardley_layout = layout_wardley_map(plan)
        canvas_width, canvas_height = wardley_layout["width"], wardley_layout["height"]
        signature = ""  # Detailed Wardley map owns its axes, dependencies and evolution signal.
    if adapter["canonical_type"] == "venn" and is_detailed_venn(plan):
        venn_layout = layout_venn(plan)
        canvas_width, canvas_height = venn_layout["width"], venn_layout["height"]
        signature = ""  # Detailed Venn owns its exact set geometry and triple-intersection label.
    if adapter["canonical_type"] == "dp-security-matrix" and is_detailed_dp_security_matrix(plan):
        matrix_layout = layout_dp_security_matrix(plan)
        canvas_width, canvas_height = matrix_layout["width"], matrix_layout["height"]
        signature = ""  # Detailed permission matrix owns its headers and legend.
    if adapter["canonical_type"] == "er-data-model" and is_detailed_er_data_model(plan):
        er_layout = layout_er_data_model(plan)
        canvas_width, canvas_height = er_layout["width"], er_layout["height"]
        signature = ""  # Detailed ER model owns its entity/key/cardinality legend.
    if adapter["canonical_type"] == "uml-class" and is_detailed_uml_class(plan):
        uml_layout = layout_uml_class(plan)
        canvas_width, canvas_height = uml_layout["width"], uml_layout["height"]
        signature = ""  # Detailed UML model owns its typed relationship legend.
    if adapter["canonical_type"] == "high-level" and is_detailed_high_level(plan):
        high_level_layout = layout_high_level(plan, plan.get("connector_corner_style", "rounded"))
        canvas_width, canvas_height = high_level_layout["width"], high_level_layout["height"]
        signature = ""  # Detailed overview owns its phase ribbon and route-policy legend.
    if adapter["canonical_type"] == "it-current-state" and is_detailed_it_current_state(plan):
        current_state_layout = layout_it_current_state(plan, plan.get("connector_corner_style", "rounded"))
        canvas_width, canvas_height = current_state_layout["width"], current_state_layout["height"]
        signature = ""  # Detailed current state owns its boundary and pain-point legend.
    if adapter["canonical_type"] == "kanban" and is_detailed_kanban(plan):
        kanban_layout = layout_kanban(plan)
        canvas_width, canvas_height = kanban_layout["width"], kanban_layout["height"]
        signature = ""  # Detailed Kanban owns its column, WIP and work-state legend.
    if adapter["canonical_type"] == "story-map" and is_detailed_story_map(plan):
        story_map_layout = layout_story_map(plan)
        canvas_width, canvas_height = story_map_layout["width"], story_map_layout["height"]
        signature = ""  # Detailed story map owns its activities, release slices and cutline legend.
    if adapter["canonical_type"] == "state-machine" and is_detailed_state_machine(plan):
        state_layout = layout_state_machine(plan)
        canvas_width, canvas_height = state_layout["width"], state_layout["height"]
        signature = ""  # Detailed state machine owns its endpoints, transitions and return-route legend.
    if adapter["canonical_type"] == "sequence" and is_detailed_sequence(plan):
        sequence_layout = layout_sequence(plan)
        canvas_width, canvas_height = sequence_layout["width"], sequence_layout["height"]
        signature = ""  # Detailed sequence owns its participant, activation, message and response legend.
    if is_layers_variant:
        layers_layout = layout_layers(plan)
        canvas_width, canvas_height = layers_layout["width"], layers_layout["height"]
        signature = ""  # Layers owns its abstraction axis and focal-layer note.
    if adapter["canonical_type"] == "medallion" and is_detailed_medallion(plan):
        medallion_layout = layout_medallion(plan)
        canvas_width, canvas_height = medallion_layout["width"], medallion_layout["height"]
        signature = ""  # Detailed medallion owns its lifecycle states and processing paths.
    if adapter["canonical_type"] == "tree" and is_detailed_tree(plan):
        tree_layout = layout_tree(plan)
        canvas_width, canvas_height = tree_layout["width"], tree_layout["height"]
        signature = ""  # Detailed tree owns its tier labels and centered-span legend.
    svg = f'''<svg id="{svg_id}" role="img" aria-labelledby="{svg_id}-title {svg_id}-desc" viewBox="0 0 {canvas_width} {canvas_height}" data-layout-engine="{_text(engine)}" data-silhouette="{_text(silhouette)}" data-geometry-contract="content-fit-no-global-transform" data-connector-policy="{CONNECTOR_POLICY_ID}" data-route-priority="{ROUTE_PRIORITY}" data-visual-parent-candidate="{P18_PARENT_CANDIDATE_ID}" data-visual-parent-manifest-sha256="{P18_PARENT_MANIFEST_SHA256}" data-visual-grammar="p18r6-review17"><title id="{svg_id}-title">{_text(title)}</title><desc id="{svg_id}-desc">{_text(description)} {_text(adapter['semantic_focus'])}.</desc><defs><pattern id="dot-field" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="var(--grid)" opacity=".34"/></pattern><marker id="arrow" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--connector)"/></marker></defs><rect width="{canvas_width}" height="{canvas_height}" fill="var(--canvas)"/><rect width="{canvas_width}" height="{canvas_height}" fill="url(#dot-field)"/>{artwork}{signature}</svg>'''
    metadata = {
        "candidate_id": P19B_CANDIDATE_ID,
        "schema_version": P19B_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "identity": identity,
        "canonical_type": adapter["canonical_type"],
        "capability_id": adapter["capability_id"],
        "parent": parent,
        "mode": mode,
        "layout_engine": engine,
        "silhouette": silhouette,
        "source_ir_sha256": plan["source_ir_sha256"],
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "visual_inheritance_contract": "D-080/p18r6-review17-semantic-role-derivation",
        "connector_policy": CONNECTOR_POLICY_ID,
        "route_priority": ROUTE_PRIORITY,
        "automated_check_disposition": "p19b-static-and-browser-planned",
    }
    if is_layers_variant:
        metadata["presentation_variant_id"] = "layers"
    if is_scatter_variant:
        metadata["presentation_variant_id"] = "scatter-chart"
    style = (gantt_css(tokens) if adapter["canonical_type"] == "gantt" else "") + _p18_css(tokens)
    if adapter["canonical_type"] == "loop-flywheel":
        style = flywheel_css(tokens) + style
    if adapter["canonical_type"] == "fishbone":
        style = fishbone_css(tokens) + style
    if adapter["canonical_type"] == "dp-integration" and is_detailed_dp_integration(plan):
        style = dp_integration_css(tokens) + style
    if adapter["canonical_type"] == "bar-chart" and is_detailed_bar_chart(plan):
        style = bar_chart_css(tokens) + style
    if adapter["canonical_type"] == "line-chart" and is_detailed_line_chart(plan):
        style = line_chart_css(tokens) + style
    if adapter["canonical_type"] == "scatter-plot" and is_detailed_scatter_chart(plan):
        style = scatter_chart_css(tokens) + style
    if adapter["canonical_type"] == "radar" and is_detailed_radar(plan):
        style = radar_css(tokens) + style
    if adapter["canonical_type"] == "polar-chart" and is_detailed_polar_chart(plan):
        style = polar_chart_css(tokens) + style
    if adapter["canonical_type"] == "treemap" and is_detailed_treemap(plan):
        style = treemap_css(tokens) + style
    if adapter["canonical_type"] == "wardley-map" and is_detailed_wardley_map(plan):
        style = wardley_map_css(tokens) + style
    if adapter["canonical_type"] == "venn" and is_detailed_venn(plan):
        style = venn_css(tokens) + style
    if adapter["canonical_type"] == "dp-security-matrix" and is_detailed_dp_security_matrix(plan):
        style = dp_security_matrix_css(tokens) + style
    if adapter["canonical_type"] == "er-data-model" and is_detailed_er_data_model(plan):
        style = er_data_model_css(tokens) + style
    if adapter["canonical_type"] == "uml-class" and is_detailed_uml_class(plan):
        style = uml_class_css(tokens) + style
    if adapter["canonical_type"] == "high-level" and is_detailed_high_level(plan):
        style = high_level_css(tokens) + style
    if adapter["canonical_type"] == "it-current-state" and is_detailed_it_current_state(plan):
        style = it_current_state_css(tokens) + style
    if adapter["canonical_type"] == "kanban" and is_detailed_kanban(plan):
        style = kanban_css(tokens) + style
    if adapter["canonical_type"] == "story-map" and is_detailed_story_map(plan):
        style = story_map_css(tokens) + style
    if adapter["canonical_type"] == "state-machine" and is_detailed_state_machine(plan):
        style = state_machine_css(tokens) + style
    if adapter["canonical_type"] == "sequence" and is_detailed_sequence(plan):
        style = sequence_css(tokens) + style
    if is_layers_variant:
        style = layers_css(tokens) + style
    if adapter["canonical_type"] == "medallion" and is_detailed_medallion(plan):
        style = medallion_css(tokens) + style
    if adapter["canonical_type"] == "tree" and is_detailed_tree(plan):
        style = tree_css(tokens) + style
    alternative = gantt_table(plan) if adapter["canonical_type"] == "gantt" else '<details><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Collection</th><th scope="col">Semantic IDs</th><th scope="col">Count</th></tr></thead><tbody>' + _data_rows(plan) + '</tbody></table></details>'
    if adapter["canonical_type"] == "loop-flywheel":
        alternative = flywheel_table(plan)
    if adapter["canonical_type"] == "fishbone":
        alternative = fishbone_table(plan)
    if adapter["canonical_type"] == "dp-integration" and is_detailed_dp_integration(plan):
        alternative = dp_integration_table(plan)
    if adapter["canonical_type"] == "bar-chart" and is_detailed_bar_chart(plan):
        alternative = bar_chart_table(plan)
    if adapter["canonical_type"] == "line-chart" and is_detailed_line_chart(plan):
        alternative = line_chart_table(plan)
    if adapter["canonical_type"] == "scatter-plot" and is_detailed_scatter_chart(plan):
        alternative = scatter_chart_table(plan)
    if adapter["canonical_type"] == "radar" and is_detailed_radar(plan):
        alternative = radar_table(plan)
    if adapter["canonical_type"] == "polar-chart" and is_detailed_polar_chart(plan):
        alternative = polar_chart_table(plan)
    if adapter["canonical_type"] == "treemap" and is_detailed_treemap(plan):
        alternative = treemap_table(plan)
    if adapter["canonical_type"] == "wardley-map" and is_detailed_wardley_map(plan):
        alternative = wardley_map_table(plan)
    if adapter["canonical_type"] == "venn" and is_detailed_venn(plan):
        alternative = venn_table(plan)
    if adapter["canonical_type"] == "dp-security-matrix" and is_detailed_dp_security_matrix(plan):
        alternative = dp_security_matrix_table(plan)
    if adapter["canonical_type"] == "er-data-model" and is_detailed_er_data_model(plan):
        alternative = er_data_model_table(plan)
    if adapter["canonical_type"] == "uml-class" and is_detailed_uml_class(plan):
        alternative = uml_class_table(plan)
    if adapter["canonical_type"] == "high-level" and is_detailed_high_level(plan):
        alternative = high_level_table(plan)
    if adapter["canonical_type"] == "it-current-state" and is_detailed_it_current_state(plan):
        alternative = it_current_state_table(plan)
    if adapter["canonical_type"] == "kanban" and is_detailed_kanban(plan):
        alternative = kanban_table(plan)
    if adapter["canonical_type"] == "story-map" and is_detailed_story_map(plan):
        alternative = story_map_table(plan)
    if adapter["canonical_type"] == "state-machine" and is_detailed_state_machine(plan):
        alternative = state_machine_table(plan)
    if adapter["canonical_type"] == "sequence" and is_detailed_sequence(plan):
        alternative = sequence_table(plan)
    if is_layers_variant:
        alternative = layers_table(plan)
    if adapter["canonical_type"] == "medallion" and is_detailed_medallion(plan):
        alternative = medallion_table(plan)
    if adapter["canonical_type"] == "tree" and is_detailed_tree(plan):
        alternative = tree_table(plan)
    presentation_attr = f' data-presentation-variant="{identity}"' if is_layers_variant or is_scatter_variant else ""
    fact_label = "TYPE / VARIANT" if is_layers_variant or is_scatter_variant else "TYPE / CAPABILITY"
    return f'''<!doctype html><html lang="vi" data-candidate-id="{P19B_CANDIDATE_ID}" data-fixture-id="{_text(fixture_id)}" data-diagram-type="{_text(adapter['canonical_type'])}" data-capability-id="{_text(adapter['capability_id'] or 'none')}" data-parent-type="{_text(parent)}"{presentation_attr} data-mode="{_text(mode)}" data-layout-engine="{_text(engine)}" data-silhouette="{_text(silhouette)}" data-visual-parent-candidate="{P18_PARENT_CANDIDATE_ID}" data-visual-parent-manifest-sha256="{P18_PARENT_MANIFEST_SHA256}" data-check-disposition="p19b-static-and-browser-planned"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="{'dark' if mode == 'neutral-dark' else 'light'}"><title>{_text(identity)} · {_text(mode)} · P-19B</title><style>{style}</style></head><body><main><header><div><p class="eyebrow">P‑19B · P18 INHERITED · {_text(engine.upper())}</p><h1>{_text(title)}</h1><p class="takeaway">{takeaway}</p></div><div class="receipts" aria-label="P-18 visual lineage and resolved typography"><span>{_text(identity)} · {_text(mode)}</span><span>Georgia · display</span><span>Avenir Next · material</span><span>Menlo · technical</span></div></header><figure class="artifact-frame">{svg}</figure><section class="facts" aria-label="Thông tin specimen"><div class="fact"><span>{fact_label}</span><strong>{_text(identity)}</strong></div><div class="fact"><span>LAYOUT ENGINE</span><strong>{_text(engine)}</strong></div><div class="fact"><span>VISUAL PARENT</span><strong>P‑18R6 review‑17</strong></div></section>{alternative}<pre hidden id="p19b-metadata">{escape(json.dumps(metadata, ensure_ascii=False, sort_keys=True), quote=False)}</pre></main></body></html>'''


def renderer_inventory() -> dict[str, Any]:
    """Return the explicit adapter-to-recipe binding used by P-19B."""

    adapters = list(TYPE_ADAPTERS.values()) + list(CAPABILITY_ADAPTERS.values())
    return {
        "schema_version": P19B_SCHEMA_VERSION,
        "candidate_id": P19B_CANDIDATE_ID,
        "modes": list(MODES),
        "viewbox": list(VIEWBOX),
        "viewbox_overrides": {"gantt": "content-fit calendar; width >=1600; height from phase and row content", "loop-flywheel": "content-fit circle; width >=1600; card and shared-state clearance", "fishbone": "content-fit 5-category cause spine; exact category and label clearance", "dp-integration": "content-fit sources/platform/consumers/shared-services topology; 1800×1040", "sequence": "content-fit four-participant interaction; 2000×1140; two activations, five straight messages and one rounded self-call", "bar-chart": "content-fit eight-category zero-baseline comparison; 1800×940", "line-chart": "content-fit three-series eight-week trend; 2000×980; 24 exact points", "scatter-chart": "content-fit twelve-team deployment-performance scatter; 2000×1020; exact linear axes and OLS trend", "polar-chart": "content-fit eight-window radial spokes; 2000×1020; exact 0–100 percent scale", "treemap": "content-fit six-continent exact-area tiling; 2000×1040; one focal and one compact-label tile", "wardley-map": "content-fit eight-component visibility/evolution map; 2000×980", "venn": "content-fit three equal sets; 2000×1040; exact nested-clipped triple intersection", "dp-security-matrix": "content-fit five-role by five-component permission matrix; 2000×820", "er-data-model": "content-fit four-entity aggregate/join model; 2000×940", "high-level": "content-fit end-to-end data-platform overview; 2000×1040; rounded 90-degree corners by default", "it-current-state": "content-fit collection/processing/dissemination landscape; 2000×1040; rounded 90-degree corners by default", "kanban": "content-fit four-column WIP board; 2000×900; explicit blocked/waiting/done states", "story-map": "content-fit four-activity story map; 2000×1040; three release slices, one MVP cut and one high-risk story", "state-machine": "content-fit four-state lifecycle; 2000×980; five straight centered transitions and one rounded return route", "layers": "content-fit five-band abstraction stack; 2000×920; one non-color focal layer", "medallion": "content-fit five-stage lifecycle; 2000×1020; four directed promotions and two processing paths", "tree": "content-fit three-tier centered-span hierarchy; 2000×920; P-18 org-chart fanout grammar"},
        "adapter_count": len(adapters),
        "engine_renderer_count": len(ENGINE_RENDERERS),
        "visual_parent_candidate_id": P18_PARENT_CANDIDATE_ID,
        "visual_parent_manifest_sha256": P18_PARENT_MANIFEST_SHA256,
        "visual_mode_tokens": P18_VISUAL_MODES,
        "bindings": [
            {
                "adapter_id": item.adapter_id,
                "layout_engine": item.layout_engine,
                "silhouette": item.silhouette,
                "renderer": ENGINE_RENDERERS[item.layout_engine].__name__,
            }
            for item in adapters
        ],
        "boundary": {
            "standalone_html": True,
            "external_resources": False,
            "package_asset": False,
            "p19c_full_qa_freeze_owner_review": False,
        },
    }


__all__ = [
    "GalleryRenderError",
    "MODES",
    "P19B_CANDIDATE_ID",
    "P19B_SCHEMA_VERSION",
    "P18_PARENT_CANDIDATE_ID",
    "P18_PARENT_MANIFEST_SHA256",
    "P18_VISUAL_MODES",
    "render_gallery_html",
    "renderer_inventory",
]
