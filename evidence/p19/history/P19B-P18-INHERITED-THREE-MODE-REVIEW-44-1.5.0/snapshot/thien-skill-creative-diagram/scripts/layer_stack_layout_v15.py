"""D-124 detailed canonical layer-stack in the approved P-18 grammar."""

from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH = 2000
HEIGHT = 1250
LAYER_ORDER = tuple(f"stack-level-{level}" for level in (5, 4, 3, 2, 1))
LAYER_Y = {"stack-level-5": 60, "stack-level-4": 262, "stack-level-3": 474, "stack-level-2": 756, "stack-level-1": 968}
LAYER_HEIGHT = {"stack-level-5": 170, "stack-level-4": 180, "stack-level-3": 250, "stack-level-2": 180, "stack-level-1": 180}
LAYER_BOX_X = 170
LAYER_BOX_WIDTH = 1770
CONTENT_X = 570
CONTENT_WIDTH = 1300
FOCAL_LAYER = "stack-level-4"
DOMAIN_ORDER = ("domain-models", "domain-knowledge")
MODULE_COUNTS = {"stack-level-5": 4, "stack-level-4": 5, "stack-level-3": 6, "stack-level-2": 4, "stack-level-1": 4}


def _require(value, message):
    if not value:
        raise ValueError(message)


def _split_lane_label(value):
    parts = [part.strip() for part in value.split("|")]
    _require(len(parts) == 3, "D-124 layer label must contain code, title and scope")
    return parts


def is_detailed_layer_stack(plan):
    contract = plan.get("semantic_projection", {}).get("containment_contract", {})
    lanes = contract.get("ordered_layers", [])
    nodes = plan.get("semantic_projection", {}).get("nodes", [])
    return {item.get("id") for item in lanes} == set(LAYER_ORDER) and len(nodes) == 23


def _module_boxes(member_ids, y, *, x=CONTENT_X, width=CONTENT_WIDTH, height=64, gap=16):
    count = len(member_ids)
    card_width = (width - gap * (count - 1)) / count
    return {
        module_id: (x + index * (card_width + gap), y, card_width, height)
        for index, module_id in enumerate(member_ids)
    }


def layout_layer_stack(plan):
    projection = plan["semantic_projection"]
    contract = projection["containment_contract"]
    lanes = {item["id"]: item for item in contract["ordered_layers"]}
    nodes = {item["id"]: item for item in projection["nodes"]}
    groups = {item["id"]: item for item in contract["nested_groups"]}
    edges = {item["id"]: item for item in projection["edges"]}
    _require(set(lanes) == set(LAYER_ORDER), "D-124 layer inventory mismatch")
    _require(len(nodes) == 23, "D-124 module inventory mismatch")
    _require(set(groups) == set(DOMAIN_ORDER), "D-124 intelligence-domain inventory mismatch")
    _require(len(edges) == 4, "D-124 dependency inventory mismatch")

    rows = {}
    module_owner = {}
    for order, layer_id in enumerate(LAYER_ORDER):
        lane = lanes[layer_id]
        _require(lane["order"] == order, f"D-124 layer order mismatch: {layer_id}")
        _require(len(lane["member_ids"]) == MODULE_COUNTS[layer_id], f"D-124 module count mismatch: {layer_id}")
        code, title, scope = _split_lane_label(lane["label"])
        y, height = LAYER_Y[layer_id], LAYER_HEIGHT[layer_id]
        for module_id in lane["member_ids"]:
            _require(module_id in nodes and module_id not in module_owner, f"D-124 module ownership mismatch: {module_id}")
            module_owner[module_id] = layer_id
        rows[layer_id] = {
            "id": layer_id,
            "order": order,
            "code": code,
            "title": title,
            "scope": scope,
            "member_ids": lane["member_ids"],
            "focal": layer_id == FOCAL_LAYER,
            "box": (LAYER_BOX_X, y, LAYER_BOX_WIDTH, height),
            "module_boxes": {},
        }

    _require(set(module_owner) == set(nodes), "D-124 every module must belong to exactly one layer")
    for layer_id in ("stack-level-5", "stack-level-4", "stack-level-2", "stack-level-1"):
        row = rows[layer_id]
        row["module_boxes"] = _module_boxes(row["member_ids"], row["box"][1] + 84)

    domain_boxes = {
        "domain-models": (560, LAYER_Y["stack-level-3"] + 72, 645, 154),
        "domain-knowledge": (1225, LAYER_Y["stack-level-3"] + 72, 645, 154),
    }
    for domain_id in DOMAIN_ORDER:
        member_ids = groups[domain_id]["member_ids"]
        _require(len(member_ids) == 3, f"D-124 domain membership mismatch: {domain_id}")
        _require(all(module_owner[item] == "stack-level-3" for item in member_ids), f"D-124 domain crosses layer: {domain_id}")
        x, y, width, height = domain_boxes[domain_id]
        rows["stack-level-3"]["module_boxes"].update(_module_boxes(member_ids, y + 70, x=x + 18, width=width - 36, height=62, gap=12))

    connectors = []
    for index, edge in enumerate(edges.values()):
        source_layer = module_owner[edge["source"]]
        target_layer = module_owner[edge["target"]]
        _require(LAYER_ORDER.index(target_layer) == LAYER_ORDER.index(source_layer) + 1, f"D-124 dependency must connect adjacent layers: {edge['id']}")
        source_y = LAYER_Y[source_layer] + LAYER_HEIGHT[source_layer]
        target_y = LAYER_Y[target_layer]
        connectors.append({"id": edge["id"], "source_layer": source_layer, "target_layer": target_layer, "x": 1055, "source_y": source_y, "target_y": target_y, "order": index})

    result = {
        "width": WIDTH,
        "height": HEIGHT,
        "rows": rows,
        "nodes": nodes,
        "groups": groups,
        "domain_boxes": domain_boxes,
        "module_owner": module_owner,
        "connectors": sorted(connectors, key=lambda item: LAYER_ORDER.index(item["source_layer"])),
    }
    validate_layer_stack_layout(result)
    return result


