"""D-112 thin-stroke, uniformly inset exact-area Treemap with complete borders."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_GROUP_IDS = ("group-root", "group-world")
EXPECTED_LEAF_IDS = (
    "continent-asia", "continent-africa", "continent-europe",
    "continent-north-america", "continent-south-america", "continent-oceania",
)
FOCAL_ID = "continent-asia"
SMALL_ID = "continent-oceania"
TILE_INSET = 4.0
INTER_TILE_GAP = TILE_INSET * 2


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_treemap(plan):
    projection = plan.get("semantic_projection", {})
    quantitative = projection.get("quantitative_contract", {})
    return (
        tuple(item.get("id") for item in quantitative.get("treemap_groups", [])) == EXPECTED_GROUP_IDS
        and tuple(item.get("id") for item in quantitative.get("treemap_leaves", [])) == EXPECTED_LEAF_IDS
    )


def _share_text(value, total):
    share = value / total * 100
    return f"{share:.1f}%" if share < 1 else f"{round(share):.0f}%"


def _billions(value):
    return f"{value / 1000:.2f}".replace(".", ",") + " tỷ"


def layout_treemap(plan):
    projection = plan["semantic_projection"]
    quantitative = projection["quantitative_contract"]
    groups = quantitative["treemap_groups"]
    nodes = quantitative["treemap_leaves"]
    _require(tuple(item["id"] for item in groups) == EXPECTED_GROUP_IDS, "D-101 requires the exact two-level hierarchy")
    _require(tuple(item["id"] for item in nodes) == EXPECTED_LEAF_IDS, "D-101 requires six ordered continent leaves")
    _require(groups[0].get("member_ids") == ["group-world"], "D-101 root membership mismatch")
    _require(groups[1].get("member_ids") == list(EXPECTED_LEAF_IDS), "D-101 leaf membership mismatch")
    values = [float(item.get("value", -1)) for item in nodes]
    _require(all(math.isfinite(value) and value > 0 for value in values), "D-101 values must be finite and positive")
    total = sum(values)
    _require(abs(float(groups[0]["declared_total"]) - total) < 1e-9, "D-101 root total mismatch")
    _require(abs(float(groups[1]["declared_total"]) - total) < 1e-9, "D-101 group total mismatch")

    width, height = 2000.0, 1040.0
    x, y, chart_width, chart_height = 80.0, 72.0, 1840.0, 760.0
    asia_width = chart_width * values[0] / total
    right_x = x + asia_width
    right_width = chart_width - asia_width
    top_total = values[1] + values[2]
    bottom_total = values[3] + values[4] + values[5]
    top_height = chart_height * top_total / (top_total + bottom_total)
    bottom_y = y + top_height
    bottom_height = chart_height - top_height
    africa_width = right_width * values[1] / top_total
    north_width = right_width * values[3] / bottom_total
    south_width = right_width * values[4] / bottom_total
    rectangles = (
        (x, y, asia_width, chart_height),
        (right_x, y, africa_width, top_height),
        (right_x + africa_width, y, right_width - africa_width, top_height),
        (right_x, bottom_y, north_width, bottom_height),
        (right_x + north_width, bottom_y, south_width, bottom_height),
        (right_x + north_width + south_width, bottom_y, right_width - north_width - south_width, bottom_height),
    )
    tiles = []
    for node, value, rect in zip(nodes, values, rectangles):
        tile_x, tile_y, tile_width, tile_height = rect
        _require(tile_width > 0 and tile_height > 0, "D-101 tile dimensions must be positive")
        tiles.append({
            "id": node["id"], "label": node["label"], "value": value,
            "unit": node["unit"], "share": value / total,
            "share_text": _share_text(value, total), "value_text": _billions(value),
            "x": tile_x, "y": tile_y, "width": tile_width, "height": tile_height,
            "draw_x": tile_x + TILE_INSET, "draw_y": tile_y + TILE_INSET,
            "draw_width": tile_width - TILE_INSET * 2, "draw_height": tile_height - TILE_INSET * 2,
            "inset": TILE_INSET,
            "focal": node["id"] == FOCAL_ID, "compact": node["id"] == SMALL_ID,
        })
    canvas_area = chart_width * chart_height
    for tile in tiles:
        _require(abs(tile["width"] * tile["height"] / canvas_area - tile["share"]) < 1e-9, "D-101 tile area must encode the exact value share")
        _require(tile["x"] >= x and tile["y"] >= y, "D-101 tile starts outside chart")
        _require(tile["x"] + tile["width"] <= x + chart_width + 1e-6, "D-101 tile exceeds chart width")
        _require(tile["y"] + tile["height"] <= y + chart_height + 1e-6, "D-101 tile exceeds chart height")
        _require(tile["draw_width"] > 0 and tile["draw_height"] > 0, "D-103 inset tile must remain positive")
        _require(abs(tile["draw_x"] - tile["x"] - TILE_INSET) < 1e-9, "D-103 left inset mismatch")
        _require(abs(tile["draw_y"] - tile["y"] - TILE_INSET) < 1e-9, "D-103 top inset mismatch")
        _require(abs(tile["x"] + tile["width"] - tile["draw_x"] - tile["draw_width"] - TILE_INSET) < 1e-9, "D-103 right inset mismatch")
        _require(abs(tile["y"] + tile["height"] - tile["draw_y"] - tile["draw_height"] - TILE_INSET) < 1e-9, "D-103 bottom inset mismatch")
    return {
        "width": width, "height": height, "chart": {"x": x, "y": y, "width": chart_width, "height": chart_height},
        "total": total, "tiles": tiles,
    }


def treemap_css(tokens):
    return """
    .tm-tile{stroke:var(--connector);stroke-width:1.2;stroke-linejoin:round;vector-effect:non-scaling-stroke}
    .tm-tile.tm-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}
    .tm-tile.tm-level-1{fill:color-mix(in srgb,var(--connector) 24%,var(--surface))}
    .tm-tile.tm-level-2{fill:color-mix(in srgb,var(--connector) 17%,var(--surface))}
    .tm-tile.tm-level-3{fill:color-mix(in srgb,var(--connector) 12%,var(--surface))}
    .tm-tile.tm-level-4{fill:color-mix(in srgb,var(--connector) 9%,var(--surface))}
    .tm-tile.tm-level-5{fill:color-mix(in srgb,var(--connector) 6%,var(--surface))}
    .tm-title{font:750 27px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .tm-value{font:700 17px Menlo,Monaco,monospace;fill:var(--muted);letter-spacing:.03em}
    .tm-icon{fill:var(--text)}.tm-icon-text{font:750 13px Menlo,Monaco,monospace;fill:var(--canvas)}
    .tm-rule{stroke:var(--grid);stroke-width:1}.tm-legend{font:700 13px Menlo,Monaco,monospace;fill:var(--muted);letter-spacing:.04em}
    .tm-swatch-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}.tm-swatch-other{fill:color-mix(in srgb,var(--connector) 18%,var(--surface));stroke:var(--connector);stroke-width:1.2}
    .tm-details{overflow-x:auto}.tm-details table{min-width:780px}
    """


def _text(x, y, value, css, anchor="start"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_treemap(plan):
    layout = layout_treemap(plan)
    parts = [f'<g data-treemap-contract="D-112-thin-complete-borders" data-geometry-contract="D-103-uniform-inset-complete-borders" data-inter-tile-gap="{INTER_TILE_GAP:.1f}">']
    for index, tile in enumerate(layout["tiles"]):
        css = "tm-tile tm-focal" if tile["focal"] else f"tm-tile tm-level-{min(index, 5)}"
        label_state = "compact-icon" if tile["compact"] else "direct"
        parts.append(
            f'<rect class="{css}" data-tile-id="{tile["id"]}" data-value="{tile["value"]:.6f}" '
            f'data-share="{tile["share"]:.12f}" data-label-state="{label_state}" '
            f'data-allocation-x="{tile["x"]:.6f}" data-allocation-y="{tile["y"]:.6f}" '
            f'data-allocation-width="{tile["width"]:.6f}" data-allocation-height="{tile["height"]:.6f}" '
            f'data-edge-inset="{tile["inset"]:.1f}" data-border-edges="top right bottom left" '
            f'x="{tile["draw_x"]:.6f}" y="{tile["draw_y"]:.6f}" width="{tile["draw_width"]:.6f}" height="{tile["draw_height"]:.6f}" rx="5"/>'
        )
        if tile["compact"]:
            cx = tile["draw_x"] + tile["draw_width"] / 2
            cy = tile["draw_y"] + 48
            parts.append(f'<circle class="tm-icon" data-small-tile-label="{tile["id"]}" cx="{cx:.3f}" cy="{cy:.3f}" r="9"/>')
            parts.append(_text(cx, cy + 4.5, "i", "tm-icon-text", "middle"))
        else:
            label_x, label_y = tile["draw_x"] + 30, tile["draw_y"] + 54
            parts.append(_text(label_x, label_y, tile["label"], "tm-title"))
            parts.append(_text(label_x, label_y + 42, f'{tile["value_text"]} · {tile["share_text"]}', "tm-value"))
    parts.extend([
        '<line class="tm-rule" x1="80" y1="884" x2="1920" y2="884"/>',
        '<rect class="tm-swatch-focal" x="80" y="918" width="34" height="24" rx="5"/>',
        _text(132, 936, "Châu Á · tỷ trọng tiêu điểm", "tm-legend"),
        '<rect class="tm-swatch-other" x="520" y="918" width="34" height="24" rx="5"/>',
        _text(572, 936, "Châu lục khác · đậm hơn là lớn hơn", "tm-legend"),
        '<circle class="tm-icon" cx="1135" cy="930" r="11"/>',
        _text(1135, 934, "i", "tm-icon-text", "middle"),
        _text(1160, 936, "Châu Đại Dương · 0,05 tỷ · 0,6% · quá nhỏ để đặt nhãn", "tm-legend"),
        _text(1920, 986, "DIỆN TÍCH = DÂN SỐ · GIÁ TRỊ LÀM TRÒN THEO ẢNH THAM CHIẾU · TỔNG 8,10 TỶ", "tm-legend", "end"),
        '</g>',
    ])
    return "".join(parts)


def validate_treemap_svg(svg):
    root = ET.fromstring(svg)
    tiles = root.findall(".//*[@data-tile-id]")
    _require(len(tiles) == 6, "Serialized D-101 tile count mismatch")
    _require(tuple(item.attrib["data-tile-id"] for item in tiles) == EXPECTED_LEAF_IDS, "Serialized D-101 tile order mismatch")
    total_value = sum(float(item.attrib["data-value"]) for item in tiles)
    total_area = sum(float(item.attrib["data-allocation-width"]) * float(item.attrib["data-allocation-height"]) for item in tiles)
    for item in tiles:
        value_share = float(item.attrib["data-value"]) / total_value
        area_share = float(item.attrib["data-allocation-width"]) * float(item.attrib["data-allocation-height"]) / total_area
        _require(abs(value_share - area_share) < 1e-6, "Serialized D-101 area/value share mismatch")
        inset = float(item.attrib["data-edge-inset"])
        allocation_x = float(item.attrib["data-allocation-x"])
        allocation_y = float(item.attrib["data-allocation-y"])
        allocation_width = float(item.attrib["data-allocation-width"])
        allocation_height = float(item.attrib["data-allocation-height"])
        draw_x = float(item.attrib["x"])
        draw_y = float(item.attrib["y"])
        draw_width = float(item.attrib["width"])
        draw_height = float(item.attrib["height"])
        _require(item.attrib.get("data-border-edges") == "top right bottom left", "D-103 incomplete border-edge declaration")
        _require(abs(draw_x - allocation_x - inset) < 1e-6, "D-103 serialized left inset mismatch")
        _require(abs(draw_y - allocation_y - inset) < 1e-6, "D-103 serialized top inset mismatch")
        _require(abs(allocation_x + allocation_width - draw_x - draw_width - inset) < 1e-6, "D-103 serialized right inset mismatch")
        _require(abs(allocation_y + allocation_height - draw_y - draw_height - inset) < 1e-6, "D-103 serialized bottom inset mismatch")
    focal = [item for item in tiles if item.attrib["data-tile-id"] == FOCAL_ID]
    compact = [item for item in tiles if item.attrib.get("data-label-state") == "compact-icon"]
    _require(len(focal) == 1 and "tm-focal" in focal[0].attrib.get("class", ""), "D-101 focal tile mismatch")
    _require(len(compact) == 1 and compact[0].attrib["data-tile-id"] == SMALL_ID, "D-101 compact-label tile mismatch")
    _require(len(root.findall(".//*[@data-small-tile-label]")) == 1, "D-101 small-tile icon mismatch")
    return {"tiles": 6, "exact_area_encoding": 6, "complete_borders": 6, "uniform_insets": 6, "direct_labels": 5, "compact_labels": 1, "focal_tiles": 1}


def treemap_table(plan):
    layout = layout_treemap(plan)
    rows = []
    for tile in layout["tiles"]:
        label_mode = "Ký hiệu trong ô + chi tiết tại đây" if tile["compact"] else "Nhãn trực tiếp trong ô"
        rows.append(
            f'<tr><td>{escape(tile["id"])}</td><td>{escape(tile["label"])}</td>'
            f'<td>{tile["value"]:.0f}</td><td>{escape(tile["value_text"])}</td>'
            f'<td>{escape(tile["share_text"])}</td><td>{escape(label_mode)}</td></tr>'
        )
    return (
        '<details class="tm-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Diện tích từng ô được tính trực tiếp từ giá trị triệu người; tỷ lệ hiển thị được làm tròn riêng và không thay đổi hình học.</p>'
        '<table><thead><tr><th scope="col">Leaf ID</th><th scope="col">Châu lục</th>'
        '<th scope="col">Triệu người</th><th scope="col">Tỷ người</th><th scope="col">Tỷ trọng</th><th scope="col">Nhãn</th></tr></thead><tbody>'
        + "".join(rows) + '</tbody></table></details>'
    )
