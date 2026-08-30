"""D-094 detailed Kanban board in the approved P-18 visual grammar."""
from __future__ import annotations

from html import escape
import re
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 2000, 900
COLUMN_ORDER = ("column-backlog", "column-progress", "column-review", "column-done")
NODE_ORDER = (
    "work-api-limit", "work-infra-module", "work-onboarding-docs",
    "work-data-cluster", "work-node-migration", "work-key-rotation", "work-observability",
    "work-flag-cleanup", "work-partner-login", "work-log-policy", "work-ci-cache",
)
COLUMN_BOXES = {
    column_id: (45 + index * 490, 90, 440, 650)
    for index, column_id in enumerate(COLUMN_ORDER)
}
CARD_Y = (180, 295, 410, 525)
STATE_ORDER = ("default", "blocked", "waiting-external", "done")


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_kanban(plan):
    contract = plan.get("semantic_projection", {}).get("work_contract", {})
    return contract.get("mode") == "kanban" and {item.get("id") for item in contract.get("items", [])} == set(NODE_ORDER)


def layout_kanban(plan):
    projection = plan["semantic_projection"]
    contract = projection["work_contract"]
    _require(contract.get("mode") == "kanban", "D-094 Kanban work contract missing")
    columns = {item["id"]: item for item in contract["columns"]}
    items = {item["id"]: item for item in contract["items"]}
    states = {item["id"]: item.get("state") for item in projection["nodes"]}
    annotated_limits = {}
    for annotation in projection.get("annotations", []):
        match = re.fullmatch(r"Giới hạn WIP: ([1-9][0-9]*)", annotation["text"])
        if match:
            _require(len(annotation["target_ids"]) == 1, "D-094 WIP annotation must target one column")
            annotated_limits[annotation["target_ids"][0]] = int(match.group(1))
    _require(set(columns) == set(COLUMN_ORDER), "D-094 Kanban column mismatch")
    _require(set(items) == set(NODE_ORDER), "D-094 Kanban item mismatch")

    result_columns, result_items = {}, {}
    owned = []
    for column_index, column_id in enumerate(COLUMN_ORDER):
        column = columns[column_id]
        member_ids = list(column["member_ids"])
        owned.extend(member_ids)
        ordered = sorted(member_ids, key=lambda item_id: items[item_id]["item_order"])
        _require(ordered == member_ids, f"D-094 Kanban item order mismatch: {column_id}")
        for item_order, item_id in enumerate(member_ids):
            item = items[item_id]
            _require(item["column_order"] == column_index and item["item_order"] == item_order, f"D-094 Kanban coordinate mismatch: {item_id}")
            state = states[item_id]
            _require(state in STATE_ORDER, f"D-094 Kanban state mismatch: {item_id}")
            _require(item["blocked"] == (state == "blocked"), f"D-094 Kanban blocked mismatch: {item_id}")
            x, _, width, _ = COLUMN_BOXES[column_id]
            result_items[item_id] = {**item, "state": state, "column_id": column_id, "box": (x + 28, CARD_Y[item_order], width - 56, 94)}
        _require(not (column.get("wip_limit") is not None and column_id in annotated_limits), f"D-094 duplicate WIP declaration: {column_id}")
        limit = column.get("wip_limit", annotated_limits.get(column_id))
        count = len(member_ids)
        result_columns[column_id] = {
            **column,
            "box": COLUMN_BOXES[column_id],
            "count": count,
            "over_limit": limit is not None and count > limit,
            "counter": f"{count}/{limit}" if limit is not None else str(count),
        }
    _require(owned == list(NODE_ORDER) and len(owned) == len(set(owned)), "D-094 Kanban ownership mismatch")
    _require(sum(column["over_limit"] for column in result_columns.values()) == 1, "D-094 Kanban needs exactly one WIP breach")
    _require(sum(item["state"] == "blocked" for item in result_items.values()) == 1, "D-094 Kanban needs exactly one blocked item")
    _require(sum(item["state"] == "waiting-external" for item in result_items.values()) == 1, "D-094 Kanban needs exactly one waiting item")
    _require(sum(item["state"] == "done" for item in result_items.values()) == 2, "D-094 Kanban done count mismatch")
    result = {"width": WIDTH, "height": HEIGHT, "columns": result_columns, "items": result_items}
    validate_kanban_layout(result)
    return result


