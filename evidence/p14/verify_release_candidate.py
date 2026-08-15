#!/usr/bin/env python3
"""Dependency-free verifier for the frozen P-14 release candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
P14 = ROOT / "evidence" / "p14"
FREEZE = P14 / "release-candidate-freeze.json"
REPORT = P14 / "freeze-verification-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, condition: bool, checks: list[dict]) -> None:
    checks.append({"check": label, "result": "PASS" if condition else "FAIL"})


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: list[dict] = []

    check("release candidate identity", freeze["record_id"] == "TCD-RELEASE-1.0.0-RC1", checks)
    check("version", freeze["version"] == "1.0.0", checks)
    check(
        "owner-approved freeze and exact release authorization",
        freeze["status"] == "RELEASE_AUTHORIZED_PENDING_GITHUB_AUTHENTICATION"
        and freeze["owner_approval"]["exact_release_candidate_approved"]
        and freeze["owner_approval"]["all_three_zip_hashes_approved"]
        and freeze["owner_approval"]["accepted_medium_risks"] == ["P14-R01", "P14-R02"]
        and freeze["release_authorization"]["decision_id"] == "D-037"
        and freeze["release_authorization"]["g07_result"] == "PASS"
        and freeze["release_authorized"],
        checks,
    )
    check(
        "publication scope A sanitized mirror ready",
        freeze["repository_publication_scope"]["selection"] == "A_FULL_PRIVATE_AUDIT_REPOSITORY"
        and freeze["repository_publication_scope"]["publication_form"] == "DETERMINISTIC_SANITIZED_MIRROR"
        and freeze["repository_publication_scope"]["decision"] == "D-036"
        and freeze["repository_publication_scope"]["publication_ready"],
        checks,
    )
    readme = freeze["repository_readme"]
    readme_path = ROOT / readme["path"]
    check(
        "repository README installation and license",
        readme_path.is_file()
        and sha256(readme_path) == readme["sha256"]
        and readme["detailed_installation"]
        and readme["license_information"]
        and "LICENSE.md" in readme_path.read_text(encoding="utf-8")
        and "SHA256SUMS.txt" in readme_path.read_text(encoding="utf-8"),
        checks,
    )

    for artifact in freeze["artifacts"]:
        path = ROOT / artifact["path"]
        check(f"exists: {artifact['target']}", path.is_file(), checks)
        if path.is_file():
            check(f"bytes: {artifact['target']}", path.stat().st_size == artifact["bytes"], checks)
            check(f"sha256: {artifact['target']}", sha256(path) == artifact["sha256"], checks)

    checksum = freeze["checksum_manifest"]
    checksum_path = ROOT / checksum["path"]
    check("checksum manifest", checksum_path.is_file() and sha256(checksum_path) == checksum["sha256"], checks)

    for binding in freeze["approval_bindings"]:
        path = ROOT / binding["path"]
        check(f"{binding['gate']} evidence", binding["result"] == "PASS" and path.is_file() and sha256(path) == binding["sha256"], checks)

    for key in ("approval_record",):
        legal = freeze["legal_candidate"]
        path = ROOT / legal[key]
        check("lawyer approval record", path.is_file() and sha256(path) == legal[f"{key}_sha256"], checks)

    for key in ("approved_golden_manifest", "approved_brand_selection"):
        record = freeze[key]
        path = ROOT / record["path"]
        check(key.replace("_", " "), path.is_file() and sha256(path) == record["sha256"], checks)

    surface = freeze["surface_status"]
    surface_path = ROOT / surface["record"]
    check("surface record", surface_path.is_file() and sha256(surface_path) == surface["record_sha256"], checks)
    check("surface counts", (surface["supported"], surface["conditional"], surface["unsupported"]) == (0, 13, 2), checks)

    failed = [item for item in checks if item["result"] == "FAIL"]
    report = {
        "record_id": "P14-FREEZE-VERIFICATION-1",
        "candidate": freeze["record_id"],
        "status": "RELEASE_AUTHORIZED_PENDING_GITHUB_AUTHENTICATION" if not failed else "FREEZE_INTEGRITY_FAILED",
        "checks": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "results": checks,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
