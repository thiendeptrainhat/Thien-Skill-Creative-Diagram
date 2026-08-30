"""D-099 content-fit Wardley map with visibility, evolution and dependency geometry."""
from __future__ import annotations

from html import escape
import math
import xml.etree.ElementTree as ET


EXPECTED_COMPONENT_IDS = (
    "component-answer",
    "component-chat",
    "component-orchestrator",
    "component-evaluation",
    "component-knowledge",
    "component-model-api",
    "component-compute",
    "component-object-store",
)
EXPECTED_DEPENDENCY_IDS = (
    "dependency-answer-chat",
    "dependency-orchestrator-chat",
    "dependency-evaluation-chat",
    "dependency-evaluation-model",
    "dependency-orchestrator-knowledge",
    "dependency-orchestrator-model",
    "dependency-knowledge-model",
    "dependency-model-compute",
    "dependency-model-store",
)
EXPECTED_AXES = {"wardley-evolution", "wardley-value"}
EXPECTED_ANNOTATION = "annotation-evolving-orchestrator"
FOCAL_COMPONENT = "component-orchestrator"
STAGES = (
    ("Khởi nguyên", 0.00, 0.25),
    ("Tự xây dựng", 0.25, 0.50),
    ("Sản phẩm", 0.50, 0.75),
    ("Hàng hóa", 0.75, 1.00),
)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def is_detailed_wardley_map(plan):
    components = plan.get("semantic_projection", {}).get("spatial_contract", {}).get("wardley_components", [])
    return tuple(item.get("id") for item in components) == EXPECTED_COMPONENT_IDS


def layout_wardley_map(plan):
    projection = plan["semantic_projection"]
    spatial = projection["spatial_contract"]
    components = spatial["wardley_components"]
    nodes = {item["id"]: item for item in projection["nodes"]}
    edges = projection["edges"]
    axes = {item["id"]: item for item in spatial["axes"]}
    annotations = {item["id"]: item for item in projection["annotations"]}
    _require(tuple(item["id"] for item in components) == EXPECTED_COMPONENT_IDS, "D-099 component order mismatch")
    _require(set(nodes) == set(EXPECTED_COMPONENT_IDS), "D-099 component inventory mismatch")
    _require(tuple(item["id"] for item in edges) == EXPECTED_DEPENDENCY_IDS, "D-099 dependency inventory mismatch")
    _require(set(axes) == EXPECTED_AXES, "D-099 requires exact visibility and evolution axes")
    _require(set(annotations) == {EXPECTED_ANNOTATION}, "D-099 requires one evolving annotation")
    _require(annotations[EXPECTED_ANNOTATION].get("target_ids") == [FOCAL_COMPONENT], "D-099 evolving target mismatch")
    _require(
        axes["wardley-evolution"].get("dimension") == "x"
        and axes["wardley-value"].get("dimension") == "y"
        and all(axes[key].get("scale") == "linear" for key in EXPECTED_AXES),
        "D-099 axis dimension/scale mismatch",
    )
    _require(
        all(axes[key].get("domain_min") == 0 and axes[key].get("domain_max") == 1 for key in EXPECTED_AXES),
        "D-099 axes must use normalized 0–1 domains",
    )
    for item in components:
        _require(
            all(isinstance(item.get(key), (int, float)) and math.isfinite(item[key]) and 0 <= item[key] <= 1 for key in ("evolution", "value_chain_position")),
            f"D-099 invalid normalized position: {item['id']}",
        )
    for edge in edges:
        _require(edge["kind"] == "dependency" and edge["source"] in nodes and edge["target"] in nodes, f"D-099 invalid dependency: {edge['id']}")

    width, height = 2000, 980
    plot = {"left": 230.0, "top": 126.0, "right": 1880.0, "bottom": 706.0}
    label_offsets = {
        "component-answer": (0, -28, "middle"),
        "component-chat": (0, -28, "middle"),
        "component-orchestrator": (0, -28, "middle"),
        "component-evaluation": (0, -28, "middle"),
        "component-knowledge": (0, -28, "middle"),
        "component-model-api": (0, -28, "middle"),
        "component-compute": (0, -28, "middle"),
        "component-object-store": (28, 7, "start"),
    }
    positioned = []
    for item in components:
        x = plot["left"] + item["evolution"] * (plot["right"] - plot["left"])
        y = plot["bottom"] - item["value_chain_position"] * (plot["bottom"] - plot["top"])
        dx, dy, anchor = label_offsets[item["id"]]
        positioned.append({
            **item,
            "label": nodes[item["id"]]["label"],
            "x": x,
            "y": y,
            "label_x": x + dx,
            "label_y": y + dy,
            "label_anchor": anchor,
            "state": "evolving" if item["id"] == FOCAL_COMPONENT else "standard",
        })
    by_id = {item["id"]: item for item in positioned}
    dependencies = [{**edge, "source_point": by_id[edge["source"]], "target_point": by_id[edge["target"]]} for edge in edges]
    evolution_target = min(by_id[FOCAL_COMPONENT]["evolution"] + 0.13, 0.49)
    evolution_x = plot["left"] + evolution_target * (plot["right"] - plot["left"])
    return {
        "width": width,
        "height": height,
        "plot": plot,
        "components": positioned,
        "dependencies": dependencies,
        "axes": axes,
        "annotation": annotations[EXPECTED_ANNOTATION],
        "evolution_target_x": evolution_x,
        "stages": STAGES,
    }


