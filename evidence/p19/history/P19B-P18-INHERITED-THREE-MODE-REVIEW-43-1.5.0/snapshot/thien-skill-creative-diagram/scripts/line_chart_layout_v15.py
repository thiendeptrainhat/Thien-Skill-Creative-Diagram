"""D-096 content-fit line chart derived from quantitative semantic material."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_SERIES = (
    "series-organic-growth",
    "series-direct-growth",
    "series-referral-growth",
)
EXPECTED_AXES = {"axis-week", "axis-signups"}
EXPECTED_ANNOTATION = "annotation-organic-focal"
EXPECTED_DOMAINS = tuple(f"Tuần {index}" for index in range(1, 9))


def is_detailed_line_chart(plan):
    series_items = plan.get("semantic_projection", {}).get("quantitative_contract", {}).get("series", [])
    return tuple(item.get("id") for item in series_items) == EXPECTED_SERIES


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def layout_line_chart(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-096 requires exact week/value axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-096 requires exact ordered series")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-096 requires one focal-series annotation")
    x_axis, y_axis = axes["axis-week"], axes["axis-signups"]
    _require(x_axis["dimension"] == "x" and x_axis["scale"] == "ordinal", "D-096 x axis mismatch")
    _require(
        y_axis["dimension"] == "y" and y_axis["scale"] == "linear"
        and y_axis.get("domain_min") == 0 and y_axis.get("domain_max") == 240
        and y_axis.get("unit") == "lượt",
        "D-096 requires a truthful 0–240 lượt scale",
    )
    _require(annotations[EXPECTED_ANNOTATION].get("target_ids") == [EXPECTED_SERIES[0]], "D-096 focal target mismatch")

    width, height = 2000, 980
    left, right, top, bottom = 154, 1660, 72, 744
    x_step = (right - left) / 7
    rendered_series = []
    for series_index, item in enumerate(series_items):
        data = item["data"]
        _require(len(data) == 8, "D-096 requires eight points per series")
        _require(tuple(point["domain"] for point in data) == EXPECTED_DOMAINS, "D-096 week order mismatch")
        _require(len({point["id"] for point in data}) == 8, "D-096 point IDs must be unique within a series")
        _require(all(not point.get("missing") and isinstance(point.get("value"), (int, float)) for point in data), "D-096 requires 24 numeric values")
        _require(all(math.isfinite(point["value"]) and 0 <= point["value"] <= 240 for point in data), "D-096 value outside scale")
        points = []
        for index, point in enumerate(data):
            points.append({
                **point,
                "x": left + index * x_step,
                "y": bottom - point["value"] / 240 * (bottom - top),
                "series_id": item["id"],
                "series_label": item["label"],
                "series_index": series_index,
            })
        rendered_series.append({**item, "points": points, "focal": item["id"] == EXPECTED_SERIES[0]})
    _require(len({point["id"] for item in rendered_series for point in item["points"]}) == 24, "D-096 point IDs must be globally unique")
    return {
        "width": width, "height": height,
        "left": left, "right": right, "top": top, "bottom": bottom,
        "axes": axes, "series": rendered_series,
        "annotation": annotations[EXPECTED_ANNOTATION],
        "ticks": tuple(range(40, 241, 40)),
    }


def line_chart_css(tokens):
    return """
    .lc-grid{stroke:var(--grid);stroke-width:1.2;opacity:.62}
    .lc-axis{stroke:var(--border);stroke-width:1.8}
    .lc-area{fill:var(--accent-soft);opacity:.58;stroke:none}
    .lc-line{fill:none;stroke-width:3.2;stroke-linejoin:round;stroke-linecap:round}
    .lc-line.is-focal{stroke:var(--accent);stroke-width:4.2}
    .lc-line.is-direct{stroke:var(--series-3);stroke-dasharray:13 7}
    .lc-line.is-referral{stroke:var(--series-1);stroke-dasharray:3 8}
    .lc-marker{stroke-width:2.2}
    .lc-marker.is-focal{fill:var(--accent);stroke:var(--accent)}
    .lc-marker.is-direct{fill:var(--canvas);stroke:var(--series-3)}
    .lc-marker.is-referral{fill:var(--canvas);stroke:var(--series-1)}
    .lc-tick,.lc-category,.lc-value,.lc-axis-title{font:600 16px Menlo,Monaco,monospace;fill:var(--connector)}
    .lc-category{font-size:17px;fill:var(--text)}
    .lc-axis-title{font-size:14px;letter-spacing:2px;fill:var(--muted)}
    .lc-value{font-size:14px;font-weight:700}
    .lc-value.is-focal{fill:var(--accent-text)}.lc-value.is-direct{fill:var(--series-3)}.lc-value.is-referral{fill:var(--series-1)}
    .lc-legend-rule{stroke:var(--grid);stroke-width:1.3}
    .lc-legend-title{font:700 13px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}
    .lc-legend-label{font:600 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}
    .lc-details{overflow-x:auto}.lc-details table{min-width:820px}
    """


def _text(x, y, value, css, anchor="middle", transform=""):
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}"{transform_attr}>{escape(str(value))}</text>'


def _path(points):
    return " ".join(("M" if index == 0 else "L") + f"{point['x']:.3f} {point['y']:.3f}" for index, point in enumerate(points))


def _marker(point, role):
    attrs = (
        f'data-point-id="{escape(point["id"], quote=True)}" '
        f'data-series-id="{escape(point["series_id"], quote=True)}" '
        f'data-domain="{escape(str(point["domain"]), quote=True)}" data-value="{point["value"]}" '
        f'data-marker-shape="{role}"'
    )
    x, y = point["x"], point["y"]
    if role == "circle":
        return f'<circle class="lc-marker is-focal" {attrs} cx="{x:.3f}" cy="{y:.3f}" r="7"/>'
    if role == "square":
        return f'<rect class="lc-marker is-direct" {attrs} x="{x-6:.3f}" y="{y-6:.3f}" width="12" height="12" rx="2"/>'
    return f'<path class="lc-marker is-referral" {attrs} d="M{x:.3f} {y-7:.3f} L{x+7:.3f} {y:.3f} L{x:.3f} {y+7:.3f} L{x-7:.3f} {y:.3f} Z"/>'


def render_line_chart(plan):
    layout = layout_line_chart(plan)
    left, right, top, bottom = layout["left"], layout["right"], layout["top"], layout["bottom"]
    parts = ['<g data-line-chart-contract="D-096-three-series-eight-week">']
    for tick in layout["ticks"]:
        y = bottom - tick / 240 * (bottom - top)
        parts.append(f'<line class="lc-grid" data-tick="{tick}" x1="{left}" y1="{y:.3f}" x2="{right}" y2="{y:.3f}"/>')
        parts.append(_text(left - 18, y + 6, tick, "lc-tick", "end"))
    parts.append(f'<line class="lc-axis" data-axis-id="axis-signups" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>')
    parts.append(f'<line class="lc-axis" data-axis-id="axis-week" data-zero-baseline="true" x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}"/>')
    parts.append(_text(48, (top + bottom) / 2, "ĐĂNG KÝ / TUẦN", "lc-axis-title", "middle", f"rotate(-90 48 {(top + bottom) / 2:.3f})"))
    focal_points = layout["series"][0]["points"]
    area = _path(focal_points) + f" L{focal_points[-1]['x']:.3f} {bottom:.3f} L{focal_points[0]['x']:.3f} {bottom:.3f} Z"
    parts.append(f'<path class="lc-area" data-area-series-id="{EXPECTED_SERIES[0]}" d="{area}"/>')
    roles = ("circle", "square", "diamond")
    role_classes = ("is-focal", "is-direct", "is-referral")
    for index, item in enumerate(layout["series"]):
        points = item["points"]
        parts.append(
            f'<path class="lc-line {role_classes[index]}" data-line-series-id="{item["id"]}" '
            f'data-line-style="{("solid", "long-dash", "dot-dash")[index]}" data-marker-shape="{roles[index]}" d="{_path(points)}"/>'
        )
        parts.extend(_marker(point, roles[index]) for point in points)
        last = points[-1]
        y_offset = (-14, -6, 22)[index]
        parts.append(_text(last["x"] + 24, last["y"] + y_offset, f'{item["label"]} · {last["value"]}', f"lc-value {role_classes[index]}", "start"))
    for index, domain in enumerate(EXPECTED_DOMAINS):
        x = left + index * (right - left) / 7
        parts.append(_text(x, bottom + 42, domain.replace("Tuần ", "T"), "lc-category"))
    legend_y = 866
    parts.append(f'<line class="lc-legend-rule" x1="74" y1="{legend_y-30}" x2="1926" y2="{legend_y-30}"/>')
    parts.append(_text(74, legend_y, "CHÚ GIẢI", "lc-legend-title", "start"))
    legend_items = (
        (250, "is-focal", "circle", "Tăng trưởng tự nhiên · trọng tâm"),
        (820, "is-direct", "square", "Truy cập trực tiếp"),
        (1280, "is-referral", "diamond", "Nguồn giới thiệu"),
    )
    for x, css, shape, label in legend_items:
        dash = "" if shape == "circle" else (' stroke-dasharray="13 7"' if shape == "square" else ' stroke-dasharray="3 8"')
        parts.append(f'<line class="lc-line {css}" x1="{x}" y1="{legend_y+32}" x2="{x+56}" y2="{legend_y+32}"{dash}/>')
        marker_point = {"id": f"legend-{shape}", "series_id": f"legend-{shape}", "domain": "legend", "value": 0, "x": x + 28, "y": legend_y + 32}
        marker = _marker(marker_point, shape).replace("data-point-id=", "data-legend-marker-id=")
        parts.append(marker)
        parts.append(_text(x + 72, legend_y + 38, label, "lc-legend-label", "start"))
    parts.append(_text(1926, legend_y + 38, "Đơn vị · lượt", "lc-legend-title", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_line_chart_svg(svg):
    root = ET.fromstring(svg)
    lines = root.findall(".//*[@data-line-series-id]")
    _require(len(lines) == 3 and {item.attrib["data-line-series-id"] for item in lines} == set(EXPECTED_SERIES), "Serialized D-096 series mismatch")
    points = root.findall(".//*[@data-point-id]")
    _require(len(points) == 24 and len({item.attrib["data-point-id"] for item in points}) == 24, "Serialized D-096 point count mismatch")
    _require({item.attrib["data-marker-shape"] for item in points} == {"circle", "square", "diamond"}, "D-096 marker redundancy missing")
    _require({item.attrib["data-line-style"] for item in lines} == {"solid", "long-dash", "dot-dash"}, "D-096 line-style redundancy missing")
    axes = root.findall(".//*[@data-axis-id]")
    _require({item.attrib["data-axis-id"] for item in axes} == EXPECTED_AXES, "Serialized D-096 axes mismatch")
    _require(all("marker-end" not in item.attrib for item in axes), "D-096 axes must be arrow-free")
    _require(len(root.findall(".//*[@data-tick]")) == 6, "Serialized D-096 tick count mismatch")
    areas = root.findall(".//*[@data-area-series-id]")
    _require(len(areas) == 1 and areas[0].attrib["data-area-series-id"] == EXPECTED_SERIES[0], "D-096 focal area mismatch")
    return {"series": 3, "points": 24, "axes": 2, "ticks": 6, "focus_areas": 1}


def line_chart_table(plan):
    layout = layout_line_chart(plan)
    rows = []
    for item in layout["series"]:
        role = "Trọng tâm" if item["focal"] else "So sánh"
        for point in item["points"]:
            rows.append(
                "<tr>"
                f'<td>{escape(item["id"])}</td><td>{escape(item["label"])}</td>'
                f'<td>{escape(str(point["domain"]))}</td><td>{point["value"]}</td><td>{role}</td>'
                "</tr>"
            )
    return (
        '<details class="lc-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Ba chuỗi dùng chung thang tuyến tính 0–240 lượt. Chuỗi trọng tâm được lặp lại bằng vùng nhấn, đường liền và marker tròn; hai chuỗi so sánh dùng kiểu nét và marker khác nhau.</p>'
        '<table><thead><tr><th scope="col">Series ID</th><th scope="col">Chuỗi</th><th scope="col">Tuần</th>'
        '<th scope="col">Lượt</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
