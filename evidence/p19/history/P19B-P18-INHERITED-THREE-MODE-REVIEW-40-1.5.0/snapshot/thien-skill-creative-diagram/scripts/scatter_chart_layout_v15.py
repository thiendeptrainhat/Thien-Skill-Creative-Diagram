"""D-113 content-fit deployment-performance scatter presentation variant."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_SERIES = "series-team-performance"
EXPECTED_AXES = {"axis-deploys", "axis-lead-time"}
EXPECTED_ANNOTATION = "annotation-platform-focal"
EXPECTED_POINTS = (
    "team-01", "team-02", "team-03", "team-04", "team-05", "team-06",
    "team-07", "team-08", "team-09", "team-10", "team-platform", "team-11",
)
FOCAL_POINT = "team-platform"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_scatter_chart(plan):
    series_items = plan.get("semantic_projection", {}).get("quantitative_contract", {}).get("series", [])
    return len(series_items) == 1 and series_items[0].get("id") == EXPECTED_SERIES


def _linear_regression(points):
    mean_x = sum(point["domain"] for point in points) / len(points)
    mean_y = sum(point["value"] for point in points) / len(points)
    denominator = sum((point["domain"] - mean_x) ** 2 for point in points)
    _require(denominator > 0, "D-113 regression requires x variance")
    slope = sum((point["domain"] - mean_x) * (point["value"] - mean_y) for point in points) / denominator
    return slope, mean_y - slope * mean_x


def layout_scatter_chart(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-113 requires exact deployment/lead-time axes")
    _require(len(series_items) == 1 and series_items[0]["id"] == EXPECTED_SERIES, "D-113 requires one team series")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-113 requires one platform annotation")
    x_axis, y_axis = axes["axis-deploys"], axes["axis-lead-time"]
    _require(x_axis["dimension"] == "x" and x_axis["scale"] == "linear" and x_axis.get("domain_min") == 0 and x_axis.get("domain_max") == 20, "D-113 x scale mismatch")
    _require(y_axis["dimension"] == "y" and y_axis["scale"] == "linear" and y_axis.get("domain_min") == 0 and y_axis.get("domain_max") == 24, "D-113 y scale mismatch")
    points = series_items[0]["data"]
    _require(tuple(point["id"] for point in points) == EXPECTED_POINTS, "D-113 point order mismatch")
    _require(all(not point.get("missing") and isinstance(point.get("domain"), (int, float)) and isinstance(point.get("value"), (int, float)) for point in points), "D-113 requires twelve numeric pairs")
    _require(all(math.isfinite(point["domain"]) and 0 <= point["domain"] <= 20 and math.isfinite(point["value"]) and 0 <= point["value"] <= 24 for point in points), "D-113 point outside axis domain")
    _require(annotations[EXPECTED_ANNOTATION].get("target_ids") == [FOCAL_POINT], "D-113 focal target mismatch")

    width, height = 2000, 1020
    left, right, top, bottom = 160, 1940, 80, 830
    rendered = []
    for point in points:
        rendered.append({
            **point,
            "x": left + point["domain"] / 20 * (right - left),
            "y": bottom - point["value"] / 24 * (bottom - top),
            "focal": point["id"] == FOCAL_POINT,
        })
    _require(sum(point["focal"] for point in rendered) == 1, "D-113 requires exactly one focal point")
    slope, intercept = _linear_regression(points)
    _require(slope < 0, "D-113 trend must descend")
    trend_domain = (2, 20)
    trend = []
    for domain in trend_domain:
        value = slope * domain + intercept
        trend.append({
            "domain": domain,
            "value": value,
            "x": left + domain / 20 * (right - left),
            "y": bottom - value / 24 * (bottom - top),
        })
    return {
        "width": width, "height": height,
        "left": left, "right": right, "top": top, "bottom": bottom,
        "axes": axes, "series": series_items[0], "annotation": annotations[EXPECTED_ANNOTATION],
        "points": rendered, "x_ticks": (0, 4, 8, 12, 16, 20), "y_ticks": (0, 6, 12, 18, 24),
        "trend": trend, "trend_slope": slope, "trend_intercept": intercept,
    }


def scatter_chart_css(tokens):
    return """
    .sc-grid{stroke:var(--grid);stroke-width:1;opacity:.55}
    .sc-axis{stroke:var(--border);stroke-width:1.35}
    .sc-trend{fill:none;stroke:var(--border);stroke-width:1.45;stroke-dasharray:9 8}
    .sc-point{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.8}
    .sc-point.is-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.2}
    .sc-tick,.sc-axis-title,.sc-guide,.sc-label,.sc-legend-title{font:600 16px Menlo,Monaco,monospace;fill:var(--connector)}
    .sc-axis-title,.sc-guide,.sc-legend-title{font-size:13px;letter-spacing:2px;fill:var(--muted)}
    .sc-guide{opacity:.52}.sc-label{font-size:14px;font-weight:700;letter-spacing:1px;fill:var(--accent-text)}
    .sc-legend-rule{stroke:var(--grid);stroke-width:1.2}
    .sc-legend-label{font:500 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}
    .sc-details{overflow-x:auto}.sc-details table{min-width:820px}
    """


def _text(x, y, value, css, anchor="middle", transform=""):
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}"{transform_attr}>{escape(str(value))}</text>'


def render_scatter_chart(plan):
    layout = layout_scatter_chart(plan)
    left, right, top, bottom = layout["left"], layout["right"], layout["top"], layout["bottom"]
    parts = ['<g data-scatter-chart-contract="D-113-twelve-team-linear-trend">']
    for tick in layout["x_ticks"]:
        x = left + tick / 20 * (right - left)
        parts.append(f'<line class="sc-grid" data-x-tick="{tick}" x1="{x:.3f}" y1="{top}" x2="{x:.3f}" y2="{bottom}"/>')
        parts.append(_text(x, bottom + 40, tick, "sc-tick"))
    for tick in layout["y_ticks"]:
        y = bottom - tick / 24 * (bottom - top)
        parts.append(f'<line class="sc-grid" data-y-tick="{tick}" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>')
        parts.append(_text(left - 18, y + 6, tick, "sc-tick", "end"))
    parts.append(f'<line class="sc-axis" data-axis-id="axis-deploys" data-zero-baseline="true" x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}"/>')
    parts.append(f'<line class="sc-axis" data-axis-id="axis-lead-time" data-zero-baseline="true" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>')
    parts.append(_text((left + right) / 2, bottom + 92, "SỐ LẦN TRIỂN KHAI MỖI TUẦN", "sc-axis-title"))
    parts.append(_text(48, (top + bottom) / 2, "LEAD TIME (NGÀY)", "sc-axis-title", "middle", f"rotate(-90 48 {(top + bottom) / 2:.3f})"))
    parts.append(_text(left + 16, top + 30, "LEAD TIME CAO", "sc-guide", "start"))
    parts.append(_text(left + 16, bottom - 18, "LEAD TIME THẤP", "sc-guide", "start"))
    a, b = layout["trend"]
    parts.append(f'<line class="sc-trend" data-trend="least-squares" data-slope="{layout["trend_slope"]:.12f}" data-intercept="{layout["trend_intercept"]:.12f}" x1="{a["x"]:.3f}" y1="{a["y"]:.3f}" x2="{b["x"]:.3f}" y2="{b["y"]:.3f}"/>')
    for point in layout["points"]:
        focal = " is-focal" if point["focal"] else ""
        parts.append(
            f'<circle class="sc-point{focal}" data-point-id="{escape(point["id"], quote=True)}" '
            f'data-domain="{point["domain"]}" data-value="{point["value"]}" data-focal="{str(point["focal"]).lower()}" '
            f'cx="{point["x"]:.3f}" cy="{point["y"]:.3f}" r="10"/>'
        )
        if point["focal"]:
            parts.append(_text(point["x"] - 26, point["y"] - 30, "NỀN TẢNG", "sc-label", "end"))
    legend_y = 980
    parts.append(f'<line class="sc-legend-rule" x1="74" y1="{legend_y-34}" x2="1926" y2="{legend_y-34}"/>')
    parts.append(_text(74, legend_y, "CHÚ GIẢI", "sc-legend-title", "start"))
    parts.append(f'<circle class="sc-point is-focal" cx="288" cy="{legend_y}" r="10"/>')
    parts.append(_text(312, legend_y + 6, "Nhóm nền tảng · hiệu suất tốt nhất", "sc-legend-label", "start"))
    parts.append(f'<circle class="sc-point" cx="836" cy="{legend_y}" r="10"/>')
    parts.append(_text(860, legend_y + 6, "Nhóm kỹ thuật", "sc-legend-label", "start"))
    parts.append(f'<line class="sc-trend" x1="1160" y1="{legend_y}" x2="1220" y2="{legend_y}"/>')
    parts.append(_text(1238, legend_y + 6, "Xu hướng", "sc-legend-label", "start"))
    parts.append(_text(1926, legend_y + 6, "12 nhóm · OLS", "sc-legend-title", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_scatter_chart_svg(svg):
    root = ET.fromstring(svg)
    points = root.findall(".//*[@data-point-id]")
    _require(len(points) == 12 and {item.attrib["data-point-id"] for item in points} == set(EXPECTED_POINTS), "Serialized D-113 point mismatch")
    _require(sum(item.attrib.get("data-focal") == "true" for item in points) == 1, "Serialized D-113 focal mismatch")
    axes = root.findall(".//*[@data-axis-id]")
    _require({item.attrib["data-axis-id"] for item in axes} == EXPECTED_AXES, "Serialized D-113 axes mismatch")
    _require(all("marker-end" not in item.attrib for item in axes), "D-113 axes must be arrow-free")
    _require(len(root.findall(".//*[@data-x-tick]")) == 6 and len(root.findall(".//*[@data-y-tick]")) == 5, "Serialized D-113 tick mismatch")
    trends = root.findall(".//*[@data-trend]")
    _require(len(trends) == 1 and float(trends[0].attrib["data-slope"]) < 0, "Serialized D-113 trend mismatch")
    return {"points": 12, "focal": 1, "axes": 2, "x_ticks": 6, "y_ticks": 5, "trends": 1}


def scatter_chart_table(plan):
    layout = layout_scatter_chart(plan)
    rows = []
    for point in layout["points"]:
        rows.append(
            "<tr>"
            f'<td>{escape(point["id"])}</td><td>{point["domain"]}</td><td>{point["value"]}</td>'
            f'<td>{"Nhóm nền tảng · trọng tâm" if point["focal"] else "Nhóm kỹ thuật"}</td>'
            "</tr>"
        )
    return (
        '<details class="sc-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        f'<p>Mười hai cặp số dùng thang tuyến tính x=0–20 lần/tuần và y=0–24 ngày. Đường xu hướng OLS có hệ số góc {layout["trend_slope"]:.6f}; điểm nền tảng được lặp lại bằng viền coral, nhãn trực tiếp và trạng thái trong bảng.</p>'
        '<table><thead><tr><th scope="col">Nhóm</th><th scope="col">Triển khai/tuần</th><th scope="col">Lead time (ngày)</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
