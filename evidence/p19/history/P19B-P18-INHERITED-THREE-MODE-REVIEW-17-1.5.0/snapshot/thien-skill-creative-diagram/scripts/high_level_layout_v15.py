"""D-092 detailed high-level data-platform overview with P-18 corner policy."""
from __future__ import annotations
from html import escape
import math
import xml.etree.ElementTree as ET

WIDTH, HEIGHT = 2000, 1040
NODE_ORDER = ("source-portal","source-files","source-operational","source-legacy","stage-collect","stage-query","stage-store","stage-model","stage-serve","control-orchestration","control-identity")
EDGE_ORDER = ("flow-portal-collect","flow-files-collect","flow-operational-collect","flow-legacy-collect","flow-collect-query","flow-collect-store","flow-store-query","flow-query-model","flow-store-model","flow-model-serve","trigger-query","trigger-model","trigger-serve")
BOXES = {
    "source-portal":(45,150,260,112), "source-files":(45,300,260,112), "source-operational":(45,450,260,112), "source-legacy":(45,600,260,112),
    "stage-collect":(380,275,300,145), "stage-query":(760,230,330,145), "stage-store":(760,485,330,145),
    "stage-model":(1215,330,330,145), "stage-serve":(1640,330,300,145),
    "control-orchestration":(380,115,1560,88), "control-identity":(45,790,1895,88),
}
BOUNDARIES = {"boundary-sources":(25,100,300,650), "boundary-platform":(345,100,1625,650)}
ROUTE_POINTS = {
    "flow-portal-collect":[(305,206),(345,206),(345,305),(380,305)],
    "flow-files-collect":[(305,356),(345,356),(345,335),(380,335)],
    "flow-operational-collect":[(305,506),(345,506),(345,365),(380,365)],
    "flow-legacy-collect":[(305,656),(345,656),(345,395),(380,395)],
    "flow-collect-query":[(680,315),(720,315),(720,302),(760,302)],
    "flow-collect-store":[(680,380),(720,380),(720,557),(760,557)],
    "flow-store-query":[(925,485),(925,375)],
    "flow-query-model":[(1090,302),(1150,302),(1150,385),(1215,385)],
    "flow-store-model":[(1090,557),(1150,557),(1150,430),(1215,430)],
    "flow-model-serve":[(1545,402),(1640,402)],
    "trigger-query":[(925,203),(925,230)], "trigger-model":[(1380,203),(1380,330)], "trigger-serve":[(1790,203),(1790,330)],
}
PAIRS = {
    "flow-portal-collect":("source-portal","stage-collect"), "flow-files-collect":("source-files","stage-collect"),
    "flow-operational-collect":("source-operational","stage-collect"), "flow-legacy-collect":("source-legacy","stage-collect"),
    "flow-collect-query":("stage-collect","stage-query"), "flow-collect-store":("stage-collect","stage-store"),
    "flow-store-query":("stage-store","stage-query"), "flow-query-model":("stage-query","stage-model"),
    "flow-store-model":("stage-store","stage-model"), "flow-model-serve":("stage-model","stage-serve"),
    "trigger-query":("control-orchestration","stage-query"), "trigger-model":("control-orchestration","stage-model"),
    "trigger-serve":("control-orchestration","stage-serve"),
}

def _require(value, message):
    if not value: raise ValueError(message)
def _split(label):
    values=[part.strip() for part in label.split(" | ",1)]; return values[0], values[1] if len(values)>1 else ""

