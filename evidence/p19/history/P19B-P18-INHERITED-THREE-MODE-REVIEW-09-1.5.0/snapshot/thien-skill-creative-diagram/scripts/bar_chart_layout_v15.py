"""D-088 content-fit bar chart derived from quantitative semantic material."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_POINTS = tuple(f"sprint-{index:02d}" for index in range(1, 9))
EXPECTED_AXES = {"axis-sprint", "axis-story-points"}
EXPECTED_SERIES = "series-sprint-points"
EXPECTED_ANNOTATION = "annotation-record-high"


def is_detailed_bar_chart(plan):
    contract = plan.get("semantic_projection", {}).get("quantitative_contract", {})
    series = contract.get("series", [])
    return len(series) == 1 and series[0].get("id") == EXPECTED_SERIES


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def layout_bar_chart(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-088 requires exact categorical/value axes")
    _require(len(series) == 1 and series[0]["id"] == EXPECTED_SERIES, "D-088 requires one sprint series")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-088 requires one record-high annotation")
    x_axis, y_axis = axes["axis-sprint"], axes["axis-story-points"]
    _require(x_axis["dimension"] == "x" and x_axis["scale"] == "categorical", "D-088 x axis mismatch")
    _require(
        y_axis["dimension"] == "y" and y_axis["scale"] == "linear"
        and y_axis.get("domain_min") == 0 and y_axis.get("domain_max") == 120
        and y_axis.get("unit") == "điểm",
        "D-088 requires a truthful 0–120 point scale",
    )
    points = series[0]["data"]
    _require(tuple(point["id"] for point in points) == EXPECTED_POINTS, "D-088 sprint order mismatch")
    _require(all(not point.get("missing") and isinstance(point.get("value"), (int, float)) for point in points), "D-088 requires eight numeric values")
    _require(all(math.isfinite(point["value"]) and 0 <= point["value"] <= 120 for point in points), "D-088 value outside scale")
    targets = annotations[EXPECTED_ANNOTATION].get("target_ids", [])
    _require(targets == ["sprint-05"], "D-088 focal target mismatch")
    maximum = max(point["value"] for point in points)
    _require(next(point["value"] for point in points if point["id"] == "sprint-05") == maximum, "D-088 focal must be the record high")

    width, height = 1800, 940
    left, right, top, bottom = 148, 1740, 74, 748
    slot = (right - left) / len(points)
    bar_width = 132
    rendered = []
    for index, point in enumerate(points):
        x = left + slot * index + (slot - bar_width) / 2
        y = bottom - point["value"] / 120 * (bottom - top)
        rendered.append({**point, "x": x, "y": y, "width": bar_width, "height": bottom - y, "focal": point["id"] == "sprint-05"})
    return {
        "width": width, "height": height,
        "left": left, "right": right, "top": top, "bottom": bottom,
        "axes": axes, "series": series[0], "annotation": annotations[EXPECTED_ANNOTATION],
        "points": rendered, "ticks": tuple(range(20, 121, 20)),
    }


def bar_chart_css(tokens):
    def blend(a, b, share):
        return "#" + "".join(
            f"{round(int(a[index:index+2], 16) * share + int(b[index:index+2], 16) * (1-share)):02x}"
            for index in (1, 3, 5)
        )
    neutral_fill = blend(tokens["connector"], tokens["canvas"], .16)
    return f"""
    .bar-chart-grid{{stroke:var(--grid);stroke-width:1.2;opacity:.58}}
    .bar-chart-axis{{stroke:var(--border);stroke-width:1.7}}
    .bar-chart-bar{{fill:{neutral_fill};stroke:var(--connector);stroke-width:2.2}}
    .bar-chart-bar.is-focal{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.5}}
    .bar-chart-tick,.bar-chart-value,.bar-chart-category,.bar-chart-axis-title{{font:600 17px Menlo,Monaco,monospace;fill:var(--connector)}}
    .bar-chart-category{{font:650 20px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}}
    .bar-chart-value{{font-size:16px}}
    .bar-chart-value.is-focal,.bar-chart-category.is-focal{{fill:var(--accent-text);font-weight:700}}
    .bar-chart-axis-title{{font-size:14px;letter-spacing:2px;fill:var(--muted)}}
    .bar-chart-legend-rule{{stroke:var(--grid);stroke-width:1.3}}
    .bar-chart-legend-label{{font:500 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}}
    .bar-chart-legend-title{{font:700 13px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}}
    .bar-chart-details{{overflow-x:auto}}.bar-chart-details table{{min-width:760px}}
    """


def _text(x, y, value, css, anchor="middle", transform=""):
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}"{transform_attr}>{escape(str(value))}</text>'


def render_bar_chart(plan):
    layout = layout_bar_chart(plan)
    left, right, top, bottom = layout["left"], layout["right"], layout["top"], layout["bottom"]
    parts = ['<g data-bar-chart-contract="D-088-eight-category-zero-baseline">']
    for tick in layout["ticks"]:
        y = bottom - tick / 120 * (bottom - top)
        parts.append(f'<line class="bar-chart-grid" data-tick="{tick}" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>')
        parts.append(_text(left - 18, y + 6, tick, "bar-chart-tick", "end"))
    parts.append(f'<line class="bar-chart-axis" data-axis-id="axis-story-points" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>')
    parts.append(f'<line class="bar-chart-axis" data-axis-id="axis-sprint" data-zero-baseline="true" x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}"/>')
    parts.append(_text(48, (top + bottom) / 2, "ĐIỂM HOÀN THÀNH", "bar-chart-axis-title", "middle", f"rotate(-90 48 {(top + bottom) / 2:.3f})"))
    for point in layout["points"]:
        focal = " is-focal" if point["focal"] else ""
        attrs = (
            f'data-bar-id="{escape(point["id"], quote=True)}" '
            f'data-domain="{escape(str(point["domain"]), quote=True)}" '
            f'data-value="{point["value"]}" data-focal="{str(point["focal"]).lower()}"'
        )
        parts.append(
            f'<rect class="bar-chart-bar{focal}" {attrs} x="{point["x"]:.3f}" y="{point["y"]:.3f}" '
            f'width="{point["width"]}" height="{point["height"]:.3f}"/>'
        )
        parts.append(_text(point["x"] + point["width"] / 2, point["y"] - 16, point["value"], f"bar-chart-value{focal}"))
        parts.append(_text(point["x"] + point["width"] / 2, bottom + 43, point["domain"], f"bar-chart-category{focal}"))
    legend_y = 842
    parts.append(f'<line class="bar-chart-legend-rule" x1="74" y1="{legend_y-28}" x2="1726" y2="{legend_y-28}"/>')
    parts.append(_text(74, legend_y, "CHÚ GIẢI", "bar-chart-legend-title", "start"))
    parts.append(f'<rect class="bar-chart-bar is-focal" x="74" y="{legend_y+24}" width="34" height="24" rx="5"/>')
    parts.append(_text(124, legend_y + 43, "Sprint 5 · kỷ lục 108 điểm", "bar-chart-legend-label", "start"))
    parts.append(f'<rect class="bar-chart-bar" x="442" y="{legend_y+24}" width="34" height="24" rx="5"/>')
    parts.append(_text(492, legend_y + 43, "Các sprint còn lại", "bar-chart-legend-label", "start"))
    parts.append(_text(1726, legend_y + 43, "Đơn vị · điểm", "bar-chart-legend-title", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_bar_chart_svg(svg):
    root = ET.fromstring(svg)
    bars = root.findall(".//*[@data-bar-id]")
    _require(len(bars) == 8, "Serialized D-088 bar count mismatch")
    _require({item.attrib["data-bar-id"] for item in bars} == set(EXPECTED_POINTS), "Serialized D-088 point IDs mismatch")
    _require(sum(item.attrib.get("data-focal") == "true" for item in bars) == 1, "Serialized D-088 focal count mismatch")
    axes = root.findall(".//*[@data-axis-id]")
    _require({item.attrib["data-axis-id"] for item in axes} == EXPECTED_AXES, "Serialized D-088 axes mismatch")
    baseline = next(item for item in axes if item.attrib["data-axis-id"] == "axis-sprint")
    _require(baseline.attrib.get("data-zero-baseline") == "true" and "marker-end" not in baseline.attrib, "D-088 baseline must be truthful and arrow-free")
    _require(len(root.findall(".//*[@data-tick]")) == 6, "Serialized D-088 tick count mismatch")
    return {"bars": 8, "focal": 1, "axes": 2, "ticks": 6}


def bar_chart_table(plan):
    layout = layout_bar_chart(plan)
    rows = []
    for point in layout["points"]:
        status = "Kỷ lục cao nhất" if point["focal"] else "Sprint khác"
        rows.append(
            "<tr>"
            f'<td>{escape(point["id"])}</td><td>{escape(str(point["domain"]))}</td>'
            f'<td>{point["value"]}</td><td>{escape(status)}</td>'
            "</tr>"
        )
    return (
        '<details class="bar-chart-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Thang tuyến tính 0–120 điểm; cột dùng chung zero-baseline. Màu cam được lặp lại bằng nhãn trực tiếp và trạng thái trong bảng.</p>'
        '<table><thead><tr><th scope="col">Semantic ID</th><th scope="col">Sprint</th>'
        '<th scope="col">Điểm</th><th scope="col">Trạng thái</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
