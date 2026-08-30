"""D-084/D-085 coverage, exact reuse, withdrawal and unchanged artwork proof."""
import hashlib
import json
import sys
from pathlib import Path
from p19_scope import ROOT, REUSED_TYPES, p18_references

sys.path.insert(0, str(ROOT / 'thien-skill-creative-diagram/scripts'))
from gallery_renderer_v15 import P19B_CANDIDATE_ID

OLD = 'P19B-P18-INHERITED-THREE-MODE-REVIEW-04-1.5.0'
ARCHIVE = ROOT / 'evidence/p19/history' / OLD
GALLERY = ROOT / 'evidence/p19/gallery'
WITHDRAWN = ROOT / 'evidence/p19/withdrawn/review05-duplicates'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def verify():
    receipt = json.loads((ARCHIVE / 'ARCHIVE-RECEIPT.json').read_bytes())
    for name, expected in receipt['snapshot_records'].items():
        require(digest(ARCHIVE / 'snapshot' / name) == expected, f'Archive drift: {name}')
    for name, expected in receipt['protected_records'].items():
        require(digest(ROOT / name) == expected, f'Protected drift: {name}')
    inventory = json.loads((GALLERY / 'P-19B-INVENTORY.json').read_bytes())
    records = inventory['records']
    require(len(records) == 87, 'Expected exactly 87 retained HTML')
    require(len({r['identity'] for r in records}) == 29, 'Expected 29 retained identities')
    canonical = {r['identity'] for r in records if r['capability_id'] is None}
    require(len(canonical) == 25 and not canonical & REUSED_TYPES, 'Duplicate canonical type remains')
    require({r['capability_id'] for r in records if r['capability_id']} == {'CAP-V17', 'CAP-V18', 'CAP-V19', 'CAP-V20'}, 'A capability was dropped')
    require(inventory['reused_p18_anchors'] == p18_references(), 'Incorrect P-18 reuse binding')
    unchanged_previews = 0
    for record in records:
        path = GALLERY / record['path']
        page = path.read_text()
        original = (ARCHIVE / 'snapshot' / path.relative_to(ROOT)).read_text()
        require(page.replace(P19B_CANDIDATE_ID, OLD) == original, f'Retained artwork changed: {path.name}')
        if record['mode'] == 'neutral-light':
            preview = GALLERY / 'previews' / (record['fixture_id'] + '.svg')
            require(digest(preview) == digest(ARCHIVE / 'snapshot' / preview.relative_to(ROOT)), f'Preview drift: {preview.name}')
            unchanged_previews += 1
    withdrawal = json.loads((WITHDRAWN / 'WITHDRAWAL-RECEIPT.json').read_bytes())
    require(len(withdrawal['moved']) == 56, 'Expected 42 HTML and 14 previews in custody')
    for name, expected in withdrawal['moved'].items():
        require(not (ROOT / name).exists(), f'Withdrawn active file reappeared: {name}')
        require(digest(WITHDRAWN / 'files' / name) == expected, f'Custody drift: {name}')
    for name, expected in withdrawal['draft_copies'].items():
        require(digest(WITHDRAWN / 'interrupted-draft' / name) == expected, f'Draft custody drift: {name}')
    require(unchanged_previews == 29, 'Wrong preview count')
    return {'candidate_id': P19B_CANDIDATE_ID, 'authority': 'D-084/D-085', 'status': 'PASS',
            'gallery_manifest_sha256': digest(GALLERY / 'P-19B-MANIFEST.json'),
            'archived_files_verified': len(receipt['snapshot_records']),
            'protected_files_verified': len(receipt['protected_records']),
            'retained_html_unchanged_except_candidate_id': len(records),
            'retained_preview_svg_byte_identical': unchanged_previews,
            'approved_p18_anchor_pairs_hash_verified': len(p18_references()),
            'withdrawn_html': 42, 'withdrawn_previews': 14, 'withdrawn_files_recoverable': 56,
            'combined_canonical_type_count': len(canonical | REUSED_TYPES),
            'capabilities_retained': 4, 'p19_mode_count': 3,
            'p18_extra_mode_derivation': 'not-performed',
            'browser': 'BLOCKED_NOT_EXECUTABLE', 'owner_approval': 'pending', 'p19c': 'not-performed'}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'evidence/p19/P-19B-REVIEW-05-VERIFICATION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2))
