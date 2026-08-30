"""D-098 content-fit polar chart with eight exact radial spokes."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_SERIES = "series-request-intensity"
EXPECTED_AXES = {"axis-utc-window", "axis-normalized-demand"}
EXPECTED_ANNOTATION = "annotation-peak-window"
EXPECTED_DOMAINS = ("00–03", "03–06", "06–09", "09–12", "12–15", "15–18", "18–21", "21–24")
EXPECTED_TICKS = (20, 40, 60, 80, 100)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_polar_chart(plan):
    items = plan.get("semantic_projection", {}).get("quantitative_contract", {}).get("series", [])
    return len(items) == 1 and items[0].get("id") == EXPECTED_SERIES


def layout_polar_chart(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    series_items = contract["series"]
    axes = {item["id"]: item for item in contract["axes"]}
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(len(series_items) == 1 and series_items[0]["id"] == EXPECTED_SERIES, "D-098 requires one exact series")
    _require(set(axes) == EXPECTED_AXES, "D-098 requires exact angular and radial axes")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-098 requires one peak annotation")
    angular, radial = axes["axis-utc-window"], axes["axis-normalized-demand"]
    _require(angular["dimension"] == "angular" and angular["scale"] == "categorical", "D-098 angular axis mismatch")
    _require(
        radial["dimension"] == "radial" and radial["scale"] == "linear"
        and radial.get("domain_min") == 0 and radial.get("domain_max") == 100 and radial.get("unit") == "%",
        "D-098 requires a truthful radial scale from 0 to 100 percent",
    )
    data = series_items[0]["data"]
    _require(len(data) == 8, "D-098 requires eight windows")
    _require(tuple(item["domain"] for item in data) == EXPECTED_DOMAINS, "D-098 UTC window order mismatch")
    _require(len({item["id"] for item in data}) == 8, "D-098 datum IDs must be unique")
    _require(all(not item.get("missing") and isinstance(item.get("value"), (int, float)) for item in data), "D-098 requires eight numeric values")
    _require(all(math.isfinite(item["value"]) and 0 <= item["value"] <= 100 for item in data), "D-098 value outside scale")
    maximum = max(item["value"] for item in data)
    peaks = [item for item in data if item["value"] == maximum]
    _require(maximum == 100 and len(peaks) == 1, "D-098 requires one unique 100-percent peak")
    peak = peaks[0]
    _require(annotations[EXPECTED_ANNOTATION].get("target_ids") == [peak["id"]], "D-098 peak target mismatch")

    width, height = 2000, 1020
    cx, cy, radius = 1060.0, 444.0, 276.0
    points = []
    for index, item in enumerate(data):
        angle = -90.0 + index * 45.0
        radians = math.radians(angle)
        value_radius = radius * item["value"] / 100.0
        label_radius = 350.0
        x, y = cx + math.cos(radians) * value_radius, cy + math.sin(radians) * value_radius
        lx, ly = cx + math.cos(radians) * label_radius, cy + math.sin(radians) * label_radius
        points.append({
            **item, "angle": angle, "x": x, "y": y, "label_x": lx, "label_y": ly,
            "state": "peak" if item["id"] == peak["id"] else "standard",
        })
    return {
        "width": width, "height": height, "cx": cx, "cy": cy, "radius": radius,
        "axes": axes, "series": series_items[0], "points": points,
        "annotation": annotations[EXPECTED_ANNOTATION], "ticks": EXPECTED_TICKS,
    }


def polar_chart_css(tokens):
    return """
    .pc-ring{fill:none;stroke:var(--grid);stroke-width:1.4;opacity:.82}
    .pc-guide{stroke:var(--grid);stroke-width:1.2;opacity:.7}
    .pc-spoke{stroke:var(--connector);stroke-width:3.4;stroke-linecap:round}
    .pc-spoke.is-peak{stroke:var(--accent);stroke-width:5.2}
    .pc-marker{fill:var(--canvas);stroke:var(--connector);stroke-width:2.3}
    .pc-marker.is-peak{stroke:var(--accent);stroke-width:3.2}
    .pc-center{fill:var(--connector)}
    .pc-tick,.pc-metric,.pc-value,.pc-note,.pc-peak-tag{font:700 14px Menlo,Monaco,monospace;fill:var(--connector)}
    .pc-tick{font-size:13px}.pc-metric,.pc-note{letter-spacing:2px;fill:var(--muted)}
    .pc-category{font:700 18px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .pc-value{font-size:15px}.pc-value.is-peak,.pc-peak-tag{fill:var(--accent-text)}
    .pc-peak-tag{font-size:12px;letter-spacing:1.5px}
    .pc-rule{stroke:var(--grid);stroke-width:1.3}
    .pc-details{overflow-x:auto}.pc-details table{min-width:760px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _label_anchor(angle):
    cosine = math.cos(math.radians(angle))
    if cosine > .35:
        return "start"
    if cosine < -.35:
        return "end"
    return "middle"


def render_polar_chart(plan):
    layout = layout_polar_chart(plan)
    cx, cy, radius = layout["cx"], layout["cy"], layout["radius"]
    parts = ['<g data-polar-chart-contract="D-098-eight-window-radial-spokes">']
    parts.append(_text(104, 132, "% SO VỚI ĐỈNH NGÀY · 0–100", "pc-metric", "start"))
    for tick in layout["ticks"]:
        r = radius * tick / 100
        parts.append(f'<circle class="pc-ring" data-radial-tick="{tick}" cx="{cx}" cy="{cy}" r="{r:.3f}"/>')
        parts.append(_text(cx - 12, cy - r + 5, tick, "pc-tick", "end"))
    for point in layout["points"]:
        angle = math.radians(point["angle"])
        gx, gy = cx + math.cos(angle) * radius, cy + math.sin(angle) * radius
        parts.append(
            f'<line class="pc-guide" data-angular-domain="{escape(str(point["domain"]), quote=True)}" '
            f'x1="{cx}" y1="{cy}" x2="{gx:.3f}" y2="{gy:.3f}"/>'
        )
    for point in layout["points"]:
        css = " is-peak" if point["state"] == "peak" else ""
        attrs = (
            f'data-spoke-id="spoke-{escape(point["id"], quote=True)}" '
            f'data-datum-id="{escape(point["id"], quote=True)}" data-domain="{escape(str(point["domain"]), quote=True)}" '
            f'data-value="{point["value"]}" data-state="{point["state"]}" data-angle="{point["angle"]:.3f}" '
            f'data-center-x="{cx}" data-center-y="{cy}" data-max-radius="{radius}"'
        )
        parts.append(f'<line class="pc-spoke{css}" {attrs} x1="{cx}" y1="{cy}" x2="{point["x"]:.3f}" y2="{point["y"]:.3f}"/>')
        parts.append(
            f'<circle class="pc-marker{css}" data-endpoint-id="endpoint-{escape(point["id"], quote=True)}" '
            f'data-datum-id="{escape(point["id"], quote=True)}" data-state="{point["state"]}" '
            f'cx="{point["x"]:.3f}" cy="{point["y"]:.3f}" r="8"/>'
        )
        anchor = _label_anchor(point["angle"])
        category_y = point["label_y"]
        value_y = category_y + 25
        if point["angle"] == -90:
            category_y -= 12; value_y = category_y - 25
        elif point["angle"] == 90:
            category_y += 12; value_y = category_y + 27
        parts.append(_text(point["label_x"], category_y, point["domain"], "pc-category", anchor))
        value_label = f'{point["value"]}%'
        if point["state"] == "peak":
            value_label += " · ĐỈNH"
        parts.append(_text(point["label_x"], value_y, value_label, f'pc-value{css}', anchor))
    parts.append(f'<circle class="pc-center" data-common-origin="true" cx="{cx}" cy="{cy}" r="5"/>')
    parts.append(f'<line class="pc-rule" x1="104" y1="900" x2="1896" y2="900"/>')
    parts.append(_text(104, 940, "HỒ SƠ CƯỜNG ĐỘ MINH HỌA · CHUẨN HÓA THEO ĐỈNH NGÀY", "pc-note", "start"))
    parts.append(_text(1896, 940, "ĐỈNH · 12–15 · 100%", "pc-peak-tag", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_polar_chart_svg(svg):
    root = ET.fromstring(svg)
    spokes = root.findall(".//*[@data-spoke-id]")
    endpoints = root.findall(".//*[@data-endpoint-id]")
    _require(len(spokes) == 8 and len(endpoints) == 8, "Serialized D-098 spoke/endpoint count mismatch")
    _require(len({item.attrib["data-datum-id"] for item in spokes}) == 8, "Serialized D-098 datum IDs mismatch")
    _require(tuple(item.attrib["data-domain"] for item in spokes) == EXPECTED_DOMAINS, "Serialized D-098 domain order mismatch")
    _require({int(item.attrib["data-radial-tick"]) for item in root.findall(".//*[@data-radial-tick]")} == set(EXPECTED_TICKS), "Serialized D-098 tick mismatch")
    peaks = [item for item in spokes if item.attrib["data-state"] == "peak"]
    _require(len(peaks) == 1 and float(peaks[0].attrib["data-value"]) == 100, "Serialized D-098 peak mismatch")
    _require(len([item for item in endpoints if item.attrib["data-state"] == "peak"]) == 1, "D-098 peak endpoint redundancy missing")
    for item in spokes:
        cx, cy = float(item.attrib["data-center-x"]), float(item.attrib["data-center-y"])
        angle = math.radians(float(item.attrib["data-angle"]))
        expected_radius = float(item.attrib["data-max-radius"]) * float(item.attrib["data-value"]) / 100
        expected_x, expected_y = cx + math.cos(angle) * expected_radius, cy + math.sin(angle) * expected_radius
        _require(abs(float(item.attrib["x1"]) - cx) < .001 and abs(float(item.attrib["y1"]) - cy) < .001, "D-098 spokes must share one origin")
        _require(abs(float(item.attrib["x2"]) - expected_x) < .01 and abs(float(item.attrib["y2"]) - expected_y) < .01, "D-098 radial geometry mismatch")
        _require("marker-end" not in item.attrib, "D-098 spokes must be arrow-free")
    _require(not root.findall(".//path[@data-spoke-id]"), "D-098 forbids filled wedge spokes")
    return {"series": 1, "spokes": 8, "endpoints": 8, "rings": 5, "peak": 1, "axes": 2}


def polar_chart_table(plan):
    layout = layout_polar_chart(plan)
    rows = []
    for point in layout["points"]:
        role = "Đỉnh ngày" if point["state"] == "peak" else "Cửa sổ so sánh"
        rows.append(
            "<tr>"
            f'<td>{escape(point["id"])}</td><td>{escape(str(point["domain"]))}</td>'
            f'<td>{point["value"]}%</td><td>{role}</td>'
            "</tr>"
        )
    return (
        '<details class="pc-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Tám cửa sổ UTC dùng chung thang xuyên tâm tuyến tính 0–100%. Đỉnh duy nhất được lặp lại bằng màu, độ dày nét, marker viền và nhãn chữ “ĐỈNH”.</p>'
        '<table><thead><tr><th scope="col">Datum ID</th><th scope="col">Cửa sổ UTC</th>'
        '<th scope="col">So với đỉnh ngày</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
