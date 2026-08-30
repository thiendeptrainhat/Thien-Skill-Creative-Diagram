"""D-083 exact source scope, serialized flywheel and protected-byte checks."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
for path in (ROOT/'thien-skill-creative-diagram/scripts',ROOT/'thien-skill-creative-diagram/scripts/tests',ROOT/'evidence/p19/comparison'):
    sys.path.insert(0,str(path))
from gallery_renderer_v15 import P19B_CANDIDATE_ID, validate_target_geometry
from generate_comparison import p19_preview
from flywheel_review04_fixture import flywheel_fixture

OLD='P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0'
ARCHIVE=ROOT/'evidence/p19/history'/OLD
GALLERY=ROOT/'evidence/p19/gallery'

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def require(condition,message):
    if not condition: raise RuntimeError(message)

def main():
    receipt=json.loads((ARCHIVE/'ARCHIVE-RECEIPT.json').read_text())
    for name,expected in receipt['snapshot_records'].items():
        require(digest(ARCHIVE/'snapshot'/name)==expected,f'Archive drift: {name}')
    for name,expected in receipt['protected_records'].items():
        require(digest(ROOT/name)==expected,f'Protected drift: {name}')
    records=json.loads((GALLERY/'P-19B-INVENTORY.json').read_text())['records']
    unchanged_html=unchanged_preview=0
    proofs,measurements,geometries=[],[],[]
    proof_dir=ROOT/'evidence/p19/review04-checks'; proof_dir.mkdir(exist_ok=True)
    fixture=flywheel_fixture()
    expected_edges={e['id']:(e['source'],e['target']) for e in fixture['edges']}
    expected_spokes={a['id']:tuple(a['target_ids']) for a in fixture['annotations'] if len(a['target_ids'])==2}
    for record in records:
        path=GALLERY/record['path']; page=path.read_text()
        if record['canonical_type']!='loop-flywheel':
            require(page.replace(P19B_CANDIDATE_ID,OLD)==(ARCHIVE/'snapshot'/path.relative_to(ROOT)).read_text(),f'Non-target HTML drift: {path}')
            unchanged_html+=1
            if record['mode']=='neutral-light':
                preview=GALLERY/'previews'/(record['fixture_id']+'.svg')
                require(digest(preview)==digest(ARCHIVE/'snapshot'/preview.relative_to(ROOT)),f'Non-target preview drift: {preview}')
                unchanged_preview+=1
            if record['canonical_type'] in ('dp-integration','swimlane'):
                validate_target_geometry(re.search(r'<svg .*?</svg>',page,re.S).group(),record['canonical_type'])
            continue
        svg=re.search(r'<svg .*?</svg>',page,re.S).group(); geometries.append(svg.replace(record['mode'],'MODE'))
        root=ET.fromstring(svg)
        nodes=root.findall('.//*[@data-flywheel-node]')
        require(len(nodes)==7,'Seven material nodes required')
        require(sum(n.get('data-role')=='station' for n in nodes)==6,'Six cycle stations required')
        require(sum(n.get('data-role')=='shared-state' for n in nodes)==1,'Shared state is not a cycle station')
        rects={node.get('data-flywheel-node'):node.find('rect') for node in nodes}
        boxes={key:tuple(float(r.get(k)) for k in ('x','y','width','height')) for key,r in rects.items()}
        require(sum(r.get('class')=='flywheel-card decision' for r in rects.values())==1,'One decision highlight required')
        arcs=root.findall('.//*[@data-cycle-edge]'); spokes=root.findall('.//*[@data-contribution]')
        require({a.get('data-cycle-edge'):(a.get('data-source'),a.get('data-target')) for a in arcs}==expected_edges,'Cycle semantics differ')
        require({a.get('data-contribution'):(a.get('data-source'),a.get('data-target')) for a in spokes}==expected_spokes,'Contribution semantics differ')
        def inside(point,box):
            x,y,w,h=box
            return x <= point[0] <= x+w and y <= point[1] <= y+h
        _,_,width,height=map(float,root.get('viewBox').split())
        center=(width/2,height/2)
        for key,(x,y,w,h) in boxes.items():
            require(x>=20 and y>=20 and x+w<=width-20 and y+h<=height-20,'Canvas containment failed')
            for other,(ox,oy,ow,oh) in boxes.items():
                require(key==other or not (x<ox+ow+12 and x+w+12>ox and y<oy+oh+12 and y+h+12>oy),'Card clearance failed')
        for arc in arcs:
            route=arc.get('d')
            require(re.fullmatch(r'M[-\d.]+ [-\d.]+ A[-\d.]+ [-\d.]+ 0 0 1 [-\d.]+ [-\d.]+',route) is not None,'Expected one continuous clockwise arc')
            nums=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',route)))
            sx,sy,r,ry,_,_,_,ex,ey=nums
            require(r==ry and abs(math.dist(center,(sx,sy))-r)<.002 and abs(math.dist(center,(ex,ey))-r)<.002,'Shared-circle drift')
            a=math.atan2(sy-center[1],sx-center[0]); b=math.atan2(ey-center[1],ex-center[0]); b+=2*math.pi if b<a else 0
            for i in range(201):
                angle=a+(b-a)*i/200; point=(center[0]+r*math.cos(angle),center[1]+r*math.sin(angle))
                require(not any(inside(point,box) for box in boxes.values()),'Serialized arc intersects card')
        for spoke in spokes:
            require(spoke.get('marker-end')=='url(#flywheel-inward-arrow)','Missing inward arrow')
            sx,sy,ex,ey=map(float,re.findall(r'-?\d+(?:\.\d+)?',spoke.get('d')))
            require(math.dist(center,(ex,ey))<math.dist(center,(sx,sy)),'Spoke points outward')
            for i in range(101):
                point=(sx+(ex-sx)*i/100,sy+(ey-sy)*i/100)
                require(not any(inside(point,box) for box in boxes.values()),'Serialized spoke intersects card')
        require('class="bridge"' not in svg,'Erase overlay is forbidden')
        for collection in ('nodes','edges','annotations'):
            for item in fixture[collection]: require(item['id'] in page[page.index('<details'):],'Alternative dropped material')
        proof=proof_dir/f'type-loop-flywheel--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page.encode())[0])
        proofs.append({'path':str(proof.relative_to(ROOT)),'sha256':digest(proof),'source_html_sha256':digest(path)})
        measurements.append({'mode':record['mode'],'stations':6,'shared_state':1,'clockwise_arcs':len(arcs),'inward_spokes':len(spokes),'serialized_geometry':'PASS'})
    require(unchanged_html==126 and unchanged_preview==42,'Wrong mutation scope')
    require(len(geometries)==3 and len(set(geometries))==1,'Mode geometry drift')
    report={'candidate_id':P19B_CANDIDATE_ID,'authority':'D-083','status':'PASS','gallery_manifest_sha256':digest(GALLERY/'P-19B-MANIFEST.json'),
            'archived_files_verified':len(receipt['snapshot_records']),'protected_files_verified':len(receipt['protected_records']),
            'unchanged_non_target_html_after_candidate_id_normalization':unchanged_html,'byte_identical_non_target_preview_svg':unchanged_preview,
            'measurements':measurements,'proof_svg_files':proofs,'browser':'BLOCKED_NOT_EXECUTABLE','owner_approval':'pending','p19c':'not-performed'}
    (ROOT/'evidence/p19/P-19B-REVIEW-04-VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
