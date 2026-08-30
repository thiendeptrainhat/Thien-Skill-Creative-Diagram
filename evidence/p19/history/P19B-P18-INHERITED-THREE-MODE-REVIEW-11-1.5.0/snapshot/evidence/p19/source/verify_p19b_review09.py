#!/usr/bin/env python3
"""D-089 dp-security-matrix-only verification against archived review-08 bytes."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "thien-skill-creative-diagram/scripts",
    ROOT / "thien-skill-creative-diagram/scripts/tests",
    ROOT / "evidence/p19/source",
    ROOT / "evidence/p19/comparison",
):
    sys.path.insert(0, str(path))

from dp_security_matrix_layout_v15 import (  # noqa: E402
    COMPONENT_KEYS, ROLE_KEYS, dp_security_matrix_table,
    layout_dp_security_matrix, validate_dp_security_matrix_svg,
)
from dp_security_matrix_review09_fixture import dp_security_matrix_fixture  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-08-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review09-checks"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def verify():
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 87, "Wrong active gallery")
    targets = [record for record in records if record["fixture_id"] == "type-dp-security-matrix"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "Security matrix must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-dp-security-matrix":
            require(digest(active) != digest(previous), f"Security matrix not regenerated: {record['mode']}")
            continue
        require(
            active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD) == previous.read_text(encoding="utf-8"),
            f"Non-target artwork changed: {active.name}",
        )
        non_target_html += 1
        if record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f"{record['fixture_id']}.svg"
            require(digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)), f"Non-target preview changed: {preview.name}")
            non_target_previews += 1

    plan = adapt_visual(dp_security_matrix_fixture())
    layout = layout_dp_security_matrix(plan)
    require(layout["roles"] == ROLE_KEYS and layout["components"] == COMPONENT_KEYS, "Matrix header material mismatch")
    table = dp_security_matrix_table(plan)
    require(table.count("<tr>") == 26 and "Dashboard được chia sẻ" in table, "Alternative matrix table incomplete")

    PROOFS.mkdir(exist_ok=True)
    geometry = []
    proof_files = []
    for record in targets:
        page_path = GALLERY / record["path"]
        page = page_path.read_bytes()
        match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
        require(match is not None, "Missing security-matrix SVG")
        measurement = validate_dp_security_matrix_svg(match.group())
        require(measurement == {"cells": 25, "roles": 5, "components": 5, "focal": 1}, "Serialized security matrix mismatch")
        geometry.append(match.group().replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-dp-security-matrix--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "Security-matrix geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-089",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "dp_security_matrix_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "permission_cell_count": 25,
        "role_count": 5,
        "component_count": 5,
        "focal_boundary_count": 1,
        "explicit_text_state_encoding": "PASS",
        "partner_bi_read_scope": "PASS",
        "three_mode_geometry": "PASS",
        "alternative_exact_matrix_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-09-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
