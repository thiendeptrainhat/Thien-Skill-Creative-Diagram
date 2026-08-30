"""Shared original visual foundation for the bounded P-18R pilot.

This module is QA-only evidence source.  It deliberately contains no upstream
code, template, SVG or CSS and is not part of a distributable runtime.
"""

from __future__ import annotations

from html import escape
from typing import Mapping


CANVAS_WIDTH = 1440
CANVAS_HEIGHT = 900
FIELD_TOP = 34
FIELD_BOTTOM = 748
LEGEND_TOP = 770
LEGEND_BOTTOM = 878
BODY_TRANSFORM = "matrix(1.03 0 0 1.03 -21.6 -112)"

PROFILE_BY_CASE = {
    "P18-C01-ARCH": "network-field",
    "P18-C02-SWIM": "network-field",
    "P18-C03-SANKEY": "quantitative-field",
    "P18-C04-TREEMAP": "quantitative-field",
    "P18-C05-WARDLEY": "quantitative-field",
    "P18-C06-DEPLOY": "network-field",
    "P18-C07-JOURNEY": "narrative-field",
    "P18-C08-FISH": "narrative-field",
    "P18-V17-DUMBBELL": "quantitative-field",
    "P18-V18-SLOPE": "quantitative-field",
    "P18-V19-RIDGE": "quantitative-field",
    "P18-V20-BUBBLE": "quantitative-field",
}

INTENT_BY_CASE = {
    "P18-C01-ARCH": "Tuyến phê duyệt đi qua bốn ranh giới, không có đường tắt.",
    "P18-C02-SWIM": "Năm handoff chuyển chứng từ qua sáu chủ thể.",
    "P18-C03-SANKEY": "100 ML/ngày tách thành dòng phân phối và tổn thất được bảo toàn.",
    "P18-C04-TREEMAP": "Quỹ 100 đơn vị được chia theo diện tích và đúng nhóm cha.",
    "P18-C05-WARDLEY": "Chuỗi giá trị đi từ portal tùy biến đến hosting tiến hóa cao.",
    "P18-C06-DEPLOY": "Gateway dẫn vào cụm ứng dụng rồi fan-out sang hai kho dữ liệu.",
    "P18-C07-JOURNEY": "Điểm thấp nhất ở Apply; hành trình phục hồi mạnh đến Activate.",
    "P18-C08-FISH": "Mười giả thuyết từ năm nhóm cùng hội tụ vào một effect.",
    "P18-V17-DUMBBELL": "Mọi vùng đều giảm thời gian; Central và Remote giảm nhiều nhất.",
    "P18-V18-SLOPE": "Permits và Grants giảm; Records tăng nhẹ và không được tô như cải thiện.",
    "P18-V19-RIDGE": "Ba phân bố dùng chung bins và biên độ chuẩn hóa toàn cục.",
    "P18-V20-BUBBLE": "Migration có ngân sách lớn nhất và nằm ở vùng nỗ lực cao.",
}

LEGEND_BY_CASE = {
    "P18-C01-ARCH": (("node", "Thành phần"), ("boundary", "Ranh giới tin cậy"), ("route", "Quan hệ có hướng")),
    "P18-C02-SWIM": (("lane", "Chủ thể / lane"), ("artifact", "Chứng từ"), ("route", "Handoff đánh số")),
    "P18-C03-SANKEY": (("band", "Độ rộng = ML/ngày"), ("node", "Điểm tách / gộp"), ("focus", "Dòng phân phối")),
    "P18-C04-TREEMAP": (("area", "Diện tích = tỷ trọng"), ("boundary", "Nhóm cha"), ("value", "Giá trị chính xác")),
    "P18-C05-WARDLEY": (("point", "Thành phần"), ("route", "Phụ thuộc"), ("axis", "Vị trí chiến lược")),
    "P18-C06-DEPLOY": (("boundary", "Zone / host"), ("artifact", "Runtime artifact"), ("route", "Quan hệ runtime")),
    "P18-C07-JOURNEY": (("stage", "Giai đoạn"), ("positive", "Cảm xúc ≥ 0"), ("negative", "Cảm xúc < 0")),
    "P18-C08-FISH": (("branch", "Nhóm nguyên nhân"), ("cause", "Giả thuyết"), ("focus", "Effect cần phân tích")),
    "P18-V17-DUMBBELL": (("before", "Trước"), ("after", "Sau"), ("gap", "Khoảng chênh")),
    "P18-V18-SLOPE": (("left", "Q1"), ("right", "Q2"), ("slope", "Hướng thay đổi")),
    "P18-V19-RIDGE": (("ridge", "Histogram / team"), ("axis", "Shared domain"), ("value", "n = 6 mỗi team")),
    "P18-V20-BUBBLE": (("point", "x/y = tác động/nỗ lực"), ("area", "Diện tích = ngân sách"), ("focus", "Bong bóng lớn nhất")),
}


