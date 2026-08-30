#!/usr/bin/env python3
"""Build three deterministic local-only v2.0.0 package candidates."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
P20 = ROOT / "evidence" / "p20"
CANDIDATE_DIST = P20 / "candidate-dist"
VERSION = "2.0.0"
CANDIDATE_ID = "TCD-PACKAGES-2.0.0-RC1"
LEGAL_CANDIDATE_ID = "TCD-LEGAL-2.0.0-RC1"
SKILL_ID = "thien-skill-creative-diagram"
PACKAGE_FILES = {
    "claude-plugin": f"{SKILL_ID}-{VERSION}-claude-plugin.zip",
    "openai-plugin": f"{SKILL_ID}-{VERSION}-openai-plugin.zip",
    "universal-raw-skill": f"{SKILL_ID}-{VERSION}-universal-raw-skill.zip",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_module("p13_builder_base", ROOT / "evidence" / "p13" / "build_packages.py")
legal_builder = load_module("p20_legal_builder", P20 / "build_legal_candidate_v2.py")
base.VERSION = VERSION
base.CANDIDATE_ID = CANDIDATE_ID
base.PACKAGE_FILES = PACKAGE_FILES
base.ZIP_TIMESTAMP = (2026, 8, 30, 0, 0, 0)


def legal_files() -> dict[str, bytes]:
    return legal_builder.candidate_files()


base.legal_files = legal_files


def expected_build() -> tuple[dict, dict[str, bytes], bytes]:
    mappings = base.package_mappings()
    runtime_digest = base.digest_logical(base.runtime_files())
    legal = legal_files()
    legal_digest = base.digest_logical(legal)
    archives = {target: base.zip_bytes(files) for target, files in mappings.items()}
    packages = []
    for target in sorted(archives):
        members = [
            {"path": path, "role": base.role_for(path), "bytes": len(data), "sha256": base.sha(data)}
            for path, data in mappings[target].items()
        ]
        packages.append({
            "target": target,
            "filename": PACKAGE_FILES[target],
            "sha256": base.sha(archives[target]),
            "bytes": len(archives[target]),
            "file_count": len(members),
            "runtime_core_aggregate_sha256": runtime_digest,
            "legal_bundle_aggregate_sha256": legal_digest,
            "members": members,
        })
    record = {
        "record_id": "P20-PACKAGE-BUILD-1",
        "candidate_id": CANDIDATE_ID,
        "version": VERSION,
        "built_at": "2026-08-30T00:00:00+07:00",
        "zip_timestamp": "2026-08-30T00:00:00",
        "canonical_source": SKILL_ID,
        "source_gallery_lineage": "P17 + exact P18 review-17 + P19B review-45 + P19C review-01",
        "legal_candidate_id": LEGAL_CANDIDATE_ID,
        "legal_candidate_aggregate_sha256": legal_digest,
        "brand_decision": "D-130 exact-byte carry-forward candidate from D-027/D-028",
        "authorization": "D-130",
        "status": "LOCAL-CANDIDATE-NOT-RELEASE-ELIGIBLE",
        "output_scope": "evidence/p20/candidate-dist only; historical dist is untouched",
        "packages": packages,
    }
    sums = "".join(f"{item['sha256']}  {item['filename']}\n" for item in packages).encode("utf-8")
    return record, archives, sums


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record, archives, sums = expected_build()
    record_bytes = base.canonical_json(record)
    expected = {CANDIDATE_DIST / PACKAGE_FILES[target]: data for target, data in archives.items()}
    expected[P20 / "package-build.json"] = record_bytes
    expected[CANDIDATE_DIST / "SHA256SUMS.txt"] = sums
    if args.check:
        drift = [str(path.relative_to(ROOT)) for path, data in expected.items() if not path.is_file() or path.read_bytes() != data]
        print(json.dumps({"status": "PASS" if not drift else "FAIL", "drift": drift, "candidate_id": CANDIDATE_ID}, indent=2))
        return 1 if drift else 0
    CANDIDATE_DIST.mkdir(parents=True, exist_ok=True)
    for path, data in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(json.dumps({"status": "BUILT", "packages": len(archives), "candidate_id": CANDIDATE_ID}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