def _contained(inner, outer, padding=0):
    ix, iy, iw, ih = inner
    ox, oy, ow, oh = outer
    return ix >= ox + padding and iy >= oy + padding and ix + iw <= ox + ow - padding and iy + ih <= oy + oh - padding


def validate_layer_stack_layout(layout):
    _require(len(layout["rows"]) == 5 and len(layout["module_owner"]) == 23, "D-124 count mismatch")
    _require(sum(row["focal"] for row in layout["rows"].values()) == 1, "D-124 focal layer mismatch")
    for layer_id, row in layout["rows"].items():
        _require(len(row["module_boxes"]) == MODULE_COUNTS[layer_id], f"D-124 serialized module count mismatch: {layer_id}")
        for module_id, box in row["module_boxes"].items():
            _require(_contained(box, row["box"], 16), f"D-124 module escapes layer: {module_id}")
    for domain_id, domain_box in layout["domain_boxes"].items():
        _require(_contained(domain_box, layout["rows"]["stack-level-3"]["box"], 16), f"D-124 domain escapes intelligence layer: {domain_id}")
        for module_id in layout["groups"][domain_id]["member_ids"]:
            _require(_contained(layout["rows"]["stack-level-3"]["module_boxes"][module_id], domain_box, 16), f"D-124 module escapes domain: {module_id}")
    _require(len(layout["connectors"]) == 4 and all(item["x"] == 1055 for item in layout["connectors"]), "D-124 centered dependency mismatch")
    _require(all(item["source_y"] < item["target_y"] for item in layout["connectors"]), "D-124 dependency direction mismatch")


