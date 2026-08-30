#!/usr/bin/env python3
"""Preserve exact D-091 review-11 before high-level review-12."""
import hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "evidence/p19/history/P19B-P18-INHERITED-THREE-MODE-REVIEW-11-1.5.0"
PINS = {
    "evidence/p19/gallery/P-19B-MANIFEST.json": "85ba48b7b66d985bc39dd5ffc5ca30212248899ae9d454cc6b7ff3834229c54a",
    "evidence/p19/P-19B-PLAN-MANIFEST.json": "3a2ac8db7631c5a6a0c419a8b6c34e0fe44ae0cee28a6f42836655f12fc02d6c",
    "evidence/p19/P-19B-SOURCE-MANIFEST.json": "bc299a1c03e419ef1ebe874593e8cc347b3bc9a5754280969c41fe35c88ee024",
}
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if DEST.exists(): raise RuntimeError("Archive exists; refusing overwrite")
    records = dict(PINS)
    for name, expected in PINS.items():
        if digest(ROOT/name) != expected: raise RuntimeError(f"Candidate pin mismatch: {name}")
        manifest = json.loads((ROOT/name).read_text())
        for item in manifest.get("files", manifest.get("records", [])): records[item["path"]] = item["sha256"]
    for path in (ROOT/"evidence/p19/comparison").iterdir():
        if path.is_file(): records[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in records.items():
        if digest(ROOT/name) != expected: raise RuntimeError(f"Source drift: {name}")
    protected = {}
    for directory in ("evidence/p18", "evidence/p19/history", "evidence/p19/withdrawn", "dist", ".release-staging"):
        for path in sorted((ROOT/directory).rglob("*")):
            if path.is_file(): protected[str(path.relative_to(ROOT))] = digest(path)
    for name in ("evidence/p19/P-19A-SOURCE-MANIFEST.json", "evidence/p19/P-19A-PLAN-MANIFEST.json", "thien-skill-creative-diagram/scripts/tests/semantic_fixtures.py", "thien-skill-creative-diagram/scripts/visual_adapters_v15.py"):
        protected[name] = digest(ROOT/name)
    for name, expected in records.items():
        target = DEST/"snapshot"/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, target)
        if digest(target) != expected: raise RuntimeError(f"Archive copy drift: {name}")
    receipt = {"candidate_id":"P19B-P18-INHERITED-THREE-MODE-REVIEW-11-1.5.0", "disposition":"historical before D-092 high-level-only remediation; not owner approval", "manifest_pins":PINS, "snapshot_records":records, "protected_records":protected}
    (DEST/"ARCHIVE-RECEIPT.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"archived_files":len(records),"protected_files":len(protected)}))
if __name__ == "__main__": main()
