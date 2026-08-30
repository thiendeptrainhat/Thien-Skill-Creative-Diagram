"""D-100 content-fit three-set Venn with an exact triple intersection."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_SET_IDS = ("set-desirable", "set-feasible", "set-viable")
EXPECTED_MEMBER_IDS = (
    "member-desirable", "member-feasible", "member-viable", "member-ready",
)
CORE_MEMBER = "member-ready"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_venn(plan):
    projection = plan.get("semantic_projection", {})
    groups = projection.get("groups", [])
    nodes = projection.get("nodes", [])
    return (
        tuple(item.get("id") for item in groups) == EXPECTED_SET_IDS
        and tuple(item.get("id") for item in nodes) == EXPECTED_MEMBER_IDS
    )


def layout_venn(plan):
    projection = plan["semantic_projection"]
    groups = projection["groups"]
    nodes = projection["nodes"]
    _require(tuple(item["id"] for item in groups) == EXPECTED_SET_IDS, "D-100 requires three exact ordered sets")
    _require(tuple(item["id"] for item in nodes) == EXPECTED_MEMBER_IDS, "D-100 requires four exact members")
    node_ids = {item["id"] for item in nodes}
    _require(len(node_ids) == 4, "D-100 member IDs must be unique")
    node_by_id = {item["id"]: item for item in nodes}
    for group, exclusive in zip(groups, EXPECTED_MEMBER_IDS[:3]):
        _require(group.get("member_ids") == [exclusive, CORE_MEMBER], "Each D-100 set needs one exclusive and the shared core member")
        _require(node_by_id[exclusive].get("label"), "Each D-100 set needs a direct subtitle")
    _require(sum(CORE_MEMBER in group["member_ids"] for group in groups) == 3, "Core member must belong to all three sets")
    _require(all(sum(member in group["member_ids"] for group in groups) == 1 for member in EXPECTED_MEMBER_IDS[:3]), "Exclusive members must belong to one set")

    width, height, radius = 2000, 1040, 340.0
    circles = (
        {"id": groups[0]["id"], "cx": 1000.0, "cy": 355.0, "r": radius, "label_x": 1000.0, "label_y": 205.0},
        {"id": groups[1]["id"], "cx": 820.0, "cy": 620.0, "r": radius, "label_x": 650.0, "label_y": 750.0},
        {"id": groups[2]["id"], "cx": 1180.0, "cy": 620.0, "r": radius, "label_x": 1350.0, "label_y": 750.0},
    )
    for circle, group, exclusive in zip(circles, groups, EXPECTED_MEMBER_IDS[:3]):
        circle.update({"label": group["label"], "subtitle": node_by_id[exclusive]["label"], "member_ids": tuple(group["member_ids"])})
        _require(circle["cx"] - radius >= 0 and circle["cx"] + radius <= width, "D-100 circle exceeds canvas")
        _require(circle["cy"] - radius >= 0 and circle["cy"] + radius <= height, "D-100 circle exceeds canvas")
    center = {"x": 1000.0, "y": 535.0, "title": "Sẵn sàng triển khai", "subtitle": "ĐIỂM CÂN BẰNG"}
    _require(all(math.hypot(center["x"] - item["cx"], center["y"] - item["cy"]) < radius for item in circles), "D-100 core label must lie in the triple intersection")
    return {"width": width, "height": height, "radius": radius, "circles": circles, "center": center, "nodes": nodes}


def venn_css(tokens):
    return """
    .vn-set-fill{fill:color-mix(in srgb,var(--connector) 7%,transparent);stroke:none}
    .vn-set-outline{fill:none;stroke:var(--connector);stroke-width:2.5}
    .vn-core{fill:var(--text);stroke:none}
    .vn-title{font:700 28px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .vn-subtitle{font:700 15px Menlo,Monaco,monospace;letter-spacing:3px;fill:var(--muted)}
    .vn-core-title{font:750 28px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--canvas)}
    .vn-core-subtitle{font:700 15px Menlo,Monaco,monospace;letter-spacing:3px;fill:var(--canvas);opacity:.84}
    .vn-details{overflow-x:auto}.vn-details table{min-width:760px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_venn(plan):
    layout = layout_venn(plan)
    circles = layout["circles"]
    parts = [
        '<g data-venn-contract="D-100-three-set-exact-triple-intersection">',
        '<defs>',
        f'<clipPath id="venn-clip-desirable"><circle cx="{circles[0]["cx"]}" cy="{circles[0]["cy"]}" r="{circles[0]["r"]}"/></clipPath>',
        f'<clipPath id="venn-clip-feasible"><circle cx="{circles[1]["cx"]}" cy="{circles[1]["cy"]}" r="{circles[1]["r"]}"/></clipPath>',
        '</defs>',
    ]
    for item in circles:
        members = " ".join(item["member_ids"])
        attrs = (
            f'data-set-id="{escape(item["id"], quote=True)}" data-member-ids="{escape(members, quote=True)}" '
            f'data-cx="{item["cx"]}" data-cy="{item["cy"]}" data-radius="{item["r"]}"'
        )
        parts.append(f'<circle class="vn-set-fill" {attrs} cx="{item["cx"]}" cy="{item["cy"]}" r="{item["r"]}"/>')
    parts.append(
        f'<g clip-path="url(#venn-clip-desirable)"><g clip-path="url(#venn-clip-feasible)">'
        f'<circle class="vn-core" data-region-id="triple-intersection" data-member-id="{CORE_MEMBER}" '
        f'cx="{circles[2]["cx"]}" cy="{circles[2]["cy"]}" r="{circles[2]["r"]}"/></g></g>'
    )
    for item in circles:
        parts.append(f'<circle class="vn-set-outline" data-outline-for="{item["id"]}" cx="{item["cx"]}" cy="{item["cy"]}" r="{item["r"]}"/>')
        parts.append(_text(item["label_x"], item["label_y"], item["label"], "vn-title"))
        parts.append(_text(item["label_x"], item["label_y"] + 36, item["subtitle"].upper(), "vn-subtitle"))
    center = layout["center"]
    parts.append(_text(center["x"], center["y"], center["title"], "vn-core-title"))
    parts.append(_text(center["x"], center["y"] + 38, center["subtitle"], "vn-core-subtitle"))
    parts.append('</g>')
    return "".join(parts)


def validate_venn_svg(svg):
    root = ET.fromstring(svg)
    sets = root.findall(".//*[@data-set-id]")
    outlines = root.findall(".//*[@data-outline-for]")
    cores = root.findall(".//*[@data-region-id='triple-intersection']")
    _require(len(sets) == 3 and len(outlines) == 3 and len(cores) == 1, "Serialized D-100 set/core count mismatch")
    _require(tuple(item.attrib["data-set-id"] for item in sets) == EXPECTED_SET_IDS, "Serialized D-100 set order mismatch")
    _require({item.attrib["data-outline-for"] for item in outlines} == set(EXPECTED_SET_IDS), "Serialized D-100 outline binding mismatch")
    _require(cores[0].attrib.get("data-member-id") == CORE_MEMBER, "Serialized D-100 core binding mismatch")
    clips = root.findall(".//clipPath")
    _require(len(clips) == 2 and cores[0].get("class") == "vn-core", "D-100 triple region must use exact nested clipping")
    circles = []
    for item in sets:
        cx, cy, radius = (float(item.attrib[name]) for name in ("data-cx", "data-cy", "data-radius"))
        _require(radius > 0 and math.isfinite(cx + cy + radius), "D-100 circle geometry invalid")
        circles.append((cx, cy, radius))
    _require(len({round(item[2], 6) for item in circles}) == 1, "D-100 set circles must be equal")
    _require(abs(circles[1][0] + circles[2][0] - 2 * circles[0][0]) < .001, "D-100 lower circles must balance around the top circle")
    _require(abs(circles[1][1] - circles[2][1]) < .001, "D-100 lower circles must share one baseline")
    return {"sets": 3, "members": 4, "triple_intersections": 1, "clip_paths": 2, "direct_labels": 4}


def venn_table(plan):
    layout = layout_venn(plan)
    memberships = {node["id"]: [] for node in layout["nodes"]}
    for circle in layout["circles"]:
        for member_id in circle["member_ids"]:
            memberships[member_id].append(circle["label"])
    rows = []
    for node in layout["nodes"]:
        role = "Giao ba tập · điểm cân bằng" if node["id"] == CORE_MEMBER else "Tiêu chí riêng"
        rows.append(
            f'<tr><td>{escape(node["id"])}</td><td>{escape(node["label"])}</td>'
            f'<td>{escape(" · ".join(memberships[node["id"]]))}</td><td>{role}</td></tr>'
        )
    return (
        '<details class="vn-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Bốn tiêu chí được ánh xạ trực tiếp vào ba tập; “Sẵn sàng triển khai” là thành viên duy nhất của cả ba tập.</p>'
        '<table><thead><tr><th scope="col">Member ID</th><th scope="col">Tiêu chí</th>'
        '<th scope="col">Thuộc tập</th><th scope="col">Vai trò</th></tr></thead><tbody>'
        + "".join(rows) + '</tbody></table></details>'
    )