def wardley_map_css(tokens):
    return """
    .wm-axis{fill:none;stroke:var(--connector);stroke-width:1.8}
    .wm-stage-line{stroke:var(--grid);stroke-width:1.3;stroke-dasharray:8 8}
    .wm-dependency{fill:none;stroke:var(--connector);stroke-width:2.1;stroke-linecap:round;opacity:.92}
    .wm-component{fill:var(--canvas);stroke:var(--text);stroke-width:2.4}
    .wm-component.is-evolving{stroke:var(--accent);stroke-width:3.2}
    .wm-evolution{fill:none;stroke:var(--accent);stroke-width:3.2;stroke-dasharray:11 9;stroke-linecap:round}
    .wm-label{font:700 18px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .wm-label.is-evolving{fill:var(--accent-text)}
    .wm-axis-label,.wm-stage,.wm-note,.wm-state{font:700 13px Menlo,Monaco,monospace;fill:var(--muted);letter-spacing:2px}
    .wm-state{fill:var(--accent-text);font-size:12px;letter-spacing:1.4px}
    .wm-rule{stroke:var(--grid);stroke-width:1.3}
    .wm-details{overflow-x:auto}.wm-details table{min-width:980px}
    """


def _text(x, y, value, css, anchor="middle"):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_wardley_map(plan):
    layout = layout_wardley_map(plan)
    plot = layout["plot"]
    parts = ['<g data-wardley-map-contract="D-099-visibility-evolution-value-chain">']
    parts.append('<defs><marker id="wm-evolution-arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker></defs>')
    parts.append(f'<line class="wm-axis" data-axis-id="wardley-value" x1="{plot["left"]}" y1="{plot["bottom"]}" x2="{plot["left"]}" y2="{plot["top"]}"/>')
    parts.append(f'<line class="wm-axis" data-axis-id="wardley-evolution" x1="{plot["left"]}" y1="{plot["bottom"]}" x2="{plot["right"]}" y2="{plot["bottom"]}"/>')
    parts.append(_text(142, 88, "NHÌN THẤY BỞI", "wm-axis-label"))
    parts.append(_text(142, 110, "NGƯỜI DÙNG", "wm-axis-label"))
    parts.append(_text(142, 742, "ẨN / HẠ TẦNG", "wm-axis-label"))
    for boundary in (0.25, 0.50, 0.75):
        x = plot["left"] + boundary * (plot["right"] - plot["left"])
        parts.append(f'<line class="wm-stage-line" data-stage-boundary="{boundary:.2f}" x1="{x:.3f}" y1="{plot["top"]}" x2="{x:.3f}" y2="{plot["bottom"]}"/>')
    for label, start, end in layout["stages"]:
        x = plot["left"] + ((start + end) / 2) * (plot["right"] - plot["left"])
        parts.append(_text(x, 748, label.upper(), "wm-stage"))
    for edge in layout["dependencies"]:
        source, target = edge["source_point"], edge["target_point"]
        parts.append(
            f'<line class="wm-dependency" data-dependency-id="{escape(edge["id"], quote=True)}" '
            f'data-source="{escape(edge["source"], quote=True)}" data-target="{escape(edge["target"], quote=True)}" '
            f'x1="{source["x"]:.3f}" y1="{source["y"]:.3f}" x2="{target["x"]:.3f}" y2="{target["y"]:.3f}"/>'
        )
    focal = next(item for item in layout["components"] if item["id"] == FOCAL_COMPONENT)
    parts.append(
        f'<line class="wm-evolution" data-evolution-signal="true" data-source="{FOCAL_COMPONENT}" '
        f'x1="{focal["x"] + 18:.3f}" y1="{focal["y"]:.3f}" x2="{layout["evolution_target_x"]:.3f}" y2="{focal["y"]:.3f}" marker-end="url(#wm-evolution-arrow)"/>'
    )
    for item in layout["components"]:
        suffix = " is-evolving" if item["state"] == "evolving" else ""
        parts.append(
            f'<circle class="wm-component{suffix}" data-component-id="{escape(item["id"], quote=True)}" '
            f'data-state="{item["state"]}" data-evolution="{item["evolution"]:.2f}" '
            f'data-visibility="{item["value_chain_position"]:.2f}" cx="{item["x"]:.3f}" cy="{item["y"]:.3f}" r="13"/>'
        )
        parts.append(_text(item["label_x"], item["label_y"], item["label"], f'wm-label{suffix}', item["label_anchor"]))
        if item["state"] == "evolving":
            parts.append(_text(item["label_x"], item["label_y"] + 22, "ĐANG TIẾN HÓA", "wm-state", item["label_anchor"]))
    parts.append('<line class="wm-rule" x1="80" y1="844" x2="1920" y2="844"/>')
    parts.append('<circle class="wm-component" cx="104" cy="890" r="9"/>')
    parts.append(_text(132, 895, "THÀNH PHẦN", "wm-note", "start"))
    parts.append('<line class="wm-dependency" x1="390" y1="890" x2="448" y2="890"/>')
    parts.append(_text(470, 895, "PHỤ THUỘC", "wm-note", "start"))
    parts.append('<circle class="wm-component is-evolving" cx="760" cy="890" r="9"/>')
    parts.append('<line class="wm-evolution" x1="780" y1="890" x2="842" y2="890" marker-end="url(#wm-evolution-arrow)"/>')
    parts.append(_text(864, 895, "ĐANG TIẾN HÓA", "wm-note", "start"))
    parts.append(_text(1920, 895, "VỊ TRÍ TRÊN TRỤC TIẾN HÓA LÀ TÍN HIỆU CHIẾN LƯỢC", "wm-note", "end"))
    parts.append("</g>")
    return "".join(parts)


