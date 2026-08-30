"""D-125 detailed canonical nested containment in the approved P-18 grammar."""

from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH = 2000
HEIGHT = 1080
SCOPE_ORDER = (
    "scope-enterprise",
    "scope-data",
    "scope-analytics",
    "scope-operations",
    "scope-project",
)
SCOPE_BOXES = {
    "scope-enterprise": (80, 90, 1840, 820),
    "scope-data": (145, 165, 1710, 670),
    "scope-analytics": (210, 240, 1580, 520),
    "scope-operations": (275, 315, 1450, 370),
    "scope-project": (340, 390, 1320, 220),
}
ARTIFACT_BY_SCOPE = {
    "scope-enterprise": "artifact-enterprise-policy",
    "scope-data": "artifact-data-standard",
    "scope-analytics": "artifact-metric-dictionary",
    "scope-operations": "artifact-deployment-rule",
    "scope-project": "artifact-project-config",
}
ARTIFACT_POSITIONS = {
    "scope-enterprise": (1840, 852),
    "scope-data": (1775, 777),
    "scope-analytics": (1710, 702),
    "scope-operations": (1645, 627),
}


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_nested(plan):
    projection = plan.get("semantic_projection", {})
    groups = projection.get("containment_contract", {}).get("nested_groups", [])
    nodes = projection.get("nodes", [])
    return {item.get("id") for item in groups} == set(SCOPE_ORDER) and len(nodes) == 5


def _contained(inner, outer, padding=0):
    ix, iy, iw, ih = inner
    ox, oy, ow, oh = outer
    return ix >= ox + padding and iy >= oy + padding and ix + iw <= ox + ow - padding and iy + ih <= oy + oh - padding


def layout_nested(plan):
    projection = plan["semantic_projection"]
    groups = {item["id"]: item for item in projection["containment_contract"]["nested_groups"]}
    nodes = {item["id"]: item for item in projection["nodes"]}
    _require(set(groups) == set(SCOPE_ORDER), "D-125 scope inventory mismatch")
    _require(set(nodes) == set(ARTIFACT_BY_SCOPE.values()), "D-125 artifact inventory mismatch")

    scopes = {}
    for index, scope_id in enumerate(SCOPE_ORDER):
        group = groups[scope_id]
        parent = None if index == 0 else SCOPE_ORDER[index - 1]
        _require(group.get("parent_group_id") == parent, f"D-125 parent mismatch: {scope_id}")
        artifact_id = ARTIFACT_BY_SCOPE[scope_id]
        _require(artifact_id in group["member_ids"], f"D-125 artifact membership mismatch: {scope_id}")
        if index < len(SCOPE_ORDER) - 1:
            _require(SCOPE_ORDER[index + 1] in group["member_ids"], f"D-125 child membership mismatch: {scope_id}")
        scopes[scope_id] = {
            "id": scope_id,
            "order": index,
            "label": group["label"],
            "parent": parent,
            "artifact_id": artifact_id,
            "box": SCOPE_BOXES[scope_id],
            "focal": scope_id == "scope-project",
        }

    result = {"width": WIDTH, "height": HEIGHT, "scopes": scopes, "nodes": nodes}
    validate_nested_layout(result)
    return result


def validate_nested_layout(layout):
    _require(len(layout["scopes"]) == 5 and len(layout["nodes"]) == 5, "D-125 count mismatch")
    _require(sum(item["focal"] for item in layout["scopes"].values()) == 1, "D-125 focal mismatch")
    for index in range(1, len(SCOPE_ORDER)):
        child = layout["scopes"][SCOPE_ORDER[index]]["box"]
        parent = layout["scopes"][SCOPE_ORDER[index - 1]]["box"]
        _require(_contained(child, parent, 60), f"D-125 insufficient containment ring: {SCOPE_ORDER[index]}")
    for scope_id, (x, y) in ARTIFACT_POSITIONS.items():
        _require(_contained((x, y, 34, 42), layout["scopes"][scope_id]["box"], 12), f"D-125 artifact escapes scope: {scope_id}")


def nested_css(tokens):
    return '''
.ns-scope{fill:var(--surface);stroke:var(--border);stroke-width:1}.ns-scope.depth-1,.ns-scope.depth-3{fill:var(--surface-alt)}.ns-scope.depth-2{fill:var(--canvas)}.ns-scope.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}
.ns-tab{fill:var(--canvas);stroke:none}.ns-tab.focal{fill:var(--surface)}.ns-label{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.6px;fill:var(--muted)}.ns-label.focal{fill:var(--accent-text)}
.ns-file{fill:var(--canvas);stroke:var(--connector);stroke-width:1;stroke-linejoin:round}.ns-file-fold{fill:none;stroke:var(--connector);stroke-width:1;stroke-linejoin:round}.ns-file-label{font:650 11px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}
.ns-core-title{font:650 30px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.ns-core-subtitle{font:600 14px Menlo,Monaco,monospace;letter-spacing:.5px;fill:var(--muted)}
.ns-leader{fill:none;stroke:var(--muted);stroke-width:1;stroke-dasharray:7 7;stroke-linecap:round}.ns-leader-dot{fill:var(--text)}.ns-note{font:italic 18px Georgia,'Times New Roman',serif;fill:var(--text)}
.ns-footer-rule{stroke:var(--grid);stroke-width:1}.ns-legend-text{font:650 13px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.ns-legend-swatch{fill:var(--surface);stroke:var(--border);stroke-width:1}.ns-legend-swatch.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}.ns-details{overflow-x:auto}.ns-details table{min-width:820px}
'''


