"""D-116 marker-free radar chart with five shared axes and four solid profiles."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_SERIES = (
    "series-internal-platform", "series-managed-service", "series-open-stack", "series-cloud-suite",
)
EXPECTED_AXES = (
    "axis-small-files", "axis-large-reads", "axis-write-throughput", "axis-operations", "axis-open-tables",
)
EXPECTED_DOMAINS = (
    "Xử lý tệp nhỏ", "Đọc đối tượng lớn", "Thông lượng ghi", "Vận hành đơn giản", "Tích hợp bảng mở",
)
EXPECTED_ANNOTATION = "annotation-recommended"
FOCAL_SERIES = "series-internal-platform"
TICKS = (2, 4, 6, 8, 10)
SERIES_STYLES = {
    "series-internal-platform": ("focal", "circle"),
    "series-managed-service": ("series-three", "square"),
    "series-open-stack": ("series-one", "triangle"),
    "series-cloud-suite": ("series-four", "diamond"),
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_radar(plan):
    contract = plan.get("semantic_projection", {}).get("quantitative_contract", {})
    return tuple(item.get("id") for item in contract.get("series", [])) == EXPECTED_SERIES


def _point(cx, cy, radius, angle):
    radians = math.radians(angle)
    return cx + math.cos(radians) * radius, cy + math.sin(radians) * radius


def layout_radar(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = contract["axes"]
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(tuple(item["id"] for item in axes) == EXPECTED_AXES, "D-114 requires five exact radar axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-114 requires four exact profiles")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-114 requires one recommendation annotation")
    _require(annotations[EXPECTED_ANNOTATION].get("target_ids") == [FOCAL_SERIES], "D-114 focal target mismatch")
    for item in axes:
        _require(
            item["dimension"] == "radial" and item["scale"] == "linear"
            and item.get("domain_min") == 0 and item.get("domain_max") == 10 and item.get("unit") == "điểm",
            "D-114 requires one truthful shared 0–10 scale",
        )
    width, height = 2000, 1040
    cx, cy, radius = 1000.0, 460.0, 300.0
    angles = tuple(-90.0 + index * 72.0 for index in range(5))
    axis_layout = []
    for axis_item, domain, angle in zip(axes, EXPECTED_DOMAINS, angles):
        _require(axis_item["label"] == domain, "D-114 axis label/order mismatch")
        x, y = _point(cx, cy, radius, angle)
        lx, ly = _point(cx, cy, radius + 90, angle)
        axis_layout.append({**axis_item, "angle": angle, "x": x, "y": y, "label_x": lx, "label_y": ly})
    profiles = []
    for series_item in series_items:
        data = series_item["data"]
        _require(len(data) == 5 and tuple(item["domain"] for item in data) == EXPECTED_DOMAINS, "D-114 profile criterion order mismatch")
        _require(all(not item.get("missing") and isinstance(item.get("value"), (int, float)) for item in data), "D-114 requires twenty numeric values")
        _require(all(math.isfinite(item["value"]) and 0 <= item["value"] <= 10 for item in data), "D-114 value outside shared domain")
        points = []
        for datum, angle in zip(data, angles):
            x, y = _point(cx, cy, radius * datum["value"] / 10.0, angle)
            points.append({**datum, "angle": angle, "x": x, "y": y})
        css, marker = SERIES_STYLES[series_item["id"]]
        profiles.append({**series_item, "points": points, "css": css, "marker": marker, "focal": series_item["id"] == FOCAL_SERIES})
    return {
        "width": width, "height": height, "cx": cx, "cy": cy, "radius": radius,
        "axes": axis_layout, "profiles": profiles, "ticks": TICKS,
    }


def radar_css(tokens):
    return """
    .rd-ring{fill:none;stroke:var(--grid);stroke-width:1.4;opacity:.88}
    .rd-spoke{stroke:var(--grid);stroke-width:1.4;opacity:.82}
    .rd-profile{stroke-width:3.2;stroke-linejoin:round;fill-opacity:.10}
    .rd-profile.focal{stroke:var(--accent);fill:var(--accent-soft);fill-opacity:.58;stroke-width:4.2}
    .rd-profile.series-three{stroke:var(--series-3);fill:var(--series-3)}
    .rd-profile.series-one{stroke:var(--series-1);fill:var(--series-1)}
    .rd-profile.series-four{stroke:var(--series-4);fill:var(--series-4)}
    .rd-marker{fill:var(--canvas);stroke-width:2.6}
    .rd-marker.focal{fill:var(--accent);stroke:var(--accent)}
    .rd-marker.series-three{stroke:var(--series-3)}.rd-marker.series-one{stroke:var(--series-1)}.rd-marker.series-four{stroke:var(--series-4)}
    .rd-axis-label{font:700 22px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .rd-tick,.rd-kicker,.rd-legend-label,.rd-note{font:700 14px Menlo,Monaco,monospace;fill:var(--muted)}
    .rd-kicker,.rd-note{letter-spacing:2px}.rd-tick{font-size:13px}.rd-legend-label{font-size:14px;fill:var(--connector)}
    .rd-rule{stroke:var(--grid);stroke-width:1.3}
    .rd-details{overflow-x:auto}.rd-details table{min-width:820px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _points(points):
    return " ".join(f'{point["x"]:.3f},{point["y"]:.3f}' for point in points)


def _marker(point, profile, size=8):
    attrs = (
        f'class="rd-marker {profile["css"]}" data-marker-series="{escape(profile["id"], quote=True)}" '
        f'data-datum-id="{escape(point["id"], quote=True)}" data-marker-shape="{profile["marker"]}" '
        f'data-value="{point["value"]}"'
    )
    x, y = point["x"], point["y"]
    if profile["marker"] == "circle":
        return f'<circle {attrs} cx="{x:.3f}" cy="{y:.3f}" r="{size}"/>'
    if profile["marker"] == "square":
        return f'<rect {attrs} x="{x-size:.3f}" y="{y-size:.3f}" width="{2*size}" height="{2*size}" rx="2"/>'
    if profile["marker"] == "triangle":
        return f'<polygon {attrs} points="{x:.3f},{y-size-1:.3f} {x-size-1:.3f},{y+size:.3f} {x+size+1:.3f},{y+size:.3f}"/>'
    return f'<polygon {attrs} points="{x:.3f},{y-size-2:.3f} {x+size+2:.3f},{y:.3f} {x:.3f},{y+size+2:.3f} {x-size-2:.3f},{y:.3f}"/>'


def render_radar(plan):
    layout = layout_radar(plan)
    cx, cy, radius = layout["cx"], layout["cy"], layout["radius"]
    parts = ['<g data-radar-contract="D-116-five-axis-four-solid-marker-free-profile">']
    parts.append(_text(106, 118, "ĐIỂM NĂNG LỰC · THANG CHUNG 0–10", "rd-kicker", "start"))
    for tick in layout["ticks"]:
        ring_points = []
        for axis_item in layout["axes"]:
            x, y = _point(cx, cy, radius * tick / 10.0, axis_item["angle"])
            ring_points.append({"x": x, "y": y})
        parts.append(f'<polygon class="rd-ring" data-ring-value="{tick}" points="{_points(ring_points)}"/>')
        tx, ty = _point(cx, cy, radius * tick / 10.0, -90)
        parts.append(_text(tx - 13, ty + 5, tick, "rd-tick", "end"))
    for axis_item in layout["axes"]:
        parts.append(
            f'<line class="rd-spoke" data-spoke-id="spoke-{escape(axis_item["id"], quote=True)}" '
            f'x1="{cx}" y1="{cy}" x2="{axis_item["x"]:.3f}" y2="{axis_item["y"]:.3f}"/>'
        )
        cosine = math.cos(math.radians(axis_item["angle"]))
        anchor = "start" if cosine > .35 else "end" if cosine < -.35 else "middle"
        label_y = axis_item["label_y"] - 14 if axis_item["angle"] == -90 else axis_item["label_y"] + 8
        parts.append(_text(axis_item["label_x"], label_y, axis_item["label"], "rd-axis-label", anchor))
    for profile in reversed(layout["profiles"]):
        parts.append(
            f'<polygon class="rd-profile {profile["css"]}" data-series-id="{escape(profile["id"], quote=True)}" '
            f'data-focal="{str(profile["focal"]).lower()}" data-marker-shape="{profile["marker"]}" '
            f'data-line-style="solid" points="{_points(profile["points"])}"/>'
        )
    parts.append('<line class="rd-rule" x1="106" y1="865" x2="1894" y2="865"/>')
    parts.append(_text(106, 906, "CHÚ GIẢI", "rd-kicker", "start"))
    legend_x = (250, 660, 1060, 1450)
    for x, profile in zip(legend_x, layout["profiles"]):
        sample = {"id": f'legend-{profile["id"]}', "x": x, "y": 940, "value": "legend"}
        parts.append(f'<line class="rd-profile {profile["css"]}" x1="{x-28}" y1="940" x2="{x+28}" y2="940"/>')
        parts.append(_marker(sample, profile, 6))
        label = profile["label"] + (" · KHUYẾN NGHỊ" if profile["focal"] else "")
        parts.append(_text(x + 45, 946, label, "rd-legend-label", "start"))
    parts.append(_text(1894, 1000, "Màu + chú giải · nét liền · không marker trong plot", "rd-note", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_radar_svg(svg):
    root = ET.fromstring(svg)
    rings = root.findall(".//*[@data-ring-value]")
    spokes = root.findall(".//*[@data-spoke-id]")
    profiles = root.findall(".//*[@data-series-id]")
    markers = root.findall(".//*[@data-marker-series]")
    _require(tuple(int(item.attrib["data-ring-value"]) for item in rings) == TICKS, "Serialized D-114 ring mismatch")
    _require(len(spokes) == 5 and len(profiles) == 4 and len(markers) == 4, "Serialized D-116 material count mismatch")
    _require(tuple(item.attrib["data-series-id"] for item in profiles) == tuple(reversed(EXPECTED_SERIES)), "Serialized D-114 profile order mismatch")
    focal = [item for item in profiles if item.attrib["data-focal"] == "true"]
    _require(len(focal) == 1 and focal[0].attrib["data-series-id"] == FOCAL_SERIES, "Serialized D-114 focal mismatch")
    chart_markers = [item for item in markers if not item.attrib["data-datum-id"].startswith("legend-")]
    _require(len(chart_markers) == 0, "D-116 forbids plotted radar markers")
    _require({item.attrib["data-marker-shape"] for item in profiles} == {"circle", "square", "triangle", "diamond"}, "D-114 non-color redundancy missing")
    _require(all(item.attrib.get("data-line-style") == "solid" for item in profiles), "D-115 requires solid lines for every radar profile")
    _require(all("marker-end" not in item.attrib for item in spokes), "D-114 radar axes must be arrow-free")
    return {"profiles": 4, "values": 20, "axes": 5, "rings": 5, "markers": 0, "focal": 1}


def radar_table(plan):
    layout = layout_radar(plan)
    rows = []
    for profile in layout["profiles"]:
        for point in profile["points"]:
            rows.append(
                "<tr>"
                f'<td>{escape(profile["label"])}</td><td>{escape(str(point["domain"]))}</td>'
                f'<td>{point["value"]}/10</td><td>{escape(profile["marker"])}</td>'
                f'<td>{"Khuyến nghị" if profile["focal"] else "So sánh"}</td>'
                "</tr>"
            )
    return (
        '<details class="rd-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Bốn hồ sơ dùng cùng năm tiêu chí và cùng miền tuyến tính 0–10. Hai mươi giá trị được lặp lại dưới dạng bảng; mọi profile dùng nét liền, không có marker trong vùng plot và được nhận diện bằng màu cùng chú giải trực tiếp.</p>'
        '<table><thead><tr><th scope="col">Phương án</th><th scope="col">Tiêu chí</th><th scope="col">Điểm</th>'
        '<th scope="col">Marker</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
