"""Build the single P-18R5 neutral-light Swimlane anchor.

The display is an original lane-interaction composition derived from the locked
P18-C02 semantic IR.  The old rejected P-18 renderer is not imported.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True

from master_visual_kernel import (
    DataTag,
    EdgeSpec,
    FontMetricEngine,
    IntrinsicNodeSizer,
    LaneInteractionEngine,
    LaneLayout,
    LaneSpec,
    NodeContent,
    OrthogonalRouter,
    ResolvedFont,
    RoutedEdge,
    StageSpec,
    TypographyRequest,
    resolve_default_typography,
    rounded_orthogonal_path,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
LOCKED_CASE_SOURCE = REPO_ROOT / "evidence" / "p18" / "source"
if str(LOCKED_CASE_SOURCE) not in sys.path:
    sys.path.insert(0, str(LOCKED_CASE_SOURCE))

from p18_cases import swimlane_case  # noqa: E402


TOKENS = {
    "canvas": "#F7F6F2",
    "surface": "#FFFFFF",
    "surface_soft": "#F1F0EC",
    "surface_focus": "#FFF3EC",
    "ink": "#242B3D",
    "ink_soft": "#526078",
    "ink_faint": "#667085",
    "line": "#C9CDD2",
    "line_soft": "#DFE1E2",
    "connector": "#51617A",
    "accent": "#F26A32",
    "accent_text": "#B84A1B",
    "accent_soft": "#FAD8C9",
    "tag_check": "#4F6F94",
    "tag_notice": "#675D73",
    "tag_listing": "#5E7452",
    "tag_ar": "#8C632E",
    "tag_ledger": "#A56545",
}


@dataclass(frozen=True)
class AnchorModel:
    semantic_ir: Mapping[str, Any]
    typography: Mapping[str, ResolvedFont]
    metrics: FontMetricEngine
    layout: LaneLayout
    routes: tuple[RoutedEdge, ...]
    artifact_types: tuple[DataTag, ...]


def _tag(code: str, label: str, kind: str) -> DataTag:
    return DataTag(code, label, kind)


def build_anchor_model(request: TypographyRequest | None = None) -> AnchorModel:
    semantic_ir = swimlane_case()
    typography = resolve_default_typography(request)
    metrics = FontMetricEngine(typography)

    lanes = (
        LaneSpec("sw-lane-customer", "KHA", "Khách hàng"),
        LaneSpec("sw-lane-mail", "THU", "Phòng thư"),
        LaneSpec("sw-lane-cash", "TIE", "Thu tiền"),
        LaneSpec("sw-lane-ar", "PTH", "Phải thu"),
        LaneSpec("sw-lane-ledger", "SCA", "Sổ cái"),
        LaneSpec("sw-lane-bank", "NHA", "Ngân hàng"),
    )
    stages = (
        StageSpec(0, "", "KHỞI TẠO"),
        StageSpec(1, "1", "NHẬN BỘ"),
        StageSpec(2, "2", "PHÂN LOẠI"),
        StageSpec(3, "3", "GỬI NGÂN HÀNG"),
        StageSpec(4, "4", "CẬP NHẬT NỢ", True),
        StageSpec(5, "5", "ĐĂNG SỔ"),
    )
    artifact_types = (
        _tag("SÉC", "Séc", "check"),
        _tag("GBC", "Giấy báo chuyển tiền", "notice"),
        _tag("B.KÊ", "Bảng kê chuyển tiền", "listing"),
        _tag("TỆP PT", "Tệp phải thu", "ar"),
        _tag("TỆP SC", "Tệp sổ cái", "ledger"),
    )
    by_kind = {item.kind: item for item in artifact_types}
    nodes = (
        NodeContent(
            "card-customer",
            "sw-lane-customer",
            0,
            "KHA",
            "Chuẩn bị thanh toán",
            "chứng từ → gửi đi",
            "cổng khách hàng",
            (by_kind["check"], by_kind["notice"]),
            ("sw-check-customer", "sw-notice-customer"),
        ),
        NodeContent(
            "card-mail",
            "sw-lane-mail",
            1,
            "THU",
            "Tiếp nhận bộ chứng từ",
            "nhận → phân luồng",
            "phòng thư đến",
            (by_kind["check"], by_kind["notice"], by_kind["listing"]),
            ("sw-check-mail", "sw-notice-mail", "sw-listing-mail"),
        ),
        NodeContent(
            "card-cash",
            "sw-lane-cash",
            2,
            "TIE",
            "Kiểm đếm và đối chiếu",
            "bộ nhận → bộ đã kiểm",
            "bàn thu tiền",
            (by_kind["check"], by_kind["listing"]),
            ("sw-check-cash", "sw-listing-cash"),
        ),
        NodeContent(
            "card-bank",
            "sw-lane-bank",
            3,
            "NHA",
            "Ghi nhận tiền gửi",
            "séc → xác nhận ngân hàng",
            "ngân hàng đối tác",
            (by_kind["check"],),
            ("sw-check-bank",),
        ),
        NodeContent(
            "card-ar",
            "sw-lane-ar",
            4,
            "PTH",
            "Cập nhật công nợ",
            "giấy báo → số dư mới",
            "phân hệ phải thu",
            (by_kind["notice"], by_kind["ar"]),
            ("sw-notice-ar", "sw-file-ar"),
            True,
        ),
        NodeContent(
            "card-ledger-post",
            "sw-lane-ledger",
            4,
            "SCA",
            "Đăng bảng kê tổng hợp",
            "bảng kê → bút toán",
            "phân hệ sổ cái",
            (by_kind["listing"],),
            ("sw-listing-ledger",),
        ),
        NodeContent(
            "card-ledger-close",
            "sw-lane-ledger",
            5,
            "SCA",
            "Đối soát cuối ngày",
            "hai luồng → tệp chốt",
            "sổ trung tâm",
            (by_kind["ar"], by_kind["ledger"]),
            ("sw-file-ledger",),
        ),
    )
    edges = (
        EdgeSpec("route-01", "card-customer", "card-mail", "01 · NHẬN BỘ", ("sw-e01", "sw-e04")),
        EdgeSpec("route-02", "card-mail", "card-cash", "02 · PHÂN LOẠI", ("sw-e02", "sw-e07")),
        EdgeSpec("route-03", "card-cash", "card-bank", "", ("sw-e03",)),
        EdgeSpec("route-04", "card-mail", "card-ar", "04 · CẬP NHẬT", ("sw-e05", "sw-e06"), True),
        EdgeSpec("route-05", "card-cash", "card-ledger-post", "05 · ĐĂNG SỔ", ("sw-e08",)),
        EdgeSpec("route-06", "card-ledger-post", "card-ledger-close", "", ("sw-e09",)),
        EdgeSpec("route-07", "card-ar", "card-ledger-close", "", ("sw-e10",), True),
    )

    _validate_semantic_projection(semantic_ir, nodes, edges)
    stress_text = "Đối chiếu séc, giấy báo chuyển tiền và tệp phải thu — Đặng Thị Mỹ Hạnh"
    for role_name in typography:
        missing = metrics.validate_glyphs(role_name, stress_text)
        if missing:
            raise RuntimeError(f"Missing glyphs in {role_name}: {missing}")

    layout = LaneInteractionEngine(IntrinsicNodeSizer(metrics)).layout(lanes, stages, nodes)
    label_widths = {edge.edge_id: metrics.measure("technical", edge.label).width for edge in edges}
    routes = OrthogonalRouter(clearance=16, label_clearance=10).route(layout, edges, label_widths)
    return AnchorModel(semantic_ir, typography, metrics, layout, routes, artifact_types)


def _validate_semantic_projection(
    semantic_ir: Mapping[str, Any],
    nodes: Sequence[NodeContent],
    edges: Sequence[EdgeSpec],
) -> None:
    expected_nodes = {item["id"] for item in semantic_ir["nodes"]}
    projected_nodes = [semantic_id for node in nodes for semantic_id in node.semantic_node_ids]
    if set(projected_nodes) != expected_nodes or len(projected_nodes) != len(set(projected_nodes)):
        raise RuntimeError("Swimlane node projection must cover every locked semantic node exactly once")
    expected_edges = {item["id"] for item in semantic_ir["edges"]}
    projected_edges = [semantic_id for edge in edges for semantic_id in edge.semantic_edge_ids]
    if set(projected_edges) != expected_edges or len(projected_edges) != len(set(projected_edges)):
        raise RuntimeError("Swimlane edge projection must cover every locked semantic edge exactly once")


def _font_css(model: AnchorModel) -> str:
    role_names = {
        "lane": "--font-human",
        "node_title": "--font-human",
        "material": "--font-human",
        "legend": "--font-human",
        "technical": "--font-mono",
        "badge": "--font-mono",
        "tag": "--font-mono",
    }
    declarations: dict[str, str] = {}
    for role_name, css_name in role_names.items():
        declarations[css_name] = model.typography[role_name].resolved_family
    declarations["--font-display"] = model.typography["display"].resolved_family
    return ";".join(f"{name}:'{escape(value)}'" for name, value in declarations.items())


def _node_svg(model: AnchorModel, node: Any) -> str:
    box = node.box
    content = node.content
    classes = "node-card focal" if content.focal else "node-card"
    parts = [
        f'<g class="{classes}" data-node-id="{escape(content.node_id)}" '
        f'data-semantic-node-ids="{escape(",".join(content.semantic_node_ids))}" '
        f'role="group" aria-label="{escape(content.title)}">',
        f'<rect class="node-boundary" x="{box.x:.2f}" y="{box.y:.2f}" width="{box.width:.2f}" height="{box.height:.2f}" rx="14"/>',
        f'<rect class="role-badge" x="{box.x + 16:.2f}" y="{box.y + 16:.2f}" width="56" height="20" rx="5"/>',
        f'<text class="badge-text" x="{box.x + 44:.2f}" y="{box.y + 31:.2f}" text-anchor="middle">{escape(content.role_badge)}</text>',
    ]
    title_top = box.y + 44
    for index, line in enumerate(node.title_lines):
        parts.append(
            f'<text class="node-title" data-material-text="true" data-owner-node="{escape(content.node_id)}" '
            f'x="{box.x + 20:.2f}" y="{title_top + 24 + index * 30:.2f}">{escape(line)}</text>'
        )
    transition_y = title_top + len(node.title_lines) * 30 + 20
    parts.append(
        f'<text class="node-transition" data-material-text="true" data-owner-node="{escape(content.node_id)}" '
        f'x="{box.x + 20:.2f}" y="{transition_y:.2f}">{escape(content.transition)}</text>'
    )
    bottom_y = box.bottom - 16
    parts.append(
        f'<text class="system-line" data-material-text="true" data-owner-node="{escape(content.node_id)}" '
        f'x="{box.x + 20:.2f}" y="{bottom_y:.2f}">{escape(content.system_line)}</text>'
    )
    tag_x = box.right - 16
    for tag, width in reversed(tuple(zip(content.tags, node.tag_widths))):
        tag_x -= width
        parts.extend(
            [
                f'<rect class="data-tag tag-{escape(tag.kind)}" x="{tag_x:.2f}" y="{box.bottom - 34:.2f}" width="{width:.2f}" height="22" rx="5"/>',
                f'<text class="tag-text" data-material-text="true" data-owner-node="{escape(content.node_id)}" '
                f'x="{tag_x + width / 2:.2f}" y="{box.bottom - 18:.2f}" text-anchor="middle">{escape(tag.code)}</text>',
            ]
        )
        tag_x -= 7
    parts.append("</g>")
    return "".join(parts)


def _route_svg(route: RoutedEdge) -> str:
    color_class = "edge critical" if route.spec.critical else "edge"
    marker = "url(#arrow-accent)" if route.spec.critical else "url(#arrow-standard)"
    label = route.label_box
    parts = [
        f'<path class="{color_class}" data-edge-id="{escape(route.spec.edge_id)}" '
        f'data-source="{escape(route.spec.source)}" data-target="{escape(route.spec.target)}" '
        f'data-semantic-edge-ids="{escape(",".join(route.spec.semantic_edge_ids))}" '
        f'd="{rounded_orthogonal_path(route.points)}" marker-end="{marker}"/>',
        f'<circle class="port-dot" cx="{route.source_port.point.x:.2f}" cy="{route.source_port.point.y:.2f}" r="4"/>',
    ]
    if route.spec.label:
        parts.extend(
            [
                f'<rect class="edge-label-mask" data-edge-label-for="{escape(route.spec.edge_id)}" '
                f'x="{label.x:.2f}" y="{label.y:.2f}" width="{label.width:.2f}" height="{label.height:.2f}" rx="5"/>',
                f'<text class="edge-label{(" critical-label" if route.spec.critical else "")}" '
                f'x="{label.cx:.2f}" y="{label.y + 19:.2f}" text-anchor="middle">{escape(route.spec.label)}</text>',
            ]
        )
    for bridge in route.bridges:
        parts.append(
            f'<path class="bridge-hop" d="M {bridge.point.x - 11:.2f} {bridge.point.y:.2f} '
            f'C {bridge.point.x - 7:.2f} {bridge.point.y - 12:.2f}, {bridge.point.x + 7:.2f} {bridge.point.y - 12:.2f}, '
            f'{bridge.point.x + 11:.2f} {bridge.point.y:.2f}"/>'
        )
    return "".join(parts)


def render_svg(model: AnchorModel) -> str:
    layout = model.layout
    board = layout.artboard
    human_family = model.typography["node_title"].resolved_family
    mono_family = model.typography["technical"].resolved_family
    css = f"""
      :root{{{_font_css(model)}}}
      text{{font-family:'{escape(human_family)}';fill:{TOKENS['ink']};text-rendering:geometricPrecision}}
      .mono,.rail-label,.rail-number,.edge-label,.badge-text,.tag-text,.legend-kicker,.legend-note{{font-family:'{escape(mono_family)}'}}
      .lane-divider{{stroke:{TOKENS['line_soft']};stroke-width:1.5}}
      .lane-rail{{fill:{TOKENS['surface_soft']};fill-opacity:.62}}
      .lane-code{{font-family:'{escape(mono_family)}';font-size:14px;font-weight:700;letter-spacing:1.7px;fill:{TOKENS['ink_faint']}}}
      .lane-label{{font-size:18px;font-weight:600;letter-spacing:.3px;fill:{TOKENS['ink_soft']}}}
      .rail-line{{stroke:{TOKENS['line']};stroke-width:2}}
      .rail-dot{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line']};stroke-width:2}}
      .rail-dot.focal{{fill:{TOKENS['accent_soft']};stroke:{TOKENS['accent']}}}
      .rail-number{{font-size:14px;font-weight:700;fill:{TOKENS['ink']}}}
      .rail-number.focal,.rail-label.focal{{fill:{TOKENS['accent_text']}}}
      .rail-label{{font-size:14px;font-weight:700;letter-spacing:1.8px;fill:{TOKENS['ink_soft']}}}
      .node-boundary{{fill:{TOKENS['surface']};stroke:{TOKENS['line']};stroke-width:2.2}}
      .node-card.focal .node-boundary{{fill:{TOKENS['surface_focus']};stroke:{TOKENS['accent']};stroke-width:2.6}}
      .role-badge{{fill:{TOKENS['surface_soft']};stroke:{TOKENS['line_soft']};stroke-width:1}}
      .focal .role-badge{{fill:{TOKENS['accent_soft']};stroke:none}}
      .badge-text{{font-size:14px;font-weight:700;letter-spacing:.8px;fill:{TOKENS['ink_soft']}}}
      .focal .badge-text{{fill:{TOKENS['accent_text']}}}
      .node-title{{font-size:24px;font-weight:600;fill:{TOKENS['ink']}}}
      .node-transition{{font-size:16px;font-weight:500;fill:{TOKENS['ink_soft']}}}
      .system-line{{font-family:'{escape(mono_family)}';font-size:14px;fill:{TOKENS['ink_faint']}}}
      .data-tag{{stroke:none}}
      .tag-check{{fill:{TOKENS['tag_check']}}}.tag-notice{{fill:{TOKENS['tag_notice']}}}.tag-listing{{fill:{TOKENS['tag_listing']}}}.tag-ar{{fill:{TOKENS['tag_ar']}}}.tag-ledger{{fill:{TOKENS['tag_ledger']}}}
      .tag-text{{font-size:14px;font-weight:700;letter-spacing:.3px;fill:#fff}}
      .edge{{fill:none;stroke:{TOKENS['connector']};stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
      .edge.critical{{stroke:{TOKENS['accent']};stroke-width:3.6}}
      .port-dot{{fill:{TOKENS['canvas']};stroke:{TOKENS['connector']};stroke-width:2}}
      .edge-label-mask{{fill:{TOKENS['canvas']};stroke:none}}
      .edge-label{{font-size:14px;font-weight:700;letter-spacing:1px;fill:{TOKENS['ink_soft']}}}
      .critical-label{{fill:{TOKENS['accent_text']}}}
      .bridge-hop{{fill:{TOKENS['canvas']};stroke:{TOKENS['connector']};stroke-width:3}}
      .legend-divider{{stroke:{TOKENS['line']};stroke-width:1.5}}
      .legend-kicker{{font-size:14px;font-weight:700;letter-spacing:1.8px;fill:{TOKENS['ink_faint']}}}
      .legend-label{{font-size:16px;font-weight:500;fill:{TOKENS['ink_soft']}}}
      .legend-note{{font-size:14px;letter-spacing:1.2px;fill:{TOKENS['ink_faint']}}}
    """
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {board.width:.2f} {board.height:.2f}" '
        f'width="{board.width:.0f}" height="{board.height:.0f}" role="img" aria-labelledby="anchor-title anchor-desc" '
        f'data-anchor-id="P18R5-SWIMLANE-NEUTRAL-LIGHT" data-layout-engine="lane-interaction" '
        f'data-mode="neutral-light" data-resolved-human-font="{escape(human_family)}" data-resolved-mono-font="{escape(mono_family)}">',
        '<title id="anchor-title">Luồng chứng từ thu tiền theo sáu chủ thể</title>',
        '<desc id="anchor-desc">Sơ đồ lane từ khách hàng đến ngân hàng, phải thu và sổ cái; nhánh cập nhật công nợ được nhấn màu coral.</desc>',
        "<defs>",
        f'<pattern id="dot-field" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="{TOKENS["line"]}" opacity=".24"/></pattern>',
        f'<marker id="arrow-standard" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1,1 L11,6 L1,11 Z" fill="{TOKENS["connector"]}"/></marker>',
        f'<marker id="arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1,1 L11,6 L1,11 Z" fill="{TOKENS["accent"]}"/></marker>',
        f"<style>{css}</style>",
        "</defs>",
        f'<rect width="{board.width:.2f}" height="{board.height:.2f}" fill="{TOKENS["canvas"]}"/>',
        f'<rect x="0" y="0" width="{board.width:.2f}" height="{board.height:.2f}" fill="url(#dot-field)"/>',
        f'<rect class="lane-rail" x="0" y="{board.rail_height:.2f}" width="280" height="{board.legend_top - board.rail_height:.2f}"/>',
    ]

    for lane_index, lane in enumerate(layout.lanes):
        top = board.lane_top + lane_index * board.lane_height
        center = top + board.lane_height / 2
        parts.extend(
            [
                f'<line class="lane-divider" x1="0" y1="{top:.2f}" x2="{board.width:.2f}" y2="{top:.2f}"/>',
                f'<text class="lane-code" x="58" y="{center - 9:.2f}">{escape(lane.code)}</text>',
                f'<text class="lane-label" x="58" y="{center + 20:.2f}">{escape(lane.label)}</text>',
            ]
        )
    parts.append(
        f'<line class="lane-divider" x1="0" y1="{board.legend_top:.2f}" x2="{board.width:.2f}" y2="{board.legend_top:.2f}"/>'
    )

    rail_y = 66.0
    visible_stages = [stage for stage in layout.stages if stage.number]
    first_x = layout.stage_centers[visible_stages[0].index]
    last_x = layout.stage_centers[visible_stages[-1].index]
    parts.append(f'<line class="rail-line" x1="{first_x:.2f}" y1="{rail_y:.2f}" x2="{last_x:.2f}" y2="{rail_y:.2f}"/>')
    for stage in visible_stages:
        x = layout.stage_centers[stage.index]
        focus_class = " focal" if stage.focal else ""
        parts.extend(
            [
                f'<circle class="rail-dot{focus_class}" cx="{x:.2f}" cy="{rail_y:.2f}" r="19"/>',
                f'<text class="rail-number{focus_class}" x="{x:.2f}" y="{rail_y + 5:.2f}" text-anchor="middle">{escape(stage.number)}</text>',
                f'<text class="rail-label{focus_class}" x="{x:.2f}" y="{rail_y + 43:.2f}" text-anchor="middle">{escape(stage.label)}</text>',
            ]
        )

    parts.extend(_route_svg(route) for route in model.routes)
    parts.extend(_node_svg(model, node) for node in layout.nodes)

    legend_top = board.legend_top
    row1 = legend_top + 46
    row2 = legend_top + 98
    row3 = legend_top + 148
    parts.extend(
        [
            f'<line class="legend-divider" x1="52" y1="{legend_top + 20:.2f}" x2="{board.width - 52:.2f}" y2="{legend_top + 20:.2f}"/>',
            f'<text class="legend-kicker" x="58" y="{row1:.2f}">HANDOFF</text>',
            f'<text class="legend-kicker" x="58" y="{row2:.2f}">DỮ LIỆU</text>',
            f'<text class="legend-kicker" x="58" y="{row3:.2f}">LUỒNG</text>',
        ]
    )
    legend_x = 280.0
    for stage in visible_stages:
        focus = stage.focal
        fill = TOKENS["accent_soft"] if focus else TOKENS["surface_soft"]
        stroke = TOKENS["accent"] if focus else TOKENS["line"]
        number_color = TOKENS["accent_text"] if focus else TOKENS["ink"]
        parts.extend(
            [
                f'<circle cx="{legend_x:.2f}" cy="{row1 - 6:.2f}" r="16" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
                f'<text class="rail-number" x="{legend_x:.2f}" y="{row1 - 1:.2f}" text-anchor="middle" fill="{number_color}">{escape(stage.number)}</text>',
                f'<text class="legend-label" x="{legend_x + 28:.2f}" y="{row1:.2f}">{escape(stage.label.title())}</text>',
            ]
        )
        legend_x += 250
    legend_x = 280.0
    for item in model.artifact_types:
        color = TOKENS[f"tag_{item.kind}"]
        parts.extend(
            [
                f'<rect x="{legend_x:.2f}" y="{row2 - 18:.2f}" width="40" height="18" rx="5" fill="{color}"/>',
                f'<text class="legend-label" x="{legend_x + 54:.2f}" y="{row2:.2f}">{escape(item.label)}</text>',
            ]
        )
        legend_x += 360
    parts.extend(
        [
            f'<line x1="280" y1="{row3 - 6:.2f}" x2="348" y2="{row3 - 6:.2f}" stroke="{TOKENS["accent"]}" stroke-width="3.6" marker-end="url(#arrow-accent)"/>',
            f'<text class="legend-label" x="372" y="{row3:.2f}">Nhánh cần chú ý</text>',
            f'<line x1="650" y1="{row3 - 6:.2f}" x2="718" y2="{row3 - 6:.2f}" stroke="{TOKENS["connector"]}" stroke-width="3" marker-end="url(#arrow-standard)"/>',
            f'<text class="legend-label" x="742" y="{row3:.2f}">Handoff tuần tự</text>',
            f'<text class="legend-note" x="{board.width - 58:.2f}" y="{row3:.2f}" text-anchor="end">TRÁI VÀO · PHẢI RA</text>',
        ]
    )
    parts.append("</svg>")
    return "".join(parts)


def render_html(model: AnchorModel, svg: str) -> str:
    board = model.layout.artboard
    font_receipts = []
    seen_roles: set[str] = set()
    for role_name, resolved in model.typography.items():
        if resolved.resolved_family in seen_roles:
            continue
        seen_roles.add(resolved.resolved_family)
        source = "fallback đã công bố" if resolved.fallback_used else "font mặc định"
        font_receipts.append(
            f'<span class="receipt"><strong>{escape(resolved.resolved_family)}</strong> · {escape(source)}</span>'
        )
    rows = []
    for node in model.layout.nodes:
        rows.append(
            "<tr>"
            f"<td>{escape(node.content.role_badge)}</td>"
            f"<td>{escape(node.content.title)}</td>"
            f"<td>{escape(', '.join(node.content.semantic_node_ids))}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luồng chứng từ thu tiền · P-18R5</title>
  <style>
    :root {{ color-scheme: light; --paper: #eeece7; --ink: #242b3d; --muted: #687286; }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background: var(--paper); color: var(--ink); }}
    body {{ font-family: '{escape(model.typography['material'].resolved_family)}', sans-serif; padding: 48px 24px 80px; }}
    .page-shell {{ width: min(100%, {board.width:.0f}px); margin: 0 auto; }}
    .page-header {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; align-items: end; margin: 0 0 24px; }}
    .eyebrow {{ margin: 0 0 8px; font-family: '{escape(model.typography['technical'].resolved_family)}', monospace; font-size: 14px; letter-spacing: .16em; color: #f26a32; }}
    h1 {{ margin: 0; font-family: '{escape(model.typography['display'].resolved_family)}', serif; font-size: 48px; line-height: 1.08; font-weight: 400; }}
    .lede {{ max-width: 660px; margin: 10px 0 0; font-size: 16px; line-height: 1.55; color: var(--muted); }}
    .receipt-strip {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }}
    .receipt {{ padding: 7px 10px; border: 1px solid #c9cdd2; border-radius: 7px; background: rgba(255,255,255,.52); font-family: '{escape(model.typography['technical'].resolved_family)}', monospace; font-size: 12px; color: #657086; }}
    .artifact-frame {{ overflow: hidden; border: 1px solid #d8d6d1; border-radius: 18px; background: #f7f6f2; box-shadow: 0 20px 60px rgba(45, 52, 67, .10); }}
    .artifact-frame svg {{ display: block; width: 100%; height: auto; }}
    .evidence {{ margin-top: 24px; padding: 24px; border: 1px solid #d8d6d1; border-radius: 14px; background: rgba(255,255,255,.54); }}
    .evidence h2 {{ margin: 0 0 10px; font-size: 20px; }}
    .evidence p {{ margin: 0 0 14px; color: var(--muted); line-height: 1.55; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 12px; border-top: 1px solid #d8d6d1; text-align: left; vertical-align: top; }}
    th {{ color: #58647a; font-weight: 600; }}
    @media (max-width: 820px) {{
      body {{ padding: 24px 12px 48px; }}
      .page-header {{ grid-template-columns: 1fr; }}
      .receipt-strip {{ justify-content: flex-start; }}
      h1 {{ font-size: 40px; }}
      .evidence {{ overflow-x: auto; }}
    }}
    @media print {{ body {{ padding: 0; background: #fff; }} .page-header, .evidence {{ display: none; }} .artifact-frame {{ border: 0; box-shadow: none; }} }}
  </style>
</head>
<body>
  <main class="page-shell">
    <header class="page-header">
      <div>
        <p class="eyebrow">P‑18R5 · NEUTRAL LIGHT ANCHOR</p>
        <h1>Luồng chứng từ thu tiền</h1>
        <p class="lede">Một Swimlane nguyên bản từ semantic IR đã khóa; lane, handoff và năm loại chứng từ được giữ độc lập. Nhánh công nợ là focal path duy nhất.</p>
      </div>
      <div class="receipt-strip" aria-label="Biên nhận font đã resolve">{''.join(font_receipts)}</div>
    </header>
    <section class="artifact-frame" aria-label="Canonical Swimlane render">{svg}</section>
    <section class="evidence" aria-labelledby="evidence-title">
      <h2 id="evidence-title">Semantic projection</h2>
      <p>Phần này nằm ngoài canonical screenshot và không tham gia blind/five-second review.</p>
      <table>
        <thead><tr><th>Lane</th><th>Activity card</th><th>Locked semantic nodes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


__all__ = ["AnchorModel", "TOKENS", "build_anchor_model", "render_html", "render_svg"]
