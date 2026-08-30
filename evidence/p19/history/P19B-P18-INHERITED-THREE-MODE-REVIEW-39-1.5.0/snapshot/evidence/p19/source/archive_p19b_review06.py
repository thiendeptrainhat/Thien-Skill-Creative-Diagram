#!/usr/bin/env python3
"""Preserve exact D-086 review-06 before dp-integration review-07."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0'
PINS = {
    'evidence/p19/gallery/P-19B-MANIFEST.json': 'f5419c55276a694b1961cd61b917152670ffaf1aacec1166a938c65843c7f531',
    'evidence/p19/P-19B-PLAN-MANIFEST.json': '058af924c66d98db80a81363e31f9feb04046ed74c855056eeeb572861db524a',
    'evidence/p19/P-19B-SOURCE-MANIFEST.json': '19a48906fe3630f37bd254c6fbd1095a668e97085ee928e845e87bb77d64627d',
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
        manifest = json.loads((ROOT / name).read_text(encoding='utf-8'))
        for item in manifest.get('files', manifest.get('records', [])):
            records[item['path']] = item['sha256']
    for path in (ROOT / 'evidence/p19/comparison').iterdir():
        if path.is_file():
            records[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in records.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f'Source drift: {name}')
    protected = {}
    for directory in ('evidence/p18', 'evidence/p19/history', 'evidence/p19/withdrawn', 'dist', '.release-staging'):
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
        if digest(target) != expected:
            raise RuntimeError(f'Archive copy drift: {name}')
    receipt = {
        'candidate_id': 'P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0',
        'disposition': 'historical before D-087 dp-integration-only remediation; not owner approval',
        'manifest_pins': PINS,
        'snapshot_records': records,
        'protected_records': protected,
    }
    (DEST / 'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps({'archived_files': len(records), 'protected_files': len(protected)}))


if __name__ == '__main__':
    main()