def estimate_text_width(value: str, font_px: float, *, mono: bool = False, weight: int = 500) -> float:
    """Deterministic width estimate used to reserve SVG line boxes.

    Browser QA later measures the real rendered bounds.  This estimate avoids
    the old character-count-only wrapping while keeping generation offline.
    """

    units = 0.0
    for char in value:
        if char.isspace():
            units += 0.34
        elif char in "ilI1.,:;|'`":
            units += 0.32
        elif char in "MW@#%&QGƠƯ":
            units += 0.92
        elif ord(char) > 127:
            units += 0.62
        else:
            units += 0.58
    if mono:
        units = len(value) * 0.62
    weight_factor = 1.03 if weight >= 650 else 1.0
    return units * font_px * weight_factor


def wrap_text(value: str, max_width: float, font_px: float, *, mono: bool = False, weight: int = 500) -> list[str]:
    words = value.split()
    if not words:
        return [value]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if estimate_text_width(candidate, font_px, mono=mono, weight=weight) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines


def _legend_mark(kind: str, x: float, y: float, t: Mapping[str, str]) -> str:
    if kind in {"route", "slope", "gap"}:
        return f'<line x1="{x}" y1="{y}" x2="{x+42}" y2="{y}" stroke="{t["connector"]}" stroke-width="3"/><path d="M{x+42},{y} L{x+33},{y-5} L{x+33},{y+5} Z" fill="{t["connector"]}"/>'
    if kind in {"boundary", "lane"}:
        return f'<rect x="{x}" y="{y-11}" width="42" height="22" rx="7" fill="none" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="7 5"/>'
    if kind in {"point", "before", "left", "cause", "value", "axis"}:
        return f'<circle cx="{x+20}" cy="{y}" r="8" fill="{t["panel"]}" stroke="{t["connector"]}" stroke-width="3"/>'
    if kind in {"focus", "after", "right", "positive"}:
        return f'<circle cx="{x+20}" cy="{y}" r="9" fill="{t["accent"]}" stroke="{t["canvas"]}" stroke-width="3"/>'
    if kind == "negative":
        return f'<rect x="{x+12}" y="{y-8}" width="16" height="16" transform="rotate(45 {x+20} {y})" fill="{t["negative"]}"/>'
    if kind in {"area", "band", "ridge", "branch"}:
        return f'<path d="M{x},{y+9} C{x+12},{y-12} {x+30},{y-12} {x+42},{y+9} Z" fill="{t["accent"]}" fill-opacity=".22" stroke="{t["accent"]}" stroke-width="2"/>'
    return f'<rect x="{x}" y="{y-12}" width="42" height="24" rx="7" fill="{t["panel"]}" stroke="{t["connector"]}" stroke-width="2"/>'


def type_legend(case_id: str, t: Mapping[str, str]) -> str:
    items = LEGEND_BY_CASE[case_id]
    starts = (68, 410, 752)
    parts = [
        f'<g class="type-legend" data-type-legend="true" data-legend-top="{LEGEND_TOP}" data-legend-bottom="{LEGEND_BOTTOM}">',
        f'<line x1="54" y1="{LEGEND_TOP}" x2="1386" y2="{LEGEND_TOP}" stroke="{t["grid"]}" stroke-width="1.5"/>',
        f'<text x="54" y="{LEGEND_TOP+34}" class="legend-heading">LEGEND</text>',
    ]
    for (kind, label), x in zip(items, starts):
        parts.append(_legend_mark(kind, x + 88, LEGEND_TOP + 31, t))
        parts.append(f'<text x="{x+144}" y="{LEGEND_TOP+37}" class="legend-label">{escape(label)}</text>')
    parts.append(f'<text x="1386" y="{LEGEND_TOP+82}" class="legend-insight" text-anchor="end">{escape(INTENT_BY_CASE[case_id])}</text>')
    parts.append("</g>")
    return "".join(parts)


def semantic_field_marker(profile: str) -> str:
    return (
        f'<rect x="28" y="{FIELD_TOP}" width="1384" height="{FIELD_BOTTOM-FIELD_TOP}" '
        f'fill="none" stroke="none" data-semantic-field="true" data-profile="{profile}"/>'
    )


__all__ = [
    "BODY_TRANSFORM",
    "CANVAS_HEIGHT",
    "CANVAS_WIDTH",
    "FIELD_BOTTOM",
    "FIELD_TOP",
    "INTENT_BY_CASE",
    "LEGEND_BOTTOM",
    "LEGEND_TOP",
    "PROFILE_BY_CASE",
    "estimate_text_width",
    "semantic_field_marker",
    "type_legend",
    "wrap_text",
]