def validate_kanban_layout(layout):
    for column_id, column in layout["columns"].items():
        cx, cy, cw, ch = column["box"]
        for item_id in column["member_ids"]:
            x, y, w, h = layout["items"][item_id]["box"]
            _require(cx < x and cy < y and x + w < cx + cw and y + h < cy + ch, f"D-094 Kanban containment mismatch: {item_id}")
    boxes = [item["box"] for item in layout["items"].values()]
    for index, (ax, ay, aw, ah) in enumerate(boxes):
        for bx, by, bw, bh in boxes[index + 1:]:
            _require(ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay, "D-094 Kanban card overlap")


def kanban_css(tokens):
    return '''
.kb-column{fill:color-mix(in srgb,var(--surface-alt) 54%,transparent);stroke:none}.kb-divider{stroke:var(--border);stroke-width:1.8}.kb-column-title{font:650 18px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}
.kb-counter{fill:var(--surface);stroke:var(--muted);stroke-width:1.4}.kb-counter.over{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1.8}.kb-counter-text{font:700 12px Menlo,Monaco,monospace;fill:var(--muted)}.kb-counter-text.over{fill:var(--accent-text)}
.kb-card{fill:var(--surface);stroke:var(--connector);stroke-width:2}.kb-card.blocked{fill:color-mix(in srgb,var(--accent-soft) 40%,var(--surface));stroke:var(--accent);stroke-dasharray:8 6}.kb-card.waiting{fill:color-mix(in srgb,var(--surface-alt) 74%,var(--surface));stroke:var(--border);stroke-dasharray:8 6}.kb-card.done{fill:color-mix(in srgb,var(--series-1) 10%,var(--surface));stroke:var(--series-1)}
.kb-blocked-rail{fill:var(--accent)}.kb-title{font:650 16px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.kb-meta{font:600 12px Menlo,Monaco,monospace;fill:var(--muted)}
.kb-legend-rule{stroke:var(--grid);stroke-width:1.3}.kb-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.7px;fill:var(--muted)}.kb-legend-text{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.kb-details{overflow-x:auto}.kb-details table{min-width:920px}
'''


def _card(item_id, item):
    x, y, width, height = item["box"]
    state = item["state"]
    css = "kb-card blocked" if state == "blocked" else "kb-card waiting" if state == "waiting-external" else "kb-card done" if state == "done" else "kb-card"
    parts = [part.strip() for part in item["label"].split(" | ", 1)]
    title, meta = parts[0], parts[1] if len(parts) == 2 else state
    rail = f'<rect class="kb-blocked-rail" x="{x}" y="{y}" width="7" height="{height}" rx="3"/>' if state == "blocked" else ""
    return (
        f'<g data-kb-item-id="{item_id}" data-column-id="{item["column_id"]}" data-state="{state}">'
        f'<rect class="{css}" x="{x}" y="{y}" width="{width}" height="{height}" rx="10"/>{rail}'
        f'<text class="kb-title" x="{x+24}" y="{y+39}">{escape(title)}</text>'
        f'<text class="kb-meta" x="{x+24}" y="{y+66}">{escape(meta)}</text></g>'
    )