def layer_stack_css(tokens):
    return '''
.ls-axis,.ls-dependency{fill:none;stroke:var(--connector);stroke-width:1;stroke-linecap:round;stroke-linejoin:round}.ls-axis-label{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}
.ls-band{fill:var(--surface);stroke:var(--border);stroke-width:1.2}.ls-band.alt{fill:color-mix(in srgb,var(--surface-alt) 58%,var(--surface))}.ls-band.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}
.ls-level-badge{fill:var(--canvas);stroke:var(--border);stroke-width:.9}.ls-level-badge.focal{fill:var(--surface);stroke:var(--accent)}.ls-level{font:700 11px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--muted)}.ls-level.focal{fill:var(--accent-text)}
.ls-title{font:650 24px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.ls-scope{font:600 12px Menlo,Monaco,monospace;letter-spacing:.35px;fill:var(--muted)}.ls-scope.focal{fill:var(--accent-text)}
.ls-module{fill:var(--canvas);stroke:var(--connector);stroke-width:1;rx:10}.ls-module.focal{fill:var(--surface);stroke:var(--accent);stroke-width:1.2}.ls-module-label{font:650 14px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}
.ls-domain{fill:var(--surface-alt);stroke:var(--grid);stroke-width:1}.ls-domain-title{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--muted)}
.ls-focus-tag{fill:var(--accent);stroke:none}.ls-focus-tag-text{font:700 10px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--on-accent)}.ls-footer-rule{stroke:var(--grid);stroke-width:1}.ls-legend-text{font:650 13px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.ls-legend-swatch{fill:var(--surface);stroke:var(--border);stroke-width:1.2}.ls-legend-swatch.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.6}.ls-details{overflow-x:auto}.ls-details table{min-width:900px}
'''


def render_layer_stack(plan):
    layout = layout_layer_stack(plan)
    parts = ['<g data-layer-stack-contract="D-124-five-layer-modular-split" data-template-contract="p18r6-review17-preserved" data-layer-count="5" data-module-count="23" data-domain-count="2" data-dependency-count="4">']
    parts.append(
        '<path class="ls-axis" data-abstraction-axis="1" d="M105 1130 L105 82 M96 96 L105 82 L114 96"/>'
        '<text class="ls-axis-label" x="72" y="61">GẦN NGƯỜI DÙNG</text>'
        '<text class="ls-axis-label" x="72" y="1168">GẦN HẠ TẦNG</text>'
    )
    for layer_id in LAYER_ORDER:
        row = layout["rows"][layer_id]
        x, y, width, height = row["box"]
        band_class = "ls-band focal" if row["focal"] else "ls-band alt" if row["order"] >= 3 else "ls-band"
        badge_class = "ls-level-badge focal" if row["focal"] else "ls-level-badge"
        level_class = "ls-level focal" if row["focal"] else "ls-level"
        scope_class = "ls-scope focal" if row["focal"] else "ls-scope"
        parts.append(
            f'<g data-layer-id="{layer_id}" data-layer-order="{row["order"]}" data-focal="{str(row["focal"]).lower()}" data-module-count="{len(row["member_ids"])}">'
            f'<rect class="{band_class}" x="{x}" y="{y}" width="{width}" height="{height}" rx="16"/>'
            f'<rect class="{badge_class}" x="{x+28}" y="{y+20}" width="62" height="26" rx="5"/>'
            f'<text class="{level_class}" x="{x+59}" y="{y+38}" text-anchor="middle">{escape(row["code"])}</text>'
            f'<text class="ls-title" x="{x+122}" y="{y+42}">{escape(row["title"])}</text>'
            f'<text class="{scope_class}" x="{x+width-28}" y="{y+38}" text-anchor="end">{escape(row["scope"])}</text>'
        )
        if row["focal"]:
            parts.append(
                f'<rect class="ls-focus-tag" x="{x+122}" y="{y+54}" width="108" height="22" rx="4"/>'
                f'<text class="ls-focus-tag-text" x="{x+176}" y="{y+69}" text-anchor="middle">TRỌNG TÂM</text>'
            )
        if layer_id == "stack-level-3":
            for domain_id in DOMAIN_ORDER:
                dx, dy, dw, dh = layout["domain_boxes"][domain_id]
                parts.append(
                    f'<g data-domain-id="{domain_id}" data-member-count="3"><rect class="ls-domain" x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="12"/>'
                    f'<text class="ls-domain-title" x="{dx+dw/2:g}" y="{dy+30}" text-anchor="middle">{escape(layout["groups"][domain_id]["label"].upper())}</text></g>'
                )
        for module_id in row["member_ids"]:
            mx, my, mw, mh = row["module_boxes"][module_id]
            module_class = "ls-module focal" if layout["nodes"][module_id].get("state") == "focal" else "ls-module"
            parts.append(
                f'<g data-module-id="{module_id}" data-owner-layer="{layer_id}"><rect class="{module_class}" x="{mx:g}" y="{my:g}" width="{mw:g}" height="{mh:g}" rx="10"/>'
                f'<text class="ls-module-label" x="{mx+mw/2:g}" y="{my+mh/2+5:g}" text-anchor="middle">{escape(layout["nodes"][module_id]["label"])}</text></g>'
            )
        parts.append('</g>')
    for connector in layout["connectors"]:
        parts.append(
            f'<path class="ls-dependency" data-edge-id="{connector["id"]}" data-source-layer="{connector["source_layer"]}" data-target-layer="{connector["target_layer"]}" data-route-kind="straight-centered" d="M{connector["x"]} {connector["source_y"]} L{connector["x"]} {connector["target_y"]}" marker-end="url(#arrow)"/>'
        )
    parts.append(
        '<line class="ls-footer-rule" x1="170" y1="1182" x2="1940" y2="1182"/>'
        '<rect class="ls-legend-swatch" x="170" y="1203" width="26" height="20" rx="5"/><text class="ls-legend-text" x="210" y="1218">Tầng kiến trúc</text>'
        '<rect class="ls-legend-swatch focal" x="390" y="1203" width="26" height="20" rx="5"/><text class="ls-legend-text" x="430" y="1218">Tầng trọng tâm</text>'
        '<rect class="ls-module" x="640" y="1203" width="26" height="20" rx="5"/><text class="ls-legend-text" x="680" y="1218">Module</text>'
        '<text class="ls-legend-text" x="1940" y="1218" text-anchor="end">Tầng trên phụ thuộc năng lực của tầng dưới</text>'
        '</g>'
    )
    return ''.join(parts)


