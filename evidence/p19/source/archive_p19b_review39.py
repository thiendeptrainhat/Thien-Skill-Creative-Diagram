#!/usr/bin/env python3
"""Preserve exact D-119 review-39 before D-120 Bubble remediation."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-39-1.5.0"
PINS = {
    "evidence/p19/gallery/P-19B-MANIFEST.json": "b2d8fd30720b13b6079c2add4697cce65507ea5cc4b3ff826eaf7c117daff153",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "892bd9459fc94721bf3a91660533642a95dfd389e5f46979f08eebe589581476",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "b8cb7211b9087a02c9a301e042126e81cfee9e6ed128ea1a23c1ce68ca2237ce",
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
        "candidate_id": "P19B-P18-INHERITED-THREE-MODE-REVIEW-39-1.5.0",
        "disposition": "historical before D-120 Bubble rename and detailed quantitative redraw; not owner approval",
        "manifest_pins": PINS,
        "snapshot_records": records,
        "protected_records": protected,
    }
    (DEST / "ARCHIVE-RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archived_files": len(records), "protected_files": len(protected)}))


if __name__ == "__main__":
    main()
