"""D-109 detailed story map in the approved P-18 visual grammar."""
from __future__ import annotations

from html import escape
import xml.etree.ElementTree as ET


WIDTH, HEIGHT = 2000, 1040
COLUMN_X = (245, 675, 1105, 1535)
COLUMN_W = 360
HEADER_Y, HEADER_H = 72, 116
STORY_W, STORY_H = 320, 86
RELEASE_Y = {"MVP": 446, "R2": 624, "LATER": 802}
RELEASE_LABELS = {"MVP": "MVP", "R2": "PHÁT HÀNH 2", "LATER": "SAU NÀY"}
ACTIVITIES = (
    ("Tìm dữ liệu", "HOẠT ĐỘNG 1", ("Tra cứu nguồn", "Xem mẫu dữ liệu")),
    ("Dựng báo cáo", "HOẠT ĐỘNG 2", ("Chọn trường", "Thêm biểu đồ")),
    ("Chia sẻ", "HOẠT ĐỘNG 3", ("Gửi liên kết",)),
    ("Tin cậy", "HOẠT ĐỘNG 4", ("Kiểm tra độ mới",)),
)
NODE_ORDER = (
    "story-keyword", "story-saved-filters", "story-natural-query",
    "story-table-chart", "story-internal-link", "story-scheduled-email",
    "story-freshness-stamp", "story-unit-permission", "story-anomaly-alert",
)
RISK_ID = "story-unit-permission"


def _require(value, message):
    if not value:
        raise ValueError(message)


def is_detailed_story_map(plan):
    contract = plan.get("semantic_projection", {}).get("work_contract", {})
    return contract.get("mode") == "story-map" and {item.get("id") for item in contract.get("stories", [])} == set(NODE_ORDER)


def _split_label(label):
    parts = [part.strip() for part in label.split(" | ", 1)]
    return parts[0], parts[1] if len(parts) == 2 else ""


def layout_story_map(plan):
    contract = plan["semantic_projection"]["work_contract"]
    _require(contract.get("mode") == "story-map", "D-109 story-map contract missing")
    stories = {item["id"]: item for item in contract["stories"]}
    releases = {item["release_slice"]: item for item in contract["release_slices"]}
    _require(set(stories) == set(NODE_ORDER), "D-109 story inventory mismatch")
    _require(set(releases) == set(RELEASE_Y), "D-109 release inventory mismatch")

    laid_out = {}
    for story_id in NODE_ORDER:
        story = stories[story_id]
        column = story["backbone_order"]
        release = story["release_slice"]
        _require(column in range(4) and release in RELEASE_Y, f"D-109 invalid story coordinate: {story_id}")
        expected_order = {"MVP": 0, "R2": 1, "LATER": 2}[release]
        _require(story["story_order"] == expected_order or story["story_order"] == 0, f"D-109 story order mismatch: {story_id}")
        x = COLUMN_X[column] + (COLUMN_W - STORY_W) / 2
        laid_out[story_id] = {
            **story,
            "column": column,
            "release": release,
            "box": (x, RELEASE_Y[release], STORY_W, STORY_H),
            "risk": story_id == RISK_ID,
        }
    memberships = [member for release in releases.values() for member in release["member_ids"]]
    _require(len(memberships) == len(set(memberships)) == len(NODE_ORDER), "D-109 release ownership mismatch")
    for release, group in releases.items():
        _require(set(group["member_ids"]) == {story_id for story_id, story in laid_out.items() if story["release"] == release}, f"D-109 release membership mismatch: {release}")
    layout = {"width": WIDTH, "height": HEIGHT, "stories": laid_out, "releases": releases}
    validate_story_map_layout(layout)
    return layout


def validate_story_map_layout(layout):
    boxes = [item["box"] for item in layout["stories"].values()]
    for x, y, w, h in boxes:
        _require(210 < x and x + w < 1960 and 410 < y and y + h < 930, "D-109 story card outside content bounds")
    for index, (ax, ay, aw, ah) in enumerate(boxes):
        for bx, by, bw, bh in boxes[index + 1:]:
            _require(ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay, "D-109 story card overlap")
    _require(sum(item["risk"] for item in layout["stories"].values()) == 1, "D-109 requires exactly one risk story")


def story_map_css(tokens):
    return '''
.sm-column-rule{stroke:var(--grid);stroke-width:1;stroke-dasharray:7 8}.sm-row-band{fill:color-mix(in srgb,var(--surface-alt) 42%,transparent);stroke:none}.sm-header{fill:var(--surface-alt);stroke:var(--connector);stroke-width:1.2}.sm-header-title{font:650 18px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.sm-header-code{font:650 11px Menlo,Monaco,monospace;letter-spacing:1.6px;fill:var(--muted)}
.sm-step{fill:var(--surface);stroke:var(--connector);stroke-width:1.1}.sm-step-text{font:500 15px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.sm-row-label{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}
.sm-story{fill:var(--surface);stroke:var(--connector);stroke-width:1.2}.sm-story.risk{fill:color-mix(in srgb,var(--accent-soft) 48%,var(--surface));stroke:var(--accent);stroke-width:1.4;stroke-dasharray:8 6}.sm-story-title{font:650 16px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.sm-story-meta{font:600 12px Menlo,Monaco,monospace;fill:var(--muted)}.sm-risk-badge{fill:var(--accent-soft);stroke:var(--accent);stroke-width:1}.sm-risk-text{font:700 10px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--accent-text)}
.sm-cut{stroke:var(--accent);stroke-width:1.6}.sm-cut-label-bg{fill:var(--canvas)}.sm-cut-label{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.5px;fill:var(--accent-text)}.sm-legend-rule{stroke:var(--grid);stroke-width:1}.sm-legend-title{font:700 11px Menlo,Monaco,monospace;letter-spacing:1.8px;fill:var(--muted)}.sm-legend-text{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.sm-details{overflow-x:auto}.sm-details table{min-width:980px}
'''


