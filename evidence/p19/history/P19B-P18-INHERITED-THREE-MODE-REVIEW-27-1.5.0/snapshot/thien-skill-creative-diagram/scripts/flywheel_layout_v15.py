"""Original circular flywheel geometry, derived from the declared cycle and state."""
from collections import Counter
from html import escape
import math
import textwrap


def _point(center, radius, angle):
    return center[0]+radius*math.cos(angle), center[1]+radius*math.sin(angle)


def _inside(point, box, pad=0):
    x,y,w,h=box
    return x-pad <= point[0] <= x+w+pad and y-pad <= point[1] <= y+h+pad


def _arc_exit(center, radius, angle, direction, box, interval, pad):
    lo,hi=0,interval/2
    if _inside(_point(center,radius,angle+direction*hi),box,pad):
        raise ValueError('Flywheel stations leave no arc corridor')
    for _ in range(50):
        mid=(lo+hi)/2
        if _inside(_point(center,radius,angle+direction*mid),box,pad): lo=mid
        else: hi=mid
    return angle+direction*hi


def _port(box, toward, clearance):
    x,y,w,h=box
    cx,cy=x+w/2,y+h/2
    dx,dy=toward[0]-cx,toward[1]-cy
    length=math.hypot(dx,dy)
    if length == 0: raise ValueError('Coincident flywheel port centers')
    scale=min(w/2/abs(dx) if dx else math.inf,h/2/abs(dy) if dy else math.inf)
    return cx+dx*scale+dx/length*clearance, cy+dy*scale+dy/length*clearance


def layout_flywheel(plan):
    p=plan['semantic_projection']
    stations=[node for node in p['nodes'] if node['role']=='station']
    shared=[node for node in p['nodes'] if node['role']=='shared-state']
    if not 3 <= len(stations) <= 12 or len(shared)>1 or len(stations)+len(shared)!=len(p['nodes']):
        raise ValueError('Flywheel requires 3–12 stations and at most one shared-state node')
    if any(p.get(k) for k in ('groups','lanes','series','axes')):
        raise ValueError('Unsupported flywheel material; refusing omission')
    by_id={n['id']:n for n in stations}
    edges=p['edges']
    if len(edges)!=len(stations) or any(e['kind']!='cycle' or not e['directed'] or e['source'] not in by_id or e['target'] not in by_id for e in edges):
        raise ValueError('Flywheel needs exactly the declared directed station cycle')
    if any(Counter(e[field] for e in edges) != Counter(by_id.keys()) for field in ('source','target')):
        raise ValueError('Every station needs one incoming and one outgoing cycle edge')
    edge_by_source={e['source']:e for e in edges}
    order=[]
    current=stations[0]['id']
    for _ in stations:
        if current in order: raise ValueError('Disconnected cycles are not a flywheel')
        order.append(current)
        current=edge_by_source[current]['target']
    if current!=order[0]: raise ValueError('Open station cycle')
    nodes={n['id']:dict(n) for n in p['nodes']}
    subtitles={key:[] for key in nodes}
    contributions=[]
    for note in p['annotations']:
        targets=note['target_ids']
        if len(targets)==1 and targets[0] in nodes:
            subtitles[targets[0]].append(note['text'])
        elif (len(targets)==2 and shared and targets[0] in by_id and targets[1]==shared[0]['id']
              and note['text'].startswith('Góp vào '+shared[0]['label']+': ')):
            contributions.append(dict(note,source=targets[0],target=targets[1]))
        else:
            raise ValueError('Ambiguous flywheel annotation; declare a subtitle or inward contribution')
    if len({c['source'] for c in contributions})!=len(contributions):
        raise ValueError('Duplicate shared-state contribution')
    for key,node in nodes.items():
        node['title_lines']=textwrap.wrap(node['label'],24) or [node['label']]
        node['detail_lines']=textwrap.wrap(' · '.join(subtitles[key]),30)
    card_w=300
    card_h=max(112,max(len(nodes[k]['title_lines'])*28+len(nodes[k]['detail_lines'])*23+40 for k in order))
    hub_w=360
    hub_h=max(170,(len(nodes[shared[0]['id']]['title_lines'])*34+len(nodes[shared[0]['id']]['detail_lines'])*24+60) if shared else 170)
    radius=max(390, math.hypot(card_w,card_h)/(2*math.sin(math.pi/len(order)))+60,
               math.hypot(hub_w,hub_h)/2+math.hypot(card_w,card_h)/2+70 if shared else 0)
    width=max(1600,math.ceil(2*radius+2*card_w+100))
    height=max(1080,math.ceil(2*radius+card_h+180))
    center=(width/2,height/2)
    interval=2*math.pi/len(order)
    for i,key in enumerate(order):
        angle=-math.pi/2+i*interval
        cx,cy=_point(center,radius,angle)
        nodes[key].update(box=(cx-card_w/2,cy-card_h/2,card_w,card_h),angle=angle)
    if shared:
        nodes[shared[0]['id']]['box']=(center[0]-hub_w/2,center[1]-hub_h/2,hub_w,hub_h)
    arcs=[]
    for i,key in enumerate(order):
        target=order[(i+1)%len(order)]
        a=-math.pi/2+i*interval
        b=a+interval
        start=_arc_exit(center,radius,a,1,nodes[key]['box'],interval,3)
        end=_arc_exit(center,radius,b,-1,nodes[target]['box'],interval,5)
        if end<=start: raise ValueError('No visible arc between stations')
        arcs.append(dict(edge_by_source[key],start_angle=start,end_angle=end,
                         start=_point(center,radius,start),end=_point(center,radius,end)))
    spokes=[]
    for note in contributions:
        source,target=nodes[note['source']]['box'],nodes[note['target']]['box']
        source_center=(source[0]+source[2]/2,source[1]+source[3]/2)
        spokes.append(dict(note,start=_port(source,center,3),end=_port(target,source_center,12)))
    result=dict(width=width,height=height,center=center,radius=radius,nodes=nodes,
                order=order,shared_id=shared[0]['id'] if shared else None,arcs=arcs,spokes=spokes)
    validate_flywheel_layout(result)
    return result


