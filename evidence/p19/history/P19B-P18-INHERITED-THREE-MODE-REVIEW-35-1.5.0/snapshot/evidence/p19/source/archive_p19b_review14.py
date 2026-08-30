#!/usr/bin/env python3
"""Preserve exact D-094 review-14 before Layers review-15."""
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-14-1.5.0"
PINS = {
    "evidence/p19/gallery/P-19B-MANIFEST.json": "1ee5be8ff832fd19725270be8349479048d92662ceb69cd3437116f9e09acef6",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "64dd5516498bb70910ad8cb3397958f00d8c03214c31733a0e236d8231de992a",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "a79cce1a9609bcb7729dc18fae6cdd92d117c596b42ec0c6dfd2dbda365b1cab",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if DEST.exists():
        raise RuntimeError("Archive exists; refusing overwrite")
    records = dict(PINS)
    for name, expected in PINS.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f"Candidate pin mismatch: {name}")
        manifest = json.loads((ROOT / name).read_text())
        for item in manifest.get("files", manifest.get("records", [])):
            records[item["path"]] = item["sha256"]
    for path in (ROOT / "evidence/p19/comparison").iterdir():
        if path.is_file():
            records[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in records.items():
        if digest(ROOT / name) != expected:
            raise RuntimeError(f"Source drift: {name}")

    protected = {}
    for directory in ("evidence/p18", "evidence/p19/history", "evidence/p19/withdrawn", "dist", ".release-staging"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file():
                protected[str(path.relative_to(ROOT))] = digest(path)
    for name in (
        "evidence/p19/P-19A-SOURCE-MANIFEST.json",
        "evidence/p19/P-19A-PLAN-MANIFEST.json",
        "thien-skill-creative-diagram/scripts/semantic_grammars.py",
        "thien-skill-creative-diagram/scripts/tests/semantic_fixtures.py",
        "thien-skill-creative-diagram/scripts/visual_adapters_v15.py",
    ):
        protected[name] = digest(ROOT / name)

    for name, expected in records.items():
        target = DEST / "snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        if digest(target) != expected:
            raise RuntimeError(f"Archive copy drift: {name}")
    receipt = {
        "candidate_id": "P19B-P18-INHERITED-THREE-MODE-REVIEW-14-1.5.0",
        "disposition": "historical before D-095 Layers addition; not owner approval",
        "manifest_pins": PINS,
        "snapshot_records": records,
        "protected_records": protected,
    }
    (DEST / "ARCHIVE-RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archived_files": len(records), "protected_files": len(protected)}))


if __name__ == "__main__":
    main()