def validate_layer_stack_svg(svg):
    root = ET.fromstring(svg)
    layers = root.findall(".//*[@data-layer-id]")
    modules = root.findall(".//*[@data-module-id]")
    domains = root.findall(".//*[@data-domain-id]")
    dependencies = root.findall(".//*[@data-edge-id]")
    axes = root.findall(".//*[@data-abstraction-axis]")
    _require(len(layers) == 5, "D-124 serialized layer count mismatch")
    _require(len(modules) == 23, "D-124 serialized module count mismatch")
    _require(len(domains) == 2, "D-124 serialized domain count mismatch")
    _require(len(dependencies) == 4, "D-124 serialized dependency count mismatch")
    _require(len(axes) == 1, "D-124 serialized abstraction-axis mismatch")
    _require(sum(item.attrib["data-focal"] == "true" for item in layers) == 1, "D-124 serialized focal mismatch")
    _require(all(item.attrib["data-route-kind"] == "straight-centered" and "Q" not in item.attrib["d"] for item in dependencies), "D-124 dependency routing mismatch")
    owner_ids = [item.attrib["data-owner-layer"] for item in modules]
    _require(all(owner_id in LAYER_ORDER for owner_id in owner_ids), "D-124 serialized module owner mismatch")
    return {"layers": 5, "modules": 23, "domains": 2, "dependencies": 4, "focal_layers": 1, "abstraction_axes": 1}


def layer_stack_table(plan):
    layout = layout_layer_stack(plan)
    domain_by_module = {
        module_id: domain_id
        for domain_id, group in layout["groups"].items()
        for module_id in group["member_ids"]
    }
    rows = []
    for layer_id in LAYER_ORDER:
        layer = layout["rows"][layer_id]
        for module_id in layer["member_ids"]:
            node = layout["nodes"][module_id]
            domain_id = domain_by_module.get(module_id)
            rows.append((layer["code"], layer["title"], layout["groups"][domain_id]["label"] if domain_id else "—", module_id, node["label"], "trọng tâm" if node.get("state") == "focal" else "mặc định"))
    body = ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows)
    return '<details class="ls-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Tầng</th><th>Tên tầng</th><th>Miền</th><th>Semantic ID</th><th>Module</th><th>Trạng thái</th></tr></thead><tbody>' + body + '</tbody></table></details>'
