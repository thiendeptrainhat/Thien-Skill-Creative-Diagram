#!/usr/bin/env python3
"""D-090 er-data-model-only verification against archived review-09 bytes."""
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

from er_data_model_layout_v15 import (  # noqa: E402
    er_data_model_table, layout_er_data_model, validate_er_data_model_svg,
)
from er_data_model_review10_fixture import er_data_model_fixture  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-09-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review10-checks"


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
    targets = [record for record in records if record["fixture_id"] == "type-er-data-model"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "ER data model must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-er-data-model":
            require(digest(active) != digest(previous), f"ER data model not regenerated: {record['mode']}")
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

    plan = adapt_visual(er_data_model_fixture())
    layout = layout_er_data_model(plan)
    require(len(layout["entities"]) == 4 and len(layout["relationships"]) == 3, "ER topology mismatch")
    table = er_data_model_table(plan)
    require(table.count("<tr>") == 23 and "primary-key" in table and "foreign-key" in table, "Alternative ER table incomplete")

    PROOFS.mkdir(exist_ok=True)
    geometry = []
    proof_files = []
    for record in targets:
        page_path = GALLERY / record["path"]
        page = page_path.read_bytes()
        match = re.search(r"<svg\b.*?</svg>", page.decode("utf-8"), re.S)
        require(match is not None, "Missing ER SVG")
        measurement = validate_er_data_model_svg(match.group())
        require(measurement == {"entities": 4, "members": 19, "relationships": 3, "aggregate": 1, "join": 1}, "Serialized ER model mismatch")
        geometry.append(match.group().replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-er-data-model--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "ER geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-090",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "er_data_model_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "entity_count": 4,
        "member_count": 19,
        "relationship_count": 3,
        "aggregate_root_count": 1,
        "associative_entity_count": 1,
        "explicit_pk_fk_cardinality_encoding": "PASS",
        "three_mode_geometry": "PASS",
        "alternative_exact_er_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    output = ROOT / "evidence/p19/P-19B-REVIEW-10-VERIFICATION.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