def validate_flywheel_layout(layout):
    boxes={key:node['box'] for key,node in layout['nodes'].items()}
    for key,(x,y,w,h) in boxes.items():
        if not all(math.isfinite(v) for v in (x,y,w,h)) or min(w,h)<=0 or min(x,y)<20 or x+w>layout['width']-20 or y+h>layout['height']-20:
            raise ValueError('Flywheel box is outside canvas')
        for other,(ox,oy,ow,oh) in boxes.items():
            if key<other and x<ox+ow+12 and x+w+12>ox and y<oy+oh+12 and y+h+12>oy:
                raise ValueError('Flywheel cards overlap or lack clearance')
    for arc in layout['arcs']:
        for i in range(201):
            angle=arc['start_angle']+(arc['end_angle']-arc['start_angle'])*i/200
            if any(_inside(_point(layout['center'],layout['radius'],angle),box) for box in boxes.values()):
                raise ValueError('Flywheel arc crosses a card')
    for spoke in layout['spokes']:
        for i in range(101):
            point=tuple(spoke['start'][j]+(spoke['end'][j]-spoke['start'][j])*i/100 for j in (0,1))
            if any(_inside(point,box) for box in boxes.values()):
                raise ValueError('Flywheel spoke crosses a card')


def flywheel_css(tokens):
    return '''
    .flywheel-card{fill:var(--canvas);stroke:var(--connector);stroke-width:2}
    .flywheel-card.decision{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.4}
    .flywheel-hub{fill:#252b3c;stroke:var(--connector);stroke-width:1.8}
    .flywheel-title{font:650 23px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:var(--text)}
    .flywheel-title.decision{fill:var(--accent-text)}
    .flywheel-subtitle{font:400 14px Menlo,Monaco,monospace;fill:var(--muted)}
    .flywheel-hub-title{font:650 29px 'Avenir Next',Avenir,'Segoe UI',sans-serif;fill:#f7f6f2}
    .flywheel-hub-detail{font:400 14px Menlo,Monaco,monospace;fill:#c7ccd2}
    .flywheel-cycle{fill:none;stroke:var(--connector);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
    .flywheel-contribution{fill:none;stroke:var(--muted);stroke-width:1.8;stroke-dasharray:8 8;stroke-linecap:butt}
    .flywheel-details{overflow-x:auto}.flywheel-details table{min-width:760px}.flywheel-details th,.flywheel-details td:last-child{width:auto}
    '''