def _file_icon(x, y, label):
    return (
        f'<g data-artifact-glyph="1"><path class="ns-file" d="M{x} {y} H{x+23} L{x+34} {y+11} V{y+42} H{x} Z"/>'
        f'<path class="ns-file-fold" d="M{x+23} {y} V{y+11} H{x+34}"/>'
        f'<text class="ns-file-label" x="{x-12}" y="{y+27}" text-anchor="end">{escape(label)}</text></g>'
    )


def render_nested(plan):
    layout = layout_nested(plan)
    parts = ['<g data-nested-contract="D-125-five-depth-inheritance" data-template-contract="p18r6-review17-preserved" data-scope-count="5" data-artifact-count="5" data-max-depth="4">']
    for scope_id in SCOPE_ORDER:
        scope = layout["scopes"][scope_id]
        x, y, width, height = scope["box"]
        scope_class = f'ns-scope depth-{scope["order"]}' + (' focal' if scope["focal"] else '')
        tab_class = 'ns-tab focal' if scope["focal"] else 'ns-tab'
        label_class = 'ns-label focal' if scope["focal"] else 'ns-label'
        tab_width = 330 if scope["order"] == 0 else 290
        parts.append(
            f'<g data-scope-id="{scope_id}" data-depth="{scope["order"]}" data-parent-scope="{scope["parent"] or "none"}" data-focal="{str(scope["focal"]).lower()}">'
            f'<rect class="{scope_class}" x="{x}" y="{y}" width="{width}" height="{height}" rx="18"/>'
            f'<rect class="{tab_class}" x="{x+32}" y="{y-14}" width="{tab_width}" height="30"/>'
            f'<text class="{label_class}" x="{x+48}" y="{y+6}">{escape(scope["label"])}</text>'
            '</g>'
        )
    for scope_id, (x, y) in ARTIFACT_POSITIONS.items():
        artifact_id = ARTIFACT_BY_SCOPE[scope_id]
        parts.append(f'<g data-artifact-id="{artifact_id}" data-owner-scope="{scope_id}">{_file_icon(x, y, layout["nodes"][artifact_id]["label"])}</g>')
    core = layout["scopes"]["scope-project"]["box"]
    cx = core[0] + core[2] / 2
    parts.append(
        f'<g data-artifact-id="artifact-project-config" data-owner-scope="scope-project" data-focal="true">'
        f'<text class="ns-core-title" x="{cx:g}" y="480" text-anchor="middle">Cấu hình dự án</text>'
        f'<text class="ns-core-subtitle" x="{cx:g}" y="522" text-anchor="middle">kế thừa bốn cấp bên ngoài</text></g>'
        '<path class="ns-leader" data-annotation-leader="inheritance" d="M1000 405 L1510 118"/>'
        '<circle class="ns-leader-dot" cx="1000" cy="405" r="4"/>'
        '<text class="ns-note" x="1530" y="108">Quy tắc gần nhất được ưu tiên</text>'
        '<line class="ns-footer-rule" x1="80" y1="952" x2="1920" y2="952"/>'
        '<rect class="ns-legend-swatch" x="80" y="980" width="28" height="22" rx="5"/><text class="ns-legend-text" x="122" y="996">Phạm vi kế thừa</text>'
        '<rect class="ns-legend-swatch focal" x="330" y="980" width="28" height="22" rx="5"/><text class="ns-legend-text" x="372" y="996">Phạm vi hiện hành</text>'
        '<path class="ns-file" d="M615 980 H632 L643 991 V1002 H615 Z"/><path class="ns-file-fold" d="M632 980 V991 H643"/><text class="ns-legend-text" x="660" y="996">Artifact cấu hình</text>'
        '<text class="ns-legend-text" x="1920" y="996" text-anchor="end">Khung trong kế thừa các cấp bao ngoài</text>'
        '</g>'
    )
    return ''.join(parts)


def validate_nested_svg(svg):
    root = ET.fromstring(svg)
    scopes = root.findall('.//*[@data-scope-id]')
    artifacts = root.findall('.//*[@data-artifact-id]')
    leaders = root.findall('.//*[@data-annotation-leader]')
    _require(len(scopes) == 5, "D-125 serialized scope count mismatch")
    _require(len(artifacts) == 5, "D-125 serialized artifact count mismatch")
    _require(len(leaders) == 1, "D-125 serialized annotation leader mismatch")
    _require(sum(item.attrib["data-focal"] == "true" for item in scopes) == 1, "D-125 serialized focal scope mismatch")
    _require([int(item.attrib["data-depth"]) for item in scopes] == list(range(5)), "D-125 serialized depth mismatch")
    return {"scopes": 5, "artifacts": 5, "max_depth": 4, "focal_scopes": 1, "annotation_leaders": 1}


def nested_table(plan):
    layout = layout_nested(plan)
    rows = []
    for scope_id in SCOPE_ORDER:
        scope = layout["scopes"][scope_id]
        artifact_id = scope["artifact_id"]
        rows.append((scope["order"], scope_id, scope["label"], scope["parent"] or "—", artifact_id, layout["nodes"][artifact_id]["label"]))
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows)
    return '<details class="ns-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Depth</th><th>Scope ID</th><th>Phạm vi</th><th>Scope cha</th><th>Artifact ID</th><th>Artifact</th></tr></thead><tbody>' + body + '</tbody></table></details>'
