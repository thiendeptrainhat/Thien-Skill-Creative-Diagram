"""Preserve exact D-084/D-085 review-05 before Fishbone review-06."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-05-1.5.0'
PINS = {
    'evidence/p19/gallery/P-19B-MANIFEST.json': 'fe8d1ec697c140f867ae476774373b0194f7c851004734e57aa2f285eb960e11',
    'evidence/p19/P-19B-PLAN-MANIFEST.json': '376e0212513610d3815c80420b4b671d67b4f3a00d70d189826ea425023e3732',
    'evidence/p19/P-19B-SOURCE-MANIFEST.json': 'b00d3375643196659c8f79d69adc35589f3efb7dbb6b2848745393126e868de3',
}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if DEST.exists(): raise RuntimeError('Archive exists; refusing overwrite')
    records = dict(PINS)
    for name, expected in PINS.items():
        if digest(ROOT / name) != expected: raise RuntimeError(f'Candidate pin mismatch: {name}')
        manifest = json.loads((ROOT / name).read_text())
        for item in manifest.get('files', manifest.get('records', [])):
            records[item['path']] = item['sha256']
    for path in (ROOT / 'evidence/p19/comparison').iterdir():
        if path.is_file(): records[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in records.items():
        if digest(ROOT / name) != expected: raise RuntimeError(f'Source drift: {name}')
    protected = {}
    for directory in ('evidence/p18', 'evidence/p19/history', 'evidence/p19/withdrawn', 'dist', '.release-staging'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file(): protected[str(path.relative_to(ROOT))] = digest(path)
    for name in ('evidence/p19/P-19A-SOURCE-MANIFEST.json', 'evidence/p19/P-19A-PLAN-MANIFEST.json',
                 'thien-skill-creative-diagram/scripts/tests/semantic_fixtures.py',
                 'thien-skill-creative-diagram/scripts/visual_adapters_v15.py'):
        protected[name] = digest(ROOT / name)
    for name, expected in records.items():
        target = DEST / 'snapshot' / name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        assert digest(target) == expected
    receipt = {'candidate_id': 'P19B-P18-INHERITED-THREE-MODE-REVIEW-05-1.5.0',
               'disposition': 'historical before D-086 Fishbone-only remediation; not owner approval',
               'manifest_pins': PINS, 'snapshot_records': records, 'protected_records': protected}
    (DEST / 'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'archived_files': len(records), 'protected_files': len(protected)}))

if __name__ == '__main__': main()
