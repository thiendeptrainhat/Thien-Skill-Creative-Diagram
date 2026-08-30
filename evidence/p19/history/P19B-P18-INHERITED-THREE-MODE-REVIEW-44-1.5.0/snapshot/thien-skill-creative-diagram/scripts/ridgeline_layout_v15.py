"""D-123 detailed shared-domain ridgeline layout with quantile bands."""
from __future__ import annotations

from html import escape
import math
import statistics
import xml.etree.ElementTree as ET


EXPECTED_SERIES = (
    "series-platform", "series-payments", "series-identity", "series-search",
    "series-data", "series-mobile", "series-partners", "series-retail",
    "series-content", "series-analytics", "series-support", "series-archive",
)
EXPECTED_AXES = {"axis-ridge-domain", "axis-ridge-amplitude"}
FOCAL_SERIES = "series-platform"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _quantile(values, probability):
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def is_detailed_ridgeline(plan):
    contract = plan.get("semantic_projection", {}).get("quantitative_contract", {})
    series_items = contract.get("series", [])
    return tuple(item.get("id") for item in series_items) == EXPECTED_SERIES


def layout_ridgeline(plan):
    projection = plan["semantic_projection"]
    contract = projection["quantitative_contract"]
    axes = {item["id"]: item for item in contract["axes"]}
    series_items = contract["series"]
    profiles = contract.get("ridgeline_profiles", {})
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(set(axes) == EXPECTED_AXES, "D-123 requires exact domain/amplitude axes")
    _require(tuple(item["id"] for item in series_items) == EXPECTED_SERIES, "D-123 requires twelve ordered services")
    _require(set(annotations) == {"annotation-ridgeline-focal"}, "D-123 requires one focal annotation")
    domain_axis = axes["axis-ridge-domain"]
    amplitude_axis = axes["axis-ridge-amplitude"]
    _require(
        domain_axis["scale"] == "linear" and domain_axis.get("domain_min") == 0
        and domain_axis.get("domain_max") == 120 and domain_axis.get("unit") == "ms",
        "D-123 requires a shared 0–120 ms domain",
    )
    _require(
        amplitude_axis["scale"] == "linear" and amplitude_axis.get("domain_min") == 0
        and amplitude_axis.get("domain_max") == 1,
        "D-123 requires global-normalized amplitude",
    )
    _require(len(profiles.get("grid", [])) == 20, "D-123 requires twenty shared KDE positions")
    _require(set(profiles.get("amplitudes", {})) == set(EXPECTED_SERIES), "D-123 profile set mismatch")

    width, height = 2000, 1180
    x_left, x_right, top, row_step, axis_y = 430, 1890, 150, 66, 958
    scale = (x_right - x_left) / 120
    rows = []
    all_samples = []
    for index, item in enumerate(series_items):
        samples = item["data"][0].get("distribution_samples", [])
        _require(len(samples) == 24, "D-123 requires twenty-four observations per service")
        _require(all(isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 120 for value in samples), "D-123 sample outside shared domain")
        amplitudes = profiles["amplitudes"][item["id"]]
        _require(len(amplitudes) == len(profiles["grid"]), "D-123 amplitude grid mismatch")
        baseline = top + index * row_step
        quantiles = {
            "q025": _quantile(samples, .025), "q10": _quantile(samples, .10),
            "q25": _quantile(samples, .25), "median": _quantile(samples, .50),
            "q75": _quantile(samples, .75), "q90": _quantile(samples, .90),
            "q975": _quantile(samples, .975),
        }
        rows.append({
            "id": item["id"].removeprefix("series-"), "series_id": item["id"],
            "label": item["label"], "samples": tuple(samples), "n": len(samples),
            "baseline": baseline, "quantiles": quantiles,
            "points": tuple(
                (x_left + float(grid_value) * scale, baseline - float(amplitude) * 43)
                for grid_value, amplitude in zip(profiles["grid"], amplitudes)
            ),
            "focal": item["id"] == FOCAL_SERIES,
        })
        all_samples.extend(samples)
    _require(sum(row["focal"] for row in rows) == 1, "D-123 requires one focal distribution")
    return {
        "width": width, "height": height, "x_left": x_left, "x_right": x_right,
        "top": top, "axis_y": axis_y, "scale": scale, "rows": rows,
        "ticks": tuple(range(0, 121, 20)),
        "reference_median": statistics.median(all_samples),
        "domain_min": 0, "domain_max": 120, "global_max": profiles["global_max"],
    }


