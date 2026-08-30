"""Original D-082 calendar layout. Dates, groups and dependencies come from IR."""
from collections import Counter
from datetime import datetime, timedelta
from html import escape
import textwrap


def _next_month(value):
    return value.replace(year=value.year + (value.month == 12), month=value.month % 12 + 1, day=1)


def _time(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() is None:
        raise ValueError('Gantt timestamps require timezone offsets')
    return result


def layout_gantt(plan):
    projection = plan['semantic_projection']
    nodes = {node['id']: node for node in projection['nodes']}
    items = projection['time_contract']['items']
    if not items or len(items) > 100:
        raise ValueError('Gantt requires 1–100 explicitly dated rows')
    rows = []
    for item in items:
        start, end = _time(item['start']), _time(item['end'])
        if end < start:
            raise ValueError('Gantt end precedes start')
        rows.append(dict(item, start_time=start, end_time=end,
                         gate=nodes[item['id']].get('state') == 'gate',
                         lines=textwrap.wrap(item['label'], width=24) or [item['label']]))
    tz = rows[0]['start_time'].tzinfo
    low = min(row['start_time'] for row in rows).astimezone(tz)
    high = max(row['end_time'] for row in rows).astimezone(tz)
    origin = low.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    limit = _next_month(high.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
    if high == high.replace(day=1, hour=0, minute=0, second=0, microsecond=0) and high > origin:
        limit = high
    months, cursor = [], origin
    while cursor < limit:
        months.append(cursor)
        cursor = _next_month(cursor)
        if len(months) > 36:
            raise ValueError('Gantt calendar exceeds 36 months; split the source schedule')
    width = max(1600, 320 + len(months) * 120 + 60)
    left, right = 320, width - 60
    seconds = (limit-origin).total_seconds()
    def x(value):
        return left + (value-origin).total_seconds()/seconds*(right-left)
    groups = projection['groups']
    row_ids = {row['id'] for row in rows}
    if groups:
        membership = Counter(member for group in groups for member in group['member_ids'])
        if set(membership) != row_ids or any(count != 1 for count in membership.values()) or any(group.get('parent_group_id') for group in groups):
            raise ValueError('Gantt phase bands require a flat, exact one-phase-per-row partition')
    else:
        groups = [{'id': None, 'label': '', 'member_ids': [row['id'] for row in rows]}]
    by_id = {row['id']: row for row in rows}
    bands, cursor_y, ordered = [], 112, []
    for group in groups:
        band_y = cursor_y
        cursor_y += 34 if group['id'] else 14
        for item_id in group['member_ids']:
            row = by_id[item_id]
            row_height = max(64, len(row['lines']) * 27 + 18)
            row.update(x=x(row['start_time']), end_x=x(row['end_time']),
                       y=cursor_y+row_height/2, group_id=group['id'], group_label=group['label'])
            cursor_y += row_height
            ordered.append(row)
        cursor_y += 16
        bands.append(dict(group, y=band_y, height=cursor_y-band_y))
        cursor_y += 26
    return dict(width=width, height=cursor_y+112, left=left, right=right,
                origin=origin, limit=limit, months=months, x=x, rows=ordered,
                bands=bands, bottom=cursor_y-26, edges=projection['edges'])


def gantt_css(tokens):
    # Opaque neutral fill avoids export-engine differences in color-mix support.
    def blend(a, b):
        return '#'+''.join(f'{round(int(a[i:i+2],16)*.18+int(b[i:i+2],16)*.82):02x}' for i in (1,3,5))
    fill = blend(tokens['connector'], tokens['canvas'])
    return f'''
    .gantt-phase{{fill:var(--surface-alt);fill-opacity:.38;stroke:var(--border);stroke-opacity:.65;stroke-width:1.5}}
    .gantt-grid{{stroke:var(--grid);stroke-width:1;opacity:.38}}
    .gantt-month-line{{stroke:var(--border);stroke-width:1.2;stroke-dasharray:5 5;opacity:.65}}
    .gantt-axis{{stroke:var(--border);stroke-width:1.4}}
    .gantt-task{{fill:{fill};stroke:var(--connector);stroke-width:2}}
    .gantt-gate{{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2}}
    .gantt-name,.gantt-month{{font:600 21px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}}
    .gantt-phase-name,.gantt-small{{font:400 14px Menlo,Monaco,monospace;letter-spacing:1.2px;fill:var(--muted)}}
    .gantt-gate-label{{font:600 17px Menlo,Monaco,monospace;fill:var(--text)}}
    .gantt-name.is-gate{{fill:var(--accent-text)}}
    .gantt-legend{{font:500 17px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--connector)}}
    .gantt-details{{overflow-x:auto}}.gantt-details table{{min-width:760px}}.gantt-details th,.gantt-details td:last-child{{width:auto}}
    '''


def _text(x, y, value, css, anchor='start'):
    return f'<text class="{css}" x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}">{escape(str(value))}</text>'


def render_gantt(plan):
    layout = layout_gantt(plan)
    left, right, bottom = layout['left'], layout['right'], layout['bottom']
    parts = [f'<g data-gantt-scale-start="{layout["origin"].isoformat()}" data-gantt-scale-end="{layout["limit"].isoformat()}" data-gantt-interval="half-open">']
    for band in layout['bands']:
        if band['id']:
            parts.append(f'<rect class="gantt-phase" data-phase-id="{escape(band["id"], quote=True)}" x="22" y="{band["y"]}" width="{layout["width"]-44}" height="{band["height"]}" rx="12"/>')
            parts.append(_text(36, band['y']+23, band['label'], 'gantt-phase-name'))
    day = layout['origin']
    while day <= layout['limit']:
        position = layout['x'](day)
        parts.append(f'<line class="gantt-grid" x1="{position:.3f}" y1="92" x2="{position:.3f}" y2="{bottom+18}"/>')
        day += timedelta(days=7)
    for month in layout['months']:
        position, end = layout['x'](month), layout['x'](_next_month(month))
        parts.append(f'<line class="gantt-month-line" x1="{position:.3f}" y1="48" x2="{position:.3f}" y2="{bottom+18}"/>')
        parts.append(_text((position+end)/2, 74, f'Tháng {month.month:02d} · {month.year}', 'gantt-month', 'middle'))
    parts.append(f'<line class="gantt-axis" x1="{left}" y1="92" x2="{right}" y2="92"/><line class="gantt-axis" x1="{left}" y1="48" x2="{left}" y2="{bottom+18}"/>')
    row_map = {row['id']: row for row in layout['rows']}
    for row in layout['rows']:
        css = 'gantt-name is-gate' if row['gate'] else 'gantt-name'
        for line_index, line in enumerate(row['lines']):
            parts.append(_text(36, row['y']+7+(line_index-(len(row['lines'])-1)/2)*27, line, css))
        width = row['end_x']-row['x']
        attrs = f'data-task-id="{escape(row["id"],quote=True)}" data-phase-id="{escape(row["group_id"] or "",quote=True)}" data-start="{escape(row["start"],quote=True)}" data-end="{escape(row["end"],quote=True)}"'
        mark_css = 'gantt-gate' if row['gate'] else 'gantt-task'
        title = escape(f'{row["label"]}: {row["start"]} → {row["end"]}')
        if width == 0:
            x, y = row['x'], row['y']
            parts.append(f'<path class="{mark_css}" {attrs} d="M{x:.3f} {y-9} L{x+9:.3f} {y} L{x:.3f} {y+9} L{x-9:.3f} {y} Z"><title>{title}</title></path>')
        else:
            parts.append(f'<rect class="{mark_css}" {attrs} x="{row["x"]:.3f}" y="{row["y"]-20}" width="{width:.3f}" height="40" rx="{min(7,width/2):.3f}"><title>{title}</title></rect>')
        if row['gate']:
            # Keep short gates truthful; place the label beside, never inflate duration.
            gx, anchor = ((row['x']+row['end_x'])/2, 'middle') if width >= 72 else ((row['end_x']+12, 'start') if row['end_x']+84 < right else (row['x']-12, 'end'))
            parts.append(_text(gx, row['y']+6, 'GATE', 'gantt-gate-label', anchor))
    for edge in layout['edges']:
        if edge['kind'] != 'dependency':
            raise ValueError('Unsupported Gantt relationship; refusing silent omission')
        source, target = row_map[edge['source']], row_map[edge['target']]
        if target['y'] <= source['y'] or target['x'] < source['end_x']:
            raise ValueError('Dependency requires a forward, non-overlapping schedule for this recipe')
        # Route in the source/target row gap, outside the bars; one continuous path.
        x1, y1, x2, y2 = source['end_x'], source['y'], target['x'], target['y']
        elbow = (x1+x2)/2
        parts.append(f'<path class="connector" data-dependency-id="{escape(edge["id"],quote=True)}" d="M{x1:.3f} {y1} H{elbow:.3f} V{y2} H{x2:.3f}" marker-end="url(#arrow)"/>')
    legend_y = bottom+48
    parts.append(f'<line class="gantt-axis" x1="52" y1="{legend_y}" x2="{layout["width"]-52}" y2="{legend_y}"/>')
    parts.append(_text(52, legend_y+27, 'CHÚ GIẢI', 'gantt-small'))
    for x, css, label in ((52,'gantt-gate','GATE · Cửa sổ duyệt'), (460,'gantt-task','Công việc'), (760,'gantt-phase','Giai đoạn')):
        parts.append(f'<rect class="{css}" x="{x}" y="{legend_y+43}" width="34" height="22" rx="5"/>')
        parts.append(_text(x+47, legend_y+60, label, 'gantt-legend'))
    parts.append(_text(right, legend_y+60, 'UTC'+layout['origin'].strftime('%z'), 'gantt-small', 'end'))
    parts.append('</g>')
    return ''.join(parts)


def gantt_table(plan):
    layout = layout_gantt(plan)
    rows = []
    for row in layout['rows']:
        kind = 'GATE · Cửa sổ duyệt' if row['gate'] else ('Mốc' if row['start_time']==row['end_time'] else 'Công việc')
        cells = [row['id'], row['label'], row['group_label'] or '—', kind, row['start'], row['end']]
        rows.append('<tr>'+''.join(f'<td>{escape(value)}</td>' for value in cells)+'</tr>')
    dependencies = '; '.join(f'{edge["source"]} → {edge["target"]}' for edge in layout['edges']) or 'Không khai báo'
    return '<details class="gantt-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><p>Khoảng [bắt đầu, kết thúc); timezone trong từng timestamp. Phụ thuộc: '+escape(dependencies)+'</p><table><thead><tr>'+''.join(f'<th scope="col">{value}</th>' for value in ('Semantic IDs','Công việc / Gate','Giai đoạn','Loại','Bắt đầu','Kết thúc'))+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></details>'
