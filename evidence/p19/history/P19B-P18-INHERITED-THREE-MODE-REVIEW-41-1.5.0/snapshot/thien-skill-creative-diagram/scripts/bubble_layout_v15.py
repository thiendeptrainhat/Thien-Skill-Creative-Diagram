"""D-120 content-fit Bubble capability with area-faithful size encoding."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_AXES = {"axis-bubble-revenue", "axis-bubble-growth", "axis-bubble-share"}
EXPECTED_SERIES = ("series-core", "series-growth", "series-mature")
EXPECTED_POINTS = (
    "bubble-platform", "bubble-mobile", "bubble-enterprise", "bubble-data",
    "bubble-partner", "bubble-retail", "bubble-labs",
)
FOCAL_POINT = "bubble-platform"
POINT_LABELS = {
    "bubble-platform": "Nền tảng",
    "bubble-mobile": "Di động",
    "bubble-enterprise": "Doanh nghiệp",
    "bubble-data": "Dữ liệu",
    "bubble-partner": "Đối tác",
    "bubble-retail": "Bán lẻ",
    "bubble-labs": "Thử nghiệm",
}
SERIES_CLASS = {"series-core": "core", "series-growth": "growth", "series-mature": "mature"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_bubble(plan):
    adapter = plan.get("adapter", {})
    series_items = plan.get("semantic_projection", {}).get("quantitative_contract", {}).get("series", [])
    return adapter.get("capability_id") == "CAP-V20" and tuple(item.get("id") for item in series_items) == EXPECTED_SERIES


def layout_bubble(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-120 requires exact Bubble axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-120 requires exact Bubble series")
    _require(set(annotations) == {"annotation-bubble-focal"}, "D-120 requires one focal annotation")
    x_axis = axes["axis-bubble-revenue"]
    y_axis = axes["axis-bubble-growth"]
    size_axis = axes["axis-bubble-share"]
    _require((x_axis["dimension"], x_axis["scale"], x_axis.get("domain_min"), x_axis.get("domain_max")) == ("x", "linear", 0, 1400), "D-120 x-axis mismatch")
    _require((y_axis["dimension"], y_axis["scale"], y_axis.get("domain_min"), y_axis.get("domain_max")) == ("y", "linear", 0, 160), "D-120 y-axis mismatch")
    _require((size_axis["dimension"], size_axis["scale"], size_axis.get("domain_min"), size_axis.get("domain_max")) == ("size", "linear", 0, 80), "D-120 size-axis mismatch")
    _require(annotations["annotation-bubble-focal"].get("target_ids") == [FOCAL_POINT], "D-120 focal target mismatch")

    series_by_point = {}
    for item in series_items:
        for point in item["data"]:
            series_by_point[point["id"]] = item["id"]
    points = contract["bubble_points"]
    _require(tuple(point["id"] for point in points) == EXPECTED_POINTS, "D-120 point order mismatch")
    _require(set(series_by_point) == set(EXPECTED_POINTS), "D-120 series membership mismatch")
    _require(all(math.isfinite(point["x"]) and 0 <= point["x"] <= 1400 for point in points), "D-120 x value outside domain")
    _require(all(math.isfinite(point["y"]) and 0 <= point["y"] <= 160 for point in points), "D-120 y value outside domain")
    _require(all(math.isfinite(point["area_value"]) and 0 < point["area_value"] <= 80 for point in points), "D-120 area value outside domain")

    width, height = 2000, 1040
    left, right, top, bottom = 170, 1930, 80, 820
    max_radius = 68.0
    rendered = []
    for point in points:
        radius = max_radius * math.sqrt(point["area_value"] / 80)
        rendered.append({
            **point,
            "label": POINT_LABELS[point["id"]],
            "series_id": series_by_point[point["id"]],
            "series_class": SERIES_CLASS[series_by_point[point["id"]]],
            "x_pos": left + point["x"] / 1400 * (right - left),
            "y_pos": bottom - point["y"] / 160 * (bottom - top),
            "radius": radius,
            "focal": point["id"] == FOCAL_POINT,
        })
    _require(sum(point["focal"] for point in rendered) == 1, "D-120 requires exactly one focal bubble")
    ratio = {round(point["radius"] ** 2 / point["area_value"], 12) for point in rendered}
    _require(len(ratio) == 1, "D-120 bubble area scale must be constant")
    return {
        "width": width, "height": height,
        "left": left, "right": right, "top": top, "bottom": bottom,
        "axes": axes, "series": series_items, "annotation": annotations["annotation-bubble-focal"],
        "points": rendered,
        "x_ticks": tuple(range(0, 1401, 200)),
        "y_ticks": tuple(range(0, 161, 20)),
        "area_scale_factor": next(iter(ratio)),
    }


def bubble_css(tokens):
    return """
    .bc-grid{stroke:var(--grid);stroke-width:.85;opacity:.58}
    .bc-axis{stroke:var(--border);stroke-width:1.15}
    .bc-bubble{stroke:var(--connector);stroke-width:1.15;fill:var(--series-1);fill-opacity:.18}
    .bc-bubble.growth{fill:var(--series-3);fill-opacity:.30;stroke:var(--series-3)}
    .bc-bubble.mature{fill:var(--series-4);fill-opacity:.30;stroke:var(--series-4)}
    .bc-bubble.is-focal{fill:var(--accent-soft);fill-opacity:1;stroke:var(--accent);stroke-width:1.8}
    .bc-tick,.bc-axis-title,.bc-guide,.bc-value,.bc-direct,.bc-legend-title{font:600 15px Menlo,Monaco,monospace;fill:var(--connector)}
    .bc-axis-title,.bc-guide,.bc-legend-title{font-size:13px;letter-spacing:2px;fill:var(--muted)}
    .bc-value{font-size:15px;font-weight:750;fill:var(--text)}
    .bc-direct{font-size:13px;font-weight:750;letter-spacing:1.4px;fill:var(--accent-text)}
    .bc-legend-rule{stroke:var(--grid);stroke-width:1}
    .bc-legend-label{font:500 16px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}
    .bc-details{overflow-x:auto}.bc-details table{min-width:900px}
    """


def _text(x, y, value, css, anchor="middle", transform=""):
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}"{transform_attr}>{escape(str(value))}</text>'


def render_bubble(plan):
    layout = layout_bubble(plan)
    left, right, top, bottom = layout["left"], layout["right"], layout["top"], layout["bottom"]
    parts = ['<g data-bubble-contract="D-120-seven-point-area-faithful" data-template-contract="p18r6-review17-preserved">']
    for tick in layout["x_ticks"]:
        x = left + tick / 1400 * (right - left)
        parts.append(f'<line class="bc-grid" data-bubble-x-tick="{tick}" x1="{x:.3f}" y1="{top}" x2="{x:.3f}" y2="{bottom}"/>')
        parts.append(_text(x, bottom + 39, tick, "bc-tick"))
    for tick in layout["y_ticks"]:
        y = bottom - tick / 160 * (bottom - top)
        parts.append(f'<line class="bc-grid" data-bubble-y-tick="{tick}" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>')
        parts.append(_text(left - 18, y + 6, tick, "bc-tick", "end"))
    parts.append(f'<line class="bc-axis" data-bubble-axis="x" x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}"/>')
    parts.append(f'<line class="bc-axis" data-bubble-axis="y" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>')
    parts.append(_text((left + right) / 2, bottom + 92, "DOANH THU (TỶ ĐỒNG)", "bc-axis-title"))
    parts.append(_text(48, (top + bottom) / 2, "TĂNG TRƯỞNG LỢI NHUẬN (%)", "bc-axis-title", "middle", f"rotate(-90 48 {(top + bottom) / 2:.3f})"))
    parts.append(_text(left + 16, top + 28, "DIỆN TÍCH = THỊ PHẦN TƯƠNG ĐỐI", "bc-guide", "start"))
    for point in layout["points"]:
        focal = " is-focal" if point["focal"] else ""
        parts.append(
            f'<circle class="bc-bubble {point["series_class"]}{focal}" data-bubble-id="{escape(point["id"], quote=True)}" '
            f'data-x-value="{point["x"]}" data-y-value="{point["y"]}" data-area-value="{point["area_value"]}" '
            f'data-area-unit="{escape(point["area_unit"], quote=True)}" data-rendered-radius="{point["radius"]:.6f}" '
            f'data-series-id="{point["series_id"]}" data-focal="{str(point["focal"]).lower()}" '
            f'cx="{point["x_pos"]:.3f}" cy="{point["y_pos"]:.3f}" r="{point["radius"]:.6f}"/>'
        )
        parts.append(_text(point["x_pos"], point["y_pos"] + 6, int(point["area_value"]), "bc-value"))
        if point["focal"]:
            parts.append(_text(point["x_pos"], point["y_pos"] - point["radius"] - 18, "NỀN TẢNG", "bc-direct"))
    legend_y = 985
    parts.append(f'<line class="bc-legend-rule" x1="74" y1="{legend_y-40}" x2="1926" y2="{legend_y-40}"/>')
    parts.append(_text(74, legend_y, "CHÚ GIẢI", "bc-legend-title", "start"))
    legend = (("core", "Sản phẩm lõi", 290), ("growth", "Động lực tăng trưởng", 680), ("mature", "Danh mục ổn định", 1130))
    for css, label, x in legend:
        parts.append(f'<circle class="bc-bubble {css}" cx="{x}" cy="{legend_y-5}" r="12"/>')
        parts.append(_text(x + 28, legend_y + 1, label, "bc-legend-label", "start"))
    parts.append(f'<circle class="bc-bubble core is-focal" cx="1645" cy="{legend_y-5}" r="12"/>')
    parts.append(_text(1673, legend_y + 1, "Trọng tâm", "bc-legend-label", "start"))
    parts.append("</g>")
    return "".join(parts)


def validate_bubble_svg(svg):
    root = ET.fromstring(svg)
    bubbles = root.findall(".//*[@data-bubble-id]")
    _require(len(bubbles) == 7 and tuple(item.attrib["data-bubble-id"] for item in bubbles) == EXPECTED_POINTS, "Serialized D-120 bubble mismatch")
    _require(sum(item.attrib.get("data-focal") == "true" for item in bubbles) == 1, "Serialized D-120 focal mismatch")
    _require(len(root.findall(".//*[@data-bubble-axis]")) == 2, "Serialized D-120 axis mismatch")
    _require(all("marker-end" not in item.attrib and "marker-start" not in item.attrib for item in root.findall(".//*[@data-bubble-axis]")), "D-120 axes must be arrow-free")
    _require(len(root.findall(".//*[@data-bubble-x-tick]")) == 8 and len(root.findall(".//*[@data-bubble-y-tick]")) == 9, "Serialized D-120 tick mismatch")
    ratios = {round(float(item.attrib["data-rendered-radius"]) ** 2 / float(item.attrib["data-area-value"]), 5) for item in bubbles}
    _require(len(ratios) == 1, "Serialized D-120 area/radius relationship mismatch")
    return {"bubbles": 7, "focal": 1, "axes": 2, "x_ticks": 8, "y_ticks": 9, "area_scale_constant": next(iter(ratios))}


def bubble_table(plan):
    layout = layout_bubble(plan)
    rows = []
    series_labels = {item["id"]: item["label"] for item in layout["series"]}
    for point in layout["points"]:
        rows.append(
            "<tr>"
            f'<td>{escape(point["label"])}</td><td>{point["x"]}</td><td>{point["y"]}</td><td>{point["area_value"]}</td>'
            f'<td>{escape(series_labels[point["series_id"]])}</td><td>{"Trọng tâm" if point["focal"] else "Quan sát"}</td>'
            "</tr>"
        )
    return (
        '<details class="bc-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Bảy quan sát dùng chung trục x=0–1.400 tỷ đồng và y=0–160%. Bán kính hiển thị bằng căn bậc hai của giá trị thị phần, vì vậy diện tích — không phải bán kính — tỷ lệ trực tiếp với magnitude.</p>'
        '<table><thead><tr><th scope="col">Sản phẩm</th><th scope="col">Doanh thu</th><th scope="col">Tăng trưởng</th><th scope="col">Thị phần</th><th scope="col">Nhóm</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