def ridgeline_css(tokens):
    return """
    .rg-grid{stroke:var(--grid);stroke-width:1;opacity:.72}.rg-axis{stroke:var(--border);stroke-width:1.2}
    .rg-baseline{stroke:var(--grid);stroke-width:1}.rg-density{fill:var(--series-1);fill-opacity:.14;stroke:var(--series-1);stroke-width:1.25;stroke-linejoin:round}
    .rg-density.focal{fill:var(--accent);fill-opacity:.14;stroke:var(--accent);stroke-width:1.5}
    .rg-band{stroke:none;fill:var(--series-3)}.rg-band.q95{fill-opacity:.18}.rg-band.q80{fill-opacity:.34}.rg-band.q50{fill-opacity:.62}
    .rg-band.focal{fill:var(--accent)}.rg-band.focal.q95{fill-opacity:.14}.rg-band.focal.q80{fill-opacity:.27}.rg-band.focal.q50{fill-opacity:.48}
    .rg-median{fill:var(--text);stroke:var(--surface);stroke-width:1.25}.rg-median.focal{fill:var(--accent);stroke:var(--surface);stroke-width:1.5}
    .rg-reference{stroke:var(--connector);stroke-width:1.25;stroke-dasharray:8 7}.rg-label{font:700 16px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .rg-label.focal{fill:var(--accent-text)}.rg-count,.rg-tick,.rg-axis-title,.rg-note,.rg-legend{font:650 12px Menlo,Monaco,monospace;fill:var(--muted)}
    .rg-axis-title{letter-spacing:2px}.rg-note{font-size:11px}.rg-legend{fill:var(--connector)}.rg-rule{stroke:var(--grid);stroke-width:1.1}
    .rg-details{overflow-x:auto}.rg-details table{min-width:1100px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def _smooth_area(points, baseline):
    if not points:
        return ""
    commands = [f"M {points[0][0]:.3f} {baseline:.3f}", f"L {points[0][0]:.3f} {points[0][1]:.3f}"]
    extended = [points[0], *points, points[-1]]
    for index in range(1, len(extended) - 2):
        p0, p1, p2, p3 = extended[index - 1:index + 3]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        commands.append(f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p2[0]:.3f} {p2[1]:.3f}")
    commands.extend([f"L {points[-1][0]:.3f} {baseline:.3f}", "Z"])
    return " ".join(commands)


def render_ridgeline(plan):
    layout = layout_ridgeline(plan)
    parts = ['<g data-ridgeline-contract="D-123-twelve-shared-domain-quantiles" data-template-contract="p18r6-review17-preserved">']
    plot_top, plot_bottom = 92, layout["axis_y"]
    for tick in layout["ticks"]:
        x = layout["x_left"] + tick * layout["scale"]
        parts.append(f'<line class="rg-grid" data-ridgeline-tick="{tick}" x1="{x:.3f}" y1="{plot_top}" x2="{x:.3f}" y2="{plot_bottom}"/>')
        parts.append(_text(x, plot_bottom + 31, tick, "rg-tick"))
    ref_x = layout["x_left"] + layout["reference_median"] * layout["scale"]
    parts.append(f'<line class="rg-reference" data-ridgeline-reference="shared-median" data-value="{layout["reference_median"]:.3f}" x1="{ref_x:.3f}" y1="{plot_top}" x2="{ref_x:.3f}" y2="{plot_bottom}"/>')
    parts.append(_text(ref_x + 10, 82, f'TRUNG VỊ CHUNG · {layout["reference_median"]:.1f} MS', "rg-note", "start"))
    for row in layout["rows"]:
        focal = " focal" if row["focal"] else ""
        baseline = row["baseline"]
        parts.append(f'<line class="rg-baseline" x1="{layout["x_left"]}" y1="{baseline}" x2="{layout["x_right"]}" y2="{baseline}"/>')
        parts.append(
            f'<path class="rg-density{focal}" data-ridge-id="{row["id"]}" data-series-id="{row["series_id"]}" '
            f'data-domain-min="0" data-domain-max="120" data-normalization="global-max" d="{_smooth_area(row["points"], baseline)}"/>'
        )
        quantiles = row["quantiles"]
        for interval, left_key, right_key in (("95", "q025", "q975"), ("80", "q10", "q90"), ("50", "q25", "q75")):
            x = layout["x_left"] + quantiles[left_key] * layout["scale"]
            right = layout["x_left"] + quantiles[right_key] * layout["scale"]
            parts.append(
                f'<rect class="rg-band q{interval}{focal}" data-ridgeline-band="{row["id"]}-{interval}" data-ridge="{row["id"]}" '
                f'data-interval="{interval}" x="{x:.3f}" y="{baseline - 7:.3f}" width="{right - x:.3f}" height="14"/>'
            )
        median_x = layout["x_left"] + quantiles["median"] * layout["scale"]
        parts.append(f'<circle class="rg-median{focal}" data-ridgeline-median="{row["id"]}" data-value="{quantiles["median"]:.3f}" cx="{median_x:.3f}" cy="{baseline}" r="5.5"/>')
        parts.append(_text(370, baseline + 6, row["label"], f"rg-label{focal}", "end"))
        parts.append(_text(84, baseline + 5, f'n={row["n"]}', "rg-count", "start"))
        if row["focal"]:
            parts.append(_text(1910, baseline + 5, "TRỌNG TÂM", "rg-label focal", "end"))
    parts.append(f'<line class="rg-axis" data-ridgeline-axis="shared-domain" x1="{layout["x_left"]}" y1="{plot_bottom}" x2="{layout["x_right"]}" y2="{plot_bottom}"/>')
    parts.append(_text((layout["x_left"] + layout["x_right"]) / 2, plot_bottom + 69, "ĐỘ TRỄ PHẢN HỒI · MS", "rg-axis-title"))
    parts.append('<line class="rg-rule" x1="74" y1="1058" x2="1926" y2="1058"/>')
    parts.append(_text(74, 1100, "CHÚ GIẢI", "rg-axis-title", "start"))
    parts.append('<path class="rg-density" d="M 300 1100 C 320 1072 350 1072 376 1100 L 376 1100 Z"/>')
    parts.append(_text(398, 1105, "Phân phối mật độ", "rg-legend", "start"))
    parts.append('<rect class="rg-band q95" x="690" y="1091" width="70" height="14"/><rect class="rg-band q80" x="706" y="1091" width="48" height="14"/><rect class="rg-band q50" x="720" y="1091" width="24" height="14"/>')
    parts.append(_text(782, 1105, "Dải 95 / 80 / 50%", "rg-legend", "start"))
    parts.append('<circle class="rg-median" cx="1140" cy="1098" r="5.5"/>')
    parts.append(_text(1162, 1105, "Trung vị từng hàng", "rg-legend", "start"))
    parts.append('<line class="rg-reference" x1="1530" y1="1083" x2="1530" y2="1111"/>')
    parts.append(_text(1552, 1105, "Trung vị chung", "rg-legend", "start"))
    parts.append(_text(74, 1150, "DỮ LIỆU MINH HỌA · KDE · BANDWIDTH 7 MS · CHUẨN HÓA GLOBAL-MAX", "rg-note", "start"))
    parts.append(_text(1926, 1150, "12 DỊCH VỤ · CÙNG MIỀN 0–120 MS", "rg-note", "end"))
    parts.append("</g>")
    return "".join(parts)


def ridgeline_table(plan):
    layout = layout_ridgeline(plan)
    rows = []
    for row in layout["rows"]:
        q = row["quantiles"]
        rows.append(
            "<tr>" + f'<th scope="row">{escape(row["label"])}</th>'
            f'<td>{row["n"]}</td><td>{q["q025"]:.1f}</td><td>{q["q10"]:.1f}</td><td>{q["q25"]:.1f}</td>'
            f'<td>{q["median"]:.1f}</td><td>{q["q75"]:.1f}</td><td>{q["q90"]:.1f}</td><td>{q["q975"]:.1f}</td>'
            f'<td>{"Trọng tâm" if row["focal"] else "So sánh"}</td></tr>'
        )
    return (
        '<details class="rg-details"><summary>Dữ liệu ridgeline có thể kiểm chứng</summary><table><thead><tr>'
        '<th scope="col">Dịch vụ</th><th scope="col">n</th><th scope="col">P2.5</th><th scope="col">P10</th>'
        '<th scope="col">P25</th><th scope="col">Trung vị</th><th scope="col">P75</th><th scope="col">P90</th>'
        '<th scope="col">P97.5</th><th scope="col">Vai trò</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></details>'
    )


def validate_ridgeline_svg(svg):
    root = ET.fromstring(svg)
    ridges = root.findall('.//*[@data-ridge-id]')
    medians = root.findall('.//*[@data-ridgeline-median]')
    bands = root.findall('.//*[@data-ridgeline-band]')
    references = root.findall('.//*[@data-ridgeline-reference]')
    axes = root.findall('.//*[@data-ridgeline-axis]')
    ticks = root.findall('.//*[@data-ridgeline-tick]')
    _require(len(ridges) == 12, "Serialized D-123 ridge count mismatch")
    _require(len(medians) == 12 and len(bands) == 36, "Serialized D-123 quantile encoding mismatch")
    _require(len(references) == 1 and len(axes) == 1 and len(ticks) == 7, "Serialized D-123 shared-scale structure mismatch")
    _require(all(item.attrib.get("data-domain-min") == "0" and item.attrib.get("data-domain-max") == "120" for item in ridges), "D-123 shared domain drift")
    _require(all(item.attrib.get("data-normalization") == "global-max" for item in ridges), "D-123 amplitude normalization drift")
    _require(all("marker-start" not in item.attrib and "marker-end" not in item.attrib for item in axes), "D-123 axis must be arrow-free")
    grouped = {}
    for band in bands:
        grouped.setdefault(band.attrib["data-ridge"], {})[band.attrib["data-interval"]] = band
    median_by_id = {item.attrib["data-ridgeline-median"]: item for item in medians}
    for ridge_id, intervals in grouped.items():
        _require(set(intervals) == {"50", "80", "95"}, "D-123 interval set mismatch")
        bounds = {}
        for interval, item in intervals.items():
            left = float(item.attrib["x"]); right = left + float(item.attrib["width"])
            bounds[interval] = (left, right)
        _require(bounds["95"][0] <= bounds["80"][0] <= bounds["50"][0], "D-123 left quantile nesting mismatch")
        _require(bounds["50"][1] <= bounds["80"][1] <= bounds["95"][1], "D-123 right quantile nesting mismatch")
        median_x = float(median_by_id[ridge_id].attrib["cx"])
        _require(bounds["50"][0] <= median_x <= bounds["50"][1], "D-123 median outside IQR")
    return {
        "ridges": len(ridges), "medians": len(medians), "bands": len(bands),
        "reference_lines": len(references), "axes": len(axes), "ticks": len(ticks),
        "focal": sum("focal" in item.attrib.get("class", "") for item in ridges),
        "profile_points": sum(len(item.attrib.get("d", "").split("C ")) - 1 for item in ridges),
    }
