"""D-084/D-085: reuse approved P-18 anchors; do not emit duplicate P-19 types."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P18 = ROOT / 'evidence/p18/r6'
P18_MANIFEST_SHA256 = '7925c1ab0515a59057851bb3888ff4d9974e5f5701b873b1f11468a5fd64a03a'
REUSED_TYPES = frozenset({
    'architecture', 'data-flow', 'deployment', 'dependency-graph', 'flowchart',
    'swimlane', 'timeline', 'user-journey', 'org-chart', 'pyramid-funnel',
    'database-schema', 'quadrant', 'scatter-plot', 'sankey',
})


def p18_references():
    manifest_bytes = (P18 / 'P-18R6-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != P18_MANIFEST_SHA256:
        raise ValueError('Approved P-18 manifest drift')
    manifest = json.loads(manifest_bytes)
    pinned = {r['path']: r['sha256'] for r in manifest['files']}
    inventory_path = P18 / 'P-18R6-INVENTORY.json'
    if hashlib.sha256(inventory_path.read_bytes()).hexdigest() != pinned[str(inventory_path.relative_to(ROOT))]:
        raise ValueError('Approved P-18 inventory drift')
    inventory = json.loads(inventory_path.read_bytes())
    if {a['canonical_type'] for a in inventory['engines']} != REUSED_TYPES:
        raise ValueError('Owner reuse list does not match the approved anchors')
    records = []
    for anchor in inventory['engines']:
        row = {'identity': anchor['canonical_type'], 'layout_engine': anchor['engine'],
               'mode': 'neutral-light', 'disposition': 'use-approved-p18-no-p19-duplicate'}
        for kind in ('html', 'svg'):
            path = P18 / anchor[kind]
            relative = str(path.relative_to(ROOT))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != pinned[relative]:
                raise ValueError(f'Approved P-18 artifact drift: {relative}')
            row[kind] = relative
            row[kind + '_sha256'] = digest
        records.append(row)
    return records
