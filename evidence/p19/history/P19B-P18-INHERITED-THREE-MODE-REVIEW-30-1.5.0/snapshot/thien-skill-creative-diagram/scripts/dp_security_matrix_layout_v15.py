"""D-089 content-fit five-by-five permission matrix from semantic cells."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


ROLE_KEYS = (
    "Kỹ sư dữ liệu · GRP-DATA-ENG",
    "Nhà khoa học dữ liệu · GRP-DATA-SCI",
    "Chuyên viên phân tích · GRP-ANALYST",
    "Quản trị nền tảng · GRP-PLATFORM-ADMIN",
    "Đối tác bên ngoài · GRP-PARTNER",
)
COMPONENT_KEYS = (
    "Kho đối tượng · S3",
    "Dịch vụ truy vấn · SQL",
    "Notebook · PY",
    "Không gian BI · DASH",
    "Bộ điều phối · DAG",
)
PERMISSIONS = ("Admin", "Write", "Read", "None")
FOCAL_CELL_ID = "cell-external-partner-bi-workspace"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _split_identity(value):
    _require(isinstance(value, str) and value.count("|") == 1, "D-089 cell identity must be role|component")
    return tuple(value.split("|", 1))


def _split_key(value):
    parts = value.rsplit(" · ", 1)
    _require(len(parts) == 2 and all(parts), "D-089 header key requires name and code")
    return tuple(parts)


def _permission(value):
    permission, *detail = value.split(" · ", 1)
    _require(permission in PERMISSIONS, "D-089 permission label must be Admin, Write, Read, or None")
    return permission, detail[0] if detail else ""


def is_detailed_dp_security_matrix(plan):
    cells = plan.get("semantic_projection", {}).get("spatial_contract", {}).get("permission_cells", [])
    return len(cells) == 25 and any(item.get("id") == FOCAL_CELL_ID for item in cells)


def layout_dp_security_matrix(plan):
    cells = plan["semantic_projection"]["spatial_contract"]["permission_cells"]
    _require(len(cells) == 25, "D-089 requires exactly 25 permission cells")
    indexed = {}
    for item in cells:
        role, component = _split_identity(item.get("secondary_label"))
        permission, detail = _permission(item.get("label", ""))
        _require(role in ROLE_KEYS and component in COMPONENT_KEYS, "D-089 role or component key mismatch")
        _require((role, component) not in indexed, "D-089 duplicate role-component pair")
        _require(item.get("state") == ("deny" if permission == "None" else "allow"), "D-089 semantic allow/deny state mismatch")
        indexed[(role, component)] = {**item, "permission": permission, "detail": detail}
    expected = {(role, component) for role in ROLE_KEYS for component in COMPONENT_KEYS}
    _require(set(indexed) == expected, "D-089 matrix is not rectangular")
    focal = indexed[(ROLE_KEYS[-1], COMPONENT_KEYS[3])]
    _require(focal["id"] == FOCAL_CELL_ID and focal["permission"] == "Read" and focal["detail"] == "Dashboard được chia sẻ", "D-089 partner BI boundary mismatch")
    _require(all(not item["detail"] for item in indexed.values() if item["id"] != FOCAL_CELL_ID), "D-089 unexpected secondary permission detail")

    width, height = 2000, 820
    label_x, label_width = 28, 372
    column_x, column_width, column_gap = 424, 292, 18
    header_y, header_height = 76, 108
    row_y, row_height, row_gap = 214, 72, 12
    rendered = []
    for row_index, component in enumerate(COMPONENT_KEYS):
        for column_index, role in enumerate(ROLE_KEYS):
            rendered.append({
                **indexed[(role, component)],
                "role": role,
                "component": component,
                "x": column_x + column_index * (column_width + column_gap),
                "y": row_y + row_index * (row_height + row_gap),
                "width": column_width,
                "height": row_height,
                "focal": indexed[(role, component)]["id"] == FOCAL_CELL_ID,
            })
    return {
        "width": width, "height": height,
        "label_x": label_x, "label_width": label_width,
        "column_x": column_x, "column_width": column_width, "column_gap": column_gap,
        "header_y": header_y, "header_height": header_height,
        "row_y": row_y, "row_height": row_height, "row_gap": row_gap,
        "roles": ROLE_KEYS, "components": COMPONENT_KEYS, "cells": rendered,
    }


def dp_security_matrix_css(tokens):
    return """
    .security-matrix-header{fill:var(--text);stroke:var(--text);stroke-width:1.8}
    .security-matrix-header-title{font:700 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--canvas)}
    .security-matrix-header-code{font:600 13px Menlo,Monaco,monospace;fill:var(--canvas);opacity:.78}
    .security-matrix-corner,.security-matrix-row{fill:var(--surface);stroke:var(--border);stroke-width:1.6}
    .security-matrix-corner-title,.security-matrix-row-title{font:700 18px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .security-matrix-corner-code,.security-matrix-row-code{font:600 13px Menlo,Monaco,monospace;fill:var(--muted)}
    .security-matrix-cell{stroke:var(--border);stroke-width:1.5}
    .security-matrix-cell.is-admin{fill:color-mix(in srgb,var(--connector) 15%,var(--surface))}
    .security-matrix-cell.is-write{fill:var(--surface)}
    .security-matrix-cell.is-read{fill:color-mix(in srgb,var(--connector) 9%,var(--surface))}
    .security-matrix-cell.is-none{fill:color-mix(in srgb,var(--canvas) 80%,var(--surface));opacity:.72}
    .security-matrix-cell.is-focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.6;opacity:1}
    .security-matrix-permission{font:650 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .security-matrix-permission.is-admin{font-weight:750}.security-matrix-permission.is-none{fill:var(--muted)}
    .security-matrix-permission.is-focal,.security-matrix-detail{fill:var(--accent-text)}
    .security-matrix-detail{font:600 11px Menlo,Monaco,monospace}
    .security-matrix-rule{stroke:var(--grid);stroke-width:1.3}
    .security-matrix-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:2px;fill:var(--muted)}
    .security-matrix-legend-label{font:550 14px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}
    .security-matrix-details{overflow-x:auto}.security-matrix-details table{min-width:980px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_dp_security_matrix(plan):
    layout = layout_dp_security_matrix(plan)
    parts = ['<g data-security-matrix-contract="D-089-five-by-five-role-component">']
    x0, cw, gap = layout["column_x"], layout["column_width"], layout["column_gap"]
    hy, hh = layout["header_y"], layout["header_height"]
    lx, lw = layout["label_x"], layout["label_width"]
    parts.append(f'<rect class="security-matrix-corner" x="{lx}" y="{hy}" width="{lw}" height="{hh}" rx="12"/>')
    parts.append(_text(lx + lw / 2, hy + 44, "Thành phần", "security-matrix-corner-title"))
    parts.append(_text(lx + lw / 2, hy + 73, "vs. nhóm quyền", "security-matrix-corner-code"))
    for index, role in enumerate(layout["roles"]):
        name, code = _split_key(role)
        x = x0 + index * (cw + gap)
        parts.append(f'<rect class="security-matrix-header" data-role-header="{escape(role, quote=True)}" x="{x}" y="{hy}" width="{cw}" height="{hh}" rx="12"/>')
        parts.append(_text(x + cw / 2, hy + 44, name, "security-matrix-header-title"))
        parts.append(_text(x + cw / 2, hy + 74, code, "security-matrix-header-code"))
    for row_index, component in enumerate(layout["components"]):
        name, code = _split_key(component)
        y = layout["row_y"] + row_index * (layout["row_height"] + layout["row_gap"])
        parts.append(f'<rect class="security-matrix-row" data-component-header="{escape(component, quote=True)}" x="{lx}" y="{y}" width="{lw}" height="{layout["row_height"]}" rx="9"/>')
        parts.append(_text(lx + 22, y + 44, name, "security-matrix-row-title", "start"))
        parts.append(_text(lx + lw - 22, y + 44, code, "security-matrix-row-code", "end"))
    for cell in layout["cells"]:
        permission_class = cell["permission"].lower()
        focal = " is-focal" if cell["focal"] else ""
        attrs = (
            f'data-matrix-cell-id="{escape(cell["id"], quote=True)}" '
            f'data-role="{escape(cell["role"], quote=True)}" '
            f'data-component="{escape(cell["component"], quote=True)}" '
            f'data-permission="{cell["permission"]}" data-focal="{str(cell["focal"]).lower()}"'
        )
        parts.append(f'<rect class="security-matrix-cell is-{permission_class}{focal}" {attrs} x="{cell["x"]}" y="{cell["y"]}" width="{cell["width"]}" height="{cell["height"]}" rx="9"/>')
        text_y = cell["y"] + (31 if cell["detail"] else 43)
        parts.append(_text(cell["x"] + cell["width"] / 2, text_y, cell["permission"], f"security-matrix-permission is-{permission_class}{focal}"))
        if cell["detail"]:
            parts.append(_text(cell["x"] + cell["width"] / 2, cell["y"] + 54, cell["detail"], "security-matrix-detail"))
    rule_y, legend_y = 668, 706
    parts.append(f'<line class="security-matrix-rule" x1="28" y1="{rule_y}" x2="1976" y2="{rule_y}"/>')
    parts.append(_text(28, legend_y, "CHÚ GIẢI", "security-matrix-legend-title", "start"))
    legend = (("Admin", 182), ("Write", 430), ("Read", 678), ("None", 926))
    for permission, x in legend:
        css = permission.lower()
        parts.append(f'<rect class="security-matrix-cell is-{css}" x="{x}" y="{legend_y-21}" width="28" height="24" rx="5"/>')
        parts.append(_text(x + 42, legend_y - 3, permission, "security-matrix-legend-label", "start"))
    parts.append(f'<rect class="security-matrix-cell is-focal" x="1174" y="{legend_y-21}" width="28" height="24" rx="5"/>')
    parts.append(_text(1216, legend_y - 3, "Boundary Read của đối tác", "security-matrix-legend-label", "start"))
    parts.append(_text(1976, 780, "25 ô · 5 vai trò × 5 thành phần", "security-matrix-legend-title", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_dp_security_matrix_svg(svg):
    root = ET.fromstring(svg)
    cells = root.findall(".//*[@data-matrix-cell-id]")
    _require(len(cells) == 25, "Serialized D-089 cell count mismatch")
    roles = {item.attrib["data-role"] for item in cells}
    components = {item.attrib["data-component"] for item in cells}
    pairs = {(item.attrib["data-role"], item.attrib["data-component"]) for item in cells}
    _require(roles == set(ROLE_KEYS) and components == set(COMPONENT_KEYS), "Serialized D-089 headers mismatch")
    _require(len(pairs) == 25, "Serialized D-089 duplicate matrix pair")
    permissions = [item.attrib["data-permission"] for item in cells]
    _require({permission: permissions.count(permission) for permission in PERMISSIONS} == {"Admin": 5, "Write": 7, "Read": 7, "None": 6}, "Serialized D-089 permission distribution mismatch")
    focal = [item for item in cells if item.attrib.get("data-focal") == "true"]
    _require(len(focal) == 1 and focal[0].attrib["data-matrix-cell-id"] == FOCAL_CELL_ID, "Serialized D-089 focal boundary mismatch")
    _require(len(root.findall(".//*[@data-role-header]")) == 5 and len(root.findall(".//*[@data-component-header]")) == 5, "Serialized D-089 header count mismatch")
    return {"cells": 25, "roles": 5, "components": 5, "focal": 1}


def dp_security_matrix_table(plan):
    layout = layout_dp_security_matrix(plan)
    rows = []
    for cell in layout["cells"]:
        role_name, role_code = _split_key(cell["role"])
        component_name, component_code = _split_key(cell["component"])
        scope = cell["detail"] or ("Không cấp quyền" if cell["permission"] == "None" else "Theo phạm vi vai trò")
        rows.append(
            "<tr>"
            f'<td>{escape(component_name)} <code>{escape(component_code)}</code></td>'
            f'<td>{escape(role_name)} <code>{escape(role_code)}</code></td>'
            f'<td>{escape(cell["permission"])}</td><td>{escape(scope)}</td>'
            "</tr>"
        )
    return (
        '<details class="security-matrix-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Đủ 25 giao điểm vai trò–thành phần. Mỗi trạng thái có nhãn chữ; ô coral xác định riêng boundary Read của đối tác.</p>'
        '<table><thead><tr><th scope="col">Thành phần</th><th scope="col">Vai trò / nhóm</th>'
        '<th scope="col">Quyền</th><th scope="col">Phạm vi</th></tr></thead><tbody>'
        + "".join(rows) + "</tbody></table></details>"
    )
