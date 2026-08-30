"""Preserve the exact D-082 candidate before the owner-authorized D-083 change."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0'
PINS = {
    'evidence/p19/gallery/P-19B-MANIFEST.json': '4ef32cfa8667c501e9449be67deb08dcd7074b27454fb9162b1e5855106d90c4',
    'evidence/p19/P-19B-PLAN-MANIFEST.json': '8e46a1be17835da76dbcac38a70e97a323283f5e33df4acf084eb661dffd9849',
    'evidence/p19/P-19B-SOURCE-MANIFEST.json': 'd23b602b75e1849229f9718a06ba9abcd455c5e00247429d6cdbd6cb88f157af',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if DEST.exists():
        raise RuntimeError('Archive exists; refusing overwrite')
    records = dict(PINS)
    for name, expected in PINS.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f'Candidate pin mismatch: {name}')
        manifest = json.loads((ROOT / name).read_text())
        for item in manifest.get('files', manifest.get('records', [])):
            records[item['path']] = item['sha256']
    for path in (ROOT / 'evidence/p19/comparison').iterdir():
        if path.is_file():
            records[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in records.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f'Source drift: {name}')
    protected = {}
    for directory in ('evidence/p18', 'evidence/p19/history', 'dist', '.release-staging'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                protected[str(path.relative_to(ROOT))] = digest(path)
    for name in ('evidence/p19/P-19A-SOURCE-MANIFEST.json', 'evidence/p19/P-19A-PLAN-MANIFEST.json',
                 'thien-skill-creative-diagram/scripts/tests/semantic_fixtures.py',
                 'thien-skill-creative-diagram/scripts/visual_adapters_v15.py'):
        protected[name] = digest(ROOT / name)
    for name, expected in records.items():
        target = DEST / 'snapshot' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        assert digest(target) == expected
    receipt = {'candidate_id': 'P19B-P18-INHERITED-THREE-MODE-REVIEW-03-1.5.0',
               'disposition': 'historical before D-083 flywheel-only redesign; not owner approval',
               'manifest_pins': PINS, 'snapshot_records': records, 'protected_records': protected}
    (DEST / 'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'archived_files': len(records), 'protected_files': len(protected)}))

if __name__ == '__main__':
    main()