def render_kanban(plan):
    layout = layout_kanban(plan)
    parts = ['<g data-kb-contract="D-094-detailed-kanban">']
    for column_id in COLUMN_ORDER:
        column = layout["columns"][column_id]
        x, y, width, height = column["box"]
        counter_css = "kb-counter over" if column["over_limit"] else "kb-counter"
        text_css = "kb-counter-text over" if column["over_limit"] else "kb-counter-text"
        parts.append(
            f'<g data-kb-column-id="{column_id}" data-count="{column["count"]}" data-wip-limit="{column.get("wip_limit", "none")}" data-over-limit="{str(column["over_limit"]).lower()}">'
            f'<rect class="kb-column" x="{x}" y="{y}" width="{width}" height="{height}" rx="16"/>'
            f'<text class="kb-column-title" x="{x+28}" y="{y+43}">{escape(column["label"])}</text>'
            f'<rect class="{counter_css}" x="{x+width-96}" y="{y+20}" width="68" height="34" rx="5"/>'
            f'<text class="{text_css}" x="{x+width-62}" y="{y+42}" text-anchor="middle">{column["counter"]}</text>'
            f'<line class="kb-divider" x1="{x}" y1="{y+70}" x2="{x+width}" y2="{y+70}"/></g>'
        )
        for item_id in column["member_ids"]:
            parts.append(_card(item_id, layout["items"][item_id]))
    parts.append(
        '<line class="kb-legend-rule" x1="45" y1="795" x2="1955" y2="795"/>'
        '<text class="kb-legend-title" x="45" y="829">CHÚ GIẢI</text>'
        '<rect class="kb-card" x="180" y="812" width="28" height="20" rx="2"/><text class="kb-legend-text" x="222" y="828">Mặc định</text>'
        '<rect class="kb-card blocked" x="395" y="812" width="28" height="20" rx="2"/><rect class="kb-blocked-rail" x="395" y="812" width="4" height="20" rx="1"/><text class="kb-legend-text" x="438" y="828">Bị chặn</text>'
        '<rect class="kb-card waiting" x="635" y="812" width="28" height="20" rx="2"/><text class="kb-legend-text" x="678" y="828">Chờ bên ngoài</text>'
        '<rect class="kb-card done" x="900" y="812" width="28" height="20" rx="2"/><text class="kb-legend-text" x="943" y="828">Hoàn tất</text>'
        '<rect class="kb-counter over" x="1135" y="812" width="28" height="20" rx="3"/><text class="kb-legend-text" x="1178" y="828">Vượt WIP</text></g>'
    )
    return "".join(parts)


def validate_kanban_svg(svg):
    root = ET.fromstring(svg)
    columns = {item.attrib["data-kb-column-id"]: item for item in root.findall(".//*[@data-kb-column-id]")}
    items = {item.attrib["data-kb-item-id"]: item for item in root.findall(".//*[@data-kb-item-id]")}
    _require(set(columns) == set(COLUMN_ORDER), "D-094 serialized Kanban column mismatch")
    _require(set(items) == set(NODE_ORDER), "D-094 serialized Kanban item mismatch")
    _require(sum(item.attrib["data-over-limit"] == "true" for item in columns.values()) == 1, "D-094 serialized WIP mismatch")
    states = [item.attrib["data-state"] for item in items.values()]
    _require(states.count("blocked") == 1 and states.count("waiting-external") == 1 and states.count("done") == 2, "D-094 serialized state mismatch")
    return {"columns": 4, "items": 11, "wip_breaches": 1, "blocked": 1, "waiting_external": 1, "done": 2}


def kanban_table(plan):
    layout = layout_kanban(plan)
    rows = []
    for column_id in COLUMN_ORDER:
        column = layout["columns"][column_id]
        rows.append(("column", column_id, column["label"], column["counter"], "over-limit" if column["over_limit"] else "within-limit", ", ".join(column["member_ids"])))
        for item_id in column["member_ids"]:
            item = layout["items"][item_id]
            rows.append(("item", item_id, item["label"], item["item_order"] + 1, item["state"], column_id))
    return '<details class="kb-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Loại</th><th>Semantic ID</th><th>Nhãn</th><th>Vị trí/WIP</th><th>Trạng thái</th><th>Cột/thành viên</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></details>'
