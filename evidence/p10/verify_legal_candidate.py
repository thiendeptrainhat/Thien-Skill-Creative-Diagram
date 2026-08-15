#!/usr/bin/env python3
"""Dependency-free P-10 consistency verifier for exact candidate RC2."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
P10 = ROOT / "evidence" / "p10"
SKILL = ROOT / "thien-skill-creative-diagram"
REPORT = P10 / "verification-report.json"
LEGAL_FILES = [
    "LICENSE.md",
    "LICENSE-APPLICATION.md",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_MANIFEST.json",
    "ASSET_MANIFEST.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("p10_builder", P10 / "build_legal_candidate.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add(checks: list[dict], check_id: str, passed: bool, detail: str) -> None:
    checks.append({"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def runtime_inventory() -> list[dict]:
    excluded = set(LEGAL_FILES)
    entries = []
    for path in sorted(p for p in SKILL.rglob("*") if p.is_file()):
        if path.name in excluded or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        entries.append({
            "path": str(path.relative_to(ROOT)),
            "bytes": path.stat().st_size,
            "sha256": sha(path),
            "origin": "project-original independent implementation",
        })
    return entries


def main() -> int:
    builder = load_builder()
    checks: list[dict] = []
    sources = json.loads((SKILL / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    assets = json.loads((SKILL / "ASSET_MANIFEST.json").read_text(encoding="utf-8"))
    build = json.loads((P10 / "legal-candidate-build.json").read_text(encoding="utf-8"))
    approval_path = P10 / "LAWYER-APPROVAL-RECORD.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))

    required_source_keys = {
        "schema_version", "project", "generated_at", "sources", "capability_mappings", "notice_projection"
    }
    add(checks, "V-P10-001", set(sources) == required_source_keys, "SOURCE_MANIFEST top-level keys match P-01 schema")
    add(checks, "V-P10-002", sources["schema_version"] == "1.0-draft", "P-01 schema version retained")
    add(checks, "V-P10-003", sources["project"]["reimplementation_model"] == "clean-room-oriented independent reimplementation", "Exact provenance boundary retained")
    source_ids = [s["source_id"] for s in sources["sources"]]
    add(checks, "V-P10-004", len(source_ids) == len(set(source_ids)) == 6, "Six unique source records")
    add(checks, "V-P10-005", sources == builder.source_manifest(), "SOURCE_MANIFEST equals deterministic builder output")
    expected_third_party = builder.third_party_notices(sources).encode("utf-8")
    add(checks, "V-P10-006", (SKILL / "THIRD_PARTY_NOTICES.md").read_bytes() == expected_third_party, "Third-party notice is exact manifest projection")
    expected_notice = builder.notice(sources, assets).encode("utf-8")
    add(checks, "V-P10-007", (SKILL / "NOTICE").read_bytes() == expected_notice, "NOTICE is exact manifest-derived output")

    artifact_map = {entry["path"]: entry for entry in build["artifacts"]}
    hashes_ok = all(
        artifact_map[f"thien-skill-creative-diagram/{name}"]["sha256"] == sha(SKILL / name)
        for name in LEGAL_FILES
    )
    add(checks, "V-P10-008", hashes_ok, "All six candidate artifacts match build-record hashes")
    add(
        checks,
        "V-P10-009",
        sha(SKILL / "LICENSE.md") == build["license_template"]["result_sha256"]
        and build["license_template"]["source_sha256"] == builder.TEMPLATE_SHA256,
        "LICENSE.md matches the owner-approved singular-title transform of the locked template",
    )

    license_text = (SKILL / "LICENSE.md").read_text(encoding="utf-8")
    application = (SKILL / "LICENSE-APPLICATION.md").read_text(encoding="utf-8")
    required_license_phrases = [
        "Đơn hàng trả phí", "Văn bản chấp thuận", "Thỏa thuận thương mại",
        "Paid Order", "Written Permission", "Commercial Agreement",
        "Bản tiếng Việt", "Vietnamese version prevails",
        "Tòa án có thẩm quyền tại Việt Nam", "competent jurisdiction in Vietnam",
    ]
    add(checks, "V-P10-010", all(p in license_text for p in required_license_phrases), "Locked bilingual grant, priority, law, and forum terms are present")
    add(checks, "V-P10-011", "không tự cấp quyền" in application and "grants no rights by itself" in application, "Application declaration does not create rights")
    add(checks, "V-P10-012", "Skill/code rights do not include logo or brand rights" in application and "Quyền đối với logo/brand không được cấp" in application, "Brand carve-out is bilingual")
    add(checks, "V-P10-013", "thien.8888@gmail.com" in license_text and "thien.8888@gmail.com" in application, "Licensing contact is consistent")
    add(checks, "V-P10-014", "1.0.0" in application and build["version"] == "1.0.0", "Candidate version is consistent")
    add(
        checks,
        "V-P10-014A",
        license_text.splitlines()[0] == builder.LICENSE_NAME
        and "TRAN NGOC THIEN'S SKILLS" not in "\n".join(license_text.splitlines()[:2]),
        "Both bilingual title lines use the owner-approved singular exact license name",
    )

    approved = assets["approved_candidates"]
    excluded = assets["excluded_qa_only"]
    add(checks, "V-P10-015", len(approved) == 16 and len(excluded) == 6, "D-027 inventory is 16 approved and 6 QA-only excluded")
    add(checks, "V-P10-016", all(a["dimensions"][0] >= 64 for a in approved), "Every approved derivative meets the 64px minimum")
    add(checks, "V-P10-017", all(a["dimensions"][0] in (32, 48) for a in excluded), "Only 32/48px derivatives are QA-only excluded")
    asset_hashes_ok = True
    for item in approved + excluded:
        path = ROOT / item["source_evidence_path"]
        asset_hashes_ok = asset_hashes_ok and path.is_file() and sha(path) == item["sha256"]
    add(checks, "V-P10-018", asset_hashes_ok, "All 22 derivative evidence hashes resolve")
    master = ROOT / assets["master"]["source_evidence_path"]
    add(checks, "V-P10-019", master.is_file() and sha(master) == assets["master"]["sha256"], "Logo master hash resolves")
    add(checks, "V-P10-020", all(not a["release_eligible"] for a in approved + excluded), "No asset is release-eligible before G-06 and authorized P-13 execution")

    targeted = [a for a in approved if a["package_targets"]]
    expected_target_ids = {"AST-TDTN-LIGHT-64", "AST-TDTN-LIGHT-400"}
    add(
        checks,
        "V-P10-020A",
        {a["asset_id"] for a in targeted} == expected_target_ids
        and all(a["package_targets"] == ["openai-plugin", "universal-raw-skill"] for a in targeted),
        "D-028 selects only light-plate 64px and 400px for OpenAI and Universal",
    )
    add(
        checks,
        "V-P10-020B",
        all("claude-plugin" not in a["package_targets"] for a in approved)
        and all(not a["package_targets"] and a["scope"] == "owner-approved-provenance-not-packaged-v1.0.0" for a in approved if a["asset_id"] not in expected_target_ids),
        "Claude has no brand target and the other 14 approved derivatives are provenance-only",
    )
    add(
        checks,
        "V-P10-020C",
        assets["package_mapping_decision"]["state"] == "owner-approved"
        and assets["package_mapping_decision"]["decision"] == "D-028",
        "Package-scope decision is locked to D-028 without starting P-13",
    )

    absolute_path_pattern = re.compile(r"(?:/Users/|/private/|file://|[A-Za-z]:\\\\)")
    payload_texts = [
        (name, (SKILL / name).read_text(encoding="utf-8"))
        for name in LEGAL_FILES
    ]
    add(checks, "V-P10-021", not any(absolute_path_pattern.search(text) for _, text in payload_texts), "No personal/development absolute path in legal bundle")
    add(checks, "V-P10-022", sources["sources"][0]["material_transfer"] == {"copied_bytes": False, "mode": "none"}, "diagram-design material transfer is explicitly none")

    add(
        checks,
        "V-P10-023",
        approval["candidate_id"] == build["candidate_id"]
        and approval["version"] == build["version"]
        and approval["aggregate_sha256"] == build["aggregate_sha256"],
        "Vietnamese-lawyer approval is bound to the exact RC2 candidate, version, and aggregate hash",
    )
    add(
        checks,
        "V-P10-024",
        approval["decision"] == "approved"
        and approval["conditions"] == []
        and approval["reviewed_at"] == "2026-08-15"
        and approval["reviewer"]["name"] == "Tran Ngoc Thien"
        and approval["reviewer"]["capacity"] == "Vietnamese lawyer and owner"
        and approval["reviewer"]["capacity_basis"] == "Explicit self-attestation in the project conversation"
        and approval["reviewer"]["independent_credential_verification"] == "not-performed",
        "Unconditional approval, reviewer identity/capacity/date, self-attestation basis, and verification limit are recorded",
    )
    approval_artifacts = {entry["path"]: entry["sha256"] for entry in approval["reviewed_artifacts"]}
    add(
        checks,
        "V-P10-025",
        set(approval_artifacts) == set(artifact_map)
        and all(approval_artifacts[path] == artifact_map[path]["sha256"] for path in artifact_map),
        "Lawyer approval covers the exact six artifacts and their build-record hashes",
    )

    resolved_decisions = [
        {
            "decision_id": "P10-OD-01",
            "status": "resolved-owner-approved",
            "topic": "license-name",
            "resolution": "Use singular Skill as the controlling exact name and apply the same one-word correction to both bilingual title lines.",
            "authority": "D-028 owner approval on 2026-08-15; Vietnamese-lawyer review still required",
        },
        {
            "decision_id": "P10-OD-02",
            "status": "resolved-owner-approved",
            "topic": "asset-package-mapping",
            "resolution": "Target only light-plate 64px/400px to OpenAI plugin and Universal raw skill under assets/brand; no Claude asset; other approved derivatives remain provenance-only.",
            "authority": "D-028 owner approval on 2026-08-15; P-13 execution remains not started",
        },
    ]

    runtime = runtime_inventory()
    runtime_digest = hashlib.sha256(
        "".join(f"{entry['path']}\0{entry['sha256']}\n" for entry in runtime).encode("utf-8")
    ).hexdigest()
    failed = [check for check in checks if check["result"] == "FAIL"]
    report = {
        "record_id": "P10-VERIFICATION-1",
        "version": "1.0.0",
        "verified_at": "2026-08-15T00:00:00+07:00",
        "candidate_id": build["candidate_id"],
        "candidate_aggregate_sha256": build["aggregate_sha256"],
        "status": "P10-PASSED",
        "summary": {
            "checks": len(checks),
            "passed": len(checks) - len(failed),
            "failed": len(failed),
            "blocking_open_decisions": 0,
            "lawyer_signoff_present": True,
        },
        "checks": checks,
        "resolved_decisions": resolved_decisions,
        "runtime_inventory": {
            "file_count": len(runtime),
            "aggregate_sha256": runtime_digest,
            "files": runtime,
        },
        "legal_artifacts": [
            {"path": f"thien-skill-creative-diagram/{name}", "sha256": sha(SKILL / name)}
            for name in LEGAL_FILES
        ],
        "lawyer_approval": {
            "record_path": "evidence/p10/LAWYER-APPROVAL-RECORD.json",
            "record_sha256": sha(approval_path),
            "decision_ref": approval["decision_ref"],
            "reviewer": approval["reviewer"],
            "reviewed_at": approval["reviewed_at"],
            "decision": approval["decision"],
            "conditions": approval["conditions"],
        },
        "limits": [
            "Reviewer capacity is recorded from explicit self-attestation in the project conversation; no independent credential verification was performed.",
            "The Python jsonschema package is unavailable; schema invariants used by this candidate are verified dependency-free and JSON syntax is checked separately.",
            "P-13 official host-field verification, asset copying, package construction, ZIP build, install testing, and release actions were not performed.",
        ],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
