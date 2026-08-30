#!/usr/bin/env python3
"""D-087 dp-integration-only verification against archived review-06 bytes."""
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

from dp_integration_layout_v15 import (  # noqa: E402
    EXPECTED_EDGES, EXPECTED_NODES, dp_integration_table,
    layout_dp_integration, validate_dp_integration_svg,
)
from dp_integration_review07_fixture import dp_integration_fixture  # noqa: E402
from gallery_renderer_v15 import MODES, P19B_CANDIDATE_ID  # noqa: E402
from generate_comparison import p19_preview  # noqa: E402
from visual_adapters_v15 import adapt_visual  # noqa: E402

OLD = "P19B-P18-INHERITED-THREE-MODE-REVIEW-06-1.5.0"
ARCHIVE = ROOT / "evidence/p19/history" / OLD
GALLERY = ROOT / "evidence/p19/gallery"
PROOFS = ROOT / "evidence/p19/review07-checks"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError(message)


def verify() -> dict:
    receipt = json.loads((ARCHIVE / "ARCHIVE-RECEIPT.json").read_text(encoding="utf-8"))
    for name, expected in receipt["snapshot_records"].items():
        require(digest(ARCHIVE / "snapshot" / name) == expected, f"Archive drift: {name}")
    for name, expected in receipt["protected_records"].items():
        require(digest(ROOT / name) == expected, f"Protected drift: {name}")

    inventory = json.loads((GALLERY / "P-19B-INVENTORY.json").read_text(encoding="utf-8"))
    records = inventory["records"]
    require(inventory["candidate_id"] == P19B_CANDIDATE_ID and len(records) == 87, "Wrong active gallery")
    targets = [record for record in records if record["fixture_id"] == "type-dp-integration"]
    require(len(targets) == 3 and {item["mode"] for item in targets} == set(MODES), "DP integration must expose three modes")

    non_target_html = non_target_previews = 0
    for record in records:
        active = GALLERY / record["path"]
        previous = ARCHIVE / "snapshot" / active.relative_to(ROOT)
        if record["fixture_id"] == "type-dp-integration":
            require(digest(active) != digest(previous), f"DP integration not regenerated: {record['mode']}")
            continue
        require(active.read_text(encoding="utf-8").replace(P19B_CANDIDATE_ID, OLD) == previous.read_text(encoding="utf-8"),
                f"Non-target artwork changed: {active.name}")
        non_target_html += 1
        if record["mode"] == "neutral-light":
            preview = GALLERY / "previews" / f"{record['fixture_id']}.svg"
            require(digest(preview) == digest(ARCHIVE / "snapshot" / preview.relative_to(ROOT)), f"Non-target preview changed: {preview.name}")
            non_target_previews += 1

    fixture = dp_integration_fixture()
    plan = adapt_visual(fixture)
    layout = layout_dp_integration(plan)
    require(set(layout["nodes"]) == EXPECTED_NODES and set(layout["edges"]) == EXPECTED_EDGES, "Detailed material mismatch")
    table = dp_integration_table(plan)
    for item in fixture["nodes"] + fixture["edges"] + fixture["groups"]:
        require(item["id"] in table, f"Alternative table omits {item['id']}")

    PROOFS.mkdir(exist_ok=True)
    geometry = []
    proof_files = []
    for record in targets:
        path = GALLERY / record["path"]
        page = path.read_bytes()
        text = page.decode("utf-8")
        svg = re.search(r"<svg\b.*?</svg>", text, re.S)
        require(svg is not None, "Missing DP integration SVG")
        measurement = validate_dp_integration_svg(svg.group())
        require(measurement == {"nodes": 11, "edges": 11, "groups": 1, "continuous_routes": 11}, "Serialized topology mismatch")
        geometry.append(svg.group().replace(record["mode"], "MODE"))
        proof = PROOFS / f'type-dp-integration--{record["mode"]}.svg'
        proof.write_bytes(p19_preview(page)[0])
        proof_files.append({"path": str(proof.relative_to(ROOT)), "sha256": digest(proof)})
    require(len(set(geometry)) == 1, "DP integration geometry differs across modes")

    return {
        "candidate_id": P19B_CANDIDATE_ID,
        "authority": "D-087",
        "status": "PASS",
        "gallery_manifest_sha256": digest(GALLERY / "P-19B-MANIFEST.json"),
        "archived_files_verified": len(receipt["snapshot_records"]),
        "protected_files_verified": len(receipt["protected_records"]),
        "dp_integration_html_changed": 3,
        "non_target_html_artwork_preserved": non_target_html,
        "non_target_preview_svg_byte_identical": non_target_previews,
        "node_count": len(layout["nodes"]),
        "directed_edge_count": len(layout["edges"]),
        "platform_group_count": 1,
        "three_mode_geometry": "PASS",
        "containment_and_endpoint_bindings": "PASS",
        "alternative_semantic_table": "PASS",
        "proof_files": proof_files,
        "browser": "BLOCKED_NOT_EXECUTABLE",
        "owner_approval": "pending",
        "p19c": "not-performed",
    }


if __name__ == "__main__":
    report = verify()
    path = ROOT / "evidence/p19/P-19B-REVIEW-07-VERIFICATION.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "proof_files"}, ensure_ascii=False, indent=2))