def _text(cx,y,lines,css,spacing):
    return ''.join(f'<text class="{css}" x="{cx:.3f}" y="{y+i*spacing:.3f}" text-anchor="middle">{escape(line)}</text>' for i,line in enumerate(lines))


def render_flywheel(plan):
    layout=layout_flywheel(plan)
    parts=['<defs><marker id="flywheel-inward-arrow" markerWidth="12" markerHeight="12" refX="11" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--muted)"/></marker></defs>']
    for arc in layout['arcs']:
        sx,sy=arc['start']; ex,ey=arc['end']; r=layout['radius']
        parts.append(f'<path class="flywheel-cycle" data-cycle-edge="{escape(arc["id"],quote=True)}" data-source="{escape(arc["source"],quote=True)}" data-target="{escape(arc["target"],quote=True)}" d="M{sx:.3f} {sy:.3f} A{r:.3f} {r:.3f} 0 0 1 {ex:.3f} {ey:.3f}" marker-end="url(#arrow)"/>')
    for spoke in layout['spokes']:
        sx,sy=spoke['start']; ex,ey=spoke['end']
        parts.append(f'<path class="flywheel-contribution" data-contribution="{escape(spoke["id"],quote=True)}" data-source="{escape(spoke["source"],quote=True)}" data-target="{escape(spoke["target"],quote=True)}" d="M{sx:.3f} {sy:.3f} L{ex:.3f} {ey:.3f}" marker-end="url(#flywheel-inward-arrow)"/>')
    for key in layout['order']+([layout['shared_id']] if layout['shared_id'] else []):
        node=layout['nodes'][key]; x,y,w,h=node['box']; cx=x+w/2
        hub=node['role']=='shared-state'; decision=node.get('state')=='decision'
        css='flywheel-hub' if hub else 'flywheel-card'+(' decision' if decision else '')
        parts.append(f'<g data-flywheel-node="{escape(key,quote=True)}" data-role="{node["role"]}"><rect class="{css}" x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" rx="12"/>')
        title_step=34 if hub else 28
        block_h=len(node['title_lines'])*title_step+(16 if node['detail_lines'] else 0)+len(node['detail_lines'])*23
        baseline=y+(h-block_h)/2+title_step*.8
        parts.append(_text(cx,baseline,node['title_lines'],'flywheel-hub-title' if hub else 'flywheel-title'+(' decision' if decision else ''),title_step))
        parts.append(_text(cx,baseline+len(node['title_lines'])*title_step+16,node['detail_lines'],'flywheel-hub-detail' if hub else 'flywheel-subtitle',23))
        parts.append('</g>')
    return ''.join(parts)


def flywheel_table(plan):
    layout=layout_flywheel(plan)
    p=plan['semantic_projection']; rows=[]
    for key in layout['order']+([layout['shared_id']] if layout['shared_id'] else []):
        node=layout['nodes'][key]
        role='Trạng thái chung (ngoài vòng)' if node['role']=='shared-state' else ('Bước phê duyệt' if node.get('state')=='decision' else 'Bước trong vòng')
        rows.append([key,role,node['label']])
    for edge in p['edges']: rows.append([edge['id'],'Vòng có hướng',edge['source']+' → '+edge['target']])
    for note in p['annotations']: rows.append([note['id'],', '.join(note['target_ids']),note['text']])
    return '<details class="flywheel-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th scope="col">Semantic IDs</th><th scope="col">Vai trò / Đối tượng</th><th scope="col">Nội dung / Quan hệ</th></tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(value)+'</td>' for value in row)+'</tr>' for row in rows)+'</tbody></table></details>'
