"""Detailed Fishbone geometry derived from explicit cause categories and causes."""
from html import escape
import math


def layout_fishbone(plan):
    p = plan['semantic_projection']
    causes = {n['id']: dict(n) for n in p['nodes'] if n['role'] == 'cause'}
    effects = [dict(n) for n in p['nodes'] if n['role'] == 'effect']
    if len(effects) != 1 or not 2 <= len(p['groups']) <= 8:
        raise ValueError('Fishbone requires one effect and 2–8 explicit categories')
    effect = effects[0]
    if len(causes) + 1 != len(p['nodes']) or p.get('lanes') or p.get('series') or p.get('axes') or p.get('annotations'):
        raise ValueError('Unsupported Fishbone material; refusing omission')
    ownership = {}
    categories = []
    for index, group in enumerate(p['groups']):
        members = group['member_ids']
        if not 1 <= len(members) <= 4 or any(key not in causes for key in members):
            raise ValueError('Every Fishbone category needs 1–4 declared causes')
        for key in members:
            if key in ownership: raise ValueError('A cause belongs to more than one category')
            ownership[key] = group['id']
        categories.append(dict(group, order=index, side='top' if index % 2 == 0 else 'bottom'))
    if set(ownership) != set(causes): raise ValueError('Every cause must belong to exactly one category')
    relations = {edge['source']: edge for edge in p['edges']}
    if (len(relations) != len(causes) or len(p['edges']) != len(causes)
            or any(edge['kind'] != 'cause' or not edge['directed'] or edge['target'] != effect['id'] or edge['source'] not in causes for edge in p['edges'])):
        raise ValueError('Every cause relation must point to the single effect')
    width, height, spine_y = 1750, 900, 430
    top_count = math.ceil(len(categories) / 2)
    bottom_count = len(categories) // 2
    top_x = [310 + i * (980 / max(1, top_count - 1)) for i in range(top_count)]
    bottom_x = [550 + i * (500 / max(1, bottom_count - 1)) for i in range(bottom_count)]
    top_i = bottom_i = 0
    layouts = []
    for category in categories:
        if category['side'] == 'top':
            cx = top_x[top_i]; top_i += 1
            box = (cx - 115, 78, 230, 58); start = (cx, 136); attach = (cx + 135, spine_y)
        else:
            cx = bottom_x[bottom_i]; bottom_i += 1
            box = (cx - 115, 744, 230, 58); start = (cx, 744); attach = (cx + 135, spine_y)
        members = []
        for position, key in enumerate(category['member_ids']):
            t = .42 + position * (.28 / max(1, len(category['member_ids']) - 1))
            bx = start[0] + (attach[0] - start[0]) * t
            by = start[1] + (attach[1] - start[1]) * t
            members.append(dict(
                causes[key],
                tick=((bx - 72, by), (bx, by)),
                label_position=(bx - 82, by + (5 if category['side']=='top' else 19)),
                relation=relations[key],
            ))
        layouts.append(dict(category, box=box, start=start, attach=attach, members=members))
    result = dict(width=width, height=height, spine=((95, spine_y), (1460, spine_y)),
                  effect=dict(effect, box=(1460, 350, 250, 160)), categories=layouts)
    validate_fishbone_layout(result)
    return result


def validate_fishbone_layout(layout):
    if not 2 <= len(layout['categories']) <= 8:
        raise ValueError('Fishbone category count outside supported range')
    seen = set()
    for category in layout['categories']:
        x,y,w,h = category['box']
        if min(x,y) < 30 or x+w > layout['width']-30 or y+h > layout['height']-30:
            raise ValueError('Fishbone category outside canvas')
        if category['attach'][1] != layout['spine'][0][1]: raise ValueError('Category bone misses spine')
        for member in category['members']:
            if member['id'] in seen: raise ValueError('Duplicate cause')
            seen.add(member['id'])
            if member['tick'][1] != (member['tick'][1][0], member['tick'][0][1]):
                raise ValueError('Sub-cause tick must meet its category bone')
            if not all(math.isfinite(v) for point in member['tick'] for v in point): raise ValueError('Non-finite Fishbone geometry')
    ex,ey,ew,eh = layout['effect']['box']
    if layout['spine'][1] != (ex, layout['spine'][0][1]) or not ey <= layout['spine'][0][1] <= ey+eh:
        raise ValueError('Spine must terminate at the observed effect')


