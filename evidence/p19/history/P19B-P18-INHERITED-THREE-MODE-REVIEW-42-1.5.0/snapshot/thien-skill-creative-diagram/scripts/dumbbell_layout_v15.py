"""D-122 detailed shared-scale dumbbell layout with direct gaps and statistics."""
from __future__ import annotations

from html import escape
import math
import statistics
import xml.etree.ElementTree as ET


EXPECTED_SERIES = ("series-before", "series-after")
EXPECTED_AXES = {"axis-dumbbell-category", "axis-dumbbell-value"}
EXPECTED_CATEGORIES = (
    "Nền tảng", "Thanh toán", "Dữ liệu", "Di động", "Đối tác", "Bán lẻ",
    "Tìm kiếm", "Hỗ trợ", "Nhận diện", "Vận hành", "Nội dung", "Phân tích",
)
FOCAL_CATEGORY = "Nền tảng"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_dumbbell(plan):
    contract = plan.get("semantic_projection", {}).get("quantitative_contract", {})
    series_items = contract.get("series", [])
    return (
        tuple(item.get("id") for item in series_items) == EXPECTED_SERIES
        and tuple(point.get("domain") for point in series_items[0].get("data", [])) == EXPECTED_CATEGORIES
    ) if series_items else False


def layout_dumbbell(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-122 requires exact category/value axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-122 requires exact before/after series")
    _require(set(annotations) == {"annotation-dumbbell-focal"}, "D-122 requires one focal annotation")
    value_axis = axes["axis-dumbbell-value"]
    _require(
        value_axis["scale"] == "linear" and value_axis.get("domain_min") == 0
        and value_axis.get("domain_max") == 100 and value_axis.get("unit") == "%",
        "D-122 requires a truthful shared 0–100% scale",
    )
    before_data, after_data = series_items[0]["data"], series_items[1]["data"]
    _require(len(before_data) == len(after_data) == 12, "D-122 requires twelve category pairs")
    _require(tuple(point["domain"] for point in before_data) == EXPECTED_CATEGORIES, "D-122 category order drift")
    _require(tuple(point["domain"] for point in after_data) == EXPECTED_CATEGORIES, "D-122 category mismatch")

    width, height = 2000, 1160
    x_left, x_right, top, row_step, axis_y = 430, 1820, 160, 62, 920
    scale = (x_right - x_left) / 100
    rows = []
    for index, (before, after) in enumerate(zip(before_data, after_data)):
        _require(not before.get("missing") and not after.get("missing"), "D-122 missing endpoint")
        _require(isinstance(before.get("value"), (int, float)) and isinstance(after.get("value"), (int, float)), "D-122 non-numeric endpoint")
        _require(math.isfinite(before["value"]) and math.isfinite(after["value"]), "D-122 non-finite endpoint")
        _require(0 <= before["value"] <= 100 and 0 <= after["value"] <= 100, "D-122 endpoint outside scale")
        _require(after["value"] >= before["value"], "D-122 active comparison requires non-negative gaps")
        y = top + index * row_step
        rows.append({
            "id": before["id"].removeprefix("before-"),
            "label": before["domain"],
            "before": before["value"],
            "after": after["value"],
            "delta": after["value"] - before["value"],
            "x_before": x_left + before["value"] * scale,
            "x_after": x_left + after["value"] * scale,
            "y": y,
            "focal": before["domain"] == FOCAL_CATEGORY,
        })
    _require(sum(item["focal"] for item in rows) == 1, "D-122 requires one focal category")
    stats = {}
    for key in ("before", "after"):
        values = [item[key] for item in rows]
        mean = statistics.fmean(values)
        deviation = statistics.pstdev(values)
        stats[key] = {
            "mean": mean,
            "stdev": deviation,
            "x_min": x_left + (mean - deviation) * scale,
            "x_max": x_left + (mean + deviation) * scale,
            "x_mean": x_left + mean * scale,
        }
    return {
        "width": width, "height": height, "x_left": x_left, "x_right": x_right,
        "top": top, "axis_y": axis_y, "rows": rows, "stats": stats,
        "ticks": tuple(range(0, 101, 20)),
    }


def dumbbell_css(tokens):
    return """
    .db-band{stroke:none;opacity:.09}.db-band.before{fill:var(--series-1)}.db-band.after{fill:var(--accent)}
    .db-band-swatch{fill:var(--accent);stroke:var(--accent);stroke-width:1;opacity:.18}
    .db-grid{stroke:var(--grid);stroke-width:1;opacity:.7}.db-axis{stroke:var(--border);stroke-width:1.2}
    .db-mean{stroke-width:1.4}.db-mean.before{stroke:var(--series-1)}.db-mean.after{stroke:var(--accent)}
    .db-link{stroke:var(--border);stroke-width:8;stroke-linecap:round}.db-link.focal{stroke:var(--accent-soft);stroke-width:10}
    .db-point{stroke-width:1.8}.db-point.before{fill:var(--surface);stroke:var(--series-1)}
    .db-point.after{fill:var(--accent);stroke:var(--accent)}.db-point.focal{stroke-width:2.8}
    .db-row,.db-value,.db-delta{font:650 16px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .db-row{font-size:17px}.db-row.focal,.db-delta.focal{fill:var(--accent-text);font-weight:750}
    .db-value{font:650 14px Menlo,Monaco,monospace;fill:var(--connector)}
    .db-delta{font:700 13px Menlo,Monaco,monospace;fill:var(--muted)}
    .db-tick,.db-axis-title,.db-stat,.db-legend{font:650 13px Menlo,Monaco,monospace;fill:var(--muted)}
    .db-axis-title{letter-spacing:2px}.db-stat{font-size:12px}.db-legend{font-size:13px;fill:var(--connector)}
    .db-rule{stroke:var(--grid);stroke-width:1.1}.db-sample{stroke-width:6;stroke-linecap:round}
    .db-details{overflow-x:auto}.db-details table{min-width:900px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_dumbbell(plan):
    layout = layout_dumbbell(plan)
    parts = ['<g data-dumbbell-contract="D-122-twelve-pair-shared-scale" data-template-contract="p18r6-review17-preserved">']
    band_top, band_bottom = 112, 882
    for key in ("before", "after"):
        stat = layout["stats"][key]
        parts.append(
            f'<rect class="db-band {key}" data-dumbbell-band="{key}" data-mean="{stat["mean"]:.4f}" '
            f'data-stdev="{stat["stdev"]:.4f}" x="{stat["x_min"]:.3f}" y="{band_top}" '
            f'width="{stat["x_max"] - stat["x_min"]:.3f}" height="{band_bottom - band_top}"/>'
        )
        parts.append(
            f'<line class="db-mean {key}" data-dumbbell-mean="{key}" x1="{stat["x_mean"]:.3f}" y1="{band_top}" '
            f'x2="{stat["x_mean"]:.3f}" y2="{band_bottom}"/>'
        )
        label = "TRƯỚC" if key == "before" else "SAU"
        parts.append(_text(stat["x_mean"], 94, f'{label} · TB {stat["mean"]:.1f}% · ±{stat["stdev"]:.1f}', f"db-stat {key}"))
    for tick in layout["ticks"]:
        x = layout["x_left"] + (layout["x_right"] - layout["x_left"]) * tick / 100
        parts.append(f'<line class="db-grid" data-dumbbell-tick="{tick}" x1="{x:.3f}" y1="112" x2="{x:.3f}" y2="{layout["axis_y"]}"/>')
        parts.append(_text(x, layout["axis_y"] + 34, tick, "db-tick"))
    parts.append(f'<line class="db-axis" data-dumbbell-axis="shared-value" x1="{layout["x_left"]}" y1="{layout["axis_y"]}" x2="{layout["x_right"]}" y2="{layout["axis_y"]}"/>')
    parts.append(_text((layout["x_left"] + layout["x_right"]) / 2, layout["axis_y"] + 72, "TỶ LỆ TỰ ĐỘNG HÓA · %", "db-axis-title"))
    for row in layout["rows"]:
        focal = " focal" if row["focal"] else ""
        parts.append(
            f'<line class="db-link{focal}" data-dumbbell-link="{row["id"]}" data-before="{row["before"]}" '
            f'data-after="{row["after"]}" data-delta="{row["delta"]}" x1="{row["x_before"]:.3f}" y1="{row["y"]}" '
            f'x2="{row["x_after"]:.3f}" y2="{row["y"]}"/>'
        )
        for key in ("before", "after"):
            parts.append(
                f'<circle class="db-point {key}{focal}" data-dumbbell-endpoint="{row["id"]}-{key}" '
                f'data-series="series-{key}" data-value="{row[key]}" cx="{row[f"x_{key}"]:.3f}" cy="{row["y"]}" r="8"/>'
            )
        parts.append(_text(356, row["y"] + 6, row["label"], f"db-row{focal}", "end"))
        parts.append(_text(row["x_before"] - 14, row["y"] + 5, row["before"], "db-value", "end"))
        parts.append(_text(row["x_after"] + 14, row["y"] + 5, row["after"], "db-value", "start"))
        parts.append(_text((row["x_before"] + row["x_after"]) / 2, row["y"] - 12, f'Δ +{row["delta"]}', f"db-delta{focal}"))
    parts.append('<line class="db-rule" x1="74" y1="1012" x2="1926" y2="1012"/>')
    parts.append(_text(74, 1054, "CHÚ GIẢI", "db-axis-title", "start"))
    parts.append('<circle class="db-point before" cx="300" cy="1049" r="8"/>')
    parts.append(_text(322, 1054, "Trước tối ưu", "db-legend", "start"))
    parts.append('<circle class="db-point after" cx="570" cy="1049" r="8"/>')
    parts.append(_text(592, 1054, "Sau tối ưu", "db-legend", "start"))
    parts.append('<line class="db-sample" x1="820" y1="1049" x2="876" y2="1049" stroke="var(--border)"/>')
    parts.append(_text(894, 1054, "Khoảng chênh lệch", "db-legend", "start"))
    parts.append('<rect class="db-band-swatch" x="1252" y="1038" width="46" height="22"/>')
    parts.append(_text(1316, 1054, "Dải trung bình ± 1 độ lệch chuẩn", "db-legend", "start"))
    parts.append(_text(74, 1110, "DỮ LIỆU MINH HỌA · 12 NHÓM · CÙNG THANG 0–100%", "db-stat", "start"))
    parts.append(_text(1926, 1110, "VỊ TRÍ = GIÁ TRỊ · ĐỘ DÀI = CHÊNH LỆCH", "db-stat", "end"))
    parts.append("</g>")
    return "".join(parts)


def dumbbell_table(plan):
    layout = layout_dumbbell(plan)
    rows = []
    for item in layout["rows"]:
        rows.append(
            "<tr>"
            f'<th scope="row">{escape(item["label"])}</th>'
            f'<td>{item["before"]}%</td><td>{item["after"]}%</td><td>+{item["delta"]} điểm %</td>'
            f'<td>{"Trọng tâm" if item["focal"] else "So sánh"}</td>'
            "</tr>"
        )
    return (
        '<details class="db-details"><summary>Dữ liệu dumbbell có thể kiểm chứng</summary>'
        '<table><thead><tr><th scope="col">Nhóm</th><th scope="col">Trước tối ưu</th>'
        '<th scope="col">Sau tối ưu</th><th scope="col">Chênh lệch</th><th scope="col">Vai trò</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></details>'
    )


def validate_dumbbell_svg(svg):
    root = ET.fromstring(svg)
    links = root.findall('.//*[@data-dumbbell-link]')
    endpoints = root.findall('.//*[@data-dumbbell-endpoint]')
    bands = root.findall('.//*[@data-dumbbell-band]')
    means = root.findall('.//*[@data-dumbbell-mean]')
    axes = root.findall('.//*[@data-dumbbell-axis]')
    ticks = root.findall('.//*[@data-dumbbell-tick]')
    _require(len(links) == 12, "Serialized D-122 pair count mismatch")
    _require(len(endpoints) == 24, "Serialized D-122 endpoint count mismatch")
    _require(len(bands) == len(means) == 2, "Serialized D-122 statistic overlay mismatch")
    _require(len(axes) == 1 and len(ticks) == 6, "Serialized D-122 shared axis mismatch")
    _require(all("marker-start" not in item.attrib and "marker-end" not in item.attrib for item in axes), "D-122 axis must be arrow-free")
    endpoint_by_id = {item.attrib["data-dumbbell-endpoint"]: item for item in endpoints}
    for link in links:
        key = link.attrib["data-dumbbell-link"]
        before = endpoint_by_id[f"{key}-before"]
        after = endpoint_by_id[f"{key}-after"]
        _require(abs(float(link.attrib["x1"]) - float(before.attrib["cx"])) < .001, "D-122 before attachment gap")
        _require(abs(float(link.attrib["x2"]) - float(after.attrib["cx"])) < .001, "D-122 after attachment gap")
        _require(abs(float(link.attrib["y1"]) - float(link.attrib["y2"])) < .001, "D-122 link must be horizontal")
    return {
        "pairs": len(links), "endpoints": len(endpoints), "series": len({item.attrib["data-series"] for item in endpoints}),
        "bands": len(bands), "mean_lines": len(means), "axes": len(axes), "ticks": len(ticks),
        "focal": sum("focal" in item.attrib.get("class", "") for item in links),
        "delta_labels": len(root.findall('.//text[@class="db-delta"]')) + len(root.findall('.//text[@class="db-delta focal"]')),
    }
