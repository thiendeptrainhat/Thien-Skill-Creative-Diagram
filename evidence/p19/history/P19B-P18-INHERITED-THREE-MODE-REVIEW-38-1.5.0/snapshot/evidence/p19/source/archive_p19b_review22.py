#!/usr/bin/env python3
"""Preserve exact D-102 review-22 before inset-cell Treemap review-23."""
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-22-1.5.0"
PINS = {
    "evidence/p19/gallery/P-19B-MANIFEST.json": "6c0a2f00c2eacc52c5a9c83621743b5e560c4189936e7224440ec8a116af17a4",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "795413b563e292ece6395723072d54f7cc01b627d1dbdb54a4c44e719499da6f",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "24e3a01f47f2bb9e49e614ced6d36dee501dfe0ccd69159de62be423e0d758c9",
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
    for directory in (
        "evidence/p18",
        "evidence/p19/history",
        "evidence/p19/withdrawn",
        "dist",
        ".release-staging",
    ):
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
        "candidate_id": "P19B-P18-INHERITED-THREE-MODE-REVIEW-22-1.5.0",
        "disposition": "historical before D-103 uniform-inset Treemap remediation; not owner approval",
        "manifest_pins": PINS,
        "snapshot_records": records,
        "protected_records": protected,
    }
    (DEST / "ARCHIVE-RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"archived_files": len(records), "protected_files": len(protected)}))


if __name__ == "__main__":
    main()