def fishbone_css(tokens):
    return '''
    .fishbone-spine,.fishbone-bone,.fishbone-tick{fill:none;stroke:var(--connector);stroke-linecap:round;stroke-linejoin:round}
    .fishbone-spine{stroke-width:2.7}.fishbone-bone{stroke-width:2.4}.fishbone-tick{stroke-width:1.8}
    .fishbone-category{fill:var(--surface);stroke:var(--connector);stroke-width:1.8}
    .fishbone-effect{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.6}
    .fishbone-category-label{font:650 17px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}
    .fishbone-cause-label{font:500 13px Menlo,Monaco,monospace;fill:var(--muted)}
    .fishbone-effect-label{font:650 22px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}
    .fishbone-effect-tag{font:700 11px Menlo,Monaco,monospace;letter-spacing:.12em;fill:var(--accent-text)}
    .fishbone-legend-rule{stroke:var(--grid);stroke-width:1.4}.fishbone-legend-text{font:500 12px Menlo,Monaco,monospace;fill:var(--muted)}
    .fishbone-details{overflow-x:auto}.fishbone-details table{min-width:820px}.fishbone-details th,.fishbone-details td:last-child{width:auto}
    '''


def render_fishbone(plan):
    layout = layout_fishbone(plan); parts=[]
    (sx,sy),(ex,ey)=layout['spine']
    parts.append(f'<line class="fishbone-spine" data-fishbone-spine="effect" x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" marker-end="url(#arrow)"/>')
    for category in layout['categories']:
        x,y,w,h=category['box']; ax,ay=category['attach']; bx,by=category['start']
        parts.append(f'<g data-fishbone-category="{escape(category["id"],quote=True)}" data-side="{category["side"]}"><line class="fishbone-bone" x1="{bx:.3f}" y1="{by:.3f}" x2="{ax:.3f}" y2="{ay:.3f}"/><rect class="fishbone-category" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="7"/><text class="fishbone-category-label" x="{x+w/2:.3f}" y="{y+h/2+6:.3f}" text-anchor="middle">{escape(category["label"])}</text>')
        for member in category['members']:
            (tx,ty),(ux,uy)=member['tick']; lx,ly=member['label_position']
            parts.append(f'<g data-fishbone-cause="{escape(member["id"],quote=True)}" data-category="{escape(category["id"],quote=True)}" data-relation="{escape(member["relation"]["id"],quote=True)}"><line class="fishbone-tick" x1="{tx:.3f}" y1="{ty:.3f}" x2="{ux:.3f}" y2="{uy:.3f}"/><text class="fishbone-cause-label" x="{lx:.3f}" y="{ly:.3f}" text-anchor="end">{escape(member["label"])}</text></g>')
        parts.append('</g>')
    effect=layout['effect']; x,y,w,h=effect['box']
    parts.append(f'<g data-fishbone-effect="{escape(effect["id"],quote=True)}"><rect class="fishbone-effect" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/><text class="fishbone-effect-tag" x="{x+22}" y="{y+30}">HỆ QUẢ QUAN SÁT</text><text class="fishbone-effect-label" x="{x+w/2}" y="{y+h/2+12}" text-anchor="middle">{escape(effect["label"])}</text></g>')
    parts.append('<g aria-label="Chú giải Fishbone"><line class="fishbone-legend-rule" x1="95" y1="835" x2="1710" y2="835"/><text class="micro" x="95" y="860">CHÚ GIẢI</text><line class="fishbone-bone" x1="210" y1="856" x2="250" y2="856"/><text class="fishbone-legend-text" x="266" y="860">Nhóm nguyên nhân</text><line class="fishbone-tick" x1="500" y1="856" x2="540" y2="856"/><text class="fishbone-legend-text" x="556" y="860">Nguyên nhân chi tiết</text><rect class="fishbone-effect" x="825" y="844" width="28" height="20" rx="3"/><text class="fishbone-legend-text" x="870" y="860">Hệ quả quan sát</text></g>')
    return ''.join(parts)


def fishbone_table(plan):
    layout=layout_fishbone(plan); rows=[]
    for category in layout['categories']:
        for cause in category['members']:
            rows.append((category['id'], category['label'], cause['id'], cause['label'], layout['effect']['id'], layout['effect']['label']))
    return '<details class="fishbone-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Semantic IDs</th><th scope="col">Nhóm nguyên nhân</th><th scope="col">Nguyên nhân ID</th><th scope="col">Nguyên nhân chi tiết</th><th scope="col">Hệ quả ID</th><th scope="col">Hệ quả khai báo</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(value)+'</td>' for value in row)+'</tr>' for row in rows)+'</tbody></table></details>'