def validate_wardley_map_svg(svg):
    root = ET.fromstring(svg)
    components = root.findall(".//*[@data-component-id]")
    dependencies = root.findall(".//*[@data-dependency-id]")
    axes = root.findall(".//*[@data-axis-id]")
    signals = root.findall(".//*[@data-evolution-signal]")
    _require(tuple(item.attrib["data-component-id"] for item in components) == EXPECTED_COMPONENT_IDS, "Serialized D-099 component order mismatch")
    _require(tuple(item.attrib["data-dependency-id"] for item in dependencies) == EXPECTED_DEPENDENCY_IDS, "Serialized D-099 dependency order mismatch")
    _require({item.attrib["data-axis-id"] for item in axes} == EXPECTED_AXES, "Serialized D-099 axis mismatch")
    _require(len(root.findall(".//*[@data-stage-boundary]")) == 3, "D-099 needs three evolution boundaries")
    _require(len(signals) == 1 and signals[0].attrib.get("data-source") == FOCAL_COMPONENT, "D-099 needs one evolving signal")
    _require(sum(item.attrib.get("data-state") == "evolving" for item in components) == 1, "D-099 needs one evolving component")
    _require(all("marker-end" not in item.attrib for item in dependencies + axes), "D-099 axes/dependencies must be arrow-free")
    _require(signals[0].attrib.get("marker-end") == "url(#wm-evolution-arrow)", "D-099 evolution arrow missing")
    for item in components:
        _require(0 <= float(item.attrib["data-evolution"]) <= 1 and 0 <= float(item.attrib["data-visibility"]) <= 1, "D-099 serialized coordinate outside normalized domain")
    return {"components": 8, "dependencies": 9, "axes": 2, "boundaries": 3, "evolving": 1}


def wardley_map_table(plan):
    layout = layout_wardley_map(plan)
    component_rows = []
    for item in layout["components"]:
        state = "Đang tiến hóa" if item["state"] == "evolving" else "Ổn định tại vị trí hiện tại"
        component_rows.append(
            "<tr>"
            f'<td>{escape(item["id"])}</td><td>{escape(item["label"])}</td>'
            f'<td>{item["value_chain_position"]:.2f}</td><td>{item["evolution"]:.2f}</td><td>{state}</td>'
            "</tr>"
        )
    dependency_rows = [
        "<tr>"
        f'<td>Phụ thuộc</td><td>{escape(item["id"])}</td><td>{escape(item["source"])}</td>'
        f'<td colspan="2">{escape(item["target"])}</td><td>Không mũi tên</td>'
        "</tr>"
        for item in layout["dependencies"]
    ]
    return (
        '<details class="wm-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary>'
        '<p>Visibility và evolution dùng miền chuẩn hóa 0–1. Đường phụ thuộc không có mũi tên; chỉ tín hiệu tiến hóa của Điều phối tác vụ có mũi tên nét đứt.</p>'
        '<table><thead><tr><th scope="col">Loại</th><th scope="col">ID</th><th scope="col">Nhãn / nguồn</th>'
        '<th scope="col">Visibility / đích</th><th scope="col">Evolution</th><th scope="col">Trạng thái</th></tr></thead><tbody>'
        + "".join(
            row.replace("<tr><td>", "<tr><td>Thành phần</td><td>", 1)
            for row in component_rows
        )
        + "".join(dependency_rows)
        + "</tbody></table></details>"
    )