def orthogonal_path(points, corner_style="rounded", radius=18):
    _require(corner_style in ("rounded","straight") and len(points)>=2, "D-092 invalid corner policy")
    for a,b in zip(points,points[1:]): _require(a!=b and (a[0]==b[0] or a[1]==b[1]), "D-092 route must be orthogonal")
    if corner_style == "straight" or len(points)==2: return "M"+" L".join(f"{x:g} {y:g}" for x,y in points)
    out=[f"M{points[0][0]:g} {points[0][1]:g}"]
    for i in range(1,len(points)-1):
        prev,cur,nxt=points[i-1],points[i],points[i+1]
        incoming=min(radius,math.hypot(cur[0]-prev[0],cur[1]-prev[1])/2,math.hypot(nxt[0]-cur[0],nxt[1]-cur[1])/2)
        ux=((cur[0]-prev[0]) and (1 if cur[0]>prev[0] else -1), (cur[1]-prev[1]) and (1 if cur[1]>prev[1] else -1))
        vx=((nxt[0]-cur[0]) and (1 if nxt[0]>cur[0] else -1), (nxt[1]-cur[1]) and (1 if nxt[1]>cur[1] else -1))
        before=(cur[0]-ux[0]*incoming,cur[1]-ux[1]*incoming); after=(cur[0]+vx[0]*incoming,cur[1]+vx[1]*incoming)
        out += [f"L{before[0]:g} {before[1]:g}",f"Q{cur[0]:g} {cur[1]:g} {after[0]:g} {after[1]:g}"]
    out.append(f"L{points[-1][0]:g} {points[-1][1]:g}")
    return " ".join(out)

def is_detailed_high_level(plan):
    p=plan.get("semantic_projection",{}); return {i.get("id") for i in p.get("nodes",[])}==set(NODE_ORDER)

def layout_high_level(plan, corner_style="rounded"):
    p=plan["semantic_projection"]; nodes={i["id"]:i for i in p["nodes"]}; edges={i["id"]:i for i in p["edges"]}; groups={i["id"]:i for i in p["groups"]}
    _require(set(nodes)==set(NODE_ORDER) and set(edges)==set(EDGE_ORDER) and set(groups)==set(BOUNDARIES), "D-092 high-level material mismatch")
    for edge_id,pair in PAIRS.items(): _require((edges[edge_id]["source"],edges[edge_id]["target"])==pair and edges[edge_id]["directed"], f"D-092 endpoint mismatch: {edge_id}")
    _require(set(groups["boundary-sources"]["member_ids"])==set(NODE_ORDER[:4]), "D-092 source boundary mismatch")
    _require(set(groups["boundary-platform"]["member_ids"])==set(NODE_ORDER[4:10]), "D-092 platform boundary mismatch")
    layout={"width":WIDTH,"height":HEIGHT,"corner_style":corner_style,"nodes":{k:{**nodes[k],"box":BOXES[k]} for k in NODE_ORDER},"edges":{k:{**edges[k],"points":ROUTE_POINTS[k],"path":orthogonal_path(ROUTE_POINTS[k],corner_style)} for k in EDGE_ORDER},"groups":{k:{**groups[k],"box":BOUNDARIES[k]} for k in BOUNDARIES}}
    validate_high_level_layout(layout); return layout

def validate_high_level_layout(layout):
    _require(layout["corner_style"] in ("rounded","straight"), "D-092 corner style mismatch")
    for node in layout["nodes"].values():
        x,y,w,h=node["box"]; _require(x>=20 and y>=90 and x+w<=WIDTH-20 and y+h<=HEIGHT-120, "D-092 node outside canvas")
    for edge in layout["edges"].values():
        _require(edge["path"].count("M")==1 and edge["path"].startswith("M"), "D-092 connector must be one continuous path")

