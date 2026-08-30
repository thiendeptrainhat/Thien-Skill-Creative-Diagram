"""D-121 detailed two-state slope-graph layout with direct endpoint labels."""
from __future__ import annotations

from html import escape
import itertools
import math
import xml.etree.ElementTree as ET


EXPECTED_SERIES = (
    "series-platform", "series-data", "series-mobile", "series-partner",
    "series-enterprise", "series-retail", "series-labs",
)
EXPECTED_AXES = {"axis-slope-state", "axis-slope-value"}
EXPECTED_STATES = ("Ban đầu", "Hiện tại")
FOCAL_SERIES = "series-platform"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_slope_graph(plan):
    contract = plan.get("semantic_projection", {}).get("quantitative_contract", {})
    return tuple(item.get("id") for item in contract.get("series", [])) == EXPECTED_SERIES


def _rank(values):
    ordered = sorted(values, key=lambda item: (-item[1], item[0]))
    return {series_id: index + 1 for index, (series_id, _) in enumerate(ordered)}


def layout_slope_graph(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-121 requires exact state/value axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-121 requires exact seven ordered series")
    _require(set(annotations) == {"annotation-slope-focal"}, "D-121 requires one focal annotation")
    x_axis, y_axis = axes["axis-slope-state"], axes["axis-slope-value"]
    _require(x_axis["dimension"] == "x" and x_axis["scale"] == "ordinal", "D-121 x-axis mismatch")
    _require(
        y_axis["dimension"] == "y" and y_axis["scale"] == "linear"
        and y_axis.get("domain_min") == 0 and y_axis.get("domain_max") == 100
        and y_axis.get("unit") == "%",
        "D-121 requires a shared truthful 0–100% scale",
    )
    _require(annotations["annotation-slope-focal"].get("target_ids") == [FOCAL_SERIES], "D-121 focal target mismatch")

    width, height = 2000, 980
    x_left, x_right, top, bottom = 650, 1350, 92, 752
    material = []
    for index, item in enumerate(series_items):
        data = item["data"]
        _require(len(data) == 2 and tuple(point["domain"] for point in data) == EXPECTED_STATES, "D-121 requires exactly two shared states")
        _require(all(not point.get("missing") and isinstance(point.get("value"), (int, float)) for point in data), "D-121 requires numeric endpoints")
        _require(all(math.isfinite(point["value"]) and 0 <= point["value"] <= 100 for point in data), "D-121 endpoint outside scale")
        before, after = data[0]["value"], data[1]["value"]
        direction = "up" if after > before else "down" if after < before else "flat"
        material.append({
            **item,
            "before": before,
            "after": after,
            "delta": after - before,
            "direction": direction,
            "y_left": bottom - before / 100 * (bottom - top),
            "y_right": bottom - after / 100 * (bottom - top),
            "style_index": index + 1,
            "focal": item["id"] == FOCAL_SERIES,
        })
    left_rank = _rank([(item["id"], item["before"]) for item in material])
    right_rank = _rank([(item["id"], item["after"]) for item in material])
    for item in material:
        item["rank_left"] = left_rank[item["id"]]
        item["rank_right"] = right_rank[item["id"]]
    crossings = sum(
        (a["before"] - b["before"]) * (a["after"] - b["after"]) < 0
        for a, b in itertools.combinations(material, 2)
    )
    _require(any(item["direction"] == "up" for item in material), "D-121 requires at least one rise")
    _require(any(item["direction"] == "down" for item in material), "D-121 requires at least one fall")
    _require(crossings > 0, "D-121 requires rank-changing crossings")
    return {
        "width": width, "height": height,
        "x_left": x_left, "x_right": x_right, "top": top, "bottom": bottom,
        "series": material, "crossings": crossings,
        "ticks": tuple(range(0, 101, 20)),
    }


def slope_graph_css(tokens):
    return """
    .sg-grid{stroke:var(--grid);stroke-width:1;opacity:.62}
    .sg-axis{stroke:var(--border);stroke-width:1.25}
    .sg-line{fill:none;stroke-width:3.4;stroke-linecap:round;opacity:1}
    .sg-line.is-focal{stroke:var(--accent);stroke-width:4.5;opacity:1}
    .sg-line.s2{stroke:var(--series-1)}.sg-line.s3{stroke:var(--success)}.sg-line.s4{stroke:var(--series-4)}
    .sg-line.s5{stroke:var(--danger)}.sg-line.s6{stroke:var(--connector)}.sg-line.s7{stroke:var(--muted)}
    .sg-point{fill:var(--canvas);stroke-width:2.4}.sg-point.is-focal{fill:var(--accent);stroke:var(--accent)}
    .sg-point.s2{stroke:var(--series-1)}.sg-point.s3{stroke:var(--success)}.sg-point.s4{stroke:var(--series-4)}
    .sg-point.s5{stroke:var(--danger)}.sg-point.s6{stroke:var(--connector)}.sg-point.s7{stroke:var(--muted)}
    .sg-tick,.sg-state,.sg-value,.sg-axis-title,.sg-note{font:600 15px Menlo,Monaco,monospace;fill:var(--connector)}
    .sg-state{font-size:18px;font-weight:750;fill:var(--text)}
    .sg-value{font:650 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .sg-value.is-focal{fill:var(--accent-text);font-weight:750}
    .sg-axis-title{font-size:13px;letter-spacing:2px;fill:var(--muted)}
    .sg-note{font-size:13px;fill:var(--muted)}
    .sg-legend-rule{stroke:var(--grid);stroke-width:1.1}
    .sg-details{overflow-x:auto}.sg-details table{min-width:900px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_slope_graph(plan):
    layout = layout_slope_graph(plan)
    left, right, top, bottom = layout["x_left"], layout["x_right"], layout["top"], layout["bottom"]
    parts = [f'<g data-slope-graph-contract="D-121-seven-series-two-state" data-crossing-count="{layout["crossings"]}" data-template-contract="p18r6-review17-preserved">']
    for tick in layout["ticks"]:
        y = bottom - tick / 100 * (bottom - top)
        parts.append(f'<line class="sg-grid" data-slope-tick="{tick}" x1="520" y1="{y:.3f}" x2="1480" y2="{y:.3f}"/>')
        parts.append(_text(496, y + 5, tick, "sg-tick", "end"))
        parts.append(_text(1600, y + 5, tick, "sg-tick", "start"))
    for axis_id, x in (("axis-slope-left", left), ("axis-slope-right", right)):
        parts.append(f'<line class="sg-axis" data-slope-axis="{axis_id}" x1="{x}" y1="{top}" x2="{x}" y2="{bottom}"/>')
    parts.append(_text(520, 58, "TỶ LỆ HOÀN THÀNH · %", "sg-axis-title", "start"))
    for item in layout["series"]:
        css = "is-focal" if item["focal"] else f's{item["style_index"]}'
        parts.append(
            f'<line class="sg-line {css}" data-slope-series="{item["id"]}" data-direction="{item["direction"]}" '
            f'data-before="{item["before"]}" data-after="{item["after"]}" data-rank-left="{item["rank_left"]}" '
            f'data-rank-right="{item["rank_right"]}" x1="{left}" y1="{item["y_left"]:.3f}" x2="{right}" y2="{item["y_right"]:.3f}"/>'
        )
        for side, x, y, value, rank in (
            ("left", left, item["y_left"], item["before"], item["rank_left"]),
            ("right", right, item["y_right"], item["after"], item["rank_right"]),
        ):
            parts.append(
                f'<circle class="sg-point {css}" data-slope-endpoint="{item["id"]}-{side}" data-value="{value}" '
                f'data-rank="{rank}" cx="{x}" cy="{y:.3f}" r="6.5"/>'
            )
        label_css = "sg-value is-focal" if item["focal"] else "sg-value"
        parts.append(_text(left - 20, item["y_left"] + 6, f'{item["label"]} · {item["before"]}%', label_css, "end"))
        parts.append(_text(right + 20, item["y_right"] + 6, f'{item["after"]}% · {item["label"]}', label_css, "start"))
    parts.append(_text(left, bottom + 50, "BAN ĐẦU", "sg-state"))
    parts.append(_text(right, bottom + 50, "HIỆN TẠI", "sg-state"))
    parts.append(f'<line class="sg-legend-rule" x1="74" y1="870" x2="1926" y2="870"/>')
    parts.append(_text(74, 904, "ĐỌC BIỂU ĐỒ", "sg-axis-title", "start"))
    parts.append(_text(300, 904, "Mỗi đường nối cùng một nhóm qua đúng hai kỳ; giao cắt = đổi thứ hạng.", "sg-note", "start"))
    parts.append(_text(1926, 904, f'{layout["crossings"]} giao cắt · 7 chuỗi · cùng thang 0–100%', "sg-note", "end"))
    parts.append("</g>")
    return "".join(parts)


def slope_graph_table(plan):
    layout = layout_slope_graph(plan)
    rows = []
    for item in layout["series"]:
        rows.append(
            "<tr>"
            f'<th scope="row">{escape(item["label"])}</th>'
            f'<td>{item["before"]}%</td><td>{item["after"]}%</td>'
            f'<td>{item["delta"]:+d} điểm %</td><td>{escape(item["direction"])}</td>'
            f'<td>{item["rank_left"]} → {item["rank_right"]}</td>'
            "</tr>"
        )
    return (
        '<details class="sg-details"><summary>Dữ liệu slope-graph có thể kiểm chứng</summary>'
        '<table><thead><tr><th scope="col">Nhóm</th><th scope="col">Ban đầu</th><th scope="col">Hiện tại</th>'
        '<th scope="col">Thay đổi</th><th scope="col">Hướng</th><th scope="col">Hạng</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></details>'
    )


def validate_slope_graph_svg(svg):
    root = ET.fromstring(svg)
    series = root.findall('.//*[@data-slope-series]')
    endpoints = root.findall('.//*[@data-slope-endpoint]')
    axes = root.findall('.//*[@data-slope-axis]')
    _require(len(series) == 7, "Serialized D-121 series mismatch")
    _require(len(endpoints) == 14, "Serialized D-121 endpoint mismatch")
    _require(len(axes) == 2, "Serialized D-121 state-axis mismatch")
    _require(sum(item.attrib.get("data-direction") == "up" for item in series) > 0, "Serialized D-121 rise missing")
    _require(sum(item.attrib.get("data-direction") == "down" for item in series) > 0, "Serialized D-121 fall missing")
    _require(all("marker-end" not in item.attrib and "marker-start" not in item.attrib for item in axes), "D-121 axes must be arrow-free")
    contract = root.find('.//*[@data-slope-graph-contract]')
    _require(contract is not None and int(contract.attrib["data-crossing-count"]) > 0, "Serialized D-121 crossing mismatch")
    return {
        "series": len(series), "endpoints": len(endpoints), "axes": len(axes),
        "ticks": len(root.findall('.//*[@data-slope-tick]')),
        "rises": sum(item.attrib.get("data-direction") == "up" for item in series),
        "falls": sum(item.attrib.get("data-direction") == "down" for item in series),
        "crossings": int(contract.attrib["data-crossing-count"]),
        "focal": sum("is-focal" in item.attrib.get("class", "") for item in series),
    }