def render_story_map(plan):
    layout = layout_story_map(plan)
    parts = ['<g data-story-map-contract="D-109-detailed-release-slices">']
    parts.append('<rect class="sm-row-band" x="40" y="594" width="1920" height="150"/>')
    parts.append('<rect class="sm-row-band" x="40" y="772" width="1920" height="150"/>')
    for x in (215, 645, 1075, 1505, 1935):
        parts.append(f'<line class="sm-column-rule" x1="{x}" y1="198" x2="{x}" y2="922"/>')
    for index, (title, code, steps) in enumerate(ACTIVITIES):
        x = COLUMN_X[index]
        parts.append(
            f'<g data-story-activity="{index}"><rect class="sm-header" x="{x}" y="{HEADER_Y}" width="{COLUMN_W}" height="{HEADER_H}" rx="12"/>'
            f'<text class="sm-header-title" x="{x+COLUMN_W/2}" y="{HEADER_Y+48}" text-anchor="middle">{escape(title)}</text>'
            f'<text class="sm-header-code" x="{x+COLUMN_W/2}" y="{HEADER_Y+80}" text-anchor="middle">{escape(code)}</text></g>'
        )
        for step_index, step in enumerate(steps):
            sy = 220 + step_index * 74
            parts.append(
                f'<g data-story-step="{index}-{step_index}"><rect class="sm-step" x="{x+20}" y="{sy}" width="{COLUMN_W-40}" height="58" rx="8"/>'
                f'<text class="sm-step-text" x="{x+42}" y="{sy+36}">{escape(step)}</text></g>'
            )
    for release, y in RELEASE_Y.items():
        parts.append(f'<text class="sm-row-label" x="80" y="{y+47}">{RELEASE_LABELS[release]}</text>')
    parts.append('<line class="sm-cut" x1="55" y1="576" x2="1945" y2="576"/>')
    parts.append('<rect class="sm-cut-label-bg" x="1432" y="557" width="150" height="25" rx="4"/><text class="sm-cut-label" x="1507" y="574" text-anchor="middle">ĐƯỜNG CẮT MVP</text>')
    for story_id in NODE_ORDER:
        story = layout["stories"][story_id]
        x, y, width, height = story["box"]
        title, meta = _split_label(story["label"])
        css = "sm-story risk" if story["risk"] else "sm-story"
        parts.append(
            f'<g data-story-id="{story_id}" data-release="{story["release"]}" data-backbone-order="{story["column"]}" data-risk="{str(story["risk"]).lower()}">'
            f'<rect class="{css}" x="{x:g}" y="{y}" width="{width}" height="{height}" rx="10"/>'
            f'<text class="sm-story-title" x="{x+22:g}" y="{y+36}">{escape(title)}</text>'
            f'<text class="sm-story-meta" x="{x+22:g}" y="{y+63}">{escape(meta)}</text>'
        )
        if story["risk"]:
            parts.append(f'<rect class="sm-risk-badge" x="{x+width-72:g}" y="{y+49}" width="54" height="23" rx="4"/><text class="sm-risk-text" x="{x+width-45:g}" y="{y+65}" text-anchor="middle">RỦI RO</text>')
        parts.append('</g>')
    parts.append(
        '<line class="sm-legend-rule" x1="55" y1="964" x2="1945" y2="964"/>'
        '<text class="sm-legend-title" x="55" y="997">CHÚ GIẢI</text>'
        '<rect class="sm-story" x="190" y="980" width="28" height="20" rx="2"/><text class="sm-legend-text" x="232" y="996">Story card</text>'
        '<rect class="sm-story risk" x="430" y="980" width="28" height="20" rx="2"/><text class="sm-legend-text" x="472" y="996">Rủi ro cao nhất</text>'
        '<line class="sm-cut" x1="760" y1="990" x2="815" y2="990"/><text class="sm-legend-text" x="832" y="996">Đường cắt MVP</text></g>'
    )
    return "".join(parts)


def validate_story_map_svg(svg):
    root = ET.fromstring(svg)
    activities = root.findall(".//*[@data-story-activity]")
    steps = root.findall(".//*[@data-story-step]")
    stories = {item.attrib["data-story-id"]: item for item in root.findall(".//*[@data-story-id]")}
    _require(len(activities) == 4 and len(steps) == 6, "D-109 serialized activity structure mismatch")
    _require(set(stories) == set(NODE_ORDER), "D-109 serialized story inventory mismatch")
    _require(sum(item.attrib["data-risk"] == "true" for item in stories.values()) == 1, "D-109 serialized risk mismatch")
    _require(sum(1 for item in root.iter("line") if item.attrib.get("class") == "sm-cut") == 2, "D-109 cutline/legend mismatch")
    return {"activities": 4, "steps": 6, "stories": 9, "release_slices": 3, "risk_stories": 1, "release_cut": 1}


def story_map_table(plan):
    layout = layout_story_map(plan)
    rows = []
    for index, (title, code, steps) in enumerate(ACTIVITIES):
        rows.append(("activity", index + 1, title, code, " / ".join(steps), ""))
    for story_id in NODE_ORDER:
        story = layout["stories"][story_id]
        title, meta = _split_label(story["label"])
        rows.append(("story", story_id, title, story["release"], meta, "rủi ro cao" if story["risk"] else "mặc định"))
    return '<details class="sm-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Loại</th><th>ID / thứ tự</th><th>Nhãn</th><th>Hoạt động / release</th><th>Chi tiết</th><th>Trạng thái</th></tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{escape(str(value))}</td>' for value in row) + '</tr>' for row in rows) + '</tbody></table></details>'
