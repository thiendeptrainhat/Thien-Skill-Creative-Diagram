"""Move the exact owner-withdrawn gallery files to recoverable QA custody."""
import hashlib
import json
from pathlib import Path
import shutil
from p19_scope import ROOT, REUSED_TYPES, p18_references

DEST = ROOT / 'evidence/p19/withdrawn/review05-duplicates'
DRAFT_FILES = (
    'thien-skill-creative-diagram/assets/p18-approved/sankey-review17.svg',
    'thien-skill-creative-diagram/scripts/sankey_p18_v15.py',
    'thien-skill-creative-diagram/scripts/tests/sankey_p18_fixture.py',
    'evidence/p19/P-19B-REVIEW-05-DESIGN.md',
)
EDITED_FILES = (
    'thien-skill-creative-diagram/scripts/gallery_renderer_v15.py',
    'thien-skill-creative-diagram/scripts/tests/test_gallery_renderer_v15.py',
    'evidence/p19/source/generate_p19b_gallery.py',
    'evidence/p19/source/verify_p19b.py',
    'evidence/p19/comparison/generate_comparison.py',
)


def main():
    if DEST.exists():
        raise ValueError('Withdrawal custody already exists; refusing overwrite')
    p18_references()
    gallery = ROOT / 'evidence/p19/gallery'
    inventory = json.loads((gallery / 'P-19B-INVENTORY.json').read_bytes())
    records = [r for r in inventory['records'] if r['capability_id'] is None and r['identity'] in REUSED_TYPES]
    if len(records) != 42 or {r['identity'] for r in records} != REUSED_TYPES:
        raise ValueError('Expected exactly 14 canonical types x three modes')
    targets = [gallery / r['path'] for r in records]
    targets += [gallery / 'previews' / f'type-{identity}.svg' for identity in sorted(REUSED_TYPES)]
    if len(targets) != 56 or len(set(targets)) != 56:
        raise ValueError('Unexpected withdrawal targets')
    for path in targets:
        if not path.is_file() or path.is_symlink() or path.parent not in (gallery / 'specimens', gallery / 'previews'):
            raise ValueError(f'Unsafe or missing target: {path.name}')
    for r in records:
        if hashlib.sha256((gallery / r['path']).read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('Inventory drift before withdrawal')
    receipt = {'authority': 'D-084/D-085', 'disposition': 'withdrawn duplicates, not an approved candidate',
               'note': 'Includes unfinished Sankey adoption draft; exact review-04 is separately archived.',
               'moved': {}, 'draft_copies': {}}
    for relative in DRAFT_FILES + EDITED_FILES:
        path = ROOT / relative
        target = DEST / 'interrupted-draft' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        receipt['draft_copies'][relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    for path in targets:
        relative = str(path.relative_to(ROOT))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        target = DEST / 'files' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        path.rename(target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
        receipt['moved'][relative] = digest
    (DEST / 'WITHDRAWAL-RECEIPT.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'recoverably_moved': len(targets), 'draft_copies': len(receipt['draft_copies'])}))


if __name__ == '__main__':
    main()
