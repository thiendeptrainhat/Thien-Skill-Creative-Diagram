"""Archive exact review-01 before D-081; refuse overwrite or source drift."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-01-1.5.0"
PINS = {
    "evidence/p19/gallery/P-19B-MANIFEST.json": "e866fb915a09973bb3a035b6659a0b98d66eeda4701031a4d5868cbaea803eec",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "b2f28352a6aa596880e07c9f34ff911b7bba8ac3a62710b3e8d38335eac8f1a2",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "6c6b4fad02fdcfa2fa766d96a5b0407ac17da3a2e8f52130eb6cd8a44a83eca5",
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
    # Freeze the whole protected corpus for an after-change check, without copying it.
    protected = {}
    for directory in ("evidence/p18", "dist", ".release-staging"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file():
                protected[str(path.relative_to(ROOT))] = digest(path)
    for name in ("evidence/p19/P-19A-SOURCE-MANIFEST.json", "evidence/p19/P-19A-PLAN-MANIFEST.json"):
        protected[name] = digest(ROOT / name)
    for name, expected in records.items():
        target = DEST / "snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        if digest(target) != expected:
            raise RuntimeError(f"Archive copy drift: {name}")
    receipt = {"candidate_id": "P19B-P18-INHERITED-THREE-MODE-REVIEW-01-1.5.0",
               "disposition": "historical; owner reported dp-integration containment and swimlane continuity defects",
               "manifest_pins": PINS, "snapshot_records": records, "protected_records": protected}
    (DEST / "ARCHIVE-RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"archived_files": len(records), "protected_files": len(protected), "archive": str(DEST.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
