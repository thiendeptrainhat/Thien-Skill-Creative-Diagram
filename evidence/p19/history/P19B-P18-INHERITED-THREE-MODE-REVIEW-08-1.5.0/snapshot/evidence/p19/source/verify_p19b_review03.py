"""D-082 exact scope, calendar geometry, three modes and immutable-corpus checks."""
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

ROOT=Path(__file__).resolve().parents[3]
for path in (ROOT/'thien-skill-creative-diagram/scripts', ROOT/'thien-skill-creative-diagram/scripts/tests', ROOT/'evidence/p19/comparison'):
    sys.path.insert(0,str(path))
from gallery_renderer_v15 import P19B_CANDIDATE_ID, validate_target_geometry
from generate_comparison import p19_preview
from gantt_review03_fixture import gantt_fixture

OLD='P19B-P18-INHERITED-THREE-MODE-REVIEW-02-1.5.0'
ARCHIVE=ROOT/'evidence/p19/history'/OLD
GALLERY=ROOT/'evidence/p19/gallery'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

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
    measurements,proofs,geometries=[],[],[]
    proof_dir=ROOT/'evidence/p19/review03-checks'
    proof_dir.mkdir(exist_ok=True)
    fixture=gantt_fixture()
    source={node['id']:node for node in fixture['nodes']}
    for record in records:
        path=GALLERY/record['path']
        page=path.read_text()
        old=ARCHIVE/'snapshot'/path.relative_to(ROOT)
        if record['canonical_type']!='gantt':
            require(page.replace(P19B_CANDIDATE_ID,OLD)==old.read_text(),f'Non-Gantt HTML drift: {path}')
            unchanged_html+=1
            if record['mode']=='neutral-light':
                preview=GALLERY/'previews'/(record['fixture_id']+'.svg')
                require(digest(preview)==digest(ARCHIVE/'snapshot'/preview.relative_to(ROOT)),f'Non-Gantt preview drift: {preview}')
                unchanged_preview+=1
            if record['canonical_type'] in ('dp-integration','swimlane'):
                validate_target_geometry(re.search(r'<svg .*?</svg>',page,re.S).group(),record['canonical_type'])
            continue
        svg=re.search(r'<svg .*?</svg>',page,re.S).group()
        geometries.append(svg.replace(record['mode'],'MODE'))
        root=ET.fromstring(svg)
        scale=root.find('.//*[@data-gantt-scale-start]')
        start=datetime.fromisoformat(scale.get('data-gantt-scale-start'))
        end=datetime.fromisoformat(scale.get('data-gantt-scale-end'))
        require(start.isoformat()=='2026-09-01T00:00:00+07:00' and end.isoformat()=='2026-12-01T00:00:00+07:00','Wrong calendar extent')
        bars=root.findall('.//rect[@data-task-id]')
        bands={b.get('data-phase-id'):b for b in root.findall('.//rect[@class="gantt-phase"][@data-phase-id]')}
        require(len(bars)==7 and len(bands)==3,'Wrong Gantt row/phase counts')
        require(sum(b.get('class')=='gantt-gate' for b in bars)==1,'Expected one gate')
        month_labels=[t.text for t in root.findall('.//text[@class="gantt-month"]')]
        require(month_labels==['Tháng 09 · 2026','Tháng 10 · 2026','Tháng 11 · 2026'],'Month headers mismatch')
        for bar in bars:
            node=source[bar.get('data-task-id')]
            s,e=datetime.fromisoformat(node['start']),datetime.fromisoformat(node['end'])
            x=320+(s-start).total_seconds()/(end-start).total_seconds()*1220
            w=(e-s).total_seconds()/(end-start).total_seconds()*1220
            require(abs(float(bar.get('x'))-x)<.001 and abs(float(bar.get('width'))-w)<.001,'Timestamp-to-position drift')
            band=bands[bar.get('data-phase-id')]
            y,h=float(bar.get('y')),float(bar.get('height'))
            require(y-float(band.get('y'))>=12 and float(band.get('y'))+float(band.get('height'))-y-h>=12,'Phase containment failure')
            for field in ('start','end'):
                require(bar.get('data-'+field)==node[field] and node[field] in page[page.index('<details'):],'Date alternative lost')
        proof=proof_dir/f'type-gantt--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page.encode())[0])
        proofs.append({'path':str(proof.relative_to(ROOT)),'sha256':digest(proof),'source_html_sha256':digest(path)})
        measurements.append({'mode':record['mode'],'phases':len(bands),'ordinary_tasks':6,'gate_windows':1,'calendar_days':91,'geometry':'PASS'})
    require(unchanged_html==126 and unchanged_preview==42,'Unexpected mutation scope')
    require(len(geometries)==3 and len(set(geometries))==1,'Mode geometry drift')
    report={'candidate_id':P19B_CANDIDATE_ID,'authority':'D-082','status':'PASS',
            'gallery_manifest_sha256':digest(GALLERY/'P-19B-MANIFEST.json'),
            'archived_files_verified':len(receipt['snapshot_records']),
            'protected_files_verified':len(receipt['protected_records']),
            'unchanged_non_gantt_html_after_candidate_id_normalization':unchanged_html,
            'byte_identical_non_gantt_preview_svg':unchanged_preview,
            'measurements':measurements,'proof_svg_files':proofs,
            'browser':'BLOCKED_NOT_EXECUTABLE','owner_approval':'pending','p19c':'not-performed'}
    (ROOT/'evidence/p19/P-19B-REVIEW-03-VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
