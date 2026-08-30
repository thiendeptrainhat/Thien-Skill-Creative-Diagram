"""D-084 exact approved-artifact adoption; not a general Sankey layout engine."""
import hashlib
from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ASSET=Path(__file__).resolve().parents[1]/'assets/p18-approved/sankey-review17.svg'
APPROVED_SHA256='e31e04c8b84944a91ad9ff99b719880539cdac15a3e71da0c8712dd27fa03a42'
NS={'s':'http://www.w3.org/2000/svg'}
COLOR_ROLE={
    '#f7f6f2':'canvas','#eeece7':'surface_alt','#ffffff':'surface',
    '#252b3c':'text','#4f5e76':'connector','#c7ccd2':'border','#d9d7d2':'grid',
    '#f26a32':'accent','#f8e7dd':'accent_soft','#df5522':'accent_text',
    '#53627b':'connector','#778194':'muted','#fff3ec':'accent_soft',
    '#2f65af':'blue','#7c9167':'green','#e8ebee':'surface_alt',
}

def original_svg():
    raw=ASSET.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=APPROVED_SHA256:
        raise ValueError('Approved P-18 Sankey asset hash mismatch')
    return raw.decode('utf-8')

def approved_material():
    root=ET.fromstring(original_svg())
    nodes=[]
    for node in root.findall('.//*[@data-sankey-node]'):
        key=node.get('data-sankey-node')
        title=node.find('.//*[@data-label-role="title"]').text
        nodes.append({'id':key,'role':{'source':'source','stage':'stage','outcome':'sink'}[node.get('data-column')],
                      'label':title,'value':int(node.get('data-value')),'unit':'min'})
    edges=[{'id':edge.get('data-sankey-ribbon'),'source':edge.get('data-source-node'),
            'target':edge.get('data-target-node'),'kind':'flow','directed':True,
            'amount':int(edge.get('data-value')),'unit':'min'} for edge in root.findall('.//*[@data-sankey-ribbon]')]
    return {'nodes':nodes,'edges':edges,'title':root.find('s:title',NS).text,'description':root.find('s:desc',NS).text}

def validate_approved_input(ir):
    material=approved_material()
    for collection in ('nodes','edges'):
        actual=[{k:v for k,v in item.items() if k!='source_refs'} for item in ir[collection]]
        if actual!=material[collection]:
            raise ValueError('Sankey replacement accepts only the exact approved P-18 data; arbitrary-data layout is not implemented')
    if any(ir[k] for k in ('groups','lanes','series','axes','annotations')):
        raise ValueError('Approved Sankey cannot silently omit extra material')
    if ir['diagram']['title']!=material['title'] or ir['diagram']['variant_ids']:
        raise ValueError('Approved Sankey title/variant mismatch')

def approved_svg(mode,tokens):
    raw=original_svg()
    if mode=='neutral-light': return raw
    if mode not in ('neutral-dark','editorial'): raise ValueError('Unsupported approved-Sankey mode')
    def paint(match):
        color=match.group().lower()
        if color not in COLOR_ROLE: raise ValueError('Unmapped approved-Sankey paint: '+color)
        return tokens[COLOR_ROLE[color]]
    return re.sub(r'#[0-9a-fA-F]{6}\b',paint,raw).replace('data-mode="neutral-light"',f'data-mode="{mode}"',1)

def normalize_paint(svg):
    """Allow only hex-paint changes and mode label when comparing this one asset."""
    return re.sub(r'#[0-9a-fA-F]{6}\b','#PAINT',re.sub(r'data-mode="(?:neutral-light|neutral-dark|editorial)"','data-mode="MODE"',svg))

def sankey_table(ir):
    validate_approved_input(ir)
    rows=[[n['id'],'Node · '+n['role'],n['label'],str(n['value'])+' min'] for n in ir['nodes']]
    rows.extend([e['id'],'Flow',e['source']+' → '+e['target'],str(e['amount'])+' min'] for e in ir['edges'])
    return '<details><summary>Dữ liệu thay thế có thể kiểm chứng</summary><p>Sankey P-18R6 review-17 · tổng 12,000 CI minutes · flaked 1,000 / 12,000 = 8.3%.</p><table><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in ('Semantic IDs','Loại','Nội dung / Luồng','Giá trị'))+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></details>'