def high_level_css(tokens): return '''
.hl-phase{fill:var(--text)}.hl-phase.alt{fill:var(--connector)}.hl-phase-text{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.6px;fill:var(--canvas)}
.hl-boundary{fill:color-mix(in srgb,var(--surface-alt) 48%,transparent);stroke:var(--border);stroke-width:1.8}.hl-boundary.source{stroke-dasharray:9 7}
.hl-card,.hl-band{fill:var(--surface);stroke:var(--connector);stroke-width:1.9}.hl-card.focal{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.5}.hl-band{fill:var(--surface-alt);stroke:var(--border)}
.hl-title{font:650 17px 'Avenir Next',Avenir,sans-serif;fill:var(--text)}.hl-detail{font:500 12px Menlo,Monaco,monospace;fill:var(--muted)}.hl-tag{font:700 10px Menlo,Monaco,monospace;letter-spacing:1px;fill:var(--muted)}
.hl-route{fill:none;stroke:var(--connector);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}.hl-route.primary{stroke:var(--accent);stroke-width:2.6}.hl-route.control{stroke-dasharray:8 7;stroke-width:1.8}
.hl-boundary-label-bg{fill:var(--canvas)}.hl-boundary-label,.hl-legend-title{font:700 12px Menlo,Monaco,monospace;letter-spacing:1.7px;fill:var(--muted)}.hl-legend{font:500 12px 'Avenir Next',Avenir,sans-serif;fill:var(--muted)}.hl-legend-rule{stroke:var(--grid);stroke-width:1.3}
.hl-details{overflow-x:auto}.hl-details table{min-width:980px}
'''

def _card(node_id,node):
    x,y,w,h=node["box"]; title,detail=_split(node["label"]); focal=node_id=="stage-store"; band=node_id.startswith("control-")
    css="hl-band" if band else "hl-card focal" if focal else "hl-card"; tag="CONTROL" if band else "STORE" if focal else "STAGE" if node_id.startswith("stage-") else "SOURCE"
    anchor="middle" if band else "start"; tx=x+w/2 if band else x+24
    return f'<g data-hl-node-id="{node_id}"><rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/><text class="hl-tag" x="{x+18}" y="{y+25}">{tag}</text><text class="hl-title" x="{tx}" y="{y+57}" text-anchor="{anchor}">{escape(title)}</text><text class="hl-detail" x="{tx}" y="{y+82}" text-anchor="{anchor}">{escape(detail)}</text></g>'

def render_high_level(plan, corner_style="rounded"):
    layout=layout_high_level(plan,corner_style); parts=['<g data-hl-contract="D-092-detailed-overview" data-corner-style="'+corner_style+'"><defs><marker id="hl-arrow-accent" markerWidth="12" markerHeight="12" refX="10.5" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L11 6 L1 11 Z" fill="var(--accent)"/></marker></defs>']
    phases=((0,410,"NGUỒN DỮ LIỆU"),(410,410,"THU NHẬN"),(820,410,"LƯU TRỮ"),(1230,410,"XỬ LÝ & PHÂN TÍCH"),(1640,360,"PHỤC VỤ"))
    for i,(x,w,label) in enumerate(phases):
        notch=24; d=f"M{x} 20 H{x+w-notch} L{x+w} 49 L{x+w-notch} 78 H{x} L{x+notch} 49 Z" if i else f"M0 20 H{w-notch} L{w} 49 L{w-notch} 78 H0 Z"
        parts.append(f'<path class="hl-phase{" alt" if i%2 else ""}" d="{d}"/><text class="hl-phase-text" x="{x+w/2}" y="54" text-anchor="middle">{escape(label)}</text>')
    for group_id in ("boundary-sources","boundary-platform"):
        x,y,w,h=layout["groups"][group_id]["box"]; css="hl-boundary source" if group_id=="boundary-sources" else "hl-boundary"
        if group_id == "boundary-platform":
            label_x=x+w/2
            label=f'<rect class="hl-boundary-label-bg" x="{label_x-128}" y="{y-10}" width="256" height="24"/><text class="hl-boundary-label" x="{label_x}" y="{y+7}" text-anchor="middle">{escape(layout["groups"][group_id]["label"])}</text>'
        else:
            label=f'<text class="hl-boundary-label" x="{x+w/2}" y="{y+25}" text-anchor="middle">{escape(layout["groups"][group_id]["label"])}</text>'
        parts.append(f'<g data-hl-group-id="{group_id}"><rect class="{css}" x="{x}" y="{y}" width="{w}" height="{h}" rx="16"/>{label}</g>')
    for edge_id in EDGE_ORDER:
        edge=layout["edges"]; item=edge[edge_id]; control=edge_id.startswith("trigger-"); primary=edge_id in {"flow-collect-store","flow-store-model","flow-model-serve"}; css="hl-route control" if control else "hl-route primary" if primary else "hl-route"; marker="url(#hl-arrow-accent)" if primary else "url(#arrow)"
        parts.append(f'<path class="{css}" data-hl-edge-id="{edge_id}" data-corner-style="{corner_style}" data-source="{item["source"]}" data-target="{item["target"]}" d="{item["path"]}" marker-end="{marker}"/>')
    for node_id in NODE_ORDER: parts.append(_card(node_id,layout["nodes"][node_id]))
    parts.append('<line class="hl-legend-rule" x1="45" y1="930" x2="1940" y2="930"/><text class="hl-legend-title" x="45" y="960">CHÚ GIẢI</text><rect class="hl-boundary source" x="180" y="945" width="28" height="22" rx="4"/><text class="hl-legend" x="220" y="962">Nguồn ngoài biên</text><rect class="hl-card focal" x="480" y="945" width="28" height="22" rx="4"/><text class="hl-legend" x="520" y="962">Thành phần trọng tâm</text><line class="hl-route primary" x1="860" y1="956" x2="915" y2="956"/><text class="hl-legend" x="930" y="962">Luồng dữ liệu chính</text><line class="hl-route control" x1="1260" y1="956" x2="1315" y2="956"/><text class="hl-legend" x="1330" y="962">Điều phối</text><text class="hl-legend" x="1940" y="962" text-anchor="end">Góc 90°: bo tròn mặc định · thẳng khi khai báo</text></g>')
    return ''.join(parts)

def validate_high_level_svg(svg):
    root=ET.fromstring(svg); nodes={e.attrib["data-hl-node-id"]:e for e in root.findall(".//*[@data-hl-node-id]")}; edges={e.attrib["data-hl-edge-id"]:e for e in root.findall(".//*[@data-hl-edge-id]")}; groups={e.attrib["data-hl-group-id"]:e for e in root.findall(".//*[@data-hl-group-id]")}
    _require(set(nodes)==set(NODE_ORDER) and set(edges)==set(EDGE_ORDER) and set(groups)==set(BOUNDARIES), "D-092 serialized binding mismatch")
    styles={e.attrib.get("data-corner-style") for e in edges.values()}; _require(len(styles)==1 and styles<={"rounded","straight"}, "D-092 serialized corner mismatch")
    for edge_id,e in edges.items(): _require(e.tag=="path" and e.attrib.get("d")==orthogonal_path(ROUTE_POINTS[edge_id],next(iter(styles))) and e.attrib["d"].count("M")==1, f"D-092 serialized route mismatch: {edge_id}")
    return {"nodes":11,"edges":13,"groups":2,"continuous_routes":13,"corner_style":next(iter(styles))}

def high_level_table(plan):
    layout=layout_high_level(plan); rows=[]
    for node_id in NODE_ORDER:
        node=layout["nodes"][node_id]; rows.append(("node",node_id,node["role"],node["label"],"—"))
    for edge_id in EDGE_ORDER:
        edge=layout["edges"][edge_id]; rows.append(("edge",edge_id,edge["kind"],f'{edge["source"]} → {edge["target"]}',"rounded default"))
    for group_id in BOUNDARIES:
        group=layout["groups"][group_id]; rows.append(("group",group_id,"boundary",group["label"],", ".join(group["member_ids"])))
    return '<details class="hl-details"><summary>Dữ liệu thay thế có thể kiểm chứng</summary><table><thead><tr><th>Collection</th><th>Semantic ID</th><th>Role/kind</th><th>Nhãn/quan hệ</th><th>Chi tiết</th></tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{escape(str(v))}</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></details>'
